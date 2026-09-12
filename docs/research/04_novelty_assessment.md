# Stage 1 novelty assessment

## Decision

**B — Incremental but defensible, conditional on obtaining data that actually observe the proposed mechanism.**

The classification applies to the original question: whether ex-ante operational/weather risk changes the relationship between a demand state and a quoted airline fare. The search found strong adjacent literatures and one terminologically close operational-risk pricing paper, but no verified study in the 22-source set estimates this precise interaction using quote-time risk information. That is evidence of a plausible gap, not proof of absence.

The currently selected DB1B quarterly aggregate redesign receives a weaker assessment: **B/C boundary, leaning C if framed as “delays or weather affect average fares.”** Forbes (2008), Britto, Dresner, and Voltes (2012), and Zou and Hansen (2014) already estimate reliability/delay effects on fares, while Borenstein and Rose (1994) and later work establish aggregate fare dispersion and its relationship to market structure. A DB1B study can still be useful as a replication, extension, heterogeneity analysis, or measurement contribution, but it cannot inherit the original mechanism's novelty.

## What is already substantially covered

### Demand, capacity, and dynamic fares

Revenue-management theory has long derived prices and availability from stochastic demand, remaining capacity, time to deadline, and network opportunity cost (Gallego and van Ryzin 1994, 1997; Dana 1999). Flight-level empirical research observes fare and seat states directly and finds that fares respond to inventory, rival capacity, anticipated sales, and demand shocks (Escobari and Gan 2007; Clark and Vincent 2012; Escobari 2012). Williams (2022) structurally separates stochastic demand shocks from changing willingness to pay and estimates welfare counterfactuals. A new paper cannot claim novelty merely for showing that higher demand, fewer seats, or shorter time to departure is associated with higher fares.

### Fare dispersion and restrictions

Borenstein and Rose (1994) establish large within-route fare dispersion, and Stavins (2001) shows that advance-purchase and stay restrictions have measurable price effects. Fiig, Le Guen, and Gauchet (2018) explain how modern offer systems aim to move beyond filed booking-class prices to continuous, contextual pricing. Consequently, DB1B dispersion is not itself a novel outcome, and heterogeneous tickets must be treated as differentiated products rather than repeated observations of one homogeneous fare.

### Refundability and option-like flexibility

Escobari and Jindapon (2014) already model and test refundable versus non-refundable tickets as screening contracts under individual demand uncertainty. Mason (2006) and Graham, Garrow, and Leonard (2010) document usage of changes, refunds, and exchanges. Chen and Chen (2019) model a fare-lock option. A flexibility-premium paper would need a new risk dimension, product-level contract data, or stronger identification; a generic refundable-minus-restricted comparison is already substantially done.

### Reliability and fares

Forbes (2008) provides quasi-experimental evidence that worsened delay quality can lower fares. Britto, Dresner, and Voltes (2012) and Zou and Hansen (2014) find that lagged or airport delay can raise fares through operating-cost channels while also affecting demand or frequency. These different signs reflect competing demand-quality and cost-supply mechanisms. A new aggregate regression of realized delay on fare would sit squarely in an existing literature and would need a credible extension to be defensible.

### Disruption decisions under forecast uncertainty

Rosenberger, Johnson, and Nemhauser (2003) model aircraft recovery after disruptions. Lee, Marla, and Jacquillat (2020) use partial probabilistic forecasts of airport congestion in a proactive/reactive airline recovery model. Ex-ante operating uncertainty is therefore not a wholly new airline decision variable. The narrower open link is whether and how that risk reaches the passenger offer and modifies demand-based pricing.

### “Operational risk” in airline ticket pricing

Bergey and Moon (2009) explicitly combine operational value at risk, expected shortfall, uncertain demand, seat allocation, and discount-ticket strategy. This source rules out language such as “the first study of operational risk and airline ticket pricing.” Its risk object is simulated profit downside, not a forecast probability of weather delay or cancellation. Its demand input helps generate profit risk; the paper does not estimate how an observed operational-risk state changes the marginal effect of demand on quoted prices.

## The defensible gap

The narrow candidate contribution is a three-way alignment of measurement and timing:

1. **Price:** a fare offer observed at a known query timestamp for a specific flight and product.
2. **Demand state:** a defensible contemporaneous indicator such as remaining fare-class inventory, recent booking velocity, or a validated latent demand measure, rather than days to departure alone.
3. **Ex-ante operational risk:** a forecast vintage available at the same query timestamp and shown to predict later disruption.

The estimand would ask whether risk changes the demand-price gradient, for example

