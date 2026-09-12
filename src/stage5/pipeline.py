"""Stream expanded fare products, independent capacity, and historical weather."""
import argparse
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd

from src.config import AIRPORTS, CARRIERS, RAW, bts_path
from src.cleaning.panel import chunks, MARKET_COLUMNS, TICKET_COLUMNS
from src.cleaning.db1b import clean_market, summarize_cells
from src.weather.risk import prior_season_risk

OUT = Path('outputs/stage5')
PERIODS = [(y, q) for y in (2023, 2024) for q in (1, 2, 3, 4)] + [(2025, 1), (2025, 2)]


def save_json(name, obj):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def one_way(frame):
    selected = frame.loc[frame.RoundTrip.eq(0) & frame.Coupons.eq(1)].copy()
    gap = (selected.MktFare - selected.ItinFare).abs()
    if selected.ItinFare.isna().any() or (gap > .0100001).any():
        raise ValueError('single-coupon itinerary fare does not match market fare')
    return selected, {'rows': len(selected), 'max_absolute_proration_gap': float(gap.max()) if len(gap) else None,
                      'rows_gap_above_cent': int((gap > .0100001).sum()),
                      'missing_itinerary_fare': int(selected.ItinFare.isna().sum())}


def capacity_cells(frame):
    df = frame.loc[frame.CLASS.astype(str).str.strip().eq('F')].copy()
    values = ['PASSENGERS', 'SEATS', 'DEPARTURES_PERFORMED', 'DEPARTURES_SCHEDULED']
    if not np.isfinite(df[values]).all().all() or (df[values] < 0).any().any():
        raise ValueError('invalid capacity counts')
    result = df.groupby(['YEAR', 'QUARTER', 'ORIGIN', 'DEST'])[values].sum().reset_index()
    return result.rename(columns={'YEAR': 'Year', 'QUARTER': 'Quarter', 'ORIGIN': 'Origin',
        'DEST': 'Dest', 'PASSENGERS': 't100_passengers', 'SEATS': 'seats', 'DEPARTURES_PERFORMED': 'departures',
        'DEPARTURES_SCHEDULED': 'scheduled_departures'})


def residualize(values, groups, tolerance=1e-12, max_iterations=10000):
    result = np.asarray(values, dtype=float).copy()
    codes = [pd.factorize(g)[0] for g in groups]
    if any((c < 0).any() for c in codes):
        raise ValueError('missing fixed effect group')
    for _ in range(max_iterations):
        previous = result.copy()
        for code in codes:
            counts = np.bincount(code)
            means = np.column_stack([np.bincount(code, weights=result[:, j])/counts
                                     for j in range(result.shape[1])])
            result -= means[code]
        if np.max(np.abs(result-previous)) < tolerance:
            return result
    raise ValueError('fixed effects did not converge')


def fare_quarter(year, quarter):
    scoped = []
    scanned = 0
    for chunk in chunks(bts_path('Market', year, quarter), MARKET_COLUMNS, 250000):
        scanned += len(chunk)
        if not ((chunk.Year == year) & (chunk.Quarter == quarter)).all():
            raise ValueError('Market period mismatch')
        for col in ['Origin', 'Dest', 'RPCarrier']:
            chunk[col] = chunk[col].astype('string').str.strip().str.upper()
        selected = (chunk.Origin.isin(AIRPORTS) & chunk.Dest.isin(AIRPORTS)
                    & chunk.Origin.ne(chunk.Dest) & chunk.RPCarrier.isin(CARRIERS))
        scoped.append(chunk.loc[selected])
    market = pd.concat(scoped, ignore_index=True)
    if market.duplicated(['Year', 'Quarter', 'MktID']).any():
        raise ValueError('duplicate market key')
    wanted = set(market.ItinID)
    tickets = []
    for chunk in chunks(bts_path('Ticket', year, quarter), TICKET_COLUMNS+['Coupons'], 250000):
        if not ((chunk.Year == year) & (chunk.Quarter == quarter)).all():
            raise ValueError('Ticket period mismatch')
        tickets.append(chunk.loc[chunk.ItinID.isin(wanted)])
    ticket = pd.concat(tickets, ignore_index=True)
    joined = market.merge(ticket, on=['Year', 'Quarter', 'ItinID'], how='left', validate='many_to_one', indicator=True)
    audit = {'year': year, 'quarter': quarter, 'market_scanned': scanned, 'scoped': len(market),
             'unmatched': int(joined._merge.eq('left_only').sum()),
             'unreliable_or_missing': int(joined.DollarCred.ne(1).sum())}
    clean, audit['primary_exclusions'] = clean_market(joined.loc[joined.DollarCred.eq(1)])
    simple, audit['one_way_product'] = one_way(clean)
    results = []
    for name, records in [('primary', clean), ('one_way', simple)]:
        cells = summarize_cells(records)
        audit[name+'_cells_below_30'] = int((cells.passengers < 30).sum())
        cells = cells.loc[cells.passengers >= 30].copy()
        cells['sample'] = name
        results.append(cells)
    return pd.concat(results, ignore_index=True), audit


