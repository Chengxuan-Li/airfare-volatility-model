# Autonomous execution ledger

2026-09-12, branch `codex/stage-0-to-4`.

- Stage 0 committed as `bcb1b47`: original and aggregate hypotheses separated,
  2023-2024 twelve-route pilot fixed before estimates.
- Stage 1 committed as `9e594d1`: 22 verified studies; novelty B for the original
  aligned quote design, much weaker for a generic aggregate delay-fare regression.
- Stage 2 committed as `0641787`: public Market/Ticket, ERA5 weather, and small
  BTS Delay Causes validation selected. No additional paid services used.
- Flightradar24 ledger: 0 requests, 0 credits consumed; 6,000 initial-pass ceiling,
  reported monthly allocation 60,000, reset date/balance unknown. BTS provides
  necessary operational validation, so no credential or balance query is needed.
- Original aggregate sign diagnostic refined after independent review: traffic
  is equilibrium quantity; a negative fare-traffic slope cannot by itself falsify
  its measurement or establish invalid demand pressure. No result-driven change.
- Independent review produced tests/fixes for full-schema Ticket overlaps,
  historical-quarter weather completeness, actual valid-date audits, and request
  identity on cache hits. Test fixtures are fabricated unit-test examples only;
  no synthetic record enters the research dataset.
- Raw acquisition: one Market 2024 Q3 GET reached its 240-second deadline with
  52,723,712/107,964,122 bytes. Resume via curl's standard Range support is bounded
  to a further 240 seconds; full ZIP CRC and SHA-256 are required after completion.
  Do not label the partial transfer a completed dataset or retry indefinitely.
- UTF-8 is explicit in Python file operations after a Windows locale decode error
  during an initial project-state edit. No user content was overwritten.
- Git authentication previously failed through a cancelled dialog. Future push
  attempts must be noninteractive; repository work is committed locally regardless.
- All sixteen Market/Ticket ZIPs completed, including the bounded Q3 resume.
  Seven weather responses and the small Delay Causes ZIP are cached and manifested.
- A full raw rebuild matched substantive estimates but not all output bytes when
  compared with an analysis-only run that used pandas' default CSV float parser.
  Ruling: both entry paths now read the same serialized fare cells with round-trip
  float parsing before modeling. Repeat the comparison after this correction;
  do not claim byte-identical reproduction based only on rounded estimates.

- Final verification passed: 16 offline tests; three full raw builds total; the
  final canonical raw build reproduced all 19 table/figure files byte-for-byte.
- Independent final review reconciled counts, estimates, intervals, units, support,
  and figures. Clarified prorated Market fares and full interaction units.
- Decision C: interesting aggregate observation, weak paper. Original quote-time
  H1/H2 and flexibility premiums remain unestimable. No prospective scheduler set.
# Stage 5 extension entry — 2026-09-12

User authorized additional free-source data and further methods. The extension
plan was committed before new model results. Same seven airports, all directed
pairs; 2025Q1/Q2 temporal holdout; whole one-way single-coupon ticket check; T100
independent route capacity and passengers; route/carrier/season effects.
No paid services and no FR24 calls or credits. Prior run token use was not
available as a reliable numeric total; no fabricated doubled budget was set.

Acquired four 2025 Market/Ticket ZIPs, three T100 annual form-generated extracts,
and seven ERA5 2020-25 responses. Ticket 2025Q1 timed out at 57,163,776 of
90,024,798 bytes after240 seconds; one bounded curl resume succeeded, followed
by full ZIP CRC validation and SHA-256 provenance. T100 guessed PREZIP URLs
returned404; the verified ASP.NET download form succeeds. Its archive includes
Documentation.csv before the data member; the extension explicitly selects
T_T100D_SEGMENT_ALL_CARRIER.csv. Raw files remain local and ignored.

