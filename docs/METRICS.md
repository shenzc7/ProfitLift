# Evaluation Metrics

## Metrics Definitions

### 1. Attach Rate Uplift
The difference in purchase probability between the treatment group (recommendation shown) and control group (no recommendation).
$$ \text{Uplift} = P(\text{Buy} | \text{Treatment}) - P(\text{Buy} | \text{Control}) $$

### 2. Incremental Margin per Basket
The additional profit generated specifically by the recommendation.
$$ \text{Incr. Margin} = \text{Uplift} \times \text{Price} \times \text{Margin\%} $$

### 3. Time to Insight
Measured as the time from raw data upload to actionable bundle recommendations. Target: < 5 minutes for 100k transactions.

### 4. Team Adoption
Qualitative metric: Number of weekly active users (WAU) among the merchandising team.

## Evaluation Protocol

To validate the system:
1. **Split Data**: Use time-based splitting (train on past, test on future).
2. **Simulate Treatment**: Since we lack live intervention data, we use the T-Learner to estimate effects based on natural variation in the data (observational causal inference).
3. **Benchmark**: Compare ProfitLift results against standard Apriori (frequency-only) ranking.

## Baseline Comparison

| Metric | Standard MBA (Apriori) | ProfitLift (Context-Aware) |
|--------|------------------------|----------------------------|
| **Focus** | Frequency | Profit & Causality |
| **Context** | Ignored | Native (Time/Store) |
| **Ranking** | Lift/Confidence | Multi-Objective Score |
| **Actionability** | Low (Generic) | High (Specific) |
