<!-- b98db277-5ca9-432b-8c6f-ba72e8315014 940e31be-ddf4-4317-97a3-ab1363462533 -->
# ProfitLift: Context-Aware Profit-Optimized MBA System

## Executive Summary

Build a complete final year project that combines academic innovation (context-aware MBA with causal analysis from soul.md) and business utility (Windows desktop app from idea.md). The system mines association rules with contextual awareness (time, store, season), optimizes for profit rather than just frequency, and uses uplift modeling to distinguish causation from correlation.

**Core Innovation**: Traditional MBA finds "milk → bread" patterns. ProfitLift finds "milk → cereal on weekend mornings in suburban stores during Q1, with $2.30 incremental margin and 15% true uplift."

---

## Phase 1: Foundation & Project Setup

### 1.1 Directory Structure

Create this exact structure:

```
ProfitLift/
├── README.md                          # Project overview, setup instructions
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package installation
├── .gitignore                        # Git ignore file
├── config/
│   ├── default_config.yaml           # Default configuration
│   └── scoring_weights.yaml          # Multi-objective scoring weights
├── backend/
│   ├── __init__.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── apriori.py               # Apriori implementation
│   │   ├── fpgrowth.py              # FP-Growth implementation
│   │   ├── eclat.py                 # Eclat implementation
│   │   └── rule_generator.py        # Association rule generation
│   ├── context_engine/
│   │   ├── __init__.py
│   │   ├── context_segmenter.py     # Transaction segmentation by context
│   │   ├── context_miner.py         # Context-aware rule mining
│   │   └── context_types.py         # Context dimension definitions
│   ├── scoring/
│   │   ├── __init__.py
│   │   ├── multi_objective.py       # Multi-objective scoring function
│   │   ├── profit_calculator.py     # Profit margin calculation
│   │   └── diversity_scorer.py      # Diversity metric
│   ├── uplift/
│   │   ├── __init__.py
│   │   ├── uplift_model.py          # Uplift modeling (two-model, uplift trees)
│   │   ├── causal_estimator.py      # Incremental effect estimation
│   │   └── treatment_simulator.py   # Simulate control/treatment groups
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── csv_importer.py          # CSV validation and import
│   │   ├── data_validator.py        # Data quality checks
│   │   ├── streaming_processor.py   # Incremental updates
│   │   └── file_watcher.py          # Monitor new data files
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py              # SQLite database manager
│   │   └── schema.sql               # Database schema
│   └── api/
│       ├── __init__.py
│       ├── main.py                  # FastAPI application
│       ├── routes.py                # API endpoints
│       └── models.py                # Pydantic models for requests/responses
├── desktop/
│   ├── __init__.py
│   ├── main.py                      # Desktop app entry point
│   ├── main_window.py               # Main window with navigation
│   ├── views/
│   │   ├── __init__.py
│   │   ├── rules_view.py            # Rules Dashboard
│   │   ├── bundles_view.py          # Recommended Bundles
│   │   ├── whatif_view.py           # What-If Simulator
│   │   └── explanations_view.py     # Explanations & Help
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── filter_panel.py          # Reusable filter widget
│   │   ├── export_dialog.py         # Export dialog (CSV/PDF)
│   │   └── bundle_card.py           # Bundle recommendation card
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py            # Backend API client
│   │   └── pdf_exporter.py          # PDF generation with ReportLab
│   └── resources/
│       ├── icons/                    # App icons
│       └── styles.qss                # PyQt6 stylesheet
├── data/
│   ├── sample/
│   │   ├── sample_1000.csv          # 1K transactions for testing
│   │   └── sample_50000.csv         # 50K transactions for demo
│   ├── instacart/
│   │   ├── download.py              # Download Instacart dataset
│   │   └── loader.py                # Transform to unified format
│   └── dunnhumby/
│       ├── download.py              # Download Dunnhumby dataset
│       └── loader.py                # Transform to unified format
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py                   # Evaluation metrics
│   ├── benchmark.py                 # Run benchmarks on datasets
│   ├── synthetic_promo.py           # Generate synthetic promotion data
│   └── comparison.py                # Compare vs baseline MBA
├── tests/
│   ├── __init__.py
│   ├── test_algorithms.py           # Test Apriori, FP-Growth, Eclat
│   ├── test_context_engine.py       # Test context mining
│   ├── test_scoring.py              # Test multi-objective scoring
│   ├── test_uplift.py               # Test uplift modeling
│   ├── test_pipeline.py             # Test CSV import, validation
│   ├── test_api.py                  # Test FastAPI endpoints
│   └── test_integration.py          # End-to-end integration tests
├── docs/
│   ├── academic/
│   │   ├── technical_report.md      # Full methodology
│   │   ├── literature_review.md     # Related work
│   │   ├── reproducibility.md       # How to replicate results
│   │   └── architecture_diagram.png # System architecture
│   ├── user/
│   │   ├── user_manual.md           # Complete user guide
│   │   ├── quick_start.md           # 5-minute tutorial
│   │   ├── troubleshooting.md       # Common issues
│   │   └── glossary.md              # Term definitions
│   └── presentation/
│       ├── slides.pptx              # Presentation for professors
│       └── demo_script.md           # Live demo walkthrough
└── scripts/
    ├── build_windows.py             # PyInstaller build script
    ├── run_tests.py                 # Run all tests
    └── generate_sample_data.py      # Create sample datasets
```

### 1.2 Initial Files to Create

**requirements.txt**:

```
# Core dependencies
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0

# MBA algorithms
mlxtend>=0.22.0

# Machine learning
scikit-learn>=1.3.0
lightgbm>=4.0.0  # For uplift modeling

# Backend API
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0

# Desktop GUI
PyQt6>=6.5.0
matplotlib>=3.7.0
plotly>=5.15.0

# PDF export
reportlab>=4.0.0

# Database
sqlalchemy>=2.0.0

# File watching
watchdog>=3.0.0

# Configuration
pyyaml>=6.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-qt>=4.2.0

# Code quality
black>=23.7.0
flake8>=6.0.0
mypy>=1.4.0

# Build
pyinstaller>=5.13.0
```

**config/default_config.yaml**:

```yaml
# ProfitLift Configuration

database:
  path: "profitlift.db"
  
data:
  min_support: 0.01
  min_confidence: 0.3
  min_lift: 1.1
  
context:
  time_bins:
    - "morning"     # 6-11am
    - "midday"      # 11am-2pm
    - "afternoon"   # 2-6pm
    - "evening"     # 6-10pm
  weekday_weekend: true
  seasonal_quarters: true
  store_clustering: true
  
scoring:
  weights_file: "config/scoring_weights.yaml"
  
uplift:
  method: "two_model"  # or "uplift_tree", "uplift_rf"
  min_incremental_lift: 0.05
  
streaming:
  enabled: true
  check_interval_seconds: 300
  
api:
  host: "127.0.0.1"
  port: 8000
  
export:
  pdf_logo: null
  pdf_footer: "Generated by ProfitLift"
```

**config/scoring_weights.yaml**:

