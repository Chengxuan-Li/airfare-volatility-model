"""Public Stage 5 inputs; finite requests, no paid APIs or credentials."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from urllib.parse import urlencode

import pandas as pd
import requests

from src.acquisition.batch import acquire_bts
from src.acquisition.download import fetch, digest, validate_zip
from src.config import AIRPORTS, RAW, MANIFESTS

T100_URL = 'https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=Nv4+Pn44vr45&gnoyr_VQ=GEE'
FIELDS = ['UNIQUE_CARRIER', 'ORIGIN', 'DEST', 'YEAR', 'QUARTER', 'MONTH', 'CLASS',
          'PASSENGERS', 'SEATS', 'DEPARTURES_SCHEDULED', 'DEPARTURES_PERFORMED',
          'ORIGIN_AIRPORT_ID', 'DEST_AIRPORT_ID']


class HiddenFields(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'input' and a.get('type') == 'hidden' and a.get('name', '').startswith('__'):
            self.values[a['name']] = a.get('value', '')


def hidden(text):
    parser = HiddenFields()
    parser.feed(text)
    if '__VIEWSTATE' not in parser.values:
        raise ValueError('BTS form missing state')
    return parser.values


def t100(year):
    target = RAW/'t100'/f'T_100_Domestic_Segment_All_Carrier_{year}.zip'
    manifest = MANIFESTS/f't100_{year}.json'
    params = {'method': 'ASP.NET three-step POST', 'year': year, 'period': 'All', 'fields': FIELDS}
    if target.exists() and not manifest.exists():
        raise ValueError('Unmanifested T100 input requires provenance review')
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        with requests.Session() as session:
            first = session.get(T100_URL, timeout=(20, 60))
            first.raise_for_status()
            form = {**hidden(first.text), '__EVENTTARGET': 'chkDownloadZip', '__EVENTARGUMENT': '',
                    'cboYear': str(year), 'cboPeriod': 'All', 'chkDownloadZip': 'on'}
            second = session.post(T100_URL, data=form, timeout=(20, 60))
            second.raise_for_status()
            form = {**hidden(second.text), 'cboYear': str(year), 'cboPeriod': 'All',
                    'chkDownloadZip': 'on', 'btnDownload': 'Download', **{f: 'on' for f in FIELDS}}
            response = session.post(T100_URL, data=form, timeout=(20, 120))
            response.raise_for_status()
            if not response.content.startswith(b'PK'):
                raise ValueError('T100 response is not ZIP')
            partial = target.with_suffix('.zip.part')
            partial.write_bytes(response.content)
            validate_zip(partial)
            partial.rename(target)
        # fetch registers provenance for this already validated local POST response;
        # it is never asked to download the form URL as a ZIP.
    return fetch(T100_URL, target, manifest, source='BTS T100 Domestic Segment All Carriers', params=params)


def weather():
    airports = pd.read_csv(RAW/'ourairports.csv', low_memory=False)
    for airport in AIRPORTS:
        selected = airports.loc[airports.ident == 'K'+airport]
        if len(selected) != 1:
            raise ValueError('Airport match not unique')
        row = selected.iloc[0]
        params = {'latitude': float(row.latitude_deg), 'longitude': float(row.longitude_deg),
                  'start_date': '2020-01-01', 'end_date': '2025-12-31',
                  'daily': 'precipitation_sum,snowfall_sum,wind_speed_10m_max',
                  'wind_speed_unit': 'ms', 'timezone': 'auto', 'models': 'era5'}
        fetch('https://archive-api.open-meteo.com/v1/archive?'+urlencode(params),
              RAW/'weather'/f'{airport}_2020_2025.json', MANIFESTS/f'weather_{airport}_2020_2025.json',
              source='Open-Meteo ERA5 reanalysis, CC BY 4.0', params=params)


def verify_inputs():
    names = [f'bts_db1b_{table}_{year}_q{quarter}.json'
             for year in (2023, 2024, 2025) for quarter in ((1, 2) if year == 2025 else (1, 2, 3, 4))
             for table in ('market', 'ticket')]
    names += [f't100_{year}.json' for year in (2023, 2024, 2025)]
    names += [f'weather_{a}_2020_2025.json' for a in AIRPORTS]
    for name in names:
        record = json.loads((MANIFESTS/name).read_text(encoding='utf-8'))
        if digest(record['local_path']) != record['sha256']:
            raise ValueError(f'Input checksum mismatch: {name}')
    print(f'Verified {len(names)} Stage5 input checksums', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=['all', 't100', 'weather', 'fares'], default='all')
    args = parser.parse_args()
    if args.kind in ('all', 'fares'):
        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(acquire_bts, [(t, 2025, q) for q in (1, 2) for t in ('Market', 'Ticket')]))
    if args.kind in ('all', 'weather'):
        weather()
    if args.kind in ('all', 't100'):
        for year in (2023, 2024, 2025):
            t100(year)


if __name__ == '__main__':
    main()
