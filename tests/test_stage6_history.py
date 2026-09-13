import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


EXPECTED_LATER_FILES = {
    'airport_aliases.csv', 'airport_continuity.csv', 'airport_ranking.csv',
    'carrier_continuity.csv', 'fare_carrier_cells.csv',
    'operations_carrier_identities.csv', 'operations_carrier_month.csv',
    'operations_national_month.csv', 'quality_audit.json',
    'route_continuity.csv', 'route_quarter_panel.csv',
}


def history_frames():
    panel_rows = []
    for sample, fare_only_passengers in (
            ('primary', 10.0), ('broad_fare_bounds', 20.0)):
        panel_rows.extend([
            {'Year': 2025, 'Quarter': 1, 'OriginAirportID': 1,
             'DestAirportID': 2, 'sample': sample, 'passengers': 90.0,
             'low_support': False, 'flights': 999.0, 'months_observed': 3.0,
             'cancellation_rate': .1, 'diversion_rate': 0.0,
             'delay_15_rate': .2, 'delay_60_rate': .05,
             'mean_arrival_delay': 4.0, 'coverage': 'matched'},
            {'Year': 2025, 'Quarter': 1, 'OriginAirportID': 3,
             'DestAirportID': 4, 'sample': sample,
             'passengers': fare_only_passengers, 'low_support': True,
             'flights': np.nan, 'months_observed': np.nan,
             'cancellation_rate': np.nan, 'diversion_rate': np.nan,
             'delay_15_rate': np.nan, 'delay_60_rate': np.nan,
             'mean_arrival_delay': np.nan, 'coverage': 'fare_only'},
            {'Year': 2025, 'Quarter': 2, 'OriginAirportID': 5,
             'DestAirportID': 6, 'sample': sample, 'passengers': np.nan,
             'low_support': np.nan, 'flights': 888.0, 'months_observed': 2.0,
             'cancellation_rate': .2, 'diversion_rate': 0.0,
             'delay_15_rate': np.nan, 'delay_60_rate': .1,
             'mean_arrival_delay': np.nan, 'coverage': 'operations_only'},
        ])
    panel = pd.DataFrame(panel_rows)
    fare_carriers = pd.DataFrame([
        {'Year': 2025, 'Quarter': 1, 'RPCarrier': '01',
         'OriginAirportID': 1, 'DestAirportID': 2, 'sample': 'primary'},
        {'Year': 2025, 'Quarter': 1, 'RPCarrier': '01',
         'OriginAirportID': 1, 'DestAirportID': 2,
         'sample': 'broad_fare_bounds'},
        {'Year': 2025, 'Quarter': 2, 'RPCarrier': 'BB',
         'OriginAirportID': 3, 'DestAirportID': 4, 'sample': 'primary'},
    ])
    operations_monthly = pd.DataFrame([
        {'Year': 2025, 'Month': month, 'DOT_ID_Reporting_Airline': 100,
         'Reporting_Airline': '01', 'OriginAirportID': 1,
         'DestAirportID': 2, 'flights': month}
        for month in range(1, 7)
    ])
    operations_national = pd.DataFrame([
        {'Year': 2025, 'Month': month, 'DOT_ID_Reporting_Airline': 100,
         'Reporting_Airline': '01', 'flights': 10}
        for month in range(1, 7)
    ])
    carrier_identities = operations_national[
        ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline']
    ].copy()
    return (panel, fare_carriers, operations_monthly,
            operations_national, carrier_identities)


def test_summarize_frames_keeps_samples_separate_and_counts_operations_once():
    from src.stage6.history import summarize_frames

    annual, quarterly, _, audit = summarize_frames(
        *history_frames(), year=2025, quarters=(1, 2), months=tuple(range(1, 7)))

    assert annual == {
        'year': 2025, 'regime': 'recovery_2022_onward',
        'period_label': '2025_Q1_Q2_January_June', 'partial_year': True,
        'expected_quarters': 2, 'observed_quarters': 2,
        'expected_months': 6, 'observed_months': 6,
        'national_flights': 60, 'scoped_flights': 21,
        'db1b_reporting_codes': 2, 'operations_reporting_dot_ids': 1,
        'primary_cells': 3, 'primary_matched': 1, 'primary_fare_only': 1,
        'primary_operations_only': 1, 'primary_fare_passengers': 100.0,
        'primary_matched_passengers': 90.0,
        'primary_passenger_weighted_coverage': .9,
        'primary_low_support_fare_cells': 1,
        'primary_partial_month_operations_cells': 1,
        'primary_missing_outcome_operations_cells': 1,
        'broad_cells': 3, 'broad_matched': 1, 'broad_fare_only': 1,
        'broad_operations_only': 1, 'broad_fare_passengers': 110.0,
        'broad_matched_passengers': 90.0,
        'broad_passenger_weighted_coverage': pytest.approx(90 / 110),
        'broad_low_support_fare_cells': 1,
        'broad_partial_month_operations_cells': 1,
        'broad_missing_outcome_operations_cells': 1,
    }
    assert quarterly[['quarter', 'national_flights', 'scoped_flights']].to_dict('records') == [
        {'quarter': 1, 'national_flights': 30, 'scoped_flights': 6},
        {'quarter': 2, 'national_flights': 30, 'scoped_flights': 15},
    ]
    assert audit['operations_counts_source'] == {
        'national_flights': 'operations_national_month.csv',
        'scoped_flights': 'operations_carrier_month.csv',
        'fare_sample_panels_used': False,
    }


