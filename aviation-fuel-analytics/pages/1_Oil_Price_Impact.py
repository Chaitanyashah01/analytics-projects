"""
Oil Price Impact Analysis Page
Correlation analysis between oil prices and airline financials.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_oil_price_correlation, get_monthly_oil_prices, get_filter_options
from utils.statistics import CorrelationAnalysis, RegressionAnalysis, DescriptiveStatistics
from utils.visualizations import create_correlation_heatmap, create_scatter_with_regression

st.set_page_config(page_title="Oil Price Impact", page_icon="📈", layout="wide")

st.title("📈 Oil Price Impact Analysis")
st.markdown("Analyzing the correlation between oil prices and airline financial performance")

# Load data
@st.cache_data
def load_data():
    return get_oil_price_correlation(), get_monthly_oil_prices()

try:
    df_corr, df_oil = load_data()

    # Filters
    with st.sidebar:
        st.markdown("### Filters")
        options = get_filter_options()

        selected_phases = st.multiselect(
            "Conflict Phases",
            options['conflict_phases'],
            default=options['conflict_phases']
        )

    # Filter data
    if selected_phases:
        df_corr = df_corr[df_corr['conflict_phase'].isin(selected_phases)]
        df_oil = df_oil[df_oil['conflict_phase'].isin(selected_phases)]

    # Time series visualization
    st.markdown("### Oil Prices vs Airline Profitability Over Time")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df_corr['month'],
            y=df_corr['brent_crude'],
            name="Brent Crude ($/barrel)",
            line=dict(color='#1f77b4', width=2)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_corr['month'],
            y=df_corr['jet_fuel'],
            name="Jet Fuel ($/barrel)",
            line=dict(color='#ff7f0e', width=2)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_corr['month'],
            y=df_corr['profit_margin'],
            name="Profit Margin (%)",
            line=dict(color='#2ca02c', width=2, dash='dash')
        ),
        secondary_y=True
    )

    fig.update_layout(
        title="Oil Prices and Profit Margins Time Series",
        xaxis_title="Month",
        height=450,
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    fig.update_yaxes(title_text="Price ($/barrel)", secondary_y=False)
    fig.update_yaxes(title_text="Profit Margin (%)", secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Correlation Analysis
    st.markdown("### Correlation Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Correlation heatmap
        corr_cols = ['brent_crude', 'jet_fuel', 'fuel_cost_pct', 'profit_margin', 'total_revenue']
        available_cols = [c for c in corr_cols if c in df_corr.columns]

        if len(available_cols) >= 2:
            fig_heatmap = create_correlation_heatmap(
                df_corr,
                available_cols,
                title="Correlation Matrix"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

    with col2:
        # Correlation statistics
        st.markdown("#### Statistical Correlation Results")

        # Brent vs Profit Margin
        result_brent_profit = CorrelationAnalysis.pearson_correlation(
            df_corr['brent_crude'],
            df_corr['profit_margin']
        )

        st.markdown(f"""
        **Brent Crude vs Profit Margin**
        - Correlation: `{result_brent_profit['correlation']:.3f}`
        - P-value: `{result_brent_profit['p_value']:.4f}`
        - Strength: `{result_brent_profit['strength']}`
        - Significant: `{'Yes' if result_brent_profit['significant'] else 'No'}`
        """)

        # Fuel Cost vs Profit Margin
        result_fuel_profit = CorrelationAnalysis.pearson_correlation(
            df_corr['fuel_cost_pct'],
            df_corr['profit_margin']
        )

        st.markdown(f"""
        **Fuel Cost % vs Profit Margin**
        - Correlation: `{result_fuel_profit['correlation']:.3f}`
        - P-value: `{result_fuel_profit['p_value']:.4f}`
        - Strength: `{result_fuel_profit['strength']}`
        - Significant: `{'Yes' if result_fuel_profit['significant'] else 'No'}`
        """)

    st.markdown("---")

    # Regression Analysis
    st.markdown("### Regression Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Brent Crude Price vs Profit Margin")

        fig_scatter = create_scatter_with_regression(
            df_corr,
            'brent_crude',
            'profit_margin',
            color_col='conflict_phase',
            title="Oil Price Impact on Profitability",
            show_regression=True
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Regression statistics
        reg_result = RegressionAnalysis.simple_linear_regression(
            df_corr['brent_crude'],
            df_corr['profit_margin']
        )

        st.info(f"""
        **Regression Results:**
        - Equation: `{reg_result['equation']}`
        - R-squared: `{reg_result['r_squared']:.4f}`
        - P-value: `{reg_result['p_value']:.4f}`
        - RMSE: `{reg_result['rmse']:.2f}`

        **Interpretation:** For every $1 increase in Brent crude price,
        profit margin changes by `{reg_result['slope']:.3f}` percentage points.
        """)

    with col2:
        st.markdown("#### Fuel Cost % vs Profit Margin")

        fig_scatter2 = create_scatter_with_regression(
            df_corr,
            'fuel_cost_pct',
            'profit_margin',
            color_col='conflict_phase',
            title="Fuel Cost Impact on Profitability",
            show_regression=True
        )
        st.plotly_chart(fig_scatter2, use_container_width=True)

        # Regression statistics
        reg_result2 = RegressionAnalysis.simple_linear_regression(
            df_corr['fuel_cost_pct'],
            df_corr['profit_margin']
        )

        st.info(f"""
        **Regression Results:**
        - Equation: `{reg_result2['equation']}`
        - R-squared: `{reg_result2['r_squared']:.4f}`
        - P-value: `{reg_result2['p_value']:.4f}`
        - RMSE: `{reg_result2['rmse']:.2f}`

        **Interpretation:** For every 1% increase in fuel cost ratio,
        profit margin changes by `{reg_result2['slope']:.3f}` percentage points.
        """)

    st.markdown("---")

    # Phase comparison
    st.markdown("### Performance by Conflict Phase")

    phase_stats = df_corr.groupby('conflict_phase').agg({
        'brent_crude': ['mean', 'std'],
        'profit_margin': ['mean', 'std'],
        'fuel_cost_pct': ['mean', 'std']
    }).round(2)

    phase_stats.columns = ['Avg Brent', 'Std Brent', 'Avg Profit Margin',
                           'Std Profit Margin', 'Avg Fuel Cost %', 'Std Fuel Cost %']
    phase_stats = phase_stats.reset_index()

    st.dataframe(phase_stats, use_container_width=True)

    # Box plot comparison
    fig_box = px.box(
        df_corr,
        x='conflict_phase',
        y='profit_margin',
        color='conflict_phase',
        title="Profit Margin Distribution by Conflict Phase"
    )
    fig_box.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_box, use_container_width=True)

    # Descriptive statistics
    st.markdown("### Descriptive Statistics")

    desc_stats = DescriptiveStatistics.summary(
        df_corr,
        ['brent_crude', 'jet_fuel', 'profit_margin', 'fuel_cost_pct', 'total_revenue']
    )
    st.dataframe(desc_stats, use_container_width=True)

    # Export option
    st.markdown("---")
    st.download_button(
        label="📥 Download Analysis Data",
        data=df_corr.to_csv(index=False),
        file_name="oil_price_analysis.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is initialized by visiting the main page first.")
