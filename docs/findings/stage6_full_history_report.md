# Historical fare and operations panel: 2010 Q1-2025 Q2

Execution started 2026-09-13 under the [continuous plan](../methods/stage6_full_history_plan.md).
All sixteen declared annual/partial-year panels are built and verified.
Result milestone `16b1c52` is published and verified on the public remote;
see [project state](../project_state.md) for the publication record.

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
For example, observed operations DOT IDs increase from twelve in 2017 to eighteen
in 2018, while fare reporting codes decrease from twenty-four to twenty-two. This
population break limits interpretation of changes in national record totals as
traffic growth; the sources do not share a common carrier reporting universe.
For 2025, baseline comparisons are restricted to Q1-Q2 and January-June; later
unrequested periods cannot establish exits. Full-year and half-year totals should
not be compared without matching periods.

The 2020-2021 pandemic and 2022-onward recovery labels in coverage summaries are
descriptive periods. They are not instruments, causal controls or an estimated
regime model. Quarterly nominal prorated fares remain distinct from timestamped
quotes; observed passenger traffic remains jointly determined with prices.

## Acquisition and annual coverage

All 270 remaining endpoints passed HEAD checks, advertising 13,165,882,016 bytes;
121,456,566,272 bytes were free before acquisition. See the
[access summary](../../data/manifests/stage6_full_history_access_summary.json),
per-year access inventories and [execution ledger](../status/execution_ledger.md).
The 2010/2011 panels were already published. All remaining 270 archives are
acquired and verified; all annual builds are now reproduced and certified. The
[acquisition summary](../../data/manifests/stage6_full_history_acquisition_summary.json)
records 269 downloads/reacquisitions and one verified cache, with no transfer
failures or FR24 use. HEAD access alone does not establish complete data validity.

<!-- YEAR_PROGRESS_START -->
| Verified year | Fare quarters | Retained national records | Retained scoped records | Primary fare cells | Matched | Passenger-weight match |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2010 | 4 | 6,450,117 | 2,100,986 | 3,191 | 2,904 | 99.8458% |
| 2011 | 4 | 6,085,281 | 2,110,718 | 3,198 | 2,865 | 99.8203% |
| 2012 | 4 | 6,096,762 | 2,139,724 | 3,203 | 2,882 | 99.8648% |
| 2013 | 4 | 6,369,482 | 2,156,616 | 3,206 | 2,896 | 99.8103% |
| 2014 | 4 | 5,819,811 | 2,084,233 | 3,219 | 2,899 | 99.7376% |
| 2015 | 4 | 5,819,079 | 2,191,225 | 3,216 | 2,937 | 99.8852% |
| 2016 | 4 | 5,617,658 | 2,216,189 | 3,201 | 2,943 | 99.9004% |
| 2017 | 4 | 5,674,616 | 2,220,493 | 3,192 | 2,971 | 99.9336% |
| 2018 | 4 | 7,206,193 | 2,388,143 | 3,177 | 3,027 | 99.9624% |
| 2019 | 4 | 7,422,037 | 2,380,567 | 3,182 | 3,025 | 99.9672% |
| 2020 | 4 | 4,688,354 | 1,474,864 | 3,059 | 2,914 | 99.9666% |
| 2021 | 4 | 5,995,397 | 1,855,941 | 3,140 | 2,980 | 99.9549% |
| 2022 | 4 | 6,729,125 | 2,171,867 | 3,169 | 3,019 | 99.9687% |
| 2023 | 4 | 6,847,899 | 2,264,311 | 3,196 | 3,019 | 99.9607% |
| 2024 | 4 | 7,079,061 | 2,283,263 | 3,127 | 3,021 | 99.9645% |
| 2025 Q1-Q2 | 2 | 3,446,676 | 1,120,694 | 1,560 | 1,496 | 99.9738% |
<!-- YEAR_PROGRESS_END -->

