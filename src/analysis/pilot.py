"""Predeclared descriptive models, uncertainty, diagnostics, and figures."""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analysis.models import fit_checked
from src.config import FIGURES, HUBS, TABLES

FE = 'C(route_carrier) + C(period)'
CORE = 'fare_mean ~ demand_c * risk + ' + FE
CAUTION = 'Approximate CR1 t inference; few clusters; exploratory, not confirmatory'


def contrast(result, terms):
    vector = np.array([terms.get(name, 0.) for name in result.params.index])
    test = result.t_test(vector)
    ci = np.asarray(test.conf_int()).ravel()
    return {'estimate': float(np.asarray(test.effect).item()),
            'se': float(np.asarray(test.sd).item()), 'ci_low': float(ci[0]), 'ci_high': float(ci[1]),
            'p_value': float(np.asarray(test.pvalue).item()), 'inference_note': CAUTION}


def analyze(panel, airport):
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    data = panel.loc[panel['sample'] == 'primary'].copy().reset_index(drop=True)
    reference = float(np.log(data.passengers).mean())
    panel = panel.copy()
    panel['demand_c'] = np.log(panel.passengers) - reference
    panel['log_fare'] = np.log(panel.fare_mean)
    data = panel.loc[panel['sample'] == 'primary'].copy().reset_index(drop=True)
    if data[['fare_mean', 'demand_c', 'risk']].isna().any().any():
        raise ValueError('Primary panel has missing model data; inspect matching/coverage')
    risk_low, risk_high = data.risk.quantile([.25, .75])
    specifications = [
        ('baseline_pooled', 'fare_mean ~ demand_c', data, None),
        ('baseline_fe', 'fare_mean ~ demand_c + ' + FE, data, None),
        ('benign_baseline_fe', 'fare_mean ~ demand_c + ' + FE,
         data.loc[data.risk <= data.risk.median()].copy(), None),
        ('risk_additive_fe', 'fare_mean ~ demand_c + risk + ' + FE, data, None),
        ('core_interaction_fe', CORE, data, None),
        ('passenger_weighted', CORE, data, 'passengers'),
        ('log_fare', 'log_fare ~ demand_c * risk + ' + FE, data, None),
        ('broad_fare_bounds', CORE, panel.loc[panel['sample'] == 'broad_fare_bounds'].copy(), None),
        ('max_endpoint_risk', CORE, data.assign(risk=data.risk_max), None),
    ]
    balanced = data.groupby('route_carrier').period.nunique()
    balanced = balanced.index[balanced == data.period.nunique()]
    specifications.append(('balanced_support', CORE, data.loc[data.route_carrier.isin(balanced)].copy(), None))
    for hub in HUBS:
        specifications.append((f'exclude_{hub}', CORE, data.loc[data.Origin != hub].copy(), None))
    results, diagnostics, coefficients = {}, [], []
    for name, formula, frame, weight in specifications:
        frame = frame.reset_index(drop=True)
        try:
            result = fit_checked(formula, frame,
                                 weights=frame[weight] if weight else None, cluster='route')
            results[name] = result
            design = result.model.exog
            diagnostics.append({'model': name, 'status': 'estimated', 'nobs': int(result.nobs),
                                'parameters': design.shape[1], 'rank': int(np.linalg.matrix_rank(design)),
                                'condition_number': float(np.linalg.cond(design)),
                                'route_clusters': frame.route.nunique(),
                                'route_carriers': frame.route_carrier.nunique(),
                                'r_squared': float(result.rsquared), 'formula': formula,
                                'covariance': 'route-clustered; finite-sample correction; t inference',
                                'inference_df': float(result.df_resid_inference)})
            ci = result.conf_int()
            for term in ['demand_c', 'risk', 'demand_c:risk']:
                if term in result.params:
                    coefficients.append({'model': name, 'term': term, 'estimate': result.params[term],
                                         'se': result.bse[term], 'ci_low': ci.loc[term, 0],
                                         'ci_high': ci.loc[term, 1], 'p_value': result.pvalues[term],
                                         'inference_note': CAUTION})
        except (ValueError, np.linalg.LinAlgError) as exc:
            diagnostics.append({'model': name, 'status': 'not_estimable', 'reason': str(exc),
                                'nobs': len(frame), 'formula': formula})
    pd.DataFrame(diagnostics).to_csv(TABLES/'model_diagnostics.csv', index=False)
    pd.DataFrame(coefficients).to_csv(TABLES/'coefficients.csv', index=False)
    if 'core_interaction_fe' not in results:
        raise ValueError('Core model not estimable; diagnostics saved')
    core = results['core_interaction_fe']
    fe_indices = [i for i, name in enumerate(core.model.exog_names) if name not in ['demand_c', 'risk', 'demand_c:risk']]
    fe_design = core.model.exog[:, fe_indices]
    support = []
    for term, values in [('demand_c', data.demand_c), ('risk', data.risk),
                         ('interaction', data.demand_c*data.risk)]:
        residual = values.to_numpy() - fe_design @ np.linalg.lstsq(fe_design, values, rcond=None)[0]
        support.append({'variable': term, 'raw_std': float(values.std()),
                        'within_fe_std': float(np.std(residual)), 'within_fe_min': float(residual.min()),
                        'within_fe_max': float(residual.max())})
    pd.DataFrame(support).to_csv(TABLES/'within_fe_support.csv', index=False)
    group_support = data.groupby('route_carrier').agg(risk_min=('risk','min'), risk_max=('risk','max'),
                                                     demand_min=('demand_c','min'), demand_max=('demand_c','max'),
                                                     periods=('period','nunique'))
    group_support['covers_both_risk_references'] = (group_support.risk_min <= risk_low) & (group_support.risk_max >= risk_high)
    group_support.to_csv(TABLES/'route_carrier_support.csv')
    pd.crosstab(pd.qcut(data.demand_c, 4, duplicates='drop'), pd.qcut(data.risk, 4, duplicates='drop')).to_csv(TABLES/'joint_support_counts.csv')
    marginals = []
    for label, risk in [('low_q25', risk_low), ('high_q75', risk_high)]:
        marginals.append({'effect': 'fare_per_log_traffic', 'reference': label, 'risk': risk,
                          **contrast(core, {'demand_c': 1, 'demand_c:risk': risk})})
    for label, demand in [('low_traffic_q10', data.demand_c.quantile(.1)), ('mean_log_traffic', 0),
                           ('high_traffic_q90', data.demand_c.quantile(.9))]:
        marginals.append({'effect': 'fare_per_10pp_risk', 'reference': label, 'demand_c': demand,
                          **contrast(core, {'risk': .1, 'demand_c:risk': .1*demand})})
    pd.DataFrame(marginals).to_csv(TABLES/'marginal_effects.csv', index=False)
    var_d = float(data.demand_c.var(ddof=0))
    dispersion = []
    for label, risk in [('low_q25', risk_low), ('high_q75', risk_high)]:
        slope = core.params['demand_c'] + risk * core.params['demand_c:risk']
        interval = contrast(core, {'demand_c': 1, 'demand_c:risk': risk})
        a, b = interval['ci_low'], interval['ci_high']
        lower = 0. if a <= 0 <= b else min(a*a, b*b)*var_d
        upper = max(a*a, b*b)*var_d
        dispersion.append({'risk_reference': label, 'risk': risk, 'demand_slope': slope,
                           'fixed_reference_log_traffic_variance': var_d,
                           'fitted_demand_component_variance_usd2': slope**2 * var_d,
                           'ci_low': lower, 'ci_high': upper,
                           'inference_note': CAUTION + '; squared-slope confidence-set image, fixed empirical Var(D)'})
    pd.DataFrame(dispersion).to_csv(TABLES/'conditional_dispersion.csv', index=False)
    empirical = data.assign(risk_group=np.where(data.risk <= data.risk.median(), 'low', 'high')).groupby('risk_group').agg(
        cell_mean_variance=('fare_mean', 'var'), average_within_cell_fare_variance=('fare_variance', 'mean'), cells=('fare_mean', 'size'))
    empirical.to_csv(TABLES/'empirical_dispersion.csv')
    # Independent airport-quarter validation, never expanded across fare carriers.
    validation = airport.copy()
    validation['period'] = validation.Year.astype(str) + 'Q' + validation.Quarter.astype(str)
    validation_rows = []
    for outcome in ['cancellation_rate', 'delay_rate', 'weather_delay_rate', 'realized_adverse_share']:
        for control in ['pooled', 'airport_calendar_fe']:
            formula = outcome + ' ~ risk' + (' + C(airport) + C(period)' if control != 'pooled' else '')
            try:
                model = fit_checked(formula, validation, cluster='airport')
                validation_rows.append({'outcome': outcome, 'specification': control, 'status': 'estimated',
                                        **contrast(model, {'risk': .1}), 'nobs': int(model.nobs),
                                        'clusters': validation.airport.nunique()})
            except (ValueError, np.linalg.LinAlgError) as exc:
                validation_rows.append({'outcome': outcome, 'specification': control,
                                        'status': 'not_estimable', 'reason': str(exc)})
    pd.DataFrame(validation_rows).to_csv(TABLES/'risk_validation_models.csv', index=False)
    metadata = {'demand_log_reference': reference, 'reference_sampled_passengers': float(np.exp(reference)),
                'risk_q25': float(risk_low), 'risk_q75': float(risk_high),
                'primary_cells': len(data), 'routes': data.route.nunique(),
                'route_carriers': data.route_carrier.nunique(), 'periods': data.period.nunique(),
                'sampled_passengers': float(data.passengers.sum()),
                'route_carriers_covering_both_risk_references': int(group_support.covers_both_risk_references.sum()),
                'original_H1_H2': 'not estimable from quarterly DB1B',
                'inference_caution': 'Few clusters (12 routes; 7 airports); approximate intervals, not confirmatory tests.'}
    (TABLES/'analysis_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    make_figures(data, core, airport, risk_low, risk_high, dispersion)
    return metadata


def make_figures(data, core, airport, risk_low, risk_high, dispersion):
    plt.rcParams.update({'font.size': 11, 'figure.dpi': 130, 'axes.spines.top': False, 'axes.spines.right': False})
    colors = ['#2563a6', '#cf6235']
    fig, ax = plt.subplots(figsize=(8, 5))
    for label, mask, color in [('Lower risk', data.risk <= data.risk.median(), colors[0]),
                                ('Higher risk', data.risk > data.risk.median(), colors[1])]:
        ax.scatter(data.loc[mask, 'demand_c'], data.loc[mask, 'fare_mean'], s=22, alpha=.6, label=label, color=color)
    ax.set(xlabel='Centered log sampled passengers', ylabel='Passenger-weighted fare (USD)',
           title='Raw quarterly fare–traffic relationship')
    ax.legend(frameon=False); fig.tight_layout(); fig.savefig(FIGURES/'raw_fare_traffic.png'); plt.close(fig)
    # Average model predictions over a fixed sample's FE composition.
    components = core.params['demand_c']*data.demand_c + core.params['risk']*data.risk + core.params['demand_c:risk']*data.demand_c*data.risk
    reference_fe = float((core.fittedvalues - components).mean())
    adjusted_y = data.fare_mean - core.fittedvalues + components + reference_fe
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(data.demand_c, adjusted_y, s=15, color='#687482', alpha=.3, label='FE-adjusted observations')
    low_group = data.loc[data.risk <= data.risk.median(), 'demand_c']
    high_group = data.loc[data.risk > data.risk.median(), 'demand_c']
    common_low = max(low_group.quantile(.05), high_group.quantile(.05))
    common_high = min(low_group.quantile(.95), high_group.quantile(.95))
    if common_low >= common_high:
        raise ValueError('no common central traffic support for fitted risk curves')
    grid = np.linspace(common_low, common_high, 100)
    for risk, label, color in [(risk_low, 'Risk 25th percentile', colors[0]), (risk_high, 'Risk 75th percentile', colors[1])]:
        predictions = reference_fe + core.params['demand_c']*grid + core.params['risk']*risk + core.params['demand_c:risk']*grid*risk
        ax.plot(grid, predictions, color=color, linewidth=2.5, label=f'{label} ({risk:.3f})')
    ax.set(xlabel='Centered log sampled passengers', ylabel='Fare at average FE composition (USD)',
           title='Exploratory fitted curves; pooled common traffic support')
    ax.legend(frameon=False, fontsize=9); fig.tight_layout(); fig.savefig(FIGURES/'adjusted_interaction.png'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5))
    for name, group in airport.groupby('airport'):
        ax.scatter(group.risk, 100*group.cancellation_rate, label=name, s=38, alpha=.8)
    ax.set(xlabel='Lagged seasonal adverse-weather share', ylabel='Cancelled / reported arrival flights (%)',
           title='External validation: airport-quarter observations')
    ax.legend(frameon=False, ncol=4, fontsize=9); fig.tight_layout(); fig.savefig(FIGURES/'risk_validation.png'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    estimates = np.array([x['fitted_demand_component_variance_usd2'] for x in dispersion])
    errors = np.array([estimates - [x['ci_low'] for x in dispersion], [x['ci_high'] for x in dispersion] - estimates])
    ax.bar(['Risk Q25', 'Risk Q75'], estimates, color=colors, yerr=errors, capsize=5)
    ax.set(ylabel='Fitted demand-component variance (USD²)', title='Point estimates with approximate intervals; fixed traffic variance')
    fig.tight_layout(); fig.savefig(FIGURES/'conditional_dispersion.png'); plt.close(fig)
