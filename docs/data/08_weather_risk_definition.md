# Weather and operational-risk definition

## Required distinction

The original construct is the weather/operational risk known when a fare was
quoted. The selected fare data have neither quote dates nor departure dates, so
that construct cannot be aligned directly. Realized weather during a quarter is
not a valid replacement: it is observed after many pricing decisions and can
directly affect cancellations, capacity, and completed traffic.

The aggregate pilot therefore uses a separate, rigorously labelled measure:
**strictly lagged seasonal airport weather risk derived retrospectively from a
reanalysis archive**. It approximates persistent, historically knowable
seasonal operating climate. It is not an archived airline forecast or a measure
of the exact information set used by a revenue-management system.

## Primary construction

Download daily data for 2020-2024 at ATL, LAX, JFK, SEA, ORD, DEN, and DFW from
the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).
The implemented pilot requests ERA5 consistently, airport coordinates from the
OurAirports public-domain registry, local timezone (`timezone=auto`), daily
precipitation in mm, snowfall in cm, and maximum 10m wind in m/s.

An adverse day has precipitation >=10 mm OR snowfall >=5 cm OR wind >=15 m/s.
These transparent exploratory thresholds were fixed in Stage 0 before outcome
estimation; they are not claimed to be certified airport operating limits.
All three components must be observed; an unknown component yields a missing day.
For target year y and quarter q, risk is the adverse-day share in that same
quarter in y-3, y-2, y-1. Each historical year-quarter must have >=95% calendar-day
coverage. The target year is excluded. Report the actual latest valid input date.

Route risk is the arithmetic mean of endpoint risks; maximum endpoint risk is a
sensitivity. Missing endpoints propagate rather than being silently averaged away.
This construction replaces candidate gust/temperature/standardized-component
indices considered during source assessment. No weights or thresholds are fitted
to cancellations or fare coefficients. Components and missingness are audited.

## Forecast-vintage alternatives

Open-Meteo documents four distinct products:

- Historical Weather is reanalysis/modelled past conditions; it is suitable for
  climate summaries, not quote-time forecasts.
- Historical Forecast stitches the first hours of successive forecast runs. It
  tracks realized conditions closely and does not by itself preserve a chosen
  lead time.
- [Previous Runs](https://open-meteo.com/en/docs/previous-runs-api) returns fixed
  1-7 day lead fields and generally begins in January 2024. A 2024-01-15 ORD
  request for temperature, precipitation, and wind gust at a three-day lead
  succeeded with 24 hourly rows. This is a real ex-ante forecast-vintage option,
  but DB1B supplies no purchase/departure date to align it to fare observations.
- Single Runs preserves initialization time and full forecast horizons, but most
  model coverage begins in 2026; Open-Meteo lists ECMWF IFS HRES from March 2024.

NOAA/NCEI also provides [historical numerical weather prediction archives](https://www.ncei.noaa.gov/products/weather-climate-models),
including GFS analysis and forecasts. These are the stronger government-native
fallback when exact initialization and lead time are essential, but their large
gridded files and model-version harmonization are disproportionate to this
quarterly pilot. NOAA's ordinary `api.weather.gov` endpoint serves current
forecasts and is not a general historical forecast-vintage API.

## Operational validation, not risk construction

Validate airport-quarter risk against subsequent/target-quarter realized
outcomes from BTS Delay Causes: cancellation rate
`sum(arr_cancelled) / sum(arr_flights)`, diversion rate, arrival-delay rate, and
cause counts. Check that the components and denominator reconcile before
aggregation. Use only the frozen lagged score as predictor. Report
rank correlations/calibration plots with year-quarter and airport context; do
not tune component weights until the same outcomes fit well and then report the
fit as out-of-sample.

BTS's included workbook defines `weather_ct` as the weather count for the airline
cause of delay. The public page explains that causes assigned to delayed flights
are prorated based on responsible delay minutes. Thus `weather_ct` does not
identify the cause of cancellation. BTS also notes that "extreme weather" is a
carrier-assigned cause, while National
Aviation System delay also contains nonextreme weather, airport operations,
traffic volume, and air traffic control. Cancellation is not uniquely weather-
caused in the small aggregate file. Validation therefore tests operational
predictiveness, not a clean weather causal channel.
