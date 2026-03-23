"""
Statistical analysis utilities for Aviation Fuel Analytics.
Provides descriptive statistics, hypothesis testing, and regression analysis.
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, normaltest, shapiro
from typing import Dict, List, Tuple, Any, Optional
import warnings

warnings.filterwarnings('ignore')


class DescriptiveStatistics:
    """Calculate comprehensive descriptive statistics."""

    @staticmethod
    def summary(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Generate summary statistics for numeric columns."""
        results = []

        for col in columns:
            if col not in df.columns:
                continue

            data = df[col].dropna()

            if len(data) < 2:
                continue

            stats_dict = {
                'Column': col.replace('_', ' ').title(),
                'Count': len(data),
                'Mean': data.mean(),
                'Std Dev': data.std(),
                'Min': data.min(),
                '25%': data.quantile(0.25),
                'Median': data.median(),
                '75%': data.quantile(0.75),
                'Max': data.max(),
                'Skewness': data.skew(),
                'Kurtosis': data.kurtosis(),
                'CV (%)': (data.std() / data.mean() * 100) if data.mean() != 0 else np.nan
            }
            results.append(stats_dict)

        return pd.DataFrame(results)

    @staticmethod
    def confidence_interval(
        data: pd.Series,
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        """Calculate confidence interval for mean."""
        n = len(data)
        mean = data.mean()
        se = stats.sem(data)
        h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
        return mean - h, mean, mean + h

    @staticmethod
    def detect_outliers_zscore(
        data: pd.Series,
        threshold: float = 3.0
    ) -> Dict[str, Any]:
        """Detect outliers using Z-score method."""
        z_scores = np.abs(stats.zscore(data.dropna()))
        outliers = z_scores > threshold

        return {
            'outlier_count': outliers.sum(),
            'outlier_pct': outliers.mean() * 100,
            'outlier_indices': np.where(outliers)[0].tolist()
        }

    @staticmethod
    def detect_outliers_iqr(
        data: pd.Series,
        multiplier: float = 1.5
    ) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR

        outliers = (data < lower_bound) | (data > upper_bound)

        return {
            'outlier_count': outliers.sum(),
            'outlier_pct': outliers.mean() * 100,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'Q1': Q1,
            'Q3': Q3,
            'IQR': IQR
        }


class CorrelationAnalysis:
    """Correlation and association analysis."""

    @staticmethod
    def pearson_correlation(
        x: pd.Series,
        y: pd.Series
    ) -> Dict[str, float]:
        """Calculate Pearson correlation with p-value."""
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask], y[mask]

        if len(x_clean) < 3:
            return {'correlation': np.nan, 'p_value': np.nan, 'significant': False}

        corr, p_value = pearsonr(x_clean, y_clean)

        return {
            'correlation': corr,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'strength': _interpret_correlation(corr)
        }

    @staticmethod
    def spearman_correlation(
        x: pd.Series,
        y: pd.Series
    ) -> Dict[str, float]:
        """Calculate Spearman rank correlation."""
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask], y[mask]

        if len(x_clean) < 3:
            return {'correlation': np.nan, 'p_value': np.nan, 'significant': False}

        corr, p_value = spearmanr(x_clean, y_clean)

        return {
            'correlation': corr,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'strength': _interpret_correlation(corr)
        }

    @staticmethod
    def correlation_matrix(
        df: pd.DataFrame,
        columns: List[str],
        method: str = 'pearson'
    ) -> pd.DataFrame:
        """Calculate correlation matrix."""
        return df[columns].corr(method=method)


class HypothesisTesting:
    """Statistical hypothesis testing."""

    @staticmethod
    def t_test_independent(
        group1: pd.Series,
        group2: pd.Series,
        equal_var: bool = False
    ) -> Dict[str, Any]:
        """Perform independent samples t-test."""
        group1_clean = group1.dropna()
        group2_clean = group2.dropna()

        if len(group1_clean) < 2 or len(group2_clean) < 2:
            return {'statistic': np.nan, 'p_value': np.nan, 'significant': False}

        stat, p_value = stats.ttest_ind(group1_clean, group2_clean, equal_var=equal_var)

        return {
            'statistic': stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'group1_mean': group1_clean.mean(),
            'group2_mean': group2_clean.mean(),
            'mean_difference': group1_clean.mean() - group2_clean.mean(),
            'effect_size': _cohens_d(group1_clean, group2_clean)
        }

    @staticmethod
    def anova_test(
        df: pd.DataFrame,
        value_col: str,
        group_col: str
    ) -> Dict[str, Any]:
        """Perform one-way ANOVA test."""
        groups = [group[value_col].dropna() for name, group in df.groupby(group_col)]
        groups = [g for g in groups if len(g) >= 2]

        if len(groups) < 2:
            return {'statistic': np.nan, 'p_value': np.nan, 'significant': False}

        stat, p_value = stats.f_oneway(*groups)

        # Calculate effect size (eta-squared)
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
            'eta_squared': eta_squared,
            'effect_size': _interpret_eta_squared(eta_squared)
        }

    @staticmethod
    def normality_test(
        data: pd.Series,
        method: str = 'shapiro'
    ) -> Dict[str, Any]:
        """Test for normality of distribution."""
        data_clean = data.dropna()

        if len(data_clean) < 8:
            return {'statistic': np.nan, 'p_value': np.nan, 'is_normal': None}

        if method == 'shapiro' and len(data_clean) <= 5000:
            stat, p_value = shapiro(data_clean)
        else:
            stat, p_value = normaltest(data_clean)

        return {
            'statistic': stat,
            'p_value': p_value,
            'is_normal': p_value > 0.05,
            'interpretation': 'Normal distribution' if p_value > 0.05 else 'Non-normal distribution'
        }


