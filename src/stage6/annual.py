"""Rebuild a declared annual fare and operations panel with frozen later-year scope."""
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
from src.stage6.periods import periods_for_year, restrict_tables_to_periods


def input_records(year=2010):
    periods = periods_for_year(year)
    records = []
    for month in periods.months:
        request = ontime_request(year, month)
        records.append({'kind': 'operations', 'year': year, 'month': month,
            'url': request['url'], 'target': RAW/'bts_ontime'/request['url'].rsplit('/', 1)[1],
            'manifest': MANIFESTS/f'bts_ontime_{year}_{month:02d}.json',
            'source': 'BTS Reporting Carrier On-Time Performance',
            'params': {'year': year, 'month': month}})
    for quarter in periods.quarters:
        for table in ('Market', 'Ticket'):
            target = bts_path(table, year, quarter)
            records.append({'kind': 'fare', 'table': table, 'year': year,
                'quarter': quarter, 'url': 'https://transtats.bts.gov/PREZIP/'+target.name,
                'target': target, 'manifest': MANIFESTS/f'bts_db1b_{table.lower()}_{year}_q{quarter}.json',
                'source': f'BTS DB1B{table}', 'params': {'year': year, 'quarter': quarter}})
    return records


def validate_months(audits, year=2010):
    periods = periods_for_year(year)
    if any(
        not isinstance(a.get(field), int) or isinstance(a.get(field), bool)
        for a in audits
        for field in ('year', 'month')
    ):
        raise ValueError(f'Annual build requires exact integer {year} source months')
    identities = [(a['year'], a['month']) for a in audits]
    expected = {(year, month) for month in periods.months}
    if len(identities) != len(periods.months) or set(identities) != expected:
        count = 'six' if periods.partial_year else 'twelve'
        raise ValueError(f'Annual build requires exactly {count} distinct {year} source months')


def _observed_periods(tables, column, table):
    frame = tables[table]
    if column not in frame:
        raise ValueError(f'Missing {column} in {table}')
    values = pd.to_numeric(frame[column], errors='coerce')
    if values.isna().any() or not (values % 1).eq(0).all():
        raise ValueError(f'Invalid {column} in {table}')
    return sorted(values.astype(int).unique().tolist())


def _observed_year(tables):
    years = set()
    for frame in tables.values():
        if isinstance(frame, pd.DataFrame) and 'Year' in frame and not frame.empty:
            values = pd.to_numeric(frame['Year'], errors='coerce')
            if values.isna().any() or not (values % 1).eq(0).all():
                raise ValueError('Invalid comparison Year')
            years.update(values.astype(int).unique().tolist())
    if len(years) != 1:
        raise ValueError('Comparison tables must contain exactly one year')
    return next(iter(years))


def prepare_comparison(baseline_tables, current_tables, periods):
    """Restrict a partial year's baseline and describe the comparison window."""
    if not periods.partial_year:
        return baseline_tables, None
    baseline = restrict_tables_to_periods(baseline_tables, periods)
    baseline_year = _observed_year(baseline)
    current_year = _observed_year(current_tables)
    if current_year != periods.year:
        raise ValueError('Current comparison year does not match declared periods')
    audit = {
        'label': periods.label,
        'baseline_year': baseline_year,
        'current_year': current_year,
        'baseline_restricted_to_matching_periods': True,
        'expected_fare_quarters': list(periods.quarters),
        'baseline_fare_quarters_observed': _observed_periods(
            baseline, 'Quarter', 'fare_carrier_cells.csv'),
        'current_fare_quarters_observed': _observed_periods(
            current_tables, 'Quarter', 'fare_carrier_cells.csv'),
        'expected_operations_months': list(periods.months),
        'baseline_operations_months_observed': _observed_periods(
            baseline, 'Month', 'operations_carrier_month.csv'),
        'current_operations_months_observed': _observed_periods(
            current_tables, 'Month', 'operations_carrier_month.csv'),
        'alias_period_units': {'DB1B': 'quarter', 'BTS on-time': 'month'},
        'carrier_identity_period_unit': 'month',
    }
    return baseline, audit


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


