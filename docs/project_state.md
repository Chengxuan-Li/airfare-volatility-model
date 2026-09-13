# Project state

## Current stage
Stage 6 historical/operations work is authorized and starting on
`codex/stage-6-operations`; see [execution plan](methods/stage6_execution_plan.md).
First milestone: provenance fixes, historical access inventory and a two-month
flight-operations bootstrap. The full 2010-2025 Q2 expansion is not yet complete.
The two acquisition/reproduction fixes now pass 34 relevant tests in a newly
installed pinned environment. Live historical HEAD inventory is in progress.

Stage 5 assessment is complete on `codex/stage-5-robustness`; the repository review
found two open acquisition/reproduction defects. The earlier execution recorded
two full raw builds reproducing 15 derived outputs byte-for-byte. This review
reran 21 passing tests and reproduced the Stage 5 estimates from the saved panel;
raw inputs are absent in this checkout, so a full raw build was not repeated.
Stage 0-4 results remain preserved. Original
quote-time H1/H2 and flexibility premiums remain unidentifiable from these sources.

## Last updated
2026-09-12

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
The prior pass's identification-argument stopping criterion remains met; it did not
exhaust DOT data. The user authorized the broader historical and operations-data
direction on 2026-09-12; execution begins with the bounded Stage 6 plan.
The two reproduction defects in the
[repository review](reviews/2026-09-12-repository-review.md) are fixed with regression
tests: original-stage verification is explicit, and reacquisition preserves
recorded provenance or rejects changed content. Further bootstrap work is ongoing.
The review also found two scope gaps between the broader identification note and
the narrower executed plan: departure/supply-channel models and CR2/bootstrap
inference need explicit deferred status or a separately declared follow-up.
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
coordinator controlled acquisition. No prospective collection was scheduled.

## Data status
Raw sources are ignored under `data/raw/`; intermediate quarterly aggregates are
ignored under `data/processed/`. Compact outputs and manifests are Git-controlled.
The Stage 0-4 runner now checks its 25 required paths and checksums, regardless of
other manifests. Reacquisition checks existing request identity before transfer
and checksum before promotion. Changed candidates stay in `.part`; previous
manifests are preserved. Original historical raw inputs have not all been rebuilt
on this machine, so the fixes' test coverage is not a fresh full-pilot rebuild.
See the review for reproductions and the Stage 5 guide for its separate workflow.

## Known limitations and open questions
Endogenous quantity; prorated fares and product composition; quarterly timing;
retrospective ERA5 vintage; sparse joint support; few clusters; no external demand
shifter or full capacity model. See report for competing explanations and all fits.

## Next actions
1. Complete the Stage 6 historical inventory and operations bootstrap; the two P1
   reproduction fixes now have passing regression checks.
2. Reconcile the two P2 method-scope gaps. Read docs/findings/stage5_report.md and
   docs/methods/stage5_reproduction.md alongside the broader identification note.
3. Future research needs an
   aligned information/identification design. Do not spend FR24 credits to inflate
   sample size or relabel descriptive estimates as identified effects.
4. Consider the proposed 2010-2025 Q2 aggregate extension and BTS flight-level
   irregular-operations measurement. Only ten fare quarters have been analyzed;
   FR24 remains unused. Verify access and declare scope before new acquisition.

## Blockers / Git publication
The earlier execution's failed push is historical. During this review,
`git ls-remote --heads origin codex/stage-5-robustness` returned
`08b00603d46272e182b9c7c5636c150d535b43cb`, matching the reviewed HEAD.
The research branch is published, including prior Stage 0-4 history. That read-only
check establishes publication, not write authentication on this machine.

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

## Intentionally uncommitted local files
- The review began with a clean working tree; `.env.example` is tracked and has
  no uncommitted edit here. Earlier handoffs describe a different local state.
- A local ignored `.venv` with the exact requirements pins has now been installed
  on Python 3.13.9. Earlier review tests used the available system environment.
- Credential files remain ignored; no credentials were read. Review calculations
  used temporary storage and left the tracked research outputs unchanged.
