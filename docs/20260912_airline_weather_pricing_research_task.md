# Codex Task: Airline Weather-Risk Pricing Research Repository

**Date:** 2026-09-12  
**Repository visibility:** Public GitHub repository  
**Execution environment:** Local repository, Codex or equivalent coding/research agent  
**Access model:** Full repository access; all non-destructive Git operations are allowed  
**Research scope:** Execute through Stage 4 before stopping unless blocked by an unavoidable external access/permission barrier

---

# 1. Mission

## Execution addendum agreed 2026-09-12

This addendum records subsequent user instructions and takes precedence where
it narrows the original execution scope.

- First document and verify a batch-download method for the user-selected BTS
  DB1B fare dataset before starting the research stages:
  https://www.transtats.bts.gov/tables.asp?QO_VQ=EFI&QO_anzr=Nv4yv0r
- No additional paid services, purchases, or upgrades. No fare API credentials
  or private booking/inventory dataset are available from the user.
- Flightradar24 Explorer: reported 60,000 credits for one month. Cap this initial
  research pass at 6,000 credits, subject to verified remaining balance; preserve
  the rest. Billing/reset date and actual balance remain unknown. Check endpoint
  costs before use, keep a usage ledger, cache permitted results, and centralize
  acquisition so subagents cannot duplicate spending.
- Finish the initial assessment with currently obtainable data. Prepare a
  prospective collector only if justified; multiweek scheduling is a later decision.
- If aligned fare, demand, and ex-ante risk data cannot be obtained, deliver the
  strongest real partial pilot and explicitly mark the original pricing hypotheses
  not estimable. Do not claim every Stage 4 empirical test was completed.
- Use DB1B as the selected fare source. Its quarterly ticket records must not be
  relabeled as timestamped quotes. Document any aggregate research redesign and
  its identification limits before estimating it.
- Model preference: GPT-6 Astra with high reasoning for coordination, methodology,
  integration, and conclusions; GPT-5.6 Sol with medium reasoning for bounded
  worker tasks where available. This preference does not assert the active model
  setting has been changed.
- Subagents are authorized, with at most two workers concurrently. Delegate
  independent literature/source checks and review; the coordinator owns API
  spending, integration, and Git commits.
- Follow this document's repository rules and commit at meaningful milestones
  throughout the work. Preserve user changes and configured Git identity.
- Credentials belong only in ignored local `.env`; keep `.env.example` empty
  of secrets. See `docs/data/api_credentials.md`.

Batch-download findings and reproduction instructions are recorded in
`docs/data/bts_db1b_batch_download.md`.

Build and execute a reproducible research repository investigating whether ex-ante weather / operational disruption risk changes the relationship between airline ticket prices and demand.

The central empirical hypothesis is:

\[
P_{ift}
=
\alpha
+\beta_D D_{ift}
+\beta_R R_{ift}
+\beta_{DR}D_{ift}R_{ift}
+\gamma X_{ift}
+\epsilon_{ift}
\]

with:

\[
H_1:\beta_R>0
\]

and:

\[
H_2:\beta_{DR}<0.
\]

Interpretation:

> Higher weather / operational risk raises the fare floor / intercept but flattens the demand-to-price slope.

Equivalently:

> **High risk → higher base fare, lower price sensitivity to demand.**  
> **Low risk / good weather → lower base fare, higher price sensitivity to demand.**

A related implication is:

\[
R\uparrow
\Rightarrow
\operatorname{Var}_D(P\mid R)\downarrow
\]

for demand-driven conditional dispersion.

Do **not** assume unconditional total fare variance decreases, because disruptions may introduce additional jumps, cancellation risk, capacity shocks, or repricing volatility.

---

# 2. Repository Is the System of Record

This project is designed for cross-machine and cross-user collaboration.

Conversation history is **not** guaranteed to be available to future agents or users.

Therefore:

\[
\boxed{\text{The repository is the authoritative project memory.}}
\]

