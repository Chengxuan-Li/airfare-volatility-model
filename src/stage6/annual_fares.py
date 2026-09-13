"""Stable-airport sampling and fare aggregation for the Stage 6 annual panel."""

from __future__ import annotations

import zipfile

import numpy as np
import pandas as pd

from src.config import AIRPORTS


SELECTION_COLUMNS = [
    "Year", "Quarter", "OriginAirportID", "DestAirportID", "Origin", "Dest",
    "OriginCountry", "DestCountry", "MktCoupons", "BulkFare", "Passengers",
]
MARKET_COLUMNS = [
    "ItinID", "MktID", "Year", "Quarter", "OriginAirportID", "DestAirportID",
    "Origin", "Dest", "OriginCountry", "DestCountry", "RPCarrier", "MktCoupons",
    "BulkFare", "Passengers", "MktFare",
]
TICKET_COLUMNS = ["Year", "Quarter", "ItinID", "DollarCred"]
CELL_KEYS = [
    "Year", "Quarter", "OriginAirportID", "DestAirportID", "RPCarrier", "sample",
]
CELL_COLUMNS = CELL_KEYS + [
    "passengers", "records", "fare_total", "fare_square_total", "fare_mean",
    "fare_variance", "low_support",
]
TEXT_COLUMNS = {"Origin", "Dest", "OriginCountry", "DestCountry", "RPCarrier"}


def _csv_member(archive):
    members = [name for name in archive.namelist() if name.lower().endswith(".csv")]
    if len(members) != 1:
        raise ValueError("Expected exactly one CSV member")
    return members[0]


def _chunks(path, columns, chunksize, label):
    with zipfile.ZipFile(path) as archive:
        member = _csv_member(archive)
        with archive.open(member) as stream:
            available = pd.read_csv(stream, nrows=0).columns.tolist()
        missing = sorted(set(columns) - set(available))
        if missing:
            raise ValueError(f"Missing {label} columns: {missing}")
        dtypes = {column: "string" for column in columns if column in TEXT_COLUMNS}
        with archive.open(member) as stream:
            yield from pd.read_csv(
                stream, usecols=columns, dtype=dtypes, chunksize=chunksize
            )


def _validate_period(frame, year, quarter, label):
    parsed_year = pd.to_numeric(frame["Year"], errors="coerce")
    parsed_quarter = pd.to_numeric(frame["Quarter"], errors="coerce")
    if not (parsed_year.eq(year) & parsed_quarter.eq(quarter)).all():
        raise ValueError(f"{label} period mismatch")


def _integer_ids(frame, columns, label):
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or np.isinf(values.to_numpy(dtype=float)).any():
            raise ValueError(f"Missing {label} identity: {column}")
        if not values.eq(np.floor(values)).all():
            raise ValueError(f"Invalid {label} identity: {column}")
        frame[column] = values.astype("int64")


def _normalize_codes(frame):
    for column in [name for name in ("Origin", "Dest") if name in frame]:
        frame[column] = frame[column].astype("string").str.strip().str.upper()
        frame.loc[frame[column].eq(""), column] = pd.NA


def _aliases(frame):
    parts = []
    for id_column, code_column in (("OriginAirportID", "Origin"), ("DestAirportID", "Dest")):
        part = frame[[id_column, code_column]].rename(
            columns={id_column: "AirportID", code_column: "code"}
        )
        parts.append(part)
    result = pd.concat(parts, ignore_index=True).dropna()
    result = result.loc[result.code.ne("")].drop_duplicates()
    return result.sort_values(["AirportID", "code"], kind="stable").reset_index(drop=True)


def _sequential_filter(frame, conditions):
    result = frame.copy()
    audit = {}
    for label, condition in conditions:
        excluded = condition(result).fillna(True)
        audit[f"excluded_{label}"] = int(excluded.sum())
        result = result.loc[~excluded].copy()
    audit["kept_rows"] = len(result)
    return result, audit


