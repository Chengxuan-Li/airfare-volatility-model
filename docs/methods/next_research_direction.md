# Proposed next research direction — 2026-09-12

This note answers the user's questions about unused DOT history and irregular
operations. It proposes a next phase; no additional research data have been
acquired and no FR24 credits have been spent. The earlier Stage 5 stopping decision
concerns the original quote-time estimand, not exhaustion of DOT data.

## Actual scope and unused data

The fare study uses 2023 Q1 through 2025 Q2: ten quarters. It retains four reporting
carriers (AA, DL, UA, WN) and 42 directed routes among seven airports. National
Market/Ticket archives were streamed, but out-of-scope records did not enter the
models. Coupon was not acquired. T100 annual inputs cover 2023-25; the matched fare
analysis stops in 2025 Q2. Weather archives cover 2020-25, and the operational
validation uses seven airport-quarter series in 2023-24 from a 2022-24 delay-cause
extract. There is no flight-level irregular-operations model or FR24 client.

The [official DB1B profile](https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EFI&Yv0x=D)
lists quarterly data from 1993 through 2025. The
[BTS release table](https://transtats.bts.gov/releaseinfo.asp) identifies 2025 Q2 as
the last DB1B quarter. This verifies published coverage, not successful batch
acquisition of every historical archive. Most of that history remains unused here.

[BTS's O&D transition description](https://www.bts.gov/topics/airlines-and-airports/origin-and-destination-survey-data)
states that DB1B's quarterly 10% sample ended in July 2025 and DB1C's monthly 40%
sample began then. The [first DB1C release](https://www.bts.gov/newsroom/first-quarter-od40-data-live)
included July-September 2025. Treat this as a separate extension requiring field,
reporter, and sampling comparability checks; do not concatenate it unexamined.

## Recommended sequence

1. Fix the two acquisition/provenance defects recorded in the repository review.
   Preserve original input identities and verify only each pipeline's actual inputs.
2. Declare a broader aggregate study before examining new coefficients. A proposed
   first horizon is 2010-2025 Q2, with more airports and eligible reporting carriers
   selected using preperiod coverage, not coefficient signs. Audit every quarter's
   availability and schema before bulk acquisition. Use stable airport IDs and
   explicit carrier histories; separate pandemic and recovery regimes. Earlier
   1993-2009 data can follow after comparability and incremental value are assessed.
3. Add BTS flight-level on-time data as the primary realized-operations source.
   Preserve separate cancellation, diversion, arrival-delay and severe-delay
   outcomes with appropriate denominators and missingness/coverage audits. Aggregate
   by route/carrier/day and period for compatible analyses. Do not equate aircraft
   disruption with passenger misconnection, rebooking, or refund outcomes.
4. Separate risk prediction from fare association. A forward-looking disruption
   model should use forecast vintages and schedule information available at the
   stated prediction time, with temporal holdouts and calibration checks. A
   historical-risk model using lagged outcomes is a different, explicitly labelled
   design. Match each measure at its legitimate resolution; quarterly DB1B does
   not acquire missing fare timestamps merely by joining detailed operations data.
5. Use FR24 only for a bounded supplemental question, such as checking intended
   versus actual destinations or aircraft movement sequences during selected
   disruption episodes. Verify plan access, live balance, current credit costs and
   permitted retention before an authenticated call. The existing 6,000-credit cap
   remains a ceiling, not proof of available balance.
6. Reconcile the broader methods proposals: decide before estimation whether to
   add departure/supply outcomes and CR2/bootstrap sensitivities. More history and
   geographic coverage improve support and external validity, but cannot establish
   exogenous demand or the original quote-time mechanism on their own.

## FR24 role and limits

The [FR24 Flight Summary documentation](https://fr24api.flightradar24.com/docs/endpoints/flight-summary)
lists observed takeoff/landing times and intended/actual destinations; summary
coverage begins June 1, 2022, subject to access. These can support diversion and
movement checks. Its [FAQ](https://fr24api.flightradar24.com/docs/faq) says the API
does not supply scheduling information, and missing tracking can reflect source
coverage. Therefore an absent flight cannot alone be labelled cancelled, and
observed movement times alone cannot establish schedule delay. Compare like time
events when linking sources; takeoff time is not gate-departure time.

The current repository instead used BTS aggregate cancellation and delay outcomes
to validate a lagged weather index. It has not yet implemented the richer operation
measurement above. No claim of exhaustive DOT use or completed FR24 analysis is
warranted. See the [source check](../data/irregular_operations_source_check.md).
