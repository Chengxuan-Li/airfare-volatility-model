# Full-year 2011 panel with the frozen 2010 sample

Date: 2026-09-13. Scope: the declared [2011 extension](../methods/stage6_2011_plan.md).

The 2011 panel processes all four DB1B Market/Ticket pairs and all twelve reporting
on-time months using the same thirty airport IDs selected in 2010. It contains
3,198 primary fare route-quarters, of which 2,865 match operations. Coverage changes
are retained explicitly. This is subsequent-year data validation; no new fare
model, forecast model, holdout evaluation or causal estimate has been fitted.

## Acquisition and sample

Twenty new archives total 805,060,530 compressed bytes. Twenty HEAD probes returned
200; acquisition recorded 122,350,710,784 free bytes before bounded downloads in
pairs. All twenty requests passed path/request identity, SHA-256 and ZIP CRC checks,
with no download failures. See the [access inventory](../../data/manifests/stage6_2011_access_inventory.json)
and [acquisition ledger](../../data/manifests/stage6_2011_acquisition_20260913T054410170520Z.json).
Raw inputs remain local and ignored. No paid services or FR24 calls/credits.

The [frozen manifest](../../data/manifests/stage6_frozen_sample_2010.json) was committed
before acquisition. It pins the published 2010 verification record and ranking;
loading verifies all eight baseline derived artifacts before network or build work.
The 2011 ranking file is the reused 2010 Q1 ranking, including its baseline passenger
volumes, not a ranking of 2011 traffic. No airport was reselected or required to
survive in 2011. All thirty happen to be observed in four fare quarters and twelve
operations months in both years. This network remains a selected, seasonally
influenced sample rather than a nationally representative panel.

| Measure | Count |
| --- | ---: |
| National Market records scanned | 22,999,175 |
| National Ticket records scanned | 13,343,503 |
| National reported flights checked | 6,085,281 |
| Reported flights between selected airports | 2,110,718 |
| Scoped operations carrier-route-month cells | 17,469 |
| National operations carrier-month cells | 192 |
| Primary fare reporting-carrier-route-quarter cells | 27,579 |
| Broad fare reporting-carrier-route-quarter cells | 27,609 |

All source months are present. No duplicate flight keys or missing eligible arrival
delays were found. Scoped Market and matched Ticket keys passed uniqueness checks;
all 6,045,608 scoped Market rows matched Tickets before exclusions. These checks
do not establish complete population coverage.

## Coverage and support

| Sample | Fare route-quarters | Matched | Fare only | Operations only |
| --- | ---: | ---: | ---: | ---: |
| Primary: USD 20-2000 | 3,198 | 2,865 | 333 | 1 |
| Broad bounds: USD 10-5000 | 3,199 | 2,865 | 334 | 1 |

The primary outer panel has 3,199 rows, including its operations-only cell; the
broad panel has 3,200. Matched cells cover 99.8203% of primary sampled passenger
weights, versus 99.8458% in 2010. Route matching does not establish equal carrier
coverage. The operations-only cell is 2011 Q1 HNL (12173) to DTW (11433): one
reported flight, one observed month, and no eligible fare cell under either bound.
It retains missing fares. Fare-only rows retain missing operational outcomes.

Of 2,865 matched cells, 2,844 have three observed months, fourteen have two and
seven have one. The operations-only cell adds one further partial-month cell.
Observed months cannot distinguish seasonal service, entry/exit or reporting gaps.
No absent source outcome is imputed to zero or interpreted as a cancellation.

Primary fares retain 3,936,585 Market records and 12,296,037 sampled passenger
weights. There are 160 primary fare route-quarters below thirty passenger weights:
seven matched and 153 fare-only. At reporting-carrier level, 18,999 of 27,579
primary cells have low support. These remain flagged; future models need a declared
support rule. The operations-only row has no fare support classification.

| Quarter | Primary fare cells | Matched cells | Sampled passenger weights | Scoped reported flights |
| --- | ---: | ---: | ---: | ---: |
| 2011 Q1 | 804 | 717 | 2,810,076 | 514,086 |
| 2011 Q2 | 795 | 716 | 3,228,252 | 537,155 |
| 2011 Q3 | 800 | 716 | 3,129,466 | 544,598 |
| 2011 Q4 | 799 | 716 | 3,128,243 | 514,879 |

Sequential primary exclusions are 1,953,977 connecting/unknown-coupon rows,
2,473 bulk/unknown-bulk rows, 27,765 unreliable/missing-credibility Ticket rows and
124,808 rows outside primary fare bounds. Foreign endpoints, invalid passenger
counts, unmatched Tickets and missing fares add no scoped exclusions in this year.
Quarter-specific and broad-bound counts remain in the quality audit.

