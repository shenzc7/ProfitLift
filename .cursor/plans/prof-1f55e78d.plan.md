<!-- 1f55e78d-5429-4115-aee8-fc18a6d20a3e 46fbb733-0c21-454f-9622-e1373077e893 -->
# ProfitLift: Context-Aware Profit-Optimized MBA System

## Core Innovation

Traditional MBA finds "milk → bread" patterns. **ProfitLift** finds "milk → cereal on weekend mornings in suburban stores during Q1, with $2.30 incremental margin and 15% true uplift."

**Tech Stack:**

- Backend: FastAPI + SQLite + mlxtend + scikit-learn
- UI: Streamlit (replaces PyQt6)
- Algorithms: FP-Growth (primary), Eclat (secondary)
- Uplift: T-Learner (RandomForest baseline), DR-Learner (stretch)
- Packaging: GitHub Actions → PyInstaller → Inno Setup (Windows installer)

---

## Phase 1: Project Foundation

### 1.1 Repository Structure

```
ProfitLift/
├── app/
│   ├── ingest/          # CSV import, validation, context enrichment
│   ├── mining/          # FP-Growth, Eclat implementations
│   ├── score/           # Multi-objective scoring (lift + profit + diversity)
│   ├── causal/          # T-Learner uplift modeling
│   ├── sim/             # What-if simulator
│   ├── api/             # FastAPI routes & models
│   ├── ui/              # Streamlit pages (rules, bundles, what-if, help)
│   ├── tests/           # Unit & integration tests
│   └── assets/          # Icons, sample CSVs, SQL schema
├── config/
│   ├── default.yaml     # Mining params, weights, context bins
│   └── scoring.yaml     # Multi-objective weights
├── data/
│   └── sample/
│       └── sample_1k.csv
├── docs/
│   ├── METHODS.md       # Equations & methodology
│   ├── DESIGN.md        # Architecture & interfaces
│   ├── METRICS.md       # Evaluation protocol
│   ├── DECISIONS.md     # Design rationale
│   └── DEMO_SCRIPT.md   # 1-minute walkthrough
├── .github/
│   └── workflows/
│       └── windows-build.yml
├── README.md
├── requirements.txt
├── pyproject.toml
└── .gitignore
```

### 1.2 Requirements (Trimmed)

**requirements.txt:**

```
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
mlxtend>=0.22
fastapi>=0.110
uvicorn[standard]>=0.27
pydantic>=2.6
streamlit>=1.35
sqlalchemy>=2.0
watchdog>=3.0
pyyaml>=6.0
reportlab>=4.0
pytest>=7.4
pytest-cov>=4.1
black>=23.7
flake8>=6.0
pyinstaller>=6.0
```

**Why trimmed:** No PyQt6 (using Streamlit), no Plotly (Streamlit built-in), no LightGBM (scikit-learn RF sufficient).

### 1.3 Configuration Files

**config/default.yaml:**

```yaml
database:
  path: "profitlift.db"

mining:
  min_support: 0.01
  min_confidence: 0.3
  min_lift: 1.1
  algorithms: ["fpgrowth", "eclat"]  # No apriori

context:
  time_bins: ["morning", "midday", "afternoon", "evening"]
  weekday_weekend: true
  seasonal_quarters: true
  store_clustering: false  # Optional stretch
  min_rows_per_context: 100  # Auto-backoff to broader context

scoring:
  weights_file: "config/scoring.yaml"
  diversity_scope: "within_context"  # Key: don't penalize cross-context overlap

uplift:
  method: "t_learner"  # T-Learner baseline (RandomForest)
  dr_learner_enabled: false  # Stretch goal
  min_incremental_lift: 0.05

streaming:
  enabled: true
  check_interval_seconds: 300

api:
  host: "127.0.0.1"
  port: 8000
```

**config/scoring.yaml:**

```yaml
weights:
  lift: 0.30
  profit_margin: 0.40
  diversity: 0.15
  confidence: 0.15

profit:
  default_margin_pct: 0.25
  category_margins:
    Dairy: 0.30
    Produce: 0.40
    Meat: 0.20
```

### 1.4 Initial Setup

**pyproject.toml:**

```toml
[project]
name = "profitlift"
version = "1.0.0"
description = "Context-Aware Profit-Optimized Market Basket Analysis"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
```

