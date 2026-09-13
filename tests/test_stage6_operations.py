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


def test_streaming_rejects_conflicting_duplicate_across_chunk_boundaries(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows()
    duplicate = rows.iloc[[0]].copy()
    duplicate['ArrDelay'] = 12
    path = tmp_path/'flights.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('flights.csv', pd.concat([rows, duplicate]).to_csv(index=False))
    with pytest.raises(ValueError, match='duplicate.*conflicting consumed fields'):
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
    assert 'missing_flight_number_national' not in audit
    assert 'missing_flight_number_selected' not in audit
    assert 'missing_flight_number_policy' not in audit
    assert 'retained_rows' not in audit
    assert 'repeated_key_rows_removed_national' not in audit
    assert 'repeated_key_rows_removed_selected' not in audit
    assert 'repeated_key_groups_national' not in audit
    assert 'repeat_resolution_policy' not in audit


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


@pytest.mark.parametrize('chunksize', [1, 20])
@pytest.mark.parametrize('duplicate_first', [False, True])
def test_equivalent_complete_keys_with_identical_missingness_are_coalesced(
        tmp_path, chunksize, duplicate_first):
    from src.stage6.operations import read_operations
    original = flight_rows().iloc[[3]].copy()
    original['Tail_Number'] = 'N11111'
    duplicate = original.copy()
    duplicate['Tail_Number'] = 'N22222'
    rows = pd.concat([duplicate, original] if duplicate_first else [original, duplicate])
    path = tmp_path/f'equivalent-{chunksize}-{duplicate_first}.zip'
    _write_operations_zip(path, rows)

    scoped, national, audit = read_operations(
        path, 2024, 1, airports=['ORD', 'LAX'], chunksize=chunksize)

    assert scoped.flights.sum() == 1
    assert scoped.cancelled.sum() == 1
    assert scoped.delay_observed.sum() == 0
    assert national.flights.sum() == 1
    assert audit['raw_rows'] == 2
    assert audit['retained_rows'] == 1
    assert audit['selected_rows'] == 1
    assert audit['repeated_key_rows_removed_national'] == 1
    assert audit['repeated_key_rows_removed_selected'] == 1
    assert audit['repeated_key_groups_national'] == 1
    assert 'consumed' in audit['repeat_resolution_policy']
    assert 'full source row' in audit['repeat_resolution_policy']


@pytest.mark.parametrize('column,value', [
    ('ArrDelay', 12),
    ('Reporting_Airline', 'AA'),
    ('Origin', 'MDW'),
])
def test_complete_key_conflicting_consumed_outcome_or_group_identity_fails(
        tmp_path, column, value):
    from src.stage6.operations import read_operations
    original = flight_rows().iloc[[0]].copy()
    duplicate = original.copy()
    duplicate[column] = value
    path = tmp_path/f'conflicting-{column}.zip'
    _write_operations_zip(path, pd.concat([original, duplicate]))

    with pytest.raises(ValueError, match='duplicate.*conflicting consumed fields'):
        read_operations(path, 2024, 1, chunksize=1)


@pytest.mark.parametrize('chunksize', [1, 2, 20])
def test_repeat_audit_counts_rows_groups_and_scoped_denominators_once(
        tmp_path, chunksize):
    from src.stage6.operations import read_operations
    selected = flight_rows().iloc[[0]].copy()
    outside = selected.copy()
    outside[['Origin', 'OriginAirportID']] = ['BOS', 10721]
    rows = pd.concat([selected, outside, selected, outside, selected], ignore_index=True)
    path = tmp_path/f'repeat-counts-{chunksize}.zip'
    _write_operations_zip(path, rows)

    scoped, national, audit = read_operations(
        path, 2024, 1, airports=['ORD', 'LAX'], chunksize=chunksize)

    assert scoped.flights.sum() == 1
    assert national.flights.sum() == 2
    assert audit['raw_rows'] == 5
    assert audit['retained_rows'] == 2
    assert audit['selected_rows'] == 1
    assert audit['repeated_key_rows_removed_national'] == 3
    assert audit['repeated_key_rows_removed_selected'] == 2
    assert audit['repeated_key_groups_national'] == 2
    assert audit['repeated_key_groups_selected'] == 1


def test_equivalent_repeat_results_and_audit_are_chunksize_invariant(tmp_path):
    from src.stage6.operations import read_operations
    selected = flight_rows().iloc[[0, 1]].copy()
    rows = pd.concat([selected, selected.iloc[[0]], selected.iloc[[1]]], ignore_index=True)
    path = tmp_path/'chunksize-invariant.zip'
    _write_operations_zip(path, rows)

    small = read_operations(path, 2024, 1, airports=['ORD', 'LAX'], chunksize=1)
    large = read_operations(path, 2024, 1, airports=['ORD', 'LAX'], chunksize=20)

    pd.testing.assert_frame_equal(small[0], large[0])
    pd.testing.assert_frame_equal(small[1], large[1])
    assert small[2] == large[2]


@pytest.mark.parametrize('missing_first', [True, False])
@pytest.mark.parametrize('chunksize', [1, 20])
def test_equivalent_complete_repeat_never_resolves_missing_schedule_core_collision(
        tmp_path, missing_first, chunksize):
    from src.stage6.operations import read_operations
    complete = flight_rows().iloc[[0]].copy()
    missing = complete.copy()
    missing['CRSDepTime'] = np.nan
    parts = [missing, complete, complete] if missing_first else [complete, complete, missing]
    path = tmp_path/f'missing-repeat-{missing_first}-{chunksize}.zip'
    _write_operations_zip(path, pd.concat(parts, ignore_index=True))

    with pytest.raises(ValueError, match='incomplete.*collision'):
        read_operations(path, 2024, 1, chunksize=chunksize)


def _ambiguous_rows():
    selected = flight_rows().iloc[[0]].copy()
    selected_conflict = selected.copy()
    selected_conflict['ArrDelay'] = -12.0
    selected_repeat = selected.copy()
    outside = selected.copy()
    outside[['Origin', 'Dest']] = ['DEN', 'XNA']
    outside[['OriginAirportID', 'DestAirportID']] = [11292, 15919]
    outside['Flight_Number_Reporting_Airline'] = 3624
    outside['CRSDepTime'] = 2007
    outside_conflict = outside.copy()
    outside_conflict['ArrDelay'] = np.nan
    retained = selected.copy()
    retained['Flight_Number_Reporting_Airline'] = 99
    missing_schedule = selected.copy()
    missing_schedule['Flight_Number_Reporting_Airline'] = 100
    missing_schedule['CRSDepTime'] = np.nan
    return pd.concat([
        selected, selected_conflict, selected_repeat,
        outside, outside_conflict, retained, missing_schedule,
    ], ignore_index=True)


@pytest.mark.parametrize('reverse', [False, True])
@pytest.mark.parametrize('chunksize', [1, 3, 20])
def test_quarantine_excludes_all_ambiguous_copies_with_deterministic_audit(
        tmp_path, reverse, chunksize):
    from src.stage6.operations import read_operations
    rows = _ambiguous_rows()
    if reverse:
        rows = rows.iloc[::-1].reset_index(drop=True)
    path = tmp_path/f'quarantine-{reverse}-{chunksize}.zip'
    _write_operations_zip(path, rows)

    scoped, national, audit = read_operations(
        path, 2024, 1, airports=['ORD', 'LAX'], chunksize=chunksize,
        conflict_policy='quarantine')

    assert scoped.flights.sum() == 2
    assert national.flights.sum() == 2
    assert audit['raw_rows'] == 7
    assert audit['retained_rows'] == 2
    assert audit['selected_rows'] == 2
    assert audit['ambiguous_key_rows_excluded_national'] == 5
    assert audit['ambiguous_key_rows_excluded_selected'] == 3
    assert audit['ambiguous_key_groups_national'] == 2
    assert audit['ambiguous_key_groups_selected'] == 1
    assert 'repeated_key_rows_removed_national' not in audit
    assert audit['missing_scheduled_departure_national'] == 1
    assert audit['missing_scheduled_departure_selected'] == 1
    assert 'retained reported analysis units' in audit['ambiguity_policy']
    groups = audit['ambiguous_complete_key_groups']
    assert len(groups) == 2
    assert [group['rows'] for group in groups] == [3, 2]
    assert [group['consumed_variant_count'] for group in groups] == [2, 2]
    selected_group = next(group for group in groups
                          if group['key']['Flight_Number_Reporting_Airline'] == 1)
    assert [variant['rows'] for variant in selected_group['consumed_variants']] == [1, 2]
    assert {variant['values']['ArrDelay']
            for variant in selected_group['consumed_variants']} == {-12.0, -5.0}
    outside_group = next(group for group in groups
                         if group['key']['Flight_Number_Reporting_Airline'] == 3624)
    assert {variant['values']['ArrDelay']
            for variant in outside_group['consumed_variants']} == {None, -5.0}


def test_quarantine_audit_is_identical_across_row_and_chunk_order(tmp_path):
    from src.stage6.operations import read_operations
    rows = _ambiguous_rows()
    paths = [tmp_path/'forward.zip', tmp_path/'reverse.zip']
    _write_operations_zip(paths[0], rows)
    _write_operations_zip(paths[1], rows.iloc[::-1])

    forward = read_operations(
        paths[0], 2024, 1, airports=['ORD', 'LAX'], chunksize=1,
        conflict_policy='quarantine')[2]
    reverse = read_operations(
        paths[1], 2024, 1, airports=['ORD', 'LAX'], chunksize=20,
        conflict_policy='quarantine')[2]

    ignored = {'input_sha256', 'csv_member'}
    assert {key: value for key, value in forward.items() if key not in ignored} == {
        key: value for key, value in reverse.items() if key not in ignored}


def test_quarantine_still_rejects_missing_schedule_core_collision(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0, 0]].copy()
    rows['CRSDepTime'] = [np.nan, 1100]
    path = tmp_path/'missing-core-collision-quarantine.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='incomplete.*collision'):
        read_operations(path, 2024, 1, chunksize=1,
                        conflict_policy='quarantine')