Any important, useful, conclusive, methodological, instructional, or decision-relevant information derived from user prompts, agent reasoning, external research, or analysis must be written into repository documentation and committed to Git.

Future work must never depend on access to a prior conversational prompt.

If information is important enough that another researcher or agent would need it to continue correctly, it belongs in the repository.

---

# 3. Required Repository Initialization

If the repository is not already initialized:

```bash
git init
```

Use a public-repo-ready structure from the start.

Suggested repository name:

```text
airline-weather-pricing
```

Do not assume the exact GitHub remote exists until verified.

If remote configuration is already present, preserve it.

Do not replace or rewrite an existing remote without explicit human instruction.

---

# 4. Mandatory Root Files

The repository must contain:

```text
AGENTS.md
README.md
.gitignore
docs/INDEX.md
docs/project_state.md
```

These files are mandatory and Git-controlled.

---

# 5. AGENTS.md Contract

Create and maintain a root-level `AGENTS.md`.

It must define the operating rules for any future agent working in the repository.

At minimum, `AGENTS.md` must contain the following policy.

## 5.1 Repository Authority

- Repository files are the system of record.
- Do not rely on chat history.
- Important decisions, assumptions, findings, conclusions, failures, and next steps must be documented in-repo.
- Before starting substantive work, read:
  - `AGENTS.md`
  - `README.md`
  - `docs/INDEX.md`
  - `docs/project_state.md`
  - relevant stage documents

## 5.2 Git Permissions

The agent may use all reasonable **non-destructive** Git operations, including:

- `git status`
- `git diff`
- `git log`
- `git show`
- `git branch`
- `git switch`
- `git checkout` when non-destructive
- `git add`
- `git commit`
- `git fetch`
- `git pull`
- `git push`
- `git merge` when safe
- `git rebase` only when it does not rewrite shared/public history and is clearly safe
- tags
- creating branches
- creating worktrees
- staging and unstaging
- restoring individual uncommitted files only when it does not destroy user work and the intent is clear

## 5.3 Forbidden Destructive Git Operations

Do not perform destructive actions such as:

- `git reset --hard`
- force push
- `git push --force`
- `git push --force-with-lease`
- deleting unmerged branches
- rewriting public/shared commit history
- destructive checkout that discards uncommitted work
- deleting user work to resolve conflicts
- removing commits merely to simplify history
- any command whose primary effect is irreversible data loss

If a Git conflict occurs:

1. inspect both sides;
2. preserve all meaningful work;
3. resolve conservatively;
4. document non-trivial conflict decisions.

## 5.4 Commit Identity Rules

When committing:

- Do not identify Codex, ChatGPT, OpenAI models, Claude, Gemini, Copilot, or any other AI system as author or co-author.
- Do not include model names or versions in commit trailers.
- Do not add:
  - `Co-authored-by: ChatGPT`
  - `Co-authored-by: Codex`
  - any equivalent model attribution.
- Preserve the repository/user-configured Git author identity.
- Do not modify global Git identity unless explicitly instructed.

## 5.5 Commit Style

Use conventional-style commit messages.

Examples:

```text
docs(research): define weather-pricing hypotheses
docs(literature): add revenue management evidence map
feat(data): add BTS flight outcome loader
feat(weather): add forecast risk extraction
analysis(pricing): estimate weather-demand interaction
fix(cleaning): normalize fare observation timestamps
chore(repo): add public repository hygiene
```

Make commits at meaningful milestones.

Avoid giant catch-all commits when the work naturally divides into stages.

## 5.6 Public Repository Hygiene

Never commit:

- API keys
- tokens
- credentials
- browser cookies
- private account data
- secrets
- paid/proprietary data without redistribution rights
- private user files
- machine-specific secrets
- `.env` files containing credentials
- raw data whose license forbids redistribution

Use `.gitignore` and documented environment-variable conventions.

If external data cannot be legally committed, commit:

- acquisition code
- provenance
- checksums if appropriate
- manifest
- download instructions
- schema
- metadata

