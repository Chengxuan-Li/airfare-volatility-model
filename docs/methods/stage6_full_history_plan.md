# Complete the declared 2010-2025 Q2 history

Authorized 2026-09-13: the user instructed continuous execution through all
remaining years without waiting for another command. This extends the reviewed
[2011 workflow](stage6_2011_plan.md), preserving its measurement and frozen sample.
The coordinator owns acquisition and Git; at most two independent workers.
Use executing-plans/subagent-driven-development with the standing authorization.
Work on `codex/stage-6-full-history` in the clean checkout to retain verified caches.

## Fixed scope and design

- Complete 2012-2024 (four fare quarters/twelve operations months each), then
  2025 Q1-Q2/January-June. These 270 input identities complete the 310-input
  2010 Q1-2025 Q2 horizon (124 fare and 186 monthly operations archives).
- Preserve 2010/2011 outputs, all earlier results and the thirty frozen 2010 IDs.
  No reranking, carrier crosswalk, survival restriction, new fare estimates,
  forecast-risk claims or FR24 spending. Retain source failures and missingness.
- Extend the existing annual runner rather than creating a separate measurement
  pipeline. A single declared-period helper fixes the horizon by year; reject
  years outside 2010-2025. 2025 cannot silently request Q3/Q4 or July-December.
- For 2025 continuity, compare only baseline Q1-Q2/January-June; preserve the
  original baseline ranking and selection audit. Explicitly label partial-year
  output and expected/observed periods. Never infer an exit from unrequested months.
- Probe each intended batch with at most two concurrent HEADs, save metadata,
  verify advertised bytes against disk, then acquire in bounded GET pairs.
  Reuse only verified caches; preserve existing provenance. An acquisition
  failure stops that pair/batch and is diagnosed before a bounded resume.
  A transient transport failure may receive one recorded retry with original
  partial bytes preserved under a versioned ignored path. A changed source hash
  needs explicit source-revision evidence and a versioned recipe, never replacement.
- Run each new period twice from raw and compare every derived file byte. Record
  raw/baseline/source/output hashes and environment evidence in per-year verification.
  If schema/quality problems emerge, diagnose, regression-test, document and resume.
- Publish compact per-year aggregates, annual/quarterly coverage summaries and
  source-specific carrier presence. Keep pandemic (2020-2021) and subsequent
  recovery (2022 onward) labels as descriptive periods, not causal controls.
  The partial 2025 annual total is not comparable to full-year totals.

## Task 1 — Declared periods and partial-year runner

Files: `src/stage6/periods.py`, `src/stage6/annual.py`, relevant tests.

- [x] Test 20 identities for each complete year, ten for 2025, 310 for the whole
  horizon; reject out-of-range/noninteger years and unexpected months.
- [x] Test baseline restriction to matching 2025 quarters/months, aliases and
  national reporting identities; preserve source strings and frozen selection.
- [x] Implement shared period selection, exact source completeness, partial-year
  labels and baseline-period restriction. Keep 2010/2011 behavior compatible.
- [x] Run offline regressions and independent code/spec review; commit.

## Task 2 — Full-horizon coverage summaries

Files: `src/stage6/history.py`, `tests/test_stage6_history.py`.

- [x] Test small real DataFrames for primary/broad coverage, passenger-weighted
  matching, partial months, carrier source separation, missing outcomes and 2025
  partial-year labels. No HTTP or full raw worker builds.
- [x] Build deterministic annual and quarterly summary CSVs, source-specific
  carrier presence and a horizon quality/verification audit from per-year outputs.
  Require all declared periods and verified per-year files before final publication.
  No duplicated operations counts across fare samples. Do not sum nominal fares
  or label traffic exogenous demand. Reconcile full-horizon counts to annual outputs.
- [x] Test, independently review and integrate. Keep per-year panels the canonical
  data; do not duplicate large joined CSVs just to create a single file.

## Task 3 — Continuous coordinator execution

- [ ] Inventory and acquire 2012-2025 Q2 in audited batches. Keep exact ledgers,
  cache outcomes, failure evidence and disk checks; no workers make live requests.
- [ ] Build each remaining year twice, verify input/output hashes, source coverage,
  schema/key checks, support and identities. Commit/push verified year milestones.
- [ ] Verify all 310 consumed identities across 62 fare quarters and 186 operations
  months, retaining source revisions/failures rather than claiming missing data ran.
- [ ] Build full-horizon summaries twice and reconcile them against verified annual
  outputs. Preserve old outputs; run relevant/full offline tests and independent
  final artifact review. Update report/index/state/ledger and inspect public files.
- [ ] Push final results and record actual publication and remaining research scope.

Completion means the entire declared descriptive data horizon is built and audited.
Capacity expansion, quote/forecast-vintage data and new econometric models remain
separate research work; no stage-completion claim should imply those ran.
