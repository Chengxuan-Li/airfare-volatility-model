# Stage 5 source extensions

Checked 2026-09-12. This note records bounded, anonymous access tests for a
route-level supply extension and for the last two DB1B quarters. No archive body
was retained during these tests. The machine-readable request recipe is
[stage5_requests.json](stage5_requests.json).

## Decision

Use **T-100 Domestic Segment (All Carriers)** to construct route-direction by
quarter supply controls for all 42 non-self directions among ATL, DEN, DFW, JFK,
LAX, ORD, and SEA. Restrict to `Class == "F"`, then sum `Seats`, `Passengers`,
`DepScheduled`, and `DepPerformed` across every carrier, aircraft type, and month
in the route-quarter. The [official T-100 field page](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=GEE)
defines these as available seats, non-stop segment passengers transported,
scheduled departures, and performed departures. The [official database
description](https://www.transtats.bts.gov/DatabaseInfo.asp?QO_VQ=EEE&Yv0x=D)
describes monthly non-stop segment records by aircraft type and service class.

This produces observed route supply and traffic controls, not exogenous demand.
Seats and departures are airline choices and can respond to expected demand,
fares, season, and weather. `Seats` measures available seats on operated service;
it is not scheduled seats on cancelled flights. Preserve
`DepScheduled - DepPerformed` as a service-completion diagnostic and compute
`Passengers / Seats` only after summing numerators and denominators. Audit zero,
missing, and impossible values before any ratio.

## Why all-operator aggregation is required

The current DB1B market cells use `RPCarrier`, a reporting-carrier field. T-100
segment carrier identity and DB1B Coupon `OpCarrier` describe different roles,
especially for code shares and regional affiliates. Joining T-100 carrier rows
directly to DB1B `RPCarrier` would therefore omit or misassign operated capacity.

Retain `UniqueCarrier` in the raw T-100 extract for coverage audits, but aggregate
over all operators before joining to the fare panel. Join only on `Origin`,
`Dest`, `Year`, and `Quarter`. The resulting supply variables are shared by all
DB1B carrier cells in a route-quarter. They cannot explain within-route-quarter
carrier differences or be called a carrier-specific capacity measure. A later
carrier-specific design would need an explicit, validated reporting/marketing/
operating-carrier crosswalk; code equality is insufficient.

## T-100 access test and exact fields

The official [TranStats download form](https://www.transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=Nv4+Pn44vr45&gnoyr_VQ=GEE)
requires an ASP.NET session and current hidden form tokens. Guessed static files
named `T_100_Domestic_Segment_All_Carrier_2023.zip`, `_2024.zip`, and `_2025.zip`
all returned HTTP 404. They must not be treated as endpoints.

The reproducible flow is:

1. `GET` the form in a session and capture `__VIEWSTATE`,
   `__VIEWSTATEGENERATOR`, and `__EVENTVALIDATION`.
2. In the same session, `POST` those values plus
   `__EVENTTARGET=chkDownloadZip`, an empty `__EVENTARGUMENT`,
   `cboYear=<year>`, `cboPeriod=All`, and `chkDownloadZip=on`. Capture the new
   hidden values from the returned form.
3. `POST` the refreshed values, year/period, `chkDownloadZip=on`,
   `btnDownload=Download`, and these checkbox names:
   `UNIQUE_CARRIER`, `ORIGIN_AIRPORT_ID`, `ORIGIN`, `DEST_AIRPORT_ID`, `DEST`,
   `YEAR`, `QUARTER`, `MONTH`, `CLASS`, `PASSENGERS`, `SEATS`,
   `DEPARTURES_SCHEDULED`, and `DEPARTURES_PERFORMED`.

Metadata-only streamed tests of that exact extract returned:

| Selection | Status/type | `Content-Length` | Response filename at test time |
| --- | --- | ---: | --- |
| 2023, All Months | 200, `application/zip` | 3,657,693 | `T_T100D_SEGMENT_ALL_CARRIER_20260912_070133.zip` |
| 2024, All Months | 200, `application/zip` | 3,782,321 | `T_T100D_SEGMENT_ALL_CARRIER_20260912_070151.zip` |
| 2025, All Months | 200, `application/zip` | 3,938,181 | `T_T100D_SEGMENT_ALL_CARRIER_20260912_065742.zip` |

The response filename is generated at request time and is not a
persistent PREZIP URL. The 2025 year and all twelve period choices were present
on the official form, and the annual request succeeded, so it covers the needed
2025 Q1-Q2 selection. The full acquisition must still assert that months 1-6
exist before reporting the extension. The [BTS release page](https://transtats.bts.gov/releaseinfo.asp)
also lists T-100 Domestic Segment (All Carriers) as an actively maintained table.

The official 744-byte [service-class lookup](https://www.transtats.bts.gov/Download_Lookup.asp?Y11x72=Y_fReiVPR_PYNff)
returned HTTP 200 and defines `F` as “Scheduled Passenger/ Cargo Service F.” It
separately defines `G` as scheduled all-cargo and the `L`, `N`, `P`, `Q`, `R`,
and `V` families as non-scheduled services. `Class == "F"` is therefore the
appropriate primary scheduled-passenger filter. Preserve a class frequency
table and report any scheduled passenger records under legacy classes `A`, `C`,
or `E` as a sensitivity rather than silently pooling them.

## DB1B 2025 and Coupon checks

Anonymous HEAD requests returned HTTP 200 for all five official PREZIP files:

| Table/period | Bytes | Last modified (GMT) |
| --- | ---: | --- |
| [Market 2025 Q1](https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BMarket_2025_1.zip) | 94,587,240 | 2025-06-27 20:19:03 |
| [Market 2025 Q2](https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BMarket_2025_2.zip) | 110,296,405 | 2025-10-06 12:49:08 |
| [Ticket 2025 Q1](https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BTicket_2025_1.zip) | 90,024,798 | 2025-06-27 20:20:54 |
| [Ticket 2025 Q2](https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BTicket_2025_2.zip) | 103,345,558 | 2025-10-06 12:51:14 |
| [Coupon 2024 Q1](https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BCoupon_2024_1.zip) | 223,500,145 | 2024-06-28 14:38:53 |

The 2025 Market and Ticket files permit a same-regime Q1-Q2 extension. They do
not remove the documented DB1B-to-DB1C break after June 2025, and 2025 Q1-Q2
must not be described as post-transition data.

Coupon can identify the ticketing, operating, and reporting carrier roles and
the coupon path, but it does not restore query time, offer inventory, or product
bundle attributes. The [current DB1B Coupon field page](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FLM)
is decisive about `FareClass`: its value is carrier-defined, may not follow the
same standard, and is “Not Recommended For Analysis.” The official [DB1B record
description](https://www.bts.gov/sites/bts.dot.gov/files/DB1B_Record_Description_Product%20for%20bookstore.pdf)
documents historical codes `F` unrestricted first, `G` restricted first, `C`
unrestricted business, `D` restricted business, `Y` unrestricted coach, `X`
restricted coach, and `U` unknown. Those labels are documentation, not evidence
of comparable modern Basic/Standard/Flex products. Do not estimate a flexibility
premium from them. If Coupon is acquired, use the codes only for descriptive
quality checks, publish carrier/quarter code frequencies, and join within
year-quarter using audited `ItinID`/`MktID` cardinality.

## Implementation and validation contract

- Filter the streamed T-100 CSV early to both endpoints in the seven-airport set,
  unequal endpoints, years 2023-2025, and `Class == "F"`.
- Save raw archives only under ignored data storage. Record the final request
  time, response headers, SHA-256, archive member name, member size, ZIP CRC
  result, exact header, and row counts by year/month/class.
- Assert 2025 months 1-6 and every expected route-quarter key used by the DB1B
  panel. Preserve unmatched DB1B and T-100 keys in an audit table; do not impute
  capacity to an absent key.
- Sum before ratios. Suggested fields are `t100_seats`, `t100_passengers`,
  `t100_dep_scheduled`, `t100_dep_performed`, `t100_load_factor`, and
  `t100_completion_rate`. Label all of them realized outcomes.
- Compare primary estimates with and without these controls. Their inclusion is
  a sensitivity for observed supply, not a cure for quantity endogeneity or a
  source of causal identification.
- Year-quarter fixed effects already absorb common national price-level changes,
  so no BLS CPI request is required for this extension. Deflation would remain
  useful for descriptive dollar levels across time, but it is lower priority
  than correct route supply and carrier-role handling.

No credentials, paid API, or Flightradar24 credits were used. The FR24 ledger
remains at zero calls and zero credits against the unchanged 6,000-credit cap.

## Coordinator acquisition update

The coordinator subsequently downloaded and CRC/SHA-256 validated all three
extracts. Actual archive sizes are 3,657,693, 3,782,321, and 3,933,448 bytes
for 2023, 2024, and 2025. The generated 2025 probe response differed in size;
the local acquisition manifest identifies the exact research input, not the
probe metadata. CSV rows are 427,426, 440,930, and 458,791; all twelve months
are present in each. The data member is T_T100D_SEGMENT_ALL_CARRIER.csv and
headers are uppercase names such as DEPARTURES_PERFORMED, not display labels.
No Coupon archive was acquired: ticket coupon counts permit the declared product
check, while carrier-defined FareClass cannot support a comparable flexibility
premium. Market and Ticket were acquired through2025Q2.
