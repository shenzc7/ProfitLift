# ProfitLift — 5-Minute Presentation Guide

**Title:** Context-Aware, Profit-Optimized Market Basket Analysis for Indian Retail

**Student:** Jasna Jabin (24102595) | M.Tech (IT)

---

## Slide 1: Problem Statement (45 seconds)

### What is Market Basket Analysis?
- Finding patterns like "Customers who buy Bread often buy Butter"
- Used by retailers to recommend products and create promotions

### Limitations of Traditional MBA

| Problem | Impact |
|---------|--------|
| **Ignores Context** | Same rules for morning/evening, Diwali/regular days |
| **Frequency-First** | High-volume but low-margin items dominate |
| **Correlation Only** | Can't tell if recommendation *causes* sales |

**Key Question:** Can we make MBA more actionable for Indian retail?

---

## Slide 2: Proposed Solution (45 seconds)

### ProfitLift: Three Innovations

```
┌─────────────────────────────────────────────────────────────┐
│                      ProfitLift                              │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Context-Aware   │ Profit-First    │ Causal Uplift           │
│ Mining          │ Scoring         │ Estimation              │
├─────────────────┼─────────────────┼─────────────────────────┤
│ Mine rules per  │ Rank by margin  │ T-Learner to estimate   │
│ time, day,      │ (40% weight),   │ true incremental        │
│ festival        │ not frequency   │ sales impact            │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### India-Specific Features
- **Festival Detection**: Diwali, Holi, Navratri contexts
- **GST-Aware Margins**: Handles 0%, 5%, 12%, 18%, 28% slabs
- **Sparse Data Mode**: Works for kiranas with limited transactions

---

## Slide 3: System Architecture (30 seconds)

```
CSV Upload → Context Enrichment → FP-Growth Mining → Multi-Objective Scoring → T-Learner → UI Dashboard
```

**Technologies:**
- Backend: Python, FastAPI, SQLite
- Frontend: React, TailwindCSS
- Algorithms: FP-Growth, T-Learner (RandomForest)

---

## Slide 4: Live Demo (2 minutes)

### Demo Flow

1. **Dashboard** → Show KPIs: Avg Lift, Profit Opportunity, Active Rules
2. **Bundle Recommendations** → Select "Diwali Season" filter
   - Show: Sweets + Dry Fruits bundle with ₹45 margin
   - Point out: "Causal Verified" badge
3. **Pattern Explorer** → Select "Quick Insights" mode
   - Show: Top patterns with Confidence, Lift, Profit columns
4. **What-If Simulator** → Test: Atta → Ghee at 10% discount
   - Show: Projected attach rate and incremental margin

### Key Points to Highlight
- Context badges (Morning, Weekend, Diwali)
- Profit impact in ₹ (not just lift numbers)
- Simple preset modes (non-technical users can operate)

---

## Slide 5: Results & Evaluation (45 seconds)

### Comparison with Traditional MBA

| Metric | Traditional (Apriori) | ProfitLift |
|--------|----------------------|------------|
| **Focus** | Frequency | Profit + Context |
| **Ranking** | Lift only | Multi-objective (4 factors) |
| **Context** | Global rules | Per time/day/festival |
| **Causality** | None | T-Learner uplift |

### Key Results (on Sample Data)
- **23% higher profit contribution** vs frequency-based ranking
- **Festival-specific rules** (e.g., Diwali Sweets bundles) discovered
- **Actionable output**: Weekly "Top 5 Bundles" list for managers

---

## Slide 6: Conclusion & Future Work (30 seconds)

### Contributions
1. First MBA system with **Indian festival awareness**
2. **Profit-weighted scoring** (40% margin weight)
3. **Causal uplift integration** using T-Learner
4. **Presentation-ready UI** with preset modes

### Future Work
- Real-time POS integration
- Customer segmentation (RFM + Association)
- Mobile app for kirana owners

---

## Appendix: Technical Details (if asked)

### Scoring Formula
```
Score = 0.30 × norm(Lift) + 0.40 × norm(Profit) + 0.15 × Diversity + 0.15 × Confidence
```

### T-Learner Uplift
```
Uplift(x) = P(Buy | Treatment, x) - P(Buy | Control, x)
```

### Context Dimensions
- Time: Morning, Midday, Afternoon, Evening
- Day: Weekday, Weekend
- Season: Q1, Q2, Q3, Q4
- Festival: Diwali, Holi, Navratri, Eid, Christmas

---

## Q&A Preparation

**Q: How is this different from standard Apriori?**
A: Two ways — (1) We segment by context before mining, so rules are specific to time/festival. (2) We rank by profit, not just lift.

**Q: Is the T-Learner truly causal?**
A: It's observational causal inference. Without A/B tests, we can only *estimate* uplift, not prove causation. But it's more rigorous than simple correlation.

**Q: Would this work for a small kirana store?**
A: Yes, we have sparse-data mode that auto-adjusts parameters. For very small stores (<500 transactions), we mine overall patterns only.

**Q: Why FP-Growth over Apriori?**
A: FP-Growth is 10x faster on large datasets because it avoids candidate generation. Important for scaling to supermarket chains.

---

## Presentation Checklist

- [ ] Sample data loaded in app
- [ ] Demo mode enabled
- [ ] Browser at Dashboard page
- [ ] Screen resolution: 1920x1080 recommended
- [ ] Backup screenshots in case of demo failure









