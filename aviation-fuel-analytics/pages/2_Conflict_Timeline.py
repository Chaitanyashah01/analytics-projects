"""
Conflict Event Timeline Page
Interactive visualization of geopolitical events and their impact.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_conflict_events, get_monthly_oil_prices
from utils.statistics import DescriptiveStatistics, HypothesisTesting

st.set_page_config(page_title="Conflict Timeline", page_icon="⚠️", layout="wide")

st.title("⚠️ Conflict Event Timeline")
st.markdown("Analyzing the impact of geopolitical events on oil prices and airfares")

try:
    # Load data
    df_events = get_conflict_events()
    df_oil = get_monthly_oil_prices()

    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filters")

        event_types = df_events['event_type'].unique().tolist()
        selected_types = st.multiselect(
            "Event Types",
            event_types,
            default=event_types
        )

        severities = df_events['severity'].unique().tolist()
        selected_severity = st.multiselect(
            "Severity Levels",
            severities,
            default=severities
        )

    # Filter events
    df_filtered = df_events[
        (df_events['event_type'].isin(selected_types)) &
        (df_events['severity'].isin(selected_severity))
    ]

    # Summary metrics
    st.markdown("### Event Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Events", len(df_filtered))

    with col2:
        avg_oil_impact = df_filtered['oil_price_change_pct'].mean()
        st.metric("Avg Oil Impact", f"{avg_oil_impact:.1f}%")

    with col3:
        avg_airfare_impact = df_filtered['airfare_impact_pct'].mean()
        st.metric("Avg Airfare Impact", f"{avg_airfare_impact:.1f}%")

    with col4:
        total_cancellations = df_filtered['flight_cancellations_est'].sum()
        st.metric("Est. Flight Cancellations", f"{total_cancellations:,.0f}")

    st.markdown("---")

    # Interactive Timeline
    st.markdown("### Event Timeline")

    # Create timeline visualization
    severity_colors = {
        'Low': '#28a745',
        'Medium': '#ffc107',
        'High': '#fd7e14',
        'Very High': '#dc3545'
    }

    fig = go.Figure()

    for severity in df_filtered['severity'].unique():
        subset = df_filtered[df_filtered['severity'] == severity]

        fig.add_trace(go.Scatter(
            x=subset['event_date'],
            y=subset['oil_price_change_pct'],
            mode='markers',
            name=severity,
            marker=dict(
                size=subset['oil_price_change_pct'].abs() * 2 + 15,
                color=severity_colors.get(severity, '#17a2b8'),
                line=dict(width=2, color='white')
            ),
            text=subset['event_description'],
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Date: %{x}<br>'
                'Oil Impact: %{y:.1f}%<br>'
                '<extra></extra>'
            )
        ))

    # Add reference line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title="Geopolitical Events and Oil Price Impact",
        xaxis_title="Date",
        yaxis_title="Oil Price Change (%)",
        height=500,
        hovermode='closest',
        legend=dict(title="Severity")
    )

    st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Event Details Table
    st.markdown("### Event Details")

    # Display columns
    display_cols = [
        'event_date', 'event_type', 'severity', 'location',
        'oil_price_change_pct', 'airfare_impact_pct',
        'flight_cancellations_est', 'airspace_closures_countries'
    ]

    df_display = df_filtered[display_cols].copy()
    df_display['event_date'] = pd.to_datetime(df_display['event_date']).dt.strftime('%Y-%m-%d')
    df_display.columns = [
        'Date', 'Type', 'Severity', 'Location',
        'Oil Impact %', 'Airfare Impact %',
        'Flight Cancellations', 'Airspace Closures'
    ]

    st.dataframe(df_display, width="stretch", height=400)

    st.markdown("---")

    # Analysis by Event Type
    st.markdown("### Analysis by Event Type")

    col1, col2 = st.columns(2)

    with col1:
        # Average impact by event type
        type_impact = df_filtered.groupby('event_type').agg({
            'oil_price_change_pct': 'mean',
            'airfare_impact_pct': 'mean',
            'flight_cancellations_est': 'sum'
        }).round(2).reset_index()

        fig_bar = px.bar(
            type_impact,
            x='event_type',
            y=['oil_price_change_pct', 'airfare_impact_pct'],
            barmode='group',
            title="Average Impact by Event Type",
            labels={'value': 'Impact (%)', 'event_type': 'Event Type'}
        )
        st.plotly_chart(fig_bar, width="stretch")

    with col2:
        # Events by severity
        severity_counts = df_filtered['severity'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']

        fig_pie = px.pie(
            severity_counts,
            values='Count',
            names='Severity',
            title="Events by Severity Level",
            color='Severity',
            color_discrete_map=severity_colors
        )
        st.plotly_chart(fig_pie, width="stretch")

    st.markdown("---")

    # Statistical Analysis
    st.markdown("### Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Impact by Severity - ANOVA Test")

        if len(df_filtered['severity'].unique()) >= 2:
            anova_result = HypothesisTesting.anova_test(
                df_filtered,
                'oil_price_change_pct',
                'severity'
            )

            st.markdown(f"""
            **Testing if oil price impact differs significantly across severity levels:**

            - F-statistic: `{anova_result['statistic']:.3f}`
            - P-value: `{anova_result['p_value']:.4f}`
            - Significant: `{'Yes' if anova_result['significant'] else 'No'}`
            - Effect Size (η²): `{anova_result['eta_squared']:.3f}` ({anova_result['effect_size']})

            **Interpretation:** {'There is a statistically significant difference in oil price impact across severity levels.' if anova_result['significant'] else 'No significant difference found across severity levels.'}
            """)
        else:
            st.info("Need at least 2 severity levels for ANOVA test")

    with col2:
        st.markdown("#### Descriptive Statistics")

        desc_stats = DescriptiveStatistics.summary(
            df_filtered,
            ['oil_price_change_pct', 'airfare_impact_pct', 'flight_cancellations_est']
        )
        st.dataframe(desc_stats, width="stretch")

    # Box plot by severity
    st.markdown("#### Impact Distribution by Severity")

    fig_box = px.box(
        df_filtered,
        x='severity',
        y='oil_price_change_pct',
        color='severity',
        color_discrete_map=severity_colors,
        title="Oil Price Impact Distribution by Severity"
    )
    fig_box.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_box, width="stretch")

    # Correlation between oil impact and airfare impact
    st.markdown("---")
    st.markdown("### Oil vs Airfare Impact Correlation")

    fig_scatter = px.scatter(
        df_filtered,
        x='oil_price_change_pct',
        y='airfare_impact_pct',
        color='severity',
        size='flight_cancellations_est',
        hover_data=['event_type', 'location'],
        title="Relationship Between Oil and Airfare Impact",
        color_discrete_map=severity_colors,
        trendline='ols'
    )
    st.plotly_chart(fig_scatter, width="stretch")

    # Export
    st.markdown("---")
    st.download_button(
        label="📥 Download Events Data",
        data=df_filtered.to_csv(index=False),
        file_name="conflict_events.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is initialized by visiting the main page first.")
