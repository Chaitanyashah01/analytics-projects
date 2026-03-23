"""
E-Commerce Customer 360 Dashboard
Main application.
"""

import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import create_database
from database.queries import get_kpi_metrics, get_segment_summary, get_country_summary

st.set_page_config(
    page_title="E-Commerce Customer 360",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #9b59b6;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #f5eeff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #9b59b6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_database():
    db_path = Path(__file__).parent / "data" / "ecommerce.db"
    data_dir = Path(__file__).parent / "data"

    if not db_path.exists():
        with st.spinner("Initializing database (this may take a moment for large dataset)..."):
            report = create_database(str(db_path), str(data_dir))
            st.success(f"Database initialized with {report['tables'].get('customers', 0):,} customers!")
    return True


def format_currency(value):
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.1f}K"
    return f"${value:.0f}"


def main():
    initialize_database()

    st.markdown('<p class="main-header">🛒 E-Commerce Customer 360</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Comprehensive customer analytics, segmentation, and behavioral insights</p>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("### Navigation")
        st.markdown("""
        Explore customer analytics:

        - **Overview** - Customer KPIs
        - **Demographics** - Customer profiles
        - **Purchase Behavior** - Spending patterns
        - **Segmentation** - Customer segments
        - **Engagement** - App & platform usage
        - **Statistical Analysis** - Deep dive
        """)

    try:
        kpis = get_kpi_metrics()
        df_segments = get_segment_summary()

        st.markdown("## Customer Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Customers", f"{int(kpis['total_customers']):,}")
        with col2:
            st.metric("Countries", int(kpis['countries']))
        with col3:
            st.metric("Avg Monthly Spend", f"${kpis['avg_monthly_spend']:,.0f}")
        with col4:
            st.metric("Avg Order Value", f"${kpis['avg_order_value']:,.0f}")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Monthly Revenue", format_currency(kpis['total_monthly_spend']))
        with col2:
            st.metric("Avg Weekly Purchases", f"{kpis['avg_weekly_purchases']:.1f}")
        with col3:
            st.metric("Cart Abandonment", f"{kpis['avg_abandonment_rate']:.1f}%")
        with col4:
            st.metric("Loyalty Members", f"{kpis['loyalty_pct']:.1f}%")

        st.markdown("---")

        # Segment overview
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Customer Segments")
            fig = px.pie(
                df_segments,
                values='customer_count',
                names='loyalty_segment',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Spend by Segment")
            fig = px.bar(
                df_segments,
                x='loyalty_segment',
                y='avg_spend',
                color='avg_aov',
                color_continuous_scale='Purples',
                title=""
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Geographic distribution
        st.markdown("### Geographic Distribution")
        df_countries = get_country_summary()

        fig = px.bar(
            df_countries.head(15),
            x='country',
            y='customer_count',
            color='avg_spend',
            color_continuous_scale='Purples',
            title=""
        )
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Insights
        st.markdown("### Key Insights")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="insight-box">
            <strong>👥 Customer Segmentation</strong><br>
            Analyze customer segments based on purchase behavior, lifetime value,
            and engagement metrics. Identify high-value customers and growth opportunities.
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="insight-box">
            <strong>📊 Behavioral Analytics</strong><br>
            Deep dive into shopping patterns, cart abandonment, conversion funnels,
            and lifestyle correlations for targeted marketing strategies.
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please ensure data files are present.")

    st.markdown("---")
    st.markdown("<center><small>E-Commerce Customer 360 Dashboard</small></center>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
