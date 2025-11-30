"""
Context Segmenter for ProfitLift

Segments transactions by context dimensions with auto-backoff for sparse data.
India-aware: Supports festival periods as a first-class context.
"""

import pandas as pd
from typing import Dict, List
from collections import defaultdict

from .context_types import Context


class ContextSegmenter:
    """Segments transactions by different context dimensions."""

    def __init__(self, min_rows: int = 100):
        """
        Initialize segmenter.

        Args:
            min_rows: Minimum rows per segment, auto-backoff to broader context if below
        """
        self.min_rows = min_rows

    def segment(self, transactions: pd.DataFrame, max_depth: int = 2) -> Dict[Context, pd.DataFrame]:
        """
        Segment transactions by context dimensions with auto-backoff.

        Args:
            transactions: DataFrame with transaction data including context columns
            max_depth: Maximum depth of context combinations (0=Overall, 1=Single, 2=Double)

        Returns:
            Dictionary mapping Context objects to filtered DataFrames
        """
        segments = {}

        # Level 0: Overall (always included)
        segments[Context()] = transactions

        if max_depth >= 1:
            # Level 1: Single dimensions
            self._add_single_dimension_segments(transactions, segments)

        if max_depth >= 2:
            # Level 2: Two-dimension combinations
            self._add_two_dimension_segments(transactions, segments)

        return segments

    def _add_single_dimension_segments(self, transactions: pd.DataFrame,
                                     segments: Dict[Context, pd.DataFrame]):
        """Add segments for single context dimensions."""

        # Store segments
        if 'store_id' in transactions.columns:
            for store in transactions['store_id'].unique():
                if pd.notna(store):
                    ctx = Context(store_id=str(store))
                    df = transactions[transactions['store_id'] == store]
                    if len(df) >= self.min_rows:
                        segments[ctx] = df

        # Time bin segments
        if 'context_time_bin' in transactions.columns:
            for time_bin in transactions['context_time_bin'].unique():
                if pd.notna(time_bin):
                    ctx = Context(time_bin=str(time_bin))
                    df = transactions[transactions['context_time_bin'] == time_bin]
                    if len(df) >= self.min_rows:
                        segments[ctx] = df

        # Weekday/Weekend segments
        if 'context_weekday_weekend' in transactions.columns:
            for weekday_type in transactions['context_weekday_weekend'].unique():
                if pd.notna(weekday_type):
                    ctx = Context(weekday_weekend=str(weekday_type))
                    df = transactions[transactions['context_weekday_weekend'] == weekday_type]
                    if len(df) >= self.min_rows:
                        segments[ctx] = df

        # Quarter segments
        if 'context_quarter' in transactions.columns:
            for quarter in transactions['context_quarter'].unique():
                if pd.notna(quarter):
                    ctx = Context(quarter=int(quarter))
                    df = transactions[transactions['context_quarter'] == quarter]
                    if len(df) >= self.min_rows:
                        segments[ctx] = df

        # Festival segments (India-specific, HIGH PRIORITY)
        if 'context_festival' in transactions.columns:
            for festival in transactions['context_festival'].unique():
                if pd.notna(festival) and festival:  # Non-empty festival
                    ctx = Context(festival_period=str(festival))
                    df = transactions[transactions['context_festival'] == festival]
                    # Lower threshold for festivals (they're important but short)
                    if len(df) >= max(self.min_rows // 2, 20):
                        segments[ctx] = df

    def _add_two_dimension_segments(self, transactions: pd.DataFrame,
                                  segments: Dict[Context, pd.DataFrame]):
        """Add segments for two-dimension combinations."""

        # Store × Time (key combination)
        if 'store_id' in transactions.columns and 'context_time_bin' in transactions.columns:
            for store in transactions['store_id'].unique():
                if pd.notna(store):
                    for time_bin in transactions['context_time_bin'].unique():
                        if pd.notna(time_bin):
                            ctx = Context(store_id=str(store), time_bin=str(time_bin))
                            df = transactions[
                                (transactions['store_id'] == store) &
                                (transactions['context_time_bin'] == time_bin)
                            ]
                            if len(df) >= self.min_rows:
                                segments[ctx] = df

        # Weekday/Weekend × Time
        if 'context_weekday_weekend' in transactions.columns and 'context_time_bin' in transactions.columns:
            for weekday_type in transactions['context_weekday_weekend'].unique():
                if pd.notna(weekday_type):
                    for time_bin in transactions['context_time_bin'].unique():
                        if pd.notna(time_bin):
                            ctx = Context(weekday_weekend=str(weekday_type), time_bin=str(time_bin))
                            df = transactions[
                                (transactions['context_weekday_weekend'] == weekday_type) &
                                (transactions['context_time_bin'] == time_bin)
                            ]
                            if len(df) >= self.min_rows:
                                segments[ctx] = df

        # Festival × Time (India-specific: e.g., "Diwali Morning")
        if 'context_festival' in transactions.columns and 'context_time_bin' in transactions.columns:
            for festival in transactions['context_festival'].unique():
                if pd.notna(festival) and festival:
                    for time_bin in transactions['context_time_bin'].unique():
                        if pd.notna(time_bin):
                            ctx = Context(festival_period=str(festival), time_bin=str(time_bin))
                            df = transactions[
                                (transactions['context_festival'] == festival) &
                                (transactions['context_time_bin'] == time_bin)
                            ]
                            # Lower threshold for festival combinations
                            if len(df) >= max(self.min_rows // 3, 15):
                                segments[ctx] = df

        # Store × Quarter
        if 'store_id' in transactions.columns and 'context_quarter' in transactions.columns:
            for store in transactions['store_id'].unique():
                if pd.notna(store):
                    for quarter in transactions['context_quarter'].unique():
                        if pd.notna(quarter):
                            ctx = Context(store_id=str(store), quarter=int(quarter))
                            df = transactions[
                                (transactions['store_id'] == store) &
                                (transactions['context_quarter'] == quarter)
                            ]
                            if len(df) >= self.min_rows:
                                segments[ctx] = df

    def get_segment_stats(self, segments: Dict[Context, pd.DataFrame]) -> pd.DataFrame:
        """Get statistics about created segments."""
        stats_data = []
        for context, df in segments.items():
            stats_data.append({
                'context': str(context),
                'transaction_count': len(df),
                'unique_stores': df['store_id'].nunique() if 'store_id' in df.columns else 0,
                'unique_customers': df['customer_id_hash'].nunique() if 'customer_id_hash' in df.columns else 0,
                'avg_basket_size': df.groupby('transaction_id').size().mean() if 'transaction_id' in df.columns else 0,
                'is_festival': 'Yes' if context.festival_period else 'No'
            })

        return pd.DataFrame(stats_data)
