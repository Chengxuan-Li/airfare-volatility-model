# Full-year 2010 fare and operations panel

Date: 2026-09-12 America/New_York. Scope: the authorized
[2010 development milestone](../methods/stage6_2010_plan.md).

The full-year panel is built from all four 2010 DB1B Market/Ticket pairs and all
twelve 2010 reporting on-time months. It contains 3,191 primary route-quarter
cells and 3,193 broad-fare-bound cells across 30 selected airports. This is a
data and measurement milestone: no new fare model, forecast model or causal
estimate has been fitted.

## Data acquired and processed

Twenty archives total 811,733,928 compressed bytes. Three were reused from the
bootstrap; seventeen new downloads total 675,505,965 bytes. Eleven additional
operations HEAD checks all returned 200. Every consumed path, request and SHA-256
was verified; downloads also passed ZIP CRC validation. Exact acquisition outcomes
are in the [ledger](../../data/manifests/stage6_2010_acquisition_20260913T011738492971Z.json)
and [access inventory](../../data/manifests/stage6_2010_access_inventory.json).
Raw files and environments stay local and ignored. No paid services or FR24
requests/credits were used.

| Measure | Count |
| --- | ---: |
| National Market records scanned | 22,038,685 |
| National Ticket records scanned | 12,688,062 |
| National reported flights checked | 6,450,117 |
| Reported flights between selected airports | 2,100,986 |
| Scoped operations carrier-route-month cells | 17,324 |
| National operations carrier-month cells | 216 |
| Primary fare reporting-carrier-route-quarter cells | 27,343 |
| Broad fare reporting-carrier-route-quarter cells | 27,379 |

All twelve source months are present. Flight-key checks found no duplicates and
no missing eligible arrival delays in these inputs. Scoped Market keys and
matched Ticket itinerary keys were unique, and all 5,555,019 scoped Market rows
matched a Ticket row before fare exclusions. These successful checks do not prove
that all airlines, flights or passengers are covered by the reporting systems.

## Sample selection and carrier treatment

The sample was fixed by a rule committed before new acquisition: rank airports by
2010 Q1 sampled originating plus terminating passengers in domestic, nonbulk,
single-coupon Market rows with finite positive passenger weights; take the top 30
plus the original seven. Selection reads no fare or operational outcome field.
All seven original airports were already in the top 30. The
[ranking](../../outputs/stage6/annual_2010/airport_ranking.csv) preserves all 399
eligible airports and their baseline volumes. Ties use ascending airport ID.

Selected airports, in rank order: LAS, MCO, LAX, ORD, DEN, ATL, PHX, SFO, DFW,
JFK, FLL, LGA, BOS, EWR, SEA, PHL, BWI, MSP, TPA, DTW, SAN, MDW, IAH, DCA,
HNL, SLC, MIA, OAK, RSW and STL.

2010 is the selection/development year, not a temporal holdout. A winter-quarter
volume rule can favor seasonal markets and the selected network is not nationally
representative. Future evaluation should start after this selection year under
separately declared modeling and temporal-split rules.

Fare cells retain 36 nonmissing reporting-carrier codes; operations contain 18
DOT reporting-carrier IDs. They are not treated as the same carrier universe.
The joined panel aggregates each source independently across carriers and joins
on year, quarter and stable origin/destination airport IDs. Fare cells therefore
describe purchased Market components, while operational rates describe reported
flights on the route; the weights and covered carrier populations differ.

Airport ID/code aliases and on-time code/DOT-ID mappings are retained. Within this
scoped 2010 audit, no airport ID mapped to multiple codes, no code mapped to multiple
airport IDs and no operations code mapped to multiple DOT IDs. This is a
within-year check, not a validated carrier crosswalk for 2011-2025.

## Coverage and support

| Sample | Fare route-quarters | Matched operations | Fare only | Operations only |
| --- | ---: | ---: | ---: | ---: |
| Primary: USD 20-2000 | 3,191 | 2,904 | 287 | 0 |
| Broad bounds: USD 10-5000 | 3,193 | 2,904 | 289 | 0 |

The 2,904 matched primary cells represent 91.01% of fare route-quarter cells and
99.8458% of primary sampled passenger weights. Matching a route does not imply
complete carrier coverage within it. The 287 fare-only cells remain in the panel
with missing operational fields; absence is not coded as zero disruption.

Of matched route-quarters, 2,878 contain reported service in three months, eleven
in two months and fifteen in one month. `months_observed` records this distinction.
It cannot by itself separate entry/exit, seasonality or source coverage gaps.

Primary fares include 3,560,997 Market records and 11,922,823 sampled passenger
weights. There are 152 route-quarter cells below 30 passenger weights (18 matched
and 134 fare-only). At the more granular reporting-carrier level, 19,173 of 27,343
primary cells fall below 30. Low-support cells are retained and flagged, not
silently removed; future models must predeclare their support rule.

