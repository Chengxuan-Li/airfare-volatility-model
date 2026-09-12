# Project state

## Current stage
Pre-execution: agreed operating constraints recorded; BTS batch-download
verification in progress. Research Stages 0-4 have not started.

## Last updated
2026-09-12

## Completed
- Local credential store and tracked empty template created.
- User-approved execution defaults added to the research task.
- Mandatory repository governance, overview, and navigation established.
- BTS DB1B selected; direct pre-zipped Market download verified for 2024 Q1.

## In progress
- Verify a second quarterly ZIP and finish the batch-download recipe.

## Key conclusions and important assumptions
- DB1B supplies quarterly sampled fares/traffic, not flight quote timestamps.
  An aggregate redesign cannot be presented as the original ex-ante pricing test.
- No additional paid services. Flightradar24 initial-pass cap is 6,000 credits
  within the reported 60,000 monthly allocation. Zero credits used by this task.
- At most two worker agents authorized; coordinator controls all API spending.
- Finish with currently available data; prospective scheduling is deferred.
- Report unidentifiable hypotheses explicitly rather than fabricate substitutes.

## Data status
Original BTS ZIP files are local and ignored under `data/raw/bts_db1b/`.
Provenance manifests are tracked under `data/manifests/`.
No cleaned pilot or estimated models exist yet.

## Known limitations and open questions
- Flightradar24 reset date and live remaining balance are unknown.
- Demand proxy validity and an aggregate ex-ante risk measure require Stage 0/2 work.
- Selected time range remains a research decision; 2024 Q1/Q2 are access checks.

## Next actions
1. Finish and commit batch-download verification before research execution.
2. Begin Stage 0 when the user starts the research run; preserve original hypotheses
   and define the DB1B aggregate design separately.
3. Follow staged literature, feasibility, acquisition, analysis, and Git checkpoints.

## Blockers
No blocker to the download verification. Original quote-time identification is
not supplied by DB1B alone.

## Relevant commits
- `072408b` — API credential template and initial budget notes.
- See Git history for the execution-addendum/governance and download checkpoints.

## Intentionally uncommitted files
- `.env` is ignored local credential configuration and must never be committed.
- `.env.example` was already modified by the user at session start. Preserve that
  change and exclude it from this session's commits; do not print credential values.
- Raw BTS ZIP files remain ignored; manifests and reproduction instructions are
  committed instead.