Nineteen offline tests pass at the implementation milestone. Raw fare rebuild
and fitting are in progress. Worker tasks are bounded source verification and
identification review; coordinator owns acquisition, integration, and commits.
# Stage 5 final verification — 2026-09-12

Completed all 62 predeclared attempts:54 estimates, eight saturated seasonal
holdout failures.905 primary and873 one-way cells; no unmatched capacity/risk.
The reviewed nuisance-QR fix preserves fixed-effect span and focal regressors.
Twenty-one offline tests pass. Two raw builds reproduce 15 compact outputs
byte-for-byte; all 30 consumed input paths, request identities, hashes and payloads
verify. Original Stage0-4 outputs are unchanged. Plot visually inspected.
Independent code and final numerical/interpretation review completed.

Stop on the user-authorized strong-argument criterion: quarterly observables do
not identify the original quote-time joint demand/risk mechanism. This is not a
claim of causal zero or universal exhaustion. No additional paid service or FR24
call/credit. Git fetch succeeded; noninteractive push of codex/stage-5-robustness
failed exit 128 because GitHub username credentials are unavailable. No dialog.
Research, outputs, structure and final verification are committed locally; the
pre-existing user .env.example edit remains deliberately outside research commits.

# Stage 6 execution start — 2026-09-12

User authorized the committed next direction and instructed execution. Branch
`codex/stage-6-operations`; execution plan commit `6461da8`. A clean local checkout
is used, and a new ignored `.venv` installs all pinned requirements on Python
3.13.9. No paid service or FR24 request/credit.

The original-stage runner regression reproduced failure on an unrelated missing
T100 archive before the fix. Seven input-verification tests now pass. Download
regressions reproduced silent provenance replacement; six tests now cover changed
and matching reacquisition, request identity, legacy records and local POST
registration. Thirty-four relevant original/fix tests pass in the pinned
environment; its intentional redundant-dummy reference emits one known warning.
Historical outputs remain untouched. Full original raw rebuild is not claimed.

# Stage 6 bootstrap verification — 2026-09-12 local / 2026-09-13 UTC

Coordinator performed 126 initial HEAD requests: all 124 DB1B Market/Ticket
endpoints for 2010 Q1-2025 Q2 returned 200, advertising 9,925,278,201 bytes against
125,151,219,712 free bytes. The two operations recipes with parenthesized
`1987_present` returned 404. Preserve `stage6_access_inventory.json` unchanged.
Two corrected official filenames without parentheses returned 200, recorded in
`stage6_operations_access_correction.json`. Total coordinator HEAD requests: 128.
No automatic probe retries. Future inventory writes require a new destination.

Four coordinator GET downloads succeeded and passed ZIP CRC/SHA-256 validation:
January 2010 and January 2024 reporting on-time, and 2010 Q1 Market/Ticket. Total
compressed raw bytes: 163,801,228. No paid API calls or FR24 credits. Exact request
identities and consumed checksums are in the four acquisition manifests.

Worker-test incident: while adding invalid-timeout regressions, a worker invoked
`requests.head` 252 times through an insufficiently mocked CLI test before the
validation fix. Worker-reported diagnostics show 126 NaN-timeout ValueErrors
(`Invalid value NaN (not a number)`) and 126 infinite-timeout OverflowErrors
(`timestamp out of range for platform time_t`), all with null HTTP status and zero
successful responses. NaN attempt timestamps were 00:46:45.312654-00:46:57.504381Z;
infinite-timeout attempts were 00:46:57.646907-00:47:06.121759Z on 2026-09-13.
These invocation counts do not establish that HTTP requests reached BTS. No raw
downloads, paid calls, credentials or repository acquisition manifests were
involved. Pytest retention removed the temporary diagnostic JSONs before the
coordinator could preserve them; this entry records the worker report, not a
reconstructed raw log. Nonfinite timeouts now reject before probing; tests inject
transport, and an autouse fixture blocks unmocked requests HTTP suite-wide.

