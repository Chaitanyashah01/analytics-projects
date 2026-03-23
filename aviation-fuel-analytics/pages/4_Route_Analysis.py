"""
Route Profitability Analysis Page
Route-level fuel cost and revenue analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_route_profitability, get_filter_options
from utils.statistics import DescriptiveStatistics, RegressionAnalysis

st.set_page_config(page_title="Route Analysis", page_icon="🛫", layout="wide")

st.title("🛫 Route Profitability Analysis")
st.markdown("Analyze route-level fuel costs, rerouting impacts, and revenue metrics")

try:
    # Load data
    options = get_filter_options()

    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filters")

        selected_airlines = st.multiselect(
            "Airlines",
            options['airlines'],
            default=options['airlines'][:5] if len(options['airlines']) > 5 else options['airlines']
        )

        show_cancelled = st.checkbox("Include Cancelled Flights", value=False)
        show_rerouted = st.checkbox("Show Only Rerouted Flights", value=False)

    # Load filtered data
    df_routes = get_route_profitability(selected_airlines if selected_airlines else None)

    # Apply additional filters
    if not show_cancelled:
        df_routes = df_routes[df_routes['flight_cancelled'] == 'No']

    if show_rerouted:
        df_routes = df_routes[df_routes['rerouted'] == 'Yes']

    if df_routes.empty:
        st.warning("No data available with current filters")
        st.stop()

    # Summary metrics
    st.markdown("### Route Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        unique_routes = len(df_routes.groupby(['origin_city', 'destination_city']))
        st.metric("Unique Routes", unique_routes)

    with col2:
        avg_fuel_cost = df_routes['total_fuel_cost_usd'].mean()
        st.metric("Avg Fuel Cost", f"${avg_fuel_cost:,.0f}")

    with col3:
        rerouted_pct = (df_routes['rerouted'] == 'Yes').mean() * 100
        st.metric("Rerouted Flights", f"{rerouted_pct:.1f}%")

    with col4:
        total_revenue = df_routes['route_revenue_usd'].sum()
        st.metric("Total Route Revenue", f"${total_revenue/1e6:.1f}M")

    st.markdown("---")

    # Route distance analysis
    st.markdown("### Distance and Fuel Cost Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig_scatter = px.scatter(
            df_routes,
            x='original_distance_km',
            y='total_fuel_cost_usd',
            color='airline',
            title="Distance vs Fuel Cost",
            labels={
                'original_distance_km': 'Distance (km)',
                'total_fuel_cost_usd': 'Fuel Cost (USD)'
            },
            trendline='ols'
        )
        st.plotly_chart(fig_scatter, width="stretch")

    with col2:
        # Regression analysis
        reg_result = RegressionAnalysis.simple_linear_regression(
            df_routes['original_distance_km'],
            df_routes['total_fuel_cost_usd']
        )

        st.markdown(f"""
        #### Distance-Fuel Cost Relationship

        **Regression Results:**
        - Equation: `{reg_result['equation']}`
        - R-squared: `{reg_result['r_squared']:.4f}`
        - P-value: `{reg_result['p_value']:.6f}`

        **Interpretation:** For every additional 1,000 km of distance,
        fuel cost increases by approximately `${reg_result['slope'] * 1000:,.0f}`.
        """)

        # Additional metrics
        avg_cost_per_km = df_routes['total_fuel_cost_usd'].sum() / df_routes['original_distance_km'].sum()
        st.metric("Average Cost per km", f"${avg_cost_per_km:.2f}")

    st.markdown("---")

    # Rerouting impact
    st.markdown("### Rerouting Impact Analysis")

    # Calculate rerouting stats
    rerouted = df_routes[df_routes['rerouted'] == 'Yes'].copy()
    not_rerouted = df_routes[df_routes['rerouted'] == 'No'].copy()

    col1, col2 = st.columns(2)

    with col1:
        if len(rerouted) > 0:
            st.markdown("#### Rerouted Flight Statistics")

            avg_extra_distance = rerouted['extra_distance_km'].mean()
            avg_extra_cost = rerouted['extra_fuel_cost_usd'].mean()
            total_extra_cost = rerouted['extra_fuel_cost_usd'].sum()

            st.metric("Avg Extra Distance", f"{avg_extra_distance:.0f} km")
            st.metric("Avg Extra Fuel Cost", f"${avg_extra_cost:,.0f}")
            st.metric("Total Extra Cost", f"${total_extra_cost:,.0f}")

            # Distribution of extra costs
            fig_hist = px.histogram(
                rerouted,
                x='extra_fuel_cost_usd',
                nbins=30,
                title="Distribution of Extra Fuel Costs",
                labels={'extra_fuel_cost_usd': 'Extra Fuel Cost (USD)'}
            )
            st.plotly_chart(fig_hist, width="stretch")
        else:
            st.info("No rerouted flights in current selection")

    with col2:
        if len(rerouted) > 0 and len(not_rerouted) > 0:
            # Compare rerouted vs non-rerouted
            comparison_data = pd.DataFrame({
                'Category': ['Rerouted', 'Not Rerouted'],
                'Avg Fuel Cost': [
                    rerouted['total_fuel_cost_usd'].mean(),
                    not_rerouted['total_fuel_cost_usd'].mean()
                ],
                'Avg Revenue': [
                    rerouted['route_revenue_usd'].mean(),
                    not_rerouted['route_revenue_usd'].mean()
                ],
                'Count': [len(rerouted), len(not_rerouted)]
            })

            fig_compare = px.bar(
                comparison_data,
                x='Category',
                y='Avg Fuel Cost',
                title="Average Fuel Cost: Rerouted vs Normal",
                text='Avg Fuel Cost'
            )
            fig_compare.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            st.plotly_chart(fig_compare, width="stretch")

    st.markdown("---")

    # Route profitability by airline
    st.markdown("### Route Profitability by Airline")

    airline_stats = df_routes.groupby('airline').agg({
        'route_revenue_usd': 'sum',
        'total_fuel_cost_usd': 'sum',
        'estimated_passengers': 'sum',
        'original_distance_km': 'sum'
    }).reset_index()

    airline_stats['profit_margin'] = (
        (airline_stats['route_revenue_usd'] - airline_stats['total_fuel_cost_usd'])
        / airline_stats['route_revenue_usd'] * 100
    )
    airline_stats['revenue_per_passenger'] = (
        airline_stats['route_revenue_usd'] / airline_stats['estimated_passengers']
    )
    airline_stats = airline_stats.sort_values('route_revenue_usd', ascending=False)

    fig_airline = px.bar(
        airline_stats.head(15),
        x='airline',
        y='route_revenue_usd',
        color='profit_margin',
        color_continuous_scale='RdYlGn',
        title="Route Revenue by Airline (color = profit margin %)"
    )
    fig_airline.update_layout(height=400)
    st.plotly_chart(fig_airline, width="stretch")

    st.markdown("---")

    # Popular routes
    st.markdown("### Top Routes Analysis")

    route_stats = df_routes.groupby(['origin_city', 'destination_city', 'airline']).agg({
        'route_revenue_usd': 'sum',
        'total_fuel_cost_usd': 'sum',
        'estimated_passengers': 'sum',
        'original_distance_km': 'first'
    }).reset_index()

    route_stats['route'] = route_stats['origin_city'] + ' → ' + route_stats['destination_city']
    route_stats = route_stats.sort_values('route_revenue_usd', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        fig_top_routes = px.bar(
            route_stats.head(10),
            x='route_revenue_usd',
            y='route',
            orientation='h',
            color='airline',
            title="Top 10 Routes by Revenue"
        )
        fig_top_routes.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )
        st.plotly_chart(fig_top_routes, width="stretch")

    with col2:
        # Top routes by passengers
        route_stats_pass = route_stats.sort_values('estimated_passengers', ascending=False)

        fig_top_pass = px.bar(
            route_stats_pass.head(10),
            x='estimated_passengers',
            y='route',
            orientation='h',
            color='airline',
            title="Top 10 Routes by Passengers"
        )
        fig_top_pass.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )
        st.plotly_chart(fig_top_pass, width="stretch")

    st.markdown("---")

    # Aircraft analysis
    st.markdown("### Aircraft Type Analysis")

    aircraft_stats = df_routes.groupby('aircraft_type').agg({
        'fuel_consumption_bbl': 'mean',
        'total_fuel_cost_usd': 'mean',
        'estimated_passengers': 'mean',
        'original_distance_km': 'mean'
    }).reset_index()

    aircraft_stats['fuel_per_passenger'] = (
        aircraft_stats['total_fuel_cost_usd'] / aircraft_stats['estimated_passengers']
    )
    aircraft_stats['fuel_per_km'] = (
        aircraft_stats['total_fuel_cost_usd'] / aircraft_stats['original_distance_km']
    )

    fig_aircraft = px.scatter(
        aircraft_stats,
        x='estimated_passengers',
        y='fuel_per_passenger',
        size='total_fuel_cost_usd',
        color='aircraft_type',
        title="Aircraft Efficiency: Passengers vs Fuel Cost per Passenger",
        labels={
            'estimated_passengers': 'Avg Passengers',
            'fuel_per_passenger': 'Fuel Cost per Passenger ($)'
        }
    )
    st.plotly_chart(fig_aircraft, width="stretch")

    # Descriptive statistics
    st.markdown("### Descriptive Statistics")

    desc_cols = ['original_distance_km', 'total_fuel_cost_usd', 'route_revenue_usd',
                 'estimated_passengers', 'fuel_pct_of_cost']
    desc_stats = DescriptiveStatistics.summary(df_routes, desc_cols)
    st.dataframe(desc_stats, width="stretch")

    # Export
    st.markdown("---")
    st.download_button(
        label="📥 Download Route Data",
        data=df_routes.to_csv(index=False),
        file_name="route_analysis.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please ensure the database is initialized by visiting the main page first.")