```yaml
# Multi-objective scoring weights (must sum to 1.0)
weights:
  lift: 0.30
  profit_margin: 0.40
  diversity: 0.15
  confidence: 0.15

# Profit calculation
profit:
  default_margin_pct: 0.25  # If margin not provided
  category_margins:  # Override per category if available
    "Dairy": 0.30
    "Produce": 0.40
    "Meat": 0.20
```

### 1.3 Setup Script

**setup.py**:

```python
from setuptools import setup, find_packages

setup(
    name="profitlift",
    version="1.0.0",
    description="Context-Aware Profit-Optimized Market Basket Analysis",
    author="Shenz",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        # Read from requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "profitlift=desktop.main:main",
            "profitlift-api=backend.api.main:run",
        ],
    },
)
```

**Acceptance Criteria for Phase 1**:

- [ ] All directories and files created as specified
- [ ] Virtual environment activated
- [ ] All dependencies install without errors: `pip install -r requirements.txt`
- [ ] Python can import empty packages: `python -c "import backend, desktop"`
- [ ] Configuration files parse correctly with PyYAML

---

## Phase 2: Data Layer

### 2.1 Database Schema

**backend/storage/schema.sql**:

```sql
-- Transactions table
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    store_id TEXT NOT NULL,
    customer_id_hash TEXT,  -- Optional, hashed
    total_value REAL,
    discount_flag INTEGER DEFAULT 0,
    context_time_bin TEXT,
    context_weekday_weekend TEXT,
    context_quarter TEXT
);

-- Transaction items table
CREATE TABLE transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    item_name TEXT,
    category TEXT,
    quantity INTEGER DEFAULT 1,
    price REAL NOT NULL,
    margin_pct REAL,  -- Optional
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

-- Association rules table
CREATE TABLE association_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    antecedent TEXT NOT NULL,  -- JSON array of item IDs
    consequent TEXT NOT NULL,  -- JSON array of item IDs
    support REAL NOT NULL,
    confidence REAL NOT NULL,
    lift REAL NOT NULL,
    profit_score REAL,
    diversity_score REAL,
    overall_score REAL,
    context_store_id TEXT,
    context_time_bin TEXT,
    context_weekday_weekend TEXT,
    context_quarter TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Uplift results table
CREATE TABLE uplift_results (
    rule_id INTEGER PRIMARY KEY,
    incremental_attach_rate REAL,
    incremental_revenue REAL,
    incremental_margin REAL,
    control_rate REAL,
    treatment_rate REAL,
    FOREIGN KEY (rule_id) REFERENCES association_rules(id)
);

-- Indexes for performance
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX idx_transactions_store ON transactions(store_id);
CREATE INDEX idx_items_transaction ON transaction_items(transaction_id);
CREATE INDEX idx_items_item ON transaction_items(item_id);
CREATE INDEX idx_rules_score ON association_rules(overall_score DESC);
CREATE INDEX idx_rules_context ON association_rules(context_store_id, context_time_bin);
```

### 2.2 CSV Import Specification

**Expected CSV Format** (backend/pipeline/csv_importer.py should validate):

```csv
transaction_id,timestamp,store_id,customer_id_hash,item_id,item_name,category,quantity,price,discount_flag,margin_pct
T001,2024-01-15 08:30:00,STORE_A,hash123,ITEM_001,Milk,Dairy,1,3.99,0,0.30
T001,2024-01-15 08:30:00,STORE_A,hash123,ITEM_002,Bread,Bakery,2,2.49,0,0.25
T002,2024-01-15 09:15:00,STORE_A,,ITEM_003,Cereal,Breakfast,1,4.99,1,0.35
```

**Required Columns**:

- `transaction_id` (TEXT): Unique per basket
- `timestamp` (DATETIME): ISO format or common formats
- `store_id` (TEXT): Store identifier
- `item_id` (TEXT): Product identifier
- `price` (REAL): Price paid per unit

**Optional Columns**:

- `customer_id_hash` (TEXT): Anonymized customer ID
- `item_name` (TEXT): Human-readable name
- `category` (TEXT): Product category
- `quantity` (INTEGER): Defaults to 1
- `discount_flag` (0/1): Whether item was discounted
- `margin_pct` (REAL): Profit margin percentage (0.0-1.0)

**Validation Rules** in `data_validator.py`:

1. No missing required columns
2. `transaction_id` must not be empty
3. `timestamp` must parse to valid datetime
4. `price` must be > 0
5. `margin_pct` if present must be in [0, 1]
6. No PII (check for email patterns, phone numbers)
7. Warn if >20% missing `margin_pct` (will use defaults)

### 2.3 Data Loader Classes

**backend/pipeline/csv_importer.py**:

```python
class CSVImporter:
    """Import and validate CSV transaction data."""
    
    def __init__(self, db_path: str, validator: DataValidator):
        self.db = DatabaseManager(db_path)
        self.validator = validator
    
    def import_csv(self, filepath: str) -> ImportResult:
        """
        Import CSV file, validate, transform, and store in database.
        
        Returns:
            ImportResult with stats: rows_imported, rows_rejected, errors
        """
        # 1. Read CSV with pandas
        # 2. Validate using self.validator
        # 3. Add context columns (time_bin, weekday/weekend, quarter)
        # 4. Insert into transactions and transaction_items tables
        # 5. Return ImportResult
        pass
    
    def _add_context_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add context dimension columns based on timestamp."""
        df['context_time_bin'] = df['timestamp'].apply(self._get_time_bin)
        df['context_weekday_weekend'] = df['timestamp'].apply(
            lambda x: 'weekend' if x.weekday() >= 5 else 'weekday'
        )
        df['context_quarter'] = df['timestamp'].dt.quarter
        return df
    
    def _get_time_bin(self, timestamp) -> str:
        """Map hour to time bin."""
        hour = timestamp.hour
        if 6 <= hour < 11: return 'morning'
        elif 11 <= hour < 14: return 'midday'
        elif 14 <= hour < 18: return 'afternoon'
        elif 18 <= hour < 22: return 'evening'
        else: return 'night'
```

**Acceptance Criteria for Phase 2**:

- [ ] SQLite database created with schema
- [ ] CSVImporter can load sample CSV and populate database
- [ ] All validation rules enforced, errors reported clearly
- [ ] Context columns correctly derived from timestamp
- [ ] Can query imported data: `SELECT COUNT(*) FROM transactions`

---

## Phase 3: Traditional MBA Algorithms (Baseline)

### 3.1 Algorithm Implementations

**backend/algorithms/fpgrowth.py**:

```python
from mlxtend.frequent_patterns import fpgrowth, association_rules
import pandas as pd

class FPGrowthMiner:
    """FP-Growth algorithm for frequent pattern mining."""
    
    def __init__(self, min_support: float = 0.01):
        self.min_support = min_support
    
    def mine_patterns(self, transactions: List[List[str]]) -> pd.DataFrame:
        """
        Mine frequent itemsets using FP-Growth.
        
        Args:
            transactions: List of transaction item lists
            
        Returns:
            DataFrame with columns: itemset, support
        """
        # 1. Convert to one-hot encoded DataFrame
        basket = self._create_basket_matrix(transactions)
        
        # 2. Run FP-Growth
        frequent_itemsets = fpgrowth(basket, min_support=self.min_support, use_colnames=True)
        
        return frequent_itemsets
    
    def generate_rules(self, frequent_itemsets: pd.DataFrame, 
                      min_confidence: float = 0.3) -> pd.DataFrame:
        """Generate association rules from frequent itemsets."""
        rules = association_rules(frequent_itemsets, metric="confidence", 
                                 min_threshold=min_confidence)
        
        # Add lift calculation
        rules['lift'] = rules['confidence'] / rules['consequent support']
        
        return rules
    
    def _create_basket_matrix(self, transactions: List[List[str]]) -> pd.DataFrame:
        """Convert transaction list to one-hot encoded matrix."""
        # Create binary matrix where rows=transactions, cols=items
        # Value is 1 if item in transaction, 0 otherwise
        pass
```