def select_airports(market_path, *, year=2010, quarter=1, top_n=30, chunksize=250000):
    """Rank baseline airports by eligible endpoint passenger volume.

    Selection deliberately reads no fare field. The returned ranking covers every
    eligible airport and marks the volume top ``top_n`` plus the original seven.
    """
    if top_n < 0:
        raise ValueError("top_n must be nonnegative")
    alias_parts = []
    passenger_parts = []
    exclusion_totals = {
        "excluded_foreign_endpoints": 0,
        "excluded_bulk_or_unknown": 0,
        "excluded_connecting_or_unknown": 0,
        "excluded_missing_or_invalid_passengers": 0,
    }
    raw_rows = 0
    eligible_rows = 0
    for chunk in _chunks(market_path, SELECTION_COLUMNS, chunksize, "Market"):
        _validate_period(chunk, year, quarter, "Market")
        _integer_ids(chunk, ["OriginAirportID", "DestAirportID"], "Market airport")
        _normalize_codes(chunk)
        raw_rows += len(chunk)
        alias_parts.append(_aliases(chunk))
        chunk["Passengers"] = pd.to_numeric(chunk["Passengers"], errors="coerce")
        chunk["MktCoupons"] = pd.to_numeric(chunk["MktCoupons"], errors="coerce")
        chunk["BulkFare"] = pd.to_numeric(chunk["BulkFare"], errors="coerce")
        eligible, exclusions = _sequential_filter(chunk, [
            ("foreign_endpoints", lambda d: ~(d.OriginCountry.astype("string").str.strip().str.upper().eq("US")
                                               & d.DestCountry.astype("string").str.strip().str.upper().eq("US"))),
            ("bulk_or_unknown", lambda d: d.BulkFare.ne(0)),
            ("connecting_or_unknown", lambda d: d.MktCoupons.ne(1)),
            ("missing_or_invalid_passengers", lambda d: ~np.isfinite(d.Passengers) | d.Passengers.le(0)),
        ])
        for key in exclusion_totals:
            exclusion_totals[key] += exclusions[key]
        eligible_rows += len(eligible)
        endpoints = pd.concat([
            eligible[["OriginAirportID", "Passengers"]].rename(
                columns={"OriginAirportID": "AirportID", "Passengers": "passengers"}),
            eligible[["DestAirportID", "Passengers"]].rename(
                columns={"DestAirportID": "AirportID", "Passengers": "passengers"}),
        ], ignore_index=True)
        passenger_parts.append(
            endpoints.groupby("AirportID", as_index=False, observed=True).passengers.sum()
        )
    if not raw_rows:
        raise ValueError("Market archive contains no rows")
    aliases = (pd.concat(alias_parts, ignore_index=True).drop_duplicates()
               .sort_values(["AirportID", "code"], kind="stable").reset_index(drop=True))

    original_ids = set()
    for code in AIRPORTS:
        mapped = aliases.loc[aliases.code.eq(code), "AirportID"].unique()
        if len(mapped) != 1:
            detail = "missing" if len(mapped) == 0 else "ambiguous"
            raise ValueError(f"{detail} original airport mapping for {code}")
        original_ids.add(int(mapped[0]))

    passenger_totals = (pd.concat(passenger_parts, ignore_index=True)
                        .groupby("AirportID", as_index=False, observed=True).passengers.sum())
    passenger_totals = pd.concat([
        passenger_totals,
        pd.DataFrame({"AirportID": sorted(original_ids), "passengers": 0.0}),
    ], ignore_index=True).groupby("AirportID", as_index=False, observed=True).passengers.sum()
    code_lists = (aliases.groupby("AirportID", observed=True).code
                  .agg(lambda values: "|".join(sorted(values))).rename("codes").reset_index())
    ranking = passenger_totals.merge(code_lists, on="AirportID", how="left", validate="one_to_one")
    ranking = ranking.sort_values(["passengers", "AirportID"], ascending=[False, True], kind="stable")
    ranking["rank"] = np.arange(1, len(ranking) + 1)
    selected_ids = set(ranking.head(top_n).AirportID.astype(int)).union(original_ids)
    ranking["selected"] = ranking.AirportID.isin(selected_ids)
    ranking = ranking[["AirportID", "codes", "passengers", "rank", "selected"]].reset_index(drop=True)
    audit = {
        "year": year,
        "quarter": quarter,
        "development_selection_year": year == 2010,
        "raw_rows": raw_rows,
        **exclusion_totals,
        "kept_rows": eligible_rows,
        "eligible_rows": eligible_rows,
        "ranked_airports": len(ranking),
        "top_n": top_n,
        "selected_airports": int(ranking.selected.sum()),
        "original_airport_ids": sorted(original_ids),
    }
    return ranking, audit