**Acceptance:**

- All directories created
- `pip install -r requirements.txt` succeeds
- `python -c "import app.ingest, app.mining, app.score, app.causal, app.api, app.ui"` works
- Config files parse with `yaml.safe_load()`

---

## Phase 2: Data Layer

### 2.1 Database Schema (Enhanced)

**app/assets/schema.sql:**

```sql
-- Items table (NEW: avoid parsing JSON everywhere)
CREATE TABLE items (
    item_id TEXT PRIMARY KEY,
    item_name TEXT,
    category TEXT,
    avg_price REAL,
    margin_pct REAL
);

-- Transactions
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    store_id TEXT NOT NULL,
    customer_id_hash TEXT,
    total_value REAL,
    discount_flag INTEGER DEFAULT 0,
    context_time_bin TEXT,
    context_weekday_weekend TEXT,
    context_quarter INTEGER
);

-- Transaction items
CREATE TABLE transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price REAL NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- Association rules (context-specific)
CREATE TABLE association_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antecedent TEXT NOT NULL,  -- JSON array
    consequent TEXT NOT NULL,  -- JSON array
    support REAL NOT NULL,
    confidence REAL NOT NULL,
    lift REAL NOT NULL,
    profit_score REAL,
    diversity_score REAL,
    overall_score REAL,
    context_store_id TEXT,
    context_time_bin TEXT,
    context_weekday_weekend TEXT,
    context_quarter INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Uplift results
CREATE TABLE uplift_results (
    rule_id INTEGER PRIMARY KEY,
    incremental_attach_rate REAL,
    incremental_revenue REAL,
    incremental_margin REAL,
    control_rate REAL,
    treatment_rate REAL,
    FOREIGN KEY (rule_id) REFERENCES association_rules(id)
);

-- Indexes
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_store ON transactions(store_id);
CREATE INDEX idx_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_items_item ON transaction_items(item_id);
CREATE INDEX idx_rules_score ON association_rules(overall_score DESC);
CREATE INDEX idx_rules_context ON association_rules(context_store_id, context_time_bin);
```

### 2.2 CSV Import

**app/ingest/csv_importer.py:**

```python
class CSVImporter:
    """Import, validate, enrich CSV with context dimensions."""
    
    REQUIRED_COLS = ['transaction_id', 'timestamp', 'store_id', 'item_id', 'price']
    OPTIONAL_COLS = ['customer_id_hash', 'item_name', 'category', 'quantity', 
                     'discount_flag', 'margin_pct']
    
    def import_csv(self, filepath: str) -> ImportResult:
        # 1. Load & validate required columns
        # 2. Enrich with context columns (time_bin, weekday_weekend, quarter)
        # 3. Populate items table (upsert unique items)
        # 4. Populate transactions & transaction_items
        # 5. Return stats (rows imported, rejected, errors)
```

**app/ingest/context_enricher.py:**

```python
def add_context_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add context dimensions based on timestamp."""
    df['context_time_bin'] = df['timestamp'].apply(_get_time_bin)
    df['context_weekday_weekend'] = df['timestamp'].apply(
        lambda x: 'weekend' if x.weekday() >= 5 else 'weekday'
    )
    df['context_quarter'] = df['timestamp'].dt.quarter
    return df

def _get_time_bin(timestamp) -> str:
    hour = timestamp.hour
    if 6 <= hour < 11: return 'morning'
    elif 11 <= hour < 14: return 'midday'
    elif 14 <= hour < 18: return 'afternoon'
    elif 18 <= hour < 22: return 'evening'
    else: return 'night'
```

**Acceptance:**

- `sample_1k.csv` imports successfully
- Context columns correctly derived
- Items table populated with unique items
- Query `SELECT * FROM transactions JOIN transaction_items USING(transaction_id)` returns correct data

---

## Phase 3: Mining Algorithms (Focused)

### 3.1 FP-Growth (Primary)

**app/mining/fpgrowth.py:**

