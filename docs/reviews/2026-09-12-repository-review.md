# Repository and documentation review — 2026-09-12

Reviewed HEAD `08b00603d46272e182b9c7c5636c150d535b43cb` on
`codex/stage-5-robustness`, using `git diff main...HEAD` with baseline
`643859c85032cd0547b69a0bdceaa02f5a7fad2c`. Scope: repository operating rules,
research specification, Stage 0-5 methods/reports, acquisition and analysis code,
tests, compact outputs, and handoff consistency. Separate bounded reviewers
checked standards/code and specification/methodology. This was a review, not an
implementation pass; the two code findings below remain open.

Subsequent Stage 6 update: both P1 code defects below have now been fixed with
regression tests. See [current project state](../project_state.md) and the execution
ledger. The findings below preserve the reviewed commit's behavior.

## Standards

### P1 — Stage 0-4 reproduction checks unrelated Stage 5 inputs

`src/run.py:26-30` iterates every JSON manifest. The branch contains 39 manifests,
but the README's `python -m src.acquisition.batch --kind all` acquires only the
25 original inputs. The other 14 describe four 2025 fare archives, seven extended
weather responses, and three T100 extracts. The runner aborts on a missing
Stage 5 file before building the original pilot, violating the documented
standalone reproduction workflow and the operating contract's reproducibility rule.

Confirmed by invoking `src.run.main()` with a mock checksum reader accepting
original inputs and raising for extension inputs. The first failure was
`Origin_and_Destination_Survey_DB1BMarket_2025_1.zip`. No downloads were needed.
Scope verification to the original pipeline's explicit consumed input set and
test it in the presence of unrelated manifests.

### P1 — New downloads can silently replace committed provenance

`src/acquisition/download.py:45-70` validates a downloaded payload's format, then
renames it and writes a new manifest. When the target is absent but its committed
manifest exists, this branch does not compare the new checksum or request identity
to that manifest. A source revision can silently replace the input identity that
the README says protects the exact research data. The existing-cache branch does
perform checks; a fresh clone takes the vulnerable path.

Confirmed in temporary storage with a manifest for one JSON payload and a mocked
download returning a different valid payload. Acquisition succeeded and replaced
the saved checksum. Compare the completed temporary payload and request to the
existing manifest before promotion; intentional source revisions need an explicit
refresh workflow preserving the old provenance. T100's separate POST acquisition
re-enters the existing-target path, so the demonstrated case concerns direct
downloads such as DB1B and weather.

## Specification and documentation

### P2 — Supply-channel checks are specified more broadly than implemented

`docs/methods/stage5_identification.md:167-170` says: "Use T-100 in three nested
descriptive models" with scheduled departures/seats and performed departures,
and "Also model each capacity measure as an outcome of risk."
`src/stage5/analyze.py:22-24,93-98` includes log seats and a route-passenger
substitution, but no departure-control or risk-to-capacity outcome models. The
narrower `stage5_plan.md` matches that implementation. Reconcile the broader
identification note with the executed scope by explicitly marking these proposals
deferred, or implementing them under a separately declared follow-up. Their
absence does not undermine the quote-time non-identification argument.

### P2 — Small-cluster inference proposals lack an explicit disposition

`docs/methods/stage5_identification.md:239-244` directs the reader to "report CR1,
CR2 with contrast-specific Satterthwaite degrees of freedom, and a route-level
wild cluster bootstrap-t interval as parallel sensitivity results."
`src/stage5/analyze.py:66-79` reports CR1 only. The final report correctly calls
these intervals approximate and descriptive; this is a scope/documentation gap,
not an unsupported significance claim. Record CR2/bootstrap as deferred proposals
with the reason for stopping, or implement a separately declared follow-up. The
current narrow execution plan does not promise these additional estimators.

The saved results and their descriptive interpretation agree with the reviewed
Stage 5 analysis rerun. Original quote-time H1/H2 and flexibility premiums are
explicitly unavailable; the execution addendum permits that partial-pilot outcome.
The aggregate coefficients do not establish or refute the original causal
mechanism. No new substantive research-completion claim is made by this review.

The current-state document incorrectly retained an active publication blocker and
an uncommitted `.env.example` edit from the earlier execution. The review began
with a clean working tree, and a live `git ls-remote` returned the exact reviewed
HEAD for the research branch. Those current-state statements were corrected; an
update on the historical Stage 5 handoff preserves its original account while
pointing to the new evidence. A published branch does not prove local write access.

## Verification and limits

- `python -m pytest -q`: 21 passed on Python 3.13.9.
- Re-executed `src.stage5.analyze.main()` against the committed panel in temporary
  storage with `OPENBLAS_NUM_THREADS=1`. All 62 model attempts retained their
  status: 54 estimated and eight saturated seasonal holdout fits unavailable.
  Model/term order matched. Estimates, standard errors, interval endpoints, and
  p-values agreed at `rtol=1e-8, atol=1e-8`; the largest absolute difference was
  approximately `2.69e-9`. Tracked research outputs were not modified.
- All 15 recorded Stage 5 output hashes match this Windows working tree. The 14
  text-file hashes do not match Git's LF-normalized blobs; the PNG does. The saved
  byte-equality evidence is platform/newline-specific. A portable verification
  workflow should declare newline normalization or compare parsed numeric data
  with explicit tolerances, separately from byte identity.
- `pip install --dry-run --ignore-installed -r requirements.txt` resolved all
  pinned dependencies without installing them. The actual test/reanalysis
  environment has different package versions, so this is not verification in a
  newly installed pinned environment.
- All local Markdown links in README and docs resolved. No raw-data or `.env`/
  `.venv` paths are tracked. Credential contents were not read.
- No local raw inputs are present. Full acquisition/raw-pipeline reproduction,
  fresh raw checksum validation, and renewed literature/source verification were
  outside this review. Historical raw-build counts remain historical evidence.
- No paid service, FR24 request, or research-data download was used. Network
  checks were limited to the configured Git remote and package-resolution metadata.

Prioritize the two P1 reproduction fixes before another raw acquisition. The
scientific stopping decision remains C: an interesting descriptive observation
with insufficient identification for the original mechanism.

Finding counts: standards, two open P1 defects; specification, two P2 scope gaps.
The stale current publication/local-state documentation was corrected in this
review. Newline-specific hash verification is recorded as a portability limitation.
