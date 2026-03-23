"""
Seasonal Analysis Page - Seasonal and monthly patterns.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_data, get_seasonal_summary, get_monthly_summary, get_filter_options
from utils.statistics import HypothesisTesting

st.set_page_config(page_title="Seasonal Analysis", page_icon="🍂", layout="wide")

st.title("🍂 Seasonal Production Analysis")
st.markdown("Analyzing energy production patterns across seasons and months")

try:
    df = get_all_data()
    df_seasonal = get_seasonal_summary()
    df_monthly = get_monthly_summary()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")
        selected_source = st.selectbox("Energy Source", ['All'] + options['sources'])

    if selected_source != 'All':
        df = df[df['source'] == selected_source]
        df_seasonal = df_seasonal[df_seasonal['source'] == selected_source]
        df_monthly = df_monthly[df_monthly['source'] == selected_source]

    # Seasonal overview
    st.markdown("### Seasonal Production Overview")

    season_order = ['Spring', 'Summer', 'Fall', 'Winter']

    col1, col2 = st.columns(2)

    with col1:
        df_seasonal_sorted = df_seasonal.copy()
        df_seasonal_sorted['season_order'] = df_seasonal_sorted['season'].map({s: i for i, s in enumerate(season_order)})
        df_seasonal_sorted = df_seasonal_sorted.sort_values('season_order')

        fig = px.bar(
            df_seasonal_sorted,
            x='season',
            y='total_production',
            color='source' if selected_source == 'All' else None,
            barmode='group',
            title="Total Production by Season",
            category_orders={'season': season_order}
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            df_seasonal_sorted,
            x='season',
            y='avg_production',
            color='source' if selected_source == 'All' else None,
            barmode='group',
            title="Average Production by Season",
            category_orders={'season': season_order}
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Monthly trends
    st.markdown("### Monthly Production Trends")

    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    df_monthly_sorted = df_monthly.sort_values('month')

    fig = px.line(
        df_monthly_sorted,
        x='month_name',
        y='total_production',
        color='source' if selected_source == 'All' else None,
        title="Monthly Production Trend",
        markers=True,
        category_orders={'month_name': month_order}
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Total Production (MWh)")
    st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        # Best and worst months
        if selected_source != 'All':
            monthly_agg = df_monthly_sorted
        else:
            monthly_agg = df_monthly_sorted.groupby('month_name').agg({
                'total_production': 'sum',
                'avg_production': 'mean'
            }).reset_index()

        best_month = monthly_agg.nlargest(1, 'total_production')['month_name'].iloc[0]
        worst_month = monthly_agg.nsmallest(1, 'total_production')['month_name'].iloc[0]

        st.markdown(f"""
        #### Production Highlights
        - **Best Month:** {best_month}
        - **Lowest Month:** {worst_month}
        """)

        # Seasonal statistics table
        st.markdown("#### Seasonal Statistics")
        seasonal_stats = df_seasonal_sorted[['season', 'total_production', 'avg_production', 'readings']]
        seasonal_stats.columns = ['Season', 'Total (MWh)', 'Avg (MWh)', 'Readings']
        st.dataframe(seasonal_stats.round(0), width="stretch")

    with col2:
        # Seasonal pie chart
        if selected_source != 'All':
            pie_data = df_seasonal_sorted
        else:
            pie_data = df_seasonal_sorted.groupby('season')['total_production'].sum().reset_index()

        fig = px.pie(
            pie_data,
            values='total_production',
            names='season',
            title="Production Share by Season"
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Statistical analysis
    st.markdown("### Statistical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ANOVA: Production Across Seasons")

        anova_result = HypothesisTesting.anova_test(df, 'production', 'season')

        st.markdown(f"""
        - F-statistic: `{anova_result['statistic']:.3f}`
        - P-value: `{anova_result['p_value']:.6f}`
        - Effect Size (η²): `{anova_result['eta_squared']:.4f}`

        **Result:** {'Significant seasonal differences exist' if anova_result['significant'] else 'No significant seasonal differences'}
        """)

    with col2:
        st.markdown("#### Season Distribution")

        fig = px.box(
            df,
            x='season',
            y='production',
            color='season',
            title="Production Distribution by Season",
            category_orders={'season': season_order}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width="stretch")

    # Monthly box plots
    st.markdown("### Monthly Production Distribution")

    fig = px.box(
        df,
        x='month_name',
        y='production',
        color='source' if selected_source == 'All' else None,
        title="Production Variability by Month",
        category_orders={'month_name': month_order}
    )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, width="stretch")

    # Download
    st.download_button(
        label="📥 Download Seasonal Data",
        data=df_seasonal.to_csv(index=False),
        file_name="seasonal_analysis.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {str(e)}")
