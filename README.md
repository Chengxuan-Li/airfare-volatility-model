# Airline weather-risk pricing research

This preliminary research project asks whether operational/weather risk changes
the relationship between airline fares and demand. No empirical results have
been established. The current task is to verify batch access to BTS DB1B before
starting research Stages 0-4.

BTS DB1B is the selected fare source. Its quarterly observations support an
aggregate design, but do not supply the quote timestamps required by the original
flight-level ex-ante forecast hypothesis. Any redesign must be explicit.

Start with [the documentation index](docs/INDEX.md),
[project state](docs/project_state.md), and
[the research task](docs/20260912_airline_weather_pricing_research_task.md).
Agent and Git rules are in [AGENTS.md](AGENTS.md).

## Reproduction and data

See [BTS batch download instructions](docs/data/bts_db1b_batch_download.md).
Raw files remain local under ignored `data/raw/`; acquisition manifests are
tracked under `data/manifests/`. No analysis pipeline exists yet.

For optional Flightradar24 access, copy `.env.example` to `.env` on a new machine
and add credentials only to `.env`. See [credential setup](docs/data/api_credentials.md).
No additional paid services are authorized.
