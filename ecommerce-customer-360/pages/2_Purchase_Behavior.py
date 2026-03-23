"""
Purchase Behavior Analysis Page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_customers, get_behavior_metrics, get_filter_options
from utils.statistics import DescriptiveStatistics, CorrelationAnalysis

st.set_page_config(page_title="Purchase Behavior", page_icon="💳", layout="wide")

st.title("💳 Purchase Behavior Analysis")
st.markdown("Analyzing spending patterns, purchase frequency, and cart behavior")

try:
    df = get_all_customers()
    df_behavior = get_behavior_metrics()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")
        selected_segments = st.multiselect(
            "Loyalty Segments",
            options['loyalty_segments'],
            default=[]
        )

    if selected_segments:
        df = df[df['loyalty_segment'].isin(selected_segments)]

    # KPIs
    st.markdown("### Purchase Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Avg Monthly Spend", f"${df['monthly_spend'].mean():,.0f}")
    with col2:
        st.metric("Avg Order Value", f"${df['average_order_value'].mean():,.0f}")
    with col3:
        st.metric("Avg Weekly Purchases", f"{df['weekly_purchases'].mean():.1f}")
    with col4:
        st.metric("Cart Abandonment", f"{df['cart_abandonment_rate'].mean():.1f}%")

    st.markdown("---")

    # Spending distribution
    st.markdown("### Spending Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='monthly_spend',
            nbins=50,
            title="Monthly Spend Distribution",
            color='spend_segment'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        spend_seg = df['spend_segment'].value_counts().reset_index()
        spend_seg.columns = ['Segment', 'Count']

        fig = px.pie(
            spend_seg,
            values='Count',
            names='Segment',
            title="Spend Segments"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Purchase frequency
    st.markdown("### Purchase Frequency Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            df.sample(min(5000, len(df))),
            x='weekly_purchases',
            y='monthly_spend',
            color='loyalty_segment',
            title="Purchase Frequency vs Monthly Spend",
            opacity=0.6
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            df,
            x='weekly_purchases',
            nbins=30,
            title="Weekly Purchase Frequency Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Category analysis
    st.markdown("### Product Category Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df_behavior,
            x='category',
            y='customer_count',
            color='avg_spend',
            color_continuous_scale='Purples',
            title="Customers by Product Category"
        )
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_behavior,
            x='category',
            y='avg_aov',
            color='avg_abandonment',
            color_continuous_scale='RdYlGn_r',
            title="Avg Order Value by Category"
        )
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Cart abandonment
    st.markdown("### Cart Abandonment Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='cart_abandonment_rate',
            nbins=30,
            title="Cart Abandonment Rate Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Abandonment by segment
        abandon_by_seg = df.groupby('loyalty_segment')['cart_abandonment_rate'].mean().reset_index()

        fig = px.bar(
            abandon_by_seg,
            x='loyalty_segment',
            y='cart_abandonment_rate',
            title="Cart Abandonment by Customer Segment",
            color='cart_abandonment_rate',
            color_continuous_scale='RdYlGn_r'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Payment methods
    st.markdown("### Payment Preferences")

    payment_stats = df.groupby('preferred_payment_method').agg({
        'user_id': 'count',
        'monthly_spend': 'mean',
        'average_order_value': 'mean'
    }).reset_index()
    payment_stats.columns = ['Payment Method', 'Customers', 'Avg Spend', 'Avg AOV']

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            payment_stats,
            values='Customers',
            names='Payment Method',
            title="Payment Method Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            payment_stats,
            x='Payment Method',
            y='Avg Spend',
            title="Avg Spend by Payment Method",
            color='Avg AOV',
            color_continuous_scale='Purples'
        )
        st.plotly_chart(fig, use_container_width=True)

    # Correlation analysis
    st.markdown("### Correlation Analysis")

    behavior_cols = ['monthly_spend', 'weekly_purchases', 'average_order_value',
                    'cart_abandonment_rate', 'browse_to_buy_ratio']
    corr_matrix = df[behavior_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[c.replace('_', ' ').title() for c in corr_matrix.columns],
        y=[c.replace('_', ' ').title() for c in corr_matrix.index],
        colorscale='RdBu_r',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}'
    ))
    fig.update_layout(title="Purchase Behavior Correlations", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    st.markdown("### Descriptive Statistics")
    desc_stats = DescriptiveStatistics.summary(df, behavior_cols)
    st.dataframe(desc_stats, use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")