**backend/algorithms/apriori.py**:

```python
from mlxtend.frequent_patterns import apriori

class AprioriMiner:
    """Apriori algorithm (baseline comparison)."""
    
    def mine_patterns(self, transactions: List[List[str]], 
                     min_support: float = 0.01) -> pd.DataFrame:
        """Mine frequent itemsets using Apriori."""
        basket = self._create_basket_matrix(transactions)
        frequent_itemsets = apriori(basket, min_support=min_support, use_colnames=True)
        return frequent_itemsets
```

**backend/algorithms/eclat.py**:

```python
class EclatMiner:
    """Eclat algorithm using vertical data format."""
    
    def mine_patterns(self, transactions: List[List[str]], 
                     min_support: float = 0.01) -> pd.DataFrame:
        """Mine frequent itemsets using Eclat."""
        # 1. Convert to vertical format (item -> set of transaction IDs)
        vertical_db = self._create_vertical_db(transactions)
        
        # 2. Find frequent itemsets by intersecting transaction ID sets
        frequent_itemsets = self._eclat_recursive(vertical_db, min_support)
        
        return frequent_itemsets
    
    def _create_vertical_db(self, transactions: List[List[str]]) -> Dict[str, Set[int]]:
        """Convert to vertical format: {item: {tid1, tid2, ...}}"""
        vertical = {}
        for tid, items in enumerate(transactions):
            for item in items:
                if item not in vertical:
                    vertical[item] = set()
                vertical[item].add(tid)
        return vertical
```

### 3.2 Rule Generator

**backend/algorithms/rule_generator.py**:

```python
class RuleGenerator:
    """Generate association rules with standard metrics."""
    
    @staticmethod
    def calculate_metrics(rule: Dict, transactions: List[List[str]]) -> Dict:
        """
        Calculate support, confidence, lift for a rule.
        
        Args:
            rule: {'antecedent': ['item1'], 'consequent': ['item2']}
            transactions: All transactions
            
        Returns:
            Dict with support, confidence, lift, antecedent_support, consequent_support
        """
        n_transactions = len(transactions)
        
        # Count occurrences
        count_antecedent = sum(1 for t in transactions if all(i in t for i in rule['antecedent']))
        count_consequent = sum(1 for t in transactions if all(i in t for i in rule['consequent']))
        count_both = sum(1 for t in transactions if 
                        all(i in t for i in rule['antecedent'] + rule['consequent']))
        
        # Calculate metrics
        support = count_both / n_transactions
        antecedent_support = count_antecedent / n_transactions
        consequent_support = count_consequent / n_transactions
        confidence = count_both / count_antecedent if count_antecedent > 0 else 0
        lift = confidence / consequent_support if consequent_support > 0 else 0
        
        return {
            'support': support,
            'confidence': confidence,
            'lift': lift,
            'antecedent_support': antecedent_support,
            'consequent_support': consequent_support
        }
```

**Acceptance Criteria for Phase 3**:

- [ ] FP-Growth mines frequent itemsets from sample data
- [ ] Apriori produces same results as FP-Growth (validation)
- [ ] Eclat produces same results (validation)
- [ ] Rules generated with correct support/confidence/lift values
- [ ] Unit tests verify metrics calculations with known examples
- [ ] Performance: processes 50K transactions in <30 seconds

---

## Phase 4: Context-Aware Mining

### 4.1 Context Segmentation

**backend/context_engine/context_types.py**:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Context:
    """Represents a context dimension combination."""
    store_id: Optional[str] = None
    time_bin: Optional[str] = None  # morning, midday, afternoon, evening
    weekday_weekend: Optional[str] = None  # weekday, weekend
    quarter: Optional[int] = None  # 1-4
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    def matches(self, transaction: Dict) -> bool:
        """Check if transaction matches this context."""
        if self.store_id and transaction['store_id'] != self.store_id:
            return False
        if self.time_bin and transaction['context_time_bin'] != self.time_bin:
            return False
        if self.weekday_weekend and transaction['context_weekday_weekend'] != self.weekday_weekend:
            return False
        if self.quarter and transaction['context_quarter'] != self.quarter:
            return False
        return True
```

**backend/context_engine/context_segmenter.py**:

```python
class ContextSegmenter:
    """Segment transactions by context dimensions."""
    
    def segment(self, transactions: pd.DataFrame) -> Dict[Context, pd.DataFrame]:
        """
        Segment transactions into context-specific groups.
        
        Returns:
            Dictionary mapping Context -> DataFrame of transactions in that context
        """
        segments = {}
        
        # Get unique values for each dimension
        stores = transactions['store_id'].unique()
        time_bins = transactions['context_time_bin'].unique()
        weekday_weekends = transactions['context_weekday_weekend'].unique()
        quarters = transactions['context_quarter'].unique()
        
        # Create segments for meaningful combinations
        # 1. Overall (no context filter)
        segments[Context()] = transactions
        
        # 2. By store only
        for store in stores:
            ctx = Context(store_id=store)
            segments[ctx] = transactions[transactions['store_id'] == store]
        
        # 3. By time bin only
        for time_bin in time_bins:
            ctx = Context(time_bin=time_bin)
            segments[ctx] = transactions[transactions['context_time_bin'] == time_bin]
        
        # 4. By store + time bin (important combination)
        for store in stores:
            for time_bin in time_bins:
                ctx = Context(store_id=store, time_bin=time_bin)
                df = transactions[
                    (transactions['store_id'] == store) &
                    (transactions['context_time_bin'] == time_bin)
                ]
                if len(df) >= 100:  # Minimum transactions for reliability
                    segments[ctx] = df
        
        # 5. By weekday/weekend + time bin
        for wdwe in weekday_weekends:
            for time_bin in time_bins:
                ctx = Context(weekday_weekend=wdwe, time_bin=time_bin)
                df = transactions[
                    (transactions['context_weekday_weekend'] == wdwe) &
                    (transactions['context_time_bin'] == time_bin)
                ]
                if len(df) >= 100:
                    segments[ctx] = df
        
        # 6. By quarter (seasonal)
        for quarter in quarters:
            ctx = Context(quarter=quarter)
            segments[ctx] = transactions[transactions['context_quarter'] == quarter]
        
        return segments
