"""Acquire and rebuild the declared historical fare/operations schema bootstrap."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import zipfile

import pandas as pd

from src.acquisition.download import digest, fetch
from src.cleaning.panel import MARKET_COLUMNS, TICKET_COLUMNS
from src.config import MANIFESTS, RAW, bts_path
from src.stage6.inventory import ontime_request
from src.stage6.operations import read_operations


def input_records():
    records = []
    for year in (2010, 2024):
        request = ontime_request(year, 1)
        records.append({'kind': 'operations', 'year': year, 'month': 1,
            'url': request['url'], 'target': RAW/'bts_ontime'/request['url'].rsplit('/', 1)[1],
            'manifest': MANIFESTS/f'bts_ontime_{year}_01.json',
            'source': 'BTS Reporting Carrier On-Time Performance',
            'params': {'year': year, 'month': 1}})
    for table in ('Market', 'Ticket'):
        target = bts_path(table, 2010, 1)
        records.append({'kind': 'fare', 'table': table, 'year': 2010, 'quarter': 1,
            'url': 'https://transtats.bts.gov/PREZIP/'+target.name, 'target': target,
            'manifest': MANIFESTS/f'bts_db1b_{table.lower()}_2010_q1.json',
            'source': f'BTS DB1B{table}', 'params': {'year': 2010, 'quarter': 1}})
    return records


def verify_input(target, manifest, url, params):
    target = Path(target)
    record = json.loads(Path(manifest).read_text(encoding='utf-8'))
    if Path(record['local_path']).resolve() != target.resolve():
        raise ValueError('Bootstrap manifest path differs from consumed input')
    recorded_params = (record['query_parameters'] if 'query_parameters' in record
                       else {key: record[key] for key in ('year', 'quarter') if key in record})
    if record['url'] != url or recorded_params != params:
        raise ValueError('Bootstrap manifest request identity differs')
    if digest(target) != record['sha256']:
        raise ValueError('Bootstrap raw input checksum mismatch')


def inspect_fare(path, table, year, quarter, *, chunksize=250000):
    if table == 'Market':
        required = MARKET_COLUMNS + ['OriginAirportID', 'DestAirportID']
    elif table == 'Ticket':
        required = TICKET_COLUMNS + ['Coupons', 'OriginAirportID']
    else:
        raise ValueError('Expected Market or Ticket table')
    rows = missing_ids = 0
    with zipfile.ZipFile(path) as archive:
        members = [name for name in archive.namelist() if name.lower().endswith('.csv')]
        if len(members) != 1:
            raise ValueError('Expected one fare CSV member')
        member = members[0]
        with archive.open(member) as stream:
            columns = pd.read_csv(stream, nrows=0).columns.tolist()
        if set(required) - set(columns):
            raise ValueError(f'Missing historical fare columns: {sorted(set(required) - set(columns))}')
        with archive.open(member) as stream:
            for chunk in pd.read_csv(stream, usecols=['Year', 'Quarter', 'ItinID'], chunksize=chunksize):
                if not (chunk.Year.eq(year) & chunk.Quarter.eq(quarter)).all():
                    raise ValueError('Historical fare period mismatch')
                rows += len(chunk)
                missing_ids += int(chunk.ItinID.isna().sum())
    if not rows or missing_ids:
        raise ValueError('Empty historical fare input or missing itinerary IDs')
    return {'table': table, 'year': year, 'quarter': quarter, 'rows': rows,
            'input_sha256': digest(path), 'csv_member': member, 'columns': columns,
            'required_columns_present': True, 'missing_itinerary_ids': missing_ids,
            'scope': 'national header/period/ID audit only; no fare estimates or filtering'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('outputs/stage6'))
    args = parser.parse_args(argv)
    records = input_records()
    if args.acquire:
        def acquire(record):
            return fetch(record['url'], record['target'], record['manifest'],
                         source=record['source'], params=record['params'])
        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(acquire, records))
    scoped, national, operation_audits, fare_audits = [], [], [], []
    for record in records:
        verify_input(record['target'], record['manifest'], record['url'], record['params'])
        if record['kind'] == 'operations':
            cells, totals, audit = read_operations(record['target'], record['year'], record['month'])
            scoped.append(cells)
            national.append(totals)
            operation_audits.append(audit)
            print(f"Operations {record['year']}-01: {audit['raw_rows']:,} national rows", flush=True)
        else:
            audit = inspect_fare(record['target'], record['table'], record['year'], record['quarter'])
            fare_audits.append(audit)
            print(f"Fare {record['table']} 2010Q1: {audit['rows']:,} rows", flush=True)
    # Write only after all inputs and audits succeed, preserving prior outputs on failure.
    args.output.mkdir(parents=True, exist_ok=True)
    pd.concat(scoped, ignore_index=True).to_csv(args.output/'operations_bootstrap_cells.csv', index=False, lineterminator='\n')
    pd.concat(national, ignore_index=True).to_csv(args.output/'operations_bootstrap_national.csv', index=False, lineterminator='\n')
    for name, payload in [('operations_bootstrap_audit.json', operation_audits),
                          ('fare_schema_audit.json', fare_audits)]:
        (args.output/name).write_text(json.dumps(payload, indent=2, allow_nan=False)+'\n',
                                     encoding='utf-8', newline='\n')
    print('Bootstrap complete; no expanded fare models have been estimated.', flush=True)


if __name__ == '__main__':
    main()
