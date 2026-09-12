# Aggregate analysis and interpretation

Read the Stage 0 charter and hypotheses before interpreting output.

Primary model: fare_mean ~ centered log sampled passengers * historical seasonal
risk + route/carrier fixed effects + year-quarter fixed effects. Reference demand
is the unweighted mean log traffic in the primary analysis cells, held fixed in
robustness samples. Report its exponent only as a sampled-passenger reference.

The risk coefficient is a price association at reference log traffic. Marginal
traffic slopes combine the main and interaction coefficients; risk effects combine
risk and interaction at chosen traffic values. Confidence intervals use covariance
contrasts, not independent coefficient standard errors. Price effects for risk
are expressed per ten-percentage-point increase in the exposure index.

All fare models cluster by directional route (12 in full sample), using cluster
finite-sample correction and t inference with cluster-count minus one degrees
of freedom. There are few clusters; intervals are approximate and exploratory,
not reliable confirmatory hypothesis tests. Leave-one-hub-out fits have fewer.
The effective risk support is route-quarter, not each carrier record independently.

Every model exports sample size, design rank, condition number, cluster count,
formula, fit status, R-squared, and inference degrees of freedom. Exact rank
deficiency, no residual degrees of freedom, or condition number above 1e12 aborts
that specification. A failed core model stops model reporting with diagnostics.
No coefficients are interpreted from singular or absorbed designs.

Prespecified fits: pooled and fixed-effect traffic baselines; benign-risk baseline;
additive risk; full interaction; passenger-weighted WLS; log fare; broader fare
bounds; maximum endpoint risk; balanced route/carrier support; leave each hub out.
They diagnose sensitivity, not multiple opportunities to select a favorable sign.

Weather validation uses 56 airport-quarter rows and seven airport clusters,
separately from the expanded fare panel. Pooled and airport/calendar FE models
relate lagged seasonal exposure to realized cancellation, delay, weather-attributed
delay, and adverse-weather shares. These are not causal validation designs.

Figures show both raw relationships and FE-adjusted observations. Fitted risk
curves hold route/carrier and calendar composition at the average sample mix.
They visualize an additive fixed-effect model, not literal quote prices for a
particular itinerary. The displayed traffic range may have sparse joint support;
consult cell support before extrapolating. Marginal-effect intervals are tabulated.

Dispersion: fitted demand-component variance holds a common log-traffic distribution
fixed and computes squared conditional slope times its variance. Separately report
variance of cell mean fares and mean within-cell fare variance. None is dynamic
flight repricing volatility, and no additive decomposition of total fare variance
into independent causal demand/weather components is claimed.

Flexibility premiums are not estimable: DB1B does not pair offered restricted and
flexible products at a common quote timestamp. Coupon fare-class fields cannot
repair that absence. Coupon is not downloaded because no selected computation
requires it; its schema/role is documented in feasibility work.
