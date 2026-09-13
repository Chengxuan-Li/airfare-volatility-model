import zipfile

import numpy as np
import pandas as pd
import pytest


ORIGINAL_AIRPORTS = {
    "ORD": 13930,
    "DEN": 11292,
    "DFW": 11298,
    "ATL": 10397,
    "LAX": 12892,
    "JFK": 12478,
    "SEA": 14747,
}


def write_zip(path, member, rows):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, pd.DataFrame(rows).to_csv(index=False))
    return path


def market_row(mkt_id, itin_id, origin_id, dest_id, **changes):
    reverse_codes = {value: key for key, value in ORIGINAL_AIRPORTS.items()}
    row = {
        "ItinID": itin_id,
        "MktID": mkt_id,
        "Year": 2010,
        "Quarter": 1,
        "OriginAirportID": origin_id,
        "DestAirportID": dest_id,
        "Origin": reverse_codes.get(origin_id, f"A{origin_id}"),
        "Dest": reverse_codes.get(dest_id, f"A{dest_id}"),
        "OriginCountry": "US",
        "DestCountry": "US",
        "RPCarrier": "UA",
        "MktCoupons": 1,
        "BulkFare": 0,
        "Passengers": 1.0,
        "MktFare": 100.0,
    }
    row.update(changes)
    return row


def ticket_row(itin_id, **changes):
    row = {"Year": 2010, "Quarter": 1, "ItinID": itin_id, "DollarCred": 1}
    row.update(changes)
    return row


def baseline_rows():
    rows = []
    for offset, (code, airport_id) in enumerate(ORIGINAL_AIRPORTS.items(), 1):
        rows.append(market_row(offset, offset, airport_id, 16000 + offset,
                               Origin=code, Dest=f"Z{offset}", Passengers=1))
    rows.extend([
        market_row(20, 20, 200, 300, Origin="BBB", Dest="CCC", Passengers=10, MktFare=1),
        market_row(21, 21, 100, 301, Origin="AAA", Dest="DDD", Passengers=10, MktFare=9999),
        market_row(22, 22, 100, 302, Origin="AAX", Dest="EEE", Passengers=2),
        market_row(23, 23, 400, 500, Origin="FOR", Dest="INT", Passengers=100,
                   OriginCountry="CA"),
        market_row(24, 24, 600, 700, Origin="BLK", Dest="ZZZ", Passengers=100,
                   BulkFare=1),
    ])
    return rows


def test_baseline_selection_uses_eligible_passengers_ids_and_stable_ties(tmp_path):
    from src.stage6.annual_fares import select_airports

    path = write_zip(tmp_path / "market.zip", "market.csv", baseline_rows())
    ranking, audit = select_airports(path, top_n=2, chunksize=3)

    assert ranking.loc[:1, "AirportID"].tolist() == [100, 200]
    assert ranking.loc[:1, "rank"].tolist() == [1, 2]
    assert ranking.set_index("AirportID").loc[100, "passengers"] == 12
    assert ranking.set_index("AirportID").loc[100, "codes"] == "AAA|AAX"
    assert set(ranking.loc[ranking.selected, "AirportID"]) == {100, 200, *ORIGINAL_AIRPORTS.values()}
    assert audit["development_selection_year"] is True
    assert audit["excluded_foreign_endpoints"] == 1
    assert audit["excluded_bulk_or_unknown"] == 1


def test_baseline_selection_is_independent_of_fares(tmp_path):
    from src.stage6.annual_fares import select_airports

    rows = baseline_rows()
    first = write_zip(tmp_path / "first.zip", "market.csv", rows)
    changed = [dict(row, MktFare=(-999999 if index % 2 else np.nan))
               for index, row in enumerate(rows)]
    second = write_zip(tmp_path / "second.zip", "market.csv", changed)

    left, _ = select_airports(first, top_n=2, chunksize=4)
    right, _ = select_airports(second, top_n=2, chunksize=4)
    pd.testing.assert_frame_equal(left, right)


def test_baseline_selection_is_identical_across_chunk_boundaries(tmp_path):
    from src.stage6.annual_fares import select_airports

    path = write_zip(tmp_path / "market.zip", "market.csv", baseline_rows())
    whole_ranking, whole_audit = select_airports(path, top_n=2, chunksize=1000)
    chunked_ranking, chunked_audit = select_airports(path, top_n=2, chunksize=2)

    pd.testing.assert_frame_equal(whole_ranking, chunked_ranking)
    assert whole_audit == chunked_audit


