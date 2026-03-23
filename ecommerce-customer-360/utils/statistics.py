"""
Statistical utilities for E-Commerce Customer 360.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Any


class DescriptiveStatistics:
    @staticmethod
    def summary(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        results = []
        for col in columns:
            if col not in df.columns:
                continue
            data = df[col].dropna()
            if len(data) < 2:
                continue
            results.append({
                'Column': col.replace('_', ' ').title(),
                'Count': len(data),
                'Mean': data.mean(),
                'Std': data.std(),
                'Min': data.min(),
                '25%': data.quantile(0.25),
                'Median': data.median(),
                '75%': data.quantile(0.75),
                'Max': data.max()
            })
        return pd.DataFrame(results)


class CorrelationAnalysis:
    @staticmethod
    def pearson_correlation(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        from scipy.stats import pearsonr
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask], y[mask]
        if len(x_clean) < 3:
            return {'correlation': np.nan, 'p_value': np.nan}
        corr, p_value = pearsonr(x_clean, y_clean)
        return {'correlation': corr, 'p_value': p_value, 'significant': p_value < 0.05}


class HypothesisTesting:
    @staticmethod
    def anova_test(df: pd.DataFrame, value_col: str, group_col: str) -> Dict[str, Any]:
        groups = [g[value_col].dropna() for _, g in df.groupby(group_col)]
        groups = [g for g in groups if len(g) >= 2]

        if len(groups) < 2:
            return {'statistic': np.nan, 'p_value': np.nan, 'significant': False}

        stat, p_value = stats.f_oneway(*groups)
        all_data = pd.concat(groups)
        grand_mean = all_data.mean()
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
        ss_total = sum((all_data - grand_mean)**2)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        return {
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'eta_squared': eta_squared
        }


class RegressionAnalysis:
    @staticmethod
    def simple_linear_regression(x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask].values, y[mask].values

        if len(x_clean) < 3:
            return {'slope': np.nan, 'intercept': np.nan, 'r_squared': np.nan}

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)

        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'equation': f'y = {slope:.4f}x + {intercept:.2f}'
        }
