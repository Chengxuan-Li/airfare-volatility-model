"""Airport-season risk and external realized operating-outcome validation."""
import json
import zipfile

import pandas as pd

from src.config import AIRPORTS, PERIODS, RAW, TABLES
from src.weather.risk import adverse_days, prior_season_risk


def summarize_delay(frame):
    df = frame.copy()
    df['Quarter'] = (df.month - 1) // 3 + 1
    columns = ['arr_flights', 'arr_cancelled', 'arr_del15', 'weather_ct']
    if df[columns].isna().any().any():
        raise ValueError('missing delay counts')
    if (df[columns] < 0).any().any():
        raise ValueError('negative delay counts')
    result = df.groupby(['year', 'Quarter', 'airport'])[columns].sum().reset_index()
    if (result.arr_flights <= 0).any() or (result.arr_cancelled > result.arr_flights).any():
        raise ValueError('invalid flight denominator')
    result['cancellation_rate'] = result.arr_cancelled / result.arr_flights
    result['delay_rate'] = result.arr_del15 / result.arr_flights
    result['weather_delay_rate'] = result.weather_ct / result.arr_flights
    return result.rename(columns={'year': 'Year'})


def build_weather_panel():
    TABLES.mkdir(parents=True, exist_ok=True)
    results = []
    for airport in AIRPORTS:
        payload = json.loads((RAW/'weather'/f'{airport}_2020_2024.json').read_text(encoding='utf-8'))
        units = payload['daily_units']
        if units['wind_speed_10m_max'] != 'm/s' or units['precipitation_sum'] != 'mm' or units['snowfall_sum'] != 'cm':
            raise ValueError(f'Unexpected weather units: {units}')
        daily = pd.DataFrame(payload['daily']).rename(columns={'time': 'date'})
        daily['date'] = pd.to_datetime(daily.date)
        adverse = adverse_days(daily)
        for year, quarter in PERIODS:
            prior = prior_season_risk(daily, year, quarter)
            current = (daily.date.dt.year == year) & (daily.date.dt.quarter == quarter)
            result = {'airport': airport, 'Year': year, 'Quarter': quarter, **prior,
                      'realized_adverse_share': float(adverse.loc[current].mean()),
                      'realized_coverage': float(adverse.loc[current].notna().mean()),
                      'timezone': payload['timezone'], 'grid_latitude': payload['latitude'],
                      'grid_longitude': payload['longitude']}
            results.append(result)
    weather = pd.DataFrame(results)
    with zipfile.ZipFile(RAW/'bts_delay_causes_2022_2024.zip') as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith('.csv'))
        with archive.open(name) as f:
            delay = pd.read_csv(f)
    delay = delay.loc[delay.airport.isin(AIRPORTS)].copy()
    if delay.duplicated(['year', 'month', 'carrier', 'airport']).any():
        raise ValueError('duplicate delay-cause airport/carrier/month rows')
    outcomes = summarize_delay(delay)
    result = weather.merge(outcomes, on=['airport', 'Year', 'Quarter'], how='left', validate='one_to_one')
    result.to_csv(TABLES/'airport_weather_validation.csv', index=False)
    return result


def attach_weather(cells, weather):
    result = cells.copy()
    for side, column in [('origin', 'Origin'), ('destination', 'Dest')]:
        selected = weather[['airport', 'Year', 'Quarter', 'risk', 'cancellation_rate']].rename(
            columns={'airport': column, 'risk': f'{side}_risk', 'cancellation_rate': f'{side}_cancel_rate'})
        result = result.merge(selected, on=[column, 'Year', 'Quarter'], how='left', validate='many_to_one')
    # Arithmetic addition propagates missing values, unlike a skipna row mean.
    result['risk'] = (result.origin_risk + result.destination_risk) / 2
    result['risk_max'] = result[['origin_risk', 'destination_risk']].max(axis=1, skipna=False)
    result['route'] = result.Origin + '-' + result.Dest
    result['route_carrier'] = result.route + '_' + result.RPCarrier
    result['period'] = result.Year.astype(str) + 'Q' + result.Quarter.astype(str)
    result.to_csv(TABLES/'pilot_panel.csv', index=False)
    return result
