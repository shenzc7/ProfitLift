import time
import logging
import sys
from app.api.services import AnalyticsService
from app.api.models import RuleFilter

# Configure logging to show timing
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_bundles():
    print("Initializing Service...")
    start_init = time.time()
    service = AnalyticsService()
    print(f"Service initialized in {time.time() - start_init:.2f}s")

    filters = RuleFilter(min_support=0.05, min_confidence=0.1, min_lift=1.2, limit=10, include_causal=True)
    
    print("Starting get_bundles...")
    start_total = time.time()
    
    # We'll break down what get_bundles does manually to see the step
    
    print("1. Loading transactions...")
    t0 = time.time()
    transactions = service._load_transactions(filters)
    print(f"   Loaded {len(transactions)} transactions in {time.time() - t0:.2f}s")
    
    if transactions.empty:
        print("   No transactions found!")
        return

    print("2. Mining rules...")
    t0 = time.time()
    from app.mining.context_aware_miner import ContextAwareMiner
    miner = ContextAwareMiner(
        min_support=filters.min_support,
        min_confidence=filters.min_confidence,
        min_rows_per_context=filters.min_rows_per_context,
    )
    rules = miner.mine_all_contexts(transactions)
    print(f"   Mined {len(rules)} rules in {time.time() - t0:.2f}s")
    
    rules = [rule for rule in rules if rule.lift >= filters.min_lift]
    print(f"   Filtered to {len(rules)} rules with lift >= {filters.min_lift}")

    print("3. Scoring rules...")
    t0 = time.time()
    scored_rules = service.scorer.score_rules(rules, transactions)[: filters.limit]
    print(f"   Scored and took top {len(scored_rules)} in {time.time() - t0:.2f}s")

    print("4. Causal Inference (The likely culprit)...")
    t0 = time.time()
    for i, rule in enumerate(scored_rules):
        t_rule = time.time()
        print(f"   Estimating uplift for rule {i+1}/{len(scored_rules)}: {rule.antecedent} -> {rule.consequent}")
        uplift = service.causal_estimator.estimate_uplift(rule, transactions)
        print(f"     -> Took {time.time() - t_rule:.2f}s")
    
    print(f"Total time: {time.time() - start_total:.2f}s")

if __name__ == "__main__":
    debug_bundles()