class RegressionAnalysis:
    """Regression modeling and analysis."""

    @staticmethod
    def simple_linear_regression(
        x: pd.Series,
        y: pd.Series
    ) -> Dict[str, Any]:
        """Perform simple linear regression."""
        mask = ~(x.isna() | y.isna())
        x_clean, y_clean = x[mask].values, y[mask].values

        if len(x_clean) < 3:
            return {'slope': np.nan, 'intercept': np.nan, 'r_squared': np.nan}

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)

        # Predictions
        y_pred = slope * x_clean + intercept
        residuals = y_clean - y_pred

        # RMSE
        rmse = np.sqrt(np.mean(residuals**2))

        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2,
            'r_value': r_value,
            'p_value': p_value,
            'std_error': std_err,
            'rmse': rmse,
            'significant': p_value < 0.05,
            'equation': f'y = {slope:.4f}x + {intercept:.4f}'
        }

    @staticmethod
    def multiple_regression_summary(
        df: pd.DataFrame,
        target_col: str,
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """Perform multiple linear regression."""
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score, mean_squared_error

        # Prepare data
        df_clean = df[[target_col] + feature_cols].dropna()

        if len(df_clean) < len(feature_cols) + 2:
            return {'error': 'Insufficient data'}

        X = df_clean[feature_cols].values
        y = df_clean[target_col].values

        # Fit model
        model = LinearRegression()
        model.fit(X, y)

        # Predictions
        y_pred = model.predict(X)

        # Metrics
        r2 = r2_score(y, y_pred)
        adj_r2 = 1 - (1 - r2) * (len(y) - 1) / (len(y) - len(feature_cols) - 1)
        rmse = np.sqrt(mean_squared_error(y, y_pred))

        # Coefficients
        coefficients = dict(zip(feature_cols, model.coef_))

        return {
            'r_squared': r2,
            'adjusted_r_squared': adj_r2,
            'rmse': rmse,
            'intercept': model.intercept_,
            'coefficients': coefficients,
            'n_observations': len(y),
            'n_features': len(feature_cols)
        }


class TimeSeriesAnalysis:
    """Time series specific analysis."""

    @staticmethod
    def calculate_growth_rate(
        data: pd.Series,
        periods: int = 1
    ) -> pd.Series:
        """Calculate period-over-period growth rate."""
        return data.pct_change(periods=periods) * 100

    @staticmethod
    def moving_statistics(
        data: pd.Series,
        window: int = 3
    ) -> pd.DataFrame:
        """Calculate moving statistics."""
        return pd.DataFrame({
            'moving_avg': data.rolling(window=window).mean(),
            'moving_std': data.rolling(window=window).std(),
            'moving_min': data.rolling(window=window).min(),
            'moving_max': data.rolling(window=window).max()
        })

    @staticmethod
    def trend_analysis(
        data: pd.Series
    ) -> Dict[str, Any]:
        """Analyze trend in time series."""
        x = np.arange(len(data))
        y = data.values

        mask = ~np.isnan(y)
        x_clean, y_clean = x[mask], y[mask]

        if len(x_clean) < 3:
            return {'trend': 'insufficient_data'}

        slope, intercept, r_value, p_value, std_err = stats.linregress(x_clean, y_clean)

        # Determine trend direction and strength
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
            'significant': p_value < 0.05,
            'avg_change_per_period': slope
        }


# Helper functions
def _interpret_correlation(r: float) -> str:
    """Interpret correlation coefficient strength."""
    abs_r = abs(r)
    if abs_r >= 0.9:
        return 'Very Strong'
    elif abs_r >= 0.7:
        return 'Strong'
    elif abs_r >= 0.5:
        return 'Moderate'
    elif abs_r >= 0.3:
        return 'Weak'
    else:
        return 'Very Weak'


def _cohens_d(group1: pd.Series, group2: pd.Series) -> float:
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()

    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0

    return (group1.mean() - group2.mean()) / pooled_std


def _interpret_eta_squared(eta_sq: float) -> str:
    """Interpret eta-squared effect size."""
    if eta_sq >= 0.14:
        return 'Large'
    elif eta_sq >= 0.06:
        return 'Medium'
    elif eta_sq >= 0.01:
        return 'Small'
    else:
        return 'Negligible'
