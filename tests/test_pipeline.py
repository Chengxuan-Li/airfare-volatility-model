import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.acquisition.download import validate_zip, fetch
from src.cleaning.db1b import clean_market, join_ticket, summarize_cells
from src.weather.risk import prior_season_risk, adverse_days
from src.analysis.models import fit_checked, marginal_effects
from src.cleaning.panel import process_quarter
from src.weather.panel import summarize_delay


def market_rows():
    return pd.DataFrame({
        'ItinID': [1, 2, 3, 4], 'MktID': [11, 12, 13, 14],
        'Year': [2024]*4, 'Quarter': [1]*4, 'Origin': ['ord']*4,
        'Dest': ['lax']*4, 'RPCarrier': ['UA']*4, 'MktCoupons': [1]*4,
        'BulkFare': [0]*4, 'Passengers': [1, 3, 1, 0],
        'MktFare': [100., 200., np.nan, 300.], 'MktDistance': [1700]*4})


def test_fares_weight_by_passengers_and_reject_missing_zero_quantity():
    clean, audit = clean_market(market_rows())
    assert len(clean) == 2
    assert audit['input_rows'] == 4 and audit['kept_rows'] == 2
    assert clean.Origin.iloc[0] == 'ORD'
    cell = summarize_cells(clean).iloc[0]
    assert cell.fare_mean == 175
    assert cell.fare_variance == 1875
    assert cell.passengers == 4


def test_bulk_nonstop_and_fare_bounds_are_explicit():
    rows = market_rows().fillna({'MktFare': 100})
    rows.loc[0, 'BulkFare'] = 1
    rows.loc[1, 'MktCoupons'] = 2
    rows.loc[2, 'MktFare'] = 10
    result, audit = clean_market(rows)
    assert result.empty
    assert sum(audit[k] for k in audit if k.startswith('excluded_')) == 4


def test_ticket_keys_include_period_and_prevent_row_multiplication():
    market = market_rows().iloc[:1]
    ticket = pd.DataFrame({'Year': [2023, 2024], 'Quarter': [1, 1],
                           'ItinID': [1, 1], 'DollarCred': [0, 1]})
    result, audit = join_ticket(market, ticket)
    assert len(result) == 1 and result.DollarCred.iloc[0] == 1
    assert audit['unmatched_rows'] == 0
    with pytest.raises(ValueError, match='duplicate'):
        join_ticket(market, pd.concat([ticket, ticket.iloc[[1]]]))


def test_missing_ticket_is_audited_not_silently_credible():
    result, audit = join_ticket(market_rows(), pd.DataFrame(
        {'Year': [2024], 'Quarter': [1], 'ItinID': [1], 'DollarCred': [1]}))
    assert audit['unmatched_rows'] == 3
    assert result.DollarCred.isna().sum() == 3


def test_full_ticket_schema_does_not_replace_market_quantity_or_origin():
    ticket = pd.DataFrame({'Year': [2024], 'Quarter': [1], 'ItinID': [1],
                           'DollarCred': [1], 'Origin': ['JFK'], 'Passengers': [999],
                           'RPCarrier': ['AA'], 'BulkFare': [1]})
    result, _ = join_ticket(market_rows().iloc[:1], ticket)
    assert result.Origin.iloc[0] == 'ord'
    assert result.Passengers.iloc[0] == 1


def weather_frame():
    dates = pd.date_range('2020-01-01', '2024-12-31')
    return pd.DataFrame({'date': dates, 'precipitation_sum': 0.,
                         'snowfall_sum': 0., 'wind_speed_10m_max': 0.})


def test_risk_excludes_target_year_even_when_all_future_days_adverse():
    daily = weather_frame()
    daily.loc[daily.date.dt.year >= 2023, 'precipitation_sum'] = 100
    assert prior_season_risk(daily, 2023, 1)['risk'] == 0
    assert prior_season_risk(daily, 2024, 1)['risk'] == pytest.approx(90/270)


def test_missing_weather_not_zero_and_coverage_uses_calendar_days():
    daily = weather_frame()
    daily.loc[daily.date.dt.year < 2023, 'snowfall_sum'] = np.nan
    assert np.isnan(prior_season_risk(daily, 2023, 1)['risk'])
    assert prior_season_risk(daily, 2023, 1)['coverage'] == 0
    with pytest.raises(ValueError, match='duplicate'):
        prior_season_risk(pd.concat([weather_frame(), weather_frame().iloc[[0]]]), 2023, 1)


