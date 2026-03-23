"""
Statistical Analysis Page
Deep dive into statistical analysis and data quality.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_financial_timeseries, get_filter_options, get_phase_comparison
from utils.statistics import (
    DescriptiveStatistics, CorrelationAnalysis, HypothesisTesting,
    RegressionAnalysis, TimeSeriesAnalysis
)
from utils.data_loader import DataQualityReport
from utils.visualizations import create_correlation_heatmap

st.set_page_config(page_title="Statistical Analysis", page_icon="📊", layout="wide")

st.title("📊 Statistical Analysis & Data Quality")
st.markdown("Comprehensive statistical analysis, hypothesis testing, and data quality assessment")

try:
    # Load data
    options = get_filter_options()
    df = get_financial_timeseries()
    df_phases = get_phase_comparison()

    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Descriptive Statistics",
        "🔗 Correlation Analysis",
        "🧪 Hypothesis Testing",
        "🔍 Data Quality"
    ])

    with tab1:
        st.markdown("## Descriptive Statistics")

        # Select columns for analysis
        numeric_cols = ['revenue_usd_m', 'fuel_cost_usd_m', 'fuel_cost_pct_revenue',
                       'net_profit_usd_m', 'profit_margin_pct', 'passengers_carried_m',
                       'brent_crude_usd_barrel', 'jet_fuel_usd_barrel', 'fuel_hedging_pct']

        selected_cols = st.multiselect(
            "Select variables for analysis",
            numeric_cols,
            default=numeric_cols[:5]
        )

        if selected_cols:
            desc_stats = DescriptiveStatistics.summary(df, selected_cols)

            st.markdown("### Summary Statistics")
            st.dataframe(desc_stats, use_container_width=True)

            # Distribution plots
            st.markdown("### Distribution Analysis")

            col1, col2 = st.columns(2)

            for i, col in enumerate(selected_cols[:4]):
                with col1 if i % 2 == 0 else col2:
                    fig = px.histogram(
                        df, x=col, nbins=30,
                        title=f"Distribution of {col.replace('_', ' ').title()}",
                        marginal='box'
                    )
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)

            # Outlier detection
            st.markdown("### Outlier Detection")

            outlier_col = st.selectbox("Select variable for outlier analysis", selected_cols)

            col1, col2 = st.columns(2)

            with col1:
                # IQR method
                iqr_results = DescriptiveStatistics.detect_outliers_iqr(df[outlier_col])
                st.markdown(f"""
                **IQR Method Results:**
                - Outliers detected: `{iqr_results['outlier_count']}`
                - Outlier percentage: `{iqr_results['outlier_pct']:.2f}%`
                - Q1: `{iqr_results['Q1']:.2f}`
                - Q3: `{iqr_results['Q3']:.2f}`
                - IQR: `{iqr_results['IQR']:.2f}`
                - Lower bound: `{iqr_results['lower_bound']:.2f}`
                - Upper bound: `{iqr_results['upper_bound']:.2f}`
                """)

            with col2:
                # Z-score method
                zscore_results = DescriptiveStatistics.detect_outliers_zscore(df[outlier_col])
                st.markdown(f"""
                **Z-Score Method Results (threshold=3):**
                - Outliers detected: `{zscore_results['outlier_count']}`
                - Outlier percentage: `{zscore_results['outlier_pct']:.2f}%`
                """)

            # Box plot
            fig_box = px.box(df, y=outlier_col, title=f"Box Plot: {outlier_col}")
            st.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        st.markdown("## Correlation Analysis")

        # Correlation matrix
        st.markdown("### Correlation Matrix")

        corr_cols = st.multiselect(
            "Select variables for correlation",
            numeric_cols,
            default=numeric_cols[:6]
        )

        if len(corr_cols) >= 2:
            col1, col2 = st.columns([2, 1])

            with col1:
                fig_heatmap = create_correlation_heatmap(df, corr_cols)
                st.plotly_chart(fig_heatmap, use_container_width=True)

            with col2:
                st.markdown("### Top Correlations")

                # Calculate all correlations
                corr_matrix = df[corr_cols].corr()
                correlations = []

                for i, col1_name in enumerate(corr_cols):
                    for col2_name in corr_cols[i+1:]:
                        corr_val = corr_matrix.loc[col1_name, col2_name]
                        correlations.append({
                            'Variable 1': col1_name.replace('_', ' ').title(),
                            'Variable 2': col2_name.replace('_', ' ').title(),
                            'Correlation': corr_val
                        })

                corr_df = pd.DataFrame(correlations)
                corr_df = corr_df.sort_values('Correlation', key=abs, ascending=False)
                st.dataframe(corr_df.head(10), use_container_width=True)

            # Detailed correlation analysis
            st.markdown("### Pairwise Correlation Analysis")

            col1, col2 = st.columns(2)

            with col1:
                var1 = st.selectbox("First variable", corr_cols, key='var1')
            with col2:
                var2 = st.selectbox("Second variable",
                                   [c for c in corr_cols if c != var1],
                                   key='var2')

            if var1 and var2:
                col1, col2 = st.columns(2)

                with col1:
                    # Scatter plot
                    fig_scatter = px.scatter(
                        df, x=var1, y=var2,
                        trendline='ols',
                        title=f"{var1} vs {var2}"
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)

                with col2:
                    # Statistical results
                    pearson = CorrelationAnalysis.pearson_correlation(df[var1], df[var2])
                    spearman = CorrelationAnalysis.spearman_correlation(df[var1], df[var2])

                    st.markdown(f"""
                    **Pearson Correlation:**
                    - Coefficient: `{pearson['correlation']:.4f}`
                    - P-value: `{pearson['p_value']:.4f}`
                    - Strength: `{pearson['strength']}`
                    - Significant: `{'Yes' if pearson['significant'] else 'No'}`

                    **Spearman Correlation:**
                    - Coefficient: `{spearman['correlation']:.4f}`
                    - P-value: `{spearman['p_value']:.4f}`
                    - Strength: `{spearman['strength']}`
                    - Significant: `{'Yes' if spearman['significant'] else 'No'}`
                    """)

    with tab3:
        st.markdown("## Hypothesis Testing")

        # Test selection
        test_type = st.selectbox(
            "Select test type",
            ["ANOVA", "T-Test", "Normality Test", "Trend Analysis"]
        )

        if test_type == "ANOVA":
            st.markdown("### One-Way ANOVA")
            st.markdown("Test if means differ significantly across groups")

            col1, col2 = st.columns(2)

            with col1:
                dependent_var = st.selectbox("Dependent variable", numeric_cols)
            with col2:
                group_var = st.selectbox("Grouping variable",
                                        ['conflict_phase', 'region', 'airline_type'])

            if st.button("Run ANOVA Test"):
                result = HypothesisTesting.anova_test(df, dependent_var, group_var)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    ### Results

                    - **F-statistic:** `{result['statistic']:.4f}`
                    - **P-value:** `{result['p_value']:.6f}`
                    - **Number of groups:** `{result['num_groups']}`
                    - **Effect size (η²):** `{result['eta_squared']:.4f}`
                    - **Effect interpretation:** `{result['effect_size']}`

                    ### Conclusion
                    {'✅ **Reject null hypothesis:** There is a statistically significant difference between groups.' if result['significant'] else '❌ **Fail to reject null hypothesis:** No statistically significant difference found.'}
                    """)

                with col2:
                    # Box plot
                    fig_box = px.box(df, x=group_var, y=dependent_var,
                                    title=f"{dependent_var} by {group_var}")
                    st.plotly_chart(fig_box, use_container_width=True)

        elif test_type == "T-Test":
            st.markdown("### Independent Samples T-Test")
            st.markdown("Compare means between two groups")

            col1, col2 = st.columns(2)

            with col1:
                test_var = st.selectbox("Variable to compare", numeric_cols)
            with col2:
                group_var = st.selectbox("Grouping variable", ['region', 'airline_type'])

            groups = df[group_var].unique()
            if len(groups) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    group1 = st.selectbox("Group 1", groups)
                with col2:
                    group2 = st.selectbox("Group 2", [g for g in groups if g != group1])

                if st.button("Run T-Test"):
                    data1 = df[df[group_var] == group1][test_var]
                    data2 = df[df[group_var] == group2][test_var]

                    result = HypothesisTesting.t_test_independent(data1, data2)

                    st.markdown(f"""
                    ### Results

                    - **T-statistic:** `{result['statistic']:.4f}`
                    - **P-value:** `{result['p_value']:.6f}`
                    - **{group1} mean:** `{result['group1_mean']:.2f}`
                    - **{group2} mean:** `{result['group2_mean']:.2f}`
                    - **Mean difference:** `{result['mean_difference']:.2f}`
                    - **Cohen's d (effect size):** `{result['effect_size']:.4f}`

                    ### Conclusion
                    {'✅ The difference between groups is statistically significant.' if result['significant'] else '❌ No statistically significant difference between groups.'}
                    """)

        elif test_type == "Normality Test":
            st.markdown("### Normality Test")

            test_var = st.selectbox("Variable to test", numeric_cols)

            if st.button("Run Normality Test"):
                result = HypothesisTesting.normality_test(df[test_var])

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    ### Shapiro-Wilk Test Results

                    - **Test statistic:** `{result['statistic']:.4f}`
                    - **P-value:** `{result['p_value']:.6f}`
                    - **Interpretation:** `{result['interpretation']}`

                    {'✅ Data appears to follow a normal distribution.' if result['is_normal'] else '❌ Data does not appear to follow a normal distribution.'}
                    """)

                with col2:
                    # Q-Q plot
                    from scipy import stats
                    fig = go.Figure()
                    data = df[test_var].dropna()
                    theoretical = np.sort(stats.norm.ppf(np.linspace(0.01, 0.99, len(data))))
                    sample = np.sort(data.values)

                    fig.add_trace(go.Scatter(x=theoretical, y=sample, mode='markers', name='Data'))
                    fig.add_trace(go.Scatter(x=theoretical, y=theoretical, mode='lines', name='Normal'))
                    fig.update_layout(title='Q-Q Plot', xaxis_title='Theoretical Quantiles',
                                     yaxis_title='Sample Quantiles')
                    st.plotly_chart(fig, use_container_width=True)

        elif test_type == "Trend Analysis":
            st.markdown("### Time Series Trend Analysis")

            trend_var = st.selectbox("Variable for trend analysis", numeric_cols)

            # Aggregate by month
            monthly = df.groupby('month')[trend_var].mean().reset_index()

            result = TimeSeriesAnalysis.trend_analysis(monthly[trend_var])

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                ### Trend Analysis Results

                - **Trend direction:** `{result['trend_direction']}`
                - **Slope:** `{result['slope']:.4f}`
                - **R-squared:** `{result['r_squared']:.4f}`
                - **P-value:** `{result['p_value']:.6f}`
                - **Significant:** `{'Yes' if result['significant'] else 'No'}`

                **Interpretation:** {'Significant upward trend detected.' if result['trend_direction'] == 'upward' else 'Significant downward trend detected.' if result['trend_direction'] == 'downward' else 'No significant trend detected.'}
                """)

            with col2:
                fig = px.line(monthly, x='month', y=trend_var, title=f'{trend_var} Trend Over Time')
                fig.add_trace(go.Scatter(
                    x=monthly['month'],
                    y=result['slope'] * np.arange(len(monthly)) + monthly[trend_var].iloc[0],
                    mode='lines',
                    name='Trend Line',
                    line=dict(dash='dash', color='red')
                ))
                st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown("## Data Quality Assessment")

        # Generate quality report
        quality_report = DataQualityReport(df, "Financial Timeseries")

        # Quality score
        quality_score = quality_report.get_quality_score()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Data Quality Score", f"{quality_score:.1f}%")
        with col2:
            st.metric("Total Records", f"{quality_report.report['rows']:,}")
        with col3:
            st.metric("Total Columns", quality_report.report['columns'])

        st.markdown("---")

        # Column summary
        st.markdown("### Column Quality Summary")
        summary_df = quality_report.get_summary()
        st.dataframe(summary_df, use_container_width=True)

        # Missing values visualization
        st.markdown("### Missing Values Analysis")

        null_data = []
        for col, info in quality_report.report['columns_info'].items():
            null_data.append({
                'Column': col,
                'Null Count': info['null_count'],
                'Null %': info['null_pct']
            })

        null_df = pd.DataFrame(null_data)
        null_df = null_df[null_df['Null Count'] > 0].sort_values('Null %', ascending=False)

        if len(null_df) > 0:
            fig = px.bar(null_df, x='Column', y='Null %',
                        title="Missing Values by Column")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No missing values in the dataset!")

        # Duplicates
        st.markdown("### Duplicate Analysis")
        st.metric("Duplicate Rows", quality_report.report['duplicates'])

        # Memory usage
        st.markdown("### Memory Usage")
        st.metric("Memory Size", f"{quality_report.report['memory_usage_mb']:.2f} MB")

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is initialized by visiting the main page first.")
