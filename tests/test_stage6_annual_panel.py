import zipfile

import numpy as np
import pandas as pd
import pytest


def operations_rows():
    return pd.DataFrame({
        'FlightDate': ['2010-01-01', '2010-01-02', '2010-01-03'],
        'Year': [2010] * 3,
        'Month': [1] * 3,
        'Reporting_Airline': ['AA', 'AA', 'UA'],
        'DOT_ID_Reporting_Airline': [19805, 19805, 19977],
        'Flight_Number_Reporting_Airline': [1, 2, 3],
        'OriginAirportID': [100, 100, 300],
        'DestAirportID': [200, 200, 400],
        'Origin': ['OLD', 'OLD', 'AAA'],
        'Dest': ['NEW', 'NEW', 'BBB'],
        'CRSDepTime': [800, 900, 1000],
        'Cancelled': [0, 1, 0],
        'Diverted': [0, 0, 0],
        'ArrDelay': [20.0, np.nan, 5.0],
        'Flights': [1, 1, 1],
    })


def test_read_operations_airport_ids_override_mutable_code_scope(tmp_path):
    from src.stage6.operations import read_operations

    path = tmp_path / 'operations.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('operations.csv', operations_rows().to_csv(index=False))

    cells, national, audit = read_operations(
        path, 2010, 1, airports=['AAA', 'BBB'], airport_ids=[100, 200], chunksize=2)

    assert cells[['OriginAirportID', 'DestAirportID', 'flights']].to_dict('records') == [
        {'OriginAirportID': 100, 'DestAirportID': 200, 'flights': 2}
    ]
    assert national.flights.sum() == 3
    assert audit['selected_airport_ids'] == [100, 200]
    assert 'selected_airports' not in audit
    assert audit['selected_rows'] == 2


def monthly_cells():
    return pd.DataFrame({
        'Year': [2010, 2010, 2010],
        'Month': [1, 2, 2],
        'DOT_ID_Reporting_Airline': [1, 1, 2],
        'Reporting_Airline': ['XX', 'XY', 'YY'],
        'OriginAirportID': [100, 100, 100],
        'DestAirportID': [200, 200, 200],
        'Origin': ['OLD', 'NEW', 'NEW'],
        'Dest': ['DST', 'DST', 'DST'],
        'flights': [10, 30, 10],
        'cancelled': [1, 6, 0],
        'diverted': [0, 3, 0],
        'cancelled_and_diverted': [0, 0, 0],
        'delay_observed': [8, 20, 5],
        'delay_missing_eligible': [1, 1, 5],
        'delayed_15': [4, 5, 5],
        'delayed_60': [2, 1, 0],
        'arrival_delay_sum': [80.0, 100.0, 25.0],
    })


def test_quarterly_operations_sums_counts_before_recomputing_rates():
    from src.stage6.annual_panel import quarterly_operations

    row = quarterly_operations(monthly_cells()).iloc[0]

    assert row.Year == 2010 and row.Quarter == 1
    assert row.flights == 50 and row.cancelled == 7
    assert row.months_observed == 2
    assert row.cancellation_rate == pytest.approx(7 / 50)
    assert row.delay_15_rate == pytest.approx(14 / 33)
    assert row.mean_arrival_delay == pytest.approx(205 / 33)


def test_quarterly_operations_rejects_duplicate_carrier_month_route_ids_despite_aliases():
    from src.stage6.annual_panel import quarterly_operations

    rows = monthly_cells().iloc[[0]].copy()
    alias = rows.copy()
    alias['Reporting_Airline'] = 'RENAMED'
    alias['Origin'] = 'NEW'

    with pytest.raises(ValueError, match='carrier-month route'):
        quarterly_operations(pd.concat([rows, alias], ignore_index=True))


