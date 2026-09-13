# Project state

## Current stage
Continuous completion of 2012-2025 Q2 is authorized and in progress on
`codex/stage-6-full-history`; see the [plan](methods/stage6_full_history_plan.md).
The user explicitly requested all remaining years without further commands.
2025 is limited to Q1-Q2/January-June and must use matching baseline periods.

The 2011 extension is complete and published on `codex/stage-6-2011-panel`;
see [report](findings/stage6_2011_report.md) and [plan](methods/stage6_2011_plan.md).
It reuses the frozen thirty 2010 airport IDs and adds cross-year coverage audits.
All twenty 2011 inputs verify (805,060,530 bytes); no source failures or FR24 calls.
Two raw builds reproduce eleven derived files byte-for-byte; 118 offline tests
pass on the pinned environment. All fifty earlier output files remain unchanged.
Final artifact review found no material issues; result milestone `804a3b7` is published.
No new models are estimated.

2011 scans 22,999,175 Market rows, 13,343,503 Ticket rows and 6,085,281 national
reported flights (2,110,718 between selected airports). Primary has 3,198 fare
route-quarters: 2,865 matched, 333 fare-only, plus one operations-only cell in the
outer panel. Matched cells cover 99.8203% of sampled passenger weights. All thirty
airports remain observed; reporting populations change from 36 to 34 fare codes
and 18 to 16 operations DOT IDs. Absence is not a cancellation or a verified
service closure. Fare and operations carriers remain separately aggregated.

The full-year 2010 panel is complete on `codex/stage-6-2010-panel`; see the
[report](findings/stage6_2010_report.md) and [plan](methods/stage6_2010_plan.md).
Thirty airports selected by baseline passenger volume; stable-ID route-quarter
linkage aggregates each source independently across its reporting carriers.
All twenty inputs are cached and checksum/CRC verified (811,733,928 bytes).
Two successful raw builds reproduce eight outputs byte-for-byte; 100 offline
tests pass. One earlier CSV-parser failure is preserved in the execution ledger.
No new fare models were estimated. Full 2012-2025 Q2 expansion remains outstanding.

The 2010 inputs contain 22,038,685 Market rows, 12,688,062 Ticket rows and 6,450,117
reported flights nationally. The scoped primary panel retains 3,191 fare
route-quarters: 2,904 matched to operations and 287 fare-only, covering 99.8458% of
primary sampled passenger weights in matched cells. The broad-bound panel has
3,193 cells. All 26 matched cells with only one or two observed service months are
flagged; missing operations are not imputed to zero. Carrier populations differ
(36 fare reporting codes, 18 operations DOT IDs); there is no carrier-level join.

Stage 6 historical/operations bootstrap is complete on
`codex/stage-6-operations`; see [execution plan](methods/stage6_execution_plan.md).
The [bootstrap report](findings/stage6_bootstrap_report.md) records provenance fixes,
124 successful historical fare HEAD checks, four downloaded archives and 1,069,080
flight records checked. Two raw builds reproduce four compact outputs byte-for-byte;
71 offline tests pass in the freshly installed pinned environment. The full
2010-2025 Q2 expansion is not yet complete; no new fare models were estimated.

Stage 5 assessment is complete on `codex/stage-5-robustness`; the repository review
found two acquisition/reproduction defects, now fixed. The earlier execution recorded
two full raw builds reproducing 15 derived outputs byte-for-byte. This review
reran 21 passing tests and reproduced the Stage 5 estimates from the saved panel;
original Stage 5 raw inputs were absent in this checkout, so its full raw build
was not repeated. Four Stage 6 bootstrap inputs are now present.
Stage 0-4 results remain preserved. Original
quote-time H1/H2 and flexibility premiums remain unidentifiable from these sources.

## Last updated
2026-09-13

## Completed
- Stage 0 charter, original hypotheses, aggregate redesign, and falsification rules.
- Stage 1 primary-source map: 22 studies, fifteen required areas, cautious novelty B
  for the original aligned design and substantially weaker aggregate novelty.
- Stage 2 fare/demand/weather/outcome feasibility and public-data access matrix.
- Stage 3: sixteen DB1B Market/Ticket ZIPs (2023-24), seven ERA5 responses,
  OurAirports registry and BTS Delay Causes; 25 provenance manifests, ~1.59 GB raw.
