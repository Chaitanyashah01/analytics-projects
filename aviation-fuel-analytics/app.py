"""
Aviation Fuel Analytics Dashboard
Main application entry point.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import create_database, get_connection
from database.queries import get_kpi_metrics, get_table_stats, get_filter_options
from utils.data_loader import format_large_number

# Page configuration
st.set_page_config(
    page_title="Aviation Fuel Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_database():
    """Initialize database if not exists."""
    db_path = Path(__file__).parent / "data" / "aviation.db"
    data_dir = Path(__file__).parent / "data"

    if not db_path.exists():
        with st.spinner("Initializing database... This may take a moment."):
            report = create_database(str(db_path), str(data_dir))
            st.success(f"Database initialized with {report['total_rows']:,} records!")
    return True


def main():
    """Main application."""

    # Initialize database
    initialize_database()

    # Header
    st.markdown('<p class="main-header">✈️ Aviation Fuel Analytics</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Comprehensive analysis of airline operations, fuel costs, '
        'and geopolitical impacts on aviation economics (2019-2026)</p>',
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Aviation+Analytics", width=200)
        st.markdown("---")
        st.markdown("### Navigation")
        st.markdown("""
        Use the sidebar to navigate between different analysis views:

        - **Overview** - Executive KPIs and summary
        - **Oil Price Impact** - Correlation analysis
        - **Conflict Timeline** - Geopolitical events
        - **Airline Comparison** - Performance benchmarks
        - **Route Analysis** - Route-level metrics
        - **Statistical Analysis** - Deep dive analytics
        """)

        st.markdown("---")
        st.markdown("### Data Overview")
        try:
            stats = get_table_stats()
            for table, count in stats.items():
                st.metric(table.replace('_', ' ').title(), f"{count:,} rows")
        except Exception:
            st.info("Navigate to a page to load data")

    # Main content - Overview page
    st.markdown("## Executive Dashboard")

    try:
        # KPI metrics
        kpis = get_kpi_metrics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Revenue",
                f"${format_large_number(kpis['total_revenue'])}",
                help="Total revenue across all airlines and periods"
            )

        with col2:
            st.metric(
                "Avg Profit Margin",
                f"{kpis['avg_profit_margin']:.1f}%",
                help="Average profit margin across all airlines"
            )

        with col3:
            st.metric(
                "Total Fuel Cost",
                f"${format_large_number(kpis['total_fuel_cost'])}",
                help="Total fuel expenditure"
            )

        with col4:
            st.metric(
                "Total Passengers",
                f"{format_large_number(kpis['total_passengers'])}M",
                help="Total passengers carried (millions)"
            )

        st.markdown("---")

        # Second row of metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Airlines Analyzed",
                f"{int(kpis['airline_count'])}",
                help="Number of unique airlines in dataset"
            )

        with col2:
            st.metric(
                "Regions Covered",
                f"{int(kpis['region_count'])}",
                help="Number of geographic regions"
            )

        with col3:
            st.metric(
                "Avg Fuel Cost %",
                f"{kpis['avg_fuel_pct']:.1f}%",
                help="Average fuel cost as percentage of revenue"
            )

        st.markdown("---")

        # Key insights
        st.markdown("### Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="insight-box">
            <strong>📊 Data Coverage</strong><br>
            This dashboard analyzes aviation industry data spanning from 2019 to 2026,
            covering multiple conflict phases including pre-pandemic baseline, pandemic recovery,
            and various geopolitical events affecting oil prices and airline operations.
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="insight-box">
            <strong>🔍 Analysis Capabilities</strong><br>
            Explore correlations between oil prices and airline profitability,
            assess the impact of geopolitical events on airfares, compare airline
            performance across regions, and analyze route-level fuel economics.
            </div>
            """, unsafe_allow_html=True)

        # Quick navigation
        st.markdown("### Explore Analysis")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            #### 📈 Oil Price Impact
            Analyze correlations between crude oil prices, jet fuel costs,
            and airline financial performance.
            """)

        with col2:
            st.markdown("""
            #### ⚠️ Conflict Events
            Interactive timeline of geopolitical events and their
            measured impact on oil prices and airfares.
            """)

        with col3:
            st.markdown("""
            #### 🏢 Airline Comparison
            Benchmark airlines across revenue, profitability,
            fuel efficiency, and hedging strategies.
            """)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure the database is properly initialized.")

    # Footer
    st.markdown("---")
    st.markdown(
        "<center><small>Aviation Fuel Analytics Dashboard | "
        "Data-driven insights for aviation industry analysis</small></center>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
