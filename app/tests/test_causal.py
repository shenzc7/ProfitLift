"""Tests for causal uplift estimation."""
import pytest
import pandas as pd
import numpy as np
from app.causal.causal_estimator import CausalEstimator, UpliftResult
from app.mining.context_types import ContextualRule, Context

@pytest.fixture
def sample_transactions():
    """Create sample transactions for causal tests."""
    # Create enough data for simulation
    data = []
    for i in range(100):
        data.append({
            'transaction_id': str(i),
            'item_id': 'milk',
            'price': 2.0,
            'margin_pct': 0.2,
            'basket_size': np.random.randint(1, 10),
            'avg_price': 2.5,
            'has_discount': np.random.choice([0, 1]),
            'hour': np.random.randint(8, 20)
        })
        # Add consequent item 'bread' to some transactions
        if i % 2 == 0: # 50% attach rate roughly
             data.append({
                'transaction_id': str(i),
                'item_id': 'bread',
                'price': 1.0,
                'margin_pct': 0.3,
                'basket_size': np.random.randint(1, 10),
                'avg_price': 2.5,
                'has_discount': np.random.choice([0, 1]),
                'hour': np.random.randint(8, 20)
            })
            
    return pd.DataFrame(data)

@pytest.fixture
def sample_rule():
    """Create a sample rule."""
    return ContextualRule(
        antecedent=frozenset({'milk'}),
        consequent=frozenset({'bread'}),
        support=0.5,
        confidence=0.5,
        lift=1.0,
        context=Context()
    )

def test_t_learner_initialization():
    """Test T-Learner can be instantiated."""
    estimator = CausalEstimator()
    assert estimator is not None
    assert estimator.t_learner is not None

def test_uplift_estimation(sample_transactions, sample_rule):
    """Test uplift estimation on known rule."""
    estimator = CausalEstimator(min_incremental_lift=0.0) # Set low to ensure result
    
    result = estimator.estimate_uplift(sample_rule, sample_transactions)
    
    assert isinstance(result, UpliftResult)
    assert result.sample_size > 0
    # We can't guarantee positive uplift on random data, but we can check structure
    assert isinstance(result.incremental_attach_rate, float)
    assert isinstance(result.confidence_interval, tuple)

def test_min_incremental_lift_threshold(sample_transactions, sample_rule):
    """Test min_incremental_lift threshold filtering."""
    # Set threshold very high so it filters out everything
    estimator = CausalEstimator(min_incremental_lift=1.0)
    
    result = estimator.estimate_uplift(sample_rule, sample_transactions)
    
    assert result.incremental_attach_rate == 0.0
    assert result.incremental_revenue == 0.0

def test_insufficient_data_handling(sample_rule):
    """Test handling of insufficient data for estimation."""
    estimator = CausalEstimator()
    empty_df = pd.DataFrame(columns=['transaction_id', 'item_id'])
    
    result = estimator.estimate_uplift(sample_rule, empty_df)
    
    assert result.sample_size == 0
    assert result.incremental_attach_rate == 0.0

def test_confidence_interval_calculation():
    """Test confidence interval is calculated correctly."""
    estimator = CausalEstimator()
    
    y_control = np.array([0, 0, 0, 1, 1])
    y_treatment = np.array([0, 1, 1, 1, 1])
    
    lower, upper = estimator._calculate_confidence_interval(y_control, y_treatment, n_bootstrap=50)
    
    assert isinstance(lower, float)
    assert isinstance(upper, float)
    assert lower <= upper
