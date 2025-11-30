from typing import List, Dict, Optional
import logging
import pandas as pd

from .profit_calculator import ProfitCalculator
from .diversity_scorer import DiversityScorer
from ..mining.context_types import ContextualRule


class MultiObjectiveScorer:
    """Scores rules using multiple objectives with per-context normalization."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize multi-objective scorer.

        Args:
            weights: Weights for different scoring components (lift, profit_margin, diversity, confidence)
        """
        self.weights = weights or {
            'lift': 0.30,
            'profit_margin': 0.40,
            'diversity': 0.15,
            'confidence': 0.15
        }

        self.profit_calc = ProfitCalculator()
        self.diversity_scorer = DiversityScorer()
        self.logger = logging.getLogger(__name__)

        # Validate weights sum to 1
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.001:
            self.logger.warning(f"Weights don't sum to 1.0: {total_weight}")

    def score_rules(self, rules: List[ContextualRule],
                   transactions: pd.DataFrame) -> List[ContextualRule]:
        """
        Score rules WITHIN each context separately using multi-objective scoring.

        Overall_score = w_lift*norm(lift) + w_profit*norm(profit) + w_diversity*diversity + w_confidence*confidence

        Args:
            rules: List of contextual rules to score
            transactions: Transaction data for profit calculations

        Returns:
            Same rules list with profit_score, diversity_score, and overall_score populated
        """
        # Group rules by context
        context_groups = {}
        for rule in rules:
            ctx = rule.context
            ctx_key = str(ctx)  # Use string representation as key
            if ctx_key not in context_groups:
                context_groups[ctx_key] = []
            context_groups[ctx_key].append(rule)

        self.logger.info(f"Scoring rules across {len(context_groups)} contexts")

        scored_rules = []

        # Score each context group separately
        for ctx_key, ctx_rules in context_groups.items():
            self.logger.debug(f"Scoring {len(ctx_rules)} rules in context: {ctx_key}")

            # Calculate profit for all rules in this context
            for rule in ctx_rules:
                rule.profit_score = self.profit_calc.calculate_rule_profit(rule, transactions)

            # Calculate diversity within this context
            for rule in ctx_rules:
                rule.diversity_score = self.diversity_scorer.calculate_diversity(rule, ctx_rules)

            # Get normalization ranges for this context
            lift_vals = [r.lift for r in ctx_rules]
            profit_vals = [r.profit_score for r in ctx_rules]

            lift_min, lift_max = min(lift_vals), max(lift_vals)
            profit_min, profit_max = min(profit_vals), max(profit_vals)

            # Handle edge case where all values are the same
            lift_range = lift_max - lift_min if lift_max != lift_min else 1.0
            profit_range = profit_max - profit_min if profit_max != profit_min else 1.0

            # Calculate overall score for each rule in this context
            for rule in ctx_rules:
                # Normalize lift and profit within this context
                norm_lift = (rule.lift - lift_min) / lift_range
                norm_profit = (rule.profit_score - profit_min) / profit_range

                # Calculate overall score
                rule.overall_score = (
                    self.weights['lift'] * norm_lift +
                    self.weights['profit_margin'] * norm_profit +
                    self.weights['diversity'] * rule.diversity_score +
                    self.weights['confidence'] * rule.confidence
                )

            scored_rules.extend(ctx_rules)

        # Sort all rules by overall score (descending)
        scored_rules.sort(key=lambda r: r.overall_score, reverse=True)

        self.logger.info(f"Scored {len(scored_rules)} rules total")
        return scored_rules

    def get_scoring_weights(self) -> Dict[str, float]:
        """Get current scoring weights."""
        return self.weights.copy()

    def set_scoring_weights(self, weights: Dict[str, float]):
        """Update scoring weights."""
        self.weights = weights
        self.logger.info(f"Updated scoring weights: {weights}")