def test_original_airport_with_no_eligible_volume_remains_selected(tmp_path):
    from src.stage6.annual_fares import select_airports

    rows = baseline_rows()
    rows[0]["BulkFare"] = 1
    path = write_zip(tmp_path / "market.zip", "market.csv", rows)
    ranking, _ = select_airports(path, top_n=2, chunksize=2)

    ord_row = ranking.loc[ranking.AirportID.eq(ORIGINAL_AIRPORTS["ORD"])].iloc[0]
    assert ord_row.passengers == 0
    assert bool(ord_row.selected)


def test_baseline_selection_rejects_ambiguous_original_code(tmp_path):
    from src.stage6.annual_fares import select_airports

    rows = baseline_rows() + [market_row(90, 90, 99999, 300, Origin="ORD", Dest="CCC")]
    path = write_zip(tmp_path / "market.zip", "market.csv", rows)
    with pytest.raises(ValueError, match="ambiguous original airport"):
        select_airports(path, top_n=2, chunksize=2)


def test_baseline_selection_rejects_missing_airport_id(tmp_path):
    from src.stage6.annual_fares import select_airports

    rows = baseline_rows()
    rows[0]["OriginAirportID"] = np.nan
    path = write_zip(tmp_path / "market.zip", "market.csv", rows)
    with pytest.raises(ValueError, match="Missing Market airport identity"):
        select_airports(path, top_n=2, chunksize=2)


def fare_fixture(tmp_path):
    rows = [
        market_row(1, 1, 100, 200, Origin="AAA", Dest="BBB", Passengers=2, MktFare=100),
        market_row(2, 2, 100, 200, Origin="AAX", Dest="BBB", Passengers=1, MktFare=200),
        market_row(3, 3, 100, 200, Origin="AAA", Dest="BBC", RPCarrier="DL", Passengers=4, MktFare=15),
        market_row(4, 4, 100, 200, Origin="AAA", Dest="BBB", RPCarrier="DL", Passengers=5, MktFare=3000),
        market_row(5, 5, 100, 200, Origin="OLD", Dest="BBB", MktFare=120),
        market_row(6, 6, 100, 200, Origin="AAA", Dest="BBB", MktFare=130),
        market_row(7, 7, 100, 200, Origin="AAA", Dest="BBB", BulkFare=1),
        market_row(8, 8, 100, 200, Origin="AAA", Dest="BBB", MktCoupons=2),
        market_row(9, 9, 100, 200, Origin="AAA", Dest="BBB", Passengers=0),
        market_row(10, 10, 100, 200, Origin="AAA", Dest="BBB", OriginCountry="CA"),
        market_row(11, 11, 999, 200, Origin="OUT", Dest="BBB", MktFare=140),
    ]
    tickets = [ticket_row(i) for i in [1, 2, 3, 4, 7, 8, 9, 10, 11]]
    tickets.append(ticket_row(6, DollarCred=0))
    return (
        write_zip(tmp_path / "market.zip", "market.csv", rows),
        write_zip(tmp_path / "ticket.zip", "ticket.csv", tickets),
    )