def _fare_sample(joined, low, high):
    frame = joined.copy()
    frame["Passengers"] = pd.to_numeric(frame["Passengers"], errors="coerce")
    frame["MktFare"] = pd.to_numeric(frame["MktFare"], errors="coerce")
    frame["MktCoupons"] = pd.to_numeric(frame["MktCoupons"], errors="coerce")
    frame["BulkFare"] = pd.to_numeric(frame["BulkFare"], errors="coerce")
    frame["DollarCred"] = pd.to_numeric(frame["DollarCred"], errors="coerce")
    clean, audit = _sequential_filter(frame, [
        ("foreign_endpoints", lambda d: ~(d.OriginCountry.astype("string").str.strip().str.upper().eq("US")
                                           & d.DestCountry.astype("string").str.strip().str.upper().eq("US"))),
        ("connecting_or_unknown", lambda d: d.MktCoupons.ne(1)),
        ("bulk_or_unknown", lambda d: d.BulkFare.ne(0)),
        ("missing_or_invalid_passengers", lambda d: ~np.isfinite(d.Passengers) | d.Passengers.le(0)),
        ("unmatched_ticket", lambda d: d["_merge"].ne("both")),
        ("unreliable_or_missing_credibility", lambda d: d.DollarCred.ne(1)),
        ("missing_fare", lambda d: ~np.isfinite(d.MktFare)),
        ("fare_bounds", lambda d: ~d.MktFare.between(low, high, inclusive="both")),
    ])
    return clean, audit


def _summarize(frame, sample):
    if frame.empty:
        return pd.DataFrame(columns=CELL_COLUMNS)
    work = frame.copy()
    work["fare_total"] = work.MktFare * work.Passengers
    work["fare_square_total"] = work.MktFare.pow(2) * work.Passengers
    keys = CELL_KEYS[:-1]
    cells = work.groupby(keys, as_index=False, observed=True, dropna=False).agg(
        passengers=("Passengers", "sum"),
        records=("MktID", "size"),
        fare_total=("fare_total", "sum"),
        fare_square_total=("fare_square_total", "sum"),
    )
    cells["sample"] = sample
    cells["fare_mean"] = cells.fare_total / cells.passengers
    cells["fare_variance"] = np.maximum(
        0.0, cells.fare_square_total / cells.passengers - cells.fare_mean.pow(2)
    )
    cells["low_support"] = cells.passengers.lt(30)
    return cells[CELL_COLUMNS]


