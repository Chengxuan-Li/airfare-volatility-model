"""Explicit record exclusions, period-scoped joins, passenger-weighted moments."""
import numpy as np
import pandas as pd

KEYS = ['Year', 'Quarter', 'Origin', 'Dest', 'RPCarrier']


def clean_market(frame, low=20, high=2000):
    df = frame.copy()
    audit = {'input_rows': len(df)}
    for col in ['Origin', 'Dest', 'RPCarrier']:
        df[col] = df[col].astype('string').str.strip().str.upper()
    for col in ['Passengers', 'MktFare', 'BulkFare', 'MktCoupons']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    conditions = [
        ('missing_or_invalid_quantity', lambda d: ~np.isfinite(d.Passengers) | (d.Passengers <= 0)),
        ('missing_fare', lambda d: ~np.isfinite(d.MktFare)),
        ('fare_bounds', lambda d: ~d.MktFare.between(low, high)),
        ('bulk_or_unknown', lambda d: d.BulkFare != 0),
        ('connecting_or_unknown', lambda d: d.MktCoupons != 1),
    ]
    for label, condition in conditions:
        excluded = condition(df)
        audit['excluded_' + label] = int(excluded.sum())
        df = df.loc[~excluded].copy()
    audit['kept_rows'] = len(df)
    return df, audit


def join_ticket(market, ticket):
    keys = ['Year', 'Quarter', 'ItinID']
    if ticket.duplicated(keys).any():
        raise ValueError('duplicate Ticket keys; join would multiply rows')
    ticket = ticket[keys + [c for c in ['DollarCred', 'RoundTrip', 'ItinFare'] if c in ticket]]
    merged = market.merge(ticket, on=keys, how='left', validate='many_to_one', indicator=True)
    audit = {'market_rows': len(market), 'joined_rows': len(merged),
             'unmatched_rows': int((merged['_merge'] == 'left_only').sum())}
    return merged.drop(columns='_merge'), audit


def summarize_cells(frame):
    df = frame.copy()
    df['fare_total'] = df.MktFare * df.Passengers
    df['fare_square_total'] = df.MktFare**2 * df.Passengers
    cells = df.groupby(KEYS, observed=True).agg(
        passengers=('Passengers', 'sum'), records=('MktID', 'size'),
        fare_total=('fare_total', 'sum'), fare_square_total=('fare_square_total', 'sum')).reset_index()
    cells['fare_mean'] = cells.fare_total / cells.passengers
    cells['fare_variance'] = np.maximum(0, cells.fare_square_total / cells.passengers - cells.fare_mean**2)
    return cells.drop(columns=['fare_total', 'fare_square_total'])
