from datetime import datetime, timezone
import json
import threading
import time

import pytest

from src.stage6.inventory import (
    default_requests,
    fare_requests,
    main,
    ontime_request,
    probe_inventory,
)


def test_fare_requests_cover_the_authorized_horizon_deterministically():
    requests = list(fare_requests(2010, 2025, 2))

    assert len(requests) == 124
    assert len({request["url"] for request in requests}) == 124
    assert requests[0] == {
        "kind": "fare",
        "table": "DB1BMarket",
        "year": 2010,
        "quarter": 1,
        "url": (
            "https://transtats.bts.gov/PREZIP/"
            "Origin_and_Destination_Survey_DB1BMarket_2010_1.zip"
        ),
    }
    assert requests[-1] == {
        "kind": "fare",
        "table": "DB1BTicket",
        "year": 2025,
        "quarter": 2,
        "url": (
            "https://transtats.bts.gov/PREZIP/"
            "Origin_and_Destination_Survey_DB1BTicket_2025_2.zip"
        ),
    }


@pytest.mark.parametrize(
    "args",
    [
        (1992, 2025, 2),
        (2025, 2025, 3),
        (2026, 2026, 1),
        (2024, 2024, 0),
        (2024, 2024, 5),
        (2025, 2024, 4),
    ],
)
def test_fare_requests_reject_ranges_outside_documented_db1b_history(args):
    with pytest.raises(ValueError):
        list(fare_requests(*args))


def test_ontime_request_marks_the_documented_filename_as_a_recipe_probe():
    assert ontime_request(2024, 1) == {
        "kind": "operations",
        "table": "On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)",
        "year": 2024,
        "month": 1,
        "url": (
            "https://transtats.bts.gov/PREZIP/"
            "On_Time_Reporting_Carrier_On_Time_Performance_"
            "1987_present_2024_1.zip"
        ),
        "recipe_probe": True,
    }


@pytest.mark.parametrize("year, month", [(1986, 12), (2024, 0), (2024, 13)])
def test_ontime_request_rejects_invalid_periods(year, month):
    with pytest.raises(ValueError):
        ontime_request(year, month)


def test_default_requests_include_fares_and_two_recipe_probes():
    requests = default_requests()

    assert len(requests) == 126
    assert requests[-2:] == [ontime_request(2010, 1), ontime_request(2024, 1)]


def test_probe_inventory_captures_head_metadata_errors_and_summary():
    requests = [
        {"kind": "fare", "table": "DB1BMarket", "year": 2025,
         "quarter": 2, "url": "https://example.test/available.zip"},
        {"kind": "operations", "table": "on-time", "year": 2010,
         "month": 1, "url": "https://example.test/missing.zip",
         "recipe_probe": True},
    ]
    seen = []

    class Response:
        status_code = 200
        url = "https://cdn.example.test/available.zip"
        headers = {
            "Content-Length": "1234",
            "Content-Type": "application/zip",
            "Last-Modified": "Fri, 27 Jun 2025 20:19:03 GMT",
            "ETag": '"abc"',
        }

    def transport(url, **kwargs):
        seen.append((url, kwargs))
        if url.endswith("missing.zip"):
            raise TimeoutError("probe timed out")
        return Response()

    inventory = probe_inventory(
        requests,
        transport=transport,
        timeout=(3, 7),
        now=lambda: datetime(2026, 9, 12, 15, 30, tzinfo=timezone.utc),
    )

    assert inventory["requests"] == requests
    assert inventory["method"] == "HEAD"
    assert inventory["schema_verified"] is False
    assert inventory["summary"] == {
        "request_count": 2,
        "success_count": 1,
        "failure_count": 1,
        "advertised_bytes_total": 1234,
    }
    assert inventory["results"][0] == {
        "request_index": 0,
        "requested_at_utc": "2026-09-12T15:30:00Z",
        "status": 200,
        "final_url": "https://cdn.example.test/available.zip",
        "headers": {
            "content_length": 1234,
            "content_type": "application/zip",
            "last_modified": "Fri, 27 Jun 2025 20:19:03 GMT",
            "etag": '"abc"',
        },
        "error": None,
        "success": True,
    }
    assert inventory["results"][1]["status"] is None
    assert inventory["results"][1]["final_url"] is None
    assert inventory["results"][1]["headers"] == {
        "content_length": None,
        "content_type": None,
        "last_modified": None,
        "etag": None,
    }
    assert inventory["results"][1]["error"] == "TimeoutError: probe timed out"
    assert inventory["results"][1]["success"] is False
    assert dict(seen) == {
        "https://example.test/available.zip": {
            "allow_redirects": True, "timeout": (3, 7)
        },
        "https://example.test/missing.zip": {
            "allow_redirects": True, "timeout": (3, 7)
        },
    }


