"""
Renewable Energy Production Insights Dashboard
Main application.
"""

import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import create_database
from database.queries import get_kpi_metrics, get_source_summary, get_daily_production

st.set_page_config(
    page_title="Renewable Energy Insights",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #27ae60;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_database():
    """Initialize database if needed."""
    db_path = Path(__file__).parent / "data" / "energy.db"
    data_dir = Path(__file__).parent / "data"

    if not db_path.exists():
        with st.spinner("Initializing database..."):
            report = create_database(str(db_path), str(data_dir))
            st.success(f"Database initialized with {report['tables'].get('energy_production', 0):,} records!")
    return True


def format_production(value):
    """Format production value."""
    if value >= 1e9:
        return f"{value/1e9:.2f}B MWh"
    elif value >= 1e6:
        return f"{value/1e6:.2f}M MWh"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K MWh"
    return f"{value:.0f} MWh"


def main():
    initialize_database()

    st.markdown('<p class="main-header">🌱 Renewable Energy Production Insights</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Analyzing wind and solar energy production patterns, '
        'seasonal variations, and optimization opportunities</p>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("### Navigation")
        st.markdown("""
        Explore renewable energy production:

        - **Overview** - Production summary
        - **Source Comparison** - Wind vs Solar
        - **Temporal Patterns** - Hourly & daily trends
        - **Seasonal Analysis** - Seasonal variations
        - **Capacity Planning** - Optimization insights
        """)

    try:
        kpis = get_kpi_metrics()
        df_sources = get_source_summary()

        st.markdown("## Production Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Production", format_production(kpis['total_production']))
        with col2:
            st.metric("Avg Hourly Production", f"{kpis['avg_production']:,.0f} MWh")
        with col3:
            st.metric("Peak Production", f"{kpis['peak_production']:,.0f} MWh")
        with col4:
            st.metric("Days of Data", f"{int(kpis['total_days']):,}")

        st.markdown("---")

        # Source comparison
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Production by Source")
            fig = px.pie(
                df_sources,
                values='total_production',
                names='source',
                color_discrete_sequence=['#3498db', '#f1c40f']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Average vs Peak Production")
            fig = px.bar(
                df_sources,
                x='source',
                y=['avg_production', 'peak_production'],
                barmode='group',
                color_discrete_sequence=['#27ae60', '#e74c3c']
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Daily trend
        st.markdown("### Daily Production Trend")
        df_daily = get_daily_production()

        fig = px.line(
            df_daily,
            x='date',
            y='total_production',
            color='source',
            title='',
            labels={'total_production': 'Production (MWh)', 'date': 'Date'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Insights
        st.markdown("### Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="insight-box">
            <strong>🌬️ Wind Energy</strong><br>
            Analyze wind production patterns including peak hours,
            seasonal variations, and capacity factor calculations.
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="insight-box">
            <strong>☀️ Solar Energy</strong><br>
            Explore solar production curves, optimal generation hours,
            and weather-dependent variability analysis.
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please ensure data files are present.")

    st.markdown("---")
    st.markdown("<center><small>Renewable Energy Insights Dashboard</small></center>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
