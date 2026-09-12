# Stage 5: expanded evidence and an identification boundary

2026-09-12. Extension of the preserved Stage 0-4 assessment.

## Finding and decision

The defensible conclusion is about identification: **these quarterly sources
cannot determine the sign of the original quote-time demand-risk interaction
without additional identifying assumptions and aligned information.** More data,
independent capacity measurements, and a cleaner ticket product do not supply the
missing quote-time joint distribution. This is not a finding of no causal effect.
The formal argument is in [the identification assessment](../methods/stage5_identification.md).

The empirical extension reinforces caution. The aggregate interaction remains
mostly positive, opposite the proposed negative sign, but varies substantially
with geography, quantity measurement, and seasonal controls. Primary and one-way
baseline intervals all cross zero, including the new temporal holdout. Decision C
remains appropriate: useful descriptive evidence, insufficient for the proposed
mechanism paper. Neither a favorable nor an opposite aggregate sign identifies it.

## Data added and checked

Four additional DB1B archives contain Market and Ticket for 2025Q1/Q2. Three BTS
T100 annual extracts cover 2023-25; seven ERA5 responses extend the original airports
through 2025. No Coupon archive was downloaded. Ticket.Coupons supports the one-way
product check; BTS describes Coupon.FareClass as carrier-defined and not recommended
for analysis, so it cannot establish a comparable flexibility premium. See the
[source verification](../data/stage5_source_extensions.md) and tracked manifests.

The extension reprocesses 77,949,326 national Market records over ten quarters,
retaining all 42 non-self directions among ATL, DEN, DFW, JFK, LAX, ORD, SEA, with
AA/DL/UA/WN reporting carriers. It is a seven-airport network, not a national sample.
Rules remain credible dollar fares, positive passenger weights, USD20-2000,
non-bulk fares, one market coupon, and at least 30 sampled passengers per cell.

| Sample | Cells | Reporting-carrier/routes | Contributing Market records | Sampled passenger weights |
| --- | ---: | ---: | ---: | ---: |
| Primary | 905 | 94 | 932,371 | 2,853,718 |
| One-way single-ticket-coupon | 873 | 91 | 187,116 | 797,666 |

These are alternative overlapping samples; do not add their passenger weights or
call them unique people/population totals. Training has 725 primary cells and the
holdout 180. All 1,778 product cells match positive route capacity and complete risk.
The one-way records have zero market-versus-itinerary fare discrepancies, including
before the minimum-cell-size filter. This removes proration for that product, but
not ticket selection, ancillary-fee omissions, inventory, or timing differences.

T100 sums service class F across all operating carriers at route-quarter level,
avoiding false matches between DB1B reporting carriers and regional operators.
Available seats, passengers, scheduled/performed departures, load factors and
service ratios are retained. Scheduled-minus-performed departures are not a
weather-cancellation measure; additional operated service can make the difference
negative. All twelve months are present in each annual input. Only 2025Q1/Q2 enter
the fare panel, avoiding the DB1B-to-DB1C break after June 2025.

## Predeclared results

The [plan](../methods/stage5_plan.md) was committed before fitting. The quantity
reference uses 2023-24 primary data only. Holdout coefficients are refit on 2025Q1/Q2;
this is temporal stability assessment, not forecasting unknown year-quarter effects.

Interaction estimates below are dollars per log-traffic point per unit risk
fraction. Intervals use approximate CR1 t inference with 21 undirected route pairs.
Routes share only seven airports, so cross-pair dependence remains and these are
not confirmatory confidence statements. No multiple-testing adjustment was used;
isolated small p-values are not treated as discoveries.

