# Fare-data feasibility

## Finding

The original flight/quote design is not feasible with the selected BTS DB1B
data. DB1B is a quarterly sample of used passenger tickets. It has no query or
purchase timestamp, days to departure, flight number, scheduled departure,
search session, contemporaneous offered inventory, or comparable
Basic/Standard/Flex quotes. A quarter is not a quote date. No coefficient from
the aggregate pilot may be described as the original flight-level ex-ante
pricing effect.

DB1B nevertheless supports a real descriptive redesign. BTS defines DB1B as a
10% sample used for traffic patterns, carrier shares, and passenger flows. Its
[Market field page](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FHK)
defines `Passengers`, the bulk-fare indicator, carrier fields, airport fields,
and `MktFare`; importantly, `MktFare` is `ItinYield * MktMilesFlown`, a prorated
market fare. It is not necessarily a separately offered one-way fare.

## Aggregate pilot estimand

Use directional airport-pair x reporting or ticketing carrier x quarter cells.
Construct passenger-weighted mean and median-like/trimmed fare summaries,
traffic, carrier share, and dispersion where cell sizes permit. The estimand is
an association between aggregate realized ticket fares, realized traffic, and a
predetermined risk proxy. It does not identify airline beliefs at purchase time
or a causal demand curve.

Keep direction because endpoint exposure and market composition can differ.
Include route, carrier, year-quarter, and direction controls as the final model
allows; report how much identifying variation remains after fixed effects.
Deflate fares with a predeclared price index if values are compared across
years. Do not use quarter labels as if every ticket were purchased or flown on a
single date.

## Ticket/Market filtering plan

Acquire matching DB1B Ticket quarters before final cleaning. Audit the embedded
BTS readme and actual headers before coding filters. At minimum:

1. restrict to domestic itineraries/markets and the frozen pilot airports;
2. exclude or separately report bulk-fare records rather than mixing negotiated
   bulk transactions into the public-fare interpretation;
3. require BTS dollar-credibility where available and positive, plausible fare
   and distance values; publish thresholds and a no-trimming sensitivity;
4. harmonize round-trip and one-way interpretation explicitly; never divide a
   fare by two without confirming the relevant itinerary structure;
5. distinguish online/single-carrier from interline and carrier-change
   itineraries; use a narrower online sample as the primary carrier analysis if
   joins are reliable;
6. use `ItinID`/`MktID` only within year-quarter and verify join cardinality,
   duplicates, and passenger weights; IDs are not assumed globally unique;
7. retain both airport codes and stable DOT airport/city-market IDs, and record
   any city-market consolidation.

The already verified 2024 Q1/Q2 Market archives have a blank trailing CSV
column. Cleaning must handle it deliberately. Stream the compressed CSVs and
filter early; their uncompressed sizes exceed 1.8 GB and 2.1 GB.

## Coverage boundary and successor

The [BTS transition page](https://www.bts.gov/topics/airlines-and-airports/origin-and-destination-survey-data)
states that quarterly 10% DB1B collection ended in July 2025 and monthly 40%
DB1C began then. The [O&D40 description](https://www.bts.gov/OD-40) records
material changes: reporting carrier, sample rate, frequency, coverage, and new
fields including scheduled travel month. The last DB1B quarter is therefore
2025 Q2. DB1C is a successor, not a drop-in continuation; the 2023-2024 pilot
avoids this break.

## Why other quote approaches are not used

No public historical quote archive with lawful, reproducible access and the
required product attributes was verified. Live airline/OTA/Google Flights
collection begun now cannot recreate 2023-2024 query-time states, and automated
access would require source-specific terms review and potentially access-control
issues. Commercial fare feeds would add cost and still require historical
coverage verification. The task prohibits new purchases. These are reasons to
bound the conclusion, not reasons to relabel DB1B.
