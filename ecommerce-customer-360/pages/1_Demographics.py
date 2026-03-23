"""
Demographics Analysis Page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.queries import get_all_customers, get_filter_options, get_demographic_summary

st.set_page_config(page_title="Demographics", page_icon="👥", layout="wide")

st.title("👥 Customer Demographics")
st.markdown("Analyzing customer profiles and demographic distributions")

try:
    df = get_all_customers()
    options = get_filter_options()

    with st.sidebar:
        st.markdown("### Filters")
        selected_countries = st.multiselect(
            "Countries",
            options['countries'],
            default=[]
        )

    if selected_countries:
        df = df[df['country'].isin(selected_countries)]

    # Summary
    st.markdown("### Demographic Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Customers", f"{len(df):,}")
    with col2:
        avg_age = df['age'].mean()
        st.metric("Average Age", f"{avg_age:.0f} years")
    with col3:
        male_pct = (df['gender'] == 'Male').mean() * 100
        st.metric("Male %", f"{male_pct:.1f}%")
    with col4:
        urban_pct = (df['urban_rural'] == 'Urban').mean() * 100
        st.metric("Urban %", f"{urban_pct:.1f}%")

    st.markdown("---")

    # Age and Gender distribution
    st.markdown("### Age & Gender Distribution")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='age',
            color='gender',
            nbins=30,
            title="Age Distribution by Gender",
            barmode='overlay',
            opacity=0.7
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        gender_counts = df['gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']

        fig = px.pie(
            gender_counts,
            values='Count',
            names='Gender',
            title="Gender Distribution"
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Age group analysis
    st.markdown("### Age Group Analysis")

    col1, col2 = st.columns(2)

    with col1:
        age_group_stats = df.groupby('age_group').agg({
            'user_id': 'count',
            'monthly_spend': 'mean',
            'income_level': 'mean'
        }).reset_index()
        age_group_stats.columns = ['Age Group', 'Customers', 'Avg Spend', 'Avg Income']

        fig = px.bar(
            age_group_stats,
            x='Age Group',
            y='Customers',
            color='Avg Spend',
            color_continuous_scale='Purples',
            title="Customers by Age Group"
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.box(
            df,
            x='age_group',
            y='monthly_spend',
            color='gender',
            title="Monthly Spend by Age Group and Gender"
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Income distribution
    st.markdown("### Income Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df,
            x='income_level',
            nbins=40,
            title="Income Distribution",
            color='income_segment'
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        income_seg = df['income_segment'].value_counts().reset_index()
        income_seg.columns = ['Segment', 'Count']

        fig = px.pie(
            income_seg,
            values='Count',
            names='Segment',
            title="Income Segments"
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Employment and Education
    st.markdown("### Employment & Education")

    col1, col2 = st.columns(2)

    with col1:
        emp_stats = df.groupby('employment_status')['monthly_spend'].mean().reset_index()
        emp_stats = emp_stats.sort_values('monthly_spend', ascending=True)

        fig = px.bar(
            emp_stats,
            x='monthly_spend',
            y='employment_status',
            orientation='h',
            title="Avg Spend by Employment Status",
            color='monthly_spend',
            color_continuous_scale='Purples'
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        edu_stats = df.groupby('education_level')['monthly_spend'].mean().reset_index()
        edu_stats = edu_stats.sort_values('monthly_spend', ascending=True)

        fig = px.bar(
            edu_stats,
            x='monthly_spend',
            y='education_level',
            orientation='h',
            title="Avg Spend by Education Level",
            color='monthly_spend',
            color_continuous_scale='Purples'
        )
        st.plotly_chart(fig, width="stretch")

    # Geographic distribution
    st.markdown("### Geographic Distribution")

    country_stats = df.groupby('country').agg({
        'user_id': 'count',
        'monthly_spend': 'mean'
    }).reset_index()
    country_stats.columns = ['Country', 'Customers', 'Avg Spend']
    country_stats = country_stats.sort_values('Customers', ascending=False)

    fig = px.bar(
        country_stats.head(20),
        x='Country',
        y='Customers',
        color='Avg Spend',
        color_continuous_scale='Purples',
        title="Top 20 Countries by Customer Count"
    )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, width="stretch")

    st.download_button(
        label="📥 Download Demographics",
        data=df.to_csv(index=False),
        file_name="customer_demographics.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error: {str(e)}")
