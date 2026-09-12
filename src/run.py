"""Run from repository root: python -m src.run [--acquire] [--analysis-only]."""
import argparse
import json

import pandas as pd

from src.acquisition.batch import acquire_bts, acquire_delay, acquire_weather
from src.acquisition.download import digest
from src.analysis.pilot import analyze
from src.cleaning.panel import build_cells
from src.config import PERIODS, TABLES, MANIFESTS
from src.weather.panel import attach_weather, build_weather_panel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--acquire', action='store_true')
    parser.add_argument('--analysis-only', action='store_true', help='Reuse derived fare cells; full default run rebuilds from raw')
    args = parser.parse_args()
    if args.acquire:
        for year, quarter in PERIODS:
            for table in ['Market', 'Ticket']:
                acquire_bts((table, year, quarter))
        acquire_weather()
        acquire_delay()
    for manifest in MANIFESTS.glob('*.json'):
        record = json.loads(manifest.read_text(encoding='utf-8'))
        if 'local_path' in record and 'sha256' in record:
            if digest(record['local_path']) != record['sha256']:
                raise ValueError(f'Raw input checksum mismatch: {manifest.name}')
    cells = pd.read_csv(TABLES/'fare_cells.csv') if args.analysis_only else build_cells()
    weather = build_weather_panel()
    panel = attach_weather(cells, weather)
    metadata = analyze(panel, weather)
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == '__main__':
    main()
