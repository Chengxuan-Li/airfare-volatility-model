# Full-history handoff for another desktop

Prepared 2026-09-13. The next session can begin from the public repository without
this conversation or the originating desktop. This document is in Git at the
user's explicit request, overriding the handoff skill's temporary-directory default.

## Get the correct checkout

Repository: https://github.com/Chengxuan-Li/airfare-volatility-model

Use branch `codex/stage-6-full-history`. The handoff baseline is `ab75e38`;
the verified result milestone is `16b1c52`. Do not assume the default branch
contains this work. This handoff is a subsequent documentation commit.

For a new clone:

```powershell
git clone --branch codex/stage-6-full-history https://github.com/Chengxuan-Li/airfare-volatility-model.git
cd airfare-volatility-model
git status
git log --oneline --decorate -n 20
```

For an existing checkout, inspect its status and history before fetching or
switching. Preserve local changes and follow the repository's Git rules.

## Read first

Read [AGENTS.md](../../AGENTS.md), [README](../../README.md),
[documentation index](../INDEX.md), and [project state](../project_state.md).
Then read the [research contract and execution addendum](../20260912_airline_weather_pricing_research_task.md),
[completed full-history plan](../methods/stage6_full_history_plan.md), and
[full-history findings and reproduction contract](../findings/stage6_full_history_report.md).
These are authoritative; this handoff directs you to them rather than copying
their detailed findings, source exceptions or operating rules.

## What the user clarified before handoff

The user asked whether analysis-ready data are in Git, whether the expanded data
have been analyzed, and whether another desktop can continue. The answers are:

- The processed descriptive fare/operations panels are committed for all declared
  years, 2010 Q1 through 2025 Q2, on the frozen thirty-airport sample.
- Expanded-data work so far consists of descriptive coverage, continuity and
  data-quality analysis. No new expanded-history regression or pricing-hypothesis
  test has run. Earlier fitted results use the earlier samples.
- A new desktop can analyze the committed panels without raw downloads. A fresh
  installation on another desktop has not yet been tested.

The user requested this committed handoff. The completed historical acquisition
does not itself authorize treating new estimates as causal or already completed.

## Locate the analysis inputs and evidence

Canonical panels are `outputs/stage6/annual_YEAR/route_quarter_panel.csv`, with
supporting fare-carrier, operations-month, identity and quality tables alongside.
Start with the [2025 directory](../../outputs/stage6/annual_2025/) for the partial-year
schema and the [2010 directory](../../outputs/stage6/annual_2010/) for frozen baseline
artifacts. Preserve the `sample` and coverage fields when combining years;
primary and broad-bound samples overlap and must not be counted together.

Use [history summaries](../../outputs/stage6/history/) for compact coverage and
source-specific carrier presence, not as a substitute for the canonical panels
when estimating route-level relationships. The
[horizon verification](../../outputs/stage6/history/verification.json) links annual
proofs; the [consumed-input manifest](../../data/manifests/stage6_full_history_consumed_inputs.json)
records raw identities and checks. Source anomalies and interpretation limits are
in the findings report; failed attempts remain in the
[execution ledger](../status/execution_ledger.md) and acquisition/build manifests.

Raw archives, environments, credentials, backups and coordinator scratch scripts
are ignored and will not arrive in a clone. Do not depend on `data/processed/`
scratch recipes from the original machine. Public acquisition and verification
entry points are documented in the reproduction contract. Full raw replay needs
reacquisition, adequate disk space, and the recorded source versions; it is not
required to start analysis of the committed panels.

## First session on the new desktop

1. Complete the required repository reads and confirm the correct branch.
2. Create a local environment from `requirements.txt`. The recorded certification
   environment is Python 3.13.9. On Windows with that interpreter available:

   ```powershell
   py -3.13 -m venv .venv
   .\.venv\Scripts\python.exe --version
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   .\.venv\Scripts\python.exe -m pytest -q
   ```

   Check the actual patch version; `py -3.13` alone does not guarantee 3.13.9.
   Use the corresponding environment executable on other platforms. The last
   recorded suite has 251 passing tests and one known Stage 5 rank warning;
   report the newly observed result rather than assuming it transfers.
3. Check committed files against the SHA-256 values in the annual and horizon
   proofs. For an offline summary smoke check, run
   `python -m src.stage6.history --output data/processed/history_smoke` using the
   environment's Python. Compare its four output hashes with the horizon proof.
   This validates committed aggregate inputs; it does not reverify raw archives.
4. Start the next research step from [project state's next actions](../project_state.md#next-research-actions):
   predeclare expanded-panel analysis before fitting models. Specify the estimand,
   sample, reporting-population breaks, common support, pandemic treatment,
   partial-2025 comparisons and inference strategy. Record the plan in Git.
5. Preserve published inputs and prior findings. Put new analysis artifacts in a
   distinct location, document their provenance and limitations, test relevant
   changes, and update project state/index before committing and publishing.

Do not invoke the raw certification command as a first smoke test on a clone:
it requires all raw archives. Do not rerun annual builds into published directories
casually; the documented separate-output replay avoids displacing their proofs.
FR24 remains unused. Follow the existing cost/balance and spending rules before
any future calls; BTS outcomes already support the present operations measures.

## Suggested skills

If installed on the receiving desktop, use `superpowers:writing-plans` for the
next analysis plan, `research` for bounded primary-source questions,
`superpowers:systematic-debugging` for reproduction failures, and
`superpowers:verification-before-completion` before reporting results or publishing.
Use `code-review` for review against the recorded plan and repository standards.
Skill availability is machine-local; the checked-in research contract and methods
remain sufficient context if these skills are absent.
