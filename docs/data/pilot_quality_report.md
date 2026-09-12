# Real pilot: data quality and matching

Stage 3 / Stage 4A, 2026-09-12. Counts are from reproducible output audits.

## Inputs and retained sample

- Sixteen DB1B archives: Market and Ticket for each quarter of 2023-2024.
- Market rows scanned: 62,201,878; Ticket rows scanned: 38,083,334.
- Selected route/carrier scope before product and quality filters: 249,600 Market rows.
- Dollar-credibility exclusions: 1,098. Missing Ticket credibility: zero.
- Remaining 248,502 rows: 8,538 outside primary fare bounds; then 28,125 connecting
  market rows excluded. No additional nonfinite fare, invalid quantity, or bulk
  exclusions remained at their sequential filter steps.
- 211,839 valid Market rows before the minimum-cell-count rule; 266 cells.
- 44 cells with fewer than 30 sampled passengers were excluded, leaving 222 cells,
  211,651 contributing Market records, and 618,324 sampled passenger weights.
- Twelve directional routes, 29 observed route/carrier combinations, eight quarters.
  These passenger weights are not unique travelers or a full-population count.

The retained cell means range from USD144.05 to USD350.71; sampled passenger counts
range from 34 to 9,422. Every cell has observed fares and weather. The alternate
USD10-5000 fare bounds produce a separately labelled sensitivity sample.

## Duplicate and join audit

No duplicate year/quarter/MktID exists in the scoped Market data. Ticket join keys
are year/quarter/ItinID; duplicate selected Ticket keys would fail the pipeline.
Every scoped Market row matched a Ticket record, and the many-to-one join did
not expand Market rows. Shared column names are projected away so Ticket origin,
passengers, or bulk flags cannot overwrite Market attributes.

National rows outside the twelve routes and four reporting carriers are scope
exclusions, not missing fares. Absence of a carrier/route/quarter is not zero price
or zero demand. Balanced-support robustness retains only route/carrier groups
observed in all eight quarters; it does not establish joint risk/traffic overlap.

## Weather and outcome matching

Seven airports x eight quarters = 56 weather/outcome rows. Each prior source-year
quarter has 100% valid daily coverage. The index excludes target-year weather,
uses only prior three same-season windows, and records the latest valid date.
No endpoint risk is missing after matching to fare cells.

Operational validation uses 3,000 selected carrier-airport-month rows from BTS
Delay Causes, aggregated to airport-quarter. No duplicate keys or missing model
outcomes occur. The sum of five attributed delay-cause counts differs from the
reported delayed-flight count by at most 0.02, below the declared 0.05 rounding
tolerance. Cancellations, delays, and weather-delay counts satisfy denominator
checks. Weather delay attribution is not weather cancellation attribution.

## Source and selection limitations

Quarterly temporal resolution prevents exact flight identity, quote-time weather,
outcome matching to an individual ticket, DTD, inventory, or offered fare-product
comparison. Dollar credibility is a source flag, not proof of economic comparability.
Roundtrip composition is reported per quarter in the cleaning audit; it is not a
paired flexibility premium. National raw records are not deduplicated or audited
outside the declared scope, beyond period and schema checks.

Audit files: `outputs/tables/cleaning_audit.json`,
`outputs/tables/weather_matching_audit.json`, and
`outputs/tables/route_carrier_support.csv`. The last documents that only eight of
29 route/carrier groups span both pooled reference risk quartiles. Fitted curves
therefore require strong common-coefficient assumptions across groups.
