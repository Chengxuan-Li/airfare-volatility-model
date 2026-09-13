"""Flight-level realized outcomes with explicit eligibility and denominators."""
import zipfile

import numpy as np
import pandas as pd

from src.acquisition.download import digest
from src.config import AIRPORTS


GROUPS = ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline',
          'OriginAirportID', 'DestAirportID', 'Origin', 'Dest']
KEYS = ['FlightDate', 'DOT_ID_Reporting_Airline', 'Flight_Number_Reporting_Airline',
        'OriginAirportID', 'DestAirportID', 'CRSDepTime']
CORE_KEYS = [column for column in KEYS if column != 'CRSDepTime']
COUNTS = ['flights', 'cancelled', 'diverted', 'cancelled_and_diverted',
          'delay_observed', 'delay_missing_eligible', 'delayed_15', 'delayed_60',
          'arrival_delay_sum']


def outcome_rates(cells):
    result = cells.copy()
    result['cancellation_rate'] = result.cancelled / result.flights
    result['diversion_rate'] = result.diverted / result.flights
    denominator = result.delay_observed.where(result.delay_observed.gt(0))
    result['delay_15_rate'] = result.delayed_15 / denominator
    result['delay_60_rate'] = result.delayed_60 / denominator
    result['mean_arrival_delay'] = result.arrival_delay_sum / denominator
    return result


def summarize_operations(frame, year, month):
    df = frame.copy()
    required = set(GROUPS + KEYS + ['Cancelled', 'Diverted', 'ArrDelay'])
    if required - set(df.columns):
        raise ValueError(f'Missing operations columns: {sorted(required - set(df.columns))}')
    if df[GROUPS + CORE_KEYS].isna().any().any():
        raise ValueError('Missing operations identity')
    dates = pd.to_datetime(df.FlightDate, errors='raise')
    if not (df.Year.eq(year) & df.Month.eq(month) & dates.dt.year.eq(year)
            & dates.dt.month.eq(month)).all():
        raise ValueError('Operations period mismatch')
    if not df[['Cancelled', 'Diverted']].isin([0, 1]).all().all():
        raise ValueError('Invalid cancellation/diversion flag')
    if np.isinf(df.ArrDelay.to_numpy(dtype=float)).any():
        raise ValueError('Infinite arrival delay')
    missing_schedule = df.CRSDepTime.isna()
    duplicates = int(df.loc[~missing_schedule].duplicated(KEYS, keep=False).sum())
    if duplicates:
        raise ValueError(f'Operations duplicate flight rows: {duplicates}')
    core_collisions = df.duplicated(CORE_KEYS, keep=False)
    if (missing_schedule & core_collisions).any():
        raise ValueError(
            f'Operations incomplete key collision: {int(core_collisions.sum())}')
    eligible = df.Cancelled.eq(0) & df.Diverted.eq(0)
    observed = eligible & df.ArrDelay.notna()
    df['flights'] = 1
    df['cancelled'] = df.Cancelled.astype(int)
    df['diverted'] = df.Diverted.astype(int)
    df['cancelled_and_diverted'] = (df.Cancelled.eq(1) & df.Diverted.eq(1)).astype(int)
    df['delay_observed'] = observed.astype(int)
    df['delay_missing_eligible'] = (eligible & ~observed).astype(int)
    df['delayed_15'] = (observed & df.ArrDelay.ge(15)).astype(int)
    df['delayed_60'] = (observed & df.ArrDelay.ge(60)).astype(int)
    # Zero contributes only to the sum; observed counts determine delay denominators.
    df['arrival_delay_sum'] = df.ArrDelay.where(observed, 0)
    cells = df.groupby(GROUPS, as_index=False, observed=True)[COUNTS].sum()
    audit = {'rows': len(df), 'duplicate_rows': duplicates,
             'eligible_delay_missing': int(df.delay_missing_eligible.sum())}
    return outcome_rates(cells), audit


