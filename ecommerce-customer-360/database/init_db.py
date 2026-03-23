"""
Database initialization for E-Commerce Customer 360.
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
        csv_path = data_dir / 'e_commerce_shopper_behaviour_and_lifestyle.csv'
        logger.info(f"Loading {csv_path}...")

        # Read in chunks for large file
        df = pd.read_csv(csv_path)

        report['cleaning']['original_rows'] = len(df)

        # Clean column names
        df.columns = [c.lower().replace(' ', '_') for c in df.columns]

        # Convert boolean-like columns
        bool_cols = ['has_children', 'loyalty_program_member', 'weekend_shopper', 'premium_subscription']
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(bool).astype(int)

        # Create age groups
        df['age_group'] = pd.cut(
            df['age'],
            bins=[0, 25, 35, 45, 55, 65, 100],
            labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        )

        # Create income segments
        df['income_segment'] = pd.cut(
            df['income_level'],
            bins=[0, 30000, 60000, 100000, 150000, float('inf')],
            labels=['Low', 'Lower-Middle', 'Middle', 'Upper-Middle', 'High']
        )

        # Create spend segments
        df['spend_segment'] = pd.cut(
            df['monthly_spend'],
            bins=[0, 500, 1500, 3000, 5000, float('inf')],
            labels=['Low', 'Medium', 'High', 'Very High', 'Premium']
        )

        # Create engagement score
        df['engagement_score'] = (
            (df['daily_session_time_minutes'] / df['daily_session_time_minutes'].max()) * 25 +
            (df['product_views_per_day'] / df['product_views_per_day'].max()) * 25 +
            (df['app_usage_frequency'] / 10) * 25 +
            (df['notification_response_rate'] / 100) * 25
        )

        # Create customer value score (simplified RFM)
        df['customer_value_score'] = (
            (df['monthly_spend'] / df['monthly_spend'].max()) * 40 +
            (df['weekly_purchases'] / df['weekly_purchases'].max()) * 30 +
            (1 - df['cart_abandonment_rate'] / 100) * 30
        )

        # Create loyalty segment
        df['loyalty_segment'] = pd.cut(
            df['customer_value_score'],
            bins=[0, 20, 40, 60, 80, 100],
            labels=['At Risk', 'Occasional', 'Regular', 'Loyal', 'Champion']
        )

        # Remove duplicates
        original_len = len(df)
        df = df.drop_duplicates(subset=['user_id'])
        report['cleaning']['duplicates_removed'] = original_len - len(df)

        # Sample for faster loading if too large
        if len(df) > 500000:
            df = df.sample(n=500000, random_state=42)
            report['cleaning']['sampled'] = True

        # Save to database
        df.to_sql('customers', conn, index=False, if_exists='replace')
        report['tables']['customers'] = len(df)

        # Create summary views
        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_demographic_summary AS
            SELECT
                age_group,
                gender,
                income_segment,
                COUNT(*) as customer_count,
                AVG(monthly_spend) as avg_spend,
                AVG(weekly_purchases) as avg_purchases,
                AVG(cart_abandonment_rate) as avg_abandonment
            FROM customers
            GROUP BY age_group, gender, income_segment
        """)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_country_summary AS
            SELECT
                country,
                COUNT(*) as customer_count,
                AVG(monthly_spend) as avg_spend,
                SUM(monthly_spend) as total_spend,
                AVG(customer_value_score) as avg_value_score
            FROM customers
            GROUP BY country
        """)

        conn.execute("""
            CREATE VIEW IF NOT EXISTS v_segment_summary AS
            SELECT
                loyalty_segment,
                COUNT(*) as customer_count,
                AVG(monthly_spend) as avg_spend,
                AVG(weekly_purchases) as avg_purchases,
                AVG(average_order_value) as avg_aov,
                AVG(cart_abandonment_rate) as avg_abandonment
            FROM customers
            GROUP BY loyalty_segment
        """)

        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_country ON customers(country)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_segment ON customers(loyalty_segment)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_age ON customers(age_group)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_customers_gender ON customers(gender)")

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
    db_path = Path(__file__).parent.parent / "data" / "ecommerce.db"
    data_dir = Path(__file__).parent.parent / "data"
    report = create_database(str(db_path), str(data_dir))
    print(f"Created database with {report['tables']} tables")
