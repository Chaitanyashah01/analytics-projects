"""
SQL query functions for E-Commerce Customer 360.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st


def get_db_path() -> str:
    """Get the database path - use temp dir for Streamlit Cloud."""
    import tempfile
    import os
    if os.path.exists('/mount/src'):
        return str(Path(tempfile.gettempdir()) / "ecommerce.db")
    return str(Path(__file__).parent.parent / "data" / "ecommerce.db")


@st.cache_data(ttl=3600)
def get_kpi_metrics() -> Dict[str, Any]:
    """Get KPI metrics."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            COUNT(*) as total_customers,
            COUNT(DISTINCT country) as countries,
            AVG(monthly_spend) as avg_monthly_spend,
            SUM(monthly_spend) as total_monthly_spend,
            AVG(weekly_purchases) as avg_weekly_purchases,
            AVG(cart_abandonment_rate) as avg_abandonment_rate,
            AVG(average_order_value) as avg_order_value,
            AVG(customer_value_score) as avg_customer_value,
            SUM(CASE WHEN loyalty_program_member = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as loyalty_pct
        FROM customers
        """
        df = pd.read_sql_query(query, conn)
        return df.iloc[0].to_dict()
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_all_customers() -> pd.DataFrame:
    """Get all customer data."""
    conn = sqlite3.connect(get_db_path())
    try:
        return pd.read_sql_query("SELECT * FROM customers", conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_demographic_summary() -> pd.DataFrame:
    """Get demographic summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        return pd.read_sql_query("SELECT * FROM v_demographic_summary", conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_country_summary() -> pd.DataFrame:
    """Get country summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        return pd.read_sql_query("SELECT * FROM v_country_summary ORDER BY total_spend DESC", conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_segment_summary() -> pd.DataFrame:
    """Get segment summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        return pd.read_sql_query("SELECT * FROM v_segment_summary", conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_filter_options() -> Dict[str, List]:
    """Get filter options."""
    conn = sqlite3.connect(get_db_path())
    try:
        options = {}

        df = pd.read_sql_query("SELECT DISTINCT country FROM customers ORDER BY country", conn)
        options['countries'] = df['country'].tolist()

        df = pd.read_sql_query("SELECT DISTINCT gender FROM customers", conn)
        options['genders'] = df['gender'].tolist()

        df = pd.read_sql_query("SELECT DISTINCT age_group FROM customers", conn)
        options['age_groups'] = [x for x in df['age_group'].tolist() if x is not None]

        df = pd.read_sql_query("SELECT DISTINCT income_segment FROM customers", conn)
        options['income_segments'] = [x for x in df['income_segment'].tolist() if x is not None]

        df = pd.read_sql_query("SELECT DISTINCT loyalty_segment FROM customers", conn)
        options['loyalty_segments'] = [x for x in df['loyalty_segment'].tolist() if x is not None]

        df = pd.read_sql_query("SELECT DISTINCT product_category_preference FROM customers", conn)
        options['categories'] = df['product_category_preference'].tolist()

        return options
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_customers_filtered(
    countries: Optional[List[str]] = None,
    genders: Optional[List[str]] = None,
    age_groups: Optional[List[str]] = None,
    loyalty_segments: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get filtered customer data."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = "SELECT * FROM customers WHERE 1=1"
        params = []

        if countries:
            placeholders = ','.join(['?' for _ in countries])
            query += f" AND country IN ({placeholders})"
            params.extend(countries)

        if genders:
            placeholders = ','.join(['?' for _ in genders])
            query += f" AND gender IN ({placeholders})"
            params.extend(genders)

        if age_groups:
            placeholders = ','.join(['?' for _ in age_groups])
            query += f" AND age_group IN ({placeholders})"
            params.extend(age_groups)

        if loyalty_segments:
            placeholders = ','.join(['?' for _ in loyalty_segments])
            query += f" AND loyalty_segment IN ({placeholders})"
            params.extend(loyalty_segments)

        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_cohort_analysis() -> pd.DataFrame:
    """Get cohort analysis data."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            loyalty_segment,
            age_group,
            COUNT(*) as customer_count,
            AVG(monthly_spend) as avg_spend,
            AVG(customer_value_score) as avg_value,
            AVG(engagement_score) as avg_engagement
        FROM customers
        WHERE loyalty_segment IS NOT NULL AND age_group IS NOT NULL
        GROUP BY loyalty_segment, age_group
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_behavior_metrics() -> pd.DataFrame:
    """Get behavior metrics summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            product_category_preference as category,
            COUNT(*) as customer_count,
            AVG(monthly_spend) as avg_spend,
            AVG(weekly_purchases) as avg_purchases,
            AVG(cart_abandonment_rate) as avg_abandonment,
            AVG(average_order_value) as avg_aov
        FROM customers
        GROUP BY product_category_preference
        ORDER BY customer_count DESC
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()
