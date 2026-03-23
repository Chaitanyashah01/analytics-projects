"""
Automotive Performance Analytics Dashboard
Main application entry point.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import create_database
from database.queries import get_kpi_metrics, get_brand_summary, get_fuel_type_summary

st.set_page_config(
    page_title="Automotive Performance Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #e74c3c;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 1rem;
        border-radius: 10px;
    }
    .insight-box {
        background-color: #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #fdcb6e;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_database():
    """Initialize database if not exists."""
    db_path = Path(__file__).parent / "data" / "automotive.db"
    data_dir = Path(__file__).parent / "data"

    if not db_path.exists():
        with st.spinner("Initializing database and cleaning data..."):
            report = create_database(str(db_path), str(data_dir))
            st.success(f"Database initialized with {report['tables'].get('cars', 0):,} vehicles!")
    return True


def format_price(price):
    """Format price for display."""
    if price >= 1e6:
        return f"${price/1e6:.2f}M"
    elif price >= 1e3:
        return f"${price/1e3:.0f}K"
    return f"${price:.0f}"


def main():
    """Main application."""
    initialize_database()

    st.markdown('<p class="main-header">🚗 Automotive Performance Analytics</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Comprehensive analysis of vehicle specifications, performance metrics, '
        'and market positioning across leading automotive brands</p>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("### Navigation")
        st.markdown("""
        Explore different aspects of automotive performance:

        - **Overview** - Market summary and KPIs
        - **Performance Analysis** - Speed, power, acceleration
        - **Brand Comparison** - Cross-brand benchmarking
        - **Price Analysis** - Value and segmentation
        - **EV vs ICE** - Powertrain comparison
        - **Statistical Analysis** - Deep analytics
        """)

    try:
        kpis = get_kpi_metrics()

        st.markdown("## Market Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Models", f"{int(kpis['total_models']):,}")

        with col2:
            st.metric("Brands Analyzed", f"{int(kpis['total_brands'])}")

        with col3:
            st.metric("Avg Price", format_price(kpis['avg_price']))

        with col4:
            st.metric("Avg Horsepower", f"{kpis['avg_horsepower']:.0f} HP")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Avg Top Speed", f"{kpis['avg_top_speed']:.0f} km/h")

        with col2:
            st.metric("Avg 0-100 km/h", f"{kpis['avg_acceleration']:.1f} sec")

        with col3:
            st.metric("Fastest 0-100", f"{kpis['fastest_acceleration']:.1f} sec")

        with col4:
            st.metric("Highest Speed", f"{kpis['highest_speed']:.0f} km/h")

        st.markdown("---")

        # Brand and Fuel Type summary
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top Brands by Average Price")
            df_brands = get_brand_summary().head(10)

            import plotly.express as px
            fig = px.bar(
                df_brands,
                x='company',
                y='avg_price',
                color='avg_horsepower',
                color_continuous_scale='Reds',
                title='',
                labels={'avg_price': 'Avg Price ($)', 'company': 'Brand', 'avg_horsepower': 'Avg HP'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Models by Fuel Type")
            df_fuel = get_fuel_type_summary()

            fig = px.pie(
                df_fuel,
                values='model_count',
                names='fuel_type',
                title='',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Key Insights
        st.markdown("### Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="insight-box">
            <strong>📊 Performance Metrics</strong><br>
            This analysis covers comprehensive vehicle specifications including horsepower,
            top speed, acceleration times, and torque across multiple brands and fuel types.
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="insight-box">
            <strong>💰 Value Analysis</strong><br>
            Explore price-to-performance ratios, identify the best value vehicles,
            and compare cost efficiency across segments from budget to ultra-luxury.
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the database is properly initialized.")

    st.markdown("---")
    st.markdown(
        "<center><small>Automotive Performance Analytics | "
        "Data-driven insights for the automotive industry</small></center>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
