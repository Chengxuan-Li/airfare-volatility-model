"""Stream national ZIPs, retaining only the declared pilot scope."""
import json
import zipfile

import pandas as pd

from src.cleaning.db1b import clean_market, join_ticket, summarize_cells
from src.config import CARRIERS, DESTINATIONS, HUBS, PERIODS, PROCESSED, TABLES, bts_path

MARKET_COLUMNS = ['ItinID', 'MktID', 'Year', 'Quarter', 'Origin', 'Dest', 'RPCarrier',
                  'MktCoupons', 'BulkFare', 'Passengers', 'MktFare', 'MktDistance']
TICKET_COLUMNS = ['Year', 'Quarter', 'ItinID', 'DollarCred', 'RoundTrip', 'ItinFare']


def chunks(path, columns, size):
    with zipfile.ZipFile(path) as archive:
        name = next(n for n in archive.namelist() if n.lower().endswith('.csv'))
        with archive.open(name) as stream:
            yield from pd.read_csv(stream, usecols=columns, chunksize=size)


def process_quarter(market_path, ticket_path, *, year, quarter, chunksize=250000):
    scoped, count, missing_grouping = [], 0, 0
    for chunk in chunks(market_path, MARKET_COLUMNS, chunksize):
        count += len(chunk)
        if not ((chunk.Year == year) & (chunk.Quarter == quarter)).all():
            raise ValueError('Market period mismatch')
        for col in ['Origin', 'Dest', 'RPCarrier']:
            chunk[col] = chunk[col].astype('string').str.strip().str.upper()
        missing_grouping += int(chunk[['Origin', 'Dest', 'RPCarrier']].isna().any(axis=1).sum())
        selected = chunk.Origin.isin(HUBS) & chunk.Dest.isin(DESTINATIONS) & chunk.RPCarrier.isin(CARRIERS)
        scoped.append(chunk.loc[selected])
    market = pd.concat(scoped, ignore_index=True)
    duplicates = int(market.duplicated(['Year', 'Quarter', 'MktID']).sum())
    if duplicates:
        raise ValueError('duplicate Market keys in pilot scope')
    wanted = set(market.ItinID)
    tickets, ticket_count = [], 0
    for chunk in chunks(ticket_path, TICKET_COLUMNS, chunksize):
        ticket_count += len(chunk)
        if not ((chunk.Year == year) & (chunk.Quarter == quarter)).all():
            raise ValueError('Ticket period mismatch')
        tickets.append(chunk.loc[chunk.ItinID.isin(wanted)])
    ticket = pd.concat(tickets, ignore_index=True)
    joined, match_audit = join_ticket(market, ticket)
    unreliable = joined.DollarCred.ne(1)
    audit = {'year': year, 'quarter': quarter, 'market_rows_scanned': count,
             'scope_rows': len(market), 'out_of_scope_rows': count - len(market),
             'raw_missing_grouping_rows': missing_grouping,
             'market_duplicate_keys': duplicates, 'ticket_rows_scanned': ticket_count,
             'ticket_matched_rows': len(ticket), 'join': match_audit,
             'ticket_unreliable_rows': int((unreliable & joined.DollarCred.notna()).sum()),
             'ticket_missing_credibility_rows': int(joined.DollarCred.isna().sum())}
    cells = []
    for label, low, high in [('primary', 20, 2000), ('broad_fare_bounds', 10, 5000)]:
        clean, exclusions = clean_market(joined.loc[~unreliable], low, high)
        exclusions['roundtrip_passenger_share'] = float(
            clean.loc[clean.RoundTrip == 1, 'Passengers'].sum() / clean.Passengers.sum()) if len(clean) else None
        aggregated = summarize_cells(clean)
        exclusions['cells_before_min_passengers'] = len(aggregated)
        exclusions['cells_below_30_passengers'] = int((aggregated.passengers < 30).sum())
        aggregated = aggregated.loc[aggregated.passengers >= 30].copy()
        aggregated['sample'] = label
        cells.append(aggregated)
        audit[label] = exclusions
    return pd.concat(cells, ignore_index=True), audit


def build_cells():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    all_cells, audits = [], []
    for year, quarter in PERIODS:
        print(f'Streaming Market/Ticket {year} Q{quarter}', flush=True)
        cells, audit = process_quarter(bts_path('Market', year, quarter),
                                       bts_path('Ticket', year, quarter), year=year, quarter=quarter)
        all_cells.append(cells)
        audits.append(audit)
        # Intermediate progress is durable locally, but every rerun reprocesses raw.
        cells.to_parquet(PROCESSED/f'cells_{year}_q{quarter}.parquet', index=False)
        print(f'Aggregated {year} Q{quarter}: {len(cells)} cells including robustness sample', flush=True)
    result = pd.concat(all_cells, ignore_index=True)
    result.to_csv(TABLES/'fare_cells.csv', index=False)
    (TABLES/'cleaning_audit.json').write_text(json.dumps(audits, indent=2) + '\n', encoding='utf-8')
    return result