def test_quarantine_validates_invalid_outcome_before_excluding_conflict(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0, 0]].copy().reset_index(drop=True)
    rows['ArrDelay'] = [-5.0, 12.0]
    rows.loc[1, 'Diverted'] = 2
    path = tmp_path/'invalid-quarantined-row.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='flag'):
        read_operations(path, 2024, 1, chunksize=1,
                        conflict_policy='quarantine')


def test_unknown_conflict_policy_fails_before_reading(tmp_path):
    from src.stage6.operations import read_operations
    with pytest.raises(ValueError, match='conflict_policy'):
        read_operations(tmp_path/'missing.zip', 2024, 1,
                        conflict_policy='choose_first')


def test_unique_missing_flight_number_is_retained_only_in_quarantine(tmp_path):
    from src.stage6.operations import read_operations, summarize_operations
    rows = flight_rows().iloc[[0, 1]].copy().reset_index(drop=True)
    rows.loc[0, 'Flight_Number_Reporting_Airline'] = np.nan
    rows.loc[1, 'CRSDepTime'] = 1100
    path = tmp_path/'missing-flight-number.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='Missing operations identity'):
        read_operations(path, 2024, 1, chunksize=1)
    with pytest.raises(ValueError, match='Missing operations identity'):
        summarize_operations(rows, 2024, 1)
    assert summarize_operations(
        rows, 2024, 1, allow_missing_flight_number=True)[1]['rows'] == 2

    scoped, national, audit = read_operations(
        path, 2024, 1, airports=['ORD', 'LAX'], chunksize=1,
        conflict_policy='quarantine')

    assert scoped.flights.sum() == 2
    assert national.flights.sum() == 2
    assert audit['missing_flight_number_national'] == 1
    assert audit['missing_flight_number_selected'] == 1
    assert 'unique across the complete monthly source' in audit['missing_flight_number_policy']
    assert 'imputation' in audit['missing_flight_number_policy']