def test_thresholds_and_missing_are_not_boolean_false():
    daily = pd.DataFrame({'precipitation_sum': [10, 0, 0, np.nan],
                          'snowfall_sum': [0, 5, 0, 0],
                          'wind_speed_10m_max': [0, 0, 15, 0]})
    values = adverse_days(daily)
    assert values.iloc[:3].tolist() == [1, 1, 1]
    assert np.isnan(values.iloc[3])


def test_each_lagged_quarter_must_meet_coverage_and_max_date_is_observed():
    daily = weather_frame()
    daily.loc[daily.date.between('2021-01-01', '2021-01-11'), 'snowfall_sum'] = np.nan
    assert np.isnan(prior_season_risk(daily, 2023, 1)['risk'])
    daily = weather_frame()
    daily.loc[daily.date == '2022-03-31', 'snowfall_sum'] = np.nan
    assert prior_season_risk(daily, 2023, 1)['max_input_date'] == '2022-03-30'


def test_cached_data_cannot_be_reused_for_different_request(tmp_path):
    from src.acquisition.download import digest
    archive = tmp_path/'valid.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('sample.csv', 'x\n1\n')
    manifest = tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'sha256': digest(archive), 'url': 'https://example.com/old'}))
    with pytest.raises(ValueError, match='request'):
        fetch('https://example.com/new', archive, manifest)


def test_corrupt_download_rejected_and_cached_manifest_checked(tmp_path):
    archive = tmp_path/'test.zip'
    archive.write_text('not a zip')
    with pytest.raises(zipfile.BadZipFile):
        validate_zip(archive)
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('sample.csv', 'a,b\n1,2\n')
    manifest = tmp_path/'manifest.json'
    manifest.write_text(json.dumps({'sha256': 'wrong'}))
    with pytest.raises(ValueError, match='checksum'):
        fetch('https://invalid.example/test.zip', archive, manifest)


def test_singular_model_is_rejected_and_marginals_use_interaction():
    data = pd.DataFrame({'y': [1., 2., 3., 4.], 'x': [1., 2., 3., 4.],
                         'z': [2., 4., 6., 8.], 'route': ['a','a','b','b']})
    with pytest.raises(ValueError, match='rank'):
        fit_checked('y ~ x + z', data)
    params = {'demand_c': 10., 'risk': 20., 'demand_c:risk': -5.}
    assert marginal_effects(params, demand=2, risk=.4) == {'demand_slope': 8., 'risk_effect': 10.}


def test_zip_pipeline_applies_ticket_credibility_and_audits_scope(tmp_path):
    market = market_rows()
    market.loc[0, 'Passengers'] = 40
    market.loc[1, 'Passengers'] = 60
    ticket = pd.DataFrame({'Year': [2024, 2024], 'Quarter': [1, 1],
                           'ItinID': [1, 2], 'DollarCred': [1, 0], 'RoundTrip': [1, 0],
                           'ItinFare': [200, 200]})
    paths = []
    for name, frame in [('Market', market), ('Ticket', ticket)]:
        path = tmp_path / (name + '.zip')
        with zipfile.ZipFile(path, 'w') as z:
            z.writestr(name + '.csv', frame.to_csv(index=False))
        paths.append(path)
    cells, audit = process_quarter(*paths, year=2024, quarter=1, chunksize=2)
    assert len(cells) == 2
    assert set(cells['sample']) == {'primary', 'broad_fare_bounds'}
    assert cells.iloc[0].fare_mean == 100
    assert cells.iloc[0].passengers == 40
    assert audit['ticket_unreliable_rows'] == 1
    assert audit['market_rows_scanned'] == 4


def test_cancel_rate_uses_flight_weighted_counts_not_mean_rates():
    rows = pd.DataFrame({'year': [2024, 2024], 'month': [1, 2], 'airport': ['ORD', 'ORD'],
                         'arr_flights': [100, 900], 'arr_cancelled': [10, 0],
                         'arr_del15': [20, 90], 'weather_ct': [5, 9]})
    result = summarize_delay(rows).iloc[0]
    assert result.cancellation_rate == .01
    assert result.delay_rate == .11
    assert result.weather_delay_rate == .014


@pytest.mark.parametrize('column,value', [('arr_del15',101), ('weather_ct',21)])
def test_impossible_delay_counts_are_rejected(column, value):
    row = {'year': [2024], 'month': [1], 'airport': ['ORD'], 'arr_flights': [100],
           'arr_cancelled': [1], 'arr_del15': [20], 'weather_ct': [5]}
    row[column] = [value]
    with pytest.raises(ValueError, match='delay'):
        summarize_delay(pd.DataFrame(row))
