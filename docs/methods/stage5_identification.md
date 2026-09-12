# Stage 5 identification assessment

Date: 2026-09-12. This note evaluates what the completed quarterly DB1B pilot can
identify and specifies the strongest bounded extensions. It does not change the
Stage 0 estimand or promote the aggregate pilot to a causal design.

## Conclusion

Quarterly DB1B transaction moments do not identify the sign of the original
quote-level demand-risk interaction. The missing object is the joint distribution
of demand state and risk in the airline's information set when each fare was
quoted. Quarterly traffic, quarterly mean paid fare, and a historical seasonal
weather index do not recover that object. A positive, zero, or negative structural
interaction can therefore be consistent with the same observed aggregates after
changes in within-quarter selection, inventory, capacity, or unobserved supply and
demand shocks. This is observational equivalence, not evidence that the causal
interaction is zero.

The existing route-carrier and period fixed-effect model remains a useful
descriptive decomposition. Route-carrier-by-calendar-quarter effects provide a
stronger seasonal-confounding diagnostic, but the pilot then relies on very small
two-year changes in a rolling climatology. T-100 capacity and service measures can
probe a supply channel; they do not supply an exogenous demand shifter. No bounded
extension using these quarterly sources alone repairs the original identification
failure.

## The estimand and the observed moments

Let \(i\) index a quote or purchase occasion and \(c=(g,t)\) a
route-carrier-quarter cell. The original model contains

\[
 p_{ic}=a_c+\beta_D d_{ic}+\beta_R r_{ic}
       +\theta d_{ic}r_{ic}+u_{ic},
 \]

where \(d_{ic}\) is a demand or inventory state, \(r_{ic}\) is ex-ante risk in
the quote-time information set, and \(\theta=\beta_{DR}\) is the target. Averaging
over the transactions selected into a DB1B cell gives

\[
 E[p_{ic}\mid c]
 =a_c+\beta_D E[d_{ic}\mid c]+\beta_R E[r_{ic}\mid c]
 +\theta E[d_{ic}r_{ic}\mid c]+E[u_{ic}\mid c].
\]

Even observing both marginal means would be insufficient because

\[
 E[d_{ic}r_{ic}\mid c]
 =E[d_{ic}\mid c]E[r_{ic}\mid c]
  +\operatorname{Cov}(d_{ic},r_{ic}\mid c).
\]

The covariance is not determined by the marginal means. More fundamentally, this
pilot does not observe either quote-time marginal: sampled passengers are realized
equilibrium transactions, and lagged realized seasonal weather is not the forecast
or operational-risk information attached to a quote. Multiplying quarterly
traffic by seasonal exposure therefore does not aggregate the original interaction.
It creates a different cell-level regressor under untestable alignment and
within-cell composition assumptions.

Passenger weighting does not solve the problem. It estimates a mean among sampled
purchases, while the original pricing rule concerns offered fares conditional on
an information state. Purchases select on price, product terms, itinerary, and
traveler type. The DB1B fare is also a prorated market component of a purchased
itinerary rather than a repeated offer for a fixed product.

### Observational equivalence

Denote the observed cell outcome by \(Y_c\), observed traffic by \(Q_c\), and
seasonal exposure by \(R_c\). A cell regression represents

\[
 Y_c=A_g+T_t+b_QQ_c+b_RR_c+b_{QR}Q_cR_c+e_c.
\]

Without an exclusion restriction or a model that fixes the conditional mean of
the omitted pricing, inventory, product-composition, and supply terms, any proposed
value \(b_{QR}^{*}\) can fit the same observed moments by redefining

\[
 e_c^{*}=Y_c-A_g-T_t-b_QQ_c-b_RR_c-b_{QR}^{*}Q_cR_c.
\]

The fixed effects restrict some mean differences, but do not supply the missing
orthogonality condition \(E[e_c^{*}\mid Q_c,R_c]=0\). Simultaneous fare and traffic
determination makes that condition especially implausible. The aggregate
interaction's sign can also differ from a within-quote interaction through
aggregation and selection. Consequently:

- failure to reject a zero aggregate coefficient is not a causal null;
- a coefficient with the proposed sign would not identify the original mechanism;
- the observed opposite sign does not refute the original mechanism; and
- more quarters improve precision only after a defensible identifying restriction
  exists.

## Fixed-effect designs and the variation they use

### Route-carrier and year-quarter effects

