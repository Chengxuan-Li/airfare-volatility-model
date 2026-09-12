# Project state

## Current stage
Stage 5 analysis and verification complete on `codex/stage-5-robustness`.
Two full raw builds reproduce 15 derived outputs byte-for-byte; 21 tests pass.
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
No research work remains in this pass. Strong identification-argument stopping
criterion met; Git publication is blocked by unavailable credentials.
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
Run `python -m src.acquisition.batch --kind all` to acquire and `python -m src.run`
to rebuild from raw after installing pinned requirements. See README for Windows
commands, full source attribution, and failed-download recovery details.

## Known limitations and open questions
Endogenous quantity; prorated fares and product composition; quarterly timing;
retrospective ERA5 vintage; sparse joint support; few clusters; no external demand
shifter or full capacity model. See report for competing explanations and all fits.

## Next actions
1. Read docs/findings/stage5_report.md and docs/methods/stage5_reproduction.md.
2. Future research needs an
   aligned information/identification design. Do not spend FR24 credits to inflate
   sample size or relabel descriptive estimates as identified effects.
3. Restore Git authentication if required and publish the committed branch safely.

## Blockers / Git publication
The public origin was verified and fetch succeeded. Final noninteractive push
failed (exit 128) because GitHub username credentials were unavailable. A Stage5
fetch succeeded and noninteractive push failed for the same reason. No login
dialog was opened. Research and verification are committed locally on
`codex/stage-5-robustness`, which includes the prior Stage0-4 history.
Restore Git authentication and push that branch; see the Stage5 handoff.

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
- `.env`: ignored local key; never commit or print it.
- `.env.example`: pre-existing user edit, intentionally preserved outside commits.
- Raw/intermediate data, `.venv`, and temporary verification snapshot are ignored.