def build_fares():
    results, audits = [], []
    for y, q in PERIODS:
        print(f'Stage5 streaming {y} Q{q}', flush=True)
        cells, audit = fare_quarter(y, q)
        results.append(cells)
        audits.append(audit)
        print(f'Stage5 {y} Q{q}: {len(cells)} product cells', flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.concat(results, ignore_index=True).to_csv(OUT/'fare_cells.csv', index=False)
    save_json('fare_audit.json', audits)


def build_weather():
    rows = []
    for airport in AIRPORTS:
        payload = json.loads((RAW/'weather'/f'{airport}_2020_2025.json').read_text(encoding='utf-8'))
        units = payload['daily_units']
        if any(units[c] != u for c, u in [('precipitation_sum', 'mm'), ('snowfall_sum', 'cm'), ('wind_speed_10m_max', 'm/s')]):
            raise ValueError('weather units')
        daily = pd.DataFrame(payload['daily']).rename(columns={'time': 'date'})
        for year, quarter in PERIODS:
            row = {'airport': airport, 'Year': year, 'Quarter': quarter, **prior_season_risk(daily, year, quarter)}
            row['fixed_risk'] = prior_season_risk(daily, 2023, quarter)['risk']
            rows.append(row)
    result = pd.DataFrame(rows)
    if result[['risk', 'fixed_risk']].isna().any().any():
        raise ValueError('missing weather risk')
    result.to_csv(OUT/'weather.csv', index=False)
    return result


def build_capacity():
    results = []
    audits = []
    for year in (2023, 2024, 2025):
        path = RAW/'t100'/f'T_100_Domestic_Segment_All_Carrier_{year}.zip'
        with zipfile.ZipFile(path) as archive:
            name = 'T_T100D_SEGMENT_ALL_CARRIER.csv'
            with archive.open(name) as stream:
                df = pd.read_csv(stream, low_memory=False)
        df.columns = df.columns.str.upper()
        if not df.YEAR.eq(year).all():
            raise ValueError('capacity year mismatch')
        if 'QUARTER' not in df:
            df['QUARTER'] = (df.MONTH-1)//3+1
        if not df.QUARTER.eq((df.MONTH-1)//3+1).all() or set(df.MONTH) != set(range(1, 13)):
            raise ValueError('capacity month/quarter coverage mismatch')
        selected = df.loc[df.ORIGIN.isin(AIRPORTS) & df.DEST.isin(AIRPORTS) & df.ORIGIN.ne(df.DEST)]
        audits.append({'year': year, 'raw_rows': len(df), 'selected_rows': len(selected),
                       'months': sorted(int(v) for v in df.MONTH.unique()),
                       'service_classes': sorted(str(v) for v in selected.CLASS.unique()),
                       'rows_by_month_class': selected.groupby(['MONTH', 'CLASS']).size().rename('rows').reset_index().to_dict('records')})
        results.append(capacity_cells(selected))
    result = pd.concat(results, ignore_index=True)
    result['load_factor'] = result.t100_passengers / result.seats.where(result.seats.gt(0))
    result['scheduled_minus_performed'] = result.scheduled_departures-result.departures
    result['performed_scheduled_ratio'] = result.departures/result.scheduled_departures.where(result.scheduled_departures.gt(0))
    if (result.t100_passengers > result.seats).any():
        raise ValueError('route passenger count exceeds seats')
    result.to_csv(OUT/'capacity.csv', index=False)
    save_json('capacity_audit.json', audits)
    return result


def build_panel():
    OUT.mkdir(parents=True, exist_ok=True)
    fare = pd.read_csv(OUT/'fare_cells.csv', float_precision='round_trip')
    weather = build_weather()
    capacity = build_capacity()
    panel = fare.merge(capacity, on=['Year', 'Quarter', 'Origin', 'Dest'], how='left', validate='many_to_one')
    for col in ['Origin', 'Dest']:
        selected = weather[['airport', 'Year', 'Quarter', 'risk', 'fixed_risk']].rename(
            columns={'airport': col, 'risk': col+'_risk', 'fixed_risk': col+'_fixed'})
        panel = panel.merge(selected, on=[col, 'Year', 'Quarter'], how='left', validate='many_to_one')
    panel['risk'] = (panel.Origin_risk + panel.Dest_risk)/2
    panel['fixed_risk'] = (panel.Origin_fixed + panel.Dest_fixed)/2
    panel['route'] = panel.Origin + '-' + panel.Dest
    panel['route_carrier'] = panel.route + '_' + panel.RPCarrier
    panel['route_carrier_season'] = panel.route_carrier + '_Q' + panel.Quarter.astype(str)
    panel['period'] = panel.Year.astype(str) + 'Q' + panel.Quarter.astype(str)
    panel['pair'] = ['-'.join(sorted([o, d])) for o, d in zip(panel.Origin, panel.Dest)]
    save_json('matching_audit.json', {'rows': len(panel), 'missing_risk': int(panel.risk.isna().sum()),
        'missing_capacity': int(panel.seats.isna().sum()), 'nonpositive_capacity': int(panel.seats.le(0).sum())})
    keys = ['Year', 'Quarter', 'Origin', 'Dest']
    in_period = [(int(y), int(q)) in PERIODS for y, q in zip(capacity.Year, capacity.Quarter)]
    key_audit = fare[keys].drop_duplicates().merge(capacity.loc[in_period, keys], on=keys, how='outer', indicator=True)
    key_audit.loc[key_audit._merge.ne('both')].to_csv(OUT/'unmatched_capacity_keys.csv', index=False)
    if panel.seats.isna().any() or panel[['risk', 'fixed_risk']].isna().any().any():
        raise ValueError('missing expected panel capacity/weather key; see matching audit')
    panel.to_csv(OUT/'panel.csv', index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reuse-fares', action='store_true')
    args = parser.parse_args()
    from src.stage5.acquire import verify_inputs
    verify_inputs()
    if not args.reuse_fares:
        build_fares()
    build_panel()


if __name__ == '__main__':
    main()
