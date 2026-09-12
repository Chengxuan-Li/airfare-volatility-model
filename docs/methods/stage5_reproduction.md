# Stage 5 structure and reproduction

Run from the repository root using the pinned Python environment. The original
Stage0-4 pipeline and its outputs remain separate.

```powershell
.\.venv\Scripts\python.exe -m src.stage5.acquire
.\.venv\Scripts\python.exe -m pytest -q
$env:OPENBLAS_NUM_THREADS='1'
.\.venv\Scripts\python.exe -m src.stage5.pipeline
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
.\.venv\Scripts\python.exe -m src.stage5.analyze
```

First acquire the original 2023-24 fare inputs and OurAirports registry using the
README's Stage0-4 acquisition command if absent. Stage5 acquisition adds 2025Q1/Q2
Market/Ticket, seven extended weather files and three T100 form extracts. It is
cached and bounded; no authentication or paid API is used. Two fare downloads
maximum run concurrently. A failed download stops its batch; see the ledger for
the one bounded resume used in this pass.

`pipeline --reuse-fares` verifies raw inputs but reuses the compact fare-cell CSV;
without that flag it streams all ten raw Market/Ticket pairs. Both paths load the
same CSV with round-trip float parsing before matching weather and capacity.
`analyze` reads `panel.csv` and fits every declared model. Run it only after a
successful pipeline command. NumPy/BLAS settings improve reproducibility and avoid
thread oversubscription; no model depends on parallel computation.

## Files and responsibilities

| Location | Responsibility |
| --- | --- |
| `src/stage5/acquire.py` | Form-state parser, exact T100 fields, cached public acquisition, actual input-path/request/SHA/payload verification |
| `src/stage5/pipeline.py` | National fare streaming, product checks, route capacity sums, lagged weather, joins and audits |
| `src/stage5/analyze.py` | Nuisance FE basis, focal rank checks,62 planned attempts, approximate pair inference, sensitivity plot |
| `tests/test_stage5.py` | Product/proration, operator aggregation, absorption, redundant-FE slope equivalence, saturated rejection and consumed-path checks |
| `data/raw/bts_db1b/` | Ignored Market/Ticket archives,2023Q1-2025Q2 |
| `data/raw/t100/` | Ignored annual 2023-25 form responses; data and Documentation.csv members |
| `data/raw/weather/*_2020_2025.json` | Ignored original ERA5 responses; original 2020-24 files preserved |
| `data/manifests/` | Tracked URLs/form parameters, relative paths, SHA-256, byte counts and CRC provenance |
| `outputs/stage5/` | Compact shareable derived aggregates and all declared model outputs |

## Output dictionary

- `fare_cells.csv`: Year, Quarter, Origin, Dest, RPCarrier, sampled passengers,
  contributing records, passenger-weighted fare mean/within-cell variance, sample.
  Primary and one_way overlap. Variance is purchased-fare dispersion, not quote
  volatility or a demand-driven variance component.
- `fare_audit.json`: scanned/scoped counts, Ticket match/credibility exclusions,
  fare/product exclusions, whole-ticket fare agreement and minimum-cell removals.
- `weather.csv`: airport-quarter rolling and fixed risk, coverage, historical
  source dates. Prior three same-season years; fixed always 2020-22; 100% coverage.
- `capacity.csv`: directed-route quarterly passengers, seats, performed and
  scheduled departures, load factor and scheduled/performed diagnostics. Ratios
  are formed after all-operator sums.2025Q3/Q4 are retained as acquired capacity
  context but never matched into the ten-quarter fare study.
- `capacity_audit.json`: annual raw/selected rows, all monthly/class frequencies,
  declared month coverage. Only service class F enters aggregates.
- `panel.csv`: fare cells plus endpoint rolling/fixed risk, mean endpoint risk,
  capacity and FE/pair labels. Log-quantity centering happens in the analyzer.
- `matching_audit.json`, `unmatched_capacity_keys.csv`: row counts and unmatched
  keys within declared periods; empty key output with headers means no unmatched
  declared-period keys. No capacity imputation.
- `coefficients.csv`: all focal estimates, SE, approximate intervals/p-values,
  sample and pair counts. No nuisance coefficients are treated as discoveries.
- `model_status.csv`: every formula/attempt, estimated or explicit failure,
  numerical rank/conditioning and observation counts. Matched and unmatched base
  samples coincide here because every primary cell has valid capacity.
- `identifying_support.csv`: raw/within-FE risk standard deviation, fixed-risk
  residual maximum, groups and repeated groups. Absorption is not a causal null.
- `same_season_changes.csv`: complete training route/carrier/season differences,
 2024 minus2023, for transparent inspection of the seasonal comparison.
- `sample_summary.csv`, `analysis_metadata.json`: period/product size and fare
  range, training references, attempt totals and inference limitations.
- `interaction_sensitivity.png`: baseline interaction estimates with approximate
  intervals; saturated holdout-seasonal fits appear in status, not as zero points.
- `verification.json`: final raw rebuild hashes, offline checks and review status.

Independent review corrected nuisance-rank handling, partial coefficient output,
capacity diagnostics/key audits, input path identity, strict product comparability,
support failure reporting, and fixed-climatology coverage. These are implementation
corrections, not post-holdout specification selection. The single warning in the
dummy-equivalence test is intentional: its reference model contains redundant
nuisance effects, while the tested implementation uses an independent basis.

No secrets, raw archives, local environment or temporary snapshots are tracked.
The user's pre-existing `.env.example` edit remains outside research commits.
