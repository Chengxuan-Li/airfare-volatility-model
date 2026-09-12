"""Acquire only explicit public pilot inputs, with bounded sequential requests."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from urllib.parse import urlencode

import pandas as pd

from src.acquisition.download import fetch
from src.config import AIRPORTS, MANIFESTS, PERIODS, RAW, bts_path


def acquire_bts(item):
    table, year, quarter = item
    target = bts_path(table, year, quarter)
    return fetch('https://transtats.bts.gov/PREZIP/' + target.name, target,
                 MANIFESTS/f'bts_db1b_{table.lower()}_{year}_q{quarter}.json',
                 source=f'BTS DB1B{table}', params={'year': year, 'quarter': quarter})


def acquire_weather():
    registry = fetch('https://davidmegginson.github.io/ourairports-data/airports.csv',
                     RAW/'ourairports.csv', MANIFESTS/'ourairports.json', source='OurAirports public domain')
    airports = pd.read_csv(registry, low_memory=False)
    for airport in AIRPORTS:
        selected = airports.loc[airports.ident == 'K' + airport]
        if len(selected) != 1:
            raise ValueError(f'Airport coordinate match not unique: {airport}')
        row = selected.iloc[0]
        params = {'latitude': float(row.latitude_deg), 'longitude': float(row.longitude_deg),
                  'start_date': '2020-01-01', 'end_date': '2024-12-31',
                  'daily': 'precipitation_sum,snowfall_sum,wind_speed_10m_max',
                  'wind_speed_unit': 'ms', 'timezone': 'auto', 'models': 'era5'}
        fetch('https://archive-api.open-meteo.com/v1/archive?' + urlencode(params),
              RAW/'weather'/f'{airport}_2020_2024.json', MANIFESTS/f'weather_{airport}.json',
              source='Open-Meteo ERA5 reanalysis, CC BY 4.0', params=params)


def acquire_delay():
    request_file = __import__('pathlib').Path('docs/data/delay_causes_request.json')
    if not request_file.exists():
        raise FileNotFoundError('Verified delay-cause request metadata is required')
    request = json.loads(request_file.read_text(encoding='utf-8'))
    url = request.get('verified_download_url') or request.get('download_url') or request.get('url')
    if not url:
        raise ValueError('No download_url in delay request metadata')
    fetch(url, RAW/'bts_delay_causes_2022_2024.zip', MANIFESTS/'bts_delay_causes.json',
          source='BTS Airline On-Time Statistics and Delay Causes', params=request)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=['bts', 'weather', 'delay', 'all'], default='all')
    args = parser.parse_args()
    if args.kind in ('bts', 'all'):
        jobs = [(table, year, quarter) for year, quarter in PERIODS for table in ('Market', 'Ticket')]
        # Two bounded downloads at most; no worker agent can spend API credits.
        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(acquire_bts, jobs))
    if args.kind in ('weather', 'all'):
        acquire_weather()
    if args.kind in ('delay', 'all'):
        acquire_delay()


if __name__ == '__main__':
    main()