instead.

## 5.7 Documentation Before Handoff

Before stopping work, switching machine, or handing the repo to another agent:

1. update `docs/project_state.md`;
2. update `docs/INDEX.md` if new durable documents were created;
3. ensure important conclusions are in committed docs;
4. commit all completed non-sensitive work;
5. leave the working tree clean when practical;
6. clearly document any intentionally uncommitted files.

---

# 6. Documentation Architecture

Use:

```text
docs/
├── INDEX.md
├── project_state.md
├── research/
├── methods/
├── data/
├── decisions/
├── findings/
├── status/
└── handoffs/
```

Keep the structure simple; do not create empty directories solely for appearance.

Recommended durable documents:

```text
docs/research/00_research_charter.md
docs/research/01_hypotheses.md
docs/research/02_falsification_criteria.md
docs/research/03_literature_review.md
docs/research/04_novelty_assessment.md

docs/data/05_data_source_inventory.md
docs/data/06_fare_data_feasibility.md
docs/data/07_demand_proxy_feasibility.md
docs/data/08_weather_risk_definition.md
docs/data/09_data_legal_technical_constraints.md

docs/findings/10_preliminary_results.md
docs/findings/stage_0_to_4_report.md
```

Names may be adjusted if the repo already has a coherent convention.

---

# 7. docs/INDEX.md

`docs/INDEX.md` must act as a durable navigation layer.

It should include:

- project purpose
- current research stage
- key research documents
- methodology documents
- data provenance documents
- findings
- major decisions
- latest project-state file
- handoff instructions

Any durable new document should be added to the index.

A future agent should be able to reconstruct the project by starting from:

```text
AGENTS.md
README.md
docs/INDEX.md
docs/project_state.md
```

without prior chat context.

---

# 8. docs/project_state.md

This file is the current operational state of the project.

Maintain sections such as:

```markdown
# Project State

## Current Stage
Stage N

## Last Updated
YYYY-MM-DD

## Completed
- ...

## In Progress
- ...

## Key Conclusions
- ...

## Important Assumptions
- ...

## Data Status
- ...

## Known Limitations
- ...

## Open Questions
- ...

## Next Actions
1. ...
2. ...

## Blockers
- ...

## Relevant Commits
- `<sha>` — description
```

Update this file whenever:

- a stage is completed;
- a major design decision changes;
- a key source succeeds/fails;
- a methodological assumption changes;
- the project is handed to another machine or agent.

---

# 9. README.md

The public-facing README should eventually explain:

- research question
- motivation
- current status
- repository structure
- reproducibility
- data access constraints
- how to run analyses
- public-data provenance
- caveats

Do not overstate results before Stage 4.

If the project is preliminary, say so clearly.

---

# 10. Recommended Repository Layout

```text
airline-weather-pricing/
│
├── AGENTS.md
├── README.md
├── .gitignore
│
├── docs/
│   ├── INDEX.md
│   ├── project_state.md
│   ├── research/
│   ├── methods/
│   ├── data/
│   ├── decisions/
│   ├── findings/
│   ├── status/
│   └── handoffs/
│
├── literature/
│   └── literature_master.csv
│
├── data/
│   ├── README.md
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── manifests/
│
├── src/
│   ├── acquisition/
│   ├── cleaning/
│   ├── weather/
│   ├── fares/
│   └── analysis/
│
├── notebooks/
│
├── tests/
│
└── outputs/
    ├── figures/
    ├── tables/
    └── reports/
```

Adapt this if implementation evidence shows a better structure.

Avoid unnecessary scaffolding.

---

# 11. Research Concept

Airline tickets can be treated as service contracts containing different forms of embedded optionality:

\[
\text{Ticket}
=
\text{Transportation Claim}
+
\text{Cancellation Option}
+
\text{Exchange/Rebooking Option}
+
\text{IROP/Disruption Option}
\]

A strict Basic Economy ticket is closer to a prepaid forward on a non-storable service than to a futures contract.

