"""
Statistical utilities for Renewable Energy Insights.
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


class HypothesisTesting:
    @staticmethod
    def t_test_independent(group1: pd.Series, group2: pd.Series) -> Dict[str, Any]:
        g1, g2 = group1.dropna(), group2.dropna()
        if len(g1) < 2 or len(g2) < 2:
            return {'statistic': np.nan, 'p_value': np.nan, 'significant': False}

        stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)
        pooled_std = np.sqrt(((len(g1)-1)*g1.var() + (len(g2)-1)*g2.var()) / (len(g1)+len(g2)-2))
        cohens_d = (g1.mean() - g2.mean()) / pooled_std if pooled_std > 0 else 0

        return {
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'group1_mean': g1.mean(),
            'group2_mean': g2.mean(),
            'mean_difference': g1.mean() - g2.mean(),
            'effect_size': cohens_d
        }

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


class TimeSeriesAnalysis:
    @staticmethod
    def trend_analysis(data: pd.Series) -> Dict[str, Any]:
        x = np.arange(len(data))
        y = data.values
        mask = ~np.isnan(y)
        x_clean, y_clean = x[mask], y[mask]

        if len(x_clean) < 3:
            return {'trend': 'insufficient_data'}

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)

        if p_value > 0.05:
            trend = 'no_significant_trend'
        elif slope > 0:
            trend = 'upward'
        else:
            trend = 'downward'

        return {
            'trend_direction': trend,
            'slope': slope,
            'r_squared': r_value**2,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
