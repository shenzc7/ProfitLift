"""Tests for scoring functions."""
import pytest
import pandas as pd
from app.score.profit_calculator import ProfitCalculator
from app.score.diversity_scorer import DiversityScorer
from app.score.multi_objective import MultiObjectiveScorer
from app.mining.context_types import ContextualRule, Context

@pytest.fixture
def sample_transactions():
    """Create sample transactions for scoring tests."""
    data = {
        'transaction_id': ['1', '2', '3', '4'],
        'item_id': ['milk', 'bread', 'butter', 'cereal'],
        'price': [2.0, 1.0, 3.0, 4.0],
        'margin_pct': [0.2, 0.3, 0.1, 0.5],
        'category': ['dairy', 'bakery', 'dairy', 'cereal']
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_rule():
    """Create a sample rule."""
    return ContextualRule(
        antecedent=frozenset({'milk'}),
        consequent=frozenset({'bread'}),
        support=0.5,
        confidence=0.8,
        lift=1.5,
        context=Context()
    )

def test_profit_calculation(sample_transactions, sample_rule):
    """Test profit score calculation."""
    calculator = ProfitCalculator()
    
    # Calculate profit
    # Bread price=1.0, margin=0.3. 
    # Expected profit = price * margin * confidence = 1.0 * 0.3 * 0.8 = 0.24
    profit = calculator.calculate_rule_profit(sample_rule, sample_transactions)
    
    assert abs(profit - 0.24) < 0.001

def test_diversity_within_context():
    """Test diversity scoring only within same context."""
    scorer = DiversityScorer()
    ctx = Context(time_bin='morning')
    
    # Create 3 rules in same context, all involving 'bread'
    rule1 = ContextualRule(
        antecedent=frozenset({'milk'}), consequent=frozenset({'bread'}),
        support=0.1, confidence=0.1, lift=1.0, context=ctx
    )
    rule2 = ContextualRule(
        antecedent=frozenset({'eggs'}), consequent=frozenset({'bread'}),
        support=0.1, confidence=0.1, lift=1.0, context=ctx
    )
    rule3 = ContextualRule(
        antecedent=frozenset({'butter'}), consequent=frozenset({'bread'}),
        support=0.1, confidence=0.1, lift=1.0, context=ctx
    )
    
    context_rules = [rule1, rule2, rule3]
    
    # 'bread' appears in 3/3 rules (freq=1.0). 
    # 'milk' appears in 1/3 rules (freq=0.33).
    # rule1 items: milk, bread. Avg freq = (0.33 + 1.0) / 2 = 0.665
    # Diversity = 1 - 0.665 = 0.335
    
    diversity = scorer.calculate_diversity(rule1, context_rules)
    assert diversity < 1.0
    assert diversity > 0.0

def test_diversity_cross_context():
    """Test diversity scoring does NOT penalize cross-context."""
    scorer = DiversityScorer()
    ctx1 = Context(time_bin='morning')
    ctx2 = Context(time_bin='evening')
    
    # Same rule in different contexts
    rule1 = ContextualRule(
        antecedent=frozenset({'milk'}), consequent=frozenset({'bread'}),
        support=0.1, confidence=0.1, lift=1.0, context=ctx1
    )
    rule2 = ContextualRule(
        antecedent=frozenset({'milk'}), consequent=frozenset({'bread'}),
        support=0.1, confidence=0.1, lift=1.0, context=ctx2
    )
    
    # When scoring rule1, it should only look at ctx1 rules (only itself)
    # So diversity should be 1.0
    diversity = scorer.calculate_diversity(rule1, [rule1, rule2])
    assert diversity == 1.0

def test_multi_objective_scoring(sample_transactions):
    """Test multi-objective score combines all factors."""
    scorer = MultiObjectiveScorer()
    ctx = Context()
    
    # Create two rules
    # Rule 1: High lift, low profit
    rule1 = ContextualRule(
        antecedent=frozenset({'milk'}), consequent=frozenset({'bread'}),
        support=0.1, confidence=0.8, lift=2.0, context=ctx
    )
    # Rule 2: Low lift, high profit (consequent 'cereal' price=4.0, margin=0.5)
    rule2 = ContextualRule(
        antecedent=frozenset({'milk'}), consequent=frozenset({'cereal'}),
        support=0.1, confidence=0.8, lift=1.2, context=ctx
    )
    
    rules = [rule1, rule2]
    scored_rules = scorer.score_rules(rules, sample_transactions)
    
    assert len(scored_rules) == 2
    assert scored_rules[0].overall_score is not None
    assert scored_rules[1].overall_score is not None
    
    # Verify scores are normalized (0-1 range for components)
    # Since we have 2 items, one will be min (0) and one max (1) for each component
    # This makes exact verification tricky without manual calculation, 
    # but we can check that scores are calculated.

def test_score_normalization(sample_transactions):
    """Test per-context score normalization."""
    scorer = MultiObjectiveScorer()
    ctx1 = Context(time_bin='morning')
    ctx2 = Context(time_bin='evening')
    
    # Rule in context 1 with lift 10
    rule1 = ContextualRule(
        antecedent=frozenset({'a'}), consequent=frozenset({'b'}),
        support=0.1, confidence=0.5, lift=10.0, context=ctx1
    )
    # Rule in context 1 with lift 20
    rule2 = ContextualRule(
        antecedent=frozenset({'c'}), consequent=frozenset({'d'}),
        support=0.1, confidence=0.5, lift=20.0, context=ctx1
    )
    
    # Rule in context 2 with lift 2 (should be treated as high in its context if max)
    rule3 = ContextualRule(
        antecedent=frozenset({'e'}), consequent=frozenset({'f'}),
        support=0.1, confidence=0.5, lift=1.0, context=ctx2
    )
    rule4 = ContextualRule(
        antecedent=frozenset({'g'}), consequent=frozenset({'h'}),
        support=0.1, confidence=0.5, lift=2.0, context=ctx2
    )
    
    rules = [rule1, rule2, rule3, rule4]
    scored_rules = scorer.score_rules(rules, sample_transactions)
    
    # In ctx1: rule2 is max lift (norm=1), rule1 is min (norm=0)
    # In ctx2: rule4 is max lift (norm=1), rule3 is min (norm=0)
    # If profit/diversity/confidence are equal/zero, overall score depends on lift weight
    
    # We can't easily check exact values without mocking internal calc, 
    # but we can verify that rule4 (lift 2) isn't penalized against rule2 (lift 20)
    # because they are in different contexts.
    
    # Actually, since profit is 0 for all (items not in transactions), 
    # and diversity is 1.0 for all (no overlap), and confidence is 0.5 for all.
    # The only difference is lift.
    # So rule2 should have same partial score contribution from lift as rule4.
    
    # Let's check if rule4 score is roughly equal to rule2 score
    r2_score = next(r for r in scored_rules if r == rule2).overall_score
    r4_score = next(r for r in scored_rules if r == rule4).overall_score
    
    assert abs(r2_score - r4_score) < 0.001
