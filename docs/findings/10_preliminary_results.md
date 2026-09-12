# Preliminary results

Date: 2026-09-12. Exploratory quarterly DB1B design, not the original quote-time test.

The real pilot contains 222 route/carrier/quarter cells on twelve routes in
2023-2024. Original H1 and H2 are **not estimable as specified** because the source
does not contain quote timestamps, contemporaneous demand states, or matched
forecast vintages. The aggregate analogues do not show the predicted signs.

| Core fixed-effect model term | Estimate | Approximate 95% interval |
| --- | ---: | ---: |
| Log-traffic slope at risk zero | -31.04 USD | [-62.97, 0.89] |
| Risk effect per 10 percentage points at mean log traffic | -20.52 USD | [-37.15, -3.88] |
| Log-traffic x risk coefficient, risk expressed as a fraction | +227.55 USD | [-32.23, 487.33] |

Traffic-slope units are USD per natural-log point of sampled passengers; interaction
units are USD per log point per unit risk fraction. A 10pp risk increase corresponds
to a +22.75 USD-per-log-point slope change. Fares are passenger-weighted prorated
DB1B market components, not separately observed market transaction quotes.

The expected aggregate risk sign was positive, and interaction sign negative.
The observed signs are reversed. These are associations in jointly determined
traffic and fares, not evidence that weather causally reduces fares or that the
original mechanism has been disproved. Twelve route clusters make CR1/t intervals
approximate and fragile; all p-values are exploratory.

The pooled fare–traffic slope is +9.80, versus -1.02 with route/carrier and calendar
fixed effects. The benign-risk FE slope is -39.59. This sensitivity is consistent
with confounding and equilibrium quantity; it does not by itself invalidate the
measurement of passenger traffic.

At risk quartiles 0.0562 and 0.1026, conditional slopes are -18.26 and -7.70 USD per
unit log traffic. Both approximate intervals cross zero. The fitted slope becomes
less negative, not a positive demand-price slope flattened by a negative interaction.
Passenger weighting, log fares, broader fare bounds, maximum endpoint risk,
balanced cells, and leaving each hub out preserve the positive interaction point
sign, but intervals and magnitudes vary materially. All specifications are published.

The weather index predicts realized adverse weather in the airport/calendar FE
validation. Its cancellation association is positive but imprecise: a 10pp index
increase associates with a 0.67pp cancellation increase, interval [-0.24, 1.59]pp.
There are only seven airport clusters. This does not establish a calibrated
operational-failure probability or strong cancellation validation.

Fixed-reference fitted demand-component variances are 316.90 and 56.38 USD squared
at low/high risk, with broad approximate confidence sets including zero. This
reduction occurs because a negative slope approaches zero; it does not rescue H2
or establish lower total fare volatility. Within-cell fare dispersion and between-
cell variance are different outputs. Flexibility premiums are not estimable.

Recommendation: **C — Interesting empirical observation, weak paper.** Do not
scale this specification or spend the reserved FR24 credits on it. A next stage
should first acquire a defensible demand shifter/quantity design or aligned quote
data, and address the close reliability-fare literature. See the consolidated
[Stage 0-4 report](stage_0_to_4_report.md) for scope, evidence, and next steps.
