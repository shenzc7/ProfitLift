from app.assets.database import DatabaseManager
from app.mining.context_aware_miner import ContextAwareMiner
from app.causal.causal_estimator import CausalEstimator
import pandas as pd

# Get transaction data
db = DatabaseManager()
transactions_df = pd.DataFrame(db.execute_query('''
SELECT
    t.transaction_id, t.timestamp, t.store_id, t.context_time_bin, t.discount_flag,
    ti.item_id, ti.price, i.margin_pct
FROM transactions t
JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
JOIN items i ON ti.item_id = i.item_id
'''))

print(f'Loaded {len(transactions_df)} transaction items')

# Mine some rules
miner = ContextAwareMiner(min_support=0.1, min_confidence=0.3, min_rows_per_context=3)
rules = miner.mine_all_contexts(transactions_df)

print(f'Mined {len(rules)} rules')

# Test causal estimation on a few rules
estimator = CausalEstimator(min_incremental_lift=0.01)  # Lower threshold for testing

print('\n=== Causal Uplift Estimation Test ===')

# Test on rules with high confidence that might show causal effects
test_rules = []
for rule in rules:
    if rule.confidence > 0.8 and len(rule.antecedent) == 1 and len(rule.consequent) == 1:
        test_rules.append(rule)

print(f'Testing {min(5, len(test_rules))} high-confidence rules:')

for i, rule in enumerate(test_rules[:5]):
    print(f'\n{i+1}. Testing rule: {rule.antecedent} -> {rule.consequent}')
    print(f'   Context: {rule.context}')
    print(f'   Association metrics: conf={rule.confidence:.2f}, lift={rule.lift:.2f}')

    try:
        uplift_result = estimator.estimate_uplift(rule, transactions_df)
        print(f'   Causal uplift: {uplift_result.incremental_attach_rate:.3f}')
        print(f'   Control rate: {uplift_result.control_rate:.3f}')
        print(f'   Treatment rate: {uplift_result.treatment_rate:.3f}')
        print(f'   Incremental margin: ${uplift_result.incremental_margin:.3f}')
        print(f'   Sample size: {uplift_result.sample_size}')

        if uplift_result.confidence_interval:
            ci_lower, ci_upper = uplift_result.confidence_interval
            print(f'   95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]')

    except Exception as e:
        print(f'   Error: {e}')
