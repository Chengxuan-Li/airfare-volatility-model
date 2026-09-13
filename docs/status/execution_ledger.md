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