```python
from mlxtend.frequent_patterns import fpgrowth, association_rules

class FPGrowthMiner:
    def mine(self, transactions: List[List[str]], min_support: float) -> pd.DataFrame:
        """Mine frequent itemsets using FP-Growth."""
        basket = self._to_basket_matrix(transactions)
        itemsets = fpgrowth(basket, min_support=min_support, use_colnames=True)
        return itemsets
    
    def generate_rules(self, itemsets: pd.DataFrame, min_confidence: float) -> pd.DataFrame:
        """Generate association rules."""
        rules = association_rules(itemsets, metric="confidence", min_threshold=min_confidence)
        return rules
```

### 3.2 Eclat (Secondary, Validation)

**app/mining/eclat.py:**

```python
class EclatMiner:
    """Eclat using vertical format (tid-list intersections)."""
    
    def mine(self, transactions: List[List[str]], min_support: float) -> pd.DataFrame:
        # 1. Convert to vertical DB: {item: {tid1, tid2, ...}}
        # 2. Intersect tid-sets to find frequent itemsets
        # 3. Return same format as FP-Growth for consistency
```

**Why no Apriori:** Redundant (slower, same results as FP-Growth). Keep two algorithms for validation/comparison.

**Acceptance:**

- FP-Growth mines patterns from sample data
- Eclat produces equivalent itemsets (validate with unit test)
- Rules have correct support, confidence, lift values

---

## Phase 4: Context-Aware Mining

### 4.1 Context Segmentation

**app/mining/context_segmenter.py:**

```python
@dataclass
class Context:
    store_id: Optional[str] = None
    time_bin: Optional[str] = None
    weekday_weekend: Optional[str] = None
    quarter: Optional[int] = None

class ContextSegmenter:
    def __init__(self, min_rows: int = 100):
        self.min_rows = min_rows
    
    def segment(self, transactions: pd.DataFrame) -> Dict[Context, pd.DataFrame]:
        """Segment by context, auto-backoff if < min_rows."""
        segments = {}
        
        # Level 1: Overall (always)
        segments[Context()] = transactions
        
        # Level 2: Single dimensions
        for store in transactions['store_id'].unique():
            ctx = Context(store_id=store)
            df = transactions[transactions['store_id'] == store]
            if len(df) >= self.min_rows:
                segments[ctx] = df
        
        # Level 3: Store × Time (key combination)
        for store in transactions['store_id'].unique():
            for time_bin in transactions['context_time_bin'].unique():
                ctx = Context(store_id=store, time_bin=time_bin)
                df = transactions[
                    (transactions['store_id'] == store) &
                    (transactions['context_time_bin'] == time_bin)
                ]
                if len(df) >= self.min_rows:
                    segments[ctx] = df
        
        # Level 4: Weekday/Weekend × Time
        # ... similar logic
        
        return segments
```

### 4.2 Context-Aware Rule Mining

**app/mining/context_miner.py:**

```python
class ContextAwareMiner:
    def mine_all_contexts(self, transactions: pd.DataFrame) -> List[ContextualRule]:
        """Mine rules per context segment."""
        segments = self.segmenter.segment(transactions)
        all_rules = []
        
        for context, segment_df in segments.items():
            trans_list = self._df_to_transactions(segment_df)
            
            # Mine with FP-Growth
            itemsets = self.fpgrowth.mine(trans_list, min_support=0.01)
            rules_df = self.fpgrowth.generate_rules(itemsets, min_confidence=0.3)
            
            # Tag with context
            for _, rule in rules_df.iterrows():
                all_rules.append(ContextualRule(
                    antecedent=frozenset(rule['antecedents']),
                    consequent=frozenset(rule['consequents']),
                    support=rule['support'],
                    confidence=rule['confidence'],
                    lift=rule['lift'],
                    context=context
                ))
        
        return all_rules
```

**Acceptance:**

- Segments created for store, time, store×time, weekday×time, quarter
- Segments with <100 transactions skipped (or backoff to broader context)
- Rules correctly tagged with context metadata
- Unit test: "milk→bread" has different lift in "morning" vs "evening"

---

## Phase 5: Multi-Objective Scoring (Per-Context)

### 5.1 Profit Calculator

**app/score/profit_calculator.py:**

