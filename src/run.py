"""Run from repository root: python -m src.run [--acquire] [--analysis-only]."""
import argparse
import json

import pandas as pd

from src.acquisition.batch import acquire_bts, acquire_delay, acquire_weather
from src.acquisition.verify import verify_pilot_inputs
from src.analysis.pilot import analyze
from src.cleaning.panel import build_cells
from src.config import PERIODS, TABLES
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
    verify_pilot_inputs()
    if not args.analysis_only:
        build_cells()
    # One canonical representation for both full and analysis-only execution.
    # Round-trip parsing preserves serialized binary64 values without parser drift.
    cells = pd.read_csv(TABLES/'fare_cells.csv', float_precision='round_trip')
    weather = build_weather_panel()
    panel = attach_weather(cells, weather)
    metadata = analyze(panel, weather)
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == '__main__':
    main()
