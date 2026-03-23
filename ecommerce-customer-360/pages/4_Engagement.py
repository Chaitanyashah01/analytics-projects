"""
Engagement Metrics Page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_customers, get_filter_options
from utils.statistics import CorrelationAnalysis, RegressionAnalysis

st.set_page_config(page_title="Engagement", page_icon="📱", layout="wide")

st.title("📱 Customer Engagement Metrics")
st.markdown("Analyzing app usage, session behavior, and platform engagement")

try:
    df = get_all_customers()
    options = get_filter_options()

    # Engagement KPIs
    st.markdown("### Engagement Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Session Time", f"{df['daily_session_time_minutes'].mean():.0f} min")
    with col2:
        st.metric("Avg Product Views", f"{df['product_views_per_day'].mean():.1f}")
    with col3:
        st.metric("Avg Ad Clicks", f"{df['ad_clicks_per_day'].mean():.1f}")
    with col4:
        st.metric("Avg Engagement Score", f"{df['engagement_score'].mean():.1f}")

    st.markdown("---")

    # Session time analysis
    st.markdown("### Session Time Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='daily_session_time_minutes',
            nbins=40,
            title="Daily Session Time Distribution",
            color='device_type'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        device_stats = df.groupby('device_type').agg({
            'daily_session_time_minutes': 'mean',
            'product_views_per_day': 'mean',
            'monthly_spend': 'mean'
        }).reset_index()

        fig = px.bar(
            device_stats,
            x='device_type',
            y='daily_session_time_minutes',
            color='monthly_spend',
            color_continuous_scale='Purples',
            title="Avg Session Time by Device"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Engagement vs spending
    st.markdown("### Engagement vs Spending Relationship")

    col1, col2 = st.columns(2)

    with col1:
        sample_df = df.sample(min(5000, len(df)))
        fig = px.scatter(
            sample_df,
            x='daily_session_time_minutes',
            y='monthly_spend',
            color='loyalty_segment',
            title="Session Time vs Monthly Spend",
            opacity=0.5,
            trendline='ols'
        )
        st.plotly_chart(fig, use_container_width=True)

        reg = RegressionAnalysis.simple_linear_regression(
            df['daily_session_time_minutes'],
            df['monthly_spend']
        )
        st.info(f"R² = {reg['r_squared']:.3f} | {reg['equation']}")

    with col2:
        fig = px.scatter(
            sample_df,
            x='engagement_score',
            y='monthly_spend',
            color='loyalty_segment',
            title="Engagement Score vs Monthly Spend",
            opacity=0.5,
            trendline='ols'
        )
        st.plotly_chart(fig, use_container_width=True)

        reg = RegressionAnalysis.simple_linear_regression(
            df['engagement_score'],
            df['monthly_spend']
        )
        st.info(f"R² = {reg['r_squared']:.3f} | {reg['equation']}")

    st.markdown("---")

    # Product views analysis
    st.markdown("### Product Browsing Behavior")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='product_views_per_day',
            nbins=30,
            title="Daily Product Views Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            sample_df,
            x='product_views_per_day',
            y='browse_to_buy_ratio',
            color='loyalty_segment',
            title="Views vs Conversion Rate",
            opacity=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # App usage patterns
    st.markdown("### App Usage Patterns")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='app_usage_frequency',
            nbins=10,
            title="App Usage Frequency Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        app_spend = df.groupby('app_usage_frequency')['monthly_spend'].mean().reset_index()

        fig = px.bar(
            app_spend,
            x='app_usage_frequency',
            y='monthly_spend',
            title="Avg Spend by App Usage Frequency",
            color='monthly_spend',
            color_continuous_scale='Purples'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Ad engagement
    st.markdown("### Advertisement Engagement")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            sample_df,
            x='ad_views_per_day',
            y='ad_clicks_per_day',
            color='monthly_spend',
            color_continuous_scale='Purples',
            title="Ad Views vs Clicks",
            opacity=0.5
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df['click_rate'] = df['ad_clicks_per_day'] / (df['ad_views_per_day'] + 0.01)
        click_by_segment = df.groupby('loyalty_segment')['click_rate'].mean().reset_index()

        fig = px.bar(
            click_by_segment,
            x='loyalty_segment',
            y='click_rate',
            title="Ad Click Rate by Segment",
            color='click_rate',
            color_continuous_scale='Purples'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Engagement correlation matrix
    st.markdown("### Engagement Metrics Correlation")

    engagement_cols = ['daily_session_time_minutes', 'product_views_per_day',
                       'ad_views_per_day', 'ad_clicks_per_day', 'wishlist_items_count',
                       'engagement_score', 'monthly_spend']
    corr_matrix = df[engagement_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[c.replace('_', ' ').title() for c in corr_matrix.columns],
        y=[c.replace('_', ' ').title() for c in corr_matrix.index],
        colorscale='RdBu_r',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}'
    ))
    fig.update_layout(title="Engagement Metrics Correlation", height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")
