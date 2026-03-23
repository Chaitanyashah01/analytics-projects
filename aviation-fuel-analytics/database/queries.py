"""
SQL query functions for Aviation Fuel Analytics dashboard.
Provides type-safe query execution with caching support.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import streamlit as st


def get_db_path() -> str:
    """Get the database path."""
    return str(Path(__file__).parent.parent / "data" / "aviation.db")


@st.cache_data(ttl=3600)
def get_table_stats() -> Dict[str, int]:
    """Get row counts for all tables."""
    conn = sqlite3.connect(get_db_path())
    try:
        cursor = conn.cursor()
        tables = ['airline_financials', 'ticket_prices', 'conflict_events',
                  'fuel_surcharges', 'oil_prices', 'route_costs']
        stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        return stats
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_kpi_metrics() -> Dict[str, Any]:
    """Get key performance indicators for executive dashboard."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            SUM(revenue_usd_m) as total_revenue,
            AVG(profit_margin_pct) as avg_profit_margin,
            SUM(fuel_cost_usd_m) as total_fuel_cost,
            AVG(fuel_cost_pct_revenue) as avg_fuel_pct,
            SUM(passengers_carried_m) as total_passengers,
            COUNT(DISTINCT airline) as airline_count,
            COUNT(DISTINCT region) as region_count
        FROM airline_financials
        """
        df = pd.read_sql_query(query, conn)
        return df.iloc[0].to_dict()
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_financial_timeseries(
    airlines: Optional[List[str]] = None,
    regions: Optional[List[str]] = None,
    conflict_phases: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get financial time series data with optional filters."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            month,
            conflict_phase,
            airline,
            region,
            airline_type,
            revenue_usd_m,
            fuel_cost_usd_m,
            fuel_cost_pct_revenue,
            net_profit_usd_m,
            profit_margin_pct,
            passengers_carried_m,
            brent_crude_usd_barrel,
            jet_fuel_usd_barrel,
            fuel_hedging_pct,
            hedge_savings_usd_m
        FROM airline_financials
        WHERE 1=1
        """
        params = []

        if airlines:
            placeholders = ','.join(['?' for _ in airlines])
            query += f" AND airline IN ({placeholders})"
            params.extend(airlines)

        if regions:
            placeholders = ','.join(['?' for _ in regions])
            query += f" AND region IN ({placeholders})"
            params.extend(regions)

        if conflict_phases:
            placeholders = ','.join(['?' for _ in conflict_phases])
            query += f" AND conflict_phase IN ({placeholders})"
            params.extend(conflict_phases)

        query += " ORDER BY month"

        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_oil_price_correlation() -> pd.DataFrame:
    """Get data for oil price correlation analysis."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            f.month,
            f.conflict_phase,
            AVG(f.brent_crude_usd_barrel) as brent_crude,
            AVG(f.jet_fuel_usd_barrel) as jet_fuel,
            AVG(f.fuel_cost_pct_revenue) as fuel_cost_pct,
            AVG(f.profit_margin_pct) as profit_margin,
            SUM(f.revenue_usd_m) as total_revenue,
            AVG(f.fuel_hedging_pct) as avg_hedging
        FROM airline_financials f
        GROUP BY f.month, f.conflict_phase
        ORDER BY f.month
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_conflict_events() -> pd.DataFrame:
    """Get all conflict events with impact data."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            event_date,
            event_type,
            event_description,
            location,
            severity,
            brent_before_usd,
            brent_after_usd,
            oil_price_change_pct,
            airfare_impact_pct,
            conflict_phase,
            flight_cancellations_est,
            airspace_closures_countries
        FROM conflict_events
        ORDER BY event_date
        """
        df = pd.read_sql_query(query, conn)
        df['event_date'] = pd.to_datetime(df['event_date'])
        return df
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_airline_comparison() -> pd.DataFrame:
    """Get airline comparison metrics."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            airline,
            region,
            airline_type,
            AVG(revenue_usd_m) as avg_quarterly_revenue,
            SUM(revenue_usd_m) as total_revenue,
            AVG(profit_margin_pct) as avg_profit_margin,
            AVG(fuel_cost_pct_revenue) as avg_fuel_cost_pct,
            SUM(passengers_carried_m) as total_passengers,
            AVG(fuel_hedging_pct) as avg_hedging_pct,
            SUM(hedge_savings_usd_m) as total_hedge_savings,
            COUNT(*) as quarters_reported
        FROM airline_financials
        GROUP BY airline, region, airline_type
        ORDER BY total_revenue DESC
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_route_profitability(
    airlines: Optional[List[str]] = None
) -> pd.DataFrame:
    """Get route-level profitability data."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            airline,
            origin_city,
            destination_city,
            aircraft_type,
            original_distance_km,
            actual_distance_km,
            extra_distance_km,
            rerouted,
            flight_cancelled,
            fuel_consumption_bbl,
            brent_crude_usd,
            jet_fuel_usd_barrel,
            total_fuel_cost_usd,
            extra_fuel_cost_usd,
            base_ticket_price_usd,
            fuel_surcharge_usd,
            total_ticket_price_usd,
            estimated_passengers,
            route_revenue_usd,
            fuel_pct_of_cost,
            conflict_phase,
            month
        FROM route_costs
        WHERE 1=1
        """
        params = []

        if airlines:
            placeholders = ','.join(['?' for _ in airlines])
            query += f" AND airline IN ({placeholders})"
            params.extend(airlines)

        return pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_fuel_surcharge_analysis() -> pd.DataFrame:
    """Get fuel surcharge analysis by distance band."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            surcharge_band,
            km_range,
            conflict_phase,
            AVG(fuel_surcharge_usd) as avg_surcharge,
            MIN(fuel_surcharge_usd) as min_surcharge,
            MAX(fuel_surcharge_usd) as max_surcharge,
            AVG(surcharge_as_pct_base) as avg_surcharge_pct,
            AVG(brent_crude_usd_barrel) as avg_brent,
            COUNT(*) as data_points
        FROM fuel_surcharges
        GROUP BY surcharge_band, km_range, conflict_phase
        ORDER BY surcharge_band, conflict_phase
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_monthly_oil_prices() -> pd.DataFrame:
    """Get monthly oil and jet fuel prices."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            month,
            conflict_phase,
            brent_crude_usd_barrel,
            jet_fuel_usd_barrel,
            refinery_margin_usd,
            jet_fuel_usd_per_gallon,
            wti_crude_usd_barrel,
            opec_production_mbd,
            us_strategic_reserve_mbl,
            strait_hormuz_disrupted,
            yoy_brent_change_pct
        FROM oil_prices
        ORDER BY month
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_filter_options() -> Dict[str, List[str]]:
    """Get unique values for filter dropdowns."""
    conn = sqlite3.connect(get_db_path())
    try:
        options = {}

        # Airlines
        df = pd.read_sql_query("SELECT DISTINCT airline FROM airline_financials ORDER BY airline", conn)
        options['airlines'] = df['airline'].tolist()

        # Regions
        df = pd.read_sql_query("SELECT DISTINCT region FROM airline_financials ORDER BY region", conn)
        options['regions'] = df['region'].tolist()

        # Airline types
        df = pd.read_sql_query("SELECT DISTINCT airline_type FROM airline_financials ORDER BY airline_type", conn)
        options['airline_types'] = df['airline_type'].tolist()

        # Conflict phases
        df = pd.read_sql_query("SELECT DISTINCT conflict_phase FROM airline_financials ORDER BY conflict_phase", conn)
        options['conflict_phases'] = df['conflict_phase'].tolist()

        # Months
        df = pd.read_sql_query("SELECT DISTINCT month FROM airline_financials ORDER BY month", conn)
        options['months'] = df['month'].tolist()

        return options
    finally:
        conn.close()


@st.cache_data(ttl=3600)
def get_phase_comparison() -> pd.DataFrame:
    """Get metrics comparison across conflict phases."""
    conn = sqlite3.connect(get_db_path())
    try:
        query = """
        SELECT
            conflict_phase,
            AVG(brent_crude_usd_barrel) as avg_brent,
            AVG(jet_fuel_usd_barrel) as avg_jet_fuel,
            AVG(profit_margin_pct) as avg_profit_margin,
            AVG(fuel_cost_pct_revenue) as avg_fuel_cost_pct,
            SUM(revenue_usd_m) as total_revenue,
            SUM(passengers_carried_m) as total_passengers,
            COUNT(DISTINCT airline) as airlines_reporting
        FROM airline_financials
        GROUP BY conflict_phase
        """
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()
