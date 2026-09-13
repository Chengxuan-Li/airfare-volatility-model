# Irregular-operations source check — 2026-09-12

## What has and has not been used

The project has **not** used the full DOT operational-data horizon. Its fare panel
covers 2023 Q1–2025 Q2, while operational validation uses a BTS Delay Causes
aggregate for seven airports in 2023–2024. T-100 supplies realized route-quarter
capacity for 2023–2025. No flight-level on-time records were acquired or modeled.
Flightradar24 (FR24) usage remains zero calls and zero credits; there is no FR24
client in the repository.

## BTS flight-level source

The official [Reporting Carrier On-Time Performance profile](https://www.transtats.bts.gov/TableInfo.asp?QO_fu146_anzr=b0-gvzr&gnoyr_VQ=FGJ)
describes individual non-stop domestic flight records from 1987 through the
present; on 2026-09-12 it listed June 2026 as the latest month. This is the
appropriate primary source for realized U.S. irregular operations, subject to
reporting-carrier coverage and changes over time.

The official [field table](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FGJ)
separates scheduled gate times (`CRSDepTime`, `CRSArrTime`) from actual gate times
(`DepTime`, `ArrTime`), plus wheels-off/on times and delay minutes. It directly
identifies `Cancelled`, `CancellationCode`, and `Diverted`; diversion detail
includes diverted airports and whether the flight eventually reached its scheduled
destination. Delay-cause minutes begin in June 2003 (carrier, weather, NAS,
security, late aircraft), and gate-return/diversion detail begins in October 2008.
The [current BTS reporting directive](https://www.bts.gov/explore-topics-and-geography/modes/aviation/number-40-technical-directive-reporting-time)
defines cancellation causes as carrier, weather, NAS, or security.

These fields measure flight operations. A cancelled or diverted flight is not a
count of disrupted passengers, misconnections, rebookings, refunds, or final
itinerary completion. Delay/cancellation cause codes are reported operational
attributions, not passenger-level causal effects.

## FR24 capability and boundary

The official [Flight Summary documentation](https://fr24api.flightradar24.com/docs/endpoints/flight-summary)
lists observed takeoff/landing times and intended and actual destinations, useful
for selected diversion or movement checks. Summary availability begins
2022-06-01, returned fields may be null, results are capped, plan history limits
apply, and historical records consume credits.

FR24's [FAQ](https://fr24api.flightradar24.com/docs/faq) says the API does not
provide schedules: a flight appears live only after its aircraft transmits and is
captured. It also says missing historical aircraft can reflect either inactivity
or source-coverage limits. Therefore, absence from FR24 cannot by itself establish
cancellation, and observed takeoff cannot be compared with a nonexistent FR24
scheduled gate-departure time to measure delay.

## Recommendation

For the next declared extension, acquire bounded BTS flight-level months first and
build separate cancellation, diversion, arrival-delay, and severe-delay outcomes
with explicit denominators and coverage audits. Use FR24 only for a predeclared,
small supplemental validation that BTS cannot answer, after verifying balance,
cost, plan access, and retention terms. Neither source restores DB1B quote timing
or identifies passenger disruption by itself.