def test_fares_keep_reporters_ids_moments_low_support_and_scoped_raw_aliases(tmp_path):
    from src.stage6.annual_fares import process_fares

    market, ticket = fare_fixture(tmp_path)
    cells, audit, aliases = process_fares(
        market, ticket, year=2010, quarter=1, airport_ids=[100, 200], chunksize=2
    )

    assert list(cells.columns) == [
        "Year", "Quarter", "OriginAirportID", "DestAirportID", "RPCarrier", "sample",
        "passengers", "records", "fare_total", "fare_square_total", "fare_mean",
        "fare_variance", "low_support",
    ]
    primary = cells.loc[cells["sample"].eq("primary")].iloc[0]
    assert primary.RPCarrier == "UA"
    assert primary.passengers == 3 and primary.records == 2
    assert primary.fare_total == 400 and primary.fare_square_total == 60000
    assert primary.fare_mean == pytest.approx(400 / 3)
    assert primary.fare_variance == pytest.approx(20000 - (400 / 3) ** 2)
    assert bool(primary.low_support)
    broad = cells.loc[cells["sample"].eq("broad_fare_bounds")]
    assert set(broad.RPCarrier) == {"UA", "DL"}
    assert set(aliases.loc[aliases.AirportID.eq(100), "code"]) >= {"AAA", "AAX", "OLD"}
    assert audit["scope_rows"] == 10 and audit["out_of_scope_rows"] == 1
    assert audit["join"] == {
        "market_rows": 10, "joined_rows": 10, "matched_rows": 9, "unmatched_rows": 1
    }
    assert audit["primary"]["excluded_foreign_endpoints"] == 1
    assert audit["primary"]["excluded_connecting_or_unknown"] == 1
    assert audit["primary"]["excluded_bulk_or_unknown"] == 1
    assert audit["primary"]["excluded_missing_or_invalid_passengers"] == 1
    assert audit["primary"]["excluded_unmatched_ticket"] == 1
    assert audit["primary"]["excluded_unreliable_or_missing_credibility"] == 1
    assert audit["primary"]["excluded_fare_bounds"] == 2
    assert sum(value for key, value in audit["primary"].items() if key.startswith("excluded_")) == 8
    assert audit["primary"]["kept_rows"] == 2


def test_fares_preserve_numeric_looking_carrier_codes_and_leading_zeroes(tmp_path):
    from src.stage6.annual_fares import process_fares

    rows = [
        market_row(1, 1, 100, 200, RPCarrier="01"),
        market_row(2, 2, 100, 200, RPCarrier="AA"),
    ]
    market = write_zip(tmp_path / "market.zip", "market.csv", rows)
    ticket = write_zip(
        tmp_path / "ticket.zip", "ticket.csv", [ticket_row(1), ticket_row(2)]
    )

    cells, _, _ = process_fares(
        market, ticket, year=2010, quarter=1, airport_ids=[100, 200], chunksize=1
    )

    assert set(cells.RPCarrier) == {"01", "AA"}


@pytest.mark.parametrize("table", ["market", "ticket"])
def test_fares_reject_period_mismatch_in_any_national_row(tmp_path, table):
    from src.stage6.annual_fares import process_fares

    market, ticket = fare_fixture(tmp_path)
    target = market if table == "market" else ticket
    with zipfile.ZipFile(target) as archive:
        member = next(name for name in archive.namelist() if name.endswith(".csv"))
        rows = pd.read_csv(archive.open(member))
    rows.loc[len(rows) - 1, "Quarter"] = 2
    write_zip(target, f"{table}.csv", rows)
    with pytest.raises(ValueError, match="period mismatch"):
        process_fares(market, ticket, year=2010, quarter=1, airport_ids=[100, 200], chunksize=2)


@pytest.mark.parametrize("table", ["market", "ticket"])
def test_fares_reject_scoped_duplicate_keys(tmp_path, table):
    from src.stage6.annual_fares import process_fares

    market, ticket = fare_fixture(tmp_path)
    target = market if table == "market" else ticket
    with zipfile.ZipFile(target) as archive:
        member = next(name for name in archive.namelist() if name.endswith(".csv"))
        rows = pd.read_csv(archive.open(member))
    duplicate = rows.iloc[[0]].copy()
    rows = pd.concat([rows, duplicate], ignore_index=True)
    write_zip(target, f"{table}.csv", rows)
    with pytest.raises(ValueError, match=f"duplicate {table.title()}"):
        process_fares(market, ticket, year=2010, quarter=1, airport_ids=[100, 200], chunksize=2)


@pytest.mark.parametrize("column", ["RPCarrier", "MktID"])
def test_fares_reject_missing_scoped_identity_instead_of_grouping_it_away(tmp_path, column):
    from src.stage6.annual_fares import process_fares

    market, ticket = fare_fixture(tmp_path)
    with zipfile.ZipFile(market) as archive:
        rows = pd.read_csv(archive.open("market.csv"))
    rows.loc[0, column] = np.nan
    write_zip(market, "market.csv", rows)
    with pytest.raises(ValueError, match="Missing scoped Market identity"):
        process_fares(market, ticket, year=2010, quarter=1, airport_ids=[100, 200], chunksize=2)
