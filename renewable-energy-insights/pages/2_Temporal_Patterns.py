"""
Temporal Patterns Page - Hourly, daily, and weekly analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_data, get_hourly_pattern, get_day_of_week_summary, get_filter_options

st.set_page_config(page_title="Temporal Patterns", page_icon="🕐", layout="wide")

st.title("🕐 Temporal Production Patterns")
st.markdown("Analyzing energy production patterns across different time scales")

try:
    df = get_all_data()
    df_hourly = get_hourly_pattern()
    df_dow = get_day_of_week_summary()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")
        selected_source = st.selectbox("Energy Source", ['All'] + options['sources'])

    # Filter data
    if selected_source != 'All':
        df = df[df['source'] == selected_source]
        df_hourly = df_hourly[df_hourly['source'] == selected_source]
        df_dow = df_dow[df_dow['source'] == selected_source]

    # Hourly patterns
    st.markdown("### Hourly Production Profile")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            df_hourly,
            x='start_hour',
            y='avg_production',
            color='source' if selected_source == 'All' else None,
            title="Average Hourly Production",
            markers=True
        )
        fig.update_layout(xaxis_title="Hour", yaxis_title="Avg Production (MWh)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Peak hours
        if selected_source != 'All':
            peak_hours = df_hourly.nlargest(5, 'avg_production')
        else:
            peak_hours = df_hourly.groupby('start_hour')['avg_production'].sum().reset_index().nlargest(5, 'avg_production')

        fig = px.bar(
            peak_hours,
            x='start_hour',
            y='avg_production',
            title="Top 5 Peak Production Hours",
            color='avg_production',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Heatmap: Hour vs Day of Week
    st.markdown("### Hour vs Day of Week Heatmap")

    # Create pivot for heatmap
    heatmap_data = df.groupby(['day_name', 'start_hour'])['production'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='day_name', columns='start_hour', values='production')

    # Order days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex([d for d in day_order if d in heatmap_pivot.index])

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='YlGn',
        colorbar=dict(title="Avg MWh")
    ))
    fig.update_layout(
        title="Production Intensity: Hour vs Day of Week",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Day of week analysis
    st.markdown("### Day of Week Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Reorder days
        df_dow_ordered = df_dow.copy()
        df_dow_ordered['day_order'] = df_dow_ordered['day_name'].map({
            d: i for i, d in enumerate(day_order)
        })
        df_dow_ordered = df_dow_ordered.sort_values('day_order')

        fig = px.bar(
            df_dow_ordered,
            x='day_name',
            y='avg_production',
            color='source' if selected_source == 'All' else None,
            title="Average Production by Day of Week"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Weekend vs Weekday
        df['is_weekend'] = df['day_name'].isin(['Saturday', 'Sunday'])
        weekend_comp = df.groupby('is_weekend')['production'].agg(['mean', 'sum']).reset_index()
        weekend_comp['Day Type'] = weekend_comp['is_weekend'].map({True: 'Weekend', False: 'Weekday'})

        fig = px.bar(
            weekend_comp,
            x='Day Type',
            y='mean',
            title="Weekday vs Weekend Avg Production",
            color='Day Type'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Time of day analysis
    st.markdown("### Time of Day Analysis")

    tod_data = df.groupby(['time_of_day', 'source'])['production'].mean().reset_index()

    fig = px.bar(
        tod_data,
        x='time_of_day',
        y='production',
        color='source' if selected_source == 'All' else None,
        barmode='group',
        title="Average Production by Time of Day",
        category_orders={'time_of_day': ['Morning', 'Afternoon', 'Evening', 'Night']}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Production variability by hour
    st.markdown("### Hourly Production Variability")

    hourly_var = df.groupby('start_hour')['production'].agg(['mean', 'std']).reset_index()
    hourly_var['cv'] = hourly_var['std'] / hourly_var['mean'] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hourly_var['start_hour'],
        y=hourly_var['mean'],
        name='Mean Production',
        error_y=dict(type='data', array=hourly_var['std'], visible=True)
    ))
    fig.update_layout(
        title="Hourly Mean Production with Standard Deviation",
        xaxis_title="Hour",
        yaxis_title="Production (MWh)"
    )
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {str(e)}")
