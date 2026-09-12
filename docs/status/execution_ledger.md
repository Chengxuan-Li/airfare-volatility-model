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
