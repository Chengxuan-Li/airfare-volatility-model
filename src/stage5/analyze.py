"""Predeclared temporal, product, capacity, and seasonal stress tests."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.analysis.models import fit_checked
from src.stage5.pipeline import OUT, residualize, save_json


def main():
    panel = pd.read_csv(OUT/'panel.csv', float_precision='round_trip')
    reference = float(np.log(panel.loc[(panel.Year < 2025) & panel['sample'].eq('primary'), 'passengers']).mean())
    t_reference = float(np.log(panel.loc[(panel.Year < 2025) & panel['sample'].eq('primary') & panel.t100_passengers.gt(0), 't100_passengers']).mean())
    panel['demand_c'] = np.log(panel.passengers)-reference
    panel['t100_c'] = np.log(panel.t100_passengers.where(panel.t100_passengers.gt(0)))-t_reference
    panel['log_seats'] = np.log(panel.seats.where(panel.seats.gt(0)))
    coefficients, statuses, support = [], [], []

    def fit(name, data, fe, demand='demand_c', capacity=False):
        formula = f'fare_mean ~ {demand} * risk' + (' + log_seats' if capacity else '') + f' + C({fe}) + C(period)'
        status = {'model': name, 'n': len(data), 'pairs': data.pair.nunique(),
                  'airports': len(set(data.Origin) | set(data.Dest)), 'formula': formula}
        if data.empty:
            statuses.append({**status, 'status': 'not_estimable', 'reason': 'empty sample'})
            return
        residuals = residualize(data[['risk', 'fixed_risk']].to_numpy(), [data[fe], data.period])
        support.append({'model': name, 'risk_raw_sd': float(data.risk.std()),
            'risk_residual_sd': float(residuals[:, 0].std(ddof=1)),
            'fixed_risk_residual_max_abs': float(np.abs(residuals[:, 1]).max()),
            'groups': data[fe].nunique(), 'repeated_groups': int(data.groupby(fe).size().gt(1).sum())})
        try:
            result = fit_checked(formula, data, cluster='pair')
            status.update(status='estimated', rank=int(result.model.exog.shape[1]),
                          condition=float(np.linalg.cond(result.model.exog)))
            terms = {demand: 'traffic', 'risk': 'risk', demand+':risk': 'interaction'}
            if capacity:
                terms['log_seats'] = 'log_seats'
            for term, label in terms.items():
                interval = result.conf_int().loc[term]
                coefficients.append({'model': name, 'term': label, 'estimate': float(result.params[term]),
                    'se': float(result.bse[term]), 'ci_low': float(interval.iloc[0]), 'ci_high': float(interval.iloc[1]),
                    'p_value': float(result.pvalues[term]), 'n': len(data), 'pairs': data.pair.nunique(),
                    'inference': 'Approximate CR1 t; undirected pairs; shared-airport dependence remains'})
        except (ValueError, np.linalg.LinAlgError) as exc:
            status.update(status='not_estimable', reason=str(exc))
        statuses.append(status)

    for sample in ['primary', 'one_way']:
        for period in ['training', 'holdout', 'full']:
            data = panel.loc[panel['sample'].eq(sample)].copy()
            if period == 'training':
                data = data.loc[data.Year < 2025]
            elif period == 'holdout':
                data = data.loc[data.Year == 2025]
            matched = data.loc[data.seats.gt(0) & data.t100_passengers.gt(0)].copy()
            for fe_name, fe in [('standard', 'route_carrier'), ('seasonal', 'route_carrier_season')]:
                prefix = f'{sample}_{period}_{fe_name}'
                fit(prefix+'_base', data, fe)
                fit(prefix+'_matched', matched, fe)
                fit(prefix+'_capacity', matched, fe, capacity=True)
                fit(prefix+'_t100', matched, fe, demand='t100_c', capacity=True)
    training = panel.loc[panel['sample'].eq('primary') & panel.Year.lt(2025)]
    for airport in sorted(set(training.Origin) | set(training.Dest)):
        selected = training.loc[training.Origin.ne(airport) & training.Dest.ne(airport)]
        for label, fe in [('standard', 'route_carrier'), ('seasonal', 'route_carrier_season')]:
            fit('leave_'+airport+'_'+label, selected, fe)
    pd.DataFrame(coefficients).to_csv(OUT/'coefficients.csv', index=False)
    pd.DataFrame(statuses).to_csv(OUT/'model_status.csv', index=False)
    pd.DataFrame(support).to_csv(OUT/'identifying_support.csv', index=False)
    save_json('analysis_metadata.json', {'training_log_traffic_reference': reference,
        'training_log_t100_reference': t_reference, 'models_attempted': len(statuses),
        'models_estimated': sum(s['status'] == 'estimated' for s in statuses),
        'holdout': '2025Q1-Q2, no tuning; coefficients refit, not out-of-time prediction',
        'inference_limit': 'At most 21 pairs and seven connected airports; intervals are descriptive approximations'})
    summary = panel.groupby(['sample', 'Year', 'Quarter']).agg(cells=('fare_mean', 'size'),
        sampled_passengers=('passengers', 'sum'), records=('records', 'sum'),
        fare_min=('fare_mean', 'min'), fare_max=('fare_mean', 'max')).reset_index()
    summary.to_csv(OUT/'sample_summary.csv', index=False)
    diffs = training.pivot(index=['route_carrier', 'Quarter'], columns='Year',
        values=['fare_mean', 'risk', 'demand_c']).dropna()
    change = pd.DataFrame({name+'_change': diffs[name][2024]-diffs[name][2023]
                          for name in ['fare_mean', 'risk', 'demand_c']}).reset_index()
    change.to_csv(OUT/'same_season_changes.csv', index=False)
    results = pd.DataFrame(coefficients)
    selected = results.loc[results.term.eq('interaction') & results.model.str.match(
        r'(primary|one_way)_(training|holdout|full)_(standard|seasonal)_base$')].copy()
    fig, ax = plt.subplots(figsize=(10, 6))
    positions = np.arange(len(selected))
    ax.errorbar(selected.estimate, positions,
        xerr=np.vstack([selected.estimate-selected.ci_low, selected.ci_high-selected.estimate]), fmt='o', capsize=3)
    ax.set_yticks(positions, selected.model.str.replace('_', ' '))
    ax.axvline(0, color='grey', linewidth=1)
    ax.set_xlabel('Traffic × historical risk coefficient (USD per log traffic × risk fraction)')
    ax.set_title('Descriptive sensitivity; approximate pair-cluster 95% intervals')
    fig.tight_layout()
    fig.savefig(OUT/'interaction_sensitivity.png', dpi=160)
    plt.close(fig)
    print(f'Stage5: {len(statuses)} attempted, {sum(s["status"] == "estimated" for s in statuses)} estimated', flush=True)


if __name__ == '__main__':
    main()
