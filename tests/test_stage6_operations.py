import numpy as np
import pandas as pd
import pytest
import zipfile


def flight_rows():
    return pd.DataFrame({
        'FlightDate': ['2024-01-01']*6, 'Year': [2024]*6, 'Month': [1]*6,
        'Reporting_Airline': ['UA']*6, 'DOT_ID_Reporting_Airline': [19977]*6,
        'Flight_Number_Reporting_Airline': list(range(1, 7)),
        'OriginAirportID': [13930]*6, 'DestAirportID': [12892]*6,
        'Origin': ['ORD']*6, 'Dest': ['LAX']*6, 'CRSDepTime': [1000]*6,
        'Cancelled': [0, 0, 0, 1, 0, 0], 'Diverted': [0, 0, 0, 0, 1, 0],
        'ArrDelay': [-5., 15., 60., np.nan, np.nan, np.nan],
        'Flights': [1]*6,
    })


def test_operational_outcomes_use_separate_denominators_and_preserve_missingness():
    from src.stage6.operations import summarize_operations
    cells, audit = summarize_operations(flight_rows(), 2024, 1)
    row = cells.iloc[0]
    assert row.flights == 6 and row.cancelled == 1 and row.diverted == 1
    assert row.delay_observed == 3 and row.delay_missing_eligible == 1
    assert row.delayed_15 == 2 and row.delayed_60 == 1
    assert row.arrival_delay_sum == 70
    assert row.cancellation_rate == pytest.approx(1/6)
    assert row.diversion_rate == pytest.approx(1/6)
    assert row.delay_15_rate == pytest.approx(2/3)
    assert row.mean_arrival_delay == pytest.approx(70/3)
    assert audit['duplicate_rows'] == 0


def test_no_valid_arrivals_produces_missing_delay_rate_not_zero():
    from src.stage6.operations import summarize_operations
    cells, _ = summarize_operations(flight_rows().iloc[3:], 2024, 1)
    assert pd.isna(cells.iloc[0].delay_15_rate)
    assert cells.iloc[0].delay_observed == 0


@pytest.mark.parametrize('column,value', [('Cancelled', np.nan), ('Diverted', 2), ('ArrDelay', np.inf)])
def test_invalid_operating_flags_and_infinite_delay_fail(column, value):
    from src.stage6.operations import summarize_operations
    rows = flight_rows()
    rows.loc[0, column] = value
    with pytest.raises(ValueError):
        summarize_operations(rows, 2024, 1)


def test_wrong_period_fails_before_aggregation():
    from src.stage6.operations import summarize_operations
    rows = flight_rows()
    rows.loc[0, 'FlightDate'] = '2024-02-01'
    with pytest.raises(ValueError, match='period'):
        summarize_operations(rows, 2024, 1)


def test_duplicate_flight_records_are_not_silently_counted_or_dropped():
    from src.stage6.operations import summarize_operations
    rows = flight_rows()
    with pytest.raises(ValueError, match='duplicate'):
        summarize_operations(pd.concat([rows, rows.iloc[[0]]]), 2024, 1)


def test_reporting_carriers_remain_separate():
    from src.stage6.operations import summarize_operations
    rows = flight_rows()
    rows.loc[0, 'Reporting_Airline'] = 'AA'
    rows.loc[0, 'DOT_ID_Reporting_Airline'] = 19805
    cells, _ = summarize_operations(rows, 2024, 1)
    assert cells.set_index('Reporting_Airline').flights.to_dict() == {'AA': 1, 'UA': 5}