The operations reader checked 1,069,080 national flight records; no duplicate keys
or missing eligible arrival delays in these two months. The seven-airport subset
contains 33,648 flights in 265 carrier-route-month cells. Full national fare-period
checks read 4,906,864 Market and 2,835,075 Ticket rows. This is a schema/operations
bootstrap, not an expanded fare panel or new model fit.

Two full raw bootstrap builds reproduce four derived files byte-for-byte. All 71
offline tests pass in the exact pinned Python 3.13.9 environment; one known
Stage 5 reference warning remains. Independent review passed operations logic and
identified inventory-overwrite risk. A failing regression reproduced that issue;
the fix rejects existing outputs before probes and uses exclusive file creation.
The inventory-only change leaves bootstrap recipes/aggregations unchanged.
Original Stage 0-5 outputs remain unchanged. See the indexed bootstrap report and
`outputs/stage6/bootstrap_verification.json` for scope, hashes and next work.

Final independent code/report review found no remaining material issues and
reconciled every reported count and hash to artifacts. Staged public-hygiene and
local-link checks passed. Bootstrap milestone `4ae39ec` was committed and pushed
successfully to `origin/codex/stage-6-operations`, including plan `6461da8` and
provenance fixes `631e56e`. No historical output changes or raw files were included.

# Full-year 2010 execution — 2026-09-12 local / 2026-09-13 UTC

User authorized the proposed 2010 milestone with "go on". Plan `af1544c` fixes
baseline passenger-volume airport selection, stable-ID scope, independent
carrier aggregation and outer route-quarter linkage before new acquisition.
Ruling: 2010 Q1 supplies selection volume and 2010 remains a development year;
future temporal evaluation begins after the selection year. This avoids treating
sample selection as independent of the evaluated year. No fare models are fitted.

Coordinator issued 11 HEAD requests for February-December 2010 reporting on-time;
all returned 200. The original verified fare inventory and January operations
correction cover the other nine identities. New metadata is preserved in
`stage6_2010_access_inventory.json`; 124,744,589,312 free bytes were recorded.
All 20 advertised archives total 811,733,928 bytes. Three 2010 archives were cached;
17 new GET downloads passed CRC and SHA-256 validation, totaling 675,505,965 bytes.
No failures, automatic retries, credentials or FR24 calls/credits. Pairwise bounded
acquisition and exact hashes/statuses are recorded in
`stage6_2010_acquisition_20260913T011738492971Z.json`.

Implementation workers used offline fixtures only. Review caught misleading
default airport labels in the new ID scope, omission of entirely empty fare
samples from outer linkage, and unnecessary retention of national selection rows
in memory. Fixes retain old bootstrap behavior, preserve operations-only cells in
both declared fare samples, and aggregate baseline volumes by chunk. A complete
20-archive fixture runs through verification, selection, fares, operations and
linkage successfully. The real annual raw build is now in progress.

The first real annual build selected 30 airports but stopped in pandas CSV parsing
of 2010 Q1 Market before publishing outputs: `c_parser_wrapper._concatenate_chunks`
raised `IndexError: list index out of range` while handling mixed inferred column
types with a selected column subset. The reader now specifies text fields at read
time; targeted mixed-code/leading-zero regressions and a raw-reader check are
being completed before retry. Input CRC/checksums were unchanged.

Independent runner review identified orphan-raw adoption and interrupted output
replacement risks. The annual acquisition preflight now rejects existing raw
without a manifest. A regression reproduced an unrelated valid ZIP being assigned
new provenance before the fix. Complete output directories now publish through
sibling renames, with rollback on failure and prior sets retained in ignored
backup directories. Injected publication failure preserves all previous bytes.

Parser diagnosis confirmed the numeric carrier token `16` in 57,963 Q1 Market
rows, mixed with 35 alphanumeric tokens. Explicit string fields read all 4,906,864
rows successfully and preserve the leading-zero fixture token `01`. The final
implementation suite passes 100 tests (one existing Stage 5 reference warning);
independent review accepts the annual provenance/publication fixes. The second
real build attempt is running with the corrected parser.

