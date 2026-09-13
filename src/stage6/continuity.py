"""Source-separated continuity diagnostics for two annual Stage 6 panels."""

from __future__ import annotations

import pandas as pd


ANNUAL_TABLES = {
    "airport_ranking.csv",
    "fare_carrier_cells.csv",
    "operations_carrier_month.csv",
    "operations_national_month.csv",
    "airport_aliases.csv",
    "operations_carrier_identities.csv",
    "route_quarter_panel.csv",
}
ROUTE_KEY = ["Quarter", "OriginAirportID", "DestAirportID"]


def _require_tables(tables, label):
    missing = ANNUAL_TABLES - set(tables)
    if missing:
        raise ValueError(f"Missing {label} annual tables: {sorted(missing)}")
    invalid = [name for name in ANNUAL_TABLES if not isinstance(tables[name], pd.DataFrame)]
    if invalid:
        raise TypeError(f"Annual tables must be DataFrames: {sorted(invalid)}")


def _require_columns(frame, columns, label):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing {label} columns: {sorted(missing)}")


def _annual_year(tables, label):
    years = set()
    for name in ANNUAL_TABLES - {"airport_ranking.csv"}:
        frame = tables[name]
        if "Year" in frame and not frame.empty:
            values = pd.to_numeric(frame["Year"], errors="coerce")
            if values.isna().any() or not (values % 1).eq(0).all():
                raise ValueError(f"Invalid Year in {label} {name}")
            years.update(values.astype(int).tolist())
    if len(years) != 1:
        raise ValueError(f"{label} annual tables must contain exactly one consistent year")
    return next(iter(years))


def _integer_series(frame, column, label):
    values = pd.to_numeric(frame[column], errors="coerce")
    if values.isna().any() or not (values % 1).eq(0).all():
        raise ValueError(f"Missing or invalid {label} identity")
    return values.astype(int)


def _strings(frame, column, label):
    if frame[column].isna().any():
        raise ValueError(f"Missing {label} identity")
    return frame[column].astype("string")


def _selected_ids(ranking):
    _require_columns(ranking, ["AirportID", "selected"], "airport ranking")
    selected = ranking["selected"]
    if not pd.api.types.is_bool_dtype(selected):
        normalized = selected.astype("string").str.lower()
        if not normalized.isin(["true", "false"]).all():
            raise ValueError("Invalid airport selected flag")
        selected = normalized.eq("true")
    ids = _integer_series(ranking, "AirportID", "airport")
    result = sorted(ids.loc[selected].unique().tolist())
    if not result:
        raise ValueError("Baseline airport ranking has no selected IDs")
    return result


def _continuity(baseline_present, current_present):
    if baseline_present and current_present:
        return "retained"
    if baseline_present:
        return "exited"
    if current_present:
        return "entered"
    return "absent"


def _code_map(aliases, source, selected_ids):
    _require_columns(aliases, ["AirportID", "code", "source", "Year", "period"], "airport aliases")
    work = aliases.loc[aliases["source"].astype("string").eq(source)].copy()
    work["AirportID"] = _integer_series(work, "AirportID", "airport")
    work["code"] = _strings(work, "code", "airport code")
    work = work.loc[work["AirportID"].isin(selected_ids)]
    return {
        int(airport_id): sorted(group["code"].unique().tolist())
        for airport_id, group in work.groupby("AirportID", observed=True)
    }


def _airport_observations(tables, source, selected_ids):
    if source == "fare_primary":
        frame = tables["fare_carrier_cells.csv"]
        _require_columns(
            frame,
            ["Quarter", "OriginAirportID", "DestAirportID", "sample"],
            "fare carrier",
        )
        work = frame.loc[frame["sample"].astype("string").eq("primary")].copy()
        period = "Quarter"
        alias_source = "DB1B"
    else:
        frame = tables["operations_carrier_month.csv"]
        _require_columns(frame, ["Month", "OriginAirportID", "DestAirportID"], "monthly operations")
        work = frame.copy()
        period = "Month"
        alias_source = "BTS on-time"
    endpoints = []
    for endpoint in ("OriginAirportID", "DestAirportID"):
        part = pd.DataFrame(
            {
                "AirportID": _integer_series(work, endpoint, "airport"),
                "period": _integer_series(work, period, period.lower()),
            }
        )
        endpoints.append(part.loc[part["AirportID"].isin(selected_ids)])
    observed = pd.concat(endpoints, ignore_index=True).drop_duplicates()
    periods = observed.groupby("AirportID", observed=True)["period"].nunique().to_dict()
    codes = _code_map(tables["airport_aliases.csv"], alias_source, selected_ids)
    return {int(key): int(value) for key, value in periods.items()}, codes


