# Research charter

Date: 2026-09-12. Stage 0, specified before empirical estimation.

## Question and designs

Original question: does operational/weather risk known at the time an airline
quotes a fare raise price at a reference demand state while flattening the
demand-to-price relationship? That design requires timestamped quotes, defensible
demand signals, and forecast vintages available at those timestamps. DB1B lacks
the timestamps, so the original test is not identified by the selected data.

The executable pilot asks a narrower descriptive question: across quarterly
route/carrier cells, how do passenger-weighted prorated DB1B market fares covary with
sampled passenger traffic and historical seasonal airport weather exposure?
This is an aggregate association, not a causal demand curve or quote-time test.

Options considered: (1) seek live fare APIs, requiring unavailable credentials
and prospective sampling; (2) stop after feasibility; (3) build a real DB1B pilot
with explicit aggregate limitations. User selected DB1B and authorized option 3.
Do not spend Flightradar24 credits to compensate for absent fare timestamps.

## Pilot scope and measurement

- Initial period: 2023 Q1 through 2024 Q4, before inspecting regression signs.
- Twelve directional markets: ORD, DEN, DFW to ATL, LAX, JFK, SEA. Retain the
  reporting-carrier cells with at least 30 sampled passengers per quarter.
- Primary product: nonstop domestic markets; analyze reporting carriers AA, DL,
  UA, WN where observations exist. An absent carrier/route cell is not zero fare.
- P: passenger-weighted DB1B market fare in nominal USD; log-price robustness.
- D: log sampled passengers per route/carrier/quarter, centered at the analysis
  sample mean. This is observed traffic, jointly determined with price, not
  exogenous demand. It does not measure price elasticity of demand.
- R: mean origin/destination share of adverse-weather days in the same calendar
  quarter during the preceding three calendar years, computed separately for
  each target year. Thresholds: daily precipitation >=10 mm, snowfall >=5 cm,
  or maximum 10m wind >=15 m/s. Equal airport weights; fraction in [0,1].
- Weather source feasibility may require revision; document any revision before
  fitting. A retrospectively retrieved weather archive has vintage limitations:
  historical dates alone do not prove exact availability to a quoting airline.
- Basic controls: route/carrier fixed effects and year-quarter fixed effects;
  a route + carrier alternative is descriptive. DTD and flight fixed effects
  cannot be recovered and will not be invented. Distance is absorbed by route FE.
- Market/Ticket join: year, quarter, ItinID. Use Ticket dollar-credibility and
  roundtrip fields if downloadable; audit uniqueness and row expansion.

## Identification and competing mechanisms

Weather can shift traveler demand, supply, reliability, schedules, and product
composition. Fare and traffic are jointly determined; capacity and competition
are incompletely controlled. Seasonal route composition can mimic an interaction.
Reporting-carrier measures may differ from marketing/operating carrier measures.
Aggregating itinerary fares and flights to quarters introduces ecological bias.

The pilot can establish source feasibility, data quality, descriptive signs, and
sensitivity. It cannot establish airline pricing policy, a structural fare floor,
the original weather-forecast response, or causality. Null or reversed results
remain valid outcomes. The final recommendation concerns investment in better
data, not whether coefficients can be made to match expectations.

## Engineering and delivery

Use small Python modules for acquisition, cleaning, risk construction, and
analysis. Raw downloads are ignored, checksummed, and manifested. Stream ZIP CSVs
in chunks; publish compact aggregate outputs, source definitions, and audits.
Use targeted tests for weighting, exclusions, keyed joins, time leakage, missing
weather, and model rank. Commit by stage; do not touch the user's template edit.
No additional paid services; initial Flightradar24 cap remains 6,000 credits.
