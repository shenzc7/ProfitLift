import pandas as pd
from typing import Optional
import logging

from ..mining.context_types import ContextualRule


class ProfitCalculator:
    """Calculates expected incremental profit for association rules."""

    def __init__(self, default_margin_pct: float = 0.25):
        """
        Initialize profit calculator.

        Args:
            default_margin_pct: Default profit margin percentage if not available
        """
        self.default_margin_pct = default_margin_pct
        self.logger = logging.getLogger(__name__)

    def calculate_rule_profit(self, rule: ContextualRule,
                             transactions: pd.DataFrame) -> float:
        """
        Calculate expected incremental profit per basket for a rule.

        Formula: E[profit] = Avg(consequent_price) × Margin% × Confidence

        Args:
            rule: The association rule to evaluate
            transactions: Transaction data with price and margin information

        Returns:
            Expected incremental profit per basket
        """
        try:
            # Get items in consequent
            consequent_items = list(rule.consequent)

            # Filter transactions to those containing consequent items
            consequent_data = transactions[transactions['item_id'].isin(consequent_items)]

            if consequent_data.empty:
                self.logger.warning(f"No transaction data found for consequent items: {consequent_items}")
                return 0.0

            # Calculate average price of consequent items
            avg_price = consequent_data['price'].mean()

            # Get average margin percentage
            avg_margin = self._get_margin(consequent_data)

            # Calculate expected incremental profit
            # This is the expected profit from the additional items sold due to the rule
            profit = avg_price * avg_margin * rule.confidence

            return profit

        except Exception as e:
            self.logger.error(f"Error calculating profit for rule {rule}: {e}")
            return 0.0

    def _get_margin(self, item_data: pd.DataFrame) -> float:
        """
        Calculate average margin percentage from item data.

        Args:
            item_data: DataFrame with margin_pct column

        Returns:
            Average margin percentage
        """
        if 'margin_pct' not in item_data.columns:
            return self.default_margin_pct

        # Get margin values, fill missing with default
        margins = item_data['margin_pct'].fillna(self.default_margin_pct)

        # Return average margin
        return margins.mean()

    def get_category_margins(self, transactions: pd.DataFrame) -> dict:
        """
        Extract category-based margin information from transaction data.

        Args:
            transactions: Transaction data with item categories

        Returns:
            Dictionary mapping categories to average margins
        """
        if 'category' not in transactions.columns or 'margin_pct' not in transactions.columns:
            return {}

        # Group by category and calculate average margin
        category_margins = transactions.groupby('category')['margin_pct'].mean().to_dict()

        return category_margins