def test_summarize_frames_preserves_source_specific_carrier_identities_and_presence():
    from src.stage6.history import summarize_frames

    _, _, presence, _ = summarize_frames(
        *history_frames(), year=2025, quarters=(1, 2), months=tuple(range(1, 7)))

    assert presence.to_dict('records') == [
        {'source': 'DB1B', 'identity_type': 'reporting_carrier_code',
         'carrier_id': '01', 'carrier_code': '01', 'year': 2025,
         'period_unit': 'quarter', 'first_period': 1, 'last_period': 1,
         'periods_present': '1', 'periods_observed': 1,
         'expected_periods': 2, 'partial_year': True},
        {'source': 'DB1B', 'identity_type': 'reporting_carrier_code',
         'carrier_id': 'BB', 'carrier_code': 'BB', 'year': 2025,
         'period_unit': 'quarter', 'first_period': 2, 'last_period': 2,
         'periods_present': '2', 'periods_observed': 1,
         'expected_periods': 2, 'partial_year': True},
        {'source': 'BTS on-time', 'identity_type': 'dot_reporting_airline_id',
         'carrier_id': '100', 'carrier_code': '01', 'year': 2025,
         'period_unit': 'month', 'first_period': 1, 'last_period': 6,
         'periods_present': '1;2;3;4;5;6', 'periods_observed': 6,
         'expected_periods': 6, 'partial_year': True},
    ]


def test_summarize_frames_allows_verified_period_with_no_scoped_rows():
    from src.stage6.history import summarize_frames

    frames = list(history_frames())
    frames[0] = frames[0].loc[lambda frame: frame.Quarter.eq(1)]
    frames[1] = frames[1].loc[lambda frame: frame.Quarter.eq(1)]
    frames[2] = frames[2].loc[lambda frame: frame.Month.le(3)]

    annual, quarterly, _, _ = summarize_frames(
        *frames, year=2025, quarters=(1, 2), months=tuple(range(1, 7)))

    assert annual['observed_quarters'] == 2
    q2 = quarterly.loc[lambda frame: frame.quarter.eq(2)].iloc[0]
    assert q2.scoped_flights == 0
    assert q2.primary_cells == 0 and q2.broad_cells == 0


def test_summarize_frames_rejects_missing_declared_period_before_summarizing():
    from src.stage6.history import summarize_frames

    frames = list(history_frames())
    frames[3] = frames[3].loc[lambda frame: frame.Month.ne(6)]

    with pytest.raises(ValueError, match='national operations periods'):
        summarize_frames(
            *frames, year=2025, quarters=(1, 2), months=tuple(range(1, 7)))


def test_summarize_frames_rejects_unexpected_scoped_period():
    from src.stage6.history import summarize_frames

    frames = list(history_frames())
    extra = frames[0].iloc[[0]].assign(Quarter=3)
    frames[0] = pd.concat([frames[0], extra], ignore_index=True)

    with pytest.raises(ValueError, match='route-quarter panel'):
        summarize_frames(
            *frames, year=2025, quarters=(1, 2), months=tuple(range(1, 7)))