## Cross-year continuity

Comparisons match equal calendar quarters and stable endpoint IDs. The route
diagnostics use the union of route-quarter keys observed in either sample/year,
not all theoretically possible airport pairs. Primary has three keys absent in
both years' primary fares but observed in the broad sample or operations.

| Source/sample | Present both years | Observed in 2011 only | Observed in 2010 only | Absent both within union |
| --- | ---: | ---: | ---: | ---: |
| Primary fares | 3,139 | 59 | 52 | 3 |
| Broad-bound fares | 3,139 | 60 | 54 | 0 |
| Operations, once per route-quarter | 2,848 | 18 | 56 | 331 |

These are observed-source entries/exits, not verified openings or closures of
physical service. Operations continuity is repeated identically for both fare
samples in the CSV; never sum those repetitions. Audit summary counts likewise
span both samples, while the table above presents each sample separately.

The fare population has 34 reporting codes in 2011 versus 36 in 2010. Codes `CS`
and `F8` are absent from the scoped 2011 fare aggregates; all other codes persist.
National operations identities fall from eighteen to sixteen: DOT ID 20363/code
`9E` and DOT ID 20417/code `OH` are absent throughout the 2011 reporting files.
Both codes remain in DB1B fare aggregates. This is direct evidence that the two
source populations differ; it does not establish merger, closure or cancellation.
Fare carrier continuity covers selected routes across either fare bound; operations
carrier continuity uses national reporting identities. There is no carrier crosswalk
or carrier-level join. Each source is aggregated independently to route-quarter.

The scoped alias audit finds no cross-year airport ID/code changes, no airport
code assigned to multiple selected IDs, and no operations reporting code assigned
to multiple DOT IDs. This is a 2010-2011 observation, not validation of later years.

## Outputs and measurement

The seven annual CSVs and quality audit retain the [2010 dictionary and measurement
rules](stage6_2010_report.md#measurement-and-output-dictionary). New diagnostics are:

- `airport_continuity.csv`: sixty rows, one per selected ID and source (primary
  fares or operations); observed periods, codes and presence in each year.
- `carrier_continuity.csv`: 54 source-specific reporting identities with observed
  quarters/months and presence; fare rows have no fabricated DOT ID.
- `route_continuity.csv`: 6,506 rows, one per union route-quarter and fare sample;
  separate fare and operations presence flags and continuity categories.
- `quality_audit.json`: adds frozen selection year and continuity summaries,
  including alias and identity diagnostics.

Cancellation/diversion rates use all reported flights; arrival delay rates use
observed, noncancelled, nondiverted arrivals. Quarterly counts are summed before
division. Delay thresholds include fifteen and sixty minutes, and signed mean
arrival delay retains early arrivals. Fare moments are passenger weighted.
Quarterly nominal prorated fares are not timestamped quotes, traffic is endogenous,
and these operational outcomes are not quote-time forecast probabilities.

## Verification and reproduction

Two successful full raw builds reproduce all eleven derived files byte-for-byte,
with no failed 2011 build attempts. The pinned Python 3.13.9 environment passes
118 offline tests with one known Stage 5 reference warning. The
[verification record](../../outputs/stage6/annual_2011/verification.json) records
twenty raw hashes, ten additional frozen/baseline artifact hashes, nine Stage 6
source hashes and implementation commit `b085a1a`. All requirements pins match.
All fifty earlier output files remain unchanged relative to `21ede00`.
Independent code/spec and final artifact reviews found no material issues. The
artifact review reconciled all reported counts and hashes and independently reran
the 118 passing offline tests.

From the repository root, with the pinned environment and curl installed:

```powershell
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2011 --acquire
.\.venv\Scripts\python.exe -m src.stage6.annual --year 2011
.\.venv\Scripts\python.exe -m pytest -q
```

The 2011 command requires the frozen manifest and nine published 2010 baseline
files, in addition to twenty 2011 raw archives and their manifests. It verifies
those baseline artifacts rather than rescanning 2010 raw data. Reacquisition must
match committed identities and hashes. The default year remains 2010; only the two
declared years are accepted. Output cannot overlap the frozen baseline. Complete
directories publish with rollback, retaining earlier sets as ignored backups.
Rebuilding replaces the derived directory and retains an older verification record
with the backup rather than attaching it to a newly unverified build.

## Next milestone

Declare and process the 2012 batch with the same frozen sample, reviewing reporting
changes and source coverage before broadening later years. Full 2012-2025 Q2
acquisition remains outstanding. Capacity, compatible risk information,
departure/supply models and CR2/bootstrap inference remain separate work before new
fare estimation. More quarterly history does not recover missing quote-time
information. FR24 remains unused and supplemental, subject to verified cost,
balance and a specific coverage-valid use.