```

### 4.2 Context-Aware Miner

**backend/context_engine/context_miner.py**:

```python
class ContextAwareMiner:
    """Mine association rules within each context."""
    
    def __init__(self, base_miner: FPGrowthMiner, segmenter: ContextSegmenter):
        self.base_miner = base_miner
        self.segmenter = segmenter
    
    def mine_all_contexts(self, transactions: pd.DataFrame) -> List[ContextualRule]:
        """
        Mine rules in all context segments.
        
        Returns:
            List of ContextualRule objects with context tags
        """
        segments = self.segmenter.segment(transactions)
        all_rules = []
        
        for context, segment_df in segments.items():
            # Convert to transaction list format
            trans_list = self._df_to_transaction_list(segment_df)
            
            # Mine patterns in this context
            patterns = self.base_miner.mine_patterns(trans_list)
            
            # Generate rules
            rules = self.base_miner.generate_rules(patterns)
            
            # Tag with context
            for _, rule in rules.iterrows():
                contextual_rule = ContextualRule(
                    antecedent=frozenset(rule['antecedents']),
                    consequent=frozenset(rule['consequents']),
                    support=rule['support'],
                    confidence=rule['confidence'],
                    lift=rule['lift'],
                    context=context
                )
                all_rules.append(contextual_rule)
        
        return all_rules
    
    def _df_to_transaction_list(self, df: pd.DataFrame) -> List[List[str]]:
        """Convert DataFrame to list of item lists grouped by transaction_id."""
        grouped = df.groupby('transaction_id')['item_id'].apply(list)
        return grouped.tolist()

@dataclass
class ContextualRule:
    """Association rule with context tags."""
    antecedent: FrozenSet[str]
    consequent: FrozenSet[str]
    support: float
    confidence: float
    lift: float
    context: Context
    profit_score: Optional[float] = None
    diversity_score: Optional[float] = None
    overall_score: Optional[float] = None
```

**Acceptance Criteria for Phase 4**:

- [ ] ContextSegmenter creates meaningful segments (store, time, season combinations)
- [ ] Each segment has ≥100 transactions (configurable minimum)
- [ ] ContextAwareMiner produces rules for each segment
- [ ] Rules correctly tagged with context metadata
- [ ] Unit test: verify "milk→bread" has different lift in "morning" vs "evening"

---

## Phase 5: Multi-Objective Scoring

### 5.1 Profit Calculator

**backend/scoring/profit_calculator.py**:

```python
class ProfitCalculator:
    """Calculate expected incremental profit for rules."""
    
    def __init__(self, default_margin: float = 0.25, 
                 category_margins: Dict[str, float] = None):
        self.default_margin = default_margin
        self.category_margins = category_margins or {}
    
    def calculate_rule_profit(self, rule: ContextualRule, 
                            transactions: pd.DataFrame) -> float:
        """
        Calculate expected incremental profit per basket for rule.
        
        Formula:
            Profit = Avg(consequent_price) * Margin% * Incremental_Attach_Rate
        
        Returns:
            Expected incremental profit in currency units
        """
        # Get consequent items
        consequent_items = list(rule.consequent)
        
        # Find transactions with these items to get avg price and margin
        mask = transactions['item_id'].isin(consequent_items)
        consequent_data = transactions[mask]
        
        if len(consequent_data) == 0:
            return 0.0
        
        # Calculate average price
        avg_price = consequent_data['price'].mean()
        
        # Get margin (use item margin if available, else category, else default)
        if 'margin_pct' in consequent_data.columns and consequent_data['margin_pct'].notna().any():
            avg_margin = consequent_data['margin_pct'].mean()
        elif 'category' in consequent_data.columns:
            categories = consequent_data['category'].unique()
            margins = [self.category_margins.get(cat, self.default_margin) for cat in categories]
            avg_margin = np.mean(margins)
        else:
            avg_margin = self.default_margin
        
        # Incremental attach rate = confidence (how often consequent appears with antecedent)
        incremental_attach = rule.confidence
        
        # Expected profit
        profit = avg_price * avg_margin * incremental_attach
        
        return profit
```

### 5.2 Diversity Scorer

**backend/scoring/diversity_scorer.py**:

```python
class DiversityScorer:
    """Penalize over-representation of same items in recommendations."""
    
    def __init__(self):
        self.item_frequency = {}  # Track how often items recommended
    
    def calculate_diversity(self, rule: ContextualRule, 
                          all_rules: List[ContextualRule]) -> float:
        """
        Calculate diversity score (0-1, higher = more diverse).
        
        Penalize rules where items appear in many other rules.
        """
        # Get all items in this rule
        rule_items = set(rule.antecedent) | set(rule.consequent)
        
        # Count how often each item appears across all rules
        item_counts = {}
        total_rules = len(all_rules)
        
        for r in all_rules:
            items = set(r.antecedent) | set(r.consequent)
            for item in items:
                item_counts[item] = item_counts.get(item, 0) + 1
        
        # Calculate diversity: inverse of average frequency
        frequencies = [item_counts.get(item, 1) / total_rules for item in rule_items]
        avg_frequency = np.mean(frequencies)
        
        # Diversity score: 1 = unique items, 0 = appears in all rules
        diversity = 1.0 - avg_frequency
        
        return max(0.0, diversity)  # Ensure non-negative
```

### 5.3 Multi-Objective Scorer

**backend/scoring/multi_objective.py**:

```python
class MultiObjectiveScorer:
    """Combine lift, profit, diversity, confidence into single score."""
    
    def __init__(self, weights: Dict[str, float], 
                 profit_calc: ProfitCalculator,
                 diversity_scorer: DiversityScorer):
        """
        Args:
            weights: {'lift': 0.3, 'profit_margin': 0.4, 'diversity': 0.15, 'confidence': 0.15}
        """
        assert abs(sum(weights.values()) - 1.0) < 0.01, "Weights must sum to 1.0"
        self.weights = weights
        self.profit_calc = profit_calc
        self.diversity_scorer = diversity_scorer
    
    def score_rules(self, rules: List[ContextualRule], 
                   transactions: pd.DataFrame) -> List[ContextualRule]:
        """
        Score all rules and add profit_score, diversity_score, overall_score.
        
        Returns:
            Rules sorted by overall_score descending
        """
        # First pass: calculate profit for all rules
        for rule in rules:
            rule.profit_score = self.profit_calc.calculate_rule_profit(rule, transactions)
        
        # Second pass: calculate diversity (needs all rules)
        for rule in rules:
            rule.diversity_score = self.diversity_scorer.calculate_diversity(rule, rules)
        
        # Normalize metrics to [0, 1] for fair weighting
        lift_values = [r.lift for r in rules]
        profit_values = [r.profit_score for r in rules]
        diversity_values = [r.diversity_score for r in rules]
        confidence_values = [r.confidence for r in rules]
        
        lift_min, lift_max = min(lift_values), max(lift_values)
        profit_min, profit_max = min(profit_values), max(profit_values)
        
        for rule in rules:
            # Normalize
            norm_lift = (rule.lift - lift_min) / (lift_max - lift_min + 1e-6)
            norm_profit = (rule.profit_score - profit_min) / (profit_max - profit_min + 1e-6)
            norm_diversity = rule.diversity_score  # Already 0-1
            norm_confidence = rule.confidence  # Already 0-1
            
            # Weighted sum
            rule.overall_score = (
                self.weights['lift'] * norm_lift +
                self.weights['profit_margin'] * norm_profit +
                self.weights['diversity'] * norm_diversity +
                self.weights['confidence'] * norm_confidence
            )
        
        # Sort by overall score
        rules.sort(key=lambda r: r.overall_score, reverse=True)
        
        return rules
