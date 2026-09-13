import pandas as pd
import pytest

from src.stage6.periods import periods_for_year, restrict_tables_to_periods


@pytest.mark.parametrize("year", range(2010, 2025))
def test_complete_years_declare_four_quarters_and_twelve_months(year):
    periods = periods_for_year(year)

    assert periods.year == year
    assert periods.quarters == (1, 2, 3, 4)
    assert periods.months == tuple(range(1, 13))
    assert periods.partial_year is False
    assert periods.label == str(year)


def test_2025_is_fixed_at_q2_and_june():
    periods = periods_for_year(2025)

    assert periods.quarters == (1, 2)
    assert periods.months == (1, 2, 3, 4, 5, 6)
    assert periods.partial_year is True
    assert periods.label == "2025 Q1-Q2 / January-June"


@pytest.mark.parametrize("year", [2009, 2026, True, False, 2010.0, "2010", None])
def test_period_declaration_rejects_out_of_range_and_noninteger_years(year):
    with pytest.raises(ValueError, match="year"):
        periods_for_year(year)


def test_partial_period_restriction_covers_every_period_bearing_annual_table():
    tables = {
        "airport_ranking.csv": pd.DataFrame({"AirportID": [1], "selected": [True]}),
        "fare_carrier_cells.csv": pd.DataFrame({"Quarter": [1, 2, 3, 4], "value": range(4)}),
        "operations_carrier_month.csv": pd.DataFrame({"Month": [1, 6, 7, 12], "value": range(4)}),
        "operations_national_month.csv": pd.DataFrame({"Month": [1, 6, 7, 12], "value": range(4)}),
        "operations_carrier_identities.csv": pd.DataFrame({"Month": [1, 6, 7, 12], "value": range(4)}),
        "route_quarter_panel.csv": pd.DataFrame({"Quarter": [1, 2, 3, 4], "value": range(4)}),
        "airport_aliases.csv": pd.DataFrame(
            {
                "source": ["DB1B", "DB1B", "BTS on-time", "BTS on-time"],
                "period": [2, 3, 6, 7],
                "value": range(4),
            }
        ),
    }

    restricted = restrict_tables_to_periods(tables, periods_for_year(2025))

    assert restricted["airport_ranking.csv"] is not tables["airport_ranking.csv"]
    assert restricted["airport_ranking.csv"].equals(tables["airport_ranking.csv"])
    assert restricted["fare_carrier_cells.csv"].Quarter.tolist() == [1, 2]
    assert restricted["route_quarter_panel.csv"].Quarter.tolist() == [1, 2]
    for name in (
        "operations_carrier_month.csv",
        "operations_national_month.csv",
        "operations_carrier_identities.csv",
    ):
        assert restricted[name].Month.tolist() == [1, 6]
    assert restricted["airport_aliases.csv"][["source", "period"]].values.tolist() == [
        ["DB1B", 2],
        ["BTS on-time", 6],
    ]
    assert tables["fare_carrier_cells.csv"].Quarter.tolist() == [1, 2, 3, 4]


def test_period_restriction_rejects_unknown_alias_period_units():
    tables = {
        "airport_aliases.csv": pd.DataFrame({"source": ["unknown"], "period": [1]}),
    }

    with pytest.raises(ValueError, match="alias source"):
        restrict_tables_to_periods(tables, periods_for_year(2025))
