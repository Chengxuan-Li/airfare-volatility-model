# Historical fare and operations panel: 2010 Q1-2025 Q2

Execution started 2026-09-13 under the [continuous plan](../methods/stage6_full_history_plan.md).
This is a living report; completion is recorded only after all declared years
are built, verified and published.

## Scope and interpretation

The target consists of 62 DB1B fare quarters (124 Market/Ticket archives) and 186
reporting on-time months, ending June 2025. The airport sample remains the thirty
stable IDs selected using 2010 Q1 passenger volume. The same primary/broad fare
filters, passenger-weighted moments, support flags and flight-outcome denominators
apply to every year. Carrier populations are aggregated separately by source.
No new fare model, forecast-risk calibration or causal estimate is added.

Missing coverage stays missing. Retained/entered/exited in continuity tables means
observed source presence, not physical service opening/closure or cancellation.
Numeric reporting codes and stable DOT IDs remain distinct. Airport aliases and
carrier reporting populations are audited each year against the frozen baseline.
For 2025, baseline comparisons are restricted to Q1-Q2 and January-June; later
unrequested periods cannot establish exits. Full-year and half-year totals should
not be compared without matching periods.

The 2020-2021 pandemic and 2022-onward recovery labels in coverage summaries are
descriptive periods. They are not instruments, causal controls or an estimated
regime model. Quarterly nominal prorated fares remain distinct from timestamped
quotes; observed passenger traffic remains jointly determined with prices.

## Acquisition and progress

All 270 remaining endpoints passed HEAD checks, advertising 13,165,882,016 bytes;
121,456,566,272 bytes were free before acquisition. See the
[access summary](../../data/manifests/stage6_full_history_access_summary.json),
per-year access inventories and [execution ledger](../status/execution_ledger.md).
The 2010/2011 panels were already published. Remaining year batches are in progress.
HEAD access does not establish schema or complete data validity.

<!-- YEAR_PROGRESS_START -->
| Verified year | Fare quarters | National reported flights | Scoped flights | Primary fare cells | Matched | Passenger-weight match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2010 | 4 | 6,450,117 | 2,100,986 | 3,191 | 2,904 | 99.8458% |
| 2011 | 4 | 6,085,281 | 2,110,718 | 3,198 | 2,865 | 99.8203% |
<!-- YEAR_PROGRESS_END -->

The coordinator alone downloads in bounded pairs and verifies caches, request
identities, checksums and ZIP CRCs. Existing manifests are preserved, including
two legacy 2024 fare manifests with top-level year/quarter fields. No paid
services, FR24 calls or credits are used. Raw files and environment remain ignored.

## Reproduction contract

Each new year is built twice from raw. Its `verification.json` records all derived
hashes, consumed raw hashes, frozen baseline artifact hashes, implementation/source
identity, Python/requirements pins and test evidence. Failed attempts are preserved
in per-year build-attempt manifests. Old output sets remain ignored backups.

From the repository root with the pinned environment:

```powershell
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2012 --acquire
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2012
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2025
.\.venv\Scripts\python.exe -m pytest -q
```

Use each declared year in the annual command. `--year 2025` automatically requests
only Q1-Q2/January-June, not a full year. The published frozen 2010 artifacts and
manifest are required; later years do not rescan or rerank 2010 raw data.
Per-year files remain the canonical panels; compact horizon summaries will verify
all annual artifacts before publication. A rebuild moves an old verification record
to the backup rather than attaching it to newly unverified outputs.

## Remaining research

Completing this data horizon does not complete capacity expansion, aligned
forecast/quote collection, departure/supply modeling or new econometric estimates.
Those require separate measurement and identification decisions. The original
quote-time hypotheses remain unidentifiable from quarterly purchases alone.
