"""Flight-level realized outcomes with explicit eligibility and denominators."""
import json
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
CONSUMED = sorted(set(GROUPS + KEYS + ['Cancelled', 'Diverted', 'ArrDelay', 'Flights']))
NON_KEY_CONSUMED = [column for column in CONSUMED if column not in KEYS]
_MISSING = object()


def _exact_tuple(values):
    """Represent values exactly enough to distinguish missing from observed values."""
    return tuple(_MISSING if pd.isna(value) else value for value in values)


def _json_value(value):
    if value is _MISSING or pd.isna(value):
        return None
    value = value.item() if isinstance(value, np.generic) else value
    # Blank values can change a CSV chunk's integral columns to floating dtype.
    return int(value) if isinstance(value, float) and value.is_integer() else value


def _validate_consumed_values(frame, year, month, *, require_flights):
    if frame[GROUPS + CORE_KEYS].isna().any().any():
        raise ValueError('Missing operations identity')
    dates = pd.to_datetime(frame.FlightDate, errors='raise')
    if not (frame.Year.eq(year) & frame.Month.eq(month) & dates.dt.year.eq(year)
            & dates.dt.month.eq(month)).all():
        raise ValueError('Operations period mismatch')
    if not frame[['Cancelled', 'Diverted']].isin([0, 1]).all().all():
        raise ValueError('Invalid cancellation/diversion flag')
    if np.isinf(frame.ArrDelay.to_numpy(dtype=float)).any():
        raise ValueError('Infinite arrival delay')
    if require_flights and not frame.Flights.eq(1).all():
        raise ValueError('Expected one reported flight per source row')


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
    _validate_consumed_values(df, year, month, require_flights=False)
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


def _quarantine_preflight(archive, member, required, year, month, chunksize):
    """Validate a complete month and return its conflicting complete-key groups."""
    consumed_positions = {column: position for position, column in enumerate(CONSUMED)}
    key_positions = [consumed_positions[column] for column in KEYS]
    core_positions = [consumed_positions[column] for column in CORE_KEYS]
    signature_positions = [consumed_positions[column] for column in NON_KEY_CONSUMED]
    variants_by_key = {}
    seen_cores = set()
    seen_missing_cores = set()
    with archive.open(member) as stream:
        for frame in pd.read_csv(stream, usecols=required, chunksize=chunksize):
            _validate_consumed_values(frame, year, month, require_flights=True)
            missing_schedule = frame.CRSDepTime.isna().to_numpy(copy=False)
            for position, values in enumerate(
                    frame[CONSUMED].itertuples(index=False, name=None)):
                core = _exact_tuple(values[index] for index in core_positions)
                if missing_schedule[position]:
                    if core in seen_cores:
                        raise ValueError('Operations incomplete key collision: 1')
                    seen_missing_cores.add(core)
                    seen_cores.add(core)
                    continue
                if core in seen_missing_cores:
                    raise ValueError('Operations incomplete key collision: 1')
                key = _exact_tuple(values[index] for index in key_positions)
                signature = _exact_tuple(values[index]
                                         for index in signature_positions)
                counts = variants_by_key.setdefault(key, {})
                counts[signature] = counts.get(signature, 0) + 1
                seen_cores.add(core)

    ambiguous = {
        key: variants for key, variants in variants_by_key.items()
        if len(variants) > 1
    }
    del variants_by_key, seen_cores, seen_missing_cores

    details = []
    for key, variants in ambiguous.items():
        variant_rows = [
            {
                'values': {
                    column: _json_value(value)
                    for column, value in zip(NON_KEY_CONSUMED, signature)
                },
                'rows': count,
            }
            for signature, count in variants.items()
        ]
        variant_rows.sort(key=lambda item: json.dumps(
            item['values'], sort_keys=True, separators=(',', ':')))
        details.append({
            'key': {
                column: _json_value(value)
                for column, value in zip(KEYS, key)
            },
            'rows': sum(variants.values()),
            'consumed_variant_count': len(variants),
            'consumed_variants': variant_rows,
        })
    details.sort(key=lambda item: json.dumps(
        item['key'], sort_keys=True, separators=(',', ':')))
    return set(ambiguous), details