| Primary specification | Interaction | Approximate95% interval |
| --- | ---: | ---: |
| Training, route/carrier and period effects | 50.58 | [-38.02,139.19] |
| Training, add log route seats | 55.82 | [-30.85,142.49] |
| Training, route/carrier/season and period effects | 248.45 | [-90.09,587.00] |
| Training, seasonal effects plus seats | 112.90 | [-229.00,454.80] |
| Holdout, standard effects | 33.88 | [-112.42,180.18] |
| Full ten quarters, standard effects | 36.47 | [-39.47,112.41] |
| Full ten quarters, seasonal effects | 125.46 | [-61.79,312.71] |

The original12-route pilot estimate was+227.55. Expanding directions among the
same airports reduces the training estimate to +50.58; this is a material geographic
sensitivity. Leaving ORD out gives -1.19, whereas leaving LAX out gives +180.43.
Every leave-one-airport standard and seasonal interval crosses zero.

One-way baseline interactions are +94.80 for training, +157.25 for holdout, and
+52.62 for the full standard-effect sample; all intervals cross zero. Training
one-way with seats produces+104.13 with an approximate interval[3.61,204.64], but
this isolated result is not stable under stronger seasonal controls or in the
holdout. The whole-ticket check does not rescue the proposed negative interaction.

Replacing sampled carrier traffic with T100 total-route passengers changes the
quantity construct and gives a training standard-effect interaction+424.97
[153.49,696.44]. Under seasonal effects it is +353.43[-568.19,1275.05]; the holdout
is +219.92[-945.53,1385.36]. This sensitivity is evidence against treating an
aggregate quantity proxy as an identified demand state. Both quantity and capacity
are equilibrium outcomes; seats are not an instrument or a guaranteed safe causal
control.

The primary training risk effect at the reference quantity is-16.29 dollars per
10 percentage points of exposure under standard effects[-27.71,-4.87]. Under
seasonal effects it is-19.86[-83.35,43.64]. Even the apparently precise negative
standard-effect association does not survive the stronger seasonal comparison as
a precise statement. Exposure is not a cancellation probability.

## What the seasonal test establishes

Training risk has raw standard deviation 0.03616, falling to 0.02126 after standard
effects and 0.005319 after route/carrier/season effects: a 75% further reduction in
standard deviation. There are only two training years, so the latter comparison
uses changes from replacing one year in a three-year historical window.

For a fixed 2020-22 climatology, the residual risk is exactly zero under
route/carrier/season effects. This is algebraic absorption, not an estimated zero
weather effect. The rolling-risk coefficient uses a different, narrow source of
variation. In the two-quarter 2025 holdout, each route/carrier/season occurs once;
all eight seasonal specifications are saturated and genuinely unestimable.

The implementation initially rejected redundant nuisance dummy columns even in
training. A reviewed pivoted-QR basis now preserves their full span while retaining
all focal regressors. Offline tests verify slope equivalence to explicit dummies
and rejection of truly absorbed focal columns. Final output records 62 attempts:
54 estimates and eight saturated holdout failures. No failed model was silently
dropped or assigned a zero coefficient.

## Stopping decision

This pass meets the user's strong-argument criterion: the original interaction is
not identified by these quarterly observables. The expanded empirical checks also
show why simply enlarging this regression is not a promising way to resolve it.
This does not claim that all public data or all possible econometric methods have
been exhausted. Further seasons, thresholds, or p-value searches cannot recover
the absent quote-time joint moments without an explicit new identification design.

The next scientific investment would be aligned offered fares, query/departure
times, product terms, contemporaneous forecast vintages, and a defensible source
of demand variation. No new paid service, credential request, prospective
collection, or FR24 expenditure was initiated. Zero FR24 calls/credits were used.

## Reproduction and durable outputs

See [Stage5 structure and reproduction](../methods/stage5_reproduction.md) for the
source-to-output mapping, commands, audited assumptions, and verification record.
Stage0-4 tables and figures remain unchanged. The full coefficient table and every
model status are retained under `outputs/stage5/`, together with input matching,
product exclusions, seasonal support, same-season changes, and the comparison
figure. The exact final rebuild verification is recorded separately after rerun.
