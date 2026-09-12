# Pilot data dictionary

The published aggregate panel is `outputs/tables/pilot_panel.csv`. No individual
synthetic or reconstructed fare observations are used. Raw national ZIPs and
weather responses remain local; manifests identify source bytes and retrievals.

| Field | Definition |
| --- | --- |
| Year, Quarter | BTS travel reporting period; not quote/booking date |
| Origin, Dest | Directional airport pair; nonstop Market rows only |
| RPCarrier | BTS reporting carrier (AA, DL, UA, WN in scope) |
| passengers | Sum of sampled passenger counts after record filters; not total market demand |
| records | Number of retained DB1B Market rows contributing to a cell |
| fare_mean | Sum(MktFare * Passengers) / sum(Passengers), nominal USD |
| fare_variance | Weighted second raw moment minus squared mean, USD squared |
| sample | primary USD20-2000 bounds or broad_fare_bounds USD10-5000 |
| origin_risk, destination_risk | Same-calendar-quarter adverse-day share from prior three years |
| risk | Equal-weight arithmetic mean of endpoint risks |
| risk_max | Maximum endpoint risk, alternate construction |
| origin_cancel_rate, destination_cancel_rate | Realized airport-quarter cancelled arrivals / reported arrivals |
| route | Origin-Dest cluster key |
| route_carrier | Route and reporting carrier fixed-effect key |
| period | Year-quarter calendar fixed-effect key |

Risk is dimensionless; a change of .10 is ten percentage points. It is a
retrospectively computed historical-season exposure, not a quoted-flight forecast.
Weather data: Open-Meteo, ERA5 via Copernicus/ECMWF, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Changes made: threshold daily components and aggregate historical seasons/endpoints.
Coordinates: [OurAirports public-domain registry](https://ourairports.com/data/).

`airport_weather_validation.csv` contains one row per airport/year/quarter:
historical risk, pooled and minimum-source-year coverage, valid/expected day
counts, actual latest valid selected date, requested grid coordinates/timezone,
realized adverse-weather share, counts and rates for cancellations and delays.
Weather-attributed delay counts describe delayed flights, not weather cancellations.

`cleaning_audit.json` reports national scanned rows, scope restrictions, missing
grouping values, Market duplicate IDs, period-scoped Ticket join coverage,
unknown/unreliable dollar credibility, sequential fare/product exclusions,
roundtrip passenger composition, and low-count cell exclusions. Raw Market rows
with duplicate period/MktID fail the run; Ticket keys must be many-to-one.

Thresholds: nonbulk, one market coupon, positive finite passengers, finite fare
within declared bounds, credible Ticket dollars, at least 30 sampled passengers
per cell. Missing Ticket matches are excluded and audited. Other ticket attributes
are not treated as equivalent offered fare products.