def read_operations(path, year, month, *, airports=AIRPORTS, airport_ids=None,
                    chunksize=100000):
    """Validate all national rows and retain scoped route and national carrier totals."""
    required = sorted(set(GROUPS + KEYS + ['Cancelled', 'Diverted', 'ArrDelay', 'Flights']))
    selected_parts, national_parts = [], []
    seen_complete_keys = set()
    seen_cores = set()
    seen_missing_cores = set()
    raw_rows = selected_rows = 0
    missing_schedule_national = missing_schedule_selected = 0
    national_groups = ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline']
    selected_airport_ids = None if airport_ids is None else set(airport_ids)
    national_airport_ids = set()
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        if len(members) != 1:
            raise ValueError('Expected exactly one operations CSV member')
        member = members[0]
        with archive.open(member) as stream:
            columns = pd.read_csv(stream, nrows=0).columns.tolist()
        if set(required) - set(columns):
            raise ValueError(f'Missing operations columns: {sorted(set(required) - set(columns))}')
        with archive.open(member) as stream:
            for frame in pd.read_csv(stream, usecols=required, chunksize=chunksize):
                if not frame.Flights.eq(1).all():
                    raise ValueError('Expected one reported flight per source row')
                missing_schedule = frame.CRSDepTime.isna()
                complete_keys = set(frame.loc[~missing_schedule, KEYS]
                                    .itertuples(index=False, name=None))
                current_cores = set(frame[CORE_KEYS].itertuples(index=False, name=None))
                current_missing_cores = set(frame.loc[missing_schedule, CORE_KEYS]
                                            .itertuples(index=False, name=None))
                repeated = len(seen_complete_keys.intersection(complete_keys))
                if repeated:
                    raise ValueError(f'Operations duplicate keys across chunks: {repeated}')
                incomplete_collisions = (
                    current_missing_cores.intersection(seen_cores)
                    | current_cores.intersection(seen_missing_cores))
                if incomplete_collisions:
                    raise ValueError(
                        'Operations incomplete key collision across chunks: '
                        f'{len(incomplete_collisions)}')
                cells, _ = summarize_operations(frame, year, month)
                national_parts.append(cells.groupby(national_groups, as_index=False)[COUNTS].sum())
                if selected_airport_ids is None:
                    in_scope = cells.Origin.isin(airports) & cells.Dest.isin(airports)
                    raw_in_scope = frame.Origin.isin(airports) & frame.Dest.isin(airports)
                else:
                    in_scope = (cells.OriginAirportID.isin(selected_airport_ids)
                                & cells.DestAirportID.isin(selected_airport_ids))
                    raw_in_scope = (frame.OriginAirportID.isin(selected_airport_ids)
                                    & frame.DestAirportID.isin(selected_airport_ids))
                selected = cells.loc[in_scope
                                     & cells.OriginAirportID.ne(cells.DestAirportID)]
                selected_parts.append(selected[GROUPS + COUNTS])
                raw_rows += len(frame)
                selected_rows += int(selected.flights.sum())
                missing_schedule_national += int(missing_schedule.sum())
                missing_schedule_selected += int((
                    missing_schedule & raw_in_scope
                    & frame.OriginAirportID.ne(frame.DestAirportID)).sum())
                national_airport_ids.update(frame.OriginAirportID.unique())
                national_airport_ids.update(frame.DestAirportID.unique())
                seen_complete_keys.update(complete_keys)
                seen_cores.update(current_cores)
                seen_missing_cores.update(current_missing_cores)
    if not raw_rows:
        raise ValueError('Operations archive contains no flight rows')
    scoped = pd.concat(selected_parts, ignore_index=True).groupby(GROUPS, as_index=False)[COUNTS].sum()
    national = pd.concat(national_parts, ignore_index=True).groupby(national_groups, as_index=False)[COUNTS].sum()
    audit = {'year': year, 'month': month, 'input_sha256': digest(path),
             'csv_member': member, 'columns': columns, 'raw_rows': raw_rows,
             'selected_rows': selected_rows, 'duplicate_rows': 0,
             'national_airport_count': len(national_airport_ids),
             'national_reporting_carriers': len(national), 'selected_airports': sorted(airports),
             'eligible_delay_missing_national': int(national.delay_missing_eligible.sum()),
             'scope': 'both endpoints in original seven-airport set; all reporting carriers'}
    if selected_airport_ids is not None:
        audit.pop('selected_airports')
        audit['selected_airport_ids'] = sorted(selected_airport_ids)
        audit['scope'] = 'both endpoint airport IDs in supplied stable-ID set; all reporting carriers'
    if missing_schedule_national:
        audit['missing_scheduled_departure_national'] = missing_schedule_national
        audit['missing_scheduled_departure_selected'] = missing_schedule_selected
        audit['incomplete_key_policy'] = (
            'Missing CRSDepTime retained only when the remaining flight identity '
            'is unique across the complete monthly source; no schedule imputation.')
    return outcome_rates(scoped), outcome_rates(national), audit