@pytest.mark.parametrize('missing_first', [False, True])
@pytest.mark.parametrize('chunksize', [1, 20])
def test_missing_flight_number_projection_collision_fails_across_orders(
        tmp_path, missing_first, chunksize):
    from src.stage6.operations import read_operations
    complete = flight_rows().iloc[[0]].copy()
    missing = complete.copy()
    missing['Flight_Number_Reporting_Airline'] = np.nan
    rows = pd.concat([missing, complete] if missing_first else [complete, missing],
                     ignore_index=True)
    path = tmp_path/f'missing-number-collision-{missing_first}-{chunksize}.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='incomplete.*collision'):
        read_operations(path, 2024, 1, chunksize=chunksize,
                        conflict_policy='quarantine')


@pytest.mark.parametrize('chunksize', [1, 20])
def test_two_missing_flight_numbers_with_same_projection_fail(tmp_path, chunksize):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0, 0]].copy()
    rows['Flight_Number_Reporting_Airline'] = np.nan
    path = tmp_path/f'two-missing-numbers-{chunksize}.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='incomplete.*collision'):
        read_operations(path, 2024, 1, chunksize=chunksize,
                        conflict_policy='quarantine')


def test_both_schedule_and_flight_number_missing_always_fails(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0]].copy()
    rows[['CRSDepTime', 'Flight_Number_Reporting_Airline']] = np.nan
    path = tmp_path/'both-partial-identities.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='both CRSDepTime and flight number'):
        read_operations(path, 2024, 1, conflict_policy='quarantine')