```

**Acceptance Criteria for Phase 5**:

- [ ] ProfitCalculator correctly computes profit from price × margin × attach rate
- [ ] DiversityScorer penalizes frequently occurring items
- [ ] MultiObjectiveScorer produces normalized overall_score
- [ ] Unit test: high-profit low-frequency rule scores higher than low-profit high-frequency
- [ ] Weights from config file correctly applied

---

## Phase 6: Uplift Modeling (Causal Analysis)

### 6.1 Uplift Model

**backend/uplift/uplift_model.py**:

```python
from sklearn.ensemble import RandomForestClassifier

class UpliftModel:
    """Estimate causal effect of recommendations using uplift modeling."""
    
    def __init__(self, method: str = "two_model"):
        """
        Args:
            method: "two_model", "uplift_tree", or "uplift_rf"
        """
        self.method = method
        self.control_model = None
        self.treatment_model = None
    
    def train(self, X_control: np.ndarray, y_control: np.ndarray,
              X_treatment: np.ndarray, y_treatment: np.ndarray):
        """
        Train uplift model on control and treatment data.
        
        Args:
            X_control: Features for control group (not shown recommendation)
            y_control: Outcomes for control group (0/1 bought consequent item)
            X_treatment: Features for treatment group (shown recommendation)
            y_treatment: Outcomes for treatment group (0/1 bought consequent item)
        """
        if self.method == "two_model":
            # Train separate models for control and treatment
            self.control_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.treatment_model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            self.control_model.fit(X_control, y_control)
            self.treatment_model.fit(X_treatment, y_treatment)
        
        # TODO: Implement uplift_tree and uplift_rf methods
    
    def predict_uplift(self, X: np.ndarray) -> np.ndarray:
        """
        Predict uplift (incremental effect) for given features.
        
        Returns:
            Array of uplift values: P(Y=1|treatment) - P(Y=1|control)
        """
        if self.method == "two_model":
            # Predict probability in each group
            p_treatment = self.treatment_model.predict_proba(X)[:, 1]
            p_control = self.control_model.predict_proba(X)[:, 1]
            
            # Uplift = difference
            uplift = p_treatment - p_control
            
            return uplift
        
        return np.zeros(len(X))
```

### 6.2 Treatment Simulator

**backend/uplift/treatment_simulator.py**:

```python
class TreatmentSimulator:
    """Simulate control/treatment groups from historical data."""
    
    def simulate_experiment(self, transactions: pd.DataFrame, 
                          rule: ContextualRule,
                          treatment_fraction: float = 0.5) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Simulate A/B test for a rule.
        
        For transactions containing antecedent:
        - treatment group: shown the recommendation (assume some follow it)
        - control group: not shown the recommendation
        
        Returns:
            (control_df, treatment_df) with features and outcomes
        """
        # Find transactions with antecedent items
        antecedent_items = list(rule.antecedent)
        
        # Get all transactions
        trans_with_antecedent = self._find_transactions_with_items(
            transactions, antecedent_items
        )
        
        # Randomly assign to control/treatment
        n_treatment = int(len(trans_with_antecedent) * treatment_fraction)
        shuffled = trans_with_antecedent.sample(frac=1, random_state=42)
        
        treatment = shuffled.iloc[:n_treatment]
        control = shuffled.iloc[n_treatment:]
        
        # Create outcome: did they buy consequent item?
        consequent_items = list(rule.consequent)
        
        control['outcome'] = control.apply(
            lambda row: self._has_items(row, consequent_items), axis=1
        )
        treatment['outcome'] = treatment.apply(
            lambda row: self._has_items(row, consequent_items), axis=1
        )
        
        # Extract features
        control_features = self._extract_features(control)
        treatment_features = self._extract_features(treatment)
        
        return control_features, treatment_features
    
    def _find_transactions_with_items(self, transactions: pd.DataFrame, 
                                     items: List[str]) -> pd.DataFrame:
        """Find all transactions containing all items in list."""
        # Group by transaction_id
        grouped = transactions.groupby('transaction_id')['item_id'].apply(set)
        
        # Filter where transaction contains all items
        mask = grouped.apply(lambda x: set(items).issubset(x))
        valid_trans_ids = mask[mask].index
        
        return transactions[transactions['transaction_id'].isin(valid_trans_ids)]
    
    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features for uplift model."""
        # Features: time of day, day of week, store, basket size, etc.
        features = pd.DataFrame({
            'hour': df['timestamp'].dt.hour,
            'day_of_week': df['timestamp'].dt.dayofweek,
            'is_weekend': (df['timestamp'].dt.dayofweek >= 5).astype(int),
            'store_id_encoded': pd.Categorical(df['store_id']).codes,
            'basket_size': df.groupby('transaction_id')['item_id'].transform('count'),
        })
        features['outcome'] = df['outcome']
        
        return features
```

### 6.3 Causal Estimator

**backend/uplift/causal_estimator.py**:

```python
class CausalEstimator:
    """Estimate incremental effects for rules."""
    
    def __init__(self, uplift_model: UpliftModel, simulator: TreatmentSimulator):
        self.uplift_model = uplift_model
        self.simulator = simulator
    
    def estimate_incremental_effect(self, rule: ContextualRule, 
                                    transactions: pd.DataFrame) -> Dict[str, float]:
        """
        Estimate true causal effect of recommending this rule.
        
        Returns:
            {
                'incremental_attach_rate': uplift in probability,
                'incremental_revenue': expected revenue increase,
                'incremental_margin': expected profit increase,
                'control_rate': baseline purchase rate,
                'treatment_rate': purchase rate when recommended
            }
        """
        # Simulate experiment
        control_df, treatment_df = self.simulator.simulate_experiment(transactions, rule)
        
        # Train uplift model
        X_control = control_df.drop('outcome', axis=1).values
        y_control = control_df['outcome'].values
        X_treatment = treatment_df.drop('outcome', axis=1).values
        y_treatment = treatment_df['outcome'].values
        
        self.uplift_model.train(X_control, y_control, X_treatment, y_treatment)
        
        # Calculate metrics
        control_rate = y_control.mean()
        treatment_rate = y_treatment.mean()
        incremental_attach_rate = treatment_rate - control_rate
        
        # Estimate revenue/margin impact
        consequent_items = list(rule.consequent)
        avg_price = transactions[transactions['item_id'].isin(consequent_items)]['price'].mean()
        avg_margin_pct = transactions[transactions['item_id'].isin(consequent_items)].get('margin_pct', pd.Series([0.25])).mean()
        
        incremental_revenue = incremental_attach_rate * avg_price
        incremental_margin = incremental_revenue * avg_margin_pct
        
        return {
            'incremental_attach_rate': incremental_attach_rate,
            'incremental_revenue': incremental_revenue,
            'incremental_margin': incremental_margin,
            'control_rate': control_rate,
            'treatment_rate': treatment_rate
        }