The coordinator alone downloads in bounded pairs and verifies caches, request
identities, checksums and ZIP CRCs. Existing manifests are preserved, including
two legacy 2024 fare manifests with top-level year/quarter fields. No paid
services, FR24 calls or credits are used. Raw files and environment remain ignored.

## Observed data-quality exceptions

The first 2012 build stopped before publication on one July flight with a blank
scheduled departure time. Source inspection confirmed a genuine blank, not a CSV
parsing substitution. The reader now retains such a row only if its remaining
date/DOT-carrier/flight-number/endpoint key is unique across the complete month.
The schedule stays missing; actual departure is never substituted. Both directions
of cross-chunk ambiguity and missing required grouping identities still fail verification.
Affected national and selected-flight counts are explicit in the monthly audit.
The July case is outside the selected network (one national, zero selected rows).
The failed attempt remains in its build-attempt ledger alongside the two successful
reproduction passes. No input bytes were changed.

The first 2017 build stopped in May on two records sharing a complete scheduled
flight key. Every identity and outcome field consumed here agrees, including a
cancellation, no diversion and missing arrival delay. Tail/departure/ground-return
metadata outside this analysis differ, so these are not identical full source
rows. The reviewed rule counts a repeated complete key once only when all consumed
fields agree, including missingness. The default reader rejects conflicts; the
annual workflow uses the quarantine rule below. Ambiguous incomplete keys still
fail. Raw rows, retained records and removed repeats are audited
separately; national totals above count retained reported analysis units.
The original raw variants remain available for any future aircraft or departure
analysis, which would need its own resolution rule.

Later 2017/2018 builds stopped on conflicting outcomes for complete keys. July
2017 has a SEA-LAS scheduled flight with both a delayed-arrival record and a
return/diversion record on different aircraft. June 2018 has a DEN-XNA scheduled
flight with two aircraft and arrival delays of 4 versus 941 minutes. The key alone
cannot establish which physical-flight history should be the analysis unit.
November 2017 also has a conflicting MSP-DLH key (DOT20304, flight 4529):
arrival delay 750 minutes versus a diverted record with missing arrival delay.
The 2017 exclusions therefore total four rows in two groups: two July rows within
the selected sample and two November rows outside it. The two June 2018 rows are
also outside the selected sample.

After independent policy review, the annual workflow quarantines every row for a
conflicting complete key. A full-month preflight validates all rows and classifies
exact consumed variants; a second pass aggregates only unambiguous retained rows.
The audit reports excluded groups/rows nationally and in scope and preserves each
consumed variant and its count. Equivalent repeats within a conflicting group are
all quarantined, never also counted as equivalent removals. Raw equals retained
plus equivalent removals plus ambiguity exclusions. Invalid source values and
incomplete-key collisions still fail. Raw bytes and all failed attempts remain.
These small exclusions may depend on disruptions; retained outcome rates are
conditional on unambiguous records and do not resolve every irregular operation.

The first 2024 build stopped in August on one genuinely blank flight number:
F9/DOT20436, August 25, MIA-ATL, scheduled 0600. Its remaining exact key occurs
once among 619,025 monthly rows. The annual workflow may retain this unique
incomplete key without imputing a number, with explicit national/scoped counts.
It contributes one retained national row and one retained selected row.
Scheduled time must be present; both optional fields missing, projected-key
collisions, and potentially overlapping missing-time/missing-number rows fail.
The original missing number and failed build remain part of the evidence.

The combined-summary reconciliation initially failed in 2025 because it compared
national and scoped carrier populations. The summary now reports both:
`operations_reporting_dot_ids` is national, while
`scoped_operations_reporting_dot_ids` counts retained routes between selected
airports and reconciles to the annual panel audit. In 2025 these counts are 14
and 13: DOT20368/G4 is observed nationally in January-June but has no retained
route between the frozen airports. National carrier presence remains preserved;
sample absence does not establish service closure.

## Reproduction contract

