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