def fare_cells():
    return pd.DataFrame([
        {'Year': 2010, 'Quarter': 1, 'OriginAirportID': 100, 'DestAirportID': 200,
         'RPCarrier': 'AA', 'sample': 'primary', 'passengers': 20.0, 'records': 2,
         'fare_total': 2000.0, 'fare_square_total': 200000.0,
         'fare_mean': 100.0, 'fare_variance': 0.0, 'low_support': True},
        {'Year': 2010, 'Quarter': 1, 'OriginAirportID': 100, 'DestAirportID': 200,
         'RPCarrier': 'BB', 'sample': 'primary', 'passengers': 40.0, 'records': 4,
         'fare_total': 8000.0, 'fare_square_total': 1600000.0,
         'fare_mean': 200.0, 'fare_variance': 0.0, 'low_support': False},
        {'Year': 2010, 'Quarter': 1, 'OriginAirportID': 100, 'DestAirportID': 200,
         'RPCarrier': 'AA', 'sample': 'broad_fare_bounds', 'passengers': 10.0,
         'records': 1, 'fare_total': 500.0, 'fare_square_total': 25000.0,
         'fare_mean': 50.0, 'fare_variance': 0.0, 'low_support': True},
        {'Year': 2010, 'Quarter': 1, 'OriginAirportID': 500, 'DestAirportID': 600,
         'RPCarrier': 'CC', 'sample': 'primary', 'passengers': 35.0, 'records': 3,
         'fare_total': 4200.0, 'fare_square_total': 504000.0,
         'fare_mean': 120.0, 'fare_variance': 0.0, 'low_support': False},
        {'Year': 2010, 'Quarter': 1, 'OriginAirportID': 500, 'DestAirportID': 600,
         'RPCarrier': 'CC', 'sample': 'broad_fare_bounds', 'passengers': 35.0,
         'records': 3, 'fare_total': 4200.0, 'fare_square_total': 504000.0,
         'fare_mean': 120.0, 'fare_variance': 0.0, 'low_support': False},
    ])


def test_join_annual_panel_aggregates_roles_independently_and_preserves_unmatched():
    from src.stage6.annual_panel import join_annual_panel

    operations = monthly_cells()
    extra = operations.iloc[[0]].copy()
    extra['OriginAirportID'] = 700
    extra['DestAirportID'] = 800
    panel, audit = join_annual_panel(fare_cells(), pd.concat([operations, extra]))

    primary = panel.loc[panel['sample'].eq('primary')].set_index(
        ['OriginAirportID', 'DestAirportID'])
    matched = primary.loc[(100, 200)]
    assert matched.passengers == 60
    assert matched.fare_mean == pytest.approx(10000 / 60)
    assert matched.fare_variance == pytest.approx(1800000 / 60 - (10000 / 60) ** 2)
    assert matched.flights == 50
    assert matched['coverage'] == 'matched'
    assert primary.loc[(500, 600), 'coverage'] == 'fare_only'
    assert primary.loc[(700, 800), 'coverage'] == 'operations_only'
    assert pd.isna(primary.loc[(500, 600), 'flights'])
    assert pd.isna(primary.loc[(700, 800), 'fare_mean'])
    assert set(panel.loc[panel.OriginAirportID.eq(700), 'sample']) == {
        'primary', 'broad_fare_bounds'
    }
    assert audit['by_sample']['primary'] == {
        'fare_routes': 2, 'operations_routes': 2, 'matched': 1,
        'fare_only': 1, 'operations_only': 1,
    }
    assert audit['fare_reporting_carriers'] == 3
    assert audit['operations_reporting_carriers'] == 2


def test_join_annual_panel_rejects_duplicate_fare_carrier_cells():
    from src.stage6.annual_panel import join_annual_panel

    fares = fare_cells()
    with pytest.raises(ValueError, match='fare carrier'):
        join_annual_panel(pd.concat([fares, fares.iloc[[0]]]), monthly_cells())


def test_join_annual_panel_keeps_declared_sample_when_it_has_no_fare_rows():
    from src.stage6.annual_panel import join_annual_panel

    broad_only = fare_cells().loc[lambda frame: frame['sample'].eq('broad_fare_bounds')]
    panel, audit = join_annual_panel(broad_only, monthly_cells())

    primary = panel.loc[panel['sample'].eq('primary')]
    assert len(primary) == 1
    assert primary.iloc[0]['coverage'] == 'operations_only'
    assert pd.isna(primary.iloc[0].fare_mean)
    assert audit['by_sample']['primary'] == {
        'fare_routes': 0, 'operations_routes': 1, 'matched': 0,
        'fare_only': 0, 'operations_only': 1,
    }