# Full-year 2010 final verification

Two successful full raw annual builds now reproduce all eight derived files
byte-for-byte; twenty consumed raw path/request/checksum identities verify.
Together with the earlier parser failure, there were three full annual attempts.
The targeted Q1 diagnostic read was separate and produced no research output.
Environment pins match requirements exactly on Python 3.13.9. Full offline suite:
100 passed, one known Stage 5 rank-deficient reference warning. Independent
code/spec review of `cec3616...96e0c31` found no material issues.

Real annual totals: 22,038,685 Market rows, 12,688,062 Ticket rows, 6,450,117
national reported flights; 2,100,986 flights between selected airports. Baseline
ranking selects 30 of 399 airports (all original seven included). Primary fare
panel: 3,191 route-quarters, 2,904 matched and 287 fare-only. Matched cells represent
99.8458% of primary sampled passenger weights. Broad-bound panel: 3,193 cells,
2,904 matched and 289 fare-only. Neither sample has operations-only cells in this
year. Twenty-six matched cells have fewer than three reported service months;
all source months exist, and partial service/coverage is explicitly recorded.
No national duplicate flight keys or missing eligible arrival delays were found;
all scoped Market rows matched Ticket identities before exclusions. Fare and
operations carrier populations remain independently aggregated, not crosswalked.

See `docs/findings/stage6_2010_report.md` and
`outputs/stage6/annual_2010/verification.json` for exclusions, support, exact hashes,
reproduction and next-year scope. No new models or FR24 calls/credits. Earlier
Stage 0-5 and bootstrap outputs are preserved.

Independent final artifact review reconciled all reported numbers, identities and
hashes. It caught a prematurely checked publication item; that item was separated
and left pending until the push succeeds. No remaining numerical, interpretation,
code/spec or local-link findings. Public staged inspection verifies all eight
output hashes and excludes raw inputs, credentials and retained backup directories.

Publication succeeded: `8a036a8` and all preceding annual milestones pushed to
`origin/codex/stage-6-2010-panel`. The publication checklist is now complete.
Only source, tests, documentation, manifests and compact aggregates are published;
raw inputs, the pinned environment and one previous derived-set backup stay ignored.

# Frozen-sample 2011 acquisition — 2026-09-13

The user's next-step authorization starts the bounded 2011 extension on
`codex/stage-6-2011-panel`. Plan and frozen-baseline manifest were committed as
`7190f84` before acquisition. The manifest pins the published 2010 verification
and ranking; baseline loading verifies all eight derived artifacts before use.
The thirty selected IDs are retained without 2011 reranking or survival filtering.

Twenty HEAD probes returned 200 and advertised 805,060,530 compressed bytes.
Acquisition preflight recorded 122,350,710,784 free bytes. The coordinator made
twenty new bounded GET requests in pairs, downloading exactly eight fare archives
and twelve operations months. All twenty passed request/path, SHA-256 and ZIP CRC
checks; there were no failed downloads or cache substitutions. Exact request
outcomes and hashes are preserved in
`data/manifests/stage6_2011_acquisition_20260913T054410170520Z.json` and the
corresponding access inventory. No paid services, FR24 calls or credits.

The frozen-baseline/year-parameter regressions and continuity fixtures pass in
the full offline suite: 118 tests, one existing Stage 5 reference warning.
Independent Task 1 review found no material issues. Continuity review and the
first real 2011 raw build are in progress; no new model estimates are planned.

Independent Task 2 code/spec review also found no material issues. Focused tests
pass (27 annual/baseline/continuity cases); shuffled inputs confirm deterministic
continuity results and nonmutation. The first real raw build completed successfully,
producing eleven derived files; the second comparison build is running. Baseline
selection, source separation and missing-outcome semantics are preserved.

