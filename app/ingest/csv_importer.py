from pathlib import Path
from typing import NamedTuple, List, Optional, TYPE_CHECKING
from dataclasses import dataclass
import logging

from .context_enricher import add_context_columns
from ..assets.database import DatabaseManager

# Lazy import pandas to avoid hanging on module import
if TYPE_CHECKING:
    import pandas as pd
else:
    def _get_pandas():
        import pandas as pd
        return pd


@dataclass
class ImportResult:
    """Result of CSV import operation."""
    rows_imported: int
    rejected_rows: int
    errors: List[str]
    items_created: int
    transactions_created: int


class CSVImporter:
    """Import, validate, enrich CSV with context dimensions."""

    REQUIRED_COLS = ['transaction_id', 'timestamp', 'store_id', 'item_id', 'price']
    OPTIONAL_COLS = ['customer_id_hash', 'item_name', 'category', 'quantity',
                     'discount_flag', 'margin_pct']

    def __init__(self, db_path: str = "profitlift.db"):
        self.db = DatabaseManager(db_path)
        self.logger = logging.getLogger(__name__)

    def import_csv(self, filepath: str) -> ImportResult:
        """
        Import CSV and populate database.
        Returns: ImportResult with statistics and any errors.
        """
        errors = []
        rejected_rows = 0

        try:
            # 1. Load & validate required columns
            pd = _get_pandas()
            df = pd.read_csv(filepath)
            missing_cols = [col for col in self.REQUIRED_COLS if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # 2. Validate data types and ranges
            df, validation_errors = self._validate_data(df)
            errors.extend(validation_errors)
            rejected_rows += len(validation_errors)

            # 3. Enrich with context columns
            df = add_context_columns(df)

            # 4. Populate items table (upsert unique items)
            items_created = self._populate_items(df)

            # 5. Populate transactions & transaction_items
            transactions_created = self._populate_transactions(df)

            rows_imported = len(df) - rejected_rows

            return ImportResult(
                rows_imported=rows_imported,
                rejected_rows=rejected_rows,
                errors=errors,
                items_created=items_created,
                transactions_created=transactions_created
            )

        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return ImportResult(0, len(df) if 'df' in locals() else 0, [str(e)], 0, 0)

    def _validate_data(self, df: 'pd.DataFrame') -> tuple['pd.DataFrame', List[str]]:
        """Validate data and return clean df and errors."""
        pd = _get_pandas()
        errors = []
        original_len = len(df)

        # Remove rows with missing required values
        for col in self.REQUIRED_COLS:
            missing_mask = df[col].isna()
            if missing_mask.any():
                errors.append(f"Removed {missing_mask.sum()} rows with missing {col}")
                df = df[~missing_mask]

        # Validate price > 0
        invalid_price = df['price'] <= 0
        if invalid_price.any():
            errors.append(f"Removed {invalid_price.sum()} rows with invalid price")
            df = df[~invalid_price]

        # Validate quantity > 0 (default to 1 if missing)
        if 'quantity' not in df.columns:
            df['quantity'] = 1
        else:
            df['quantity'] = df['quantity'].fillna(1).astype(int)
            invalid_qty = df['quantity'] <= 0
            if invalid_qty.any():
                errors.append(f"Removed {invalid_qty.sum()} rows with invalid quantity")
                df = df[~invalid_qty]

        # Ensure discount_flag is 0/1
        if 'discount_flag' in df.columns:
            df['discount_flag'] = df['discount_flag'].fillna(0).astype(int)
        else:
            df['discount_flag'] = 0

        # Ensure margin_pct has defaults
        if 'margin_pct' not in df.columns:
            df['margin_pct'] = 0.25  # Default margin
        else:
            df['margin_pct'] = df['margin_pct'].fillna(0.25)

        return df, errors

    def _populate_items(self, df: 'pd.DataFrame') -> int:
        """Populate items table with unique items."""
        pd = _get_pandas()
        # Ensure optional item attributes exist before aggregation
        if 'item_name' not in df.columns:
            df['item_name'] = df['item_id']
        if 'category' not in df.columns:
            df['category'] = 'Unknown'

        # Calculate aggregate data per item
        item_data = df.groupby('item_id').agg({
            'item_name': 'first',
            'category': 'first',
            'price': 'mean',
            'margin_pct': 'first'
        }).reset_index()

        item_data.columns = ['item_id', 'item_name', 'category', 'avg_price', 'margin_pct']

        # Insert items
        items_created = 0
        for _, row in item_data.iterrows():
            try:
                self.db.execute_insert("""
                    INSERT OR REPLACE INTO items
                    (item_id, item_name, category, avg_price, margin_pct)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row['item_id'],
                    row['item_name'] if pd.notna(row['item_name']) else row['item_id'],
                    row['category'] if pd.notna(row['category']) else 'Unknown',
                    row['avg_price'],
                    row['margin_pct']
                ))
                items_created += 1
            except Exception as e:
                self.logger.warning(f"Failed to insert item {row['item_id']}: {e}")

        return items_created

    def _populate_transactions(self, df: 'pd.DataFrame') -> int:
        """Populate transactions and transaction_items tables."""
        pd = _get_pandas()
        # Get unique transactions
        transaction_cols = [
            'transaction_id', 'timestamp', 'store_id', 'customer_id_hash',
            'total_value', 'discount_flag', 'context_time_bin',
            'context_weekday_weekend', 'context_quarter'
        ]
        available_trans_cols = [col for col in transaction_cols if col in df.columns]

        transactions_df = df[available_trans_cols].drop_duplicates(subset=['transaction_id'])

        # Calculate total_value if not provided
        if 'total_value' not in transactions_df.columns:
            trans_totals = df.groupby('transaction_id')['price'].sum().reset_index()
            trans_totals.columns = ['transaction_id', 'total_value']
            transactions_df = transactions_df.merge(trans_totals, on='transaction_id', how='left')

        # Insert transactions
        transactions_created = 0
        for _, row in transactions_df.iterrows():
            try:
                self.db.execute_insert("""
                    INSERT OR REPLACE INTO transactions
                    (transaction_id, timestamp, store_id, customer_id_hash,
                     total_value, discount_flag, context_time_bin,
                     context_weekday_weekend, context_quarter)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['transaction_id'],
                    str(row['timestamp']),
                    row['store_id'],
                    row.get('customer_id_hash'),
                    row.get('total_value', 0),
                    row.get('discount_flag', 0),
                    row.get('context_time_bin'),
                    row.get('context_weekday_weekend'),
                    row.get('context_quarter')
                ))
                transactions_created += 1
            except Exception as e:
                self.logger.warning(f"Failed to insert transaction {row['transaction_id']}: {e}")

        # Insert transaction items
        transaction_item_cols = ['transaction_id', 'item_id', 'quantity', 'price']
        items_df = df[transaction_item_cols]

        items_data = []
        for _, row in items_df.iterrows():
            items_data.append((
                row['transaction_id'],
                row['item_id'],
                row['quantity'],
                row['price']
            ))

        if items_data:
            try:
                self.db.execute_many("""
                    INSERT INTO transaction_items
                    (transaction_id, item_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                """, items_data)
            except Exception as e:
                self.logger.error(f"Failed to insert transaction items: {e}")

        return transactions_created
