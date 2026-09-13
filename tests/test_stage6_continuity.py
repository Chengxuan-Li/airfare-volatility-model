import copy

import pandas as pd
import pytest

from src.stage6.continuity import compare_years


REQUIRED_TABLES = {
    "airport_ranking.csv",
    "fare_carrier_cells.csv",
    "operations_carrier_month.csv",
    "operations_national_month.csv",
    "airport_aliases.csv",
    "operations_carrier_identities.csv",
    "route_quarter_panel.csv",
}


def annual_tables(year, *, current=False):
    ranking = pd.DataFrame(
        {
            "AirportID": [10, 20, 30],
            "codes": ["AAA", "BBB", "CCC"],
            "passengers": [300.0, 200.0, 100.0],
            "rank": [1, 2, 3],
            "selected": [True, True, True],
        }
    )
    if current:
        fares = pd.DataFrame(
            [
                [year, 1, 10, 20, "01", "primary"],
                [year, 1, 20, 10, "ZZ", "broad_fare_bounds"],
                [year, 2, 20, 30, "NEW", "primary"],
            ],
            columns=["Year", "Quarter", "OriginAirportID", "DestAirportID", "RPCarrier", "sample"],
        )
        operations = pd.DataFrame(
            [
                [year, 1, 200, "01", 10, 20],
                [year, 2, 201, "XY", 10, 20],
                [year, 4, 300, "NEW", 20, 30],
            ],
            columns=["Year", "Month", "DOT_ID_Reporting_Airline", "Reporting_Airline", "OriginAirportID", "DestAirportID"],
        )
        identities = pd.DataFrame(
            [[year, 1, 200, "01"], [year, 2, 201, "XY"], [year, 4, 300, "NEW"]],
            columns=["Year", "Month", "DOT_ID_Reporting_Airline", "Reporting_Airline"],
        )
        aliases = pd.DataFrame(
            [
                [10, "AAX", "DB1B", year, 1],
                [20, "BBB", "DB1B", year, 1],
                [10, "AAA", "BTS on-time", year, 1],
                [20, "BBX", "BTS on-time", year, 1],
                [30, "CCC", "BTS on-time", year, 4],
            ],
            columns=["AirportID", "code", "source", "Year", "period"],
        )
    else:
        fares = pd.DataFrame(
            [
                [year, 1, 10, 20, "01", "primary"],
                [year, 2, 10, 30, "OLD", "primary"],
                [year, 1, 10, 20, "01", "broad_fare_bounds"],
            ],
            columns=["Year", "Quarter", "OriginAirportID", "DestAirportID", "RPCarrier", "sample"],
        )
        operations = pd.DataFrame(
            [
                [year, 1, 100, "01", 10, 20],
                [year, 2, 100, "01", 10, 20],
                [year, 7, 201, "XY", 30, 10],
            ],
            columns=["Year", "Month", "DOT_ID_Reporting_Airline", "Reporting_Airline", "OriginAirportID", "DestAirportID"],
        )
        identities = pd.DataFrame(
            [[year, 1, 100, "01"], [year, 2, 100, "01"], [year, 7, 201, "XY"]],
            columns=["Year", "Month", "DOT_ID_Reporting_Airline", "Reporting_Airline"],
        )
        aliases = pd.DataFrame(
            [
                [10, "AAA", "DB1B", year, 1],
                [10, "AAA", "DB1B", year, 2],
                [20, "BBB", "DB1B", year, 1],
                [30, "CCC", "DB1B", year, 2],
                [10, "AAA", "BTS on-time", year, 1],
                [20, "BBB", "BTS on-time", year, 1],
                [30, "CCC", "BTS on-time", year, 7],
            ],
            columns=["AirportID", "code", "source", "Year", "period"],
        )

    if current:
        route_panel = pd.DataFrame(
            [
                [year, 1, 10, 20, "primary", "matched"],
                [year, 2, 20, 30, "primary", "matched"],
                [year, 4, 20, 10, "primary", "operations_only"],
                [year, 1, 20, 10, "broad_fare_bounds", "fare_only"],
            ],
            columns=["Year", "Quarter", "OriginAirportID", "DestAirportID", "sample", "coverage"],
        )
    else:
        route_panel = pd.DataFrame(
            [
                [year, 1, 10, 20, "primary", "matched"],
                [year, 2, 10, 30, "primary", "fare_only"],
                [year, 3, 30, 10, "primary", "operations_only"],
                [year, 1, 10, 20, "broad_fare_bounds", "matched"],
            ],
            columns=["Year", "Quarter", "OriginAirportID", "DestAirportID", "sample", "coverage"],
        )
    return {
        "airport_ranking.csv": ranking,
        "fare_carrier_cells.csv": fares,
        "operations_carrier_month.csv": operations,
        "operations_national_month.csv": identities.rename(columns={"Month": "Month"}),
        "airport_aliases.csv": aliases,
        "operations_carrier_identities.csv": identities,
        "route_quarter_panel.csv": route_panel,
    }