# Frozen-sample 2011 reproduction

Implementation milestone `b085a1a` contains the independently reviewed runner,
baseline pinning and continuity diagnostics. Two successful full raw builds now
reproduce all eleven derived files byte-for-byte, with no failed 2011 raw attempts.
Twenty raw request/path/checksum identities and ten frozen/baseline artifact hashes
verify. Requirements pins match on Python 3.13.9; the full offline suite passes
118 tests with one known Stage 5 rank-deficient reference warning. All fifty
earlier output files are unchanged relative to `21ede00`.

The 2011 scan includes 22,999,175 Market rows, 13,343,503 Ticket rows and 6,085,281
national reported flights. The selected network has 2,110,718 reported flights.
Primary fares have 3,198 route-quarters: 2,865 matched and 333 fare-only; one
operations-only cell is retained in the outer panel. Matched cells cover 99.8203%
of primary sampled passenger weights. Twenty-one matched route-quarters have fewer
than three observed months; the operations-only cell also has one observed month.
All twelve source months are complete, with no duplicate flight keys or missing
eligible arrival delays. All 6,045,608 scoped Market rows match Ticket identities
before exclusions. No source absence is imputed to zero.

The thirty baseline airport IDs remain observed in both sources and all periods.
2011 fare codes number 34 versus 36 in 2010; national operations DOT IDs number
16 versus 18. Fare codes CS/F8 and operations identities 20363/9E and 20417/OH
are absent in 2011 in their respective populations. These observations establish
neither physical service closure nor a carrier crosswalk. The two latter codes
remain present in fares. The alias/code-reuse audits find no conflicts across
these two years. Continuity tables preserve observed entries/exits without a
future-survival selection rule. See the 2011 report for sample-specific counts.

Final artifact review and public staged inspection are in progress. No fare
models, paid services or FR24 calls/credits were added. Raw archives, environments
and previous derived-set backups remain ignored.

Final independent artifact review reconciled all report counts, exclusions, source
populations, continuity statuses and hashes, with no actionable findings. It also
reran the full suite: 118 passed, one documented warning. Staged inspection verifies
all eleven derived hashes, ten baseline artifact hashes and nine source hashes;
local Markdown links resolve. Only compact text outputs and documentation are
staged; the largest new aggregate is 5,460,764 bytes. Publication is still pending.

Publication succeeded: `804a3b7` and all preceding milestones pushed to
`origin/codex/stage-6-2011-panel`. The publication checklist is now complete.
During final review a worker inadvertently redirected the committed annual runner
to an untracked `CON` file using PowerShell `Set-Content -NoNewline`, violating the
read-only review scope. The worker identified the exact command and source-only
contents. The coordinator verified its workspace path and SHA-256
`e7cd6b3458e3e6fe92b87aa3e09ee064f6d77a9cd318e7380ba464e0465ab3fc`, then removed
only that generated file. No raw data, credentials or user edits were affected.
Use stdout for read-only inspection; do not redirect to reserved device names.

# Continuous full-history execution — 2026-09-13

The user authorized continuing through all remaining years without another
command. Plan `b61f563` fixes 2012-2024 full years and 2025 Q1-Q2/January-June,
retaining the original frozen sample and all scientific measurement constraints.
The coordinator owns live requests and Git, with two bounded implementation workers.
No paid services or FR24 calls/credits are added.

All 270 remaining HEAD probes succeeded, advertising 13,165,882,016 bytes against
121,456,566,272 free bytes before acquisition. Fourteen per-year access inventories
and a horizon summary preserve exact endpoints, response metadata and disk checks.
The coordinator has begun year-ordered acquisition with two bounded GETs at a time.
Any failed pair stops acquisition for diagnosis and a documented bounded resume.
The full horizon is 310 identities: 124 DB1B Market/Ticket archives and 186 monthly
operations archives. Endpoint access is not yet schema or complete data validation.

