"""Quarterly operations aggregation and stable-ID annual panel linkage."""

import numpy as np
import pandas as pd

from src.stage6.operations import COUNTS, outcome_rates


ROUTE_QUARTER = ['Year', 'Quarter', 'OriginAirportID', 'DestAirportID']
MONTHLY_CARRIER_KEY = [
    'Year', 'Month', 'DOT_ID_Reporting_Airline',
    'OriginAirportID', 'DestAirportID',
]
FARE_CARRIER_KEY = ROUTE_QUARTER + ['RPCarrier', 'sample']
FARE_TOTALS = ['passengers', 'records', 'fare_total', 'fare_square_total']
RATE_COLUMNS = [
    'cancellation_rate', 'diversion_rate', 'delay_15_rate', 'delay_60_rate',
    'mean_arrival_delay',
]


def _require_columns(frame, columns, label):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing {label} columns: {sorted(missing)}')


def quarterly_operations(monthly_cells):
    """Sum monthly/reporter counts and recompute route-quarter outcome rates."""
    cells = monthly_cells.copy()
    _require_columns(cells, MONTHLY_CARRIER_KEY + COUNTS, 'monthly operations')
    if cells[MONTHLY_CARRIER_KEY].isna().any().any():
        raise ValueError('Missing monthly operations identity')
    months = pd.to_numeric(cells['Month'], errors='coerce')
    if months.isna().any() or not months.between(1, 12).all() or not (months % 1).eq(0).all():
        raise ValueError('Invalid operations month')
    duplicates = cells.duplicated(MONTHLY_CARRIER_KEY, keep=False)
    if duplicates.any():
        raise ValueError(
            f'Duplicate operations carrier-month route IDs: {int(duplicates.sum())}')
    if cells[COUNTS].isna().any().any():
        raise ValueError('Missing operations counts')
    cells['Quarter'] = ((months.astype(int) - 1) // 3) + 1
    grouped = cells.groupby(ROUTE_QUARTER, as_index=False, observed=True).agg(
        **{column: (column, 'sum') for column in COUNTS},
        months_observed=('Month', 'nunique'),
    )
    grouped = outcome_rates(grouped)
    return grouped[ROUTE_QUARTER + COUNTS + ['months_observed'] + RATE_COLUMNS].sort_values(
        ROUTE_QUARTER, kind='stable').reset_index(drop=True)


def _aggregate_fares(fare_carrier_cells):
    fares = fare_carrier_cells.copy()
    _require_columns(fares, FARE_CARRIER_KEY + FARE_TOTALS, 'fare carrier')
    if fares[FARE_CARRIER_KEY].isna().any().any():
        raise ValueError('Missing fare carrier identity')
    duplicates = fares.duplicated(FARE_CARRIER_KEY, keep=False)
    if duplicates.any():
        raise ValueError(f'Duplicate fare carrier cells: {int(duplicates.sum())}')
    if fares[FARE_TOTALS].isna().any().any():
        raise ValueError('Missing fare totals')
    if not np.isfinite(fares[FARE_TOTALS].to_numpy(dtype=float)).all():
        raise ValueError('Non-finite fare totals')
    if fares['passengers'].le(0).any():
        raise ValueError('Fare passenger weights must be positive')
    keys = ROUTE_QUARTER + ['sample']
    grouped = fares.groupby(keys, as_index=False, observed=True)[FARE_TOTALS].sum()
    grouped['fare_mean'] = grouped.fare_total / grouped.passengers
    grouped['fare_variance'] = np.maximum(
        0, grouped.fare_square_total / grouped.passengers - grouped.fare_mean ** 2)
    grouped['low_support'] = grouped.passengers.lt(30)
    return grouped


def join_annual_panel(fare_carrier_cells, monthly_operations):
    """Outer join independently aggregated fare samples and operations by route IDs."""
    fares = _aggregate_fares(fare_carrier_cells)
    operations = quarterly_operations(monthly_operations)
    preferred = ['primary', 'broad_fare_bounds']
    observed_samples = list(dict.fromkeys(fare_carrier_cells['sample'].tolist()))
    samples = preferred + sorted(
        sample for sample in observed_samples if sample not in preferred)

    panels = []
    by_sample = {}
    for sample in samples:
        sample_fares = fares.loc[fares['sample'].eq(sample)].copy()
        merged = sample_fares.merge(
            operations, on=ROUTE_QUARTER, how='outer', validate='one_to_one',
            indicator=True)
        merged['sample'] = sample
        merged['coverage'] = merged['_merge'].map({
            'both': 'matched', 'left_only': 'fare_only',
            'right_only': 'operations_only',
        }).astype(object)
        merged = merged.drop(columns='_merge')
        counts = merged['coverage'].value_counts()
        by_sample[sample] = {
            'fare_routes': len(sample_fares),
            'operations_routes': len(operations),
            'matched': int(counts.get('matched', 0)),
            'fare_only': int(counts.get('fare_only', 0)),
            'operations_only': int(counts.get('operations_only', 0)),
        }
        panels.append(merged)

    panel = pd.concat(panels, ignore_index=True)
    sample_order = {sample: index for index, sample in enumerate(samples)}
    panel['_sample_order'] = panel['sample'].map(sample_order)
    panel = panel.sort_values(
        ['_sample_order'] + ROUTE_QUARTER, kind='stable').drop(
            columns='_sample_order').reset_index(drop=True)
    audit = {
        'by_sample': by_sample,
        'fare_reporting_carriers': int(fare_carrier_cells['RPCarrier'].nunique()),
        'operations_reporting_carriers': int(
            monthly_operations['DOT_ID_Reporting_Airline'].nunique()),
    }
    return panel, audit