\[
P_{ifqt}=\alpha+\beta_D D_{ifqt}+\beta_R R_{ifqt}+\beta_{DR}(D_{ifqt}R_{ifqt})+\gamma X_{ifqt}+\varepsilon_{ifqt},
\]

where (i) indexes itinerary/flight, (f) fare product, (q) quote time, and (t) departure. The primary hypothesis (eta_{DR}<0) is not established by the reviewed papers. The design would also have to distinguish a risk premium ((eta_R>0)) from quality discounting ((eta_R<0)), inventory protection, expected disruption cost, endogenous schedule padding, and selection of travelers into routes or products.

This gap is incremental because every component has close prior work: demand shocks and seat-state pricing; reliability effects on fares; probabilistic disruption management; and option-like fare flexibility. The combination is potentially defensible because those components have not been joined in a verified empirical quoted-fare design in this review.

## Why DB1B does not identify the original gap

DB1B is a quarterly sample of completed tickets, coupons, and market itineraries. It does not contain the shopping query timestamp, quote history, fare products offered but not chosen, remaining seat inventory, or archived forecast that existed when the price was offered. Its passenger counts are realized sales, jointly determined with fare, service, capacity, and competition. It therefore cannot estimate the displayed flight-level relationship represented above.

An aggregate carrier-market-quarter model could estimate something like

\[
\overline{Fare}_{cmq}=\alpha+\theta Q_{cmq}+\delta Z_{cm,q-1}+\phi(Q_{cmq}Z_{cm,q-1})+\Gamma X_{cmq}+u_{cmq},
\]

where (Q) is ticketed quantity and (Z) is lagged reliability or a long-run exposure measure. That interaction is between equilibrium quantity and an aggregate route attribute. It is not the structural derivative of quote price with respect to demand under a known flight-risk state. Without an instrument, simultaneous system, natural experiment, or structural model, (	heta) and (phi) are associational.

Realized weather during the departure quarter cannot be called quote-time forecast risk. A lagged reliability measure may be information available to customers and airlines, and a climatological exposure may represent persistent route risk, but each changes the research question. Those designs should be positioned as extensions of the delay/reliability-fare literature, with the original hypothesis recorded as not identifiable.

## Classification by feasible paper framing

| Candidate framing | Classification | Basis |
|---|---|---|
| Quote-time operational/weather risk moderates demand-based flight fare pricing | **B — Incremental but defensible** | No exact empirical interaction verified; many close components mean the contribution must rest on aligned timing, measurement, and identification. |
| Quote-time risk changes the Flex-minus-restricted premium | **B — Incremental but defensible** | Refund/flex option value is established, but operational-service risk is a distinct untested state if comparable offers can be observed. |
| Lagged route reliability affects DB1B average fare and traffic | **C unless materially extended** | Britto et al. and Zou & Hansen already estimate delay, airfare, and demand/frequency channels. |
| Weather exposure affects quarterly DB1B fare dispersion | **B/C boundary** | The exact exposure/dispersion pairing may be less studied, but causal interpretation is weak and fare-composition confounding is substantial. |
| Realized departure weather interacted with quarterly passengers explains fare | **C / invalid for original claim** | Timing does not represent ex-ante information and passengers are an endogenous equilibrium outcome. |

## Conditions that could move the judgment

The original mechanism could move toward **A** only after a broader systematic search confirms the gap and a dataset observes repeated comparable quotes, demand state, and archived forecasts with credible variation. Novel data alone would not establish causal novelty, but it could make a strong measurement contribution.

The judgment should move to **C** if further searching finds a study that jointly observes airline quote prices, contemporaneous inventory or booking demand, and forecast disruption probability and estimates their interaction. It should also move to **C** for the DB1B redesign if the final model amounts to a direct repeat of aggregate delay-fare or delay-demand equations without new identification, data scope, or mechanism evidence.

## Required claim language

Defensible wording:

> In a targeted review of 22 verified primary studies, we found extensive evidence on demand-responsive airline pricing, reliability effects on fares, and stochastic disruption management, but no study in the reviewed set that estimates whether quote-time operational risk changes the demand-price gradient for a specific flight. This is a bounded literature finding, not proof that no such study exists.

Wording to avoid:

- “No prior research links operational risk and airline pricing.”
- “This is the first weather-aware airline pricing study.”
- “DB1B measures quoted fares, demand shocks, or ex-ante risk.”
- “The interaction causally identifies risk-adjusted pricing” without a design that supports that claim.

The detailed evidence and primary links are in [the literature review](03_literature_review.md) and `literature/literature_master.csv`.
