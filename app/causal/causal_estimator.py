import pandas as pd
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass
import logging

from .t_learner import TLearner
from .treatment_simulator import TreatmentSimulator
from ..mining.context_types import ContextualRule


@dataclass
class UpliftResult:
    """Result of causal uplift estimation."""
    incremental_attach_rate: float
    incremental_revenue: float
    incremental_margin: float
    control_rate: float
    treatment_rate: float
    confidence_interval: Optional[Tuple[float, float]] = None
    sample_size: int = 0


class CausalEstimator:
    """Estimates causal uplift effects using T-Learner."""

    def __init__(self, min_incremental_lift: float = 0.05):
        """
        Initialize causal estimator.

        Args:
            min_incremental_lift: Minimum incremental lift to consider significant
        """
        self.t_learner = TLearner()
        self.simulator = TreatmentSimulator()
        self.min_incremental_lift = min_incremental_lift
        self.logger = logging.getLogger(__name__)

    def estimate_uplift(self, rule: ContextualRule,
                       transactions: pd.DataFrame) -> UpliftResult:
        """
        Estimate true causal effect using T-Learner.

        Returns: incremental attach rate, revenue, margin.

        Args:
            rule: Association rule to evaluate
            transactions: Transaction data

        Returns:
            UpliftResult with causal estimates
        """
        try:
            # Simulate experiment
            control_df, treatment_df = self.simulator.simulate_experiment(transactions, rule)

            if len(control_df) < 3 or len(treatment_df) < 3:
                self.logger.debug(f"Insufficient data for causal estimation of rule {rule}: control={len(control_df)}, treatment={len(treatment_df)}")
                return UpliftResult(0.0, 0.0, 0.0, 0.0, 0.0, sample_size=len(control_df) + len(treatment_df))

            # Prepare features and outcomes
            feature_cols = ['basket_size', 'avg_price', 'has_discount', 'hour']

            # Ensure all required columns exist
            for col in feature_cols + ['outcome']:
                if col not in control_df.columns:
                    control_df[col] = 0
                if col not in treatment_df.columns:
                    treatment_df[col] = 0

            X_control = control_df[feature_cols].values
            y_control = control_df['outcome'].values
            X_treatment = treatment_df[feature_cols].values
            y_treatment = treatment_df['outcome'].values

            # Train T-Learner
            self.t_learner.fit(X_control, y_control, X_treatment, y_treatment)

            # Calculate basic metrics
            control_rate = y_control.mean()
            treatment_rate = y_treatment.mean()
            incremental_attach_rate = treatment_rate - control_rate

            # Only consider significant positive effects
            if incremental_attach_rate < self.min_incremental_lift:
                self.logger.debug(f"Incremental lift {incremental_attach_rate:.3f} below threshold {self.min_incremental_lift}")
                return UpliftResult(0.0, 0.0, 0.0, control_rate, treatment_rate,
                                  sample_size=len(control_df) + len(treatment_df))

            # Estimate revenue and margin impact
            consequent_items = list(rule.consequent)

            # Get average price and margin for consequent items
            consequent_data = transactions[transactions['item_id'].isin(consequent_items)]
            if consequent_data.empty:
                avg_price = 0.0
                avg_margin_pct = 0.25
            else:
                avg_price = consequent_data['price'].mean()
                avg_margin_pct = consequent_data['margin_pct'].mean() if 'margin_pct' in consequent_data.columns else 0.25

            incremental_revenue = incremental_attach_rate * avg_price
            incremental_margin = incremental_revenue * avg_margin_pct

            # Calculate confidence interval (simplified bootstrap)
            ci_lower, ci_upper = self._calculate_confidence_interval(
                y_control, y_treatment, n_bootstrap=20
            )

            result = UpliftResult(
                incremental_attach_rate=incremental_attach_rate,
                incremental_revenue=incremental_revenue,
                incremental_margin=incremental_margin,
                control_rate=control_rate,
                treatment_rate=treatment_rate,
                confidence_interval=(ci_lower, ci_upper),
                sample_size=len(control_df) + len(treatment_df)
            )

            self.logger.debug(f"Causal estimation for {rule}: uplift={incremental_attach_rate:.3f}")
            return result

        except Exception as e:
            self.logger.error(f"Error in causal estimation for rule {rule}: {e}")
            return UpliftResult(0.0, 0.0, 0.0, 0.0, 0.0, sample_size=0)

    def _calculate_confidence_interval(self, y_control: np.ndarray,
                                     y_treatment: np.ndarray,
                                     n_bootstrap: int = 20,
                                     confidence_level: float = 0.95) -> Tuple[float, float]:
        """
        Calculate confidence interval using bootstrap.

        Args:
            y_control: Control group outcomes
            y_treatment: Treatment group outcomes
            n_bootstrap: Number of bootstrap samples
            confidence_level: Confidence level (0-1)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        try:
            uplifts = []
            n_control = len(y_control)
            n_treatment = len(y_treatment)

            np.random.seed(42)  # For reproducibility

            for _ in range(n_bootstrap):
                # Bootstrap control group
                control_sample = np.random.choice(y_control, size=n_control, replace=True)
                # Bootstrap treatment group
                treatment_sample = np.random.choice(y_treatment, size=n_treatment, replace=True)

                uplift = treatment_sample.mean() - control_sample.mean()
                uplifts.append(uplift)

            uplifts = np.array(uplifts)
            alpha = 1 - confidence_level
            lower = np.percentile(uplifts, alpha/2 * 100)
            upper = np.percentile(uplifts, (1 - alpha/2) * 100)

            return float(lower), float(upper)

        except Exception as e:
            self.logger.warning(f"Error calculating confidence interval: {e}")
            return 0.0, 0.0
