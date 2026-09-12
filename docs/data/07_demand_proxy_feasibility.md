# Demand-proxy feasibility

## Finding

No observed variable in the selected historical data is an exogenous demand
state. DB1B `Passengers` is realized traffic on sampled, used tickets. It is
jointly determined by preferences, fares, capacity, schedules, competition, and
disruptions. Calling it simply "demand" would overstate what is measured.

For the aggregate pilot, name the variable **observed passenger quantity** or
**traffic**, and interpret its interaction with risk descriptively. A positive
fare-traffic slope under low-risk conditions is a construct-validity check, not
proof that traffic identifies a demand shock.

## Candidate measures

| Candidate | Strength | Main problem | Use |
| --- | --- | --- | --- |
| DB1B passenger-weighted route/carrier/quarter traffic | Same records as fare; true transported ticket sample | Simultaneous with price; 10% sample; itinerary/reporting composition | Primary descriptive quantity |
| DB1B carrier share | Captures route competitive position | Price and capacity jointly determine share | Control/sensitivity |
| [T-100 Domestic Segment](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=GEE) passengers | Monthly census-style carrier segment traffic | Realized quantity, not latent demand; segment differs from itinerary market | External traffic check/control |
| T-100 seats and load factor | Capacity utilization and supply context | Both capacity and bookings are endogenous; aggregate cabin/service classes | Capacity robustness, never an instrument by default |
| T-100 departures scheduled/performed | Service intensity | Airline supply decision and disruption outcome | Supply control/context |
| Days to departure, booking velocity, fare buckets, remaining inventory | Close to the original construct | Absent from DB1B/T-100 | Unavailable historically |
| Holidays, calendar, route seasonality | Predetermined demand shifters | Coarse and may also affect operations | Controls; potential instruments only with a separate exclusion argument |

BTS explains that T-100 is monthly carrier-reported market/segment traffic. Its
[database profile](https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EEE&Yv0x=D)
also states that segment data contain passengers, available capacity, scheduled
and performed departures, and load factor. Market passengers are enplaned and
segment passengers are transported per leg, so route definitions must be
matched carefully rather than merged by airport pair without an audit.

## Validation strategy

1. Freeze the route set, carrier definition, aggregation, weights, exclusions,
   and minimum cell sizes before outcome analysis.
2. Under the lowest-risk tercile, estimate whether the within-route/carrier
   fare-traffic association is positive. Failure weakens the proposed proxy and
   should be reported; it does not automatically falsify airline revenue
   management.
3. Compare DB1B quarterly traffic movements with aggregated T-100 monthly
   passenger movements for compatible nonstop route/carrier cells. Report
   coverage gaps and correlations, not equality.
4. Re-estimate with lagged traffic, carrier share, seats, departures, and load
   factor as separately labelled controls/sensitivities. Lagging reduces direct
   simultaneity but does not make traffic exogenous.
5. Test whether results are driven by thin cells, a carrier, a hub, COVID-era
   recovery, or seasonal route entry/exit.
6. Never use realized cancellation or current-quarter weather as a demand
   instrument. Both can change capacity, passenger completion, and measured
   traffic directly.

The interaction coefficient in this pilot describes how the fare-traffic
association varies with predetermined operational climate. Causal demand-to-
price transmission remains unidentified without a defensible demand shifter or
inventory/booking data.
