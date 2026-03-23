"""
Source Comparison Page - Wind vs Solar analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_source_summary, get_daily_production, get_hourly_pattern
from utils.statistics import HypothesisTesting, DescriptiveStatistics

st.set_page_config(page_title="Source Comparison", page_icon="⚡", layout="wide")

st.title("⚡ Wind vs Solar Comparison")
st.markdown("Comparing production characteristics between wind and solar energy")

try:
    df_sources = get_source_summary()
    df_daily = get_daily_production()
    df_hourly = get_hourly_pattern()

    # Summary metrics
    st.markdown("### Production Summary")

    wind_data = df_sources[df_sources['source'] == 'Wind'].iloc[0] if len(df_sources[df_sources['source'] == 'Wind']) > 0 else None
    solar_data = df_sources[df_sources['source'] == 'Solar'].iloc[0] if len(df_sources[df_sources['source'] == 'Solar']) > 0 else None

    col1, col2, col3, col4 = st.columns(4)

    if wind_data is not None:
        with col1:
            st.metric("Wind Total", f"{wind_data['total_production']/1e6:.2f}M MWh")
        with col2:
            st.metric("Wind Avg", f"{wind_data['avg_production']:,.0f} MWh")

    if solar_data is not None:
        with col3:
            st.metric("Solar Total", f"{solar_data['total_production']/1e6:.2f}M MWh")
        with col4:
            st.metric("Solar Avg", f"{solar_data['avg_production']:,.0f} MWh")

    st.markdown("---")

    # Daily comparison
    st.markdown("### Daily Production Trends")

    # Pivot for comparison
    df_pivot = df_daily.pivot(index='date', columns='source', values='total_production').reset_index()

    fig = go.Figure()
    for source in df_daily['source'].unique():
        source_data = df_daily[df_daily['source'] == source]
        fig.add_trace(go.Scatter(
            x=source_data['date'],
            y=source_data['total_production'],
            name=source,
            mode='lines'
        ))

    fig.update_layout(
        title="Daily Production by Source",
        xaxis_title="Date",
        yaxis_title="Production (MWh)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Hourly patterns
    st.markdown("### Hourly Production Patterns")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            df_hourly,
            x='start_hour',
            y='avg_production',
            color='source',
            title="Average Hourly Production",
            markers=True
        )
        fig.update_layout(xaxis_title="Hour of Day", yaxis_title="Avg Production (MWh)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Create heatmap data
        fig = px.bar(
            df_hourly,
            x='start_hour',
            y='avg_production',
            color='source',
            barmode='group',
            title="Hourly Production Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Statistical comparison
    st.markdown("### Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Production Distribution")

        from database.queries import get_all_data
        df_all = get_all_data()

        fig = px.box(
            df_all,
            x='source',
            y='production',
            color='source',
            title="Production Distribution by Source"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### T-Test: Wind vs Solar")

        wind_prod = df_all[df_all['source'] == 'Wind']['production']
        solar_prod = df_all[df_all['source'] == 'Solar']['production']

        if len(wind_prod) > 1 and len(solar_prod) > 1:
            t_result = HypothesisTesting.t_test_independent(wind_prod, solar_prod)

            st.markdown(f"""
            **Independent Samples T-Test:**

            - Wind Mean: `{t_result['group1_mean']:,.0f} MWh`
            - Solar Mean: `{t_result['group2_mean']:,.0f} MWh`
            - Difference: `{t_result['mean_difference']:,.0f} MWh`
            - T-statistic: `{t_result['statistic']:.3f}`
            - P-value: `{t_result['p_value']:.6f}`
            - Cohen's d: `{t_result['effect_size']:.3f}`

            **Result:** {'Significant difference between sources' if t_result['significant'] else 'No significant difference'}
            """)

    # Variability analysis
    st.markdown("### Production Variability")

    variability = df_all.groupby('source')['production'].agg(['mean', 'std', 'min', 'max']).reset_index()
    variability['cv'] = (variability['std'] / variability['mean'] * 100).round(2)
    variability.columns = ['Source', 'Mean', 'Std Dev', 'Min', 'Max', 'CV (%)']

    st.dataframe(variability.round(2), use_container_width=True)

    # Histogram comparison
    fig = px.histogram(
        df_all,
        x='production',
        color='source',
        nbins=50,
        barmode='overlay',
        opacity=0.7,
        title="Production Distribution Comparison"
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")
