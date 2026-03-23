"""
Brand Comparison Page
Compare automotive brands across metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_brand_summary, get_all_cars, get_filter_options
from utils.statistics import HypothesisTesting

st.set_page_config(page_title="Brand Comparison", page_icon="🏆", layout="wide")

st.title("🏆 Brand Comparison")
st.markdown("Compare automotive brands across performance and value metrics")

try:
    df_brands = get_brand_summary()
    df_cars = get_all_cars()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Comparison Options")

        selected_brands = st.multiselect(
            "Select Brands to Compare",
            options['brands'],
            default=df_brands.nlargest(10, 'model_count')['company'].tolist()
        )

        metric = st.selectbox(
            "Primary Metric",
            ['avg_price', 'avg_horsepower', 'avg_top_speed', 'avg_acceleration', 'model_count']
        )

    # Filter data
    df_filtered = df_brands[df_brands['company'].isin(selected_brands)]
    df_cars_filtered = df_cars[df_cars['company'].isin(selected_brands)]

    # Summary
    st.markdown("### Brand Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Brands Selected", len(selected_brands))
    with col2:
        st.metric("Total Models", df_filtered['model_count'].sum())
    with col3:
        st.metric("Avg Price Range", f"${df_filtered['avg_price'].min()/1000:.0f}K - ${df_filtered['avg_price'].max()/1000:.0f}K")
    with col4:
        st.metric("HP Range", f"{df_filtered['avg_horsepower'].min():.0f} - {df_filtered['avg_horsepower'].max():.0f}")

    st.markdown("---")

    # Bar charts
    st.markdown("### Brand Rankings")

    col1, col2 = st.columns(2)

    with col1:
        df_sorted = df_filtered.sort_values(metric, ascending=True)
        fig = px.bar(
            df_sorted,
            x=metric,
            y='company',
            orientation='h',
            color=metric,
            color_continuous_scale='Reds',
            title=f"Brands by {metric.replace('_', ' ').title()}"
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Radar chart for multi-metric comparison
        if len(selected_brands) <= 8:
            metrics = ['avg_horsepower', 'avg_top_speed', 'avg_acceleration', 'model_count']

            # Normalize metrics
            df_radar = df_filtered[['company'] + metrics].copy()
            for m in metrics:
                if m == 'avg_acceleration':  # Lower is better
                    df_radar[m] = 1 - (df_radar[m] - df_radar[m].min()) / (df_radar[m].max() - df_radar[m].min() + 0.001)
                else:
                    df_radar[m] = (df_radar[m] - df_radar[m].min()) / (df_radar[m].max() - df_radar[m].min() + 0.001)

            fig = go.Figure()

            for _, row in df_radar.iterrows():
                fig.add_trace(go.Scatterpolar(
                    r=[row[m] for m in metrics],
                    theta=[m.replace('avg_', '').replace('_', ' ').title() for m in metrics],
                    fill='toself',
                    name=row['company']
                ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title="Brand Performance Radar",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select 8 or fewer brands for radar chart")

    st.markdown("---")

    # Box plots for distribution comparison
    st.markdown("### Performance Distribution by Brand")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.box(
            df_cars_filtered,
            x='company',
            y='horsepower_hp',
            color='company',
            title="Horsepower Distribution by Brand"
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=45, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.box(
            df_cars_filtered,
            x='company',
            y='price_usd',
            color='company',
            title="Price Distribution by Brand"
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=45, height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Statistical comparison
    st.markdown("### Statistical Analysis")

    if len(selected_brands) >= 2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ANOVA: Horsepower Across Brands")
            anova_result = HypothesisTesting.anova_test(df_cars_filtered, 'horsepower_hp', 'company')

            st.markdown(f"""
            - F-statistic: `{anova_result['statistic']:.3f}`
            - P-value: `{anova_result['p_value']:.6f}`
            - Effect Size (η²): `{anova_result['eta_squared']:.3f}`

            **Result:** {'Significant differences exist between brands.' if anova_result['significant'] else 'No significant differences found.'}
            """)

        with col2:
            st.markdown("#### ANOVA: Price Across Brands")
            anova_result = HypothesisTesting.anova_test(df_cars_filtered, 'price_usd', 'company')

            st.markdown(f"""
            - F-statistic: `{anova_result['statistic']:.3f}`
            - P-value: `{anova_result['p_value']:.6f}`
            - Effect Size (η²): `{anova_result['eta_squared']:.3f}`

            **Result:** {'Significant differences exist between brands.' if anova_result['significant'] else 'No significant differences found.'}
            """)

    # Detailed comparison table
    st.markdown("### Detailed Brand Metrics")

    df_display = df_filtered.copy()
    df_display.columns = [
        'Brand', 'Models', 'Avg Price', 'Avg HP', 'Avg Speed', 'Avg 0-100',
        'Avg Torque', 'Min Price', 'Max Price', 'Perf Score'
    ]
    df_display = df_display.round(2)

    st.dataframe(df_display, use_container_width=True)

    st.download_button(
        label="📥 Download Comparison",
        data=df_display.to_csv(index=False),
        file_name="brand_comparison.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {str(e)}")