```python
class ProfitCalculator:
    def calculate_rule_profit(self, rule: ContextualRule, 
                             transactions: pd.DataFrame) -> float:
        """
        Expected incremental profit per basket.
        Formula: E[profit] = Avg(consequent_price) × Margin% × Confidence
        """
        consequent_items = list(rule.consequent)
        
        # Get avg price & margin from items table or transactions
        item_data = transactions[transactions['item_id'].isin(consequent_items)]
        avg_price = item_data['price'].mean()
        avg_margin = self._get_margin(item_data)
        
        # Incremental attach rate ≈ confidence
        profit = avg_price * avg_margin * rule.confidence
        return profit
```

### 5.2 Diversity Scorer (Within-Context)

**app/score/diversity_scorer.py:**

```python
class DiversityScorer:
    def calculate_diversity(self, rule: ContextualRule, 
                           context_rules: List[ContextualRule]) -> float:
        """
        Diversity score (0-1) penalizing over-representation WITHIN same context.
        Key: only compare against rules in the SAME context.
        """
        same_context_rules = [r for r in context_rules if r.context == rule.context]
        
        rule_items = set(rule.antecedent) | set(rule.consequent)
        item_counts = {}
        
        for r in same_context_rules:
            items = set(r.antecedent) | set(r.consequent)
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1
        
        # Diversity = 1 - avg(frequency)
        frequencies = [item_counts[item] / len(same_context_rules) for item in rule_items]
        diversity = 1.0 - np.mean(frequencies)
        return max(0.0, diversity)
```

### 5.3 Multi-Objective Scorer

**app/score/multi_objective.py:**

```python
class MultiObjectiveScorer:
    def score_rules(self, rules: List[ContextualRule], 
                   transactions: pd.DataFrame) -> List[ContextualRule]:
        """
        Score rules WITHIN each context separately.
        Overall_score = w_lift*norm(lift) + w_profit*norm(profit) + 
                       w_diversity*diversity + w_confidence*confidence
        """
        # Group by context
        context_groups = {}
        for rule in rules:
            ctx = rule.context
            if ctx not in context_groups:
                context_groups[ctx] = []
            context_groups[ctx].append(rule)
        
        # Score each context group separately
        scored_rules = []
        for ctx, ctx_rules in context_groups.items():
            # Calculate profit for all
            for rule in ctx_rules:
                rule.profit_score = self.profit_calc.calculate_rule_profit(rule, transactions)
            
            # Calculate diversity within context
            for rule in ctx_rules:
                rule.diversity_score = self.diversity_scorer.calculate_diversity(rule, ctx_rules)
            
            # Normalize & weight
            lift_vals = [r.lift for r in ctx_rules]
            profit_vals = [r.profit_score for r in ctx_rules]
            
            lift_min, lift_max = min(lift_vals), max(lift_vals)
            profit_min, profit_max = min(profit_vals), max(profit_vals)
            
            for rule in ctx_rules:
                norm_lift = (rule.lift - lift_min) / (lift_max - lift_min + 1e-6)
                norm_profit = (rule.profit_score - profit_min) / (profit_max - profit_min + 1e-6)
                
                rule.overall_score = (
                    self.weights['lift'] * norm_lift +
                    self.weights['profit_margin'] * norm_profit +
                    self.weights['diversity'] * rule.diversity_score +
                    self.weights['confidence'] * rule.confidence
                )
            
            scored_rules.extend(ctx_rules)
        
        # Sort all by overall_score
        scored_rules.sort(key=lambda r: r.overall_score, reverse=True)
        return scored_rules
```

**Acceptance:**

- Profit correctly calculated from price × margin × attach rate
- Diversity only considers same-context rules (cross-context overlap OK)
- Overall score normalized within context groups
- High-profit low-frequency rules score higher than low-profit high-frequency

---

## Phase 6: Causal Uplift (T-Learner)

### 6.1 T-Learner Implementation

**app/causal/t_learner.py:**

```python
from sklearn.ensemble import RandomForestClassifier

class TLearner:
    """T-Learner: train separate models for control and treatment groups."""
    
    def __init__(self):
        self.control_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.treatment_model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def fit(self, X_control, y_control, X_treatment, y_treatment):
        """Train models on control and treatment data."""
        self.control_model.fit(X_control, y_control)
        self.treatment_model.fit(X_treatment, y_treatment)
    
    def predict_uplift(self, X):
        """Predict uplift: τ(x) = P(Y=1|T=1,X) - P(Y=1|T=0,X)"""
        p_treatment = self.treatment_model.predict_proba(X)[:, 1]
        p_control = self.control_model.predict_proba(X)[:, 1]
        uplift = p_treatment - p_control
        return uplift
```

