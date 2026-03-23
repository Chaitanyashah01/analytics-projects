"""
Customer Segmentation Page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_customers, get_segment_summary, get_cohort_analysis
from utils.statistics import HypothesisTesting

st.set_page_config(page_title="Segmentation", page_icon="🎯", layout="wide")

st.title("🎯 Customer Segmentation")
st.markdown("Customer segments based on value, behavior, and engagement")

try:
    df = get_all_customers()
    df_segments = get_segment_summary()
    df_cohorts = get_cohort_analysis()

    # Segment overview
    st.markdown("### Segment Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    segments = ['Champion', 'Loyal', 'Regular', 'Occasional', 'At Risk']
    for i, (col, seg) in enumerate(zip([col1, col2, col3, col4, col5], segments)):
        with col:
            count = len(df[df['loyalty_segment'] == seg])
            st.metric(seg, f"{count:,}")

    st.markdown("---")

    # Segment distribution
    st.markdown("### Segment Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            df_segments,
            values='customer_count',
            names='loyalty_segment',
            title="Customer Distribution by Segment",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            df_segments,
            x='loyalty_segment',
            y=['avg_spend', 'avg_aov'],
            barmode='group',
            title="Spend Metrics by Segment"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Segment profiles
    st.markdown("### Segment Profiles")

    # Radar chart for segment comparison
    metrics = ['avg_spend', 'avg_purchases', 'avg_aov']
    df_radar = df_segments.copy()

    # Normalize for radar
    for m in metrics:
        if m in df_radar.columns:
            df_radar[f'{m}_norm'] = df_radar[m] / df_radar[m].max()

    fig = go.Figure()

    for _, row in df_radar.iterrows():
        if row['loyalty_segment'] is not None:
            fig.add_trace(go.Scatterpolar(
                r=[row.get(f'{m}_norm', 0) for m in metrics],
                theta=[m.replace('avg_', '').replace('_', ' ').title() for m in metrics],
                fill='toself',
                name=row['loyalty_segment']
            ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="Segment Profile Comparison",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Cohort analysis
    st.markdown("### Cohort Analysis: Segment by Age Group")

    # Create heatmap
    pivot_data = df_cohorts.pivot(
        index='loyalty_segment',
        columns='age_group',
        values='customer_count'
    ).fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns.tolist(),
        y=pivot_data.index.tolist(),
        colorscale='Purples',
        colorbar=dict(title="Customers")
    ))
    fig.update_layout(
        title="Customer Count: Segment vs Age Group",
        xaxis_title="Age Group",
        yaxis_title="Loyalty Segment",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Value distribution by segment
    st.markdown("### Customer Value Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(
            df,
            x='loyalty_segment',
            y='customer_value_score',
            color='loyalty_segment',
            title="Value Score Distribution by Segment"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(
            df,
            x='loyalty_segment',
            y='engagement_score',
            color='loyalty_segment',
            title="Engagement Score by Segment"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Statistical testing
    st.markdown("### Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ANOVA: Spend Across Segments")
        anova_result = HypothesisTesting.anova_test(df, 'monthly_spend', 'loyalty_segment')

        st.markdown(f"""
        - F-statistic: `{anova_result['statistic']:.2f}`
        - P-value: `{anova_result['p_value']:.6f}`
        - Effect Size (η²): `{anova_result['eta_squared']:.4f}`

        **Result:** {'Significant differences across segments' if anova_result['significant'] else 'No significant differences'}
        """)

    with col2:
        st.markdown("#### Segment Summary Table")
        display_df = df_segments.copy()
        display_df.columns = ['Segment', 'Customers', 'Avg Spend', 'Avg Purchases', 'Avg AOV', 'Avg Abandon']
        st.dataframe(display_df.round(2), use_container_width=True)

    # Segment migration potential
    st.markdown("### Segment Characteristics")

    segment_chars = df.groupby('loyalty_segment').agg({
        'age': 'mean',
        'income_level': 'mean',
        'loyalty_program_member': 'mean',
        'coupon_usage_frequency': 'mean',
        'daily_session_time_minutes': 'mean'
    }).reset_index()

    segment_chars.columns = ['Segment', 'Avg Age', 'Avg Income', 'Loyalty Member %', 'Coupon Usage', 'Session Time']
    segment_chars['Loyalty Member %'] = segment_chars['Loyalty Member %'] * 100

    st.dataframe(segment_chars.round(2), use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")
