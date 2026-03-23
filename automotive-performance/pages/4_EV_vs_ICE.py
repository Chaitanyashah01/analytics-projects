"""
EV vs ICE Comparison Page
Compare electric and traditional powertrains.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_cars, get_fuel_type_summary
from utils.statistics import HypothesisTesting, DescriptiveStatistics

st.set_page_config(page_title="EV vs ICE", page_icon="⚡", layout="wide")

st.title("⚡ Electric vs Internal Combustion")
st.markdown("Comparing electric vehicles with traditional powertrains")

try:
    df = get_all_cars()
    df_fuel = get_fuel_type_summary()

    # Create powertrain category
    def categorize_powertrain(fuel):
        if pd.isna(fuel):
            return 'Unknown'
        fuel = fuel.lower()
        if 'electric' in fuel:
            return 'Electric'
        elif 'hybrid' in fuel or 'plug' in fuel:
            return 'Hybrid'
        else:
            return 'ICE'

    df['powertrain'] = df['fuel_type_clean'].apply(categorize_powertrain)

    # Summary metrics
    st.markdown("### Powertrain Overview")

    ev_count = len(df[df['powertrain'] == 'Electric'])
    hybrid_count = len(df[df['powertrain'] == 'Hybrid'])
    ice_count = len(df[df['powertrain'] == 'ICE'])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Electric Vehicles", ev_count)
    with col2:
        st.metric("Hybrid Vehicles", hybrid_count)
    with col3:
        st.metric("ICE Vehicles", ice_count)
    with col4:
        ev_pct = ev_count / len(df) * 100
        st.metric("EV Market Share", f"{ev_pct:.1f}%")

    st.markdown("---")

    # Comparison by powertrain
    st.markdown("### Performance Comparison")

    powertrain_stats = df.groupby('powertrain').agg({
        'price_usd': 'mean',
        'horsepower_hp': 'mean',
        'top_speed_kmh': 'mean',
        'acceleration_sec': 'mean',
        'torque_nm': 'mean',
        'car_name': 'count'
    }).reset_index()
    powertrain_stats.columns = ['Powertrain', 'Avg Price', 'Avg HP', 'Avg Speed', 'Avg 0-100', 'Avg Torque', 'Count']

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            powertrain_stats,
            x='Powertrain',
            y=['Avg HP', 'Avg Speed'],
            barmode='group',
            title="Power & Speed by Powertrain"
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            powertrain_stats,
            x='Powertrain',
            y='Avg 0-100',
            title="Acceleration Time by Powertrain",
            color='Powertrain'
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Box plots
    st.markdown("### Distribution Comparison")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(
            df,
            x='powertrain',
            y='horsepower_hp',
            color='powertrain',
            title="Horsepower Distribution"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.box(
            df,
            x='powertrain',
            y='price_usd',
            color='powertrain',
            title="Price Distribution"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(
            df,
            x='powertrain',
            y='acceleration_sec',
            color='powertrain',
            title="Acceleration Distribution"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.box(
            df,
            x='powertrain',
            y='torque_nm',
            color='powertrain',
            title="Torque Distribution"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Statistical testing
    st.markdown("### Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ANOVA: Performance Metrics by Powertrain")

        # Horsepower ANOVA
        anova_hp = HypothesisTesting.anova_test(df, 'horsepower_hp', 'powertrain')
        st.markdown(f"""
        **Horsepower:**
        - F = {anova_hp['statistic']:.2f}, p = {anova_hp['p_value']:.4f}
        - {'Significant difference' if anova_hp['significant'] else 'No significant difference'}
        """)

        # Price ANOVA
        anova_price = HypothesisTesting.anova_test(df, 'price_usd', 'powertrain')
        st.markdown(f"""
        **Price:**
        - F = {anova_price['statistic']:.2f}, p = {anova_price['p_value']:.4f}
        - {'Significant difference' if anova_price['significant'] else 'No significant difference'}
        """)

        # Acceleration ANOVA
        anova_accel = HypothesisTesting.anova_test(df, 'acceleration_sec', 'powertrain')
        st.markdown(f"""
        **Acceleration:**
        - F = {anova_accel['statistic']:.2f}, p = {anova_accel['p_value']:.4f}
        - {'Significant difference' if anova_accel['significant'] else 'No significant difference'}
        """)

    with col2:
        st.markdown("#### EV vs ICE Direct Comparison")

        ev_data = df[df['powertrain'] == 'Electric']
        ice_data = df[df['powertrain'] == 'ICE']

        if len(ev_data) > 1 and len(ice_data) > 1:
            t_test_hp = HypothesisTesting.t_test_independent(
                ev_data['horsepower_hp'],
                ice_data['horsepower_hp']
            )

            st.markdown(f"""
            **Horsepower T-Test:**
            - EV Mean: {t_test_hp['group1_mean']:.0f} HP
            - ICE Mean: {t_test_hp['group2_mean']:.0f} HP
            - Difference: {t_test_hp['mean_difference']:.0f} HP
            - p-value: {t_test_hp['p_value']:.4f}
            - Cohen's d: {t_test_hp['effect_size']:.2f}
            """)

            t_test_accel = HypothesisTesting.t_test_independent(
                ev_data['acceleration_sec'],
                ice_data['acceleration_sec']
            )

            st.markdown(f"""
            **Acceleration T-Test:**
            - EV Mean: {t_test_accel['group1_mean']:.1f} sec
            - ICE Mean: {t_test_accel['group2_mean']:.1f} sec
            - Difference: {t_test_accel['mean_difference']:.1f} sec
            - p-value: {t_test_accel['p_value']:.4f}
            """)

    st.markdown("---")

    # Brand distribution
    st.markdown("### Brand Distribution by Powertrain")

    brand_powertrain = df.groupby(['company', 'powertrain']).size().reset_index(name='count')
    brand_powertrain = brand_powertrain[brand_powertrain['count'] > 0]

    fig = px.sunburst(
        brand_powertrain,
        path=['powertrain', 'company'],
        values='count',
        title="Brand Distribution by Powertrain"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

    # Summary table
    st.markdown("### Summary Statistics")
    st.dataframe(powertrain_stats.round(2), width="stretch")

except Exception as e:
    st.error(f"Error: {str(e)}")