def _airport_continuity(baseline, current, baseline_year, current_year, selected_ids):
    rows = []
    for source in ("fare_primary", "operations"):
        baseline_periods, baseline_codes = _airport_observations(baseline, source, selected_ids)
        current_periods, current_codes = _airport_observations(current, source, selected_ids)
        for airport_id in selected_ids:
            baseline_count = baseline_periods.get(airport_id, 0)
            current_count = current_periods.get(airport_id, 0)
            rows.append(
                {
                    "source": source,
                    "AirportID": airport_id,
                    "baseline_year": baseline_year,
                    "current_year": current_year,
                    "baseline_present": bool(baseline_count),
                    "current_present": bool(current_count),
                    "continuity": _continuity(bool(baseline_count), bool(current_count)),
                    "baseline_codes": "|".join(baseline_codes.get(airport_id, [])),
                    "current_codes": "|".join(current_codes.get(airport_id, [])),
                    "baseline_periods_observed": baseline_count,
                    "current_periods_observed": current_count,
                }
            )
    return pd.DataFrame(rows)


def _fare_carriers(tables):
    frame = tables["fare_carrier_cells.csv"]
    _require_columns(frame, ["Quarter", "RPCarrier"], "fare carrier")
    work = pd.DataFrame(
        {
            "reporting_code": _strings(frame, "RPCarrier", "fare carrier"),
            "period": _integer_series(frame, "Quarter", "fare quarter"),
        }
    ).drop_duplicates()
    return work.groupby("reporting_code", observed=True)["period"].nunique().to_dict()


def _operations_carriers(tables):
    frame = tables["operations_carrier_identities.csv"]
    _require_columns(
        frame,
        ["Month", "DOT_ID_Reporting_Airline", "Reporting_Airline"],
        "operations carrier identities",
    )
    work = pd.DataFrame(
        {
            "dot_id": _integer_series(frame, "DOT_ID_Reporting_Airline", "operations carrier"),
            "reporting_code": _strings(frame, "Reporting_Airline", "operations carrier"),
            "period": _integer_series(frame, "Month", "operations month"),
        }
    ).drop_duplicates()
    return {
        (int(dot_id), str(code)): int(group["period"].nunique())
        for (dot_id, code), group in work.groupby(["dot_id", "reporting_code"], observed=True)
    }


def _carrier_continuity(baseline, current, baseline_year, current_year):
    rows = []
    baseline_fares, current_fares = _fare_carriers(baseline), _fare_carriers(current)
    for code in sorted(set(baseline_fares) | set(current_fares)):
        baseline_count, current_count = baseline_fares.get(code, 0), current_fares.get(code, 0)
        rows.append(
            {
                "source": "DB1B",
                "dot_id": pd.NA,
                "reporting_code": str(code),
                "baseline_year": baseline_year,
                "current_year": current_year,
                "baseline_present": bool(baseline_count),
                "current_present": bool(current_count),
                "continuity": _continuity(bool(baseline_count), bool(current_count)),
                "baseline_periods_observed": baseline_count,
                "current_periods_observed": current_count,
            }
        )
    baseline_ops, current_ops = _operations_carriers(baseline), _operations_carriers(current)
    for dot_id, code in sorted(set(baseline_ops) | set(current_ops)):
        baseline_count = baseline_ops.get((dot_id, code), 0)
        current_count = current_ops.get((dot_id, code), 0)
        rows.append(
            {
                "source": "operations",
                "dot_id": dot_id,
                "reporting_code": str(code),
                "baseline_year": baseline_year,
                "current_year": current_year,
                "baseline_present": bool(baseline_count),
                "current_present": bool(current_count),
                "continuity": _continuity(bool(baseline_count), bool(current_count)),
                "baseline_periods_observed": baseline_count,
                "current_periods_observed": current_count,
            }
        )
    return pd.DataFrame(rows)


def _panel_routes(tables):
    frame = tables["route_quarter_panel.csv"]
    key = ROUTE_KEY + ["sample"]
    _require_columns(frame, key + ["coverage"], "route-quarter panel")
    work = frame[key + ["coverage"]].copy()
    for column in ROUTE_KEY:
        work[column] = _integer_series(work, column, "route-quarter panel")
    work["sample"] = _strings(work, "sample", "fare sample")
    work["coverage"] = _strings(work, "coverage", "route coverage")
    allowed = {"matched", "fare_only", "operations_only"}
    if not work["coverage"].isin(allowed).all():
        raise ValueError("Invalid route-quarter coverage")
    if work.duplicated(key).any():
        raise ValueError("Duplicate route-quarter sample identities")
    return {
        tuple(row[column] for column in key): (
            row["coverage"] in {"matched", "fare_only"},
            row["coverage"] in {"matched", "operations_only"},
        )
        for _, row in work.iterrows()
    }


