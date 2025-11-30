"""Tests for context-aware mining."""
import pytest
import pandas as pd
from app.mining.context_segmenter import ContextSegmenter
from app.mining.context_types import Context
from app.mining.fpgrowth import FPGrowthMiner
from app.mining.eclat import EclatMiner

# --- Context Segmenter Tests ---

def test_time_bin_segmentation():
    """Test time bin segmentation (morning, midday, afternoon, evening)."""
    # Create transactions with different time bins
    data = {
        'transaction_id': ['1', '2', '3', '4'],
        'context_time_bin': ['morning', 'afternoon', 'morning', 'evening'],
        'store_id': ['1', '1', '1', '1']
    }
    df = pd.DataFrame(data)
    
    segmenter = ContextSegmenter(min_rows=1)
    segments = segmenter.segment(df)
    
    # Check for morning context
    morning_ctx = Context(time_bin='morning')
    assert morning_ctx in segments
    assert len(segments[morning_ctx]) == 2
    
    # Check for afternoon context
    afternoon_ctx = Context(time_bin='afternoon')
    assert afternoon_ctx in segments
    assert len(segments[afternoon_ctx]) == 1

def test_weekday_weekend_segmentation():
    """Test weekday vs weekend segmentation."""
    data = {
        'transaction_id': ['1', '2'],
        'context_weekday_weekend': ['weekday', 'weekend'],
        'store_id': ['1', '1']
    }
    df = pd.DataFrame(data)
    
    segmenter = ContextSegmenter(min_rows=1)
    segments = segmenter.segment(df)
    
    weekday_ctx = Context(weekday_weekend='weekday')
    assert weekday_ctx in segments
    assert len(segments[weekday_ctx]) == 1

def test_quarter_segmentation():
    """Test quarterly segmentation."""
    data = {
        'transaction_id': ['1', '2'],
        'context_quarter': [1, 2],
        'store_id': ['1', '1']
    }
    df = pd.DataFrame(data)
    
    segmenter = ContextSegmenter(min_rows=1)
    segments = segmenter.segment(df)
    
    q1_ctx = Context(quarter=1)
    assert q1_ctx in segments
    assert len(segments[q1_ctx]) == 1

def test_context_backoff():
    """Test context backoff when min_rows_per_context not met."""
    data = {
        'transaction_id': ['1', '2'],
        'context_time_bin': ['morning', 'morning'],
        'store_id': ['1', '1']
    }
    df = pd.DataFrame(data)
    
    # Set min_rows higher than available data
    segmenter = ContextSegmenter(min_rows=5)
    segments = segmenter.segment(df)
    
    # Specific context should NOT be present
    morning_ctx = Context(time_bin='morning')
    assert morning_ctx not in segments
    
    # Overall context (empty context) should always be present
    assert Context() in segments

def test_context_combinations():
    """Test all context combinations (store × time)."""
    data = {
        'transaction_id': ['1', '2'],
        'store_id': ['S1', 'S1'],
        'context_time_bin': ['morning', 'morning']
    }
    df = pd.DataFrame(data)
    
    segmenter = ContextSegmenter(min_rows=1)
    segments = segmenter.segment(df)
    
    # Check combined context
    combined_ctx = Context(store_id='S1', time_bin='morning')
    assert combined_ctx in segments
    assert len(segments[combined_ctx]) == 2

# --- FP-Growth Tests ---

def test_fpgrowth_itemset_mining():
    """Test FP-Growth finds frequent itemsets."""
    transactions = [
        ['milk', 'bread', 'butter'],
        ['milk', 'bread'],
        ['milk', 'diapers'],
        ['bread', 'butter']
    ]
    
    miner = FPGrowthMiner()
    # min_support 0.5 means items appearing in at least 2 transactions
    itemsets = miner.mine(transactions, min_support=0.5)
    
    assert not itemsets.empty
    # milk (3), bread (3), butter (2), {milk, bread} (2)
    assert len(itemsets) >= 4
    
    # Check specific itemset support
    milk_support = itemsets[itemsets['itemsets'] == frozenset({'milk'})]['support'].iloc[0]
    assert milk_support == 0.75

def test_fpgrowth_rule_generation():
    """Test FP-Growth generates association rules."""
    transactions = [
        ['milk', 'bread', 'butter'],
        ['milk', 'bread'],
        ['milk', 'bread'],
        ['milk', 'bread']
    ]
    # milk -> bread should be high confidence
    
    miner = FPGrowthMiner()
    itemsets = miner.mine(transactions, min_support=0.5)
    rules = miner.generate_rules(itemsets, min_confidence=0.9)
    
    assert not rules.empty
    assert 'confidence' in rules.columns
    assert 'lift' in rules.columns

def test_fpgrowth_empty_transactions():
    """Test handling of empty transaction list."""
    miner = FPGrowthMiner()
    itemsets = miner.mine([], min_support=0.5)
    assert itemsets.empty

# --- Eclat Tests ---

def test_eclat_vertical_format():
    """Test Eclat uses vertical format correctly."""
    transactions = [
        ['a', 'b'],
        ['a', 'c']
    ]
    miner = EclatMiner()
    vertical_db = miner._to_vertical_format(transactions)
    
    assert 'a' in vertical_db
    assert vertical_db['a'] == {0, 1}
    assert vertical_db['b'] == {0}

def test_eclat_validation():
    """Test Eclat results match FP-Growth (validation)."""
    transactions = [
        ['milk', 'bread', 'butter'],
        ['milk', 'bread'],
        ['milk', 'diapers'],
        ['bread', 'butter']
    ]
    
    fp_miner = FPGrowthMiner()
    eclat_miner = EclatMiner()
    
    fp_itemsets = fp_miner.mine(transactions, min_support=0.5)
    eclat_itemsets = eclat_miner.mine(transactions, min_support=0.5)
    
    # Sort and compare supports
    fp_supports = sorted(fp_itemsets['support'].tolist())
    eclat_supports = sorted(eclat_itemsets['support'].tolist())
    
    assert len(fp_supports) == len(eclat_supports)
    for s1, s2 in zip(fp_supports, eclat_supports):
        assert abs(s1 - s2) < 0.001