```

**Acceptance Criteria for Phase 6**:

- [ ] UpliftModel trains on simulated control/treatment data
- [ ] TreatmentSimulator creates realistic A/B test scenarios
- [ ] CausalEstimator produces incremental lift estimates
- [ ] Unit test: rule with high correlation but no causation shows low/zero uplift
- [ ] Integration test: end-to-end uplift calculation for sample rule

---

## Phase 7: Backend API

### 7.1 API Models

**backend/api/models.py**:

```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UploadCSVRequest(BaseModel):
    filepath: str

class UploadCSVResponse(BaseModel):
    success: bool
    rows_imported: int
    rows_rejected: int
    errors: List[str]

class RuleFilter(BaseModel):
    store_id: Optional[str] = None
    category: Optional[str] = None
    min_score: float = 0.0
    context_time_bin: Optional[str] = None
    context_weekday_weekend: Optional[str] = None
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
    explanation: str  # Plain English explanation

class BundleRecommendation(BaseModel):
    items: List[str]
    explanation: str
    priority: str  # "High", "Medium", "Low"
    expected_margin: float
    lift: float

class WhatIfRequest(BaseModel):
    promoted_items: List[str]
    discount_pct: float
    time_window: str  # e.g., "2024-Q1", "weekend-morning"
    
class WhatIfResponse(BaseModel):
    estimated_attach_rate_change: float
    estimated_basket_size_change: float
    estimated_margin_impact: float
    affected_rules: List[RuleResponse]
```

### 7.2 API Routes

**backend/api/routes.py**:

```python
from fastapi import APIRouter, HTTPException
from .models import *
from backend.pipeline.csv_importer import CSVImporter
from backend.storage.database import DatabaseManager

router = APIRouter()

