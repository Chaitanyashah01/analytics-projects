"""
SQL query functions for Renewable Energy Insights.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st


def get_db_path() -> str:
    return str(Path(__file__).parent.parent / "data" / "energy.db")


@st.cache_data(ttl=3600)
def get_all_data() -> pd.DataFrame:
    """Get all energy production data."""
    conn = sqlite3.connect(get_db_path())
    try:
        df = pd.read_sql_query("SELECT * FROM energy_production ORDER BY date, start_hour", conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_kpi_metrics() -> Dict[str, Any]:
    """Get KPI metrics."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            SUM(production) as total_production,
            AVG(production) as avg_production,
            MAX(production) as peak_production,
            COUNT(DISTINCT date) as total_days,
            COUNT(DISTINCT source) as source_count
        FROM energy_production
        """
        df = pd.read_sql_query(query, conn)
        return df.iloc[0].to_dict()
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_source_summary() -> pd.DataFrame:
    """Get production summary by source."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            source,
            SUM(production) as total_production,
            AVG(production) as avg_production,
            MIN(production) as min_production,
            MAX(production) as peak_production,
            COUNT(*) as readings
        FROM energy_production
        GROUP BY source
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_daily_production() -> pd.DataFrame:
    """Get daily production totals."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            date,
            source,
            SUM(production) as total_production,
            AVG(production) as avg_production,
            COUNT(*) as readings
        FROM energy_production
        GROUP BY date, source
        ORDER BY date
        """
        df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_hourly_pattern() -> pd.DataFrame:
    """Get hourly production patterns."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            start_hour,
            source,
            AVG(production) as avg_production,
            MIN(production) as min_production,
            MAX(production) as max_production,
            COUNT(*) as readings
        FROM energy_production
        GROUP BY start_hour, source
        ORDER BY start_hour
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_seasonal_summary() -> pd.DataFrame:
    """Get seasonal production summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            season,
            source,
            SUM(production) as total_production,
            AVG(production) as avg_production,
            MIN(production) as min_production,
            MAX(production) as max_production,
            COUNT(*) as readings
        FROM energy_production
        GROUP BY season, source
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_monthly_summary() -> pd.DataFrame:
    """Get monthly production summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            month_name,
            month,
            source,
            SUM(production) as total_production,
            AVG(production) as avg_production,
            COUNT(*) as readings
        FROM energy_production
        GROUP BY month_name, month, source
        ORDER BY month
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_day_of_week_summary() -> pd.DataFrame:
    """Get day of week summary."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            day_name,
            source,
            AVG(production) as avg_production,
            SUM(production) as total_production,
            COUNT(*) as readings
        FROM energy_production
        GROUP BY day_name, source
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_filter_options() -> Dict[str, List]:
    """Get filter options."""
    conn = sqlite3.connect(get_db_path())
    try:
        options = {}

        df = pd.read_sql_query("SELECT DISTINCT source FROM energy_production", conn)
        options['sources'] = df['source'].tolist()

        df = pd.read_sql_query("SELECT DISTINCT season FROM energy_production", conn)
        options['seasons'] = df['season'].tolist()

        df = pd.read_sql_query("SELECT DISTINCT month_name FROM energy_production", conn)
        options['months'] = df['month_name'].tolist()

        df = pd.read_sql_query("SELECT MIN(date) as min_date, MAX(date) as max_date FROM energy_production", conn)
        options['date_range'] = (df['min_date'].iloc[0], df['max_date'].iloc[0])

        return options
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_peak_analysis() -> pd.DataFrame:
    """Get peak production analysis."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            date,
            start_hour,
            source,
            production,
            day_name,
            season
        FROM energy_production
        WHERE production > (SELECT AVG(production) * 1.5 FROM energy_production)
        ORDER BY production DESC
        LIMIT 100
        """
        df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        return df
    finally:
        conn.close()
