# Design Decisions

## Why Streamlit?
We chose Streamlit over PyQt6 or Electron for the frontend because:
- **Rapid Iteration**: Allows fast prototyping of data visualizations.
- **Python Native**: Seamless integration with our pandas/scikit-learn backend.
- **Web-Ready**: Easier to deploy as a web app in the future if needed, while still packageable as a desktop EXE.

## Why T-Learner?
We implemented a T-Learner (Two-Learner) meta-learner for causal estimation instead of a DR-Learner or S-Learner because:
- **Simplicity**: It is easier to explain to stakeholders (Control Model vs. Treatment Model).
- **Robustness**: It handles strong treatment imbalances well, which is common in retail data.

## Why FP-Growth + Eclat?
We avoided Apriori because it is computationally expensive (candidate generation).
- **FP-Growth**: Primary engine. Extremely fast for dense datasets.
- **Eclat**: Used for validation. Efficient for sparse, vertical data.

## Why Context-Aware Mining?
Standard MBA fails to capture "breakfast patterns" vs "dinner patterns". By segmenting data *before* mining, we discover rules that are locally frequent (e.g., coffee + bagel in morning) even if they are globally rare.

## Why Multi-Objective Scoring?
High-lift rules are often obscure (low support). High-support rules are often obvious (milk + bread).
Our scoring function balances:
1. **Lift** (Strength of association)
2. **Profit** (Business value)
3. **Diversity** (Catalog coverage)
4. **Confidence** (Reliability)
