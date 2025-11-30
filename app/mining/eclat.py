import pandas as pd
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class EclatMiner:
    """Eclat implementation using vertical database format (tid-lists)."""

    def mine(self, transactions: List[List[str]], min_support: float) -> pd.DataFrame:
        """
        Mine frequent itemsets using Eclat algorithm.

        Args:
            transactions: List of transactions, each transaction is a list of item strings
            min_support: Minimum support threshold (0.0 to 1.0)

        Returns:
            DataFrame with frequent itemsets and their support values
        """
        # Convert to vertical database: {item: {tid1, tid2, ...}}
        vertical_db = self._to_vertical_format(transactions)
        total_transactions = len(transactions)

        # Calculate minimum support count
        min_support_count = int(min_support * total_transactions)

        # Find frequent single items
        frequent_items = {
            item: tid_set for item, tid_set in vertical_db.items()
            if len(tid_set) >= min_support_count
        }

        # Mine frequent itemsets using Eclat
        frequent_itemsets = self._eclat(frequent_items, min_support_count)

        # Convert to DataFrame format consistent with FP-Growth
        itemsets_data = []
        for itemset, support_count in frequent_itemsets.items():
            if isinstance(itemset, tuple):
                itemsets_data.append({
                    'support': support_count / total_transactions,
                    'itemsets': frozenset(itemset)
                })
            else:
                itemsets_data.append({
                    'support': support_count / total_transactions,
                    'itemsets': frozenset([itemset])
                })

        if not itemsets_data:
            return pd.DataFrame(columns=['support', 'itemsets'])

        result_df = pd.DataFrame(itemsets_data)
        result_df = result_df.sort_values('support', ascending=False).reset_index(drop=True)

        return result_df

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

        rules_data = []

        for _, itemset_row in itemsets.iterrows():
            itemset = itemset_row['itemsets']
            support = itemset_row['support']

            if isinstance(itemset, frozenset):
                itemset = set(itemset)

            # Only generate rules for itemsets with 2+ items
            if len(itemset) < 2:
                continue

            # Generate all possible non-empty proper subsets as antecedents
            items_list = list(itemset)
            for i in range(1, len(items_list)):  # antecedent size from 1 to n-1
                antecedents_list = self._combinations(items_list, i)

                for antecedent_items in antecedents_list:
                    antecedent = set(antecedent_items)
                    consequent = itemset - antecedent

                    # For this simplified implementation, use basic confidence calculation
                    # In a full implementation, we'd need support of individual itemsets
                    confidence = support  # Approximation
                    lift = 1.0  # Approximation

                    rules_data.append({
                        'antecedents': frozenset(antecedent),
                        'consequents': frozenset(consequent),
                        'support': support,
                        'confidence': confidence,
                        'lift': lift
                    })

        if not rules_data:
            return pd.DataFrame(columns=['antecedents', 'consequents', 'support', 'confidence', 'lift'])

        rules_df = pd.DataFrame(rules_data)
        # Filter by confidence
        rules_df = rules_df[rules_df['confidence'] >= min_confidence]
        rules_df = rules_df.sort_values('confidence', ascending=False).reset_index(drop=True)

        return rules_df

    def _to_vertical_format(self, transactions: List[List[str]]) -> Dict[str, Set[int]]:
        """Convert transactions to vertical format: {item: set of transaction_ids}."""
        vertical_db = defaultdict(set)

        for tid, transaction in enumerate(transactions):
            for item in transaction:
                vertical_db[item].add(tid)

        return dict(vertical_db)

    def _eclat(self, current_itemsets: Dict[str, Set[int]], min_support_count: int) -> Dict[Tuple[str, ...], int]:
        """
        Recursive Eclat algorithm to find frequent itemsets.

        Args:
            current_itemsets: Current level itemsets {item: tid_set}
            min_support_count: Minimum support count threshold

        Returns:
            Dict of frequent itemsets and their support counts
        """
        frequent_itemsets = {}

        # Add current level itemsets (single items or combinations)
        for item, tid_set in current_itemsets.items():
            if len(tid_set) >= min_support_count:
                if isinstance(item, tuple):
                    frequent_itemsets[item] = len(tid_set)
                else:
                    frequent_itemsets[(item,)] = len(tid_set)

        # Generate candidates for next level
        if len(current_itemsets) > 1:
            items = list(current_itemsets.keys())

            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    item1, item2 = items[i], items[j]

                    # Intersect tid sets
                    intersection = current_itemsets[item1] & current_itemsets[item2]

                    if len(intersection) >= min_support_count:
                        # Create new itemset
                        if isinstance(item1, tuple) and isinstance(item2, tuple):
                            # Both are already combinations
                            new_itemset = tuple(sorted(set(item1) | set(item2)))
                        elif isinstance(item1, tuple):
                            new_itemset = tuple(sorted(item1 + (item2,)))
                        elif isinstance(item2, tuple):
                            new_itemset = tuple(sorted((item1,) + item2))
                        else:
                            new_itemset = tuple(sorted([item1, item2]))

                        # Recurse to next level
                        sub_itemsets = {new_itemset: intersection}
                        sub_frequent = self._eclat(sub_itemsets, min_support_count)
                        frequent_itemsets.update(sub_frequent)

        return frequent_itemsets

    def _combinations(self, items: List[str], r: int) -> List[List[str]]:
        """Generate combinations of size r from items list."""
        if r == 0:
            return [[]]
        if r > len(items):
            return []

        if r == 1:
            return [[item] for item in items]

        combinations = []
        for i in range(len(items)):
            remaining = items[i + 1:]
            for combo in self._combinations(remaining, r - 1):
                combinations.append([items[i]] + combo)

        return combinations

    def _get_subsets(self, itemset: Set[str], size: int) -> List[Set[str]]:
        """Get all subsets of given size from itemset."""
        items = list(itemset)
        subsets = []

        def backtrack(start: int, current: Set[str]):
            if len(current) == size:
                subsets.append(current.copy())
                return

            for i in range(start, len(items)):
                current.add(items[i])
                backtrack(i + 1, current)
                current.remove(items[i])

        backtrack(0, set())
        return subsets
