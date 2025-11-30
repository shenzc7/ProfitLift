import pandas as pd
from typing import List, Dict
import logging

from .context_segmenter import ContextSegmenter
from .context_types import Context, ContextualRule
from .fpgrowth import FPGrowthMiner


class ContextAwareMiner:
    """Mines association rules within different context segments."""

    def __init__(self, min_support: float = 0.01, min_confidence: float = 0.3,
                 min_rows_per_context: int = 100):
        """
        Initialize context-aware miner.

        Args:
            min_support: Minimum support threshold for mining
            min_confidence: Minimum confidence threshold for rules
            min_rows_per_context: Minimum rows per context segment
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.segmenter = ContextSegmenter(min_rows=min_rows_per_context)
        self.fp_growth = FPGrowthMiner()
        self.logger = logging.getLogger(__name__)

    def mine_all_contexts(self, transactions: pd.DataFrame, max_depth: int = 2) -> List[ContextualRule]:
        """
        Mine association rules across all context segments.

        Args:
            transactions: DataFrame with transaction data

        Returns:
            List of ContextualRule objects with context metadata
        """
        # Segment transactions by context
        segments = self.segmenter.segment(transactions, max_depth=max_depth)
        self.logger.info(f"Created {len(segments)} context segments")

        all_rules = []

        for context, segment_df in segments.items():
            self.logger.debug(f"Mining context: {context} ({len(segment_df)} transactions)")

            # Convert segment to transaction list
            trans_list = self._df_to_transactions(segment_df)

            if len(trans_list) < 5:  # Skip segments with too few transactions
                self.logger.debug(f"Skipping context {context}: only {len(trans_list)} transactions")
                continue

            try:
                # Mine frequent itemsets
                itemsets = self.fp_growth.mine(trans_list, min_support=self.min_support)

                if itemsets.empty:
                    self.logger.debug(f"No frequent itemsets found for context {context}")
                    continue

                # Generate association rules
                rules_df = self.fp_growth.generate_rules(itemsets, min_confidence=self.min_confidence)

                if rules_df.empty:
                    self.logger.debug(f"No association rules found for context {context}")
                    continue

                # Convert to ContextualRule objects
                for _, rule in rules_df.iterrows():
                    contextual_rule = ContextualRule(
                        antecedent=frozenset(rule['antecedents']),
                        consequent=frozenset(rule['consequents']),
                        support=rule['support'],
                        confidence=rule['confidence'],
                        lift=rule['lift'],
                        context=context
                    )
                    all_rules.append(contextual_rule)

                self.logger.debug(f"Found {len(rules_df)} rules for context {context}")

            except Exception as e:
                self.logger.warning(f"Error mining context {context}: {e}")
                continue

        self.logger.info(f"Total rules found across all contexts: {len(all_rules)}")
        return all_rules

    def _df_to_transactions(self, df: pd.DataFrame) -> List[List[str]]:
        """
        Convert DataFrame segment to list of transactions.

        Args:
            df: DataFrame with transaction_id and item_id columns

        Returns:
            List of transactions, each transaction is a list of item strings
        """
        transactions = []

        # Group by transaction_id and collect items
        grouped = df.groupby('transaction_id')['item_id'].apply(list)

        for transaction_items in grouped:
            # Convert items to strings and filter out any NaN values
            clean_items = [str(item) for item in transaction_items if pd.notna(item)]
            if clean_items:  # Only add non-empty transactions
                transactions.append(clean_items)

        return transactions

    def get_context_stats(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """Get statistics about context segments."""
        segments = self.segmenter.segment(transactions)
        return self.segmenter.get_segment_stats(segments)
