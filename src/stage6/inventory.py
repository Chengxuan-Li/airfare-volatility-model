"""Build a bounded public-endpoint access inventory for Stage 6."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import shutil

import requests

PREZIP = "https://transtats.bts.gov/PREZIP"
DB1B_FIRST_YEAR = 1993
DB1B_LAST_PERIOD = (2025, 2)
ONTIME_TABLE = "On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)"
ONTIME_FILENAME_TABLE = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present"
DEFAULT_TIMEOUT = (10, 30)
DEFAULT_OUTPUT = Path("data/manifests/stage6_access_inventory.json")


def fare_requests(start_year=2010, end_year=2025, end_quarter=2):
    """Yield deterministic DB1B Market and Ticket archive identities."""
    if not all(isinstance(value, int) and not isinstance(value, bool)
               for value in (start_year, end_year, end_quarter)):
        raise ValueError("DB1B range values must be integers")
    if start_year < DB1B_FIRST_YEAR:
        raise ValueError(f"DB1B history starts in {DB1B_FIRST_YEAR}")
    if end_quarter not in range(1, 5):
        raise ValueError("end_quarter must be between 1 and 4")
    if (end_year, end_quarter) > DB1B_LAST_PERIOD:
        raise ValueError("DB1B inventory is bounded at 2025 Q2")
    if (start_year, 1) > (end_year, end_quarter):
        raise ValueError("start period must not follow end period")

    for year in range(start_year, end_year + 1):
        final_quarter = end_quarter if year == end_year else 4
        for quarter in range(1, final_quarter + 1):
            for table in ("DB1BMarket", "DB1BTicket"):
                filename = (
                    f"Origin_and_Destination_Survey_{table}_{year}_{quarter}.zip"
                )
                yield {
                    "kind": "fare",
                    "table": table,
                    "year": year,
                    "quarter": quarter,
                    "url": f"{PREZIP}/{filename}",
                }


def ontime_request(year, month):
    """Return an unverified PREZIP recipe probe for one reporting month."""
    if not all(isinstance(value, int) and not isinstance(value, bool)
               for value in (year, month)):
        raise ValueError("on-time period values must be integers")
    if year < 1987:
        raise ValueError("reporting-carrier history starts in 1987")
    if month not in range(1, 13):
        raise ValueError("month must be between 1 and 12")
    filename = f"{ONTIME_FILENAME_TABLE}_{year}_{month}.zip"
    return {
        "kind": "operations",
        "table": ONTIME_TABLE,
        "year": year,
        "month": month,
        "url": f"{PREZIP}/{filename}",
        "recipe_probe": True,
    }


def default_requests():
    """Return the authorized 124 fare identities and two operations probes."""
    return [
        *fare_requests(),
        ontime_request(2010, 1),
        ontime_request(2024, 1),
    ]


def _utc_timestamp(now):
    value = now()
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("inventory timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _selected_headers(headers):
    normalized = {str(key).lower(): value for key, value in headers.items()}
    raw_length = normalized.get("content-length")
    try:
        content_length = int(raw_length) if raw_length is not None else None
    except (TypeError, ValueError):
        content_length = None
    if content_length is not None and content_length < 0:
        content_length = None
    return {
        "content_length": content_length,
        "content_type": normalized.get("content-type"),
        "last_modified": normalized.get("last-modified"),
        "etag": normalized.get("etag"),
    }


def probe_inventory(request_records, *, transport=None, timeout=DEFAULT_TIMEOUT,
                    max_workers=2, now=None):
    """HEAD public URLs and return ordered, auditable access results.

    A successful result establishes endpoint access only. It does not validate ZIP
    contents, CSV schema, completeness, or data quality.
    """
    if isinstance(max_workers, bool) or max_workers not in (1, 2):
        raise ValueError("max_workers must be one or two")
    if (not isinstance(timeout, (tuple, list)) or len(timeout) != 2
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) or value <= 0 for value in timeout)):
        raise ValueError(
            "timeout must contain positive finite connect and read seconds"
        )

    records = [dict(record) for record in request_records]
    head = requests.head if transport is None else transport
    clock = (lambda: datetime.now(timezone.utc)) if now is None else now

    def probe(index_and_record):
        index, record = index_and_record
        timestamp = _utc_timestamp(clock)
        empty_headers = {
            "content_length": None,
            "content_type": None,
            "last_modified": None,
            "etag": None,
        }
        try:
            response = head(
                record["url"], allow_redirects=True, timeout=tuple(timeout)
            )
            try:
                status = int(response.status_code)
                headers = _selected_headers(response.headers)
                return {
                    "request_index": index,
                    "requested_at_utc": timestamp,
                    "status": status,
                    "final_url": getattr(response, "url", record["url"]),
                    "headers": headers,
                    "error": None,
                    "success": 200 <= status < 300,
                }
            finally:
                close = getattr(response, "close", None)
                if callable(close):
                    close()
        except Exception as exc:  # each inaccessible identity remains in inventory
            return {
                "request_index": index,
                "requested_at_utc": timestamp,
                "status": None,
                "final_url": None,
                "headers": empty_headers,
                "error": f"{type(exc).__name__}: {exc}",
                "success": False,
            }

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(probe, enumerate(records)))

    success_count = sum(result["success"] for result in results)
    advertised_bytes = sum(
        result["headers"]["content_length"] or 0
        for result in results
        if result["success"]
    )
    return {
        "generated_at_utc": _utc_timestamp(clock),
        "method": "HEAD",
        "schema_verified": False,
        "requests": records,
        "results": results,
        "summary": {
            "request_count": len(records),
            "success_count": success_count,
            "failure_count": len(records) - success_count,
            "advertised_bytes_total": advertised_bytes,
        },
    }


def main(argv=None):
    """Run the bounded inventory only when the caller explicitly requests a write."""
    parser = argparse.ArgumentParser(
        description=(
            "Record BTS PREZIP HEAD access. HTTP success does not verify archive "
            "contents or schema."
        )
    )
    parser.add_argument(
        "--write", action="store_true",
        help="explicitly probe and create a new inventory JSON",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, choices=(1, 2), default=2)
    parser.add_argument("--connect-timeout", type=float, default=10.0)
    parser.add_argument("--read-timeout", type=float, default=30.0)
    args = parser.parse_args(argv)
    if not args.write:
        parser.error("--write is required; no inventory was changed")
    if args.output.exists():
        parser.error("inventory already exists; use a new versioned --output path")
    if (not math.isfinite(args.connect_timeout)
            or not math.isfinite(args.read_timeout)
            or args.connect_timeout <= 0 or args.read_timeout <= 0):
        parser.error("timeouts must be positive and finite")

    inventory = probe_inventory(
        default_requests(),
        timeout=(args.connect_timeout, args.read_timeout),
        max_workers=args.workers,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    free_bytes = shutil.disk_usage(args.output.parent).free
    inventory["summary"]["free_bytes_at_inventory"] = free_bytes
    inventory["summary"]["advertised_bytes_fit_free_disk"] = (
        inventory["summary"]["advertised_bytes_total"] <= free_bytes
    )
    # Exclusive creation also protects provenance if another writer races the probe.
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