- 222 primary route/carrier/quarter cells on twelve routes; 618,324 sampled passenger
  weights, 211,651 Market records. No synthetic research data.
- Stage 4: thirteen fare specifications, external airport-quarter validation,
  marginal-effect intervals, support/quality audits, four figures, consolidated report.
- Sixteen offline tests pass. Final full raw rebuild reproduces 19 table/figure
  outputs byte-for-byte after canonical float parsing; three raw builds total.
- Independent code/methodology and final report reviews completed; findings addressed.

## In progress
The audited 2011 batch is reproduced, independently reviewed and published.
The annual runner accepts only 2010 and 2011, retaining the 2010 default.
The next data milestone is a declared 2012 batch; later-year acquisition remains
outstanding.

The prior pass's identification-argument stopping criterion remains met; it did not
exhaust DOT data. The user authorized the broader historical and operations-data
direction on 2026-09-12; the bounded Stage 6 bootstrap is now verified.
The two reproduction defects in the
[repository review](reviews/2026-09-12-repository-review.md) are fixed with regression
tests: original-stage verification is explicit, and reacquisition preserves
recorded provenance or rejects changed content. Inventory files also refuse
replacement, preserving earlier source failures.
The review also found two scope gaps between the broader identification note and
the narrower executed plan: departure/supply-channel models and CR2/bootstrap
inference are explicitly deferred in the Stage 6 plan and bootstrap report.
The following Stage 5 counts and verification statements describe the earlier run.
The extension has 905 primary cells across 42 directions and 94 route/carrier groups,
plus 873 one-way product cells. Four new fare archives, three annual capacity
extracts and seven extended weather responses were acquired. All 1,778 product
cells match risk and capacity. Of 62 declared fits, 54 estimate and eight seasonal
holdout fits are saturated. Twenty-one offline tests pass; the second full raw
rebuild and independent code/report reviews are complete. The 15 compared outputs
are byte-identical, with all 30 consumed input identities/checksums/payloads verified.

## Key conclusions
- Stage 5 expanded training interaction+50.58, approximate interval[-38.02,139.19];
  holdout+33.88[-112.42,180.18]. Standard-effect leave-ORD-out estimate is-1.19.
  Seasonal controls reduce residual weather-risk SD by 75% and fixed climatology
  is exactly absorbed. No baseline primary/one-way interaction interval excludes 0.
- Strong stopping argument: quarterly purchases and marginal proxies lack the
  quote-time joint demand/risk moment. This is non-identification, not a causal null
  or a claim that all possible datasets/methods have been exhausted.
- Decision C: interesting empirical observation, weak paper.
- Aggregate risk effect at reference log traffic: -20.52 USD per 10pp exposure;
  interaction +227.55 USD per log-traffic point per unit risk fraction. Both point
  signs oppose the proposed aggregate signs; interaction interval crosses zero.
- Original mechanism remains untested: DB1B has no quote timestamps or aligned
  forecast/inventory information. Traffic and fares are jointly determined.
- Only eight of 29 route/carrier groups cover both reference risk quartiles.
  Twelve route clusters and seven validation clusters yield fragile inference.
- Historical weather exposure is not a calibrated cancellation probability.

## Important assumptions and budget
No additional paid services. Flightradar24: zero calls, zero credits used; initial
cap remains 6,000 within a reported 60,000 monthly allocation. Reset date and live
remaining balance remain unknown. At most two worker agents were active; the
coordinator controlled raw acquisition. An unintended worker-test HTTP invocation
incident and its prevention are documented in the execution ledger; all such
attempts returned client exceptions without HTTP status. No prospective collection
was scheduled.

## Data status
Raw sources are ignored under `data/raw/`; intermediate quarterly aggregates are
ignored under `data/processed/`. Compact outputs and manifests are Git-controlled.
The Stage 0-4 runner now checks its 25 required paths and checksums, regardless of
other manifests. Reacquisition checks existing request identity before transfer
and checksum before promotion. Changed candidates stay in `.part`; previous
manifests are preserved. Original historical raw inputs have not all been rebuilt
on this machine, so the fixes' test coverage is not a fresh full-pilot rebuild.
See the review for reproductions and the Stage 5 guide for its separate workflow.
The earlier bootstrap used four inputs totaling 163,801,228 compressed bytes:
January 2010/2024 reporting on-time and 2010 Q1 DB1B Market/Ticket. The annual
milestones now have all eight fare files and twelve operations months in each of
2010 and 2011, with three 2010 bootstrap inputs reused. The 124-fare-archive access inventory advertises
about 9.93 GB; later-year bulk acquisition is still outstanding. Original recipe
404s and successful corrected probes are both preserved.