### 6.2 Treatment Simulator (Pseudo A/B Test)

**app/causal/treatment_simulator.py:**

```python
class TreatmentSimulator:
    """Simulate control/treatment groups from historical data."""
    
    def simulate_experiment(self, transactions: pd.DataFrame, 
                           rule: ContextualRule) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Simulate A/B test:
        - Find transactions with antecedent items
        - Randomly split 50/50 into control/treatment
        - Outcome = did they buy consequent items
        """
        # Find transactions with antecedent
        antecedent_items = list(rule.antecedent)
        trans_with_antecedent = self._find_transactions_with(transactions, antecedent_items)
        
        # Split 50/50
        shuffled = trans_with_antecedent.sample(frac=1, random_state=42)
        n = len(shuffled) // 2
        control = shuffled.iloc[:n]
        treatment = shuffled.iloc[n:]
        
        # Create outcome: bought consequent?
        consequent_items = list(rule.consequent)
        control['outcome'] = control.apply(lambda row: self._has_items(row, consequent_items), axis=1)
        treatment['outcome'] = treatment.apply(lambda row: self._has_items(row, consequent_items), axis=1)
        
        # Extract features (hour, day_of_week, store, basket_size, etc.)
        control_features = self._extract_features(control)
        treatment_features = self._extract_features(treatment)
        
        return control_features, treatment_features
```

### 6.3 Causal Estimator

**app/causal/causal_estimator.py:**

```python
class CausalEstimator:
    def estimate_uplift(self, rule: ContextualRule, 
                       transactions: pd.DataFrame) -> UpliftResult:
        """
        Estimate true causal effect using T-Learner.
        Returns: incremental attach rate, revenue, margin.
        """
        control_df, treatment_df = self.simulator.simulate_experiment(transactions, rule)
        
        X_control = control_df.drop('outcome', axis=1).values
        y_control = control_df['outcome'].values
        X_treatment = treatment_df.drop('outcome', axis=1).values
        y_treatment = treatment_df['outcome'].values
        
        # Train T-Learner
        self.t_learner.fit(X_control, y_control, X_treatment, y_treatment)
        
        # Calculate metrics
        control_rate = y_control.mean()
        treatment_rate = y_treatment.mean()
        incremental_attach_rate = treatment_rate - control_rate
        
        # Estimate revenue/margin
        consequent_items = list(rule.consequent)
        avg_price = transactions[transactions['item_id'].isin(consequent_items)]['price'].mean()
        avg_margin_pct = 0.25  # From items table or config
        
        incremental_revenue = incremental_attach_rate * avg_price
        incremental_margin = incremental_revenue * avg_margin_pct
        
        return UpliftResult(
            incremental_attach_rate=incremental_attach_rate,
            incremental_revenue=incremental_revenue,
            incremental_margin=incremental_margin,
            control_rate=control_rate,
            treatment_rate=treatment_rate
        )
```

**Acceptance:**

- T-Learner trains on simulated control/treatment data
- Uplift estimates are non-negative (or filtered)
- Unit test: high-correlation-no-causation rule shows low/zero uplift
- Integration test: end-to-end uplift calculation for sample rule

---

## Phase 7: FastAPI Backend

### 7.1 API Models

**app/api/models.py:**

```python
from pydantic import BaseModel
from typing import List, Optional

class RuleFilter(BaseModel):
    store_id: Optional[str] = None
    category: Optional[str] = None
    min_score: float = 0.0
    context_time_bin: Optional[str] = None
    limit: int = 100

class RuleResponse(BaseModel):
    antecedent: List[str]
    consequent: List[str]
    support: float
    confidence: float
    lift: float
    profit_score: float
    overall_score: float
    context: dict
    explanation: str

class BundleResponse(BaseModel):
    items: List[str]
    explanation: str
    priority: str  # High/Medium/Low
    expected_margin: float
    lift: float

class WhatIfRequest(BaseModel):
    promoted_items: List[str]
    discount_pct: float
    time_window: str

class WhatIfResponse(BaseModel):
    estimated_attach_rate_change: float
    estimated_basket_size_change: float
    estimated_margin_impact: float
    affected_rules: List[RuleResponse]
```

