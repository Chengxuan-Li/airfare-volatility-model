# Airline weather-risk pricing research

This project investigates whether weather/operational risk changes the relation
between airline fares and demand. The Stage 0-4 assessment uses a real quarterly
BTS DB1B pilot. Original flight/quote-time hypotheses are **not estimable** from
these data; all aggregate results are descriptive.

The pilot contains 222 route/carrier/quarter cells on twelve routes in 2023-2024.
The aggregate risk coefficient is negative and the interaction positive, opposite
the proposed signs. Recommendation: **C — interesting empirical observation,
weak paper**. Endogenous traffic, few clusters, and limited joint support prevent
causal or confirmatory claims. See the [consolidated report](docs/findings/stage_0_to_4_report.md)
and [project state](docs/project_state.md) for verification status and limitations.

## Reproduce

Python 3.13 was used on Windows. Run from the repository root with curl installed.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.acquisition.batch --kind all
.\.venv\Scripts\python.exe -m src.run
```

On other platforms use the environment's Python executable. Acquisition is public
and requires no API credentials. It downloads Market and Ticket for eight quarters,
seven weather responses, airport coordinates, and a small BTS delay-cause archive.
Raw inputs total about 1.59 GB compressed/on disk, and national CSVs are streamed
in chunks. Downloads have finite timeouts and verified caches; a failed request
stops that batch. See [download notes](docs/data/bts_db1b_batch_download.md) and
[execution ledger](docs/status/execution_ledger.md) for the bounded resume procedure.

The default run verifies input checksums, rebuilds the fare aggregates from raw,
matches weather/outcomes, and recreates tables/figures. `python -m src.run --analysis-only`
reuses the saved fare-cell CSV for review. Both paths use identical round-trip
float parsing. Raw inputs are ignored; acquisition manifests and compact outputs
are tracked. A source revision or unavailable endpoint may require reacquisition
review; manifests protect the exact local data used here.

## Contents and interpretation

- [Documentation index](docs/INDEX.md), [agent rules](AGENTS.md), and
  [research specification](docs/20260912_airline_weather_pricing_research_task.md).
- `src/`: acquisition, cleaning, seasonal exposure, and checked exploratory models.
- `tests/`: offline weighting, key, coverage, cache, and inference-safety tests.
- `data/manifests/`: provenance and SHA-256; `outputs/`: aggregate tables and figures.
- [Data dictionary](docs/data/data_dictionary.md), [quality audit](docs/data/pilot_quality_report.md),
  and [methods](docs/methods/aggregate_analysis.md).

DB1B market fares are prorated components of sampled ticket itineraries, not
timestamped quotes. Sampled passenger counts are equilibrium traffic, not exogenous
demand. Historical seasonal weather is computed from retrospectively retrieved
ERA5, not a quote-time forecast vintage. No flexibility premium is inferred.

## Sources and access

BTS TranStats supplies fare and operational data. Weather is from
[Open-Meteo](https://open-meteo.com/) using ERA5/Copernicus/ECMWF, under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); this project thresholds and
aggregates the daily values. Airport coordinates are
[OurAirports public-domain data](https://ourairports.com/data/).
See [source constraints](docs/data/09_data_legal_technical_constraints.md).

No paid services were added, and no Flightradar24 calls or credits were used.
Optional future FR24 access uses ignored `.env`; never put a key in `.env.example`.
The initial-pass ceiling remains 6,000 credits within the reported 60,000 monthly
allocation. See [credential and budget notes](docs/data/api_credentials.md).