Ruling: use matching Q1-Q2/January-June baseline periods for 2025 continuity —
unrequested later periods cannot establish exits — full-year totals are not directly
comparable to the partial final year. Keep original ranking/selection metadata.

Task 1 implements the shared 2010-2025 period declaration, exact ten-input 2025
boundary and matched-period baseline restriction. Independent code/spec review
found no material issues. Root verified all 270 expanded request identities against
the committed inventories. The offline suite excluding the concurrently developed
history-summary tests passes 169 cases with one known Stage 5 warning. Focused
annual/period/provenance regressions are green; old 2010/2011 outputs are unchanged.

Inspection found two original 2024 Market manifests with top-level year/quarter
instead of query_parameters. The annual verifier previously rejected them, despite
matching exact source identities. A fixture reproduced that rejection; verification
now accepts exact legacy fields without rewriting provenance and still rejects
wrong or incomplete periods. Independent review accepted the fix; bootstrap and
download tests pass (11). This was found before the 2024 raw build, not a failed
historical source request. The 2012 acquisition completed all twenty inputs and
2013 is underway. Repeated raw builds are starting with the reviewed annual code.

The first 2012 raw attempt stopped in July operations before publishing results:
one source row has a genuinely blank scheduled departure time (CRSDepTime), with
all other flight and outcome fields present. It is 2012-07-12, DOT carrier 19393,
flight 935, AUS-HOU; this route is outside the selected network. National outcome
counts would otherwise include it. The failed attempt and traceback are retained
in `stage6_2012_build_attempts.json`; input bytes were not changed.

Ruling: retain a flight with missing scheduled departure only when its remaining
date/carrier/flight-number/endpoint key is unique across the entire monthly source.
Keep the schedule value missing; never substitute actual departure time. Reject
any collision involving such an incomplete key, including across chunks. All other
identity requirements and exact full-key duplicate checks remain. Report affected
national/scoped counts explicitly. This preserves reported outcome denominators
without inventing schedule data; it does not validate the missing schedule itself.

The missing-schedule regression began red (five failures); the bounded fix passes
same-chunk and both cross-chunk collision orders while retaining valid distinct
scheduled departures. Root's real July reader check now processes all 545,131
reported flights, with one missing scheduled departure nationally and zero within
the selected network. A separate identity-only scan of all 2012/2013 monthly files
found no other missing identity fields. These diagnostic reads are not full annual
build attempts and created no research outputs.

The full current offline suite passes 191 tests, one known Stage 5 warning. Task 2
independent review caught subset summaries claiming the full horizon; the fix
labels their actual consecutive span and marks full_horizon_complete only for
all sixteen declared years. Default CLI still requires all years. The new
regressions began red; fourteen history tests now pass and re-review is clean.

Ruling: resume two independent alternating-year raw-build queues (2012/2014/etc.
and 2013/2015/etc.), each with two sequential reproduction passes. Per-year paths
are disjoint; acquisition remains one coordinator with at most two transfers.
Source hashes must remain stable across each build. This reduces elapsed time
without sharing mutable output state; any failure is preserved before diagnosis.

Verified year milestone: 2012, 2013. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

The first 2017 attempt stopped in May on two rows sharing the complete declared
flight key: 2017-05-21, DOT carrier 20436, flight 170, DEN-PHL, scheduled 1855.
Complete-row inspection shows different tail/departure/ground-return metadata,
but every field consumed by this operations pipeline agrees, including cancelled=1,
diverted=0 and missing arrival delay. They are not identical full source rows.
The failed attempt remains in its build ledger. The other coordinator queue was
stopped while waiting for 2018 (no active raw child) so the rule can be reviewed
before further builds; acquisition continues unchanged.

