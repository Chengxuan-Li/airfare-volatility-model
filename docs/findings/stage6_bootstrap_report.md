# Stage 6 historical access and operations bootstrap

Date: 2026-09-12 America/New_York (acquisition timestamps are UTC).
The first four tasks of the [committed plan](../methods/stage6_execution_plan.md)
are complete. This establishes access and a reproducible reader; it does not
complete the historical panel or estimate new fare effects.

## What ran

All 124 DB1B Market/Ticket endpoints for 2010 Q1 through 2025 Q2 returned HTTP 200
to HEAD requests. Their advertised compressed total is 9,925,278,201 bytes, below
the 125,151,219,712 free bytes recorded at inventory time. These are access checks,
not 124 downloaded or schema-validated files. The initial
[inventory](../../data/manifests/stage6_access_inventory.json) also preserves two
HTTP 404 operations probes: putting parentheses around `1987_present` in the ZIP
filename was incorrect. The [separate correction](../../data/manifests/stage6_operations_access_correction.json)
records HTTP 200 for both official filenames without parentheses. The CSV members
inside those ZIPs do contain parentheses. Future inventories require a new output
path so neither failures nor earlier availability evidence can be overwritten.

Four archives were downloaded, ZIP/CRC checked and SHA-256 manifested, totaling
163,801,228 compressed bytes. Raw inputs remain local and ignored.

| Input | National rows checked | Audit result |
| --- | ---: | --- |
| Reporting on-time, January 2010 | 521,809 | 284 airports; 18 reporting carriers |
| Reporting on-time, January 2024 | 547,271 | 334 airports; 15 reporting carriers |
| DB1B Market, 2010 Q1 | 4,906,864 | Required columns and all row periods valid; no missing itinerary IDs |
| DB1B Ticket, 2010 Q1 | 2,835,075 | Required columns and all row periods valid; no missing itinerary IDs |

The fare audit reads every row's year, quarter and itinerary ID. It does not yet
validate fare distributions, join cardinality, product comparability or historical
coverage in the other 61 quarters. Saved Stage 5 fare estimates still cover only
2023 Q1-2025 Q2. No 2010 fare model has been fitted.

## Operations measurement

The reader validates flight dates, period fields, binary cancellation/diversion
flags and one flight per source row. It rejects duplicate flight keys, including
duplicates spanning chunks. Keys combine flight date, DOT reporting-carrier ID,
flight number, origin/destination airport IDs and scheduled departure time. Both
national inputs had zero duplicate keys and zero missing eligible arrival delays.

Cancellation and diversion rates divide by all reported flights. Delay rates
divide by flights with observed arrival delay that are neither cancelled nor
diverted. Thresholds are inclusive at 15 and 60 minutes; mean delay retains early
arrivals' negative values. Missing eligible delays are counted separately and an
empty delay denominator yields a missing rate. Cancellation/diversion overlap is
also counted rather than assumed impossible.

The compact route output retains all reporting carriers between ORD, DEN, DFW,
ATL, LAX, JFK and SEA, excluding identical origin/destination IDs. It contains 265
carrier-route-month cells and 33,648 flights. A separate carrier-month output
retains national totals across all routes.

| Seven-airport subset | Flights | Cancelled | Diverted | Observed eligible delay | Delay >=15 min | Delay >=60 min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| January 2010 | 17,059 | 283 | 36 | 16,740 | 2,511 | 608 |
| January 2024 | 16,589 | 676 | 26 | 15,887 | 3,761 | 1,370 |

These two winter months were declared before inspecting outcomes. They test the
reader, not trends or causal differences. Reporting coverage and carrier roles
change over time; on-time reporting carriers cannot be silently equated with DB1B
reporting, ticketing or operating carriers. The
[BTS field definitions](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)
are the primary reference for these outcomes and identifiers.

## Verification and provenance

The pinned requirements were freshly installed in an ignored Python 3.13.9
environment. The full offline suite passes **71 tests**, with one expected
rank-deficiency warning from the existing Stage 5 reference test. Two full raw
bootstrap builds produced four byte-identical derived files. Checksums, source
hashes, environment and scope are in the
[verification record](../../outputs/stage6/bootstrap_verification.json).
The final inventory-only provenance fix does not change bootstrap recipes or
aggregations; its regression reproduced the overwrite before the fix.

Independent review checked acquisition provenance, input verification, operations
denominators, identities and duplicate detection. Shared acquisition now preserves
existing manifests on matching reacquisition and quarantines changed responses.
The original runner verifies its own 25 inputs, unaffected by unrelated Stage 5/6
manifests. These fixes have regression coverage; a fresh full original-pilot raw
rebuild is not claimed. Historical Stage 0-5 outputs were not modified.

The [execution ledger](../status/execution_ledger.md) records 128 coordinator HEAD
requests and four raw GET downloads, including the recipe failures. It also records
an unintended worker-test transport incident: 252 `requests.head` invocations with
invalid timeouts returned client exceptions and no HTTP status. No successful
response or additional acquisition was recorded; the temporary diagnostic files
were not retained. Finite-timeout validation and a suite-wide HTTP block now guard
offline tests. No Flightradar24 API calls or credits were used.

## Reproduce and next work

From the repository root, use the pinned environment. The first command acquires
only the four declared bootstrap inputs when absent and verifies cached inputs.

```powershell
.\.venv\Scripts\python.exe -m src.stage6.bootstrap --acquire
.\.venv\Scripts\python.exe -m src.stage6.bootstrap
.\.venv\Scripts\python.exe -m pytest -q
```

To make a new access inventory, choose a new versioned filename; the command
refuses an existing destination before any probes:

```powershell
.\.venv\Scripts\python.exe -m src.stage6.inventory --write --output data/manifests/stage6_access_inventory_followup_01.json
```

Next, declare the expanded airport universe using preperiod coverage/traffic,
audit stable airport and carrier identities, and acquire historical fares and
monthly operations in bounded year batches. Inventory access makes 2010-2025 Q2
feasible to investigate; it does not establish comparability across that horizon.
DB1B's earlier history and the DB1C sampling transition remain separate scope
decisions. Add compatible capacity and forecast-vintage risk measures before
declaring expanded models and temporal holdouts.

Departure/supply-channel models and CR2/bootstrap inference from the broader
Stage 5 identification note remain explicitly deferred. No new inference method
has been executed here. FR24 remains supplemental, subject to verified access,
cost and balance; a missing track alone cannot establish cancellation. More
quarterly fares cannot recover the original missing quote-time information.
