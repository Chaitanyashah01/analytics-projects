"""
Airline Comparison Page
Benchmark airlines across multiple performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_airline_comparison, get_financial_timeseries, get_filter_options
from utils.statistics import DescriptiveStatistics, HypothesisTesting, CorrelationAnalysis

st.set_page_config(page_title="Airline Comparison", page_icon="🏢", layout="wide")

st.title("🏢 Airline Performance Comparison")
st.markdown("Benchmark airlines across revenue, profitability, fuel efficiency, and hedging strategies")

try:
    # Load data
    df_airlines = get_airline_comparison()
    options = get_filter_options()

    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filters")

        selected_regions = st.multiselect(
            "Regions",
            options['regions'],
            default=options['regions']
        )

        selected_types = st.multiselect(
            "Airline Types",
            options['airline_types'],
            default=options['airline_types']
        )

        min_revenue = st.slider(
            "Minimum Total Revenue ($M)",
            min_value=0,
            max_value=int(df_airlines['total_revenue'].max()),
            value=0
        )

    # Filter data
    df_filtered = df_airlines[
        (df_airlines['region'].isin(selected_regions)) &
        (df_airlines['airline_type'].isin(selected_types)) &
        (df_airlines['total_revenue'] >= min_revenue)
    ]

    # Summary metrics
    st.markdown("### Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Airlines Analyzed", len(df_filtered))

    with col2:
        avg_margin = df_filtered['avg_profit_margin'].mean()
        st.metric("Avg Profit Margin", f"{avg_margin:.1f}%")

    with col3:
        total_passengers = df_filtered['total_passengers'].sum()
        st.metric("Total Passengers", f"{total_passengers:.1f}M")

    with col4:
        avg_fuel_pct = df_filtered['avg_fuel_cost_pct'].mean()
        st.metric("Avg Fuel Cost %", f"{avg_fuel_pct:.1f}%")

    st.markdown("---")

    # Top performers
    st.markdown("### Top Performers")

    col1, col2 = st.columns(2)

    with col1:
        # Top by revenue
        top_revenue = df_filtered.nlargest(10, 'total_revenue')

        fig_revenue = px.bar(
            top_revenue,
            x='total_revenue',
            y='airline',
            orientation='h',
            color='region',
            title="Top 10 Airlines by Total Revenue",
            labels={'total_revenue': 'Total Revenue ($M)', 'airline': 'Airline'}
        )
        fig_revenue.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
        st.plotly_chart(fig_revenue, width="stretch")

    with col2:
        # Top by profit margin
        top_margin = df_filtered.nlargest(10, 'avg_profit_margin')

        fig_margin = px.bar(
            top_margin,
            x='avg_profit_margin',
            y='airline',
            orientation='h',
            color='region',
            title="Top 10 Airlines by Profit Margin",
            labels={'avg_profit_margin': 'Avg Profit Margin (%)', 'airline': 'Airline'}
        )
        fig_margin.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
        st.plotly_chart(fig_margin, width="stretch")

    st.markdown("---")

    # Scatter matrix
    st.markdown("### Multi-dimensional Analysis")

    fig_scatter = px.scatter(
        df_filtered,
        x='avg_quarterly_revenue',
        y='avg_profit_margin',
        size='total_passengers',
        color='airline_type',
        hover_name='airline',
        title="Revenue vs Profitability (bubble size = passengers)",
        labels={
            'avg_quarterly_revenue': 'Avg Quarterly Revenue ($M)',
            'avg_profit_margin': 'Avg Profit Margin (%)'
        }
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, width="stretch")

    st.markdown("---")

    # Regional comparison
    st.markdown("### Regional Performance")

    col1, col2 = st.columns(2)

    with col1:
        # Group by region
        region_stats = df_filtered.groupby('region').agg({
            'total_revenue': 'sum',
            'avg_profit_margin': 'mean',
            'avg_fuel_cost_pct': 'mean',
            'total_passengers': 'sum',
            'airline': 'count'
        }).reset_index()
        region_stats.columns = ['Region', 'Total Revenue', 'Avg Margin', 'Avg Fuel %', 'Passengers', 'Airlines']

        fig_region = px.treemap(
            region_stats,
            path=['Region'],
            values='Total Revenue',
            color='Avg Margin',
            color_continuous_scale='RdYlGn',
            title="Revenue by Region (color = profit margin)"
        )
        st.plotly_chart(fig_region, width="stretch")

    with col2:
        # Box plot by region
        fig_box = px.box(
            df_filtered,
            x='region',
            y='avg_profit_margin',
            color='region',
            title="Profit Margin Distribution by Region"
        )
        fig_box.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_box, width="stretch")

    st.markdown("---")

    # Airline type comparison
    st.markdown("### Airline Type Analysis")

    col1, col2 = st.columns(2)

    with col1:
        type_stats = df_filtered.groupby('airline_type').agg({
            'avg_profit_margin': 'mean',
            'avg_fuel_cost_pct': 'mean',
            'avg_hedging_pct': 'mean'
        }).reset_index()

        fig_type = px.bar(
            type_stats,
            x='airline_type',
            y=['avg_profit_margin', 'avg_fuel_cost_pct', 'avg_hedging_pct'],
            barmode='group',
            title="Performance Metrics by Airline Type",
            labels={'value': 'Percentage', 'airline_type': 'Airline Type'}
        )
        st.plotly_chart(fig_type, width="stretch")

    with col2:
        # ANOVA test for airline types
        st.markdown("#### Statistical Test: Airline Type Differences")

        if len(df_filtered['airline_type'].unique()) >= 2:
            anova_result = HypothesisTesting.anova_test(
                df_filtered,
                'avg_profit_margin',
                'airline_type'
            )

            st.markdown(f"""
            **ANOVA Test: Profit Margin by Airline Type**

            - F-statistic: `{anova_result['statistic']:.3f}`
            - P-value: `{anova_result['p_value']:.4f}`
            - Significant: `{'Yes' if anova_result['significant'] else 'No'}`
            - Effect Size (η²): `{anova_result['eta_squared']:.3f}`

            **Interpretation:** {'Significant differences exist between airline types.' if anova_result['significant'] else 'No significant differences found between airline types.'}
            """)
        else:
            st.info("Need at least 2 airline types for comparison")

    st.markdown("---")

    # Hedging analysis
    st.markdown("### Fuel Hedging Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig_hedge = px.scatter(
            df_filtered,
            x='avg_hedging_pct',
            y='avg_profit_margin',
            color='region',
            hover_name='airline',
            title="Hedging Strategy vs Profitability",
            trendline='ols'
        )
        st.plotly_chart(fig_hedge, width="stretch")

    with col2:
        # Correlation analysis
        corr_result = CorrelationAnalysis.pearson_correlation(
            df_filtered['avg_hedging_pct'],
            df_filtered['avg_profit_margin']
        )

        st.markdown(f"""
        #### Hedging vs Profitability Correlation

        - Correlation: `{corr_result['correlation']:.3f}`
        - P-value: `{corr_result['p_value']:.4f}`
        - Strength: `{corr_result['strength']}`
        - Significant: `{'Yes' if corr_result['significant'] else 'No'}`

        **Insight:** {'Higher hedging percentages are associated with better profit margins.' if corr_result['correlation'] > 0 and corr_result['significant'] else 'No clear relationship between hedging and profitability.'}
        """)

        # Hedge savings analysis
        total_savings = df_filtered['total_hedge_savings'].sum()
        st.metric("Total Hedge Savings", f"${total_savings:.1f}M")

    st.markdown("---")

    # Full data table
    st.markdown("### Detailed Airline Data")

    # Format columns
    df_display = df_filtered.copy()
    df_display = df_display.round(2)
    df_display.columns = [
        'Airline', 'Region', 'Type', 'Avg Quarterly Rev', 'Total Revenue',
        'Avg Margin', 'Avg Fuel %', 'Total Passengers', 'Avg Hedging %',
        'Total Hedge Savings', 'Quarters Reported'
    ]

    st.dataframe(df_display, width="stretch", height=400)

    # Descriptive statistics
    st.markdown("### Descriptive Statistics")

    desc_cols = ['avg_quarterly_revenue', 'avg_profit_margin', 'avg_fuel_cost_pct',
                 'avg_hedging_pct', 'total_passengers']
    desc_stats = DescriptiveStatistics.summary(df_filtered, desc_cols)
    st.dataframe(desc_stats, width="stretch")

    # Export
    st.markdown("---")
    st.download_button(
        label="📥 Download Airline Data",
        data=df_filtered.to_csv(index=False),
        file_name="airline_comparison.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is initialized by visiting the main page first.")