def test_summarize_frames_rejects_duplicate_operations_keys_before_counting():
    from src.stage6.history import summarize_frames

    frames = list(history_frames())
    frames[2] = pd.concat([frames[2], frames[2].iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match='Duplicate scoped operations key'):
        summarize_frames(
            *frames, year=2025, quarters=(1, 2), months=tuple(range(1, 7)))


def _write_verified_year(root: Path, *, corrupt=False, panel_mismatch=False):
    annual_dir = root / 'annual_2025'
    annual_dir.mkdir(parents=True)
    panel, fares, scoped, national, identities = history_frames()
    frames = {
        'route_quarter_panel.csv': panel,
        'fare_carrier_cells.csv': fares,
        'operations_carrier_month.csv': scoped,
        'operations_national_month.csv': national,
        'operations_carrier_identities.csv': identities,
    }
    for name in EXPECTED_LATER_FILES:
        path = annual_dir / name
        if name in frames:
            frames[name].to_csv(path, index=False, lineterminator='\n')
        elif name == 'quality_audit.json':
            path.write_text(json.dumps({
                'year': 2025,
                'fares': [{'year': 2025, 'quarter': q} for q in (1, 2)],
                'operations': [
                    {'year': 2025, 'month': m} for m in range(1, 7)
                ],
                'verified_input_count': 10,
                'source_months_complete': True,
                'panel': {'by_sample': {
                    'primary': {
                        'fare_routes': 2, 'operations_routes': 2,
                        'matched': 2 if panel_mismatch else 1,
                        'fare_only': 1, 'operations_only': 1,
                    },
                    'broad_fare_bounds': {
                        'fare_routes': 2, 'operations_routes': 2,
                        'matched': 1, 'fare_only': 1, 'operations_only': 1,
                    },
                }, 'fare_reporting_carriers': 2,
                    'operations_reporting_carriers': 1},
            }) + '\n', encoding='utf-8')
        else:
            pd.DataFrame({'year': [2025]}).to_csv(
                path, index=False, lineterminator='\n')
    hashes = {
        name: hashlib.sha256((annual_dir / name).read_bytes()).hexdigest()
        for name in EXPECTED_LATER_FILES
    }
    (annual_dir / 'verification.json').write_text(json.dumps({
        'successful_full_raw_builds': 2,
        'compared_output_files': 11,
        'byte_identical': True,
        'output_sha256': hashes,
    }) + '\n', encoding='utf-8')
    if corrupt:
        (annual_dir / 'route_quarter_panel.csv').write_text(
            'corrupt\n', encoding='utf-8')


def test_build_history_publishes_only_after_verification(tmp_path):
    from src.stage6.history import build_history

    root = tmp_path / 'stage6'
    _write_verified_year(root)
    output = root / 'history'

    audit = build_history(root, output, expected_years=(2025,))

    assert sorted(path.name for path in output.iterdir()) == [
        'annual_summary.csv', 'carrier_presence.csv', 'quality_audit.json',
        'quarterly_summary.csv',
    ]
    assert pd.read_csv(output / 'annual_summary.csv').loc[0, 'national_flights'] == 60
    presence = pd.read_csv(
        output / 'carrier_presence.csv',
        dtype={'carrier_id': str, 'carrier_code': str})
    assert presence.loc[presence.source.eq('DB1B'), 'carrier_id'].tolist() == ['01', 'BB']
    assert presence.loc[presence.source.eq('BTS on-time'), 'carrier_code'].tolist() == ['01']
    assert audit['verified_years'] == [2025]
    assert audit['declared_horizon'] == '2025_Q1_through_2025_Q2'
    assert audit['full_horizon_complete'] is False
    assert audit['reconciliation']['annual_equals_quarterly'] is True
    assert audit['horizon_totals']['national_flights'] == 60


def test_default_history_cannot_publish_only_the_available_subset(tmp_path):
    from src.stage6.history import build_history
    root = tmp_path/'stage6'
    _write_verified_year(root)
    output = root/'history'
    with pytest.raises(ValueError, match='Missing per-year verification'):
        build_history(root, output)
    assert not output.exists()


def test_subset_history_rejects_gaps_in_its_labelled_span(tmp_path):
    from src.stage6.history import build_history
    with pytest.raises(ValueError, match='consecutive'):
        build_history(tmp_path/'stage6', tmp_path/'summary', expected_years=(2010, 2012))


def test_build_history_rejects_hash_mismatch_without_replacing_output(tmp_path):
    from src.stage6.history import build_history

    root = tmp_path / 'stage6'
    _write_verified_year(root, corrupt=True)
    output = root / 'history'
    output.mkdir()
    marker = output / 'existing.txt'
    marker.write_text('preserve me', encoding='utf-8')

    with pytest.raises(ValueError, match='hash mismatch'):
        build_history(root, output, expected_years=(2025,))

    assert marker.read_text(encoding='utf-8') == 'preserve me'


def test_build_history_rejects_counts_that_do_not_reconcile_to_quality_audit(tmp_path):
    from src.stage6.history import build_history

    root = tmp_path / 'stage6'
    _write_verified_year(root, panel_mismatch=True)

    with pytest.raises(ValueError, match='does not reconcile'):
        build_history(root, root / 'history', expected_years=(2025,))

    assert not (root / 'history').exists()


@pytest.mark.parametrize('relative_output', ['.', 'annual_2025', 'annual_2025/nested'])
def test_build_history_rejects_output_overlapping_consumed_directories(
        tmp_path, relative_output):
    from src.stage6.history import build_history

    root = tmp_path / 'stage6'
    _write_verified_year(root)
    verification_before = (root / 'annual_2025' / 'verification.json').read_bytes()

    with pytest.raises(ValueError, match='must not overlap'):
        build_history(root, root / relative_output, expected_years=(2025,))

    assert (root / 'annual_2025' / 'verification.json').read_bytes() == verification_before