## Known limitations and open questions
Endogenous quantity; prorated fares and product composition; quarterly timing;
retrospective ERA5 vintage; sparse joint support; few clusters; no external demand
shifter or full capacity model. See report for competing explanations and all fits.

## Next actions
1. Declare and parameterize an audited 2012 batch using the frozen 2010 airport IDs; check
   carrier identities and reporting coverage before broadening later years.
2. Expand 2012-2025 Q2 fares and monthly operations in audited year batches; fare
   endpoint access is verified but full acquisition and comparability remain
   outstanding. The 2010 development panel is built without new model fits.
3. Add compatible capacity and forecast-vintage risk; predeclare departure/supply
   outcome models and CR2/bootstrap sensitivity before expanded fare estimation.
4. Keep the aligned information/identification design separate from descriptive
   sample expansion. FR24 remains unused and supplemental, subject to verified
   balance/cost and coverage; missing tracks cannot alone establish cancellations.

## Blockers / Git publication
The Stage 5 branch is published through `2968268`. Stage 6 uses the separate
`codex/stage-6-operations` branch. Noninteractive push succeeded for bootstrap
milestone `4ae39ec`, including the plan and provenance fixes. Final independent
code/report review found no remaining material issues. Raw inputs and the pinned
environment remain ignored; no tracked user changes were left outside the work.
The annual 2010 work is published on `codex/stage-6-2010-panel`. Noninteractive
push succeeded for result milestone `8a036a8`, including the declared plan,
acquisition and reviewed implementation. Independent final artifact review
reconciled all counts and hashes. No unresolved code or scientific-report findings.
The 2011 result milestone `804a3b7` and all preceding plan/acquisition/implementation
commits are published on `origin/codex/stage-6-2011-panel`. Independent code and
artifact reviews found no material issues. Raw data and previous output backups
remain ignored. A review command accidentally wrote a flattened source copy to
an untracked `CON` file; the coordinator verified its exact source-only hash and
removed that generated artifact before final handoff. No user work was discarded.

## Relevant commits
- `bcb1b47` — Stage 0 research specification.
- `9e594d1` — verified literature and novelty.
- `0641787` — source feasibility and data constraints.
- `6e48581` — tested acquisition/analysis implementation.
- `6465419` — real pilot, provenance, and quality audits.
- `65420ec` — final analysis, reports, and reproducibility verification.
- See subsequent history for final handoff and Git publication status.
- `e8c99f4` — predeclared Stage5 design.
- `5201a91` — tested acquisition, products, capacity and identification.
- `0738495` — expanded results, reviewed methods and durable outputs.
- `6461da8` — authorized Stage 6 execution plan, committed before implementation.
- `631e56e` — provenance preservation and original-pipeline input verification.
- `4ae39ec` — verified historical access, operations bootstrap, report and outputs.
- `af1544c` — declared full-year 2010 sampling and linkage rules.
- `6a64b7c` — verified acquisition of twenty full-year source archives.
- `96e0c31` — tested annual pipeline, parser fix and safe output publication.
- `8a036a8` — verified 2010 outputs, coverage report and reproduction evidence.
- `7190f84` — declared 2011 scope and pinned the frozen 2010 sample.
- `2129ae3` — verified twenty 2011 source archives and acquisition provenance.
- `b085a1a` — reviewed frozen-year runner and source-separated continuity audits.
- `804a3b7` — published reproduced 2011 panel, coverage report and verification.

## Intentionally uncommitted local files
- The review began with a clean working tree; `.env.example` is tracked and has
  no uncommitted edit here. Earlier handoffs describe a different local state.
- A local ignored `.venv` with the exact requirements pins has now been installed
  on Python 3.13.9. Earlier review tests used the available system environment.
- Credential files remain ignored; no credentials were read. Review calculations
  used temporary storage and left the tracked research outputs unchanged.
- Previous annual derived output sets are retained in ignored sibling backup
  directories for rollback/provenance. Current compact annual outputs are published.