def test_airport_continuity_uses_frozen_selection_and_reports_source_presence():
    baseline = annual_tables(2010)
    current = annual_tables(2011, current=True)
    current["airport_ranking.csv"] = current["airport_ranking.csv"].iloc[:1].copy()
    before_baseline = copy.deepcopy(baseline)
    before_current = copy.deepcopy(current)

    extra, audit = compare_years(baseline, current)

    airports = extra["airport_continuity.csv"]
    assert list(airports.columns) == [
        "source", "AirportID", "baseline_year", "current_year",
        "baseline_present", "current_present", "continuity",
        "baseline_codes", "current_codes", "baseline_periods_observed",
        "current_periods_observed",
    ]
    assert set(airports["AirportID"]) == {10, 20, 30}
    assert len(airports) == 6
    fare_30 = airports[(airports.source == "fare_primary") & (airports.AirportID == 30)].iloc[0]
    assert fare_30[["baseline_present", "current_present", "continuity"]].tolist() == [True, True, "retained"]
    assert fare_30[["baseline_codes", "current_codes"]].tolist() == ["CCC", ""]
    assert fare_30[["baseline_periods_observed", "current_periods_observed"]].tolist() == [1, 1]
    ops_30 = airports[(airports.source == "operations") & (airports.AirportID == 30)].iloc[0]
    assert ops_30[["baseline_periods_observed", "current_periods_observed"]].tolist() == [1, 1]
    assert audit["airport_alias_changes"] == [
        {"source": "BTS on-time", "AirportID": 20, "baseline_codes": ["BBB"], "current_codes": ["BBX"]},
        {"source": "DB1B", "AirportID": 10, "baseline_codes": ["AAA"], "current_codes": ["AAX"]},
    ]
    for name in REQUIRED_TABLES:
        pd.testing.assert_frame_equal(baseline[name], before_baseline[name])
        pd.testing.assert_frame_equal(current[name], before_current[name])


def test_carrier_continuity_keeps_fare_codes_separate_from_operations_dot_ids():
    extra, audit = compare_years(annual_tables(2010), annual_tables(2011, current=True))

    carriers = extra["carrier_continuity.csv"]
    fare_01 = carriers[(carriers.source == "DB1B") & (carriers.reporting_code == "01")].iloc[0]
    assert pd.isna(fare_01.dot_id)
    assert fare_01[["baseline_present", "current_present", "continuity"]].tolist() == [True, True, "retained"]
    ops_100 = carriers[(carriers.source == "operations") & (carriers.dot_id == 100)].iloc[0]
    assert ops_100[["reporting_code", "baseline_periods_observed", "current_periods_observed", "continuity"]].tolist() == ["01", 2, 0, "exited"]
    ops_200 = carriers[(carriers.source == "operations") & (carriers.dot_id == 200)].iloc[0]
    assert ops_200[["reporting_code", "continuity"]].tolist() == ["01", "entered"]
    assert audit["operations_codes_with_multiple_dot_ids"] == [
        {"reporting_code": "01", "dot_ids": [100, 200]}
    ]
    assert carriers.reporting_code.map(type).eq(str).all()


def test_audit_reports_airport_code_reuse_across_years_without_inference():
    baseline = annual_tables(2010)
    current = annual_tables(2011, current=True)
    current["airport_aliases.csv"] = pd.concat(
        [
            current["airport_aliases.csv"],
            pd.DataFrame([[20, "AAA", "DB1B", 2011, 2]], columns=current["airport_aliases.csv"].columns),
        ],
        ignore_index=True,
    )

    _, audit = compare_years(baseline, current)

    assert audit["airport_codes_with_multiple_ids"] == [
        {"source": "DB1B", "code": "AAA", "airport_ids": [10, 20]}
    ]


def test_route_continuity_compares_equal_quarters_and_never_imputes_absence():
    extra, _ = compare_years(annual_tables(2010), annual_tables(2011, current=True))

    routes = extra["route_continuity.csv"]
    key = (routes["Quarter"] == 1) & (routes.OriginAirportID == 10) & (routes.DestAirportID == 20)
    primary = routes[key & routes["sample"].eq("primary")].iloc[0]
    assert primary[["baseline_fare_present", "current_fare_present", "fare_continuity"]].tolist() == [True, True, "retained"]
    assert primary[["baseline_operations_present", "current_operations_present", "operations_continuity"]].tolist() == [True, True, "retained"]

    exited = routes[(routes["Quarter"] == 2) & (routes.OriginAirportID == 10) & (routes.DestAirportID == 30) & routes["sample"].eq("primary")].iloc[0]
    assert exited[["baseline_fare_present", "current_fare_present", "fare_continuity"]].tolist() == [True, False, "exited"]
    assert exited[["baseline_operations_present", "current_operations_present", "operations_continuity"]].tolist() == [False, False, "absent"]

    ops_only = routes[(routes["Quarter"] == 3) & (routes.OriginAirportID == 30) & (routes.DestAirportID == 10) & routes["sample"].eq("primary")].iloc[0]
    assert ops_only[["baseline_fare_present", "current_fare_present", "fare_continuity"]].tolist() == [False, False, "absent"]
    assert ops_only[["baseline_operations_present", "current_operations_present", "operations_continuity"]].tolist() == [True, False, "exited"]
    panel_only = routes[(routes["Quarter"] == 4) & (routes.OriginAirportID == 20) & (routes.DestAirportID == 10) & routes["sample"].eq("primary")].iloc[0]
    assert panel_only[["baseline_operations_present", "current_operations_present", "operations_continuity"]].tolist() == [False, True, "entered"]
    assert not any(column in routes for column in ("flights", "passengers", "fare_mean", "cancellation_rate"))


def test_compare_years_requires_the_complete_annual_table_contract():
    baseline = annual_tables(2010)
    baseline.pop("airport_aliases.csv")

    with pytest.raises(ValueError, match="airport_aliases.csv"):
        compare_years(baseline, annual_tables(2011, current=True))