A flexible/refundable ticket contains additional option-like rights.

A weather waiver resembles a state-contingent exchange option:

\[
W_t
=
I_{\{\text{waiver active}\}}
\max_{f\in\mathcal F}
\left[
U(f)-C_{\text{exercise}}(f)
\right].
\]

Operational uncertainty may be modeled conceptually as:

\[
dV_t
=
\mu_tdt
+
\sigma_tdW_t
+
J_tdN_t
\]

where:

- \(\sigma_t\): continuous uncertainty
- \(dN_t\): disruption / jump hazard
- \(J_t\): jump magnitude

This framing is conceptual background, not a license to impose a Black–Scholes-style model without evidence.

---

# 12. Core Distinction

Do not conflate:

\[
\sigma_{\text{demand}}
\]

with:

\[
\sigma_{\text{ops}}.
\]

Observed fares may depend on both:

\[
\sigma_{\text{fare}}
=
f(
\sigma_{\text{demand}},
\sigma_{\text{ops}},
\text{capacity},
\text{DTD},
\text{competition},
\text{RM policy}
).
\]

The research objective is to determine whether ex-ante operational/weather risk changes the **demand-to-price transmission relationship**.

---

# 13. Secondary Flexibility Metric

If comparable fare products are obtainable, define:

\[
\Omega_t
=
P_{\text{flex},t}
-
P_{\text{restricted},t}.
\]

This can be analyzed as a flexibility premium / option-price-like quantity.

It is secondary unless the main demand-slope design proves infeasible or substantially weaker.

---

# 14. Execution Scope

The agent is authorized to execute:

- Stage 0
- Stage 1
- Stage 2
- Stage 3
- Stage 4

The agent should not pause for routine human input before completing Stage 4.

If one approach fails:

1. document failure;
2. investigate alternatives;
3. continue with the strongest defensible approach.

Only stop early if a genuine external barrier prevents meaningful continuation, for example:

- required paid credentials with no alternative;
- inaccessible proprietary dataset with no substitute;
- anti-bot/access barrier that makes lawful acquisition impossible;
- missing permission required to proceed.

Do not stop merely because:

- the preferred API fails;
- one website blocks automation;
- a proxy is imperfect;
- cleaning is difficult;
- the initial hypothesis requires refinement.

---

# 15. Stage 0 — Research Specification

## Objective

Convert the conceptual hypothesis into a falsifiable research design.

## Required Work

Define:

- primary question
- hypotheses
- unit of observation
- dependent variable
- risk exposure
- demand proxy candidates
- controls
- confounders
- competing explanations
- falsification conditions
- kill criteria

Preserve at least:

\[
H_1:\beta_R>0
\]

\[
H_2:\beta_{DR}<0.
\]

Explicitly distinguish conditional demand-driven dispersion from unconditional fare volatility.

## Deliverables

```text
docs/research/00_research_charter.md
docs/research/01_hypotheses.md
docs/research/02_falsification_criteria.md
```

## Git Checkpoint

Commit after Stage 0.

Suggested message:

```text
docs(research): define weather-pricing research design
```

Update `docs/project_state.md`.

---

# 16. Stage 1 — Literature and Novelty Assessment

## Literature Areas

Research at least:

1. airline revenue management
2. demand-based pricing
3. dynamic airfare dispersion
4. fare classes
5. continuous pricing
6. refundable fares
7. partially refundable fares
8. exchangeable tickets
9. flexible fares as options / real options
10. weather and airfare
11. delay/reliability and airfare
12. cancellation/disruption economics
13. stochastic airline disruption management
14. pricing under supply/reliability uncertainty
15. direct evidence on:
   \[
   \text{operational risk}\times\text{demand}\rightarrow\text{price}
   \]

## Literature Table

Create:

```text
literature/literature_master.csv
```

Columns should include at least:

```text
paper_id
authors
year
title
venue
doi_or_url
research_question
data
method
main_result
relevance
gap_relative_to_project
notes
```