@router.post("/api/upload", response_model=UploadCSVResponse)
async def upload_csv(request: UploadCSVRequest):
    """Upload and process a new CSV file."""
    try:
        importer = CSVImporter(db_path="profitlift.db", validator=DataValidator())
        result = importer.import_csv(request.filepath)
        
        return UploadCSVResponse(
            success=True,
            rows_imported=result.rows_imported,
            rows_rejected=result.rows_rejected,
            errors=result.errors
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/rules", response_model=List[RuleResponse])
async def get_rules(filter: RuleFilter):
    """Retrieve association rules with filters."""
    db = DatabaseManager("profitlift.db")
    
    # Build SQL query based on filters
    query = "SELECT * FROM association_rules WHERE overall_score >= ?"
    params = [filter.min_score]
    
    if filter.store_id:
        query += " AND context_store_id = ?"
        params.append(filter.store_id)
    
    if filter.context_time_bin:
        query += " AND context_time_bin = ?"
        params.append(filter.context_time_bin)
    
    query += f" ORDER BY overall_score DESC LIMIT {filter.limit}"
    
    rules = db.execute(query, params)
    
    # Convert to response format
    response = []
    for rule in rules:
        response.append(RuleResponse(
            antecedent=json.loads(rule['antecedent']),
            consequent=json.loads(rule['consequent']),
            support=rule['support'],
            confidence=rule['confidence'],
            lift=rule['lift'],
            profit_score=rule['profit_score'],
            overall_score=rule['overall_score'],
            context={
                'store_id': rule['context_store_id'],
                'time_bin': rule['context_time_bin'],
                'weekday_weekend': rule['context_weekday_weekend']
            },
            explanation=generate_explanation(rule)
        ))
    
    return response

@router.get("/api/bundles", response_model=List[BundleRecommendation])
async def get_bundles(store_id: Optional[str] = None, limit: int = 10):
    """Get top bundle recommendations."""
    # Similar to get_rules but formatted as actionable bundles
    pass

@router.post("/api/whatif", response_model=WhatIfResponse)
async def whatif_simulation(request: WhatIfRequest):
    """Run what-if scenario simulation."""
    # 1. Find rules involving promoted items
    # 2. Adjust confidence/lift based on discount
    # 3. Project impact on basket size and margin
    # 4. Return estimates
    pass

@router.get("/api/metrics")
async def get_metrics():
    """Get system metrics and data freshness."""
    db = DatabaseManager("profitlift.db")
    
    return {
        'total_transactions': db.execute("SELECT COUNT(*) FROM transactions")[0][0],
        'total_rules': db.execute("SELECT COUNT(*) FROM association_rules")[0][0],
        'last_update': db.execute("SELECT MAX(created_at) FROM association_rules")[0][0],
        'data_freshness': 'current'  # TODO: calculate age
    }

def generate_explanation(rule: Dict) -> str:
    """Generate plain English explanation for a rule."""
    antecedent_str = ', '.join(json.loads(rule['antecedent']))
    consequent_str = ', '.join(json.loads(rule['consequent']))
    
    context_parts = []
    if rule['context_time_bin']:
        context_parts.append(f"during {rule['context_time_bin']}")
    if rule['context_weekday_weekend']:
        context_parts.append(f"on {rule['context_weekday_weekend']}s")
    
    context_str = ' '.join(context_parts) if context_parts else "overall"
    
    explanation = (
        f"Customers buying {antecedent_str} {context_str} "
        f"often add {consequent_str} "
        f"({rule['lift']:.1f}x lift, ${rule['profit_score']:.2f} avg margin)"
    )
    
    return explanation
```

**backend/api/main.py**:

```python
from fastapi import FastAPI
from .routes import router
import uvicorn

app = FastAPI(title="ProfitLift API", version="1.0.0")
app.include_router(router)

def run():
    """Run the API server."""
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run()
```

**Acceptance Criteria for Phase 7**:

- [ ] API starts without errors: `python -m backend.api.main`
- [ ] `/api/upload` accepts CSV and imports data
- [ ] `/api/rules` returns filtered rules with explanations
- [ ] `/api/bundles` returns top recommendations
- [ ] `/api/whatif` runs scenario simulation
- [ ] `/api/metrics` returns system stats
- [ ] API documentation accessible at http://127.0.0.1:8000/docs

---

## Phase 8: Desktop Application

### 8.1 Main Window

**desktop/main_window.py**:

```python
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt
from .views.rules_view import RulesView
from .views.bundles_view import BundlesView
from .views.whatif_view import WhatIfView
from .views.explanations_view import ExplanationsView

class MainWindow(QMainWindow):
    """Main application window with navigation."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ProfitLift - Context-Aware Market Basket Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout: sidebar + content
        main_layout = QHBoxLayout(central)
        
        # Sidebar with navigation buttons
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Stacked widget for different views
        self.stack = QStackedWidget()
        self.stack.addWidget(RulesView())      # Index 0
        self.stack.addWidget(BundlesView())    # Index 1
        self.stack.addWidget(WhatIfView())     # Index 2
        self.stack.addWidget(ExplanationsView())  # Index 3
        
        main_layout.addWidget(self.stack, stretch=1)
    
    def create_sidebar(self) -> QWidget:
        """Create navigation sidebar."""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        
        layout = QVBoxLayout(sidebar)
        
        # Logo/Title
        title = QLabel("ProfitLift")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Navigation buttons
        btn_rules = QPushButton("📊 Rules Dashboard")
        btn_rules.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        
        btn_bundles = QPushButton("🎁 Recommended Bundles")
        btn_bundles.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        btn_whatif = QPushButton("🔮 What-If Simulator")
        btn_whatif.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        btn_help = QPushButton("❓ Explanations")
        btn_help.clicked.connect(lambda: self.stack.setCurrentIndex(3))
        
        for btn in [btn_rules, btn_bundles, btn_whatif, btn_help]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    text-align: left;
                    padding: 15px;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return sidebar
```

### 8.2 Rules View

**desktop/views/rules_view.py**:

```python
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QComboBox, QLabel,
                             QLineEdit, QHeaderView)
from desktop.utils.api_client import APIClient

class RulesView(QWidget):
    """Rules Dashboard view."""
    
    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.init_ui()
        self.load_rules()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Association Rules Dashboard")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Filters panel
        filter_panel = self.create_filter_panel()
        layout.addWidget(filter_panel)
        
        # Rules table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Antecedent", "Consequent", "Lift", "Confidence", 
            "Support", "Profit Score", "Overall Score", "Context", "Explanation"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Export buttons
        export_panel = self.create_export_panel()
        layout.addWidget(export_panel)
    
    def create_filter_panel(self) -> QWidget:
        """Create filter controls."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Store filter
        layout.addWidget(QLabel("Store:"))
        self.store_combo = QComboBox()
        self.store_combo.addItems(["All", "STORE_A", "STORE_B", "STORE_C"])
        layout.addWidget(self.store_combo)
        
        # Time filter
        layout.addWidget(QLabel("Time:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems(["All", "morning", "midday", "afternoon", "evening"])
        layout.addWidget(self.time_combo)
        
        # Min score
        layout.addWidget(QLabel("Min Score:"))
        self.min_score_input = QLineEdit("0.0")
        self.min_score_input.setFixedWidth(80)
        layout.addWidget(self.min_score_input)
        
        # Apply button
        apply_btn = QPushButton("Apply Filters")
        apply_btn.clicked.connect(self.load_rules)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
        return panel
    
    def create_export_panel(self) -> QWidget:
        """Create export buttons."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        layout.addStretch()
        
        csv_btn = QPushButton("Export to CSV")
        csv_btn.clicked.connect(self.export_csv)
        layout.addWidget(csv_btn)
        
        pdf_btn = QPushButton("Export to PDF")
        pdf_btn.clicked.connect(self.export_pdf)
        layout.addWidget(pdf_btn)
        
        return panel
    
    def load_rules(self):
        """Load rules from API and populate table."""
        # Get filter values
        store = None if self.store_combo.currentText() == "All" else self.store_combo.currentText()
        time_bin = None if self.time_combo.currentText() == "All" else self.time_combo.currentText()
        min_score = float(self.min_score_input.text())
        
        # Fetch from API
        rules = self.api.get_rules(
            store_id=store,
            context_time_bin=time_bin,
            min_score=min_score
        )
        
        # Populate table
        self.table.setRowCount(len(rules))
        for i, rule in enumerate(rules):
            self.table.setItem(i, 0, QTableWidgetItem(", ".join(rule['antecedent'])))
            self.table.setItem(i, 1, QTableWidgetItem(", ".join(rule['consequent'])))
            self.table.setItem(i, 2, QTableWidgetItem(f"{rule['lift']:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{rule['confidence']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{rule['support']:.3f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"${rule['profit_score']:.2f}"))
            self.table.setItem(i, 6, QTableWidgetItem(f"{rule['overall_score']:.2f}"))
            self.table.setItem(i, 7, QTableWidgetItem(self.format_context(rule['context'])))
            self.table.setItem(i, 8, QTableWidgetItem(rule['explanation']))
    
    def format_context(self, context: dict) -> str:
        """Format context dict to readable string."""
        parts = []
        if context.get('store_id'):
            parts.append(context['store_id'])
        if context.get('time_bin'):
            parts.append(context['time_bin'])
        if context.get('weekday_weekend'):
            parts.append(context['weekday_weekend'])
        return " | ".join(parts) if parts else "Overall"
    
    def export_csv(self):
        """Export table to CSV."""
        # TODO: Implement CSV export
        pass
    
    def export_pdf(self):
        """Export table to PDF."""
        # TODO: Implement PDF export
        pass
```

### 8.3 Bundles View

**desktop/views/bundles_view.py**:

```python
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QScrollArea, QPushButton, QFrame)
from PyQt6.QtCore import Qt

class BundlesView(QWidget):
    """Recommended Bundles view with card layout."""
    
    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.init_ui()
        self.load_bundles()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Recommended Bundles")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Scroll area for bundle cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.cards_layout = QVBoxLayout(scroll_content)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Download button
        download_btn = QPushButton("Download Weekly Opportunity List")
        download_btn.clicked.connect(self.download_list)
        layout.addWidget(download_btn)
    
    def load_bundles(self):
        """Load bundles from API and create cards."""
        bundles = self.api.get_bundles(limit=20)
        
        for bundle in bundles:
            card = self.create_bundle_card(bundle)
            self.cards_layout.addWidget(card)
    
    def create_bundle_card(self, bundle: dict) -> QWidget:
        """Create a card widget for a bundle."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setLineWidth(2)
        
        # Color based on priority
        priority_colors = {
            'High': '#e74c3c',
            'Medium': '#f39c12',
            'Low': '#3498db'
        }
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 5px solid {priority_colors.get(bundle['priority'], '#95a5a6')};
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Priority badge
        priority = QLabel(f"🔥 {bundle['priority']} Priority")
        priority.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(priority)
        
        # Items
        items = QLabel(f"Bundle: {', '.join(bundle['items'])}")
        items.setStyleSheet("font-size: 16px; padding: 5px 0;")
        layout.addWidget(items)
        
        # Explanation
        explanation = QLabel(bundle['explanation'])
        explanation.setWordWrap(True)
        explanation.setStyleSheet("color: #555; font-size: 13px; padding: 5px 0;")
        layout.addWidget(explanation)
        
        # Metrics
        metrics = QLabel(
            f"Expected Margin: ${bundle['expected_margin']:.2f} | "
            f"Lift: {bundle['lift']:.1f}x"
        )
        metrics.setStyleSheet("font-size: 12px; color: #777;")
        layout.addWidget(metrics)
        
        return card
    
    def download_list(self):
        """Download opportunity list as CSV."""
        # TODO: Implement download
        pass
```

### 8.4 What-If Simulator

**desktop/views/whatif_view.py**:

```python
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QSlider, QPushButton, QTableWidget,
                             QTableWidgetItem)
from PyQt6.QtCore import Qt

class WhatIfView(QWidget):
    """What-If Simulator for promotion planning."""
    
    def __init__(self):
        super().__init__()
        self.api = APIClient()
        self.scenarios = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("What-If Simulator")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Scenario configuration panel
        config_panel = self.create_config_panel()
        layout.addWidget(config_panel)
        
        # Run simulation button
        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self.run_simulation)
        run_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-size: 14px;")
        layout.addWidget(run_btn)
        
        # Results table
        results_label = QLabel("Projected Outcomes:")
        results_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(results_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Metric", "Current", "Projected", "Change"
        ])
        layout.addWidget(self.results_table)
    
    def create_config_panel(self) -> QWidget:
        """Create scenario configuration panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Item selection
        item_row = QHBoxLayout()
        item_row.addWidget(QLabel("Promoted Item:"))
        self.item_combo = QComboBox()
        self.item_combo.addItems(["Milk", "Bread", "Cereal", "Butter"])  # TODO: Load from data
        item_row.addWidget(self.item_combo)
        layout.addLayout(item_row)
        
        # Discount slider
        discount_row = QHBoxLayout()
        discount_row.addWidget(QLabel("Discount %:"))
        self.discount_slider = QSlider(Qt.Orientation.Horizontal)
        self.discount_slider.setRange(0, 50)
        self.discount_slider.setValue(10)
        self.discount_slider.setTickInterval(5)
        self.discount_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        discount_row.addWidget(self.discount_slider)
        self.discount_label = QLabel("10%")
        self.discount_slider.valueChanged.connect(
            lambda v: self.discount_label.setText(f"{v}%")
        )
        discount_row.addWidget(self.discount_label)
        layout.addLayout(discount_row)
        
        # Time window
        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("Time Window:"))
        self.time_combo = QComboBox()
        self.time_combo.addItems([
            "Overall",
            "Weekend Morning",
            "Weekday Evening",
            "Q1 (Jan-Mar)",
            "Q4 (Oct-Dec)"
        ])
        time_row.addWidget(self.time_combo)
        layout.addLayout(time_row)
        
        return panel
    
    def run_simulation(self):
        """Run what-if simulation and display results."""
        # Get configuration
        item = self.item_combo.currentText()
        discount = self.discount_slider.value()
        time_window = self.time_combo.currentText()
        
        # Call API
        result = self.api.whatif_simulation(
            promoted_items=[item],
            discount_pct=discount / 100.0,
            time_window=time_window
        )
        
        # Display results
        self.results_table.setRowCount(3)
        
        metrics = [
            ("Attach Rate", "baseline", result['estimated_attach_rate_change']),
            ("Basket Size", "baseline", result['estimated_basket_size_change']),
            ("Margin Impact", "$baseline", result['estimated_margin_impact'])
        ]
        
        for i, (metric, current, change) in enumerate(metrics):
            self.results_table.setItem(i, 0, QTableWidgetItem(metric))
            self.results_table.setItem(i, 1, QTableWidgetItem(current))
            projected = f"+{change:.2%}" if isinstance(change, float) else str(change)
            self.results_table.setItem(i, 2, QTableWidgetItem(projected))
            
            # Change indicator
            indicator = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            self.results_table.setItem(i, 3, QTableWidgetItem(indicator))
```

### 8.5 API Client

**desktop/utils/api_client.py**:

```python
import requests
from typing import List, Dict, Optional

class APIClient:
    """Client for backend API communication."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
    
    def get_rules(self, store_id: Optional[str] = None,
                  context_time_bin: Optional[str] = None,
                  min_score: float = 0.0,
                  limit: int = 100) -> List[Dict]:
        """Fetch association rules."""
        params = {
            'store_id': store_id,
            'context_time_bin': context_time_bin,
            'min_score': min_score,
            'limit': limit
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(f"{self.base_url}/api/rules", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_bundles(self, store_id: Optional[str] = None, 
                    limit: int = 10) -> List[Dict]:
        """Fetch bundle recommendations."""
        params = {'limit': limit}
        if store_id:
            params['store_id'] = store_id
        
        response = requests.get(f"{self.base_url}/api/bundles", params=params)
        response.raise_for_status()
        return response.json()
    
    def whatif_simulation(self, promoted_items: List[str],
                         discount_pct: float,
                         time_window: str) -> Dict:
        """Run what-if simulation."""
        payload = {
            'promoted_items': promoted_items,
            'discount_pct': discount_pct,
            'time_window': time_window
        }
        
        response = requests.post(f"{self.base_url}/api/whatif", json=payload)
        response.raise_for_status()
        return response.json()
    
    def upload_csv(self, filepath: str) -> Dict:
        """Upload CSV file."""
        payload = {'filepath': filepath}
        response = requests.post(f"{self.base_url}/api/upload", json=payload)
        response.raise_for_status()
        return response.json()
```

**Acceptance Criteria for Phase 8**:

- [ ] Desktop app launches without errors: `python -m desktop.main`
- [ ] Navigation between views works
- [ ] Rules view displays data from API
- [ ] Filters in Rules view work correctly
- [ ] Bundles view shows card layout with explanations
- [ ] What-If simulator projects outcomes
- [ ] All views handle API errors gracefully
- [ ] UI is responsive and professional-looking

### To-dos

- [ ] Create modular project structure with backend/, desktop/, data/, evaluation/, docs/, tests/ directories and initial Python package setup
- [ ] Configure development environment: Python 3.10+, virtual env, requirements.txt with core dependencies (pandas, numpy, mlxtend, scikit-learn, PyQt6, FastAPI)
- [ ] Build CSV import with validation for transaction data (ID, datetime, store, items, prices, discounts, optional margin)
- [ ] Download and prepare Instacart and Dunnhumby benchmark datasets with unified format loaders
- [ ] Implement baseline MBA algorithms: Apriori, FP-Growth, Eclat with standard metrics (support, confidence, lift)
- [ ] Build context-aware rule mining: segment by time/store/season/promotion, mine rules per context, tag rules with applicable contexts
- [ ] Implement scoring function combining lift, profit margin, diversity, and confidence with configurable weights
- [ ] Implement causal uplift modeling (two-model approach or uplift trees) to estimate incremental effect of recommendations
- [ ] Create near real-time update system: file watching, incremental FP-Growth updates, context-specific rule refresh
- [ ] Build FastAPI endpoints: upload CSV, retrieve rules, get bundles, run what-if, get metrics
- [ ] Create PyQt6 desktop app shell with main window, navigation, and four view placeholders (Rules, Bundles, What-If, Explanations)
- [ ] Build Rules Dashboard view: table with filters (store, date, category), sorting, context tags display
- [ ] Build Recommended Bundles view: card layout, plain-English explanations, priority ranking, weekly list download
- [ ] Build What-If Simulator: item/discount/window selection, projection calculations, scenario comparison (up to 3)
- [ ] Build Explanations view: methodology overview, glossary, how-it-works section for non-technical users
- [ ] Implement CSV and PDF export for rules, bundles, and what-if results using ReportLab
- [ ] Implement evaluation framework: profit contribution, CTR, basket size, incremental revenue metrics on benchmark datasets
- [ ] Create simulated promotion scenarios for causal validation: control/treatment groups, outcome generation
- [ ] Write unit tests for algorithms, context engine, scoring, uplift model (>80% coverage)
- [ ] Write integration tests for pipeline, API endpoints, CSV import/export
- [ ] Create Windows .exe using PyInstaller with proper bundling, icon, installer, sample data package
- [ ] Write academic documentation: technical report, methodology, literature review, reproducibility guide
- [ ] Write user documentation: user manual, quick start guide, troubleshooting, glossary
- [ ] Create presentation deck, demo script, optional demo video for professor presentation
- [ ] UI/UX refinement, performance optimization, code quality review, final testing before submission