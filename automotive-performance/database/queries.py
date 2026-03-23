"""
SQL query functions for Automotive Performance Analytics.
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
    # Check if running on Streamlit Cloud (read-only filesystem)
    if os.path.exists('/mount/src'):
        return str(Path(tempfile.gettempdir()) / "automotive.db")
    return str(Path(__file__).parent.parent / "data" / "automotive.db")


@st.cache_data(ttl=3600)
def get_all_cars() -> pd.DataFrame:
    """Get all car data."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT * FROM cars
        ORDER BY company, car_name
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_kpi_metrics() -> Dict[str, Any]:
    """Get key performance indicators."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            COUNT(*) as total_models,
            COUNT(DISTINCT company) as total_brands,
            AVG(price_usd) as avg_price,
            AVG(horsepower_hp) as avg_horsepower,
            AVG(top_speed_kmh) as avg_top_speed,
            AVG(acceleration_sec) as avg_acceleration,
            MIN(price_usd) as min_price,
            MAX(price_usd) as max_price,
            MIN(acceleration_sec) as fastest_acceleration,
            MAX(top_speed_kmh) as highest_speed
        FROM cars
        WHERE price_usd IS NOT NULL
        """
        df = pd.read_sql_query(query, conn)
        return df.iloc[0].to_dict()
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_brand_summary() -> pd.DataFrame:
    """Get brand summary statistics."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            company,
            COUNT(*) as model_count,
            AVG(price_usd) as avg_price,
            AVG(horsepower_hp) as avg_horsepower,
            AVG(top_speed_kmh) as avg_top_speed,
            AVG(acceleration_sec) as avg_acceleration,
            AVG(torque_nm) as avg_torque,
            MIN(price_usd) as min_price,
            MAX(price_usd) as max_price,
            AVG(performance_score) as avg_performance_score
        FROM cars
        WHERE price_usd IS NOT NULL
        GROUP BY company
        ORDER BY avg_price DESC
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_fuel_type_summary() -> pd.DataFrame:
    """Get fuel type summary statistics."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            fuel_type_clean as fuel_type,
            COUNT(*) as model_count,
            AVG(price_usd) as avg_price,
            AVG(horsepower_hp) as avg_horsepower,
            AVG(top_speed_kmh) as avg_top_speed,
            AVG(acceleration_sec) as avg_acceleration,
            AVG(performance_score) as avg_performance_score
        FROM cars
        WHERE price_usd IS NOT NULL
        GROUP BY fuel_type_clean
        ORDER BY model_count DESC
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_cars_filtered(
    brands: Optional[List[str]] = None,
    fuel_types: Optional[List[str]] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_hp: Optional[float] = None
) -> pd.DataFrame:
    """Get filtered car data."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = "SELECT * FROM cars WHERE price_usd IS NOT NULL"
        params = []

        if brands:
            placeholders = ','.join(['?' for _ in brands])
            query += f" AND company IN ({placeholders})"
            params.extend(brands)

        if fuel_types:
            placeholders = ','.join(['?' for _ in fuel_types])
            query += f" AND fuel_type_clean IN ({placeholders})"
            params.extend(fuel_types)

        if min_price is not None:
            query += " AND price_usd >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND price_usd <= ?"
            params.append(max_price)

        if min_hp is not None:
            query += " AND horsepower_hp >= ?"
            params.append(min_hp)

        query += " ORDER BY company, car_name"

        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_filter_options() -> Dict[str, List]:
    """Get unique values for filters."""
    conn = sqlite3.connect(get_db_path())
    try:
        options = {}

        df = pd.read_sql_query("SELECT DISTINCT company FROM cars ORDER BY company", conn)
        options['brands'] = df['company'].tolist()

        df = pd.read_sql_query("SELECT DISTINCT fuel_type_clean FROM cars ORDER BY fuel_type_clean", conn)
        options['fuel_types'] = df['fuel_type_clean'].tolist()

        df = pd.read_sql_query("SELECT DISTINCT price_segment FROM cars WHERE price_segment IS NOT NULL", conn)
        options['price_segments'] = df['price_segment'].tolist()

        df = pd.read_sql_query("SELECT MIN(price_usd) as min, MAX(price_usd) as max FROM cars", conn)
        options['price_range'] = (df['min'].iloc[0], df['max'].iloc[0])

        return options
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_top_performers(metric: str = 'horsepower_hp', limit: int = 10) -> pd.DataFrame:
    """Get top performing cars by metric."""
    conn = sqlite3.connect(get_db_path())
    try:
        # Handle acceleration (lower is better)
        order = "ASC" if metric == 'acceleration_sec' else "DESC"

        query = f"""
        SELECT
            company,
            car_name,
            price_usd,
            horsepower_hp,
            top_speed_kmh,
            acceleration_sec,
            fuel_type_clean,
            performance_score
        FROM cars
        WHERE {metric} IS NOT NULL
        ORDER BY {metric} {order}
        LIMIT ?
        """
        return pd.read_sql_query(query, conn, params=[limit])
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_price_performance_data() -> pd.DataFrame:
    """Get data for price-performance analysis."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            company,
            car_name,
            price_usd,
            horsepower_hp,
            top_speed_kmh,
            acceleration_sec,
            fuel_type_clean,
            price_per_hp,
            performance_score,
            price_segment
        FROM cars
        WHERE price_usd IS NOT NULL
          AND horsepower_hp IS NOT NULL
          AND performance_score IS NOT NULL
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_segment_analysis() -> pd.DataFrame:
    """Get price segment analysis."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            price_segment,
            COUNT(*) as model_count,
            AVG(price_usd) as avg_price,
            AVG(horsepower_hp) as avg_horsepower,
            AVG(top_speed_kmh) as avg_top_speed,
            AVG(acceleration_sec) as avg_acceleration,
            AVG(performance_score) as avg_performance_score,
            AVG(price_per_hp) as avg_price_per_hp
        FROM cars
        WHERE price_segment IS NOT NULL
        GROUP BY price_segment
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()