### 7.2 API Routes

**app/api/routes.py:**

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/upload")
async def upload_csv(filepath: str):
    """Import CSV and mine rules."""
    importer = CSVImporter(db_path="profitlift.db")
    result = importer.import_csv(filepath)
    return {"success": True, "rows_imported": result.rows_imported}

@router.get("/api/rules", response_model=List[RuleResponse])
async def get_rules(filter: RuleFilter):
    """Retrieve filtered rules from database."""
    # Query association_rules table with filters
    # Generate plain-English explanations
    pass

@router.get("/api/bundles", response_model=List[BundleResponse])
async def get_bundles(store_id: Optional[str] = None, limit: int = 10):
    """Get top bundle recommendations."""
    # Fetch top-scored rules, format as actionable bundles
    pass

@router.post("/api/whatif", response_model=WhatIfResponse)
async def whatif_simulation(request: WhatIfRequest):
    """Run what-if scenario."""
    # Find rules involving promoted items
    # Adjust confidence based on discount
    # Project basket size & margin impact
    pass
```

**app/api/main.py:**

```python
from fastapi import FastAPI
from .routes import router
import uvicorn

app = FastAPI(title="ProfitLift API")
app.include_router(router)

def run():
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

**Acceptance:**

- API starts: `python -m app.api.main`
- `/api/rules` returns filtered rules
- `/api/bundles` returns top recommendations
- `/api/whatif` runs simulation
- OpenAPI docs at http://127.0.0.1:8000/docs

---

## Phase 8: Streamlit UI

### 8.1 Main App

**app/ui/main.py:**

```python
import streamlit as st

st.set_page_config(page_title="ProfitLift", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("Navigation", [
    "📊 Rules Dashboard",
    "🎁 Recommended Bundles",
    "🔮 What-If Simulator",
    "❓ Explanations"
])

if page == "📊 Rules Dashboard":
    from .pages import rules_page
    rules_page.render()
elif page == "🎁 Recommended Bundles":
    from .pages import bundles_page
    bundles_page.render()
elif page == "🔮 What-If Simulator":
    from .pages import whatif_page
    whatif_page.render()
else:
    from .pages import help_page
    help_page.render()
```

### 8.2 Rules Dashboard

**app/ui/pages/rules_page.py:**

```python
import streamlit as st
import requests

def render():
    st.title("Association Rules Dashboard")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        store = st.selectbox("Store", ["All", "STORE_A", "STORE_B"])
    with col2:
        time_bin = st.selectbox("Time", ["All", "morning", "midday", "evening"])
    with col3:
        min_score = st.slider("Min Score", 0.0, 1.0, 0.0)
    
    # Fetch rules from API
    params = {
        "store_id": None if store == "All" else store,
        "context_time_bin": None if time_bin == "All" else time_bin,
        "min_score": min_score,
        "limit": 100
    }
    response = requests.get("http://127.0.0.1:8000/api/rules", params=params)
    rules = response.json()
    
    # Display table
    st.dataframe(rules, use_container_width=True)
    
    # Export buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Export to CSV", data=to_csv(rules), file_name="rules.csv")
    with col2:
        st.download_button("Export to PDF", data=to_pdf(rules), file_name="rules.pdf")
```

### 8.3 Bundles View

**app/ui/pages/bundles_page.py:**

```python
def render():
    st.title("Recommended Bundles")
    
    response = requests.get("http://127.0.0.1:8000/api/bundles", params={"limit": 20})
    bundles = response.json()
    
    for bundle in bundles:
        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[bundle['priority']]
        
        with st.container():
            st.markdown(f"### {priority_color} {bundle['priority']} Priority")
            st.write(f"**Bundle:** {', '.join(bundle['items'])}")
            st.write(bundle['explanation'])
            st.caption(f"Expected Margin: ${bundle['expected_margin']:.2f} | Lift: {bundle['lift']:.1f}x")
            st.divider()
```

### 8.4 What-If Simulator

**app/ui/pages/whatif_page.py:**

