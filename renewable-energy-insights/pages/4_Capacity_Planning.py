"""
Capacity Planning Page - Production reliability and optimization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_data, get_peak_analysis, get_filter_options
from utils.statistics import DescriptiveStatistics, TimeSeriesAnalysis

st.set_page_config(page_title="Capacity Planning", page_icon="📊", layout="wide")

st.title("📊 Capacity Planning & Reliability")
st.markdown("Analyzing production reliability, capacity factors, and optimization opportunities")

try:
    df = get_all_data()
    df_peaks = get_peak_analysis()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")
        selected_source = st.selectbox("Energy Source", ['All'] + options['sources'])

    if selected_source != 'All':
        df = df[df['source'] == selected_source]
        df_peaks = df_peaks[df_peaks['source'] == selected_source]

    # Capacity metrics
    st.markdown("### Capacity Metrics")

    # Calculate capacity factor (assuming peak as nameplate capacity)
    for source in df['source'].unique():
        source_data = df[df['source'] == source]
        peak_capacity = source_data['production'].max()
        avg_production = source_data['production'].mean()
        capacity_factor = (avg_production / peak_capacity) * 100 if peak_capacity > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"{source} Peak Capacity", f"{peak_capacity:,.0f} MWh")
        with col2:
            st.metric(f"{source} Avg Output", f"{avg_production:,.0f} MWh")
        with col3:
            st.metric(f"{source} Capacity Factor", f"{capacity_factor:.1f}%")
        with col4:
            reliability = (1 - source_data['production'].isna().mean()) * 100
            st.metric(f"{source} Data Coverage", f"{reliability:.1f}%")

    st.markdown("---")

    # Production distribution
    st.markdown("### Production Distribution Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Histogram with percentiles
        fig = px.histogram(
            df,
            x='production',
            color='source' if selected_source == 'All' else None,
            nbins=50,
            title="Production Distribution",
            marginal='box'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Percentile analysis
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        perc_values = np.percentile(df['production'].dropna(), percentiles)

        perc_df = pd.DataFrame({
            'Percentile': [f'P{p}' for p in percentiles],
            'Production (MWh)': perc_values
        })

        st.markdown("#### Production Percentiles")
        st.dataframe(perc_df.round(0), use_container_width=True)

        st.info(f"""
        **Key Insights:**
        - 50% of time, production is below {perc_values[2]:,.0f} MWh
        - 90% of time, production is below {perc_values[4]:,.0f} MWh
        - Top 5% production exceeds {perc_values[5]:,.0f} MWh
        """)

    st.markdown("---")

    # Peak production analysis
    st.markdown("### Peak Production Events")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top Peak Events")
        st.dataframe(
            df_peaks[['date', 'start_hour', 'source', 'production', 'season']].head(10),
            use_container_width=True
        )

    with col2:
        # Peak hours distribution
        peak_hours = df_peaks.groupby('start_hour').size().reset_index(name='count')

        fig = px.bar(
            peak_hours,
            x='start_hour',
            y='count',
            title="Peak Events by Hour",
            color='count',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Reliability analysis
    st.markdown("### Production Reliability")

    # Calculate hours above thresholds
    thresholds = [0.25, 0.50, 0.75, 0.90]
    peak = df['production'].max()

    reliability_data = []
    for thresh in thresholds:
        threshold_val = peak * thresh
        hours_above = (df['production'] >= threshold_val).sum()
        pct_above = hours_above / len(df) * 100
        reliability_data.append({
            'Threshold': f'{int(thresh*100)}% of Peak',
            'Production Level': f'{threshold_val:,.0f} MWh',
            'Hours Above': hours_above,
            'Percentage': f'{pct_above:.1f}%'
        })

    reliability_df = pd.DataFrame(reliability_data)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Time Above Production Thresholds")
        st.dataframe(reliability_df, use_container_width=True)

    with col2:
        fig = px.bar(
            reliability_df,
            x='Threshold',
            y='Hours Above',
            title="Hours Above Threshold",
            color='Hours Above',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Variability analysis
    st.markdown("### Production Variability")

    # Calculate rolling statistics
    df_sorted = df.sort_values('date').copy()

    if 'production' in df_sorted.columns:
        # Daily aggregation
        daily = df_sorted.groupby(['date', 'source'])['production'].agg(['mean', 'std', 'sum']).reset_index()
        daily['cv'] = daily['std'] / daily['mean'] * 100

        col1, col2 = st.columns(2)

        with col1:
            fig = px.line(
                daily,
                x='date',
                y='sum',
                color='source' if selected_source == 'All' else None,
                title="Daily Total Production"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(
                daily,
                x='date',
                y='cv',
                color='source' if selected_source == 'All' else None,
                title="Daily Coefficient of Variation"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Summary statistics
    st.markdown("### Statistical Summary")
    desc_stats = DescriptiveStatistics.summary(df, ['production'])
    st.dataframe(desc_stats, use_container_width=True)

    st.download_button(
        label="📥 Download Capacity Data",
        data=df.to_csv(index=False),
        file_name="capacity_analysis.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {str(e)}")
