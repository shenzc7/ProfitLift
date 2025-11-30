from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd
from typing import List


class FPGrowthMiner:
    """FP-Growth implementation using mlxtend library."""

    def mine(self, transactions: List[List[str]], min_support: float) -> pd.DataFrame:
        """
        Mine frequent itemsets using FP-Growth.

        Args:
            transactions: List of transactions, each transaction is a list of item strings
            min_support: Minimum support threshold (0.0 to 1.0)

        Returns:
            DataFrame with frequent itemsets and their support values
        """
        # Convert transactions to basket matrix format
        basket = self._to_basket_matrix(transactions)

        # Mine frequent itemsets
        itemsets = fpgrowth(basket, min_support=min_support, use_colnames=True)

        return itemsets

    def generate_rules(self, itemsets: pd.DataFrame, min_confidence: float) -> pd.DataFrame:
        """
        Generate association rules from frequent itemsets.

        Args:
            itemsets: DataFrame with frequent itemsets (from mine method)
            min_confidence: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            DataFrame with association rules including support, confidence, and lift
        """
        if itemsets.empty:
            return pd.DataFrame(columns=['antecedents', 'consequents', 'support', 'confidence', 'lift'])

        # Generate association rules
        rules = association_rules(itemsets, metric="confidence", min_threshold=min_confidence)

        return rules

    def _to_basket_matrix(self, transactions: List[List[str]]) -> pd.DataFrame:
        """
        Convert transaction list to basket matrix format required by mlxtend.

        Args:
            transactions: List of transactions, each transaction is a list of item strings

        Returns:
            DataFrame where rows are transactions, columns are items, values are True/False (bool type)
        """
        from mlxtend.preprocessing import TransactionEncoder

        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        basket_df = pd.DataFrame(te_ary, columns=te.columns_)
        return basket_df
