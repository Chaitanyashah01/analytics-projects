"""
Statistical analysis utilities for Automotive Performance Analytics.
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from typing import Dict, List, Any


class DescriptiveStatistics:
    """Descriptive statistics utilities."""

    @staticmethod
    def summary(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Generate summary statistics."""
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
                'Max': data.max(),
                'Skew': data.skew()
            })
        return pd.DataFrame(results)


class CorrelationAnalysis:
    """Correlation analysis utilities."""

    @staticmethod
    def pearson_correlation(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        """Calculate Pearson correlation."""
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask], y[mask]
        if len(x_clean) < 3:
            return {'correlation': np.nan, 'p_value': np.nan, 'significant': False}
        corr, p_value = pearsonr(x_clean, y_clean)
        return {
            'correlation': corr,
            'p_value': p_value,
            'significant': p_value < 0.05
        }


class HypothesisTesting:
    """Hypothesis testing utilities."""

    @staticmethod
    def t_test_independent(group1: pd.Series, group2: pd.Series) -> Dict[str, Any]:
        """Perform independent t-test."""
        g1, g2 = group1.dropna(), group2.dropna()
        if len(g1) < 2 or len(g2) < 2:
            return {'statistic': np.nan, 'p_value': np.nan, 'significant': False}

        stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)

        # Cohen's d
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
        """Perform one-way ANOVA."""
        groups = [g[value_col].dropna() for _, g in df.groupby(group_col)]
        groups = [g for g in groups if len(g) >= 2]

        if len(groups) < 2:
            return {'statistic': np.nan, 'p_value': np.nan, 'significant': False}

        stat, p_value = stats.f_oneway(*groups)

        # Eta-squared
        all_data = pd.concat(groups)
        grand_mean = all_data.mean()
        ss_between = sum(len(g) * (g.mean() - grand_mean)**2 for g in groups)
        ss_total = sum((all_data - grand_mean)**2)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        return {
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'num_groups': len(groups),
            'eta_squared': eta_squared
        }


class RegressionAnalysis:
    """Regression analysis utilities."""

    @staticmethod
    def simple_linear_regression(x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """Simple linear regression."""
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask].values, y[mask].values

        if len(x_clean) < 3:
            return {'slope': np.nan, 'intercept': np.nan, 'r_squared': np.nan}

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)

        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'r_value': r_value,
            'p_value': p_value,
            'equation': f'y = {slope:.4f}x + {intercept:.2f}'
        }