Ruling: coalesce a repeated complete flight key only when all consumed identity
and outcome fields agree exactly, including equal missingness. Count that declared
scheduled-flight unit once and audit raw rows, retained rows and removed repeated
rows nationally and in scope. Keep raw bytes and distinct unconsumed metadata;
this rule does not resolve aircraft or gate-departure variants for future models.
Conflicting consumed fields still fail. Missing-schedule core collisions still fail
and are never coalesced. Check both within-chunk and cross-chunk repeats, preserving
the existing full-key definition rather than selecting a preferred outcome row.

Verified year milestone: 2014, 2015. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

Verified year milestone: 2016. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

2017 repeat-resolution fix passed independent review and the full offline suite
(206 tests; one known Stage 5 rank-deficiency warning). Coordinator validation
of May against all thirty frozen IDs records 486,483 raw rows, 486,482 retained
national flights, 191,108 retained scoped flights and one removed repeat both
nationally and in scope. Multiple chunk sizes produce identical results. The
optimized exact-tuple implementation keeps all consumed fields without hash-only
equality. Both raw-build queues resume from 2017/2018 after this code milestone.

New strict failures: the resumed 2017 build stopped in July; 2018 stopped in June.
Complete raw inspection found exactly two conflicting rows in each affected month:
2017-07-05/DOT19930/flight608/SEA-LAS/2150 has ArrDelay159,Diverted0 versus
ArrDelay missing,Diverted1 on different aircraft; 2018-06-21/DOT20452/flight3624/
DEN-XNA/2007 has ArrDelay4 versus941, both noncancelled/nondiverted, on different
aircraft. No preferred physical-flight history follows from the consumed key.
Independent review approved whole-key quarantine with full-month preflight and
second-pass aggregation. Every conflicting raw row is excluded and audited with
exact consumed variants/counts; equivalent removals remain mutually exclusive.
Incomplete-key collisions and invalid values still fail. The plan/report record
the denominator and disruption-selection limitations; raw data are unchanged.

Coordinator real-month quarantine verification on all thirty IDs: July 2017
509,070 raw -> 509,068 retained national records; 196,589 retained scoped records;
two ambiguous rows excluded nationally and in scope. June 2018: 626,217 raw ->
626,215 retained; 205,076 scoped; two national and zero scoped ambiguous exclusions.
A serialized-audit regression exposed integer/float CSV chunk inference changing
JSON bytes; numeric canonicalization fixed it. Independent code review also added
scoped equivalent-repeat group counts. Full suite passed 226 tests before final
certification-detail refinements. Exact final test evidence follows the code review.

Final code/spec re-review found no remaining material issues. All 232 offline
tests pass (one known Stage 5 warning), including annual quarantine integration
and certification proof-integrity regressions. The public final certification
script validates source revisions, exact input classes, baseline artifacts and
ambiguity details. Annual queues resume with this reviewed implementation.

Acquisition complete through 2025 Q2: all 270 remaining sources verify, totaling
13,165,882,016 bytes (269 downloads/matching reacquisitions and one verified January
2024 cache). No transfer failures; all old matching fare manifests retain original
provenance. Together with 2010/2011, all 310 declared archives are locally available.
Remaining annual reproduction and final full-horizon certification continue.

Verified year milestone: 2017. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

Verified year milestone: 2018. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

Verified year milestone: 2020. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

Verified year milestone: 2019. Each year reproduces all
eleven derived files byte-for-byte from its full declared raw input set. Per-year
verification records and build-attempt ledgers preserve input/baseline/source hashes
and any preceding failed attempts. Report progress table reconciles against those
verified artifacts. Publication follows staged inspection.

Certification portability refinement: metadata evidence uses explicitly named
LF-normalized hashes, preserving original manifest bytes and provenance across
Windows/Unix checkout endings. Raw ZIP/output/annual-proof hashes stay byte-exact;
the new consumed-input manifest is pinned LF. Independent review found no issues,
and all 233 offline tests pass (one known Stage 5 warning). Annual dependencies
did not change; ongoing raw builds retain their earlier 232-test validation record.
