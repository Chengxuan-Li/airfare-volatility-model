# Project state

## Current stage
Pre-execution checkpoint complete: operating constraints committed and BTS
batch-download method verified. Research Stages 0-4 have not started.

## Last updated
2026-09-12

## Completed
- Local credential store and tracked empty template created.
- User-approved execution defaults added to the research task.
- Mandatory repository governance, overview, and navigation established.
- BTS DB1B selected; direct pre-zipped Market downloads verified for 2024 Q1/Q2.
- Both archives passed full ZIP CRC checks; SHA-256 and schemas recorded.
- Documented Python recipe rerun successfully against the cached files.
- Ticket and Coupon 2024 Q1 endpoints passed HEAD checks; not fully downloaded.

## In progress
- No research-stage execution in progress; ready for the user to start the run.

## Key conclusions and important assumptions
- DB1B supplies quarterly sampled fares/traffic, not flight quote timestamps.
  An aggregate redesign cannot be presented as the original ex-ante pricing test.
- No additional paid services. Flightradar24 initial-pass cap is 6,000 credits
  within the reported 60,000 monthly allocation. Zero credits used by this task.
- At most two worker agents authorized; coordinator controls all API spending.
- Finish with currently available data; prospective scheduling is deferred.
- Report unidentifiable hypotheses explicitly rather than fabricate substitutes.

## Data status
Two original BTS Market ZIPs (2024 Q1/Q2; 205,026,619 total bytes) are local and
ignored under `data/raw/bts_db1b/`. Slow Python Q2 transfer was interrupted;
bounded curl GET completed successfully, and temporary probes were removed.
Provenance manifests are tracked under `data/manifests/`.
No cleaned pilot or estimated models exist yet.

## Known limitations and open questions
- Flightradar24 reset date and live remaining balance are unknown.
- Demand proxy validity and an aggregate ex-ante risk measure require Stage 0/2 work.
- Selected time range remains a research decision; 2024 Q1/Q2 are access checks.

## Next actions
1. Read the committed batch-download recipe and manifests before research execution.
2. Begin Stage 0 when the user starts the research run; preserve original hypotheses
   and define the DB1B aggregate design separately.
3. Follow staged literature, feasibility, acquisition, analysis, and Git checkpoints.

## Blockers
No blocker to the download verification. Original quote-time identification is
not supplied by DB1B alone.

## Relevant commits
- `072408b` — API credential template and initial budget notes.
- `1e42de6` — execution addendum, mandatory governance, and repository rules.
- See Git history for the subsequent verified BTS download checkpoint.

## Intentionally uncommitted files
- `.env` is ignored local credential configuration and must never be committed.
- `.env.example` was already modified by the user at session start. Preserve that
  change and exclude it from this session's commits; do not print credential values.
- Raw BTS ZIP files remain ignored; manifests and reproduction instructions are
  committed instead.
