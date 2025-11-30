import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
import logging

from ..mining.context_types import ContextualRule


class TreatmentSimulator:
    """Simulate control/treatment groups from historical data for causal inference."""

    def __init__(self, random_state: int = 42):
        """
        Initialize treatment simulator.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.logger = logging.getLogger(__name__)

    def simulate_experiment(self, transactions: pd.DataFrame,
                           rule: ContextualRule) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Simulate A/B test for a given rule.

        - Find transactions with antecedent items (treatment group)
        - Randomly split similar transactions without antecedent (control group)
        - Outcome = did they buy consequent items

        Args:
            transactions: Transaction data
            rule: Association rule to test

        Returns:
            Tuple of (control_features, treatment_features) DataFrames
        """
        try:
            transactions = transactions.copy()
            # Normalize discount flag for downstream grouping logic
            if 'discount_flag' not in transactions.columns:
                if 'has_discount' in transactions.columns:
                    transactions['discount_flag'] = transactions['has_discount']
                else:
                    transactions['discount_flag'] = 0

            # Find transactions with antecedent items
            antecedent_items = list(rule.antecedent)
            trans_with_antecedent = self._find_transactions_with_items(
                transactions, antecedent_items
            )

            if len(trans_with_antecedent) < 10:
                self.logger.warning(f"Insufficient data for rule {rule}: only {len(trans_with_antecedent)} transactions with antecedent")
                # Return minimal dataframes to avoid errors
                empty_df = pd.DataFrame(columns=['outcome', 'basket_size', 'avg_price', 'has_discount', 'hour'])
                return empty_df.copy(), empty_df.copy()

            # Split treatment group randomly (some get "treatment", some don't)
            # In reality, we'd use historical promotion data, but here we simulate
            treatment_group, control_from_treatment = self._split_treatment_group(
                trans_with_antecedent, rule
            )

            # Create control group: transactions without antecedent but similar characteristics
            control_transactions = self._create_control_group(
                transactions, trans_with_antecedent, antecedent_items
            )

            # If we cannot find external control, fall back to holdout slice from treatment
            if control_transactions.empty:
                self.logger.warning(f"Insufficient control data for rule {rule}, falling back to treatment holdout")
                all_control = control_from_treatment.copy()
            else:
                all_control = pd.concat([control_transactions, control_from_treatment])

            if len(all_control) < 3 or len(treatment_group) < 3:
                self.logger.warning(f"Not enough samples after control/treatment split for rule {rule}")
                empty_df = pd.DataFrame(columns=['outcome', 'basket_size', 'avg_price', 'has_discount', 'hour'])
                return empty_df.copy(), empty_df.copy()

            # Extract features and outcomes
            control_features = self._extract_features(all_control, rule)
            treatment_features = self._extract_features(treatment_group, rule)

            return control_features, treatment_features

        except Exception as e:
            self.logger.error(f"Error simulating experiment for rule {rule}: {e}")
            # Return empty dataframes on error
            empty_df = pd.DataFrame(columns=['outcome', 'basket_size', 'avg_price', 'has_discount', 'hour'])
            return empty_df.copy(), empty_df.copy()

    def _find_transactions_with_items(self, transactions: pd.DataFrame,
                                     items: List[str]) -> pd.DataFrame:
        """Find transactions containing specific items."""
        # Get transaction IDs that contain any of the items
        matching_trans = transactions[transactions['item_id'].isin(items)]['transaction_id'].unique()

        # Get all items from those transactions
        trans_with_items = transactions[transactions['transaction_id'].isin(matching_trans)]

        return trans_with_items

    def _create_control_group(self, all_transactions: pd.DataFrame,
                             treatment_transactions: pd.DataFrame,
                             antecedent_items: List[str],
                             n_control: Optional[int] = None) -> pd.DataFrame:
        """
        Create control group by finding similar transactions without antecedent items.
        """
        # Get transaction IDs from treatment group
        treatment_ids = treatment_transactions['transaction_id'].unique()

        # Find transactions that don't contain antecedent items
        transactions_without_antecedent = all_transactions[
            ~all_transactions['transaction_id'].isin(treatment_ids)
        ].copy()

        discount_col = None
        if 'discount_flag' in transactions_without_antecedent.columns:
            discount_col = 'discount_flag'
        elif 'has_discount' in transactions_without_antecedent.columns:
            discount_col = 'has_discount'

        treatment_discount_col = None
        if 'discount_flag' in treatment_transactions.columns:
            treatment_discount_col = 'discount_flag'
        elif 'has_discount' in treatment_transactions.columns:
            treatment_discount_col = 'has_discount'

        treatment_transactions = treatment_transactions.copy()

        # Normalize discount into a single proxy column for grouping
        if discount_col:
            transactions_without_antecedent['__discount_proxy'] = transactions_without_antecedent[discount_col]
        else:
            transactions_without_antecedent['__discount_proxy'] = 0

        if treatment_discount_col:
            treatment_transactions['__discount_proxy'] = treatment_transactions[treatment_discount_col]
        else:
            treatment_transactions['__discount_proxy'] = 0

        # Group by transaction to get transaction-level info
        trans_summary = transactions_without_antecedent.groupby('transaction_id').agg({
            'item_id': 'count',  # basket size
            'price': 'mean',     # avg price
            '__discount_proxy': 'max'
        }).reset_index()

        # Match similar transactions (similar basket size, similar time if available)
        treatment_summary = treatment_transactions.groupby('transaction_id').agg({
            'item_id': 'count',
            'price': 'mean',
            '__discount_proxy': 'max' if '__discount_proxy' in treatment_transactions.columns else 'size'
        }).reset_index()

        # Simple matching: similar basket size
        avg_basket_size = treatment_summary['item_id'].mean()
        size_tolerance = max(1, avg_basket_size * 0.5)  # ±50% tolerance

        matched_control = trans_summary[
            (trans_summary['item_id'] >= avg_basket_size - size_tolerance) &
            (trans_summary['item_id'] <= avg_basket_size + size_tolerance)
        ]

        # Limit control group size
        if n_control and len(matched_control) > n_control:
            matched_control = matched_control.sample(n=n_control, random_state=self.random_state)

        # Get full transaction details for matched control transactions
        control_transactions = all_transactions[
            all_transactions['transaction_id'].isin(matched_control['transaction_id'])
        ]

        return control_transactions

    def _split_treatment_group(self, treatment_transactions: pd.DataFrame,
                              rule: ContextualRule) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split treatment transactions into actual treatment and additional control.
        In practice, this would use historical promotion data.
        """
        # For simulation, randomly split 70/30
        trans_ids = treatment_transactions['transaction_id'].unique()
        np.random.seed(self.random_state)

        # Shuffle and split
        np.random.shuffle(trans_ids)
        split_idx = int(len(trans_ids) * 0.7)

        treatment_ids = trans_ids[:split_idx]
        control_ids = trans_ids[split_idx:]

        treatment_group = treatment_transactions[
            treatment_transactions['transaction_id'].isin(treatment_ids)
        ]
        control_from_treatment = treatment_transactions[
            treatment_transactions['transaction_id'].isin(control_ids)
        ]

        return treatment_group, control_from_treatment

    def _extract_features(self, transactions: pd.DataFrame,
                         rule: ContextualRule) -> pd.DataFrame:
        """
        Extract features and outcome for causal modeling.

        Features: basket_size, avg_price, has_discount, hour
        Outcome: whether transaction contains consequent items
        """
        consequent_items = list(rule.consequent)

        # Group by transaction
        agg_dict = {
            'item_id': ['count', lambda x: any(item in consequent_items for item in x)],  # basket_size, has_consequent
            'price': 'mean',      # avg_price
        }

        discount_col = None
        if 'discount_flag' in transactions.columns:
            discount_col = 'discount_flag'
        elif 'has_discount' in transactions.columns:
            discount_col = 'has_discount'

        if discount_col:
            agg_dict[discount_col] = 'max'

        trans_features = transactions.groupby('transaction_id').agg(agg_dict).reset_index()

        # Flatten column names
        if discount_col:
            trans_features.columns = ['transaction_id', 'basket_size', 'outcome', 'avg_price', 'has_discount']
        else:
            trans_features.columns = ['transaction_id', 'basket_size', 'outcome', 'avg_price']
            trans_features['has_discount'] = 0  # Default no discount

        # Add time-based features if available
        if 'timestamp' in transactions.columns:
            time_features = transactions.groupby('transaction_id')['timestamp'].first().reset_index()
            time_features['timestamp'] = pd.to_datetime(time_features['timestamp'])
            time_features['hour'] = time_features['timestamp'].dt.hour
            trans_features = trans_features.merge(time_features[['transaction_id', 'hour']], on='transaction_id')
        else:
            trans_features['hour'] = 12  # Default midday

        return trans_features