@pytest.mark.parametrize('missing_schedule_first', [False, True])
@pytest.mark.parametrize('chunksize', [1, 20])
def test_complementary_partial_keys_on_same_base_fail_regardless_known_values(
        tmp_path, missing_schedule_first, chunksize):
    from src.stage6.operations import read_operations
    missing_schedule = flight_rows().iloc[[0]].copy()
    missing_schedule['CRSDepTime'] = np.nan
    missing_schedule['Flight_Number_Reporting_Airline'] = 700
    missing_number = flight_rows().iloc[[0]].copy()
    missing_number['CRSDepTime'] = 1234
    missing_number['Flight_Number_Reporting_Airline'] = np.nan
    parts = ([missing_schedule, missing_number] if missing_schedule_first
             else [missing_number, missing_schedule])
    path = tmp_path/f'complementary-{missing_schedule_first}-{chunksize}.zip'
    _write_operations_zip(path, pd.concat(parts, ignore_index=True))

    with pytest.raises(ValueError, match='partial.*collision'):
        read_operations(path, 2024, 1, chunksize=chunksize,
                        conflict_policy='quarantine')


def test_unrelated_missing_schedule_and_flight_number_are_both_retained(tmp_path):
    from src.stage6.operations import read_operations
    missing_schedule = flight_rows().iloc[[0]].copy()
    missing_schedule['CRSDepTime'] = np.nan
    missing_number = flight_rows().iloc[[1]].copy()
    missing_number['Flight_Number_Reporting_Airline'] = np.nan
    missing_number['FlightDate'] = '2024-01-02'
    path = tmp_path/'unrelated-partial-identities.zip'
    _write_operations_zip(path, pd.concat(
        [missing_schedule, missing_number], ignore_index=True))

    scoped, national, audit = read_operations(
        path, 2024, 1, airports=['ORD', 'LAX'], chunksize=1,
        conflict_policy='quarantine')

    assert scoped.flights.sum() == 2
    assert national.flights.sum() == 2
    assert audit['missing_scheduled_departure_national'] == 1
    assert audit['missing_flight_number_national'] == 1


def test_invalid_flag_on_missing_flight_number_still_fails_preflight(tmp_path):
    from src.stage6.operations import read_operations
    rows = flight_rows().iloc[[0]].copy()
    rows['Flight_Number_Reporting_Airline'] = np.nan
    rows['Cancelled'] = 3
    path = tmp_path/'invalid-missing-number.zip'
    _write_operations_zip(path, rows)

    with pytest.raises(ValueError, match='flag'):
        read_operations(path, 2024, 1, conflict_policy='quarantine')


def test_quarantine_serialized_details_ignore_chunk_numeric_inference(tmp_path):
    import json
    import zipfile
    from src.stage6.operations import read_operations
    rows = _ambiguous_rows()
    path = tmp_path/'integral-lexemes.zip'
    csv = rows.to_csv(index=False).replace('.0,', ',').replace('.0\n', '\n')
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('fixture.csv', csv)
    small = read_operations(path, 2024, 1, chunksize=1,
                            conflict_policy='quarantine')[2]
    large = read_operations(path, 2024, 1, chunksize=20,
                            conflict_policy='quarantine')[2]
    assert json.dumps(small, sort_keys=True) == json.dumps(large, sort_keys=True)