def read_operations(path, year, month, *, airports=AIRPORTS, airport_ids=None,
                    chunksize=100000, conflict_policy='error'):
    """Validate all national rows and retain scoped route and national carrier totals."""
    if conflict_policy not in {'error', 'quarantine'}:
        raise ValueError("conflict_policy must be 'error' or 'quarantine'")
    required = CONSUMED
    selected_parts, national_parts = [], []
    seen_complete = {}
    repeated_keys = set()
    repeated_keys_selected = set()
    seen_cores = set()
    seen_missing_cores = set()
    raw_rows = selected_rows = 0
    repeated_rows_national = repeated_rows_selected = 0
    ambiguous_rows_national = ambiguous_rows_selected = 0
    ambiguous_groups_selected = set()
    missing_schedule_national = missing_schedule_selected = 0
    national_groups = ['Year', 'Month', 'DOT_ID_Reporting_Airline', 'Reporting_Airline']
    selected_airport_ids = None if airport_ids is None else set(airport_ids)
    national_airport_ids = set()
    consumed_positions = {column: position for position, column in enumerate(CONSUMED)}
    key_positions = [consumed_positions[column] for column in KEYS]
    core_positions = [consumed_positions[column] for column in CORE_KEYS]
    signature_positions = [consumed_positions[column] for column in NON_KEY_CONSUMED]
    with zipfile.ZipFile(path) as archive:
        members = [n for n in archive.namelist() if n.lower().endswith('.csv')]
        if len(members) != 1:
            raise ValueError('Expected exactly one operations CSV member')
        member = members[0]
        with archive.open(member) as stream:
            columns = pd.read_csv(stream, nrows=0).columns.tolist()
        if set(required) - set(columns):
            raise ValueError(f'Missing operations columns: {sorted(set(required) - set(columns))}')
        if conflict_policy == 'quarantine':
            ambiguous_keys, ambiguous_details = _quarantine_preflight(
                archive, member, required, year, month, chunksize)
        else:
            ambiguous_keys, ambiguous_details = set(), []
        with archive.open(member) as stream:
            for frame in pd.read_csv(stream, usecols=required, chunksize=chunksize):
                if not frame.Flights.eq(1).all():
                    raise ValueError('Expected one reported flight per source row')
                missing_schedule = frame.CRSDepTime.isna()
                if selected_airport_ids is None:
                    raw_in_scope = frame.Origin.isin(airports) & frame.Dest.isin(airports)
                else:
                    raw_in_scope = (frame.OriginAirportID.isin(selected_airport_ids)
                                    & frame.DestAirportID.isin(selected_airport_ids))
                raw_selected = (raw_in_scope
                                & frame.OriginAirportID.ne(frame.DestAirportID))
                keep = np.ones(len(frame), dtype=bool)
                consumed_rows = frame[CONSUMED].itertuples(index=False, name=None)
                missing_values = missing_schedule.to_numpy(copy=False)
                selected_values = raw_selected.to_numpy(copy=False)
                for position, values in enumerate(consumed_rows):
                    core = _exact_tuple(values[index] for index in core_positions)
                    if missing_values[position]:
                        if core in seen_cores:
                            raise ValueError('Operations incomplete key collision: 1')
                        seen_missing_cores.add(core)
                        seen_cores.add(core)
                        continue
                    if core in seen_missing_cores:
                        raise ValueError('Operations incomplete key collision: 1')
                    key = _exact_tuple(values[index] for index in key_positions)
                    if key in ambiguous_keys:
                        keep[position] = False
                        ambiguous_rows_national += 1
                        if selected_values[position]:
                            ambiguous_rows_selected += 1
                            ambiguous_groups_selected.add(key)
                        continue
                    signature = _exact_tuple(values[index]
                                             for index in signature_positions)
                    previous = seen_complete.get(key)
                    if previous is not None:
                        if signature != previous:
                            raise ValueError(
                                'Operations duplicate key has conflicting consumed fields')
                        keep[position] = False
                        repeated_keys.add(key)
                        repeated_rows_national += 1
                        repeated_rows_selected += int(selected_values[position])
                        if selected_values[position]:
                            repeated_keys_selected.add(key)
                    else:
                        seen_complete[key] = signature
                        seen_cores.add(core)
                retained = frame.loc[keep]
                if retained.empty:
                    raw_rows += len(frame)
                    missing_schedule_national += int(missing_schedule.sum())
                    missing_schedule_selected += int((missing_schedule & raw_selected).sum())
                    national_airport_ids.update(frame.OriginAirportID.unique())
                    national_airport_ids.update(frame.DestAirportID.unique())
                    continue
                cells, _ = summarize_operations(retained, year, month)
                national_parts.append(cells.groupby(national_groups, as_index=False)[COUNTS].sum())
                if selected_airport_ids is None:
                    in_scope = cells.Origin.isin(airports) & cells.Dest.isin(airports)
                else:
                    in_scope = (cells.OriginAirportID.isin(selected_airport_ids)
                                & cells.DestAirportID.isin(selected_airport_ids))
                selected = cells.loc[in_scope
                                     & cells.OriginAirportID.ne(cells.DestAirportID)]
                selected_parts.append(selected[GROUPS + COUNTS])
                raw_rows += len(frame)
                selected_rows += int(selected.flights.sum())
                missing_schedule_national += int(missing_schedule.sum())
                missing_schedule_selected += int((missing_schedule & raw_selected).sum())
                national_airport_ids.update(frame.OriginAirportID.unique())
                national_airport_ids.update(frame.DestAirportID.unique())
    if not raw_rows:
        raise ValueError('Operations archive contains no flight rows')
    if not national_parts:
        raise ValueError('Operations month has no retained reported analysis units')
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
    if repeated_rows_national or ambiguous_rows_national:
        audit['retained_rows'] = (
            raw_rows - repeated_rows_national - ambiguous_rows_national)
    if repeated_rows_national:
        audit['repeated_key_rows_removed_national'] = repeated_rows_national
        audit['repeated_key_rows_removed_selected'] = repeated_rows_selected
        audit['repeated_key_groups_national'] = len(repeated_keys)
        audit['repeated_key_groups_selected'] = len(repeated_keys_selected)
        audit['repeat_resolution_policy'] = (
            'Repeated complete flight keys are counted once only when every consumed '
            'identity and outcome field agrees, including missingness; this is '
            'measurement equivalence, not full source row identity.')
    if ambiguous_rows_national:
        audit['ambiguous_key_rows_excluded_national'] = ambiguous_rows_national
        audit['ambiguous_key_rows_excluded_selected'] = ambiguous_rows_selected
        audit['ambiguous_key_groups_national'] = len(ambiguous_keys)
        audit['ambiguous_key_groups_selected'] = len(ambiguous_groups_selected)
        audit['ambiguous_complete_key_groups'] = ambiguous_details
        audit['ambiguity_policy'] = (
            'All rows in a conflicting complete flight-key group are quarantined; '
            'no outcome is selected or imputed. Counts are retained reported analysis '
            'units, not a census of unique physical flights.')
    if missing_schedule_national:
        audit['missing_scheduled_departure_national'] = missing_schedule_national
        audit['missing_scheduled_departure_selected'] = missing_schedule_selected
        audit['incomplete_key_policy'] = (
            'Missing CRSDepTime retained only when the remaining flight identity '
            'is unique across the complete monthly source; no schedule imputation.')
    return outcome_rates(scoped), outcome_rates(national), audit
