from pathlib import Path

RAW = Path('data/raw')
MANIFESTS = Path('data/manifests')
PROCESSED = Path('data/processed')
TABLES = Path('outputs/tables')
FIGURES = Path('outputs/figures')
HUBS = ['ORD', 'DEN', 'DFW']
DESTINATIONS = ['ATL', 'LAX', 'JFK', 'SEA']
AIRPORTS = HUBS + DESTINATIONS
CARRIERS = ['AA', 'DL', 'UA', 'WN']
PERIODS = [(year, quarter) for year in (2023, 2024) for quarter in (1, 2, 3, 4)]


def bts_path(table, year, quarter):
    return RAW / 'bts_db1b' / f'Origin_and_Destination_Survey_DB1B{table}_{year}_{quarter}.zip'
