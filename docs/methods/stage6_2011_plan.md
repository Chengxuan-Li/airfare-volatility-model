# Stage 6 audited 2011 extension

Authorized 2026-09-13 by the user's "next" after the verified 2010 milestone.
Spec: [2010 design](stage6_2010_plan.md) and [broader direction](stage6_execution_plan.md).
Goal: extend one year using the frozen 2010 airport sample and expose changes in
source coverage before scaling later years. No models or causal tests are added.

## Fixed design and scope

- Keep all thirty selected 2010 airport IDs. Do not rerank using 2011 outcomes or
  volumes and do not require future survival. Pin the published 2010 ranking and
  verification record by SHA-256 in a new tracked frozen-sample manifest before
  acquisition. Validate baseline artifacts before use, including continuity inputs.
- Keep 2010 fare filters, moments, low-support flags, reporting-carrier separation,
  quarterly count-first operations rates and outer route-quarter join unchanged.
  2011 is a subsequent-year data validation, not a fitted-model holdout.
- Acquire exactly eight 2011 DB1B Market/Ticket archives and twelve 2011 reporting
  on-time months. Probe the twenty intended endpoints and record status/size,
  compare disk budget, use two bounded transfers at a time and preserve failures.
  All acquisition belongs to the coordinator. No paid services or FR24 calls.
- Preserve old annual/bootstrap outputs. New outputs live in
  `outputs/stage6/annual_2011/`; previous result directories remain ignored backups.
  Default annual CLI behavior for 2010 stays compatible. Initially accept only
  the two declared years (2010, 2011), so a complete-year request cannot reach
  DB1B's incomplete 2025 or silently authorize unreviewed later batches.
- Audit airport ID/code relationships across both years and source-specific
  carrier presence. Numeric-looking carrier codes remain strings. A reused code
  or different DOT ID is evidence to review, not proof of a merger or equivalence.
- Compare route presence at equal calendar quarters on stable endpoint IDs,
  separately for primary and broad fare samples and operations coverage. Keep
  observed entry/exit and missing coverage; do not label absence a cancellation.

## Task 1: frozen baseline and bounded year parameter

Files: `src/stage6/baseline.py`, `src/stage6/annual.py`,
`tests/test_stage6_baseline.py`, `tests/test_stage6_annual.py`,
`data/manifests/stage6_frozen_sample_2010.json`.
Interfaces:
```python
input_records(year=2010)  # exactly twenty identities; reject undeclared years
validate_months(audits, year=2010)
load_baseline()  # pinned ranking, 2010 selection audit, verified baseline tables
```
- [x] Write regressions for full 2011 identities, wrong-year months, modified
  baseline/ranking, frozen IDs and 2010 compatibility; run red before changes.
- [x] Parameterize year-specific paths, access inventory, acquisition ledger,
  period checks, labels and output directory. For 2011 load the frozen ranking;
  never call selection on 2011 data. Verify baseline before network/build work.
- [x] Run focused/full tests and independent code/spec review; commit.

## Task 2: independent continuity diagnostics

Files: `src/stage6/continuity.py`, `tests/test_stage6_continuity.py`.
Interface:
```python
compare_years(baseline_tables, current_tables)
# Both dictionaries use CSV filenames -> DataFrames, with the seven annual CSVs.
# Returns (extra_tables, audit). extra_tables uses CSV filenames -> DataFrames.
```
- [x] Test observed airport/carrier/route entry and exit, mutable codes versus
  stable IDs, source separation, and unchanged quarterly matching/denominators.
  Real small DataFrames only; no worker HTTP or actual raw build.
- [x] Emit `airport_continuity.csv`, `carrier_continuity.csv`,
  `route_continuity.csv`, plus a JSON-compatible summary. Airport rows cover every
  selected ID, including absence. Carrier rows distinguish fare reporting codes
  from operations DOT-ID/code observations. Route rows match equal quarter and
  stable IDs per fare sample; report fare presence and operations presence for
  both years without filling absent outcomes with zeros.
- [x] Verify no changes to input frames or fare/operations aggregation, test and
  review independently. Root integrates diagnostics into the 2011 annual output.

## Task 3: acquisition, real builds and publication

Commands:
```powershell
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2011 --acquire
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2011
```
- [x] Inventory twenty endpoints, acquire/verify twenty inputs and preserve
  immutable request metadata with failure/cache outcomes and disk budget.
- [x] Rebuild the 2011 outputs twice from raw; compare every derived file byte.
  Save twenty raw hashes plus frozen/baseline artifact hashes, source hashes and
  environment/test evidence. The reused baseline is an explicit additional input.
- [x] Review source coverage, partial months, low-support cells, carrier changes,
  ID/code aliases and every unmatched category. Keep descriptive comparisons
  separate from weather-risk, capacity and price-effect claims.
- [x] Final independent code/report review, full offline tests, source/output
  hashes and unchanged older outputs. Update report/index/state/ledger and inspect
  public staged contents.
- [x] Commit and push the verified 2011 milestone, then record publication.

Execution uses the current clean checkout on `codex/stage-6-2011-panel` with ignored
caches retained. At most two bounded workers; coordinator integrates and owns Git.
The writing-plans and subagent-driven-development workflows apply with the user's
standing execution authorization. Reproduction evidence stays in Git-controlled
documentation. Full 2012-2025 Q2 acquisition and any fitted models remain later work.