def test_probe_inventory_never_exceeds_two_concurrent_requests():
    lock = threading.Lock()
    active = 0
    maximum = 0

    class Response:
        status_code = 404
        headers = {}

        def __init__(self, url):
            self.url = url

    def transport(url, **_kwargs):
        nonlocal active, maximum
        with lock:
            active += 1
            maximum = max(maximum, active)
        time.sleep(0.01)
        with lock:
            active -= 1
        return Response(url)

    requests = [
        {"kind": "fare", "table": "DB1BMarket", "year": 2025,
         "quarter": 1, "url": f"https://example.test/{index}.zip"}
        for index in range(6)
    ]

    inventory = probe_inventory(requests, transport=transport, max_workers=2)

    assert maximum == 2
    assert [result["request_index"] for result in inventory["results"]] == list(range(6))
    assert inventory["summary"]["success_count"] == 0


@pytest.mark.parametrize("max_workers", [0, 3])
def test_probe_inventory_rejects_worker_counts_outside_bound(max_workers):
    with pytest.raises(ValueError):
        probe_inventory([], max_workers=max_workers)


@pytest.mark.parametrize("timeout", [(float("nan"), 1), (1, float("inf"))])
def test_probe_inventory_rejects_non_finite_timeouts(timeout):
    with pytest.raises(ValueError, match="finite"):
        probe_inventory([], timeout=timeout)


def test_negative_content_length_is_not_counted_and_response_is_closed():
    class Response:
        status_code = 200
        url = "https://example.test/archive.zip"
        headers = {"Content-Length": "-42"}

        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    response = Response()
    inventory = probe_inventory(
        [{"kind": "fare", "table": "DB1BMarket", "year": 2025,
          "quarter": 2, "url": response.url}],
        transport=lambda *_args, **_kwargs: response,
    )

    assert response.closed is True
    assert inventory["results"][0]["headers"]["content_length"] is None
    assert inventory["summary"]["advertised_bytes_total"] == 0


def test_cli_requires_explicit_write_action(tmp_path):
    output = tmp_path / "inventory.json"

    with pytest.raises(SystemExit) as error:
        main(["--output", str(output)])

    assert error.value.code == 2
    assert not output.exists()


def test_cli_preserves_existing_inventory_before_any_probe(tmp_path, monkeypatch):
    output = tmp_path / "inventory.json"
    original = b'{"failure": "original 404"}\n'
    output.write_bytes(original)
    calls = []

    def probe(*args, **kwargs):
        calls.append(True)
        return {"summary": {"advertised_bytes_total": 0}}

    monkeypatch.setattr("src.stage6.inventory.probe_inventory", probe)
    with pytest.raises(SystemExit) as error:
        main(["--write", "--output", str(output)])

    assert error.value.code == 2
    assert calls == []
    assert output.read_bytes() == original


@pytest.mark.parametrize("value", ["nan", "inf"])
def test_cli_rejects_non_finite_timeouts_before_writing(tmp_path, monkeypatch, value):
    output = tmp_path / "inventory.json"
    def fail_if_probe_starts():
        raise AssertionError("CLI started inventory probes")
    monkeypatch.setattr("src.stage6.inventory.default_requests", fail_if_probe_starts)

    with pytest.raises(SystemExit) as error:
        main(["--write", "--output", str(output), "--read-timeout", value])

    assert error.value.code == 2
    assert not output.exists()


def test_cli_writes_inventory_only_for_explicit_action(tmp_path, monkeypatch):
    output = tmp_path / "manifests" / "inventory.json"
    seen = []

    class Response:
        status_code = 200
        headers = {"Content-Length": "10"}

        def __init__(self, url):
            self.url = url

    def transport(url, **kwargs):
        seen.append((url, kwargs))
        return Response(url)

    monkeypatch.setattr("src.stage6.inventory.requests.head", transport)

    result = main([
        "--write",
        "--output", str(output),
        "--connect-timeout", "4",
        "--read-timeout", "9",
        "--workers", "1",
    ])

    assert result == 0
    assert len(seen) == 126
    assert all(kwargs == {"allow_redirects": True, "timeout": (4.0, 9.0)}
               for _, kwargs in seen)
    assert output.read_text(encoding="utf-8").endswith("\n")
    inventory = json.loads(output.read_text(encoding="utf-8"))
    assert len(inventory["requests"]) == 126
    assert len(inventory["results"]) == 126
    assert inventory["summary"]["success_count"] == 126
    assert inventory["summary"]["advertised_bytes_total"] == 1260
    assert inventory["summary"]["advertised_bytes_fit_free_disk"] is True
    assert inventory["summary"]["free_bytes_at_inventory"] > 0
