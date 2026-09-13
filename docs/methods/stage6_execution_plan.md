# Stage 6 historical coverage and operations implementation plan

**Authorized:** 2026-09-12, user instruction to commit the proposed plan and start.
**Goal:** establish reliable historical acquisition and flight-level operational
measurement before expanding the descriptive fare panel to 2010-2025 Q2.
**Spec:** [approved direction](next_research_direction.md).
**Architecture:** retain Stage 0-5 outputs. Shared acquisition must preserve existing
provenance; each pipeline verifies its own consumed inputs. New Stage 6 modules
produce an access inventory and auditable operations aggregates before new fare
models are declared or estimated.
**Stack:** existing Python/pandas/NumPy/pytest, curl, public BTS endpoints.
**Execution:** test-first fixes and bounded parallel workers; coordinator owns all
acquisition, integration and commits. Work in the clean current checkout on
`codex/stage-6-operations` so cached inputs remain available to subsequent steps.

## Constraints and scientific scope

- No paid services or upgrades. No authenticated FR24 calls before verified plan
  access, balance, costs and retention rules; ceiling remains 6,000 credits.
- DB1B 2010 Q1-2025 Q2 comprises 62 quarters / 124 Market-Ticket archives.
  This is a target horizon, not a statement that every archive is available.
- Prefer a substantial modern history over pooling all years since 1993 without
  comparability audits. Keep pandemic/recovery regimes separate; DB1C is a separate
  monthly/sampling-regime extension, not part of the initial pooled panel.
- Preserve missingness, negative results, failures and exact source identities.
  Only the coordinator runs live requests, with at most two downloads concurrently.
- No new fare-effect claims from the acquisition/operations bootstrap. Risk at a
  forecast timestamp and realized operational outcomes remain separate objects.
- Historical outputs are immutable during this milestone. Raw files remain ignored.

## Task 1 — Protect recorded provenance on reacquisition

Files: `src/acquisition/download.py`, `tests/test_download.py`.
Keep `fetch(url, target, manifest_path, *, source='BTS', params=None)` compatible.

- [x] Add regression cases with temporary real files and an external-transfer fake:
  changed valid payload plus existing manifest must raise and preserve manifest
  bytes; matching payload must preserve original retrieval metadata; changed
  request identity must reject even if target is missing. Legacy DB1B manifests
  encode year/quarter at top level and must remain usable.
- [x] Run the new tests against the old implementation and record intended failures.
- [x] Before promoting `.part`, validate format, checksum and request identity
  against any existing manifest. On mismatch preserve original manifest and leave
  the candidate quarantined as `.part`. Never overwrite an existing valid target.
- [x] Verify cache hits and T100's prevalidated local POST registration still work.
  A source revision requires a new explicitly versioned target/manifest; no silent
  refresh flag is introduced in this milestone.
- [x] Run `python -m pytest tests/test_download.py tests/test_pipeline.py -q`.

## Task 2 — Verify only the original pipeline's actual inputs

Files: `src/acquisition/verify.py`, `src/run.py`, `tests/test_input_verification.py`.
Introduce `verify_pilot_inputs()` with explicit 16 fare, seven weather, registry
and delay-archive identities. Verify expected paths and hashes rather than trusting
arbitrary manifest paths. Keep full and analysis-only modes' raw-check requirement.

- [x] Fixture a complete small original input set plus an unrelated missing Stage 5
  manifest; original verification must pass. Deleting a required manifest/input,
  changing its path or content must fail before analysis.
- [x] Run failing tests, implement the verifier, replace the directory-wide loop.
- [x] Run the full suite and inspect unchanged historical outputs. Commit Tasks 1-2
  as the first code milestone after an independent review.

## Task 3 — Inventory historical availability before bulk acquisition

Files: `src/stage6/inventory.py`, `tests/test_stage6_inventory.py`,
`data/manifests/stage6_access_inventory.json`.
Interface: deterministic `fare_requests(start_year=2010, end_year=2025,
end_quarter=2)` yields Market/Ticket identities; CLI records bounded HEAD results.

- [ ] Test 124 unique URLs, inclusive boundary periods, and rejection of invalid
  ranges. Test response/error capture with controlled external transport.
- [ ] Probe all intended fare archives with finite per-request timeouts, two
  concurrent requests maximum, zero automatic retry. Save status, timestamp,
  content length/type, last-modified/ETag when present, and exceptions. HEAD success
  verifies endpoint access, not CSV schema or data quality.
- [ ] Probe reporting-carrier on-time archives for January 2010 and January 2024
  using the documented PREZIP naming recipe. Preserve unavailable paths as failures.
- [ ] Compare total advertised download bytes against free disk space before batches.
  Full historical download is a later batch after bootstrap schema checks pass.

## Task 4 — Acquire and validate the operations bootstrap

Files: `src/stage6/operations.py`, `tests/test_stage6_operations.py`,
`outputs/stage6/operations_bootstrap_*`, associated raw manifests.
Bootstrap months January 2010 and January 2024 are chosen before seeing outcomes,
to test schema continuity and a winter month at two horizon points.

- [ ] Download/CRC/hash the two available official on-time archives and DB1B
  Market/Ticket 2010 Q1 as the historical fare-schema bootstrap. Inspect actual
  members/headers before fixing the reader's mapping; never guess column aliases.
- [ ] Define tested operations aggregates with flight counts, cancellations,
  diversions, valid noncancelled/nondiverted arrival-delay observations, counts
  delayed >=15 and >=60 minutes, missing eligible delay counts, and delay sums.
  Cancellation/diversion rates use all reported flights; delay rates use valid
  eligible observations. Flags and dates must validate; duplicate flight keys must
  be audited and never silently dropped. No synthetic historical data.
- [ ] Stream national rows; initial compact outputs retain the original seven
  airports for compatibility and a national coverage summary. This is a reader
  bootstrap, not the full geographic expansion. Preserve all eligible reporting
  carriers in operations data and do not equate them to DB1B carrier roles.
- [ ] Rebuild the compact bootstrap twice; compare outputs and inspect audits.
  Document downloads, schema findings, data exclusions and next batch commands.

## Subsequent research milestones

After the bootstrap, expand in audited year batches. Select a larger airport set
from preperiod coverage and traffic (not fare-effect signs), use stable airport
IDs and carrier history, and retain entry/exit rather than manufacturing balance.
Add T100 capacity, independent operations and historical/forecast-vintage risk at
compatible time resolutions. Declare temporal splits and risk calibration metrics
before fitting. Declare departure/supply outcome models and the applicable
CR2/bootstrap sensitivity implementation before expanded fare estimation. These
were broader proposals in the Stage 5 identification note, not completed analyses.

FR24 remains a supplemental acquisition decision after BTS coverage is known. An
absent track cannot alone imply cancellation, and takeoff is not gate departure.
Prospective quote collection requires a separate feasible data-access design;
more quarterly history cannot recover missing quote-time information.

## Verification and completion accounting

- [ ] Tests pass with the actual environment recorded; distinguish available-system
  verification from a fresh install of the pinned environment.
- [ ] Record attempted/failed endpoints and consumed input checksums. Inspect all
  output/model claims; bootstrap completion is not full Stage 6 completion.
- [ ] Update project state, index and execution ledger at each milestone. Inspect
  staged files, commit conventional milestones and push safely. Preserve clean
  historical outputs and report outstanding work without claiming it ran.
