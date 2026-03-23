"""
Performance Analysis Page
Analyze vehicle performance metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_cars, get_top_performers, get_filter_options
from utils.statistics import DescriptiveStatistics, CorrelationAnalysis, RegressionAnalysis

st.set_page_config(page_title="Performance Analysis", page_icon="⚡", layout="wide")

st.title("⚡ Performance Analysis")
st.markdown("Analyzing vehicle speed, power, and acceleration metrics")

try:
    df = get_all_cars()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")

        selected_brands = st.multiselect(
            "Brands",
            options['brands'],
            default=[]
        )

        selected_fuels = st.multiselect(
            "Fuel Types",
            options['fuel_types'],
            default=[]
        )

        min_hp = st.slider(
            "Minimum Horsepower",
            min_value=0,
            max_value=int(df['horsepower_hp'].max()),
            value=0
        )

    # Filter data
    df_filtered = df.copy()
    if selected_brands:
        df_filtered = df_filtered[df_filtered['company'].isin(selected_brands)]
    if selected_fuels:
        df_filtered = df_filtered[df_filtered['fuel_type_clean'].isin(selected_fuels)]
    if min_hp > 0:
        df_filtered = df_filtered[df_filtered['horsepower_hp'] >= min_hp]

    # Summary stats
    st.markdown("### Performance Metrics Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Horsepower", f"{df_filtered['horsepower_hp'].mean():.0f} HP")
    with col2:
        st.metric("Avg Top Speed", f"{df_filtered['top_speed_kmh'].mean():.0f} km/h")
    with col3:
        st.metric("Avg 0-100 km/h", f"{df_filtered['acceleration_sec'].mean():.1f} sec")
    with col4:
        st.metric("Avg Torque", f"{df_filtered['torque_nm'].mean():.0f} Nm")

    st.markdown("---")

    # Top performers
    st.markdown("### Top Performers")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Most Powerful")
        top_hp = df_filtered.nlargest(5, 'horsepower_hp')[['company', 'car_name', 'horsepower_hp']]
        st.dataframe(top_hp, width="stretch", hide_index=True)

    with col2:
        st.markdown("#### Fastest Top Speed")
        top_speed = df_filtered.nlargest(5, 'top_speed_kmh')[['company', 'car_name', 'top_speed_kmh']]
        st.dataframe(top_speed, width="stretch", hide_index=True)

    with col3:
        st.markdown("#### Quickest Acceleration")
        top_accel = df_filtered.nsmallest(5, 'acceleration_sec')[['company', 'car_name', 'acceleration_sec']]
        st.dataframe(top_accel, width="stretch", hide_index=True)

    st.markdown("---")

    # Scatter plots
    st.markdown("### Performance Relationships")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            df_filtered,
            x='horsepower_hp',
            y='top_speed_kmh',
            color='fuel_type_clean',
            hover_name='car_name',
            hover_data=['company', 'price_usd'],
            title="Horsepower vs Top Speed",
            trendline='ols'
        )
        st.plotly_chart(fig, width="stretch")

        # Regression stats
        reg_result = RegressionAnalysis.simple_linear_regression(
            df_filtered['horsepower_hp'].dropna(),
            df_filtered['top_speed_kmh'].dropna()
        )
        st.info(f"R² = {reg_result['r_squared']:.3f} | {reg_result['equation']}")

    with col2:
        fig = px.scatter(
            df_filtered,
            x='horsepower_hp',
            y='acceleration_sec',
            color='fuel_type_clean',
            hover_name='car_name',
            hover_data=['company', 'price_usd'],
            title="Horsepower vs 0-100 km/h Time",
            trendline='ols'
        )
        st.plotly_chart(fig, width="stretch")

        reg_result = RegressionAnalysis.simple_linear_regression(
            df_filtered['horsepower_hp'].dropna(),
            df_filtered['acceleration_sec'].dropna()
        )
        st.info(f"R² = {reg_result['r_squared']:.3f} | {reg_result['equation']}")

    st.markdown("---")

    # Distribution analysis
    st.markdown("### Performance Distributions")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df_filtered,
            x='horsepower_hp',
            nbins=30,
            color='fuel_type_clean',
            title="Horsepower Distribution",
            marginal='box'
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.histogram(
            df_filtered,
            x='acceleration_sec',
            nbins=30,
            color='fuel_type_clean',
            title="Acceleration Time Distribution",
            marginal='box'
        )
        st.plotly_chart(fig, width="stretch")

    # Correlation analysis
    st.markdown("### Correlation Analysis")

    corr_cols = ['horsepower_hp', 'top_speed_kmh', 'acceleration_sec', 'torque_nm', 'cc_numeric', 'price_usd']
    corr_matrix = df_filtered[corr_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[c.replace('_', ' ').title() for c in corr_matrix.columns],
        y=[c.replace('_', ' ').title() for c in corr_matrix.index],
        colorscale='RdBu_r',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    fig.update_layout(title="Performance Metrics Correlation Matrix", height=500)
    st.plotly_chart(fig, width="stretch")

    # Descriptive statistics
    st.markdown("### Descriptive Statistics")
    desc_stats = DescriptiveStatistics.summary(df_filtered, corr_cols)
    st.dataframe(desc_stats, width="stretch")

    st.download_button(
        label="📥 Download Data",
        data=df_filtered.to_csv(index=False),
        file_name="performance_analysis.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {str(e)}")
