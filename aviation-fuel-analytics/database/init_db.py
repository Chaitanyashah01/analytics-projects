"""
Database initialization module for Aviation Fuel Analytics.
Creates SQLite database from CSV files with proper schema and indexes.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Data cleaning and preprocessing utilities."""

    def __init__(self):
        self.cleaning_report = {
            'rows_before': 0,
            'rows_after': 0,
            'duplicates_removed': 0,
            'nulls_filled': {},
            'outliers_detected': {},
            'type_conversions': []
        }

    def clean_numeric_column(self, df: pd.DataFrame, col: str, fill_strategy: str = 'median') -> pd.DataFrame:
        """Clean numeric columns with various strategies."""
        if col not in df.columns:
            return df

        # Convert to numeric, coercing errors
        original_nulls = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[,$%]', '', regex=True), errors='coerce')

        # Fill missing values
        nulls_after_conversion = df[col].isna().sum()
        if nulls_after_conversion > 0:
            if fill_strategy == 'median':
                fill_value = df[col].median()
            elif fill_strategy == 'mean':
                fill_value = df[col].mean()
            elif fill_strategy == 'zero':
                fill_value = 0
            else:
                fill_value = df[col].median()

            df[col] = df[col].fillna(fill_value)
            self.cleaning_report['nulls_filled'][col] = nulls_after_conversion

        return df

    def detect_outliers_iqr(self, df: pd.DataFrame, col: str, threshold: float = 1.5) -> pd.Series:
        """Detect outliers using IQR method."""
        if col not in df.columns:
            return pd.Series([False] * len(df))

        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR

        outliers = (df[col] < lower_bound) | (df[col] > upper_bound)
        self.cleaning_report['outliers_detected'][col] = outliers.sum()

        return outliers

    def remove_duplicates(self, df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        """Remove duplicate rows."""
        self.cleaning_report['rows_before'] = len(df)
        df = df.drop_duplicates(subset=subset)
        self.cleaning_report['rows_after'] = len(df)
        self.cleaning_report['duplicates_removed'] = self.cleaning_report['rows_before'] - self.cleaning_report['rows_after']
        return df

    def get_report(self) -> dict:
        """Return cleaning report."""
        return self.cleaning_report


def create_database(db_path: str, data_dir: str) -> dict:
    """
    Create SQLite database from CSV files.

    Returns:
        dict: Database creation report with statistics
    """
    db_path = Path(db_path)
    data_dir = Path(data_dir)

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cleaner = DataCleaner()
    report = {'tables': {}, 'total_rows': 0}

    try:
        # 1. Load and clean airline financial impact data
        logger.info("Loading airline_financial_impact.csv...")
        df_financial = pd.read_csv(data_dir / 'airline_financial_impact.csv')
        df_financial = cleaner.remove_duplicates(df_financial)

        # Clean numeric columns
        numeric_cols = ['revenue_usd_m', 'fuel_cost_usd_m', 'net_profit_usd_m',
                       'profit_margin_pct', 'passengers_carried_m', 'fuel_hedging_pct',
                       'brent_crude_usd_barrel', 'jet_fuel_usd_barrel']
        for col in numeric_cols:
            df_financial = cleaner.clean_numeric_column(df_financial, col)

        df_financial.to_sql('airline_financials', conn, index=False, if_exists='replace')
        report['tables']['airline_financials'] = len(df_financial)

        # 2. Load ticket prices
        logger.info("Loading airline_ticket_prices.csv...")
        df_tickets = pd.read_csv(data_dir / 'airline_ticket_prices.csv')
        df_tickets = cleaner.remove_duplicates(df_tickets)

        ticket_numeric = ['base_fare_usd', 'fuel_surcharge_usd', 'taxes_fees_usd',
                         'total_fare_usd', 'load_factor_pct']
        for col in ticket_numeric:
            df_tickets = cleaner.clean_numeric_column(df_tickets, col)

        df_tickets.to_sql('ticket_prices', conn, index=False, if_exists='replace')
        report['tables']['ticket_prices'] = len(df_tickets)

        # 3. Load conflict events
        logger.info("Loading conflict_oil_events.csv...")
        df_events = pd.read_csv(data_dir / 'conflict_oil_events.csv')
        df_events = cleaner.remove_duplicates(df_events)
        df_events['event_date'] = pd.to_datetime(df_events['event_date'], errors='coerce')

        df_events.to_sql('conflict_events', conn, index=False, if_exists='replace')
        report['tables']['conflict_events'] = len(df_events)

        # 4. Load fuel surcharges
        logger.info("Loading fuel_surcharges.csv...")
        df_surcharges = pd.read_csv(data_dir / 'fuel_surcharges.csv')
        df_surcharges = cleaner.remove_duplicates(df_surcharges)

        df_surcharges.to_sql('fuel_surcharges', conn, index=False, if_exists='replace')
        report['tables']['fuel_surcharges'] = len(df_surcharges)

        # 5. Load oil prices
        logger.info("Loading oil_jet_fuel_prices.csv...")
        df_oil = pd.read_csv(data_dir / 'oil_jet_fuel_prices.csv')
        df_oil = cleaner.remove_duplicates(df_oil)

        df_oil.to_sql('oil_prices', conn, index=False, if_exists='replace')
        report['tables']['oil_prices'] = len(df_oil)

        # 6. Load route cost impact
        logger.info("Loading route_cost_impact.csv...")
        df_routes = pd.read_csv(data_dir / 'route_cost_impact.csv')
        df_routes = cleaner.remove_duplicates(df_routes)

        route_numeric = ['original_distance_km', 'actual_distance_km', 'fuel_consumption_bbl',
                        'total_fuel_cost_usd', 'base_ticket_price_usd', 'total_ticket_price_usd']
        for col in route_numeric:
            df_routes = cleaner.clean_numeric_column(df_routes, col)

        df_routes.to_sql('route_costs', conn, index=False, if_exists='replace')
        report['tables']['route_costs'] = len(df_routes)

        # Create indexes for performance
        logger.info("Creating indexes...")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_financials_month ON airline_financials(month)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_financials_airline ON airline_financials(airline)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tickets_month ON ticket_prices(month)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_routes_airline ON route_costs(airline)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_oil_month ON oil_prices(month)")

        # Create summary views
        logger.info("Creating summary views...")

        # Monthly summary view
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_monthly_summary AS
            SELECT
                month,
                conflict_phase,
                COUNT(DISTINCT airline) as airline_count,
                SUM(revenue_usd_m) as total_revenue,
                AVG(profit_margin_pct) as avg_profit_margin,
                AVG(fuel_cost_pct_revenue) as avg_fuel_cost_pct,
                SUM(passengers_carried_m) as total_passengers
            FROM airline_financials
            GROUP BY month, conflict_phase
        """)

        # Airline performance view
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_airline_performance AS
            SELECT
                airline,
                region,
                airline_type,
                AVG(revenue_usd_m) as avg_revenue,
                AVG(profit_margin_pct) as avg_profit_margin,
                AVG(fuel_cost_pct_revenue) as avg_fuel_cost_pct,
                SUM(passengers_carried_m) as total_passengers,
                COUNT(*) as data_points
            FROM airline_financials
            GROUP BY airline, region, airline_type
        """)

        conn.commit()

        report['total_rows'] = sum(report['tables'].values())
        report['cleaning_report'] = cleaner.get_report()

        logger.info(f"Database created successfully with {report['total_rows']} total rows")

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        conn.close()

    return report


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    # Run database initialization
    db_path = Path(__file__).parent.parent / "data" / "aviation.db"
    data_dir = Path(__file__).parent.parent / "data"

    report = create_database(str(db_path), str(data_dir))
    print("\nDatabase Creation Report:")
    print("=" * 50)
    for table, count in report['tables'].items():
        print(f"  {table}: {count:,} rows")
    print(f"\nTotal rows: {report['total_rows']:,}")
