import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf

from src.stage5.pipeline import one_way, capacity_cells, residualize


def test_single_coupon_product_and_proration_audit():
    rows = pd.DataFrame({'RoundTrip': [0, 0, 1, 0], 'Coupons': [1, 2, 2, 1],
                         'MktFare': [100., 70., 90., 110.], 'ItinFare': [100., 140., 180., 110.]})
    selected, audit = one_way(rows)
    assert selected.index.tolist() == [0, 3]
    assert audit['max_absolute_proration_gap'] == 0
    rows.loc[3, 'ItinFare'] = 111
    assert one_way(rows)[1]['max_absolute_proration_gap'] == 1


def test_capacity_sums_operators_and_excludes_nonpassenger_service():
    rows = pd.DataFrame({'YEAR': [2024]*4, 'QUARTER': [1]*4,
        'ORIGIN': ['ORD']*4, 'DEST': ['LAX']*4, 'CLASS': ['F', 'F', 'G', 'F'],
        'PASSENGERS': [50, 40, 500, 0], 'SEATS': [80, 60, 999, 0],
        'DEPARTURES_PERFORMED': [1, 1, 10, 0]})
    cell = capacity_cells(rows).iloc[0]
    assert cell.seats == 140 and cell.t100_passengers == 90 and cell.departures == 2
    rows.loc[0, 'SEATS'] = -1
    with pytest.raises(ValueError, match='capacity'):
        capacity_cells(rows)


def test_absorption_matches_dummy_residuals_on_unbalanced_panel():
    df = pd.DataFrame({'a': ['A','A','A','B','B','C','C'],
        'b': ['1','2','3','1','3','2','3'], 'y': [2.,4.,9.,5.,8.,1.,7.]})
    expected = smf.ols('y ~ C(a) + C(b)', df).fit().resid
    actual = residualize(df[['y']].to_numpy(), [df.a, df.b])[:, 0]
    np.testing.assert_allclose(actual, expected, atol=1e-9)
    fixed = df.a.map({'A': .2, 'B': .4, 'C': .8}).to_numpy()[:, None]
    assert np.max(np.abs(residualize(fixed, [df.a, df.b]))) < 1e-10
