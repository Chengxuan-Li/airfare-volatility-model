# Stage 0-4 implementation plan

> For agentic workers: use the approved autonomous workflow and bounded independent
> research/review tasks; the coordinator integrates and commits each milestone.

**Goal:** Execute a reproducible real-data pilot and an honest Stage 0-4 assessment.
**Architecture:** Download/cache/manifests -> streamed DB1B filtering and aggregation
-> historical weather risk -> keyed panel -> descriptive models, audits, figures.
**Tech stack:** Python 3.13, pandas, numpy, requests, scipy, statsmodels, matplotlib,
pyarrow, pytest in an ignored local virtual environment, pinned requirements.
**Spec:** `docs/20260912_airline_weather_pricing_research_task.md` and Stage 0 charter.

## Constraints and rulings

No additional paid services; 6,000 FR24 credits maximum, preferably zero when BTS
substitutes. At most two workers; coordinator owns acquisition and Git. Preserve
user `.env.example` edit. Use current checkout on a dedicated branch to retain
already downloaded multi-GB inputs; no parallel edits to shared modules.
Ruling: user explicitly authorized autonomous execution after the design discussion;
routine skill approval pauses are superseded. Record refinements before fitting.

## Milestones

- [x] Stage 0: charter, hypotheses, falsification; commit specification.
- [ ] Stage 1: verified literature CSV, coverage of all required areas, novelty
  assessment; review citations and commit.
- [ ] Stage 2: source matrix and five feasibility documents; select weather and
  operational validation; document available P/D/R and impossible estimands.
- [ ] Acquisition: `src/acquisition/download.py` exposes a bounded cached download
  with SHA-256 manifest and ZIP validation; reject corrupt cache. Tests use local
  fixture ZIPs and a local HTTP server, not remote calls or secret credentials.
- [ ] Cleaning: `src/cleaning/db1b.py` exposes clean_market(frame) and aggregate
  routines; tests hand-check passenger weighting, exclusion counts, year-scoped
  Ticket joins and variance. Stream all requested periods, log filtering audits.
- [ ] Weather: `src/weather/risk.py` exposes prior_season_risk(daily, year, quarter);
  tests future exclusion, leap-day coverage, null handling, and exact thresholds.
- [ ] Analysis: `src/analysis/pilot.py` fits declared models, checks rank/support,
  exports coefficient/marginal-effect/dispersion tables and raw/fitted figures.
  Test marginal effects with hand-specified coefficients and reject singular fits.
- [ ] Stage 3: run acquisition and cleaning, write dictionary/missingness/duplicate/
  matching audits, commit source code, metadata, and compact permitted aggregates.
- [ ] Stage 4: run every feasible analysis; report unestimable original H1/H2 and
  flexibility premium separately. Write preliminary and consolidated reports,
  independent methodological/code review, resolve material findings, rerun tests
  and core pipeline from cached raw inputs, update README/index/state and commit.

## Verification commands

Use `.venv/Scripts/python -m pytest -q` for offline tests. Use
`.venv/Scripts/python -m src.run --acquire` to acquire, then
`.venv/Scripts/python -m src.run` to reproduce from cached inputs. Require output
schema/rank audits and SHA-256 provenance. Inspect staged diff and scan tracked
content against local credential values without printing them. Push only with
noninteractive authentication available; do not reopen cancelled dialogs.
