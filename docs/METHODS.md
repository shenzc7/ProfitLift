# ProfitLift Methodology

## Overview

ProfitLift is a **Context-Aware, Profit-Optimized Market Basket Analysis** system designed for Indian retail. It addresses three limitations of traditional MBA:

| Traditional MBA | ProfitLift Solution |
|-----------------|---------------------|
| Ignores context (time, season) | **Context-Aware Mining** per time slot, festival, day type |
| Optimizes for frequency | **Profit-First Scoring** ranks by margin, not popularity |
| Shows correlation only | **Causal Uplift Estimation** via T-Learner |

---

## 1. Context-Aware Rule Mining

### The Problem
Traditional MBA generates one global set of rules, but:
- Morning shoppers buy differently than evening shoppers
- Diwali week patterns differ from regular weeks
- Urban stores behave differently than suburban stores

### Our Solution: Segment First, Then Mine

```
Transactions → Segment by Context → Mine Each Segment → Merge Results
```

**Context Dimensions:**
- **Time of Day**: Morning (6-11), Midday (11-14), Afternoon (14-18), Evening (18-22)
- **Day Type**: Weekday vs Weekend
- **Festival Period**: Diwali, Holi, Navratri, Eid, Christmas (India-specific)
- **Store/Region**: Location-specific patterns

### Algorithm: FP-Growth

We use **FP-Growth** (Frequent Pattern Growth) for efficient mining:

1. **Build FP-Tree**: Compress transaction data into a tree structure
2. **Mine Patterns**: Extract frequent itemsets recursively
3. **Generate Rules**: Create association rules with support, confidence, lift

**Why FP-Growth?**
- 10x faster than Apriori on large datasets
- Memory-efficient (no candidate generation)
- Scales well with Indian retail data volumes

---

## 2. Multi-Objective Scoring

### The Problem
Traditional MBA ranks rules by **Lift** alone. But:
- High-lift rules may involve low-margin items
- Popular items dominate, reducing recommendation diversity

### Our Solution: Composite Score

```
Score = 0.30 × Lift + 0.40 × Profit + 0.15 × Diversity + 0.15 × Confidence
```

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **Profit** | 40% | Expected margin contribution |
| **Lift** | 30% | Association strength |
| **Diversity** | 15% | Variety (penalizes repetition) |
| **Confidence** | 15% | Reliability of the rule |

### Profit Calculation (India-Aware)

```
Expected Profit = Price × Margin% × Confidence
```

For Indian retail, we account for:
- **GST Slabs**: 0%, 5%, 12%, 18%, 28% based on category
- **Category Margins**: Dairy (15%), Produce (30%), Packaged Food (18%)

### Diversity Score

Prevents "5 variations of the same milk" from dominating:

```
Diversity = 1 - (Avg frequency of rule items in other top rules)
```

---

## 3. Causal Uplift Estimation

### The Problem
Association ≠ Causation. Just because Bread and Butter are bought together doesn't mean recommending Butter *causes* more sales.

### Our Solution: T-Learner

The **T-Learner** (Two-Model Learner) estimates the **true incremental effect** of a recommendation:

```
                    ┌─────────────────┐
Historical Data →   │ Control Model   │ → P(Buy | No Recommendation)
                    │ (M₀)            │
                    └─────────────────┘
                    
                    ┌─────────────────┐
                    │ Treatment Model │ → P(Buy | With Recommendation)
                    │ (M₁)            │
                    └─────────────────┘

Uplift = M₁(x) - M₀(x)
```

**Key Metrics:**
- **Incremental Attach Rate**: True increase in purchase probability
- **Incremental Margin**: Extra profit from the recommendation

### Honest Limitations

- T-Learner uses **observational data**, not A/B tests
- Results are **estimates**, not proof of causation
- Requires sufficient data per context (~100+ transactions)

---

## 4. India-Specific Adaptations

### Festival-Aware Context

Indian retail has dramatic demand spikes during festivals:

| Festival | Typical Impact | Categories Affected |
|----------|----------------|---------------------|
| Diwali | 40-60% spike | Sweets, Dry Fruits, Gifting |
| Holi | 20-30% spike | Colors, Thandai, Sweets |
| Navratri | 15-25% spike | Pooja items, Vegetarian food |

ProfitLift automatically detects festival periods and creates dedicated contexts.

### GST-Aware Margin Estimation

```python
def calculate_margin_indian(mrp, purchase_price, category):
    gst_rate = get_gst_rate(category)  # 0%, 5%, 12%, 18%, 28%
    net_selling = mrp / (1 + gst_rate)
    margin = (net_selling - purchase_price) / net_selling
    return margin
```

### Sparse Data Handling

For smaller retailers (kiranas), we auto-adjust parameters:

| Data Volume | Mode | Context Depth | Min Support |
|-------------|------|---------------|-------------|
| 10,000+ | Full | Store × Time | 0.01 |
| 2,000-10,000 | Standard | Single dimension | 0.02 |
| 500-2,000 | Compact | Limited | 0.05 |
| <500 | Minimal | Overall only | 0.08 |

---

## 5. System Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│  CSV Data   │ ──▶ │ Context Enricher │ ──▶ │   SQLite DB  │
└─────────────┘     │ (Festival, Time) │     └──────────────┘
                    └─────────────────┘              │
                                                     ▼
┌─────────────┐     ┌─────────────────┐     ┌──────────────┐
│  React UI   │ ◀── │   FastAPI       │ ◀── │ Context Miner│
└─────────────┘     │   Backend       │     │ (FP-Growth)  │
                    └─────────────────┘     └──────────────┘
                            ▲                       │
                            │                       ▼
                    ┌─────────────────┐     ┌──────────────┐
                    │  T-Learner      │ ◀── │ Multi-Obj    │
                    │  (Causal)       │     │ Scorer       │
                    └─────────────────┘     └──────────────┘
```

---

## 6. Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Attach Rate Uplift | P(Buy\|Treatment) - P(Buy\|Control) | > 5% |
| Incremental Margin | Uplift × Price × Margin% | > ₹10/basket |
| Time to Insight | Data upload → Recommendations | < 5 minutes |
| Rule Relevance | Context-specific vs generic rules | > 70% context-specific |

---

## 7. Key Contributions

1. **Context-Aware MBA**: First to segment by Indian festivals (Diwali, Holi, Navratri)
2. **Profit-First Ranking**: 40% weight on margin, not just frequency
3. **Causal Integration**: T-Learner for uplift estimation in MBA (novel)
4. **India-Optimized**: GST-aware margins, festival calendars, sparse data handling

---

## References

- Han, J., et al. (2000). "Mining Frequent Patterns without Candidate Generation" (FP-Growth)
- Künzel, S., et al. (2019). "Metalearners for Estimating Heterogeneous Treatment Effects" (T-Learner)
- Agrawal, R., Srikant, R. (1994). "Fast Algorithms for Mining Association Rules" (Apriori)
