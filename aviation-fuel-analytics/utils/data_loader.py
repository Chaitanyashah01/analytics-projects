"""
Data loading and preprocessing utilities for Aviation Fuel Analytics.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st


class DataQualityReport:
    """Generate data quality reports."""

    def __init__(self, df: pd.DataFrame, name: str = 'dataset'):
        self.df = df
        self.name = name
        self.report = self._generate_report()

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive data quality report."""
        report = {
            'name': self.name,
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / 1024 / 1024,
            'duplicates': self.df.duplicated().sum(),
            'columns_info': {}
        }

        for col in self.df.columns:
            col_info = {
                'dtype': str(self.df[col].dtype),
                'non_null_count': self.df[col].count(),
                'null_count': self.df[col].isna().sum(),
                'null_pct': self.df[col].isna().mean() * 100,
                'unique_values': self.df[col].nunique()
            }

            if pd.api.types.is_numeric_dtype(self.df[col]):
                col_info.update({
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                    'mean': self.df[col].mean(),
                    'median': self.df[col].median()
                })

            report['columns_info'][col] = col_info

        return report

    def get_summary(self) -> pd.DataFrame:
        """Get summary dataframe."""
        rows = []
        for col, info in self.report['columns_info'].items():
            rows.append({
                'Column': col,
                'Type': info['dtype'],
                'Non-Null': info['non_null_count'],
                'Null %': f"{info['null_pct']:.1f}%",
                'Unique': info['unique_values']
            })
        return pd.DataFrame(rows)

    def get_quality_score(self) -> float:
        """Calculate overall data quality score (0-100)."""
        scores = []

        # Completeness score (no nulls = 100)
        null_pcts = [info['null_pct'] for info in self.report['columns_info'].values()]
        completeness = 100 - np.mean(null_pcts)
        scores.append(completeness)

        # Uniqueness score (no duplicates = 100)
        uniqueness = 100 - (self.report['duplicates'] / max(self.report['rows'], 1) * 100)
        scores.append(uniqueness)

        return np.mean(scores)


def get_data_path() -> Path:
    """Get the data directory path."""
    return Path(__file__).parent.parent / "data"


def ensure_database_exists() -> bool:
    """Ensure database is initialized."""
    db_path = get_data_path() / "aviation.db"

    if not db_path.exists():
        from database.init_db import create_database
        create_database(str(db_path), str(get_data_path()))

    return db_path.exists()


@st.cache_data(ttl=3600)
def load_csv_with_quality_report(filename: str) -> tuple:
    """Load CSV file and return dataframe with quality report."""
    filepath = get_data_path() / filename
    df = pd.read_csv(filepath)
    report = DataQualityReport(df, filename)
    return df, report


def format_large_number(num: float, decimals: int = 1) -> str:
    """Format large numbers for display."""
    if abs(num) >= 1e9:
        return f"{num/1e9:.{decimals}f}B"
    elif abs(num) >= 1e6:
        return f"{num/1e6:.{decimals}f}M"
    elif abs(num) >= 1e3:
        return f"{num/1e3:.{decimals}f}K"
    return f"{num:.{decimals}f}"


def create_date_filters(df: pd.DataFrame, date_col: str) -> tuple:
    """Create date range filter widgets."""
    df[date_col] = pd.to_datetime(df[date_col])
    min_date = df[date_col].min()
    max_date = df[date_col].max()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    return pd.Timestamp(start_date), pd.Timestamp(end_date)


def apply_filters(
    df: pd.DataFrame,
    filters: Dict[str, Any]
) -> pd.DataFrame:
    """Apply multiple filters to dataframe."""
    filtered_df = df.copy()

    for col, values in filters.items():
        if values and col in filtered_df.columns:
            if isinstance(values, list):
                filtered_df = filtered_df[filtered_df[col].isin(values)]
            elif isinstance(values, tuple) and len(values) == 2:
                # Date range
                filtered_df = filtered_df[
                    (filtered_df[col] >= values[0]) &
                    (filtered_df[col] <= values[1])
                ]
            else:
                filtered_df = filtered_df[filtered_df[col] == values]

    return filtered_df