```python
def render():
    st.title("What-If Simulator")
    
    # Inputs
    item = st.selectbox("Promoted Item", ["Milk", "Bread", "Cereal"])
    discount = st.slider("Discount %", 0, 50, 10)
    time_window = st.selectbox("Time Window", ["Overall", "Weekend Morning", "Weekday Evening"])
    
    if st.button("Run Simulation", type="primary"):
        payload = {
            "promoted_items": [item],
            "discount_pct": discount / 100.0,
            "time_window": time_window
        }
        response = requests.post("http://127.0.0.1:8000/api/whatif", json=payload)
        result = response.json()
        
        # Display results
        col1, col2, col3 = st.columns(3)
        col1.metric("Attach Rate Change", f"+{result['estimated_attach_rate_change']:.1%}")
        col2.metric("Basket Size Change", f"+{result['estimated_basket_size_change']:.1f}")
        col3.metric("Margin Impact", f"${result['estimated_margin_impact']:.2f}")
        
        st.subheader("Affected Rules")
        st.dataframe(result['affected_rules'])
```

**Acceptance:**

- `streamlit run app/ui/main.py` launches UI
- All pages render correctly
- API calls successful
- Filters work
- Export buttons generate CSV/PDF
- UI is clean and professional

---

## Phase 9: Windows Build (GitHub Actions)

### 9.1 GitHub Actions Workflow

**.github/workflows/windows-build.yml:**

```yaml
name: Build Windows Installer

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Build with PyInstaller
        run: |
          pyinstaller --name ProfitLift --onefile --windowed --icon=app/assets/icon.ico app/ui/main.py
      
      - name: Create installer with Inno Setup
        run: |
          iscc installer.iss
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: ProfitLift-Installer
          path: Output/ProfitLift-Setup.exe
```

### 9.2 Inno Setup Script

**installer.iss:**

```ini
[Setup]
AppName=ProfitLift
AppVersion=1.0
DefaultDirName={pf}\ProfitLift
DefaultGroupName=ProfitLift
OutputDir=Output
OutputBaseFilename=ProfitLift-Setup

[Files]
Source: "dist\ProfitLift.exe"; DestDir: "{app}"
Source: "data\sample\sample_1k.csv"; DestDir: "{app}\data\sample"
Source: "config\*.yaml"; DestDir: "{app}\config"

[Icons]
Name: "{group}\ProfitLift"; Filename: "{app}\ProfitLift.exe"
```

**Acceptance:**

- GitHub Actions workflow runs on tag push
- Windows EXE generated
- Installer bundles EXE + sample data + config
- Installer tested on clean Windows machine

---

## Phase 10: Documentation

### 10.1 Core Docs

**README.md:** Dev setup, quickstart, architecture overview

**METHODS.md:** Equations, algorithms, scoring formula, uplift methodology

**DESIGN.md:** System architecture, interfaces, data flow diagrams

**METRICS.md:** Evaluation protocol, metrics definitions, baseline comparison

**DECISIONS.md:** Design rationale (why Streamlit, why T-Learner, why FP-Growth+Eclat)

**DEMO_SCRIPT.md:** 1-minute walkthrough for live demo

### 10.2 Data Acquisition

**docs/how_to_get_data.md:**

```markdown
# Benchmark Datasets

## Instacart
1. Visit https://www.instacart.com/datasets/grocery-shopping-2017
2. Download `orders.csv`, `order_products.csv`, `products.csv`
3. Place in `data/instacart/`
4. Run `python -m app.ingest.loaders.instacart_loader`

## Dunnhumby
1. Visit https://www.dunnhumby.com/source-files/
2. Download "The Complete Journey" dataset
3. Place in `data/dunnhumby/`
4. Run `python -m app.ingest.loaders.dunnhumby_loader`
```

**Acceptance:**

- All docs created and reviewed
- Equations in METHODS.md match implementation
- DEMO_SCRIPT.md covers full workflow in 1 minute

---

## Phase 11: Testing & Evaluation

### 11.1 Unit Tests

**app/tests/test_mining.py:** Validate FP-Growth & Eclat produce same itemsets

**app/tests/test_scoring.py:** Verify profit calculation, diversity within-context

**app/tests/test_causal.py:** T-Learner uplift estimation, zero uplift for spurious correlation

**app/tests/test_context.py:** Segmentation, backoff to broader context when <100 rows

### 11.2 Integration Tests

