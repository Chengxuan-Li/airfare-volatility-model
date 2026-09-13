"""Declared Stage 6 annual periods and matched-period table restriction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import pandas as pd


FIRST_YEAR = 2010
LAST_YEAR = 2025


@dataclass(frozen=True)
class YearPeriods:
    """The fare quarters and operations months requested for one Stage 6 year."""

    year: int
    quarters: tuple[int, ...]
    months: tuple[int, ...]
    label: str
    partial_year: bool


def periods_for_year(year: int) -> YearPeriods:
    """Return the fixed period declaration for a supported Stage 6 year."""
    if not isinstance(year, int) or isinstance(year, bool) or not FIRST_YEAR <= year <= LAST_YEAR:
        raise ValueError(f"Stage 6 year must be an integer from {FIRST_YEAR} through {LAST_YEAR}")
    if year == LAST_YEAR:
        return YearPeriods(
            year=year,
            quarters=(1, 2),
            months=(1, 2, 3, 4, 5, 6),
            label="2025 Q1-Q2 / January-June",
            partial_year=True,
        )
    return YearPeriods(
        year=year,
        quarters=(1, 2, 3, 4),
        months=tuple(range(1, 13)),
        label=str(year),
        partial_year=False,
    )


_QUARTER_TABLES = {"fare_carrier_cells.csv", "route_quarter_panel.csv"}
_MONTH_TABLES = {
    "operations_carrier_month.csv",
    "operations_national_month.csv",
    "operations_carrier_identities.csv",
}
_ALIAS_PERIODS = {"DB1B": "quarter", "BTS on-time": "month"}


def restrict_tables_to_periods(
    tables: Mapping[str, pd.DataFrame], periods: YearPeriods
) -> dict[str, pd.DataFrame]:
    """Copy annual tables, retaining only periods comparable with ``periods``."""
    restricted: dict[str, pd.DataFrame] = {}
    for name, frame in tables.items():
        if not isinstance(frame, pd.DataFrame):
            raise TypeError(f"Annual table {name} must be a DataFrame")
        if name in _QUARTER_TABLES:
            if "Quarter" not in frame:
                raise ValueError(f"Missing Quarter in {name}")
            result = frame.loc[frame["Quarter"].isin(periods.quarters)]
        elif name in _MONTH_TABLES:
            if "Month" not in frame:
                raise ValueError(f"Missing Month in {name}")
            result = frame.loc[frame["Month"].isin(periods.months)]
        elif name == "airport_aliases.csv":
            if not {"source", "period"}.issubset(frame.columns):
                raise ValueError("Missing source or period in airport_aliases.csv")
            sources = set(frame["source"].dropna().astype(str).unique())
            unknown = sources - set(_ALIAS_PERIODS)
            if unknown:
                raise ValueError(f"Unknown airport alias source: {sorted(unknown)}")
            keep = pd.Series(False, index=frame.index)
            keep |= frame["source"].eq("DB1B") & frame["period"].isin(periods.quarters)
            keep |= frame["source"].eq("BTS on-time") & frame["period"].isin(periods.months)
            result = frame.loc[keep]
        else:
            result = frame
        restricted[name] = result.copy().reset_index(drop=True)
    return restricted