def process_fares(market_path, ticket_path, *, year, quarter, airport_ids, chunksize=250000):
    """Aggregate both declared fare samples for a stable airport-ID scope."""
    selected_ids = {int(value) for value in airport_ids}
    if not selected_ids:
        raise ValueError("airport_ids must not be empty")

    market_parts = []
    seen_market = set()
    market_rows = scope_rows = 0
    for chunk in _chunks(market_path, MARKET_COLUMNS, chunksize, "Market"):
        _validate_period(chunk, year, quarter, "Market")
        _integer_ids(chunk, ["OriginAirportID", "DestAirportID"], "Market airport")
        _normalize_codes(chunk)
        market_rows += len(chunk)
        scoped = chunk.loc[
            chunk.OriginAirportID.isin(selected_ids)
            & chunk.DestAirportID.isin(selected_ids)
            & chunk.OriginAirportID.ne(chunk.DestAirportID)
        ].copy()
        if scoped[["ItinID", "MktID", "RPCarrier"]].isna().any().any():
            raise ValueError("Missing scoped Market identity")
        scoped["RPCarrier"] = scoped.RPCarrier.astype("string").str.strip().str.upper()
        if scoped.RPCarrier.eq("").any():
            raise ValueError("Missing scoped Market identity")
        _integer_ids(scoped, ["ItinID", "MktID"], "scoped Market")
        keys = set(scoped[["Year", "Quarter", "MktID"]].itertuples(index=False, name=None))
        if len(keys) != len(scoped) or seen_market.intersection(keys):
            raise ValueError("duplicate Market keys in airport-ID scope")
        seen_market.update(keys)
        scope_rows += len(scoped)
        market_parts.append(scoped)
    if not market_rows:
        raise ValueError("Market archive contains no rows")
    market = pd.concat(market_parts, ignore_index=True) if market_parts else pd.DataFrame(columns=MARKET_COLUMNS)
    aliases = _aliases(market)
    wanted = set(market.ItinID.astype(int))

    ticket_parts = []
    seen_ticket = set()
    ticket_rows = scoped_ticket_rows = 0
    for chunk in _chunks(ticket_path, TICKET_COLUMNS, chunksize, "Ticket"):
        _validate_period(chunk, year, quarter, "Ticket")
        ticket_rows += len(chunk)
        if chunk.ItinID.isna().any():
            raise ValueError("Missing Ticket identity: ItinID")
        _integer_ids(chunk, ["ItinID"], "Ticket")
        scoped = chunk.loc[chunk.ItinID.isin(wanted)].copy()
        keys = set(scoped[["Year", "Quarter", "ItinID"]].itertuples(index=False, name=None))
        if len(keys) != len(scoped) or seen_ticket.intersection(keys):
            raise ValueError("duplicate Ticket keys in scoped itineraries")
        seen_ticket.update(keys)
        scoped_ticket_rows += len(scoped)
        ticket_parts.append(scoped)
    if not ticket_rows:
        raise ValueError("Ticket archive contains no rows")
    ticket = pd.concat(ticket_parts, ignore_index=True) if ticket_parts else pd.DataFrame(columns=TICKET_COLUMNS)
    joined = market.merge(
        ticket,
        on=["Year", "Quarter", "ItinID"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    outputs = []
    audit = {
        "year": year,
        "quarter": quarter,
        "market_rows_scanned": market_rows,
        "scope_rows": scope_rows,
        "out_of_scope_rows": market_rows - scope_rows,
        "market_duplicate_keys": 0,
        "ticket_rows_scanned": ticket_rows,
        "ticket_scoped_rows": scoped_ticket_rows,
        "ticket_duplicate_keys": 0,
        "join": {
            "market_rows": len(market),
            "joined_rows": len(joined),
            "matched_rows": int(joined["_merge"].eq("both").sum()),
            "unmatched_rows": int(joined["_merge"].eq("left_only").sum()),
        },
    }
    for sample, low, high in (("primary", 20, 2000), ("broad_fare_bounds", 10, 5000)):
        clean, sample_audit = _fare_sample(joined, low, high)
        cells = _summarize(clean, sample)
        sample_audit["cells"] = len(cells)
        sample_audit["cells_below_30_passengers"] = int(cells.low_support.sum())
        audit[sample] = sample_audit
        outputs.append(cells)
    cells = pd.concat(outputs, ignore_index=True)
    cells = cells.sort_values(CELL_KEYS, kind="stable").reset_index(drop=True)
    return cells, audit, aliases