**app/tests/test_pipeline.py:** CSV import → mining → scoring → storage → API retrieval

**app/tests/test_api.py:** All endpoints return correct responses

### 11.3 Evaluation

**app/tests/test_evaluation.py:**

```python
def test_profit_contribution():
    # Compare ProfitLift vs baseline MBA on Instacart
    # Metric: total profit from top-K recommendations
    
def test_incremental_revenue():
    # Simulated A/B test: measure incremental revenue
    
def test_uplift_accuracy():
    # Synthetic data with known uplift
    # Verify T-Learner estimates are within ±5%
```

**Acceptance:**

- Test coverage >80%
- All critical paths tested
- Evaluation shows improvement over baseline MBA

---

## Key Implementation Notes

### Algorithm Focus

- **Primary:** FP-Growth (fast, mature, mlxtend)
- **Secondary:** Eclat (validation, academic rigor)
- **Removed:** Apriori (slower, redundant)

### Uplift Approach

- **Baseline:** T-Learner with RandomForest (simple, effective, well-documented)
- **Stretch:** DR-Learner (if time permits, config flag)
- **No external libs:** Pure scikit-learn (no econml/causalml dependency)

### UI Rationale

- **Streamlit** > PyQt6: Faster development, cleaner code, easier to package, zero Qt licensing concerns
- **Local API:** FastAPI runs locally, Streamlit calls it (no cloud dependency)

### Scoring Clarity

- **Diversity:** Only within same context (don't penalize "milk→bread" in morning AND evening)
- **Normalization:** Per-context groups to avoid cross-context bias

### Data Privacy

- No PII required (IDs optional, hashed)
- Sample data anonymized

### Packaging

- GitHub Actions → Windows EXE (automated)
- Inno Setup → Professional installer
- Bundle: EXE + sample_1k.csv + config

---

## Success Criteria

**Academic (Viva-Proof):**

- Context-aware mining implemented and validated
- Multi-objective scoring with clear formula
- Causal uplift analysis (T-Learner) with evaluation
- Reproducible: README → running system in <30 min
- Evaluation shows improvement over baseline

**Business (Client-Ready):**

- Windows app runs on clean machine
- Imports CSV, shows rules, exports bundles
- What-if simulator projects outcomes
- Plain-English explanations for non-technical users
- Weekly opportunity list downloadable

**Engineering:**

- Test coverage >80%
- Clean separation: ingest / mining / score / causal / api / ui
- Config-driven (no hardcoded params)
- GitHub Actions builds Windows installer automatically

### To-dos

- [ ] Create app/ structure (ingest, mining, score, causal, sim, api, ui, tests, assets), config/, docs/, data/sample/, pyproject.toml, requirements.txt, .gitignore
- [ ] Implement schema.sql with items table, transactions, transaction_items, association_rules, uplift_results; create database manager
- [ ] Build CSV importer with validation, context enrichment (time_bin, weekday_weekend, quarter), items table population
- [ ] Implement FP-Growth miner using mlxtend (mine itemsets, generate rules)
- [ ] Implement Eclat miner with vertical format (validation algorithm)
- [ ] Build context segmenter (store, time, store×time, weekday×time, quarter) with min_rows backoff, context-aware miner
- [ ] Implement profit calculator, diversity scorer (within-context only), multi-objective scorer with per-context normalization
- [ ] Implement T-Learner (RandomForest), treatment simulator, causal estimator for incremental effect
- [ ] Build FastAPI app: /api/upload, /api/rules, /api/bundles, /api/whatif with Pydantic models
- [ ] Create Streamlit pages: main.py, rules_page, bundles_page, whatif_page, help_page with API client
- [ ] Implement CSV and PDF export for rules, bundles, what-if results (ReportLab)
- [ ] Write unit tests (mining, scoring, causal, context) and integration tests (pipeline, API) with >80% coverage
- [ ] Create windows-build.yml workflow with PyInstaller + Inno Setup, test on clean Windows VM
- [ ] Write README.md, METHODS.md, DESIGN.md, METRICS.md, DECISIONS.md, DEMO_SCRIPT.md, how_to_get_data.md
- [ ] Run benchmarks on Instacart/Dunnhumby, compare vs baseline MBA, document results in METRICS.md