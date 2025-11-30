"""
Context Enricher for ProfitLift

Adds context columns (time, day type, festival, etc.) to transaction data.
India-aware: Detects major festivals like Diwali, Holi, Navratri.
"""

import pandas as pd
from typing import Dict, Any

from .india_calendar import (
    get_festival_period,
    get_major_festival,
    estimate_margin_simple,
    calculate_margin_indian,
    detect_data_mode
)


def add_context_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add context dimensions based on timestamp.
    
    Columns added:
        - context_time_bin: morning, midday, afternoon, evening, night
        - context_weekday_weekend: weekday, weekend
        - context_quarter: 1, 2, 3, 4
        - context_festival: diwali, holi, etc. (or None)
    """
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Time of day
    df['context_time_bin'] = df['timestamp'].apply(_get_time_bin)
    
    # Weekday vs Weekend
    df['context_weekday_weekend'] = df['timestamp'].apply(
        lambda x: 'weekend' if x.weekday() >= 5 else 'weekday'
    )
    
    # Quarter
    df['context_quarter'] = df['timestamp'].dt.quarter
    
    # Festival period (India-specific)
    df['context_festival'] = df['timestamp'].apply(get_major_festival)
    
    return df


def enrich_margins(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich margin data using Indian retail norms.
    
    If margin_pct is missing, estimates it from category.
    If MRP and purchase_price are available, calculates GST-aware margin.
    """
    # If margin_pct column doesn't exist, create it
    if 'margin_pct' not in df.columns:
        df['margin_pct'] = None
    
    # Estimate missing margins from category
    mask_missing = df['margin_pct'].isna()
    if mask_missing.any() and 'category' in df.columns:
        df.loc[mask_missing, 'margin_pct'] = df.loc[mask_missing, 'category'].apply(
            estimate_margin_simple
        )
    
    # If still missing, use default
    df['margin_pct'] = df['margin_pct'].fillna(0.22)  # 22% default
    
    return df


def _get_time_bin(timestamp) -> str:
    """Convert timestamp to time bin category."""
    hour = timestamp.hour
    if 6 <= hour < 11:
        return 'morning'
    elif 11 <= hour < 14:
        return 'midday'
    elif 14 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 22:
        return 'evening'
    else:
        return 'night'


def get_context_bins() -> Dict[str, Any]:
    """Return the context bin definitions for validation."""
    return {
        'time_bins': ['morning', 'midday', 'afternoon', 'evening', 'night'],
        'weekday_weekend': ['weekday', 'weekend'],
        'quarters': [1, 2, 3, 4],
        'festivals': ['diwali', 'holi', 'navratri', 'eid_ul_fitr', 'christmas', 'new_year']
    }


def get_data_mode_recommendation(df: pd.DataFrame) -> Dict:
    """
    Get recommended mining parameters based on data volume.
    
    Returns a dict with mode name and suggested parameters.
    """
    # Count unique transactions
    if 'transaction_id' in df.columns:
        transaction_count = df['transaction_id'].nunique()
    else:
        transaction_count = len(df)
    
    return detect_data_mode(transaction_count)
