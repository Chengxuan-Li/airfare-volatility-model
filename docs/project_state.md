# Project state

## Current stage

The declared 2010 Q1-2025 Q2 descriptive fare/operations history is complete and
verified on `codex/stage-6-full-history`. The user authorized continuous completion
of all remaining years without further commands. See the
[full-history report](findings/stage6_full_history_report.md) and
[completed plan](methods/stage6_full_history_plan.md).

<!-- HISTORY_PROGRESS_START -->
Verified years: 2010-2024 in full; 2025 Q1-Q2/January-June only. Every year has
two successful byte-identical raw builds. No declared year or source period remains
outstanding. Final remote publication is verified and recorded below.
<!-- HISTORY_PROGRESS_END -->

All 310 source archives pass exact request, SHA-256 and ZIP CRC checks: 124 DB1B
Market/Ticket files for 62 quarters and 186 monthly operations archives, totaling
14,782,676,474 compressed bytes. The sample retains the thirty
airport IDs selected using 2010 Q1 volume; later years never rerank or condition
on survival. 2025 continuity uses matching Q1-Q2/January-June baseline periods.

The inputs contain 387,251,539 Market rows, 232,355,006 Ticket rows and 97,347,555
operations rows. After audited equivalent-repeat and ambiguity exclusions, operations
retain 97,347,548 national analysis units and 33,159,834 scoped units. Primary fare
coverage contains 49,236 fare route-quarters, of which 45,798
match operations (99.9108% of sampled passenger weights). Missing coverage,
partial months, missing eligible outcomes, aliases and reporting populations
remain explicit. Fare codes and operations DOT IDs are aggregated separately.

## Verification and source exceptions

The [horizon proof](../outputs/stage6/history/verification.json) links sixteen annual
verification files. Two summary builds reproduce all four derived files exactly;
annual/quarterly counts reconcile. The final offline suite passes 251 tests,
with one known Stage 5 rank-deficiency warning. All 62 earlier output files remain
unchanged against `db0cd7b`. The [consumed-input manifest](../data/manifests/stage6_full_history_consumed_inputs.json)
records final raw checks and per-year source row/retained-flight totals.

Failed raw attempts remain in build-attempt ledgers. A unique missing scheduled
departure or flight number can be retained without imputation only when the other
field is observed and its remaining flight key is unique across the complete month;
potentially overlapping incomplete keys still fail. Repeated complete keys count once only if
all consumed identity/outcome fields agree, including missingness; raw metadata
variants remain preserved. All rows of conflicting complete keys are quarantined
with explicit counts and variants; ambiguous incomplete keys and invalid values
still fail. Outcome rates are conditional on retained unambiguous records. Exact exception counts appear in the report and input manifest.

## Earlier research and interpretation

Stage 0-4 and Stage 5 outputs remain preserved. Their recommendation remains C:
interesting empirical observation, weak paper. The original quote-time H1/H2 and
flexibility premium remain unidentifiable from quarterly purchases and retrospectively
retrieved weather. Observed passenger traffic is jointly determined with fares.
No new historical fare models, causal effects or forecast-risk calibration ran.
Pandemic/recovery labels are descriptive; 2025 half-year totals require matching
periods before comparison with full years.

Historical details and results remain in the [Stage 0-4 report](findings/stage_0_to_4_report.md),
[Stage 5 report](findings/stage5_report.md), [bootstrap report](findings/stage6_bootstrap_report.md),
[2010 report](findings/stage6_2010_report.md), [2011 report](findings/stage6_2011_report.md),
and append-only [execution ledger](status/execution_ledger.md).

## Next research actions

1. Predeclare analysis of the expanded descriptive panel, including reporting
   population breaks, pandemic periods, product composition and common support.
2. Extend compatible route capacity and define departure/supply outcomes before
   estimating those channels; specify robust inference and sensitivity checks.
3. For the original mechanism, obtain aligned quote timestamps and forecast
   vintages or state explicit additional identifying assumptions. Quarterly
   transaction expansion alone does not identify the quote-time interaction.
4. Treat FR24 as optional supplementary movement evidence, subject to verified
   balance, prices and coverage; missing tracks alone cannot establish cancellation.

## Budget and publication

No paid services were added. Flightradar24 remains at zero calls and zero credits;
its live balance and reset date remain unverified. The initial ceiling is 6,000
credits within a reported 60,000 monthly allocation. One coordinator controlled
live acquisition and Git; at most two worker agents reviewed independent tasks.

Verified annual milestones are committed and pushed throughout execution.
Final result milestone `16b1c52` is published on the configured public remote.
`git ls-remote` confirmed the branch at
`16b1c529bc8f6c7126911f33734223fa1e724bbe` on 2026-09-13.
Independent final review found no remaining material issues. Public staged
contents, proof hashes and documentation links passed inspection. This completion
record follows the verified result milestone; no declared work remains pending.

## Local state and reproduction

Raw inputs, previous output backups, intermediate files and coordinator scratch
recipes remain ignored. The local Python 3.13.9 environment matches requirements
pins; credentials remain ignored and were not read. Compact outputs, acquisition
recipes, source hashes and provenance are public Git artifacts. Existing source
manifests are preserved on matching reacquisition; changed candidates fail and
remain available for source-revision review.

Use the [full-history reproduction contract](findings/stage6_full_history_report.md)
for annual commands and verification, including the public final certification
command `.\.venv\Scripts\python.exe -m scripts.verify_stage6_history --tests-passed COUNT`.
The original Stage 0-4/Stage 5 runners retain
their separate input requirements; their earlier raw analyses were not rerun as
part of this historical expansion. Last updated: 2026-09-13.
