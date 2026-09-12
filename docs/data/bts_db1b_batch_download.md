# BTS DB1B batch-download verification

Date: 2026-09-12. This is a pre-execution access check, not a Stage 3 pilot or
empirical finding. No API key, account, or paid service is needed for these files.

## Selected source and meaning

The [user-selected database](https://www.transtats.bts.gov/tables.asp?QO_VQ=EFI&QO_anzr=Nv4yv0r)
is Airline Origin and Destination Survey (DB1B). BTS describes it as a quarterly
10% sample of tickets from reporting carriers. The
[database profile](https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFI&Yv0x=D)
lists coverage beginning in 1993. The
[Market download page](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=b4vtv0+n0q+Qr56v0n6v10+f748rB&gnoyr_VQ=FHK)
displayed June 2025 as its latest data when checked. Do not assume all four
quarters exist merely because the year and quarter dropdowns permit selection.

Table roles:

- Market: directional market fare, passenger counts, origin/destination, carriers.
- Ticket: itinerary fare and itinerary characteristics; useful for quality filters.
- Coupon: individual itinerary segments; acquire only if the design needs them.

DB1B cannot supply quote timestamps, booking dates, days to departure, or exact
flight departures for matching to forecast vintages. Passenger counts represent
observed traffic, an equilibrium quantity; they are not automatically exogenous
demand. Market fare is prorated, not necessarily a separately quoted route fare.
Define an aggregate route/carrier/quarter design separately from the original
flight/quote hypothesis. Do not infer flight-level risk effects from it.

## Direct batch endpoint

The official server serves one pre-zipped archive per table/year/quarter:

```text
https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1B{Table}_{Year}_{Quarter}.zip
```

`Table` is `Market`, `Ticket`, or `Coupon`; quarter is the integer 1-4.
This avoids repeated manual form submission. ZIPs include CSV and `readme.html`.
The embedded BTS readme confirms that the filename encodes year and quarter.

Verified endpoint checks for 2024 Q1:

| Table | HTTP status | Compressed bytes | Verification |
| --- | --- | ---: | --- |
| Market | 200 | 95,062,966 | Full GET, full ZIP CRC, header and first row |
| Ticket | 200 | 91,373,415 | HEAD only; contents not downloaded |
| Coupon | 200 | 223,500,145 | HEAD only; contents not downloaded |

Market 2024 Q2 also passed full GET, ZIP CRC, header, and first-row checks:
109,963,653 compressed bytes and a 2,155,345,248-byte CSV. The two ZIPs total
205,026,619 bytes. Full-download results are in the accompanying manifests.
The documented Python recipe was subsequently executed against both cached
archives: checksums matched and both full ZIP CRC checks passed without network
downloads. The curl fallback was tested on Q2 (HTTP 200; 66.87 seconds).

## Reproduction recipe

From the repository root, run the following in Python 3.11+ (standard library
only). On PowerShell, paste it between `@'` and `'@ | python -` on separate lines.
This reproduces the two-quarter Market access check. Adjust the explicit worklist
only after selecting the research period and checking storage requirements.

```python
import csv
import datetime
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

root = Path.cwd()
raw = root / "data/raw/bts_db1b"
manifests = root / "data/manifests"
raw.mkdir(parents=True, exist_ok=True)
manifests.mkdir(parents=True, exist_ok=True)
worklist = [("Market", 2024, 1), ("Market", 2024, 2)]

for table, year, quarter in worklist:
    name = f"Origin_and_Destination_Survey_DB1B{table}_{year}_{quarter}.zip"
    url = "https://transtats.bts.gov/PREZIP/" + name
    target = raw / name
    manifest_path = manifests / f"bts_db1b_{table.lower()}_{year}_q{quarter}.json"
    existing = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    headers = {}
    fetched_at = None
    if not target.exists():
        partial = target.with_suffix(".zip.part")
        with urllib.request.urlopen(url, timeout=60) as response, partial.open("wb") as out:
            headers = {k: response.headers.get(k) for k in
                       ("Content-Type", "Content-Length", "Last-Modified", "ETag")}
            while block := response.read(1024 * 1024):
                out.write(block)
        fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Reject truncated or non-ZIP responses before assigning the final name.
        with zipfile.ZipFile(partial) as archive:
            assert archive.testzip() is None, "ZIP CRC failure"
        partial.rename(target)
    with target.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    if existing and fetched_at is None:
        assert digest == existing["sha256"], "Cached file checksum mismatch"
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None, "ZIP CRC failure"
        members = [{"name": z.filename, "uncompressed_bytes": z.file_size}
                   for z in archive.infolist()]
        csv_name = next(z.filename for z in archive.infolist()
                        if z.filename.lower().endswith(".csv"))
        with archive.open(csv_name) as source:
            reader = csv.reader(io.TextIOWrapper(source, encoding="utf-8-sig"))
            columns, first_row = next(reader), next(reader)
        assert len(first_row) == len(columns), "Header/row mismatch"
    if fetched_at is not None or existing is None:
        record = dict(source=f"BTS TranStats DB1B{table}", url=url,
                      retrieved_at_utc=fetched_at, year=year, quarter=quarter,
                      local_path=target.relative_to(root).as_posix(),
                      bytes=target.stat().st_size, sha256=digest, headers=headers,
                      zip_crc_valid=True, members=members, columns=columns,
                      first_row_column_count=len(first_row),
                      transformations="None; original ZIP retained.",
                      license_notes="Public BTS download; raw archive excluded from Git.")
        manifest_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(name, target.stat().st_size, digest)
```

The loop is sequential and skips repeat downloads of existing archives, while
rechecking integrity. HTTP errors stop the batch. Investigate missing periods or
access errors; do not retry indefinitely. A failed request can leave a `.part`
file; the next attempt overwrites that partial download only. A cached archive
with no earlier manifest has an unknown original retrieval date, recorded as null.

### Bounded transfer fallback

During this check, the Q2 Python transfer made slow progress despite a successful
HEAD and HTTP 206 byte-range probe. It was interrupted, and a separate curl
transfer was used. The cause of the throughput difference was not established.
Python's socket timeout is not a total download deadline. For bounded transfers,
use curl with both a total deadline and a low-speed cutoff, for example:

```powershell
curl.exe --fail --silent --show-error --connect-timeout 20 --max-time 120 --speed-time 20 --speed-limit 1024 --output data/raw/bts_db1b/Origin_and_Destination_Survey_DB1BMarket_2024_2.curl.part https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BMarket_2024_2.zip
if ($LASTEXITCODE -ne 0) { throw 'Transfer failed; preserve partial file for diagnosis' }
```

Validate the ZIP CRC before renaming a successful partial file to its final name,
then run the recipe above to verify cached content. Record the actual retrieval
time in the manifest; never assign a later cache-verification time as retrieval.
For other periods the deadline may need adjustment based on file size and measured
throughput. Keep a finite deadline and retry policy.

## Scale and validation considerations

- Q1 Market CSV is 1,868,609,242 bytes uncompressed. Stream from the ZIP or use
  chunked CSV processing and keep only selected columns/routes. Do not load all
  quarterly files into memory simultaneously or commit the raw archives.
- The checked CSV header has 41 named fields plus an empty trailing field, and
  the first row has 42 fields. Handle the empty field explicitly during cleaning.
- Select Market first; add Ticket/Coupon only when needed, with audited joins
  scoped by year/quarter and IDs. Do not assume IDs are globally unique.
- Full CRC checks establish archive integrity, not row-level data quality.
  Full period checks, row counts, duplicate audits, fare filters, and passenger
  weighting are later acquisition/cleaning requirements.
- Reconcile data-vintage coverage before expanding beyond June 2025; this access
  check does not establish whether a successor survey must be used or harmonized.
- Preserve manifests, checksums, download dates, and source documentation.
  No Flightradar24 calls were made for these checks.

## Verification artifacts

- [2024 Q1 Market manifest](../../data/manifests/bts_db1b_market_2024_q1.json)
- [2024 Q2 Market manifest](../../data/manifests/bts_db1b_market_2024_q2.json)

Raw ZIPs remain in ignored `data/raw/bts_db1b/`. These two periods verify access;
they are not the final research sample.
