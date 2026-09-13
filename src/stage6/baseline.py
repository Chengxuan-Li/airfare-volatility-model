"""Load the explicitly frozen and checksum-verified 2010 sample."""
from pathlib import Path
import json

import pandas as pd

from src.acquisition.download import digest

BASELINE_DIRECTORY = Path('outputs/stage6/annual_2010')
CSV_FILES = ('airport_ranking.csv','fare_carrier_cells.csv','operations_carrier_month.csv',
             'operations_national_month.csv','airport_aliases.csv','operations_carrier_identities.csv',
             'route_quarter_panel.csv')

FROZEN_MANIFEST = Path('data/manifests/stage6_frozen_sample_2010.json')


def load_baseline(manifest_path=FROZEN_MANIFEST):
    frozen = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    directory = Path(frozen['baseline_directory'])
    if frozen['baseline_year'] != 2010 or directory.resolve() != BASELINE_DIRECTORY.resolve():
        raise ValueError('Unexpected frozen baseline identity')
    verification = directory/'verification.json'
    if digest(verification) != frozen['verification_sha256']:
        raise ValueError('Frozen verification checksum mismatch')
    verified = json.loads(verification.read_text(encoding='utf-8'))
    expected_names = set(CSV_FILES) | {'quality_audit.json'}
    if set(verified['output_sha256']) != expected_names:
        raise ValueError('Frozen baseline artifact set differs')
    for name, checksum in verified['output_sha256'].items():
        if digest(directory/name) != checksum:
            raise ValueError(f'Frozen baseline checksum mismatch: {name}')
    if digest(directory/'airport_ranking.csv') != frozen['ranking_sha256']:
        raise ValueError('Frozen ranking checksum mismatch')
    tables = {name: pd.read_csv(directory/name, float_precision='round_trip',
        dtype={'RPCarrier':'string', 'Reporting_Airline':'string', 'code':'string', 'codes':'string'})
        for name in CSV_FILES}
    ranking = tables['airport_ranking.csv']
    if ranking.AirportID.isna().any() or ranking.AirportID.duplicated().any():
        raise ValueError('Frozen airport identities must be unique and present')
    if (not ranking.selected.isin([True, False]).all()
            or int(ranking.selected.sum()) != frozen['expected_selected_airports']):
        raise ValueError('Frozen selection differs')
    audit = json.loads((directory/'quality_audit.json').read_text(encoding='utf-8'))
    return ranking.copy(), audit['selection'], tables
