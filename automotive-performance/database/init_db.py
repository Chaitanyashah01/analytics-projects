"""
Database initialization for Automotive Performance Analytics.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CarDataCleaner:
    """Data cleaning for automotive dataset."""

    def __init__(self):
        self.cleaning_log = []

    def clean_price(self, price_str):
        """Clean price string to numeric value."""
        if pd.isna(price_str):
            return np.nan
        price_str = str(price_str)
        # Remove $ and commas, handle ranges
        price_str = price_str.replace('$', '').replace(',', '').strip()
        # Handle price ranges (take average)
        if '-' in price_str:
            parts = price_str.split('-')
            try:
                return (float(parts[0].strip()) + float(parts[1].strip())) / 2
            except ValueError:
                return np.nan
        try:
            return float(price_str)
        except ValueError:
            return np.nan

    def clean_horsepower(self, hp_str):
        """Clean horsepower string to numeric."""
        if pd.isna(hp_str):
            return np.nan
        hp_str = str(hp_str).lower()
        # Remove 'hp' and handle ranges
        hp_str = hp_str.replace('hp', '').strip()
        if '-' in hp_str:
            parts = hp_str.split('-')
            try:
                return (float(parts[0].strip()) + float(parts[1].strip())) / 2
            except ValueError:
                return np.nan
        try:
            return float(hp_str)
        except ValueError:
            return np.nan

    def clean_speed(self, speed_str):
        """Clean speed string to numeric (km/h)."""
        if pd.isna(speed_str):
            return np.nan
        speed_str = str(speed_str).lower()
        speed_str = speed_str.replace('km/h', '').replace('kph', '').strip()
        try:
            return float(speed_str)
        except ValueError:
            return np.nan

    def clean_acceleration(self, accel_str):
        """Clean acceleration string (0-100 km/h time in seconds)."""
        if pd.isna(accel_str):
            return np.nan
        accel_str = str(accel_str).lower()
        accel_str = accel_str.replace('sec', '').replace('s', '').strip()
        try:
            return float(accel_str)
        except ValueError:
            return np.nan

    def clean_cc(self, cc_str):
        """Clean engine CC/capacity string."""
        if pd.isna(cc_str):
            return np.nan
        cc_str = str(cc_str).lower()
        # Remove 'cc' and commas
        cc_str = cc_str.replace('cc', '').replace(',', '').strip()
        try:
            return float(cc_str)
        except ValueError:
            return np.nan

    def clean_torque(self, torque_str):
        """Clean torque string to numeric (Nm)."""
        if pd.isna(torque_str):
            return np.nan
        torque_str = str(torque_str).lower()
        torque_str = torque_str.replace('nm', '').replace(',', '').strip()
        # Handle ranges
        if '-' in torque_str:
            parts = torque_str.split('-')
            try:
                return (float(parts[0].strip()) + float(parts[1].strip())) / 2
            except ValueError:
                return np.nan
        try:
            return float(torque_str)
        except ValueError:
            return np.nan

    def clean_seats(self, seats_str):
        """Clean seats to integer."""
        if pd.isna(seats_str):
            return np.nan
        try:
            return int(float(str(seats_str).strip()))
        except ValueError:
            return np.nan

    def standardize_fuel_type(self, fuel_str):
        """Standardize fuel type names."""
        if pd.isna(fuel_str):
            return 'Unknown'
        fuel_str = str(fuel_str).lower().strip()

        if 'electric' in fuel_str or 'ev' in fuel_str:
            return 'Electric'
        elif 'hybrid' in fuel_str:
            return 'Hybrid'
        elif 'diesel' in fuel_str:
            return 'Diesel'
        elif 'petrol' in fuel_str or 'gasoline' in fuel_str or 'gas' in fuel_str:
            return 'Petrol'
        elif 'plug' in fuel_str:
            return 'Plug-in Hybrid'
        else:
            return fuel_str.title()


def create_database(db_path: str, data_dir: str) -> dict:
    """Create SQLite database from CSV file."""
    db_path = Path(db_path)
    data_dir = Path(data_dir)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cleaner = CarDataCleaner()
    report = {'tables': {}, 'cleaning': {}}

    try:
        # Load CSV
        csv_path = data_dir / 'Cars Datasets 2025.csv'
        logger.info(f"Loading {csv_path}...")
        # Try different encodings to handle special characters
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                logger.info(f"Successfully loaded with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode CSV with any supported encoding")

        report['cleaning']['original_rows'] = len(df)

        # Rename columns for consistency
        df.columns = [
            'company', 'car_name', 'engine', 'cc_capacity',
            'horsepower', 'top_speed', 'acceleration_0_100',
            'price', 'fuel_type', 'seats', 'torque'
        ]

        # Clean data
        logger.info("Cleaning data...")

        df['price_usd'] = df['price'].apply(cleaner.clean_price)
        df['horsepower_hp'] = df['horsepower'].apply(cleaner.clean_horsepower)
        df['top_speed_kmh'] = df['top_speed'].apply(cleaner.clean_speed)
        df['acceleration_sec'] = df['acceleration_0_100'].apply(cleaner.clean_acceleration)
        df['cc_numeric'] = df['cc_capacity'].apply(cleaner.clean_cc)
        df['torque_nm'] = df['torque'].apply(cleaner.clean_torque)
        df['seats_num'] = df['seats'].apply(cleaner.clean_seats)
        df['fuel_type_clean'] = df['fuel_type'].apply(cleaner.standardize_fuel_type)

        # Clean company names
        df['company'] = df['company'].str.strip().str.upper()
        df['car_name'] = df['car_name'].str.strip()

        # Remove duplicates
        original_len = len(df)
        df = df.drop_duplicates(subset=['company', 'car_name'])
        report['cleaning']['duplicates_removed'] = original_len - len(df)

        # Calculate derived metrics
        df['price_per_hp'] = df['price_usd'] / df['horsepower_hp']
        df['power_to_weight_proxy'] = df['horsepower_hp'] / df['cc_numeric'] * 1000
        df['performance_score'] = (
            (df['horsepower_hp'] / df['horsepower_hp'].max()) * 0.3 +
            (df['top_speed_kmh'] / df['top_speed_kmh'].max()) * 0.3 +
            (1 - df['acceleration_sec'] / df['acceleration_sec'].max()) * 0.4
        ) * 100

        # Categorize price segments
        df['price_segment'] = pd.cut(
            df['price_usd'],
            bins=[0, 30000, 60000, 100000, 200000, float('inf')],
            labels=['Budget', 'Mid-Range', 'Premium', 'Luxury', 'Ultra-Luxury']
        )

        # Categorize performance
        df['performance_category'] = pd.cut(
            df['performance_score'],
            bins=[0, 33, 66, 100],
            labels=['Standard', 'Sport', 'Performance']
        )

        # Save to database
        df.to_sql('cars', conn, index=False, if_exists='replace')
        report['tables']['cars'] = len(df)

        # Create brand summary view
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_brand_summary AS
            SELECT
                company,
                COUNT(*) as model_count,
                AVG(price_usd) as avg_price,
                AVG(horsepower_hp) as avg_horsepower,
                AVG(top_speed_kmh) as avg_top_speed,
                AVG(acceleration_sec) as avg_acceleration,
                MIN(price_usd) as min_price,
                MAX(price_usd) as max_price
            FROM cars
            GROUP BY company
        """)

        # Create fuel type summary view
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_fuel_type_summary AS
            SELECT
                fuel_type_clean as fuel_type,
                COUNT(*) as model_count,
                AVG(price_usd) as avg_price,
                AVG(horsepower_hp) as avg_horsepower,
                AVG(top_speed_kmh) as avg_top_speed
            FROM cars
            GROUP BY fuel_type_clean
        """)

        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cars_company ON cars(company)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cars_fuel ON cars(fuel_type_clean)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cars_price ON cars(price_usd)")

        conn.commit()

        report['cleaning']['final_rows'] = len(df)
        report['cleaning']['columns'] = list(df.columns)

        logger.info(f"Database created with {len(df)} records")

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        conn.close()

    return report


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == "__main__":
    db_path = Path(__file__).parent.parent / "data" / "automotive.db"
    data_dir = Path(__file__).parent.parent / "data"

    report = create_database(str(db_path), str(data_dir))
    print("\nDatabase Creation Report:")
    print("=" * 50)
    for table, count in report['tables'].items():
        print(f"  {table}: {count:,} rows")
    print(f"\nCleaning: {report['cleaning']}")
