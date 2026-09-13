# Stage 6 full-year 2010 panel implementation plan

Authorized by the user's "go on" after the proposed full-year 2010 milestone.
Date: 2026-09-12. Spec: [Stage 6 direction](stage6_execution_plan.md).
Use the subagent-driven-development skill for independent bounded implementation
and review; the coordinator alone runs live acquisition, integration and Git.

**Goal:** a reproducible full-year 2010 route-quarter fare/operations panel with
explicit coverage, identity and exclusion audits, before expanding later years.
**Architecture:** preserve the bootstrap and Stage 0-5 outputs. New annual modules
stream the national ZIPs, select a declared airport sample, aggregate fares and
operations independently, and outer-join by year/quarter/stable airport IDs.
**Stack:** existing pinned Python/pandas/NumPy/pytest; existing public BTS fetcher.
**Workspace:** clean checkout on `codex/stage-6-2010-panel`, retaining ignored raw
caches. No paid services, credentials or FR24 calls. At most two workers and two
concurrent coordinator transfers. Raw inputs stay ignored; metadata is committed.

## Sampling and interpretation decisions fixed before new acquisition

- Use 2010 Q1 as the airport-selection baseline. Rank US airports by the sum of
  originating and terminating sampled passengers in domestic, nonbulk,
  single-coupon Market rows with finite positive passenger counts. Do not use fare
  values or operational outcomes for selection. Ties resolve by ascending airport
  ID. Select the top 30 plus the original seven airports for continuity; preserve
  the full ranking and ID/code aliases. Abort ambiguous original-airport mappings.
- 2010 is a development/selection year, not a temporal holdout or an unbiased test
  of selection effects. The fixed sample can be evaluated from 2011 onward after
  a separate model declaration. No coefficients are estimated in this milestone.
- Retain all valid DB1B reporting carriers, with stable endpoint IDs. Primary fare
  rows require domestic endpoints, one Market coupon, nonbulk status, positive
  finite passenger weights, credible matched Ticket (`DollarCred == 1`) and
  nominal Market fare USD 20-2000 inclusive. Preserve the existing broad USD
  10-5000 sensitivity. Keep all aggregated cells and flag passenger counts below
  30 rather than hiding low-support routes. Keep passenger-weighted first/second
  fare moments and report composition/exclusions; do not call traffic exogenous.
- Quarterly operations sum count numerators/denominators across months/reporters,
  then recompute rates; never average monthly rates. Require all 12 source months.
  Preserve carrier-month cells and code-to-DOT-ID mappings as separate diagnostics.
- Primary join is route-quarter across all included carriers on each source side.
  DB1B reporting carriers are not equated to on-time reporting/operating carriers.
  Coverage is not automatically the full airline market. A code match does not
  justify carrier-level linkage. Keep fare-only and operations-only route cells.
  Operations quarters record observed service months; absent route service is not
  silently labelled zero cancellations. Fare data do not distinguish this absence
  from reporting-coverage gaps.
- Preserve airport code/ID alias audits from both sources. Aggregate and join on
  IDs, not mutable code labels. No synthetic history, interpolated missing rows,
  quote-time risk claims, capacity/weather models or new causal estimates.

## Task 1: baseline selection and annual fare aggregation

Files: `src/stage6/annual_fares.py`, `tests/test_stage6_annual_fares.py`.
Interfaces:
```python
select_airports(market_path, *, year=2010, quarter=1, top_n=30, chunksize=250000)
# -> (ranking DataFrame with AirportID, codes, passengers, rank, selected;
#     audit dict). Selected includes the original seven; raw period/IDs validate.
process_fares(market_path, ticket_path, *, year, quarter, airport_ids, chunksize=250000)
# -> (carrier cells, audit dict, airport aliases DataFrame).
# cells: Year, Quarter, OriginAirportID, DestAirportID, RPCarrier, sample,
# passengers, records, fare_total, fare_square_total, fare_mean, fare_variance,
# low_support. aliases: AirportID, code; periods supplied by runner.
```
- [x] Write real temporary CSV/ZIP tests: selection independent of fares, stable
  tie resolution, scope by ID despite code changes, weighted moments, credibility
  and fare exclusions, unmatched Ticket rows, duplicate Market/Ticket keys,
  period mismatch and missing identity. Run red before implementation.