Verify bibliographic details.

Do not rely on prior chat claims without verification.

## Deliverables

```text
docs/research/03_literature_review.md
docs/research/04_novelty_assessment.md
literature/literature_master.csv
```

## Novelty Decision

Conclude:

- A — Clearly novel
- B — Incremental but defensible
- C — Already substantially done

Explain the evidence.

## Git Checkpoint

Suggested:

```text
docs(literature): map adjacent airline pricing research
```

Update project state.

---

# 17. Stage 2 — Data Feasibility

The empirical project requires:

\[
P,\quad D,\quad R.
\]

where:

- \(P\): fare
- \(D\): demand state / proxy
- \(R\): ex-ante operational/weather risk

---

# 18. Stage 2A — Fare Data

Investigate viable sources for:

- airline
- flight number
- route
- scheduled departure
- query timestamp
- days to departure
- quoted fare
- Basic / Standard / Flex
- cabin
- taxes/fees
- fare restrictions
- fare-class availability if visible

Investigate:

- public APIs
- airline interfaces
- OTAs
- Google Flights where lawful and technically practical
- historical fare research datasets
- transportation datasets
- commercial APIs with usable free/demo tiers
- reproducible collection methods

Document:

- access method
- terms/access restrictions
- historical availability
- automation feasibility
- sampling limitations
- licensing

Do not violate access controls.

---

# 19. Stage 2B — Demand Proxy

This is a critical methodological issue.

Evaluate candidates including:

- fare-class availability
- remaining inventory
- seat-map occupancy
- booking velocity
- historical route demand
- BTS DB1B / O&D data
- route frequency
- DTD
- weekday
- holidays
- local events
- airport passenger volume
- load-factor proxies
- price rank
- fare-ladder position
- same-flight price evolution
- search-interest data
- other defensible observable demand signals

Do not label a variable "demand" merely because it is correlated with booking time.

The chosen proxy should ideally reproduce:

\[
\frac{\partial P}{\partial D}>0
\]

under relatively benign conditions.

Create a validation strategy.

---

# 20. Stage 2C — Ex-Ante Operational Risk

Use only variables observable at the quote timestamp.

Candidate variables:

- precipitation probability
- thunderstorm probability
- snow forecast
- wind
- gust
- visibility
- severe weather alerts
- airport weather severity
- forecast uncertainty
- forecast revisions
- airport operational constraints when publicly available

Prefer archived forecast vintages.

Do not substitute realized weather for forecast risk without clearly changing the research question.

---

# 21. Stage 2D — Ex-Post Outcomes

Use for validation:

- cancellation
- departure delay
- arrival delay
- diversion
- airport-wide disruption

Investigate authoritative U.S. sources such as BTS and NOAA/NWS, but verify current accessibility and schema.

---

# 22. Stage 2 Deliverables

Create:

```text
docs/data/05_data_source_inventory.md
docs/data/06_fare_data_feasibility.md
docs/data/07_demand_proxy_feasibility.md
docs/data/08_weather_risk_definition.md
docs/data/09_data_legal_technical_constraints.md
```

Create a source matrix containing:

```text
variable
source
access_method
historical_available
automatable
license_or_terms
quality
limitations
selected_for_pilot
```

## Decision

Determine whether \(P\), \(D\), and \(R\) are sufficiently observable for a pilot.

If the preferred source fails, continue searching for substitutes.

## Git Checkpoint

Suggested:

```text
docs(data): assess fare demand and weather data feasibility
```

Update project state.

---

# 23. Stage 3 — Real Pilot Dataset

If feasible, build a real, non-synthetic pilot.

Suggested initial scope:

- approximately 3 weather-sensitive hubs
- approximately 8–15 domestic routes
- approximately 2–4 airlines
- multiple departure dates
- multiple observation times where possible

Candidate hubs include:

```text
ORD
DEN
DFW
```

but substitute better airports if data/weather conditions justify it.

## Target Fields

Aim for:

```text
observation_timestamp
airline
flight_number
origin
destination
departure_timestamp
days_to_departure

fare_basic
fare_standard
fare_flex
fare_main

demand_proxy_1
demand_proxy_2

forecast_weather_variables
operational_risk_score

realized_delay
cancelled
diverted
```

## Provenance

Every acquired dataset must have provenance recorded.

For each raw dataset, document:

- source
- URL/API endpoint or acquisition method
- retrieval date
- license / terms notes
- query parameters
- date range
- transformations
- raw file checksum if useful

Use:

```text
data/manifests/
```

for provenance manifests.

## Large / Non-Redistributable Data

Do not commit large or restricted raw data merely for convenience.

Commit:

- manifests
- schemas
- scripts
- reproducible download instructions
- small allowed samples if legally permitted

---

# 24. Stage 3 Code Quality

Acquisition and cleaning code should be reproducible.

Prefer Python unless the repository already establishes another suitable stack.

Recommended baseline dependencies where useful:

```text
pandas
numpy
requests/httpx
pyarrow
statsmodels
matplotlib
scipy
```

Avoid unnecessary heavy frameworks.

Pin dependencies in a reproducible environment file once the stack stabilizes.

Possible choices:

```text
pyproject.toml
requirements.txt
```

Use one coherent approach.

---

# 25. Testing

Add targeted tests for:

- timestamp normalization
- fare parsing
- route normalization
- weather matching
- missing-value handling
- risk-score construction
- deterministic transformations

Do not write superficial tests solely for line coverage.

For data pipelines, include small fixture data under:

```text
tests/fixtures/
```

when licensing permits.

---

# 26. Stage 3 Deliverables

```text
data/raw/
data/interim/
data/processed/
data/manifests/

src/acquisition/
src/cleaning/
src/weather/
src/fares/
src/analysis/

tests/
```

Also create:

- data dictionary
- missingness report
- duplicate audit
- matching audit
- provenance notes

If historical repeated fare observations cannot be obtained:

1. exhaust reasonable lawful alternatives;
2. document failed paths;
3. construct the strongest real-data pilot possible;
4. do not fabricate synthetic historical quotes;
5. clearly state which hypotheses cannot yet be identified.

## Git Checkpoints

Make multiple meaningful commits if needed.

Examples:

```text
feat(data): add public flight outcome acquisition
feat(weather): add archived forecast pipeline
feat(fares): add fare observation collector
fix(cleaning): align flight and forecast timestamps
```

---

# 27. Stage 4 — Exploratory and Preliminary Identification Analysis

Stage 4 must be completed before stopping unless externally blocked.

---

# 28. Stage 4A — Data Quality

Analyze:

- missingness
- duplicates
- inconsistent fare products
- timestamp alignment
- weather matching
- flight identity consistency
- outcome matching
- suspicious price observations
- sampling artifacts
- source-specific artifacts

Create reproducible tables and figures.

Do not hide exclusions.

Document all filtering rules.

---

# 29. Stage 4B — Baseline Demand–Price Relationship

Estimate:

\[
P=\alpha+\beta_DD+\epsilon.
\]

Expected hypothesis:

\[
\beta_D>0.
\]

If this fails:

- inspect proxy validity
- test reasonable nonlinearities
- inspect DTD confounding
- add appropriate fixed effects
- inspect route/airline heterogeneity
- document the result honestly

Do not manipulate the model merely to recover the expected sign.

---

# 30. Stage 4C — Risk Intercept Effect

Estimate a model such as:

\[
P=
\alpha+
\beta_DD+
\beta_RR+
\gamma X+
\epsilon.
\]

Primary prediction:

\[
\beta_R>0.
\]

---

# 31. Stage 4D — Core Interaction

Estimate:

\[
P=
\alpha+
\beta_DD+
\beta_RR+
\beta_{DR}DR+
\gamma X+
\epsilon.
\]

Primary test:

\[
\boxed{\beta_{DR}<0}.
\]

