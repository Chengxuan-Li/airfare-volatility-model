# Repository operating rules

The repository is the authoritative project memory. Never depend on chat history.
Before substantive work run `git status` and `git log --oneline --decorate -n 20`,
then read this file, `README.md`, `docs/INDEX.md`, `docs/project_state.md`, and the
relevant stage documents. The full operating contract and research specification
are in `docs/20260912_airline_weather_pricing_research_task.md`, including its
2026-09-12 execution addendum. Follow that contract.

## Research and spending

- No additional paid services, purchases, or upgrades.
- Initial Flightradar24 ceiling: 6,000 credits, bounded by verified availability;
  monthly allocation reported as 60,000. Verify costs and balance before calls.
  Maintain a ledger and cache permitted results. One coordinator owns acquisition.
- BTS DB1B is the selected fare source; verify batch acquisition before Stage 0.
  Do not call quarterly records timestamped quotes or observed traffic exogenous
  demand. Do not use realized weather as quote-time forecast risk.
- Preserve negative results, source failures, provenance, and limitations.
  Never fabricate data or overstate causal identification or stage completion.
- At most two subagent workers concurrently, on independent bounded tasks.
  Main model preference: Astra/high; workers: Sol/medium where supported.

## Git and public repository hygiene

All reasonable non-destructive Git operations are authorized, including status,
diff, log, show, fetch, pull, branch/worktree creation, safe switching, staging,
unstaging, commits, tags, safe merges, and push. Rebase only unshared history when
clearly safe. Preserve configured remotes and existing user work.

Never use hard reset, force push (including force-with-lease), destructive
checkout/restore, delete unmerged branches, rewrite shared/public history, or
discard user changes. Resolve conflicts by inspecting both sides and preserving
meaningful work; document non-trivial decisions.

Use conventional commit messages and commit meaningful milestones regularly.
Preserve the configured Git author identity. Do not change global identity or
attribute commits/co-authorship/trailers to AI systems or model versions.

Never commit secrets, credentials, cookies, private files, proprietary data without
redistribution rights, restricted raw inputs, environments, or large binaries.
Keep local credentials in ignored `.env`; `.env.example` must contain no secrets.
Keep raw downloads local; track acquisition recipes, schemas, manifests, checksums,
and provenance. Inspect staged files before committing or public push.

## Handoff and verification

Document important decisions, assumptions, findings, failures, and next actions.
Update `docs/project_state.md` at milestones and before stopping; index every new
durable document in `docs/INDEX.md`. Run relevant checks, inspect diff/status, and
commit completed non-sensitive work. Push to the configured public remote when
verified and safe. Leave the working tree clean when practical and document
intentionally uncommitted user changes. Do not claim success before verification.
