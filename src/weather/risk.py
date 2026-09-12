"""Historical seasonal exposure; this is not a quote-time forecast vintage."""
import numpy as np
import pandas as pd

WEATHER_COLS = ['precipitation_sum', 'snowfall_sum', 'wind_speed_10m_max']


def adverse_days(daily):
    valid = daily[WEATHER_COLS].notna().all(axis=1)
    adverse = ((daily.precipitation_sum >= 10) | (daily.snowfall_sum >= 5)
               | (daily.wind_speed_10m_max >= 15)).astype(float)
    return adverse.where(valid, np.nan)


def prior_season_risk(daily, year, quarter):
    dates = pd.to_datetime(daily.date)
    if dates.duplicated().any():
        raise ValueError('duplicate weather dates')
    if quarter not in (1, 2, 3, 4):
        raise ValueError('invalid quarter')
    expected = pd.date_range(f'{year-3}-01-01', f'{year-1}-12-31')
    expected = expected[expected.quarter == quarter]
    indexed = daily.assign(date=dates).set_index('date')
    season = indexed.reindex(expected)
    adverse = adverse_days(season)
    coverage = float(adverse.notna().sum() / len(expected))
    yearly_coverage = adverse.notna().groupby(adverse.index.year).mean()
    valid_dates = adverse.index[adverse.notna()]
    return {'risk': float(adverse.mean()) if coverage >= .95 and yearly_coverage.min() >= .95 else np.nan,
            'coverage': coverage, 'expected_days': len(expected),
            'minimum_year_coverage': float(yearly_coverage.min()),
            'valid_days': int(adverse.notna().sum()),
            'max_input_date': valid_dates.max().date().isoformat() if len(valid_dates) else None,
            'latest_expected_date': expected.max().date().isoformat()}