The completed specification uses route-carrier effects \(A_g\) and year-quarter
effects \(T_t\). Its risk coefficient is identified from exposure remaining after
removing each route-carrier mean and each national period mean. This comparison
still combines two sources:

1. persistent route-by-season differences, such as winter exposure and seasonal
   fare composition; and
2. changes in the three-year rolling historical window between target years.

Period effects remove shocks common to all routes in a quarter. They do not remove
route-specific seasonality. The existing audit reports a residual risk standard
deviation of 0.01885 under these effects, compared with 0.03573 before them.

### Route-carrier-by-season and year-quarter effects

Adding route-carrier-by-calendar-quarter effects compares, for example, a given
carrier's ORD-ATL first-quarter cell in 2023 with the same season in 2024. This
absorbs fixed route-specific seasonality and is the strongest readily implemented
seasonal-confounding check. It changes the question: identification comes only
from replacing one year in the three-year historical weather window and from the
associated traffic change.

In the saved 222-cell panel, residualizing risk on route-carrier-by-season and
year-quarter effects reduces its standard deviation to approximately 0.00565.
There are only two target years. This specification is therefore a useful stress
test, not a credible stand-alone design: a weak or unstable estimate may reflect
little variation, while a stable estimate remains subject to endogenous traffic
and time-varying capacity, competition, and composition.

The equivalent two-year first-difference presentation is valuable for transparency.
For each observed route-carrier-season, report the 2024-minus-2023 changes in fare,
traffic, and rolling risk and show their support. It should agree algebraically
with the corresponding fixed-effect comparison after common period changes are
handled.

### Fixed preperiod climatology

A fixed climatology built entirely from a common preperiod, such as 2020-2022 for
both target years, prevents the exposure definition from changing mechanically
with the target year. Under route-carrier-by-season effects, its risk main effect
is exactly absorbed because the climatology is constant within each
route-carrier-season. An interaction between traffic and fixed climatology can
remain estimable, but it measures heterogeneity in the endogenous aggregate
fare-traffic association across climates. It is not evidence that a changing
quote-time risk state alters a pricing response.

Report both designs because their difference is informative. The rolling measure
asks whether small updates to historical exposure covary with outcomes; the fixed
measure asks whether fare-traffic associations differ across persistently different
seasonal climates. Neither is the original forecast-risk estimand.

## What T-100 capacity can and cannot do

BTS T-100 Domestic Segment provides monthly non-stop segment measures including
scheduled departures, performed departures, and available seats. These measures
can improve the description of route supply and reveal whether the weather index
predicts capacity or service responses. They are independently reported from DB1B,
which helps measurement triangulation.

Capacity remains chosen in response to expected demand, competition, costs, and
expected operating conditions. Performed departures and seats can additionally
reflect realized disruption. Controlling for them therefore does not make DB1B
traffic an exogenous demand state. If operational risk affects capacity, a
contemporaneous capacity control may also block part of the total risk-price path.

Use T-100 in three nested descriptive models: no capacity control; scheduled
departures and available seats; then performed departures as a separate sensitivity.
Also model each capacity measure as an outcome of risk. Divergence across the
models diagnoses a supply channel or post-treatment sensitivity. It does not pick
a preferred causal estimate. Lagged capacity can be reported, but airline planning
against expected demand means it is not automatically a valid instrument or an
exogenous control.

## Strongest bounded falsification and robustness work

The following tests are implementable with public quarterly data and should be
specified before examining their coefficient signs.

1. **Expose the identifying variation.** Report raw and residualized standard
   deviations, within route-carrier-season changes, leverage, condition numbers,
   and counts of groups spanning common risk and traffic support. Plot outcomes
   against the residualized interaction. Do not interpret a coefficient supported
   by a few routes or cells.
2. **Seasonal absorption.** Estimate the existing route-carrier plus period model,
   the route-carrier-by-season plus period model, and the transparent two-year
   first-difference form. Large movement is evidence of seasonal confounding;
   stability is robustness evidence only.
3. **Freeze the risk definition.** Compare the rolling index with one common,
   fully preperiod climatology. Decompose rolling exposure into the fixed
   route-season mean and its target-year update. This separates persistent climate
   heterogeneity from the small rolling-window innovation.
4. **Test timing diagnostics.** Use a future rolling-window update as a negative-
   timing control and report its correlation with the intended exposure. A similar
   coefficient weakens a temporal story, although persistence and anticipation
   mean this is not a sharp causal falsification.
