"""Rebuild the declared 2010 fare and operations development panel."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
import uuid

import pandas as pd

from src.acquisition.download import digest, fetch
from src.config import MANIFESTS, RAW, bts_path
from src.stage6.bootstrap import verify_input
from src.stage6.inventory import ontime_request


def input_records():
    records = []
    for month in range(1, 13):
        request = ontime_request(2010, month)
        records.append({'kind': 'operations', 'year': 2010, 'month': month,
            'url': request['url'], 'target': RAW/'bts_ontime'/request['url'].rsplit('/', 1)[1],
            'manifest': MANIFESTS/f'bts_ontime_2010_{month:02d}.json',
            'source': 'BTS Reporting Carrier On-Time Performance',
            'params': {'year': 2010, 'month': month}})
    for quarter in range(1, 5):
        for table in ('Market', 'Ticket'):
            target = bts_path(table, 2010, quarter)
            records.append({'kind': 'fare', 'table': table, 'year': 2010,
                'quarter': quarter, 'url': 'https://transtats.bts.gov/PREZIP/'+target.name,
                'target': target, 'manifest': MANIFESTS/f'bts_db1b_{table.lower()}_2010_q{quarter}.json',
                'source': f'BTS DB1B{table}', 'params': {'year': 2010, 'quarter': quarter}})
    return records


def validate_months(audits):
    identities = [(a['year'], a['month']) for a in audits]
    if len(identities) != 12 or set(identities) != {(2010, m) for m in range(1, 13)}:
        raise ValueError('Annual build requires exactly twelve distinct 2010 source months')


def advertised_bytes(records, inventories):
    known = {}
    for inventory in inventories:
        for result in inventory['results']:
            request = inventory['requests'][result['request_index']]
            size = result['headers']['content_length']
            if result['success'] and isinstance(size, int) and size > 0:
                known[request['url']] = size
    if any(r['url'] not in known for r in records):
        raise ValueError('Successful access inventory with content length is required for every input')
    return sum(known[r['url']] for r in records)


def acquire_inputs(records):
    for record in records:
        if record['target'].exists() and not record['manifest'].exists():
            raise ValueError(f'Existing raw input lacks provenance manifest: {record["target"]}')
    inventories = [json.loads((MANIFESTS/name).read_text(encoding='utf-8')) for name in (
        'stage6_access_inventory.json', 'stage6_operations_access_correction.json',
        'stage6_2010_access_inventory.json')]
    total = advertised_bytes(records, inventories)
    missing = [r for r in records if not r['target'].exists()]
    remaining = advertised_bytes(missing, inventories)
    free = shutil.disk_usage('.').free
    if remaining > free:
        raise ValueError('Insufficient free disk for remaining advertised downloads')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    ledger_path = MANIFESTS/f'stage6_2010_acquisition_{stamp}.json'
    ledger = {'started_at_utc': stamp, 'advertised_total_bytes': total,
              'advertised_missing_bytes': remaining, 'free_bytes_before': free,
              'fr24_calls': 0, 'fr24_credits': 0, 'results': []}
    def acquire(record):
        cached = record['target'].exists()
        result = {'url': record['url'], 'local_path': record['target'].as_posix(),
                  'cached_before': cached}
        try:
            fetch(record['url'], record['target'], record['manifest'],
                  source=record['source'], params=record['params'])
            result.update(status='verified_cache' if cached else 'downloaded',
                          bytes=record['target'].stat().st_size,
                          sha256=digest(record['target']))
        except Exception as exc:
            result.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        return result
    # No later pair begins after a failed pair. Each current pair is allowed to finish.
    with ledger_path.open('x', encoding='utf-8', newline='\n') as handle:
        with ThreadPoolExecutor(max_workers=2) as executor:
            for start in range(0, len(records), 2):
                results = list(executor.map(acquire, records[start:start+2]))
                ledger['results'].extend(results)
                handle.seek(0)
                handle.write(json.dumps(ledger, indent=2)+'\n')
                handle.truncate()
                handle.flush()
                if any(r['status'] == 'failed' for r in results):
                    raise RuntimeError(f'Acquisition failed; see {ledger_path}')
    return ledger_path


def publish_directory(staging, output):
    """Publish a complete sibling directory; retain old bytes and roll back errors."""
    staging, output = Path(staging), Path(output)
    parent = output.parent.resolve()
    if (staging.parent.resolve() != parent or staging.resolve() == output.resolve()
            or output.resolve() in (parent, Path.cwd().resolve())
            or staging.is_symlink() or output.is_symlink()):
        raise ValueError('Publication requires distinct safe sibling directories')
    if not staging.is_dir() or (output.exists() and not output.is_dir()):
        raise ValueError('Publication targets must be directories')
    backup = None
    if output.exists():
        backup = parent/f'.{output.name}.backup-{uuid.uuid4().hex}'
        if backup.parent.resolve() != parent:
            raise ValueError('Backup must remain within output parent')
        output.rename(backup)
    try:
        staging.rename(output)
    except BaseException:
        if backup is not None:
            backup.rename(output)
        raise
    return backup


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('outputs/stage6/annual_2010'))
    args = parser.parse_args(argv)
    records = input_records()
    if args.acquire:
        acquire_inputs(records)
    # Verify the entire declared input set before any derived output is replaced.
    for record in records:
        verify_input(record['target'], record['manifest'], record['url'], record['params'])
    from src.stage6.annual_fares import select_airports, process_fares
    from src.stage6.annual_panel import join_annual_panel
    from src.stage6.operations import read_operations
    ranking, selection_audit = select_airports(bts_path('Market', 2010, 1))
    airport_ids = ranking.loc[ranking.selected, 'AirportID'].astype(int).tolist()
    print(f'Selected {len(airport_ids)} baseline airports', flush=True)
    fare_parts, fare_audits, alias_parts = [], [], []
    for quarter in range(1, 5):
        cells, audit, aliases = process_fares(bts_path('Market', 2010, quarter),
            bts_path('Ticket', 2010, quarter), year=2010, quarter=quarter,
            airport_ids=airport_ids)
        fare_parts.append(cells)
        fare_audits.append(audit)
        alias_parts.append(aliases.assign(source='DB1B', Year=2010, period=quarter))
        print(f'Fare 2010Q{quarter}: {len(cells):,} carrier cells across samples', flush=True)
    monthly_parts, national_parts, operation_audits = [], [], []
    for month in range(1, 13):
        record = next(r for r in records if r.get('month') == month)
        cells, national, audit = read_operations(record['target'], 2010, month,
                                                 airport_ids=airport_ids)
        monthly_parts.append(cells)
        national_parts.append(national)
        operation_audits.append(audit)
        for endpoint in ('Origin', 'Dest'):
            aliases = cells[[endpoint+'AirportID', endpoint]].drop_duplicates().rename(
                columns={endpoint+'AirportID': 'AirportID', endpoint: 'code'})
            alias_parts.append(aliases.assign(source='BTS on-time', Year=2010, period=month))
        print(f'Operations 2010-{month:02d}: {audit["raw_rows"]:,} national flights', flush=True)
    validate_months(operation_audits)
    fares = pd.concat(fare_parts, ignore_index=True)
    monthly = pd.concat(monthly_parts, ignore_index=True)
    national = pd.concat(national_parts, ignore_index=True)
    panel, panel_audit = join_annual_panel(fares, monthly)
    aliases = pd.concat(alias_parts, ignore_index=True).drop_duplicates().sort_values(
        ['source', 'Year', 'period', 'AirportID', 'code']).reset_index(drop=True)
    carrier_map = national[['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline']].drop_duplicates()
    identity_audit = {
        'airport_ids_with_multiple_codes': int((aliases.groupby('AirportID').code.nunique() > 1).sum()),
        'codes_with_multiple_airport_ids': int((aliases.groupby('code').AirportID.nunique() > 1).sum()),
        'operations_codes_with_multiple_dot_ids': int((carrier_map.groupby('Reporting_Airline').DOT_ID_Reporting_Airline.nunique() > 1).sum()),
        'carrier_join': 'None; route-quarter join aggregates each source independently across carriers',
        'alias_period_units': {'DB1B': 'quarter', 'BTS on-time': 'month'},
    }
    audit = {'year': 2010, 'scope': 'development year; no estimated fare models',
        'selection': selection_audit, 'fares': fare_audits, 'operations': operation_audits,
        'identity': identity_audit, 'panel': panel_audit,
        'verified_input_count': len(records), 'source_months_complete': True}
    outputs = {'airport_ranking.csv': ranking, 'fare_carrier_cells.csv': fares,
        'operations_carrier_month.csv': monthly, 'operations_national_month.csv': national,
        'airport_aliases.csv': aliases, 'operations_carrier_identities.csv': carrier_map,
        'route_quarter_panel.csv': panel}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Complete serialization in temporary files before publishing any result.
    with tempfile.TemporaryDirectory(dir=args.output.parent, prefix='.annual_2010_') as temp:
        staging = Path(temp)
        for name, frame in outputs.items():
            frame.to_csv(staging/name, index=False, lineterminator='\n')
        (staging/'quality_audit.json').write_text(json.dumps(audit, indent=2, allow_nan=False)+'\n',
            encoding='utf-8', newline='\n')
        publish_directory(staging, args.output)
    print(f'2010 development panel complete: {len(panel):,} rows across samples; no fare models fitted.', flush=True)


if __name__ == '__main__':
    main()
