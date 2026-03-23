"""
Database initialization for Renewable Energy Insights.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database(db_path: str, data_dir: str) -> dict:
    """Create SQLite database from CSV file."""
    db_path = Path(db_path)
    data_dir = Path(data_dir)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    report = {'tables': {}, 'cleaning': {}}

    try:
        csv_path = data_dir / 'Energy Production Dataset.csv'
        logger.info(f"Loading {csv_path}...")
        df = pd.read_csv(csv_path)

        report['cleaning']['original_rows'] = len(df)

        # Clean column names
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]

        # Parse date
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y', errors='coerce')
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['week'] = df['date'].dt.isocalendar().week

        # Ensure numeric columns
        df['production'] = pd.to_numeric(df['production'], errors='coerce')
        df['start_hour'] = pd.to_numeric(df['start_hour'], errors='coerce')
        df['end_hour'] = pd.to_numeric(df['end_hour'], errors='coerce')

        # Clean source names
        df['source'] = df['source'].str.strip().str.title()

        # Remove duplicates
        original_len = len(df)
        df = df.drop_duplicates()
        report['cleaning']['duplicates_removed'] = original_len - len(df)

        # Remove rows with null production
        df = df.dropna(subset=['production'])

        # Add derived columns
        df['hour_duration'] = df['end_hour'] - df['start_hour']
        df['hour_duration'] = df['hour_duration'].apply(lambda x: x if x > 0 else x + 24)

        # Create time of day categories
        def categorize_time(hour):
            if 5 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 21:
                return 'Evening'
            else:
                return 'Night'

        df['time_of_day'] = df['start_hour'].apply(categorize_time)

        # Save to database
        df.to_sql('energy_production', conn, index=False, if_exists='replace')
        report['tables']['energy_production'] = len(df)

        # Create summary views
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_daily_production AS
            SELECT
                date,
                source,
                day_name,
                month_name,
                season,
                SUM(production) as total_production,
                AVG(production) as avg_production,
                COUNT(*) as readings
            FROM energy_production
            GROUP BY date, source, day_name, month_name, season
        """)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_hourly_pattern AS
            SELECT
                start_hour,
                source,
                AVG(production) as avg_production,
                MIN(production) as min_production,
                MAX(production) as max_production,
                COUNT(*) as readings
            FROM energy_production
            GROUP BY start_hour, source
        """)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_seasonal_summary AS
            SELECT
                season,
                source,
                SUM(production) as total_production,
                AVG(production) as avg_production,
                COUNT(*) as readings
            FROM energy_production
            GROUP BY season, source
        """)

        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_energy_date ON energy_production(date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_energy_source ON energy_production(source)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_energy_season ON energy_production(season)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_energy_hour ON energy_production(start_hour)")

        conn.commit()
        report['cleaning']['final_rows'] = len(df)

        logger.info(f"Database created with {len(df)} records")

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        conn.close()

    return report


if __name__ == "__main__":
    db_path = Path(__file__).parent.parent / "data" / "energy.db"
    data_dir = Path(__file__).parent.parent / "data"
    report = create_database(str(db_path), str(data_dir))
    print(f"Created database with {report['tables']} tables")