def _route_continuity(baseline, current, baseline_year, current_year):
    baseline_routes, current_routes = _panel_routes(baseline), _panel_routes(current)
    samples = {"primary", "broad_fare_bounds"}
    samples.update(key[3] for key in set(baseline_routes) | set(current_routes))
    route_keys = {
        (quarter, origin, destination)
        for quarter, origin, destination, _ in set(baseline_routes) | set(current_routes)
    }
    rows = []
    for sample in sorted(samples, key=lambda value: (value != "primary", value != "broad_fare_bounds", value)):
        for quarter, origin, destination in sorted(route_keys):
            fare_key = (quarter, origin, destination, sample)
            baseline_fare, baseline_operations = baseline_routes.get(fare_key, (False, False))
            current_fare, current_operations = current_routes.get(fare_key, (False, False))
            rows.append(
                {
                    "Quarter": quarter,
                    "OriginAirportID": origin,
                    "DestAirportID": destination,
                    "sample": sample,
                    "baseline_year": baseline_year,
                    "current_year": current_year,
                    "baseline_fare_present": baseline_fare,
                    "current_fare_present": current_fare,
                    "fare_continuity": _continuity(baseline_fare, current_fare),
                    "baseline_operations_present": baseline_operations,
                    "current_operations_present": current_operations,
                    "operations_continuity": _continuity(baseline_operations, current_operations),
                }
            )
    return pd.DataFrame(rows)


def _alias_audit(baseline, current, selected_ids):
    changes = []
    for source in ("BTS on-time", "DB1B"):
        baseline_codes = _code_map(baseline["airport_aliases.csv"], source, selected_ids)
        current_codes = _code_map(current["airport_aliases.csv"], source, selected_ids)
        for airport_id in selected_ids:
            before, after = baseline_codes.get(airport_id, []), current_codes.get(airport_id, [])
            if before and after and before != after:
                changes.append(
                    {
                        "source": source,
                        "AirportID": airport_id,
                        "baseline_codes": before,
                        "current_codes": after,
                    }
                )
    return changes


def _operations_code_reuse(baseline, current):
    identities = []
    for tables in (baseline, current):
        observed = _operations_carriers(tables)
        identities.extend((code, dot_id) for dot_id, code in observed)
    mapping = pd.DataFrame(identities, columns=["reporting_code", "dot_id"]).drop_duplicates()
    reused = []
    for code, group in mapping.groupby("reporting_code", observed=True):
        dot_ids = sorted(int(value) for value in group["dot_id"].unique())
        if len(dot_ids) > 1:
            reused.append({"reporting_code": str(code), "dot_ids": dot_ids})
    return reused


def _airport_code_reuse(baseline, current, selected_ids):
    identities = []
    for source in ("BTS on-time", "DB1B"):
        for tables in (baseline, current):
            mapping = _code_map(tables["airport_aliases.csv"], source, selected_ids)
            identities.extend(
                (source, code, airport_id)
                for airport_id, codes in mapping.items()
                for code in codes
            )
    mapping = pd.DataFrame(
        identities, columns=["source", "code", "AirportID"]
    ).drop_duplicates()
    reused = []
    for (source, code), group in mapping.groupby(["source", "code"], observed=True):
        airport_ids = sorted(int(value) for value in group["AirportID"].unique())
        if len(airport_ids) > 1:
            reused.append(
                {"source": str(source), "code": str(code), "airport_ids": airport_ids}
            )
    return reused


def _status_counts(frame, column):
    return {str(key): int(value) for key, value in frame[column].value_counts().sort_index().items()}


def compare_years(baseline_tables, current_tables):
    """Compare two annual output dictionaries without modifying either input."""
    _require_tables(baseline_tables, "baseline")
    _require_tables(current_tables, "current")
    baseline_year = _annual_year(baseline_tables, "baseline")
    current_year = _annual_year(current_tables, "current")
    if baseline_year == current_year:
        raise ValueError("Baseline and current annual tables must have different years")
    selected_ids = _selected_ids(baseline_tables["airport_ranking.csv"])

    airports = _airport_continuity(
        baseline_tables, current_tables, baseline_year, current_year, selected_ids
    )
    carriers = _carrier_continuity(baseline_tables, current_tables, baseline_year, current_year)
    routes = _route_continuity(baseline_tables, current_tables, baseline_year, current_year)
    audit = {
        "baseline_year": baseline_year,
        "current_year": current_year,
        "selected_airport_ids": selected_ids,
        "airport_rows": len(airports),
        "carrier_rows": len(carriers),
        "route_rows": len(routes),
        "airport_continuity": _status_counts(airports, "continuity"),
        "carrier_continuity": _status_counts(carriers, "continuity"),
        "fare_route_continuity": _status_counts(routes, "fare_continuity"),
        "operations_route_continuity": _status_counts(routes, "operations_continuity"),
        "airport_alias_changes": _alias_audit(baseline_tables, current_tables, selected_ids),
        "airport_codes_with_multiple_ids": _airport_code_reuse(
            baseline_tables, current_tables, selected_ids
        ),
        "operations_codes_with_multiple_dot_ids": _operations_code_reuse(
            baseline_tables, current_tables
        ),
        "carrier_linkage": "None; DB1B reporting codes and operations DOT-ID/code identities remain source-separated",
        "absence_interpretation": "Observed source absence only; no outcome, cancellation, or numeric-zero imputation",
    }
    return {
        "airport_continuity.csv": airports,
        "carrier_continuity.csv": carriers,
        "route_continuity.csv": routes,
    }, audit
