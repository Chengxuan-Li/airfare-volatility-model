"""Checked exploratory regressions and interaction interpretation."""
import numpy as np
import statsmodels.formula.api as smf


def fit_checked(formula, data, weights=None, cluster=None):
    model = smf.ols(formula, data=data, missing='raise') if weights is None else smf.wls(
        formula, data=data, weights=weights, missing='raise')
    rank = np.linalg.matrix_rank(model.exog)
    if rank < model.exog.shape[1]:
        raise ValueError(f'design rank deficient: {rank}/{model.exog.shape[1]}')
    if np.linalg.cond(model.exog) > 1e12:
        raise ValueError('design numerically near-singular; condition number > 1e12')
    if len(model.endog) <= model.exog.shape[1]:
        raise ValueError('no residual degrees of freedom')
    if cluster:
        return model.fit(cov_type='cluster', cov_kwds={'groups': data[cluster]}, use_t=True)
    return model.fit(cov_type='HC3')


def marginal_effects(params, demand, risk):
    return {'demand_slope': params['demand_c'] + params['demand_c:risk'] * risk,
            'risk_effect': params['risk'] + params['demand_c:risk'] * demand}
