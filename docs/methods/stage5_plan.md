# Stage 5: independent checks and identification limits

Declared 2026-09-12 before extension results. User authorizes autonomous work,
additional packages from the same free sources, regular commits, and stopping on
a strong defensible finding/argument or reasonable data/method exhaustion. Exact
prior token consumption is unavailable, so no invented numerical budget is used.

## Design and scope

Preserve Stage 0-4 outputs. New code and compact outputs live under `src/stage5/`
and `outputs/stage5/`; raw data remain ignored and provenance tracked. Use the
current checkout on `codex/stage-5-robustness` to retain cached national archives.
Preserve the pre-existing `.env.example` edit. No paid services or FR24 calls.

1. Reuse Market/Ticket 2023-24 but expand to all directed pairs among ATL, DEN,
   DFW, JFK, LAX, ORD, SEA, with AA/DL/UA/WN reporting carriers. This changes
   geographic support within the existing airport set, not national coverage.
2. Download Market/Ticket 2025 Q1/Q2 as a temporal holdout. Stop before the DB1C
   methodology break. Do not select specifications using holdout signs.
3. Keep primary record rules (credible dollar fare, no bulk, one market coupon,
   USD20-2000, positive passenger weights, cell minimum30). Add one-way,
   single-ticket-coupon sensitivity, verifying market fare against itinerary fare.
4. Acquire annual BTS T100 domestic segment data where verified. Sum scheduled
   passenger-service capacity/traffic across operating carriers at directed-route
   quarter level. Never equate regional operators to DB1B reporting carriers.
   Seats and traffic remain endogenous; they do not supply a demand instrument.
5. Extend ERA5 for the same airports through 2025. Keep the existing prior-three-
   years, same-season weather definition. Preserve original weather files.

## Models declared in advance

Use dollar mean fares, log sampled traffic centered at the training mean, endpoint
mean risk, and their interaction. Estimate training 2023-24, holdout 2025 Q1/Q2,
and full periods separately. Holdout fitting is coefficient stability assessment,
not a forecast with unknown future time effects. Report all attempted fits.

Compare route/carrier plus year-quarter effects to route/carrier/season plus
year-quarter effects. Add log route seats on a common matched sample; replace
sampled traffic with T100 route passengers as a sensitivity. Repeat for one-way
single-coupon fares. No significance-driven selection. Use undirected route
clusters, disclose their limited count and shared-airport dependence, and report
leave-one-airport-out sensitivity. Rank/conditioning failures are results.

For fixed 2020-22 seasonal exposure, establish whether route/carrier/season
effects absorb risk exactly; never interpret an absorbed coefficient as zero.
Show within-season variation for rolling exposure. Document why quarterly
transaction aggregates cannot identify quote-time weather/demand interactions.

## Execution and verification

- [x] Verify endpoints and acquire bounded cached inputs, with checksums.
- [x] Implement offline tests for product restrictions, capacity aggregation,
      absorbed effects, and coefficient equivalence to explicit dummy regression.
- [x] Stream raw records; save exclusion/join/coverage audits and compact panels.
- [x] Run every declared model and temporal/product/seasonal sensitivity.
- [x] Independently review identification and implementation; address findings.
- [x] Reproduce outputs, document results/structure/limitations, commit milestones,
      and attempt safe noninteractive publication.

Stopping requires substantive evidence or a rigorous identification argument,
not merely a favorable p-value. Expanded descriptive evidence cannot turn the
original quote-time mechanism into an identified causal claim.

Final verification: 21 offline tests pass; two full raw builds reproduce 15 derived
outputs byte-for-byte.62 attempts yield 54 estimates and eight saturated holdout
failures. Independent code and report reviews completed. Publication was attempted
noninteractively and failed because GitHub credentials are unavailable; all work
is committed locally. See the Stage5 report for the strong-argument stopping ruling.