- [x] Implement streamed national period checks, scoped duplicate guards and
  many-to-one Ticket joins, explicit mutually sequential exclusion accounting.
- [x] Run focused tests in `.venv`, independently review spec/quality and commit.

## Task 2: stable-ID operations and quarterly linkage

Files: `src/stage6/operations.py`, `src/stage6/annual_panel.py`,
`tests/test_stage6_annual_panel.py`; retain existing bootstrap API behavior.
Interfaces:
```python
read_operations(path, year, month, *, airports=AIRPORTS, airport_ids=None, chunksize=100000)
# Existing three outputs; supplied airport_ids overrides code scope.
quarterly_operations(monthly_cells)
# -> route-quarter counts/rates with months_observed; reject repeated carrier-month keys.
join_annual_panel(fare_carrier_cells, monthly_operations)
# -> (outer-joined route-quarter sample DataFrame, audit dict).
# Sum fare moments then recompute means/variances. Operations counts unique per route-quarter.
```
- [x] Write failing tests for ID-based selection, weighted quarterly rates,
  duplicates, fare-only/operations-only preservation and independent carrier roles.
- [x] Implement and pass new plus existing operations/bootstrap tests; independent
  spec/quality review. Do not alter previous outputs or default bootstrap hashes.

## Task 3: coordinator acquisition and annual rebuild

Files: `src/stage6/annual.py`, `tests/test_stage6_annual.py`, new acquisition
manifests and `data/manifests/stage6_2010_access_inventory.json`.
CLI:
```powershell
.\.venv\Scripts\python.exe -m src.stage6.annual --acquire
.\.venv\Scripts\python.exe -m src.stage6.annual
```
- [x] Declare exactly eight fare archives and twelve operations archives for 2010.
  Reuse the three cached 2010 inputs; HEAD only new operations months, preserving
  access metadata and failures. Reuse the earlier verified fare access inventory.
  Check advertised bytes/free space before GET batches. Verify every consumed
  expected path, URL, parameters and checksum before reading.
- [x] Test annual input identities/boundaries and missing-source failure before
  output replacement; only injected transports in tests. Implement annual runner.
- [x] Coordinator acquires missing files with bounded public fetch calls. Record
  success/failure/cache outcomes and bytes; preserve failed candidates. On source
  failure stop the dependent build and keep prior outputs intact.
- [x] Save ranking, fare carrier cells, operations carrier-month and national
  totals, airport/carrier identity audits, joined panel and quality report under
  `outputs/stage6/annual_2010/`. Preserve raw national and scoped counts, exclusions,
  monthly availability, low-support flags and unmatched data on both sides.

## Task 4: evidence, review and publication

- [x] Run the full offline suite with exact installed requirements verified.
- [x] Rebuild from all 20 raw inputs twice and compare every derived output byte;
  save manifest/output/source hashes separately in a verification record. Keep
  Stage 0-5 and bootstrap output bytes unchanged.
- [x] Independently review code/spec and final numbers/interpretation. Resolve
  material findings with regressions; record negative results and all deviations.
- [x] Write the 2010 coverage report and next-batch instructions, update state,
  index and execution ledger, and inspect staged public content.
- [x] Commit and push the verified annual results and record publication.

Completion is the verified 2010 panel and report. Full 2011-2025 Q2 acquisition,
cross-year carrier histories, capacity, risk calibration and model estimation
remain subsequent work. Review sampling continuity before applying the sample to
later years; do not claim all DOT history has been used.

Implementation review: explicit string parsing preserves numeric-looking carrier
codes; a pandas mixed-inference failure in the real Q1 file is recorded in the
ledger. Annual publication retains the old output directory in an ignored backup
and restores it if the new directory rename fails. No orphan raw file is adopted
without existing provenance. Full offline suite at implementation: 100 passed.

Final evidence: [2010 report](../findings/stage6_2010_report.md) and
[verification record](../../outputs/stage6/annual_2010/verification.json): twenty
verified inputs, two successful raw builds, eight identical derived files, 100
passing tests. All implementation tasks are complete; next-year work is distinct.
Result milestone `8a036a8` was successfully pushed to `codex/stage-6-2010-panel`.