Interpretation:

> Higher operational risk flattens the demand–price relationship.

Consider fixed effects when justified:

- route
- airline
- departure date
- flight
- DTD
- calendar time

Do not include fixed effects mechanically if they eliminate identifying variation.

---

# 32. Stage 4E — Visualization

Create clear visualizations of:

\[
P(D\mid R=\text{low})
\]

and:

\[
P(D\mid R=\text{high}).
\]

The hypothesized pattern is:

- higher intercept for high-risk observations
- flatter slope for high-risk observations
- crossover is possible

Also plot raw/partial relationships where useful so fitted models are not presented without context.

---

# 33. Stage 4F — Variance and Dispersion

Distinguish:

\[
\operatorname{Var}_D(P\mid R)
\]

from:

\[
\operatorname{Var}(P)
\]

and, where possible:

\[
\text{jump/disruption-driven variation}.
\]

Do not claim “bad weather lowers price volatility” unless the exact variance definition supports it.

---

# 34. Stage 4G — Flexibility Premium

If comparable fare products are available:

\[
\Omega=
P_{\text{flex}}
-
P_{\text{restricted}}.
\]

Analyze:

\[
\frac{\partial\Omega}{\partial R}.
\]

Treat this as:

- mechanism analysis
- secondary outcome
- possible alternate paper direction if empirically stronger

Document comparability assumptions between fare products.

---

# 35. Stage 4 Deliverables

Create analysis notebooks or scripts such as:

```text
notebooks/01_data_quality.ipynb
notebooks/02_baseline_demand_pricing.ipynb
notebooks/03_weather_interaction.ipynb
notebooks/04_variance_decomposition.ipynb
```

Notebooks are optional if scripts provide cleaner reproducibility.

Prefer reusable analysis code under `src/analysis/`.

Create:

```text
outputs/figures/
outputs/tables/
outputs/reports/
```

and:

```text
docs/findings/10_preliminary_results.md
docs/findings/stage_0_to_4_report.md
```

The consolidated report must include:

1. research question
2. verified literature gap
3. data feasibility
4. actual pilot dataset
5. demand proxy assessment
6. weather-risk construction
7. methods
8. preliminary results
9. figures
10. robustness concerns
11. competing explanations
12. limitations
13. what can be claimed
14. what cannot be claimed
15. recommendation for Stage 5

---

# 36. End-of-Stage-4 Decision

Assign one:

## A — Strong paper candidate

Evidence supports the mechanism, identification is plausible, and the data pipeline can scale.

## B — Promising but better data needed

The signal is meaningful, but measurement or identification remains weak.

## C — Interesting empirical observation, weak paper

Some result exists but novelty, robustness, or identification is insufficient.

## D — Stop

The data or signal does not support further investment.

Document the reasoning.

---

# 37. Research Integrity Rules

Do:

- verify sources
- cite primary evidence where possible
- preserve provenance
- distinguish fact from interpretation
- preserve negative results
- record failed acquisition routes
- record alternative explanations
- make analysis reproducible
- maintain public-repo hygiene

Do not:

- fabricate data
- reconstruct unavailable historical fares as though observed
- call DTD alone “demand”
- call realized weather “ex-ante risk”
- cherry-pick specifications
- suppress contradictory findings
- equate conditional variance with total volatility
- imply causal identification without design support
- write a polished paper before empirical feasibility is established

---

# 38. Cross-Machine Collaboration Protocol

This project may be opened by another user or agent on another machine.

Therefore every substantive session should begin with:

```bash
git status
git log --oneline --decorate -n 20
```

Then read:

```text
AGENTS.md
README.md
docs/INDEX.md
docs/project_state.md
```

Then inspect relevant stage documents.

Before ending a substantive session:

1. update durable docs;
2. update project state;
3. update the index;
4. run relevant tests/analysis checks;
5. inspect `git diff`;
6. commit meaningful completed work;
7. push when a configured public remote is available and doing so is safe;
8. leave clear next actions.

