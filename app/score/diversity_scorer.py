from typing import List, Dict
from collections import defaultdict
import logging

from ..mining.context_types import ContextualRule


class DiversityScorer:
    """Calculates diversity score to penalize over-represented item combinations within contexts."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_diversity(self, rule: ContextualRule,
                           context_rules: List[ContextualRule]) -> float:
        """
        Calculate diversity score (0-1) penalizing over-representation WITHIN same context.

        Key innovation: only compare against rules in the SAME context.
        Diversity = 1 - avg(frequency of rule's items across other rules in same context)

        Args:
            rule: The rule to score for diversity
            context_rules: All rules from the same context

        Returns:
            Diversity score between 0 and 1 (higher = more diverse)
        """
        try:
            # Filter to rules in the same context
            same_context_rules = [r for r in context_rules if r.context == rule.context]

            if len(same_context_rules) <= 1:
                # If this is the only rule in the context, maximum diversity
                return 1.0

            # Get all items in this rule
            rule_items = set(rule.antecedent) | set(rule.consequent)

            # Count how many rules each item appears in within this context
            item_counts = defaultdict(int)

            for r in same_context_rules:
                r_items = set(r.antecedent) | set(r.consequent)
                for item in r_items:
                    item_counts[item] += 1

            # Calculate frequency for each item in this rule
            frequencies = []
            for item in rule_items:
                frequency = item_counts[item] / len(same_context_rules)
                frequencies.append(frequency)

            if not frequencies:
                return 1.0

            # Diversity = 1 - average frequency
            # Lower frequency = higher diversity (less common items = more diverse)
            avg_frequency = sum(frequencies) / len(frequencies)
            diversity = 1.0 - avg_frequency

            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, diversity))

        except Exception as e:
            self.logger.error(f"Error calculating diversity for rule {rule}: {e}")
            return 0.5  # Neutral score on error

    def calculate_context_diversity_stats(self, rules: List[ContextualRule]) -> Dict[str, float]:
        """
        Calculate diversity statistics for all contexts.

        Args:
            rules: All rules to analyze

        Returns:
            Dictionary with context diversity statistics
        """
        # Group rules by context
        context_groups = defaultdict(list)
        for rule in rules:
            context_groups[str(rule.context)].append(rule)

        stats = {}

        for context_str, context_rules in context_groups.items():
            if len(context_rules) > 1:
                diversities = [self.calculate_diversity(rule, context_rules)
                             for rule in context_rules]
                stats[context_str] = {
                    'avg_diversity': sum(diversities) / len(diversities),
                    'min_diversity': min(diversities),
                    'max_diversity': max(diversities),
                    'rules_count': len(context_rules)
                }
            else:
                stats[context_str] = {
                    'avg_diversity': 1.0,
                    'min_diversity': 1.0,
                    'max_diversity': 1.0,
                    'rules_count': len(context_rules)
                }

        return stats
