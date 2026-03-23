"""
Price Analysis Page
Value analysis and price-performance relationships.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_price_performance_data, get_segment_analysis, get_filter_options
from utils.statistics import RegressionAnalysis, DescriptiveStatistics

st.set_page_config(page_title="Price Analysis", page_icon="💰", layout="wide")

st.title("💰 Price & Value Analysis")
st.markdown("Analyzing price-performance relationships and market segmentation")

try:
    df = get_price_performance_data()
    df_segments = get_segment_analysis()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")

        price_range = st.slider(
            "Price Range ($)",
            min_value=0,
            max_value=int(df['price_usd'].max()),
            value=(0, int(df['price_usd'].max())),
            step=10000
        )

        selected_fuels = st.multiselect(
            "Fuel Types",
            options['fuel_types'],
            default=options['fuel_types']
        )

    # Filter data
    df_filtered = df[
        (df['price_usd'] >= price_range[0]) &
        (df['price_usd'] <= price_range[1]) &
        (df['fuel_type_clean'].isin(selected_fuels))
    ]

    # Summary
    st.markdown("### Price Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Price", f"${df_filtered['price_usd'].mean():,.0f}")
    with col2:
        st.metric("Median Price", f"${df_filtered['price_usd'].median():,.0f}")
    with col3:
        st.metric("Min Price", f"${df_filtered['price_usd'].min():,.0f}")
    with col4:
        st.metric("Max Price", f"${df_filtered['price_usd'].max():,.0f}")

    st.markdown("---")

    # Price distribution
    st.markdown("### Price Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df_filtered,
            x='price_usd',
            nbins=40,
            color='fuel_type_clean',
            title="Price Distribution by Fuel Type",
            marginal='box'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            df_segments,
            values='model_count',
            names='price_segment',
            title="Models by Price Segment"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Price-Performance scatter
    st.markdown("### Price vs Performance")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            df_filtered,
            x='price_usd',
            y='horsepower_hp',
            color='fuel_type_clean',
            hover_name='car_name',
            hover_data=['company'],
            title="Price vs Horsepower",
            trendline='ols'
        )
        st.plotly_chart(fig, use_container_width=True)

        reg = RegressionAnalysis.simple_linear_regression(df_filtered['price_usd'], df_filtered['horsepower_hp'])
        st.info(f"R² = {reg['r_squared']:.3f} | Per $10K increase: +{reg['slope']*10000:.1f} HP")

    with col2:
        fig = px.scatter(
            df_filtered,
            x='price_usd',
            y='performance_score',
            color='fuel_type_clean',
            hover_name='car_name',
            hover_data=['company'],
            title="Price vs Performance Score",
            trendline='ols'
        )
        st.plotly_chart(fig, use_container_width=True)

        reg = RegressionAnalysis.simple_linear_regression(df_filtered['price_usd'], df_filtered['performance_score'])
        st.info(f"R² = {reg['r_squared']:.3f} | Per $10K increase: +{reg['slope']*10000:.1f} points")

    st.markdown("---")

    # Value analysis (Price per HP)
    st.markdown("### Value Analysis: Price per Horsepower")

    col1, col2 = st.columns(2)

    with col1:
        # Best value cars (lowest price per HP)
        df_value = df_filtered[df_filtered['price_per_hp'].notna()].copy()
        best_value = df_value.nsmallest(10, 'price_per_hp')

        fig = px.bar(
            best_value,
            x='price_per_hp',
            y='car_name',
            orientation='h',
            color='company',
            title="Best Value: Lowest $/HP"
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(
            df_filtered,
            x='price_segment',
            y='price_per_hp',
            color='price_segment',
            title="Price per HP by Segment"
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Segment analysis
    st.markdown("### Segment Performance Comparison")

    df_seg_display = df_segments.copy()
    df_seg_display.columns = [
        'Segment', 'Models', 'Avg Price', 'Avg HP', 'Avg Speed',
        'Avg 0-100', 'Avg Perf Score', 'Avg $/HP'
    ]

    # Segment bar chart
    fig = px.bar(
        df_segments,
        x='price_segment',
        y=['avg_horsepower', 'avg_top_speed'],
        barmode='group',
        title="Performance Metrics by Price Segment"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_seg_display.round(2), use_container_width=True)

    # Bubble chart
    st.markdown("### Multi-Dimensional Analysis")

    fig = px.scatter(
        df_filtered,
        x='price_usd',
        y='horsepower_hp',
        size='performance_score',
        color='price_segment',
        hover_name='car_name',
        hover_data=['company', 'top_speed_kmh', 'acceleration_sec'],
        title="Price vs HP (bubble size = performance score)"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    st.markdown("### Price Statistics")
    desc_stats = DescriptiveStatistics.summary(df_filtered, ['price_usd', 'price_per_hp', 'performance_score'])
    st.dataframe(desc_stats, use_container_width=True)

    st.download_button(
        label="📥 Download Data",
        data=df_filtered.to_csv(index=False),
        file_name="price_analysis.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {str(e)}")