A future agent must be able to continue from Git alone.

---

# 39. Handoff Files

When a machine/agent handoff is substantial, create:

```text
docs/handoffs/YYYY-MM-DD-<short-topic>.md
```

Include:

- work completed
- relevant commits
- current branch
- current data status
- important decisions
- known issues
- exact next actions
- reproduction commands
- any local files intentionally not committed

Do not create redundant handoff docs for trivial sessions.

---

# 40. Branching Strategy

Prefer simple Git workflows.

If working directly on the default branch is appropriate and the repo is single-contributor, it is acceptable.

For substantial isolated work, create a branch such as:

```text
research/stage-1-literature
data/pilot-acquisition
analysis/weather-demand-interaction
```

Avoid branch proliferation.

Do not rewrite shared history.

---

# 41. Commit Cadence

Commit when a meaningful unit is complete.

Good examples:

```text
chore(repo): initialize research repository
docs(research): define falsifiable pricing hypotheses
docs(literature): assess adjacent airline pricing work
feat(weather): add forecast risk extraction
feat(data): add BTS outcome ingestion
analysis(pricing): estimate weather-demand interaction
docs(findings): summarize stage 4 results
```

Avoid vague messages:

```text
updates
work
changes
misc
final
```

---

# 42. Public GitHub Readiness

Before first public push, inspect for:

- secrets
- personal paths
- private notes
- copyrighted datasets
- large binaries
- credentials
- accidental notebook outputs containing sensitive data
- caches
- browser state
- local virtual environments

The `.gitignore` should cover typical files such as:

```text
.env
.env.*
.venv/
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.DS_Store
Thumbs.db
```

Add data-specific ignores as needed.

Do not ignore reproducibility metadata.

---

# 43. Suggested First Execution Sequence

The agent should begin by:

1. inspect current directory and repository state;
2. initialize Git only if not already initialized;
3. inspect existing files before overwriting anything;
4. create or update `AGENTS.md`;
5. create `.gitignore`;
6. create `README.md`;
7. create `docs/INDEX.md`;
8. create `docs/project_state.md`;
9. create minimal research directory structure;
10. commit repository governance/bootstrap;
11. execute Stage 0;
12. commit Stage 0;
13. execute Stage 1;
14. commit Stage 1;
15. execute Stage 2;
16. commit Stage 2;
17. execute Stage 3;
18. commit meaningful pipeline/data milestones;
19. execute Stage 4;
20. run verification;
21. write consolidated report;
22. update index/state;
23. commit final Stage 4 artifacts;
24. push to public remote if configured and safe.

---

# 44. Initial Bootstrap Commit

A suitable first commit is:

```text
chore(repo): initialize airline weather pricing research
```

It should include only clean repository governance and project scaffolding, not unrelated work.

---

# 45. Verification Before Claiming Completion

Before stating Stage 4 is complete:

- run test suite;
- rerun core analysis pipeline from reproducible inputs;
- verify expected output files exist;
- inspect logs/errors;
- inspect `git status`;
- inspect final diff;
- verify `docs/project_state.md` is current;
- verify `docs/INDEX.md` contains all durable documents;
- verify no secrets are tracked;
- verify public-repo-safe status.

Evidence must precede completion claims.

---

# 46. Final Execution Instruction

You are the primary autonomous research/coding agent for this repository.

You have full repository access and may use all non-destructive Git operations.

Execute the research through Stage 4.

Do not depend on prior conversation history.

Write all durable context into Git-controlled repository documentation.

Use Git actively and responsibly.

Never attribute commits to Codex, ChatGPT, any AI model, or any model/version as author or co-author.

Do not destroy existing work or rewrite shared public history.

When information is important enough to affect future research, implementation, interpretation, or collaboration, document it in-repo.

At Stage 4 completion, leave the repository in a state where a competent researcher on a different machine can clone it, read the repository docs, reproduce the work where source access permits, understand all major decisions, and continue without access to the original conversation.