Each new year is built twice from raw. Its `verification.json` records all derived
hashes, consumed raw hashes, frozen baseline artifact hashes, implementation/source
identity, Python/requirements pins and test evidence. Failed attempts are preserved
in per-year build-attempt manifests. Old output sets remain ignored backups.
Text-metadata evidence hashes are explicitly LF-normalized to tolerate checkout
line endings. Raw archive and derived output hashes remain byte-exact; the final
consumed-input manifest and Stage 6 outputs have Git-enforced LF line endings.

From the repository root with the pinned environment:

```powershell
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2024 --acquire --output data/processed/replay_2024_a
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2024 --output data/processed/replay_2024_b
.\.venv\Scripts\python.exe -m pytest -q
```

After all annual proof files are available, run
`.\.venv\Scripts\python.exe -m scripts.verify_stage6_history --tests-passed COUNT`, replacing COUNT
with the freshly observed full offline test count. This public certification
recipe verifies raw archives, historical source commits, frozen artifacts and
the two summary builds.

Use each declared year in the annual command. `--year 2025` automatically requests
only Q1-Q2/January-June, not a full year. The published frozen 2010 artifacts and
manifest are required; later years do not rescan or rerank 2010 raw data.
The two separate replay directories preserve the published annual evidence.
Compare each file in `output_sha256` from the corresponding published annual
`verification.json` against both replay directories using SHA-256. For exact
historical replay, use that proof's `implementation_commit` and pinned environment:
source versions changed during this expansion, and current-code replay alone is
not evidence of an earlier implementation's byte identity. The annual command
writes aggregates and quality audits; it does not automatically issue a new
two-build verification record. Published proofs remain tied to their recorded
inputs, implementation and outputs; a changed result requires fresh verification.
Per-year files remain the canonical panels; the compact horizon summaries verify
all annual artifacts and reconcile annual/quarterly totals. A rebuild moves an old verification record
to the backup rather than attaching it to newly unverified outputs.

## Verified horizon findings

All 310 consumed archives pass exact request-identity, SHA-256 and ZIP CRC
checks, totaling 14,782,676,474 compressed bytes.

The inputs contain 387,251,539 Market rows, 232,355,006 Ticket rows and 97,347,555
reported operations rows. The operations rule retains 97,347,548 reported
analysis units nationally (1 equivalent repeat and 6 ambiguous
source rows excluded), including 33,159,834
retained records between the frozen airports. These are source-reporting populations,
not a census of every airline or an exogenous measure of demand.

The primary sample has 49,236 fare route-quarters: 45,798
matched and 3,438 fare-only; the outer panel also retains
30 operations-only cells. Matched cells account for
99.9108% of primary sampled passenger weights. High passenger-weight coverage
does not make unmatched routes ignorable or establish comparable carrier reporting.
The primary panel flags 718 operations
cells with only one or two observed months and
25 with eligible missing delay outcomes.
Absence stays distinct from zero activity and observed cancellation.

The [annual summary](../../outputs/stage6/history/annual_summary.csv),
[quarterly summary](../../outputs/stage6/history/quarterly_summary.csv) and
[carrier presence](../../outputs/stage6/history/carrier_presence.csv) expose coverage,
support and source-population changes. The
[quality audit](../../outputs/stage6/history/quality_audit.json) reconciles the
62 quarterly rows to sixteen annual/partial-year rows. The final
[consumed-input manifest](../../data/manifests/stage6_full_history_consumed_inputs.json)
records all 310 identities and every observed operations source exception.

Every year has two successful byte-identical raw builds. Two summary builds
reproduce all four derived summary files; their
[verification](../../outputs/stage6/history/verification.json) links all sixteen
annual proofs and the final raw-input verification. All 62 output files from
the pre-extension reference `db0cd7b` remain unchanged. The final offline suite
has 251 passing tests, with the known Stage 5 rank-deficient design warning.

## Remaining research

Completing this data horizon does not complete capacity expansion, aligned
forecast/quote collection, departure/supply modeling or new econometric estimates.
Those require separate measurement and identification decisions. The original
quote-time hypotheses remain unidentifiable from quarterly purchases alone.