def test_streaming_counts_national_rows_and_scopes_only_compact_output(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows()
    extra = rows.iloc[[0]].copy()
    extra['Origin'] = 'BOS'
    extra['OriginAirportID'] = 10721
    path = tmp_path/'flights.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('readme.html', 'BTS source documentation placeholder in fixture')
        archive.writestr('flights.csv', pd.concat([rows, extra]).to_csv(index=False))
    cells, national, audit = read_operations(path, 2024, 1, airports=['ORD', 'LAX'], chunksize=2)
    assert cells.flights.sum() == 6
    assert national.flights.sum() == 7
    assert audit['raw_rows'] == 7 and audit['selected_rows'] == 6
    assert national.delay_observed.sum() == 4
    assert cells.iloc[0].delay_15_rate == pytest.approx(2/3)


def test_streaming_detects_duplicate_across_chunk_boundaries(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows()
    path = tmp_path/'flights.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('flights.csv', pd.concat([rows, rows.iloc[[0]]]).to_csv(index=False))
    with pytest.raises(ValueError, match='duplicate'):
        read_operations(path, 2024, 1, airports=['ORD', 'LAX'], chunksize=2)


def _write_operations_zip(path, rows):
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('flights.csv', rows.to_csv(index=False))


def test_unique_missing_scheduled_departure_preserves_national_and_scoped_outcomes(tmp_path):
    from src.stage6.operations import read_operations, summarize_operations
    rows = flight_rows().iloc[[0, 1, 2]].copy()
    rows.loc[0, 'CRSDepTime'] = np.nan
    rows.loc[0, 'DepTime'] = 908
    rows.loc[2, ['Origin', 'Dest']] = ['AUS', 'HOU']
    rows.loc[2, ['OriginAirportID', 'DestAirportID']] = [10423, 12191]
    rows.loc[2, 'CRSDepTime'] = np.nan
    original = rows.copy(deep=True)
    summarized, _ = summarize_operations(rows, 2024, 1)
    assert summarized.flights.sum() == 3
    pd.testing.assert_frame_equal(rows, original)
    path = tmp_path/'missing-schedule.zip'
    _write_operations_zip(path, rows)

    scoped, national, audit = read_operations(
        path, 2024, 1, airports=['ORD', 'LAX'], chunksize=1)

    assert scoped.flights.sum() == 2
    assert scoped.delay_observed.sum() == 2
    assert scoped.delayed_15.sum() == 1
    assert national.flights.sum() == 3
    assert national.delay_observed.sum() == 3
    assert national.delayed_15.sum() == 2
    assert audit['missing_scheduled_departure_national'] == 2
    assert audit['missing_scheduled_departure_selected'] == 1
    assert 'unique' in audit['incomplete_key_policy']
    pd.testing.assert_frame_equal(rows, original)


def test_month_without_missing_schedule_preserves_legacy_audit_shape(tmp_path):
    from src.stage6.operations import read_operations
    path = tmp_path/'complete-schedule.zip'
    _write_operations_zip(path, flight_rows())

    _, _, audit = read_operations(path, 2024, 1, chunksize=2)

    assert 'missing_scheduled_departure_national' not in audit
    assert 'missing_scheduled_departure_selected' not in audit
    assert 'incomplete_key_policy' not in audit


@pytest.mark.parametrize('missing_first', [True, False])
def test_missing_schedule_collision_with_complete_key_fails_in_both_chunk_orders(
        tmp_path, missing_first):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0, 0]].copy()
    rows['CRSDepTime'] = [np.nan, 1100] if missing_first else [1100, np.nan]
    path = tmp_path/'missing-complete-collision.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='incomplete.*collision'):
        read_operations(path, 2024, 1, chunksize=1)


@pytest.mark.parametrize('chunksize', [1, 2])
def test_two_missing_schedules_with_same_core_fail_within_or_across_chunks(
        tmp_path, chunksize):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0, 0]].copy()
    rows['CRSDepTime'] = np.nan
    path = tmp_path/'missing-missing-collision.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='incomplete.*collision'):
        read_operations(path, 2024, 1, chunksize=chunksize)


def test_complete_rows_may_share_core_when_scheduled_departures_differ(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0, 0]].copy()
    rows['CRSDepTime'] = [1000, 1100]
    path = tmp_path/'valid-same-core.zip'
    _write_operations_zip(path, rows)

    _, national, audit = read_operations(path, 2024, 1, chunksize=1)

    assert national.flights.sum() == 2
    assert audit['duplicate_rows'] == 0


def test_missing_non_schedule_identity_still_fails(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0]].copy()
    rows.loc[0, 'OriginAirportID'] = np.nan
    path = tmp_path/'missing-other-identity.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='Missing operations identity'):
        read_operations(path, 2024, 1, chunksize=1)
