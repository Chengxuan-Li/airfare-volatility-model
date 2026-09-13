"""Create compact, verified summaries of the canonical Stage 6 annual panels."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import tempfile

import pandas as pd

from src.stage6.annual import publish_directory
from src.stage6.periods import periods_for_year


SAMPLES = (
    ('primary', 'primary'),
    ('broad_fare_bounds', 'broad'),
)
OUTCOME_COLUMNS = (
    'cancellation_rate', 'diversion_rate', 'delay_15_rate',
    'delay_60_rate', 'mean_arrival_delay',
)
COMMON_FILES = {
    'airport_aliases.csv', 'airport_ranking.csv', 'fare_carrier_cells.csv',
    'operations_carrier_identities.csv', 'operations_carrier_month.csv',
    'operations_national_month.csv', 'quality_audit.json',
    'route_quarter_panel.csv',
}
CONTINUITY_FILES = {
    'airport_continuity.csv', 'carrier_continuity.csv', 'route_continuity.csv',
}


def _require_columns(frame, columns, label):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing {label} columns: {sorted(missing)}')


def _validate_periods(frame, period_column, expected, label, year, *, complete):
    _require_columns(frame, ('Year', period_column), label)
    years = pd.to_numeric(frame['Year'], errors='coerce')
    periods = pd.to_numeric(frame[period_column], errors='coerce')
    if (years.isna().any() or periods.isna().any()
            or not (years % 1).eq(0).all() or not (periods % 1).eq(0).all()
            or (not frame.empty and set(years.astype(int)) != {year})
            or not set(periods.astype(int)).issubset(set(expected))
            or (complete and set(periods.astype(int)) != set(expected))):
        raise ValueError(
            f'{label} has invalid year or periods; expected year {year} '
            f'within {list(expected)}')


def _validate_unique_keys(frame, keys, label):
    _require_columns(frame, keys, label)
    if frame[list(keys)].isna().any().any():
        raise ValueError(f'Missing {label} key')
    if frame.duplicated(list(keys)).any():
        raise ValueError(f'Duplicate {label} key')


def _regime(year):
    if year < 2020:
        return 'pre_2020'
    if year <= 2021:
        return 'pandemic_2020_2021'
    return 'recovery_2022_onward'


def _period_label(year):
    return '2025_Q1_Q2_January_June' if year == 2025 else f'{year}_full_year'


def _sum_flights(frame, label):
    _require_columns(frame, ('flights',), label)
    flights = pd.to_numeric(frame['flights'], errors='coerce')
    if flights.isna().any() or flights.lt(0).any() or not (flights % 1).eq(0).all():
        raise ValueError(f'{label} flights must be nonnegative whole counts')
    return int(flights.sum())


def _sample_metrics(panel, sample, prefix, expected_months_by_quarter):
    cells = panel.loc[panel['sample'].eq(sample)].copy()
    allowed = {'matched', 'fare_only', 'operations_only'}
    if not set(cells['coverage']).issubset(allowed):
        raise ValueError(f'Invalid coverage value in {sample}')
    keys = ['Year', 'Quarter', 'OriginAirportID', 'DestAirportID', 'sample']
    if cells.duplicated(keys).any():
        raise ValueError(f'Duplicate route-quarter cell in {sample}')

    fare = cells['coverage'].ne('operations_only')
    matched = cells['coverage'].eq('matched')
    operations = cells['coverage'].ne('fare_only')
    passengers = pd.to_numeric(cells.loc[fare, 'passengers'], errors='coerce')
    if passengers.isna().any() or passengers.lt(0).any():
        raise ValueError(f'Invalid passenger weights in {sample}')
    fare_passengers = float(passengers.sum())
    matched_passengers = float(pd.to_numeric(
        cells.loc[matched, 'passengers'], errors='coerce').sum())
    coverage = matched_passengers / fare_passengers if fare_passengers else None

    months = pd.to_numeric(cells.loc[operations, 'months_observed'], errors='coerce')
    if months.isna().any():
        raise ValueError(f'Missing observed-month counts in {sample}')
    expected_cell_months = cells.loc[operations, 'Quarter'].map(
        expected_months_by_quarter)
    if expected_cell_months.isna().any() or months.gt(expected_cell_months).any():
        raise ValueError(f'Invalid observed-month counts in {sample}')
    missing_outcomes = cells.loc[operations, list(OUTCOME_COLUMNS)].isna().any(axis=1)
    low_support = cells.loc[fare, 'low_support']
    if low_support.isna().any():
        raise ValueError(f'Missing low-support flags in {sample}')

    counts = cells['coverage'].value_counts()
    return {
        f'{prefix}_cells': int(len(cells)),
        f'{prefix}_matched': int(counts.get('matched', 0)),
        f'{prefix}_fare_only': int(counts.get('fare_only', 0)),
        f'{prefix}_operations_only': int(counts.get('operations_only', 0)),
        f'{prefix}_fare_passengers': fare_passengers,
        f'{prefix}_matched_passengers': matched_passengers,
        f'{prefix}_passenger_weighted_coverage': coverage,
        f'{prefix}_low_support_fare_cells': int(low_support.astype(bool).sum()),
        f'{prefix}_partial_month_operations_cells': int(
            months.lt(expected_cell_months).sum()),
        f'{prefix}_missing_outcome_operations_cells': int(missing_outcomes.sum()),
    }


def _carrier_presence(fares, identities, year, quarter_count, month_count, partial):
    fare_periods = fares[['RPCarrier', 'Quarter']].drop_duplicates()
    fare_periods['RPCarrier'] = fare_periods['RPCarrier'].astype(str)
    rows = []
    for carrier, group in fare_periods.groupby('RPCarrier', sort=True):
        periods = sorted(group['Quarter'].astype(int).unique())
        rows.append({
            'source': 'DB1B', 'identity_type': 'reporting_carrier_code',
            'carrier_id': carrier, 'carrier_code': carrier, 'year': year,
            'period_unit': 'quarter', 'first_period': periods[0],
            'last_period': periods[-1],
            'periods_present': ';'.join(map(str, periods)),
            'periods_observed': len(periods),
            'expected_periods': quarter_count, 'partial_year': partial,
        })
    operation_periods = identities[[
        'DOT_ID_Reporting_Airline', 'Reporting_Airline', 'Month'
    ]].drop_duplicates()
    keys = ['DOT_ID_Reporting_Airline', 'Reporting_Airline']
    for (dot_id, code), group in operation_periods.groupby(keys, sort=True):
        periods = sorted(group['Month'].astype(int).unique())
        rows.append({
            'source': 'BTS on-time', 'identity_type': 'dot_reporting_airline_id',
            'carrier_id': str(int(dot_id)), 'carrier_code': str(code), 'year': year,
            'period_unit': 'month', 'first_period': periods[0],
            'last_period': periods[-1],
            'periods_present': ';'.join(map(str, periods)),
            'periods_observed': len(periods),
            'expected_periods': month_count, 'partial_year': partial,
        })
    columns = [
        'source', 'identity_type', 'carrier_id', 'carrier_code', 'year',
        'period_unit', 'first_period', 'last_period', 'periods_observed',
        'periods_present', 'expected_periods', 'partial_year',
    ]
    return pd.DataFrame(rows, columns=columns)


def summarize_frames(panel, fare_carriers, operations_monthly,
                     operations_national, carrier_identities, *, year,
                     quarters, months):
    """Summarize one already-verified year from small or canonical DataFrames."""
    quarters, months = tuple(quarters), tuple(months)
    if year == 2025:
        if quarters != (1, 2) or months != tuple(range(1, 7)):
            raise ValueError('2025 must be limited to Q1-Q2 and January-June')
    elif quarters != (1, 2, 3, 4) or months != tuple(range(1, 13)):
        raise ValueError('Complete years require four quarters and twelve months')

    panel_columns = (
        'Year', 'Quarter', 'OriginAirportID', 'DestAirportID', 'sample',
        'passengers', 'low_support', 'months_observed', 'coverage',
    ) + OUTCOME_COLUMNS
    _require_columns(panel, panel_columns, 'route-quarter panel')
    _require_columns(fare_carriers, ('Year', 'Quarter', 'RPCarrier', 'sample'),
                     'fare carrier')
    _require_columns(operations_monthly,
                     ('Year', 'Month', 'DOT_ID_Reporting_Airline', 'flights'),
                     'scoped operations')
    _require_columns(operations_national,
                     ('Year', 'Month', 'DOT_ID_Reporting_Airline', 'flights'),
                     'national operations')
    _require_columns(carrier_identities,
                     ('Year', 'Month', 'DOT_ID_Reporting_Airline',
                      'Reporting_Airline'), 'operations carrier identities')
    if not set(panel['sample'].dropna()).issubset(dict(SAMPLES)):
        raise ValueError('Unexpected route-quarter panel sample')
    if not set(fare_carriers['sample'].dropna()).issubset(dict(SAMPLES)):
        raise ValueError('Unexpected fare carrier sample')
    _validate_unique_keys(
        panel,
        ('Year', 'Quarter', 'OriginAirportID', 'DestAirportID', 'sample'),
        'route-quarter panel')
    _validate_unique_keys(
        fare_carriers,
        ('Year', 'Quarter', 'OriginAirportID', 'DestAirportID', 'RPCarrier',
         'sample'),
        'fare carrier')
    _validate_unique_keys(
        operations_monthly,
        ('Year', 'Month', 'DOT_ID_Reporting_Airline', 'OriginAirportID',
         'DestAirportID'),
        'scoped operations')
    _validate_unique_keys(
        operations_national,
        ('Year', 'Month', 'DOT_ID_Reporting_Airline'),
        'national operations')
    _validate_unique_keys(
        carrier_identities,
        ('Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline'),
        'operations carrier identity')
    _validate_periods(panel, 'Quarter', quarters, 'route-quarter panel', year,
                      complete=False)
    _validate_periods(fare_carriers, 'Quarter', quarters, 'fare carrier periods',
                      year, complete=False)
    _validate_periods(operations_monthly, 'Month', months,
                      'scoped operations periods', year, complete=False)
    _validate_periods(operations_national, 'Month', months,
                      'national operations periods', year, complete=True)
    _validate_periods(carrier_identities, 'Month', months,
                      'operations carrier identity periods', year, complete=True)

    expected_months_by_quarter = {
        quarter: sum(((month - 1) // 3) + 1 == quarter for month in months)
        for quarter in quarters
    }
    partial = year == 2025
    annual = {
        'year': year, 'regime': _regime(year),
        'period_label': _period_label(year), 'partial_year': partial,
        'expected_quarters': len(quarters),
        'observed_quarters': len(quarters),
        'expected_months': len(months),
        'observed_months': int(operations_national['Month'].nunique()),
        'national_flights': _sum_flights(operations_national, 'national operations'),
        'scoped_flights': _sum_flights(operations_monthly, 'scoped operations'),
        'db1b_reporting_codes': int(fare_carriers['RPCarrier'].nunique()),
        'operations_reporting_dot_ids': int(
            carrier_identities['DOT_ID_Reporting_Airline'].nunique()),
        'scoped_operations_reporting_dot_ids': int(
            operations_monthly['DOT_ID_Reporting_Airline'].nunique()),
    }
    for sample, prefix in SAMPLES:
        annual.update(_sample_metrics(
            panel, sample, prefix, expected_months_by_quarter))

    quarterly_rows = []
    for quarter in quarters:
        quarter_months = [
            month for month in months if ((month - 1) // 3) + 1 == quarter
        ]
        row = {
            'year': year, 'quarter': quarter, 'regime': _regime(year),
            'partial_year': partial, 'expected_months': len(quarter_months),
            'observed_months': len(quarter_months),
            'national_flights': _sum_flights(
                operations_national.loc[
                    operations_national['Month'].isin(quarter_months)],
                'national operations'),
            'scoped_flights': _sum_flights(
                operations_monthly.loc[
                    operations_monthly['Month'].isin(quarter_months)],
                'scoped operations'),
            'db1b_reporting_codes': int(fare_carriers.loc[
                fare_carriers['Quarter'].eq(quarter), 'RPCarrier'].nunique()),
            'operations_reporting_dot_ids': int(carrier_identities.loc[
                carrier_identities['Month'].isin(quarter_months),
                'DOT_ID_Reporting_Airline'].nunique()),
            'scoped_operations_reporting_dot_ids': int(operations_monthly.loc[
                operations_monthly['Month'].isin(quarter_months),
                'DOT_ID_Reporting_Airline'].nunique()),
        }
        quarter_panel = panel.loc[panel['Quarter'].eq(quarter)]
        for sample, prefix in SAMPLES:
            row.update(_sample_metrics(
                quarter_panel, sample, prefix,
                {quarter: len(quarter_months)}))
        quarterly_rows.append(row)

    presence = _carrier_presence(
        fare_carriers, carrier_identities, year, len(quarters), len(months), partial)
    audit = {
        'year': year,
        'regime_interpretation': (
            'Descriptive calendar grouping only; not a causal control or effect.'),
        'operations_counts_source': {
            'national_flights': 'operations_national_month.csv',
            'scoped_flights': 'operations_carrier_month.csv',
            'fare_sample_panels_used': False,
        },
        'fare_carrier_identity': 'DB1B reporting carrier code',
        'operations_carrier_identity': (
            'BTS national DOT reporting airline ID with source-reported code'),
        'operations_carrier_counts_scope': {
            'operations_reporting_dot_ids': 'national reporting population',
            'scoped_operations_reporting_dot_ids': (
                'retained routes between frozen selected airports; reconciles '
                'to annual quality panel operations_reporting_carriers'),
        },
        'carrier_crosswalk_performed': False,
    }
    return annual, pd.DataFrame(quarterly_rows), presence, audit


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected_files(year):
    return COMMON_FILES if year == 2010 else COMMON_FILES | CONTINUITY_FILES


def _declared_periods(year):
    periods = periods_for_year(year)
    return periods.quarters, periods.months


def _verify_year(directory, year, quarters, months):
    verification_path = directory / 'verification.json'
    if not verification_path.is_file():
        raise ValueError(f'Missing per-year verification: {verification_path}')
    verification = json.loads(verification_path.read_text(encoding='utf-8'))
    expected_files = _expected_files(year)
    hashes = verification.get('output_sha256')
    if not isinstance(hashes, dict) or set(hashes) != expected_files:
        raise ValueError(
            f'{year} verification output set must be exactly {sorted(expected_files)}')
    if (verification.get('successful_full_raw_builds', 0) < 2
            or verification.get('byte_identical') is not True
            or verification.get('compared_output_files') != len(expected_files)):
        raise ValueError(f'{year} verification lacks two byte-identical full builds')
    for name in sorted(expected_files):
        path = directory / name
        if not path.is_file():
            raise ValueError(f'Missing verified {year} output: {name}')
        if _sha256(path) != hashes[name]:
            raise ValueError(f'{year} output hash mismatch: {name}')

    quality = json.loads((directory / 'quality_audit.json').read_text(encoding='utf-8'))
    fare_identities = [
        (item.get('year'), item.get('quarter')) for item in quality.get('fares', [])
    ]
    operation_identities = [
        (item.get('year'), item.get('month'))
        for item in quality.get('operations', [])
    ]
    expected_fares = [(year, quarter) for quarter in quarters]
    expected_operations = [(year, month) for month in months]
    if quality.get('year') != year or fare_identities != expected_fares:
        raise ValueError(f'{year} quality audit has wrong fare period identities')
    if operation_identities != expected_operations:
        raise ValueError(f'{year} quality audit has wrong operations period identities')
    expected_inputs = len(quarters) * 2 + len(months)
    if (quality.get('verified_input_count') != expected_inputs
            or quality.get('source_months_complete') is not True):
        raise ValueError(f'{year} quality audit is not source-complete')
    return verification, quality


def _reconcile_quality_panel(annual, quality, year):
    by_sample = quality.get('panel', {}).get('by_sample')
    if not isinstance(by_sample, dict):
        raise ValueError(f'{year} quality audit lacks panel coverage counts')
    for sample, prefix in SAMPLES:
        recorded = by_sample.get(sample)
        if not isinstance(recorded, dict):
            raise ValueError(f'{year} quality audit lacks {sample} coverage counts')
        expected = {
            'fare_routes': annual[f'{prefix}_matched'] + annual[f'{prefix}_fare_only'],
            'operations_routes': (
                annual[f'{prefix}_matched'] + annual[f'{prefix}_operations_only']),
            'matched': annual[f'{prefix}_matched'],
            'fare_only': annual[f'{prefix}_fare_only'],
            'operations_only': annual[f'{prefix}_operations_only'],
        }
        if any(recorded.get(key) != value for key, value in expected.items()):
            raise ValueError(
                f'{year} {sample} summary does not reconcile to quality audit')
    carrier_expectations = {
        'fare_reporting_carriers': annual['db1b_reporting_codes'],
        'operations_reporting_carriers': annual['scoped_operations_reporting_dot_ids'],
    }
    if any(quality.get('panel', {}).get(key) != value
           for key, value in carrier_expectations.items()):
        raise ValueError(f'{year} carrier counts do not reconcile to quality audit')


def build_history(history_root=Path('outputs/stage6'),
                  output=Path('outputs/stage6/history'),
                  expected_years=tuple(range(2010, 2026))):
    """Verify annual directories; optional subsets are labelled as incomplete history."""
    history_root, output = Path(history_root), Path(output)
    years = tuple(expected_years)
    if not years or len(set(years)) != len(years):
        raise ValueError('Expected history years must be a nonempty unique sequence')
    if years != tuple(sorted(years)):
        raise ValueError('Expected history years must be sorted')
    for year in years:
        periods_for_year(year)
    if years != tuple(range(years[0], years[-1]+1)):
        raise ValueError('Expected history years must be consecutive')
    root_resolved = history_root.resolve()
    output_resolved = output.resolve()
    annual_directories = [
        (history_root / f'annual_{year}').resolve() for year in years
    ]
    if (root_resolved == output_resolved
            or root_resolved.is_relative_to(output_resolved)
            or any(output_resolved == directory
                   or output_resolved.is_relative_to(directory)
                   or directory.is_relative_to(output_resolved)
                   for directory in annual_directories)):
        raise ValueError(
            'History output must not overlap its root or consumed annual directories')

    annual_rows, quarterly_parts, presence_parts, year_audits = [], [], [], []
    verification_hashes = {}
    for year in years:
        quarters, months = _declared_periods(year)
        directory = history_root / f'annual_{year}'
        _, quality = _verify_year(directory, year, quarters, months)
        verification_hashes[str(year)] = _sha256(directory / 'verification.json')
        frames = [
            pd.read_csv(directory / 'route_quarter_panel.csv'),
            pd.read_csv(
                directory / 'fare_carrier_cells.csv',
                converters={'RPCarrier': lambda value: value}),
            pd.read_csv(
                directory / 'operations_carrier_month.csv',
                converters={'Reporting_Airline': lambda value: value}),
            pd.read_csv(
                directory / 'operations_national_month.csv',
                converters={'Reporting_Airline': lambda value: value}),
            pd.read_csv(
                directory / 'operations_carrier_identities.csv',
                converters={'Reporting_Airline': lambda value: value}),
        ]
        annual, quarterly, presence, year_audit = summarize_frames(
            *frames, year=year, quarters=quarters, months=months)
        _reconcile_quality_panel(annual, quality, year)
        annual_rows.append(annual)
        quarterly_parts.append(quarterly)
        presence_parts.append(presence)
        year_audits.append(year_audit)

    annual_summary = pd.DataFrame(annual_rows)
    quarterly_summary = pd.concat(quarterly_parts, ignore_index=True)
    carrier_presence = pd.concat(presence_parts, ignore_index=True)
    additive_metrics = [
        'national_flights', 'scoped_flights',
        *[
            f'{prefix}_{metric}'
            for _, prefix in SAMPLES
            for metric in (
                'cells', 'matched', 'fare_only', 'operations_only',
                'fare_passengers', 'matched_passengers',
                'low_support_fare_cells', 'partial_month_operations_cells',
                'missing_outcome_operations_cells',
            )
        ],
    ]
    quarterly_totals = quarterly_summary.groupby('year', as_index=True)[
        additive_metrics].sum()
    annual_equals_quarterly = True
    for row in annual_rows:
        for metric in additive_metrics:
            if not math.isclose(
                    float(row[metric]), float(quarterly_totals.loc[row['year'], metric]),
                    rel_tol=1e-12, abs_tol=1e-9):
                annual_equals_quarterly = False
                break
    if not annual_equals_quarterly:
        raise ValueError('Annual and quarterly history summaries do not reconcile')
    horizon_totals = {
        metric: (int(annual_summary[metric].sum())
                 if metric.endswith(('cells', 'matched', 'fare_only',
                                     'operations_only', 'flights'))
                 else float(annual_summary[metric].sum()))
        for metric in additive_metrics
    }
    audit = {
        'declared_horizon': f'{years[0]}_Q1_through_{years[-1]}_Q{_declared_periods(years[-1])[0][-1]}',
        'full_horizon_complete': years == tuple(range(2010, 2026)),
        'verified_years': list(years),
        'year_count': len(years),
        'quarter_count': int(quarterly_summary.shape[0]),
        'partial_2025': 2025 in years,
        'verification_sha256': verification_hashes,
        'reconciliation': {
            'annual_equals_quarterly': annual_equals_quarterly,
            'annual_equals_per_year_quality_panel': True,
            'additive_metrics_checked': additive_metrics,
        },
        'horizon_totals': horizon_totals,
        'regime_interpretation': (
            'Pre-2020, pandemic 2020-2021, and recovery 2022 onward are '
            'descriptive calendar groupings, not causal controls or effects.'),
        'operations_counting': (
            'National and scoped flights come from source-specific monthly '
            'operations tables and are counted once, outside fare samples.'),
        'fare_interpretation': (
            'Passenger weights measure sampled DB1B coverage; fares are not '
            'summed and quarterly records are not timestamped quotes.'),
        'traffic_interpretation': (
            'Observed operations are descriptive traffic, not exogenous demand.'),
        'carrier_interpretation': (
            'DB1B reporting codes and BTS DOT reporting airline IDs remain '
            'source-separated; no carrier crosswalk is applied.'),
        'year_audits': year_audits,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
            dir=output.parent, prefix='.history_') as temporary:
        staging = Path(temporary)
        annual_summary.to_csv(
            staging / 'annual_summary.csv', index=False, lineterminator='\n')
        quarterly_summary.to_csv(
            staging / 'quarterly_summary.csv', index=False, lineterminator='\n')
        carrier_presence.to_csv(
            staging / 'carrier_presence.csv', index=False, lineterminator='\n')
        (staging / 'quality_audit.json').write_text(
            json.dumps(audit, indent=2, allow_nan=False) + '\n',
            encoding='utf-8', newline='\n')
        publish_directory(staging, output)
    return audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=Path('outputs/stage6/history'))
    args = parser.parse_args(argv)
    build_history(output=args.output)


if __name__ == '__main__':
    main()