def acquire_inputs(records, year=2010):
    for record in records:
        if record['target'].exists() and not record['manifest'].exists():
            raise ValueError(f'Existing raw input lacks provenance manifest: {record["target"]}')
    names = ('stage6_access_inventory.json', 'stage6_operations_access_correction.json',
             'stage6_2010_access_inventory.json') if year == 2010 else (f'stage6_{year}_access_inventory.json',)
    inventories = [json.loads((MANIFESTS/name).read_text(encoding='utf-8')) for name in names]
    total = advertised_bytes(records, inventories)
    missing = [r for r in records if not r['target'].exists()]
    remaining = advertised_bytes(missing, inventories)
    free = shutil.disk_usage('.').free
    if remaining > free:
        raise ValueError('Insufficient free disk for remaining advertised downloads')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    ledger_path = MANIFESTS/f'stage6_{year}_acquisition_{stamp}.json'
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
    parser.add_argument('--year', type=int, choices=range(2010, 2026), default=2010)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    year = args.year
    periods = periods_for_year(year)
    args.output = args.output or Path(f'outputs/stage6/annual_{year}')
    baseline_tables = None
    if year != 2010:
        from src.stage6.baseline import load_baseline, BASELINE_DIRECTORY
        destination, baseline_dir = args.output.resolve(), BASELINE_DIRECTORY.resolve()
        if destination.is_relative_to(baseline_dir) or baseline_dir.is_relative_to(destination):
            raise ValueError('Later-year output must not overlap the frozen baseline')
        ranking, selection_audit, baseline_tables = load_baseline()
    records = input_records() if year == 2010 else input_records(year)
    if args.acquire:
        acquire_inputs(records, year=year)
    # Verify the entire declared input set before any derived output is replaced.
    for record in records:
        verify_input(record['target'], record['manifest'], record['url'], record['params'])
    from src.stage6.annual_fares import select_airports, process_fares
    from src.stage6.annual_panel import join_annual_panel
    from src.stage6.operations import read_operations
    if year == 2010:
        ranking, selection_audit = select_airports(bts_path('Market', 2010, 1))
    airport_ids = ranking.loc[ranking.selected, 'AirportID'].astype(int).tolist()
    print(f'Selected {len(airport_ids)} baseline airports', flush=True)
    fare_parts, fare_audits, alias_parts = [], [], []
    for quarter in periods.quarters:
        cells, audit, aliases = process_fares(bts_path('Market', year, quarter),
            bts_path('Ticket', year, quarter), year=year, quarter=quarter,
            airport_ids=airport_ids)
        fare_parts.append(cells)
        fare_audits.append(audit)
        alias_parts.append(aliases.assign(source='DB1B', Year=year, period=quarter))
        print(f'Fare {year}Q{quarter}: {len(cells):,} carrier cells across samples', flush=True)
    monthly_parts, national_parts, operation_audits = [], [], []
    for month in periods.months:
        record = next(r for r in records if r.get('month') == month)
        cells, national, audit = read_operations(record['target'], year, month,
                                                 airport_ids=airport_ids)
        monthly_parts.append(cells)
        national_parts.append(national)
        operation_audits.append(audit)
        for endpoint in ('Origin', 'Dest'):
            aliases = cells[[endpoint+'AirportID', endpoint]].drop_duplicates().rename(
                columns={endpoint+'AirportID': 'AirportID', endpoint: 'code'})
            alias_parts.append(aliases.assign(source='BTS on-time', Year=year, period=month))
        print(f'Operations {year}-{month:02d}: {audit["raw_rows"]:,} national flights', flush=True)
    validate_months(operation_audits, year=year)
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
    scope = ('development year; no estimated fare models' if year == 2010 else
             'subsequent-year data validation; no estimated fare models')
    if periods.partial_year:
        scope = 'partial-year data validation through Q2/June; no estimated fare models'
    audit = {'year': year, 'scope': scope,
        'selection': selection_audit, 'fares': fare_audits, 'operations': operation_audits,
        'identity': identity_audit, 'panel': panel_audit,
        'verified_input_count': len(records), 'source_months_complete': True}
    outputs = {'airport_ranking.csv': ranking, 'fare_carrier_cells.csv': fares,
        'operations_carrier_month.csv': monthly, 'operations_national_month.csv': national,
        'airport_aliases.csv': aliases, 'operations_carrier_identities.csv': carrier_map,
        'route_quarter_panel.csv': panel}
    if baseline_tables is not None:
        from src.stage6.continuity import compare_years
        comparison_baseline, comparison_audit = prepare_comparison(
            baseline_tables, outputs, periods)
        extra, continuity_audit = compare_years(comparison_baseline, outputs)
        outputs.update(extra)
        audit['continuity'] = continuity_audit
        audit['selection_reused_from_year'] = 2010
        if comparison_audit is not None:
            audit['period'] = {
                'label': periods.label,
                'partial_year': True,
                'expected_fare_quarters': list(periods.quarters),
                'observed_fare_quarters': comparison_audit['current_fare_quarters_observed'],
                'expected_operations_months': list(periods.months),
                'observed_operations_months': comparison_audit['current_operations_months_observed'],
            }
            audit['comparison_period'] = comparison_audit
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Complete serialization in temporary files before publishing any result.
    with tempfile.TemporaryDirectory(dir=args.output.parent, prefix=f'.annual_{year}_') as temp:
        staging = Path(temp)
        for name, frame in outputs.items():
            frame.to_csv(staging/name, index=False, lineterminator='\n')
        (staging/'quality_audit.json').write_text(json.dumps(audit, indent=2, allow_nan=False)+'\n',
            encoding='utf-8', newline='\n')
        publish_directory(staging, args.output)
    completion_label = periods.label if periods.partial_year else f'{year} annual'
    print(f'{completion_label} panel complete: {len(panel):,} rows across samples; no fare models fitted.', flush=True)


if __name__ == '__main__':
    main()