| Quarter | Primary fare cells | Matched cells | Sampled passenger weights | Reported scoped flights |
| --- | ---: | ---: | ---: | ---: |
| 2010 Q1 | 790 | 724 | 2,726,326 | 509,577 |
| 2010 Q2 | 802 | 732 | 3,053,956 | 527,353 |
| 2010 Q3 | 798 | 728 | 3,016,250 | 536,888 |
| 2010 Q4 | 801 | 720 | 3,126,291 | 527,168 |

The main sequential fare exclusions from 5,555,019 scoped rows are 1,863,350
connecting/unknown-coupon rows, 2,044 bulk/unknown-bulk rows, 18,628 unreliable or
missing-credibility Ticket rows and 110,000 rows outside primary fare bounds.
No additional rows were removed for foreign endpoints, invalid passenger counts,
unmatched Tickets or missing fares in this scoped annual input. Per-quarter and
broad-bound counts are preserved in the quality audit.

## Measurement and output dictionary

- `airport_ranking.csv`: baseline endpoint passenger volume, stable ID/code,
  deterministic rank and selection flag. Volume is sampled Market traffic.
- `fare_carrier_cells.csv`: period, endpoint IDs, reporting-carrier code and fare
  sample; passenger weights, records, weighted first/second fare totals, mean,
  population variance and `low_support` (fewer than 30 passenger weights).
- `operations_carrier_month.csv`: monthly stable endpoint and reporting-carrier
  identities, flight/outcome counts, delay sums and eligible denominators.
- `operations_national_month.csv`: all-route reporting-carrier monthly totals,
  retaining coverage outside the selected airports.
- `airport_aliases.csv` and `operations_carrier_identities.csv`: source-specific
  identity observations. Alias `period` means quarter for DB1B and month for on-time.
- `route_quarter_panel.csv`: independently aggregated fare moments and operations
  counts/rates, `coverage` status, observed service months and support flags.
  Both fare samples are separate rows; never sum operational counts across them.
- `quality_audit.json`: selection exclusions, four fare audits, twelve operations
  audits, identities, source completeness and outer-join counts.

Cancellation/diversion rates divide by all reported flights. Delay rates and mean
arrival delay use observed arrivals that are neither cancelled nor diverted;
thresholds include 15 and 60 minutes, and mean delay retains negative early arrivals.
Quarterly numerators and denominators are summed before rates are computed.
Missing denominators yield missing rates. Fare moments are passenger weighted;
Market fares are nominal prorated itinerary components, not timestamped quotes.
Traffic remains jointly determined with prices. No quote-time risk is inferred.

## Verification and reproduction

The pinned Python 3.13.9 environment passes 100 offline tests, including a real
twenty-archive fixture, duplicate/period/identity checks, weighted rates, empty
fare samples, provenance rejection and output-publication rollback. One expected
Stage 5 rank-deficiency reference warning remains. Two successful full raw builds
produced eight byte-identical derived files, and all twenty input checksums were
reverified. The [verification record](../../outputs/stage6/annual_2010/verification.json)
contains input, output and source hashes with implementation commit `96e0c31`.
Independent code/spec review found no material issues. Earlier Stage 0-5 and
bootstrap output files remain unchanged.

The first real build attempt exposed a pandas mixed-type parsing error in 2010 Q1
Market after 4,750,000 rows. The numeric-looking carrier token `16` occurred in
57,963 rows alongside 35 alphanumeric tokens. Explicit text-field parsing now
preserves carrier tokens, including leading zeros, and reads the complete file.
The failed attempt published no output and is retained in the
[execution ledger](../status/execution_ledger.md).

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m src.stage6.annual --acquire
.\.venv\Scripts\python.exe -m src.stage6.annual
.\.venv\Scripts\python.exe -m pytest -q
```

The acquisition command targets exactly these twenty 2010 archives and verifies
caches. Missing raw must match committed request identities/checksums on
reacquisition. Existing raw without a manifest is rejected. The build checks every
input before replacing results. Complete directories publish with rollback on
rename failure; previous output sets remain in ignored sibling backup directories.
A rerun replaces the current derived set, so an old verification record is retained
with the previous set rather than attached to a new unverified build.

## Next milestone

Apply the fixed airport IDs to an audited 2011 batch, checking coverage and carrier
identities before scaling remaining years through 2025 Q2. The current annual
runner intentionally targets 2010 only; parameterizing later batches is the next
implementation step. Preserve partial service and unbalanced entry/exit rather than
requiring future survival as a selection criterion.

Capacity, compatible historical or forecast-vintage risk, departure/supply outcomes,
CR2/bootstrap inference and new fare models remain deferred. More quarterly history
improves descriptive coverage but cannot recover the missing quote-time information.
FR24 remains unused and supplemental; source gaps here are not a reason to label
missing tracks cancellations or spend credits without a specific validated purpose.
