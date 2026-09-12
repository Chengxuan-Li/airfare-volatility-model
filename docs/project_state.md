# Project state

## Current stage
Stage 0-4 assessment complete on `codex/stage-0-to-4`. The real aggregate pilot and
all feasible Stage 4 analyses ran. Original quote-time H1/H2 and flexibility
premiums are explicitly not estimable, as permitted by the execution addendum.

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
Stage 5 extension authorized by the user and active on `codex/stage-5-robustness`.
The predeclared extension adds all directions among the seven original airports,
2025 Q1/Q2 holdout fares, one-way single-coupon products, T100 capacity controls,
and stronger seasonal effects. Four new fare archives, three annual capacity
extracts and seven extended weather responses have been acquired. Raw rebuild
and model validation are in progress; Stage 0-4 results remain preserved.

## Key conclusions
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
Run `python -m src.acquisition.batch --kind all` to acquire and `python -m src.run`
to rebuild from raw after installing pinned requirements. See README for Windows
commands, full source attribution, and failed-download recovery details.

## Known limitations and open questions
Endogenous quantity; prorated fares and product composition; quarterly timing;
retrospective ERA5 vintage; sparse joint support; few clusters; no external demand
shifter or full capacity model. See report for competing explanations and all fits.

## Next actions
1. Read docs/findings/stage_0_to_4_report.md and the quality/methods documents.
2. Complete the predeclared Stage 5 stress tests and identification assessment.
   New capacity data are diagnostics, not an instrument. Do not spend FR24 credits
   to inflate sample size or relabel descriptive estimates as identified effects.
3. Restore Git authentication if required and publish the committed branch safely.

## Blockers / Git publication
The public origin was verified and fetch succeeded. Final noninteractive push
failed (exit 128) because GitHub username credentials were unavailable. No login
dialog was opened. All work remains committed locally on `codex/stage-0-to-4`.
Restore Git authentication and push that branch; see the final handoff.

## Relevant commits
- `bcb1b47` — Stage 0 research specification.
- `9e594d1` — verified literature and novelty.
- `0641787` — source feasibility and data constraints.
- `6e48581` — tested acquisition/analysis implementation.
- `6465419` — real pilot, provenance, and quality audits.
- `65420ec` — final analysis, reports, and reproducibility verification.
- See subsequent history for final handoff and Git publication status.

## Intentionally uncommitted local files
- `.env`: ignored local key; never commit or print it.
- `.env.example`: pre-existing user edit, intentionally preserved outside commits.
- Raw/intermediate data, `.venv`, and temporary verification snapshot are ignored.