5. **Probe the supply channel.** Add T-100 scheduled capacity, then performed
   capacity, and estimate risk-capacity associations. Treat attenuation or sign
   changes as mechanism sensitivity rather than correction of endogeneity.
6. **Hold composition fixed.** Retain a balanced route-carrier panel, reweight to a
   fixed route-carrier distribution, compare passenger-weighted and cell-weighted
   fits, and report fare and itinerary composition where available. This tests
   whether changing transaction shares drive the aggregate interaction.
7. **Test local influence and network dependence.** Continue leave-one-origin-out
   fits and add leave-one-route-out coefficient and leverage summaries. Routes
   sharing an endpoint can share weather and congestion shocks, so route clusters
   are not necessarily independent.
8. **Vary defensible measurement choices as a family.** Compare mean versus maximum
   endpoint exposure, alternative predeclared weather thresholds, and two-, three-,
   and five-year lag windows. Publish every attempted member and its support. A
   specification search cannot create identification.
9. **Use label permutations only as diagnostics.** Permuting exposure innovations
   across route-seasons can show whether the observed statistic is unusual relative
   to arbitrary relabelings. Weather exposure was not randomly assigned, routes
   share airports, and there are only three focal origins, so permutation results
   are not design-based causal p-values.

No test in this list turns equilibrium traffic into an external demand shifter.
A valid next design needs either aligned repeated offers, inventory or booking
states, and archived forecast vintages, or an external demand shifter with a
credible exclusion restriction plus a model of supply and capacity.

## Inference with few and connected clusters

The primary route-clustered CR1 intervals with \(G-1=11\) reference degrees of
freedom are appropriately labelled approximate. Ordinary cluster-robust methods
rely on many independent clusters, and small-cluster procedures address inference
error rather than endogeneity. [Cameron and Miller (2015)](https://doi.org/10.3368/jhr.50.2.317)
review the choice of clustering level, multiway dependence, and few-cluster
problems. [Cameron, Gelbach, and Miller (2008)](https://doi.org/10.1162/rest.90.3.414)
show that wild cluster bootstrap-t methods can improve finite-sample inference in
some settings with few clusters. [Pustejovsky and Tipton (2018)](https://doi.org/10.1080/07350015.2016.1247004)
develop CR2 bias reduction and Satterthwaite-type tests for fixed-effect models.
Their [2023 corrigendum](https://doi.org/10.1080/07350015.2023.2174123) limits a
computational shortcut for weighted/generalized least squares, so use a verified
general implementation for the passenger-weighted sensitivity rather than carrying
over the ordinary-least-squares shortcut.

For the main and marginal interaction contrasts, report CR1, CR2 with contrast-
specific Satterthwaite degrees of freedom, and a route-level wild cluster
bootstrap-t interval as parallel sensitivity results. Do not select among them by
significance. Report bootstrap weights, replications, seed, null-imposition rule,
and interval inversion method. With twelve routes, sparse effective support, and
unequal influence, none warrants a confirmatory threshold claim.

Routes sharing airports create connected-dyad dependence that one-way route
clustering does not capture. [Aronow, Samii, and Assenova (2015)](https://doi.org/10.1093/pan/mpv018)
derive a dyadic robust variance estimator for repeated and directed dyads. It is a
conceptually relevant sensitivity, but seven airports and twelve routes are too few
to treat its asymptotics as reliable. Two-way route-period clustering also has only
eight periods. Use these estimates, if computed, as dependence diagnostics and
pair them with leave-one-hub/route stability rather than presenting them as a cure.

## Decision rule

The quarterly extension can strengthen or weaken the descriptive result. It
cannot change the original status from “not estimable.” Retain the current weak-
paper assessment unless new data recover quote times, comparable offers, a demand
or inventory state, and the risk information set, or a separate design supplies
credible demand and supply exclusions. A precisely estimated quarterly interaction
alone does not meet that standard.

## Source scope

The econometric recommendations above were checked against the linked author,
publisher, or institutional primary records. The T-100 field interpretation is
from the official [BTS T-100 Domestic Segment table](https://transtats.bts.gov/DL_SelectFields.aspx?QO_fu146_anzr=Nv4+Pn44vr45&gnoyr_VQ=FIM)
and [BTS reporting guide](https://www.bts.gov/sites/bts.dot.gov/files/docs/explore-topics-and-geography/topics/airlines-and-airports/219466/t100-guide-april-2007.pdf).
This is a bounded identification assessment, not an exhaustive review of panel or
small-cluster econometrics.
