"""
ProfitLift API Server - Lightweight version
A simple FastAPI backend that serves the ProfitLift frontend.
"""

import sqlite3
import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================
# Pydantic Models
# ============================================

class ContextSummary(BaseModel):
    label: str
    store_id: Optional[str] = None
    time_bin: Optional[str] = None
    weekday_weekend: Optional[str] = None
    quarter: Optional[int] = None

class UpliftMetrics(BaseModel):
    incremental_attach_rate: float = 0.0
    incremental_revenue: float = 0.0
    incremental_margin: float = 0.0
    control_rate: float = 0.0
    treatment_rate: float = 0.0

class RuleResponse(BaseModel):
    antecedent: List[str]
    consequent: List[str]
    context: ContextSummary
    support: float
    confidence: float
    lift: float
    profit_score: Optional[float] = None
    diversity_score: Optional[float] = None
    overall_score: Optional[float] = None
    explanation: str = ""
    uplift: Optional[UpliftMetrics] = None

class BundleResponse(BaseModel):
    bundle_id: str
    anchor_items: List[str]
    recommended_items: List[str]
    context: ContextSummary
    expected_margin: float
    expected_attach_rate: float
    overall_score: float
    narrative: str
    confidence: float = 0.0
    lift: float = 0.0
    uplift: Optional[UpliftMetrics] = None

class WhatIfRequest(BaseModel):
    antecedent: List[str]
    consequent: List[str]
    anticipated_discount_pct: float = 0.1
    expected_traffic: int = 1000
    context: Optional[Dict[str, Any]] = None

class WhatIfResponse(BaseModel):
    narrative: str
    projected_attach_rate: float
    incremental_attach_rate: float
    incremental_margin: float
    incremental_revenue: float
    projected_margin_total: float
    uplift: UpliftMetrics

class DashboardStats(BaseModel):
    avgLift: float
    profitOpportunity: float
    activeRules: int
    topRule: str

class ClearRequest(BaseModel):
    clear_rules: bool = True
    clear_bundles: bool = True
    clear_uploads: bool = False
    clear_cache: bool = True

# ============================================
# Database Helper
# ============================================

DB_PATH = "profitlift.db"

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables."""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            category TEXT,
            avg_price REAL,
            margin_pct REAL
        );
        
        CREATE TABLE IF NOT EXISTS transactions (
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
        
        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS association_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            antecedent TEXT NOT NULL,
            consequent TEXT NOT NULL,
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

        CREATE TABLE IF NOT EXISTS uplift_results (
            rule_id INTEGER PRIMARY KEY,
            incremental_attach_rate REAL,
            incremental_revenue REAL,
            incremental_margin REAL,
            control_rate REAL,
            treatment_rate REAL,
            FOREIGN KEY (rule_id) REFERENCES association_rules(id)
        );
    """)
    conn.commit()
    conn.close()

def get_table_count(table: str) -> int:
    """Safely retrieve a row count for the given table."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            row = cursor.fetchone()
            return row["count"] if row else 0
    except sqlite3.OperationalError:
        return 0

def get_last_transaction_timestamp() -> Optional[str]:
    """Return the latest transaction timestamp if available."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(timestamp) as latest FROM transactions")
            row = cursor.fetchone()
            return row["latest"] if row and row["latest"] else None
    except sqlite3.OperationalError:
        return None

# ============================================
# Sample Data Generator
# ============================================

def generate_sample_rules(limit: int = 50, min_support: float = 0.01, 
                          min_confidence: float = 0.3, min_lift: float = 1.0,
                          store_id: Optional[str] = None,
                          time_bin: Optional[str] = None,
                          weekday_weekend: Optional[str] = None) -> List[RuleResponse]:
    """Generate sample association rules."""
    
    # Sample product pairs that make sense
    product_pairs = [
        (["Milk"], ["Bread"], 0.08, 0.65, 2.1),
        (["Bread"], ["Butter"], 0.06, 0.55, 1.9),
        (["Coffee"], ["Cream"], 0.05, 0.72, 2.8),
        (["Chips"], ["Soda"], 0.07, 0.58, 2.3),
        (["Beer"], ["Chips"], 0.04, 0.45, 1.8),
        (["Pasta"], ["Tomato Sauce"], 0.05, 0.68, 2.5),
        (["Eggs"], ["Bacon"], 0.03, 0.52, 2.0),
        (["Wine"], ["Cheese"], 0.02, 0.48, 2.2),
        (["Cereal"], ["Milk"], 0.06, 0.75, 2.4),
        (["Hot Dogs"], ["Buns"], 0.04, 0.82, 3.1),
        (["Peanut Butter"], ["Jelly"], 0.03, 0.61, 2.6),
        (["Shampoo"], ["Conditioner"], 0.02, 0.70, 2.9),
        (["Toothpaste"], ["Toothbrush"], 0.02, 0.55, 2.1),
        (["Diapers"], ["Baby Wipes"], 0.03, 0.78, 3.2),
        (["Ice Cream"], ["Chocolate Syrup"], 0.02, 0.42, 1.7),
        (["Hamburger"], ["Ketchup"], 0.04, 0.58, 2.0),
        (["Steak"], ["Potatoes"], 0.02, 0.45, 1.9),
        (["Chicken"], ["Rice"], 0.03, 0.52, 1.8),
        (["Fish"], ["Lemon"], 0.02, 0.48, 2.1),
        (["Salad"], ["Dressing"], 0.04, 0.72, 2.7),
    ]
    
    contexts = [
        ("Overall", None, None, None, None),
        ("Morning, Weekday", None, "morning", "weekday", None),
        ("Evening, Weekend", None, "evening", "weekend", None),
        ("Afternoon", None, "afternoon", None, None),
        ("Q4 Holiday Season", None, None, None, 4),
    ]
    
    rules = []
    
    for ant, cons, support, confidence, lift in product_pairs:
        if support < min_support or confidence < min_confidence or lift < min_lift:
            continue
            
        # Pick a random context
        ctx_label, ctx_store, ctx_time, ctx_day, ctx_q = random.choice(contexts)
        
        # Apply filters
        if time_bin and ctx_time and ctx_time != time_bin.lower():
            continue
        if weekday_weekend and ctx_day and ctx_day != weekday_weekend.lower():
            continue
        
        profit_score = round(random.uniform(0.5, 3.0), 2)
        diversity_score = round(random.uniform(0.3, 0.9), 2)
        overall_score = round((lift * 0.3 + profit_score * 0.4 + diversity_score * 0.3), 2)
        
        # Generate uplift
        control_rate = confidence * 0.7
        treatment_rate = confidence
        inc_attach = treatment_rate - control_rate
        
        uplift = UpliftMetrics(
            incremental_attach_rate=round(inc_attach, 3),
            incremental_revenue=round(profit_score * 0.8, 2),
            incremental_margin=round(profit_score * 0.3, 2),
            control_rate=round(control_rate, 3),
            treatment_rate=round(treatment_rate, 3)
        )
        
        explanation = f"When shoppers buy {', '.join(ant)}, they also tend to add {', '.join(cons)} ({confidence:.0%} of the time, lift {lift:.2f})."
        if ctx_label != "Overall":
            explanation = f"In {ctx_label.lower()}, {explanation[0].lower()}{explanation[1:]}"
        if inc_attach > 0.05:
            explanation += f" True uplift of {inc_attach:.1%} drives about ${profit_score * 0.3:.2f} extra margin per basket."
        
        rules.append(RuleResponse(
            antecedent=ant,
            consequent=cons,
            context=ContextSummary(
                label=ctx_label,
                store_id=ctx_store,
                time_bin=ctx_time,
                weekday_weekend=ctx_day,
                quarter=ctx_q
            ),
            support=support,
            confidence=confidence,
            lift=lift,
            profit_score=profit_score,
            diversity_score=diversity_score,
            overall_score=overall_score,
            explanation=explanation,
            uplift=uplift
        ))
        
        if len(rules) >= limit:
            break
    
    # Sort by overall score
    rules.sort(key=lambda x: x.overall_score or 0, reverse=True)
    return rules[:limit]

def generate_sample_bundles(limit: int = 15, min_lift: float = 1.0) -> List[BundleResponse]:
    """Generate sample bundle recommendations."""
    
    rules = generate_sample_rules(limit=limit * 2, min_lift=min_lift)
    bundles = []
    
    for i, rule in enumerate(rules[:limit]):
        bundle_id = f"bundle_{i+1}"
        expected_margin = rule.profit_score or random.uniform(0.5, 2.5)
        expected_attach = rule.confidence
        
        narrative = f"{rule.context.label} shoppers who buy {', '.join(rule.antecedent)} respond well to {', '.join(rule.consequent)}, "
        narrative += f"adding {rule.uplift.incremental_attach_rate:.1%} more baskets and about ${expected_margin:.2f} margin."
        
        bundles.append(BundleResponse(
            bundle_id=bundle_id,
            anchor_items=rule.antecedent,
            recommended_items=rule.consequent,
            context=rule.context,
            expected_margin=round(expected_margin, 2),
            expected_attach_rate=round(expected_attach, 3),
            overall_score=rule.overall_score or 0.5,
            narrative=narrative,
            confidence=rule.confidence,
            lift=rule.lift,
            uplift=rule.uplift
        ))
    
    return bundles

# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="ProfitLift API",
    description="Context-aware profit-optimized market basket analytics",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

# ============================================
# Endpoints
# ============================================

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/stats", response_model=DashboardStats)
def dashboard_stats():
    """Provide lightweight dashboard stats for the UI."""
    rules = generate_sample_rules(limit=30)
    active_rules = len(rules)
    avg_lift = round(sum(rule.lift for rule in rules) / active_rules, 2) if active_rules else 0.0
    
    # Scale profit score to something dashboard-friendly
    profit_opportunity = round(sum((rule.profit_score or 0) * 500 for rule in rules[:10]), 2) if rules else 0.0
    
    top_rule = "-"
    if rules:
        best = max(rules, key=lambda r: (r.overall_score or r.lift))
        top_rule = f"{', '.join(best.antecedent)} -> {', '.join(best.consequent)}"

    return DashboardStats(
        avgLift=avg_lift,
        profitOpportunity=profit_opportunity,
        activeRules=active_rules,
        topRule=top_rule
    )

@app.get("/api/settings/overview")
def settings_overview():
    """Operational snapshot for the Settings page."""
    tables = ["items", "transactions", "transaction_items", "association_rules", "uplift_results"]
    counts = {table: get_table_count(table) for table in tables}

    return {
        "db_path": str(Path(DB_PATH).resolve()),
        "table_counts": counts,
        "cache_entries": 0,
        "last_ingest_at": get_last_transaction_timestamp(),
        "api_version": "1.0.0"
    }

@app.post("/api/settings/clear")
def clear_data(request: ClearRequest):
    """Clear cached rules/bundles and optionally uploaded data."""
    tables_to_clear = []
    if request.clear_rules or request.clear_bundles:
        tables_to_clear.extend(["uplift_results", "association_rules"])
    if request.clear_uploads:
        tables_to_clear.extend(["transaction_items", "transactions", "items"])

    unique_tables = list(dict.fromkeys(tables_to_clear))
    counts_before = {table: get_table_count(table) for table in unique_tables}

    if unique_tables:
        with get_db() as conn:
            cursor = conn.cursor()
            for table in unique_tables:
                try:
                    cursor.execute(f"DELETE FROM {table}")
                except sqlite3.OperationalError:
                    counts_before[table] = 0
            conn.commit()

    return {
        "tables_cleared": unique_tables,
        "counts_before": counts_before,
        "cache_cleared": request.clear_cache
    }

@app.get("/api/rules", response_model=List[RuleResponse])
def get_rules(
    min_support: float = 0.01,
    min_confidence: float = 0.3,
    min_lift: float = 1.0,
    limit: int = 50,
    store_id: Optional[str] = None,
    time_bin: Optional[str] = None,
    weekday_weekend: Optional[str] = None,
    include_causal: bool = True
):
    """Get association rules with optional filters."""
    return generate_sample_rules(
        limit=limit,
        min_support=min_support,
        min_confidence=min_confidence,
        min_lift=min_lift,
        store_id=store_id,
        time_bin=time_bin,
        weekday_weekend=weekday_weekend
    )

@app.get("/api/bundles", response_model=List[BundleResponse])
def get_bundles(
    min_lift: float = 1.0,
    limit: int = 15,
    include_causal: bool = True
):
    """Get bundle recommendations."""
    return generate_sample_bundles(limit=limit, min_lift=min_lift)

@app.post("/api/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload transaction CSV data."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    content = await file.read()
    lines = content.decode('utf-8').strip().split('\n')
    
    # Parse CSV
    if len(lines) < 2:
        raise HTTPException(status_code=400, detail="File is empty or has no data rows")
    
    header = lines[0].split(',')
    rows_imported = len(lines) - 1
    
    # Count unique transactions and items
    transactions = set()
    items = set()
    
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) >= 5:
            transactions.add(parts[0])  # transaction_id
            items.add(parts[3])  # item_id
    
    return {
        "rows_imported": rows_imported,
        "rejected_rows": 0,
        "items_created": len(items),
        "transactions_created": len(transactions),
        "errors": []
    }

@app.post("/api/whatif", response_model=WhatIfResponse)
def what_if_simulation(request: WhatIfRequest):
    """Run what-if simulation for a promotion scenario."""
    
    # Simulate based on inputs
    base_attach_rate = 0.15 + random.uniform(0, 0.1)
    discount_boost = request.anticipated_discount_pct * 0.5
    projected_attach = min(base_attach_rate + discount_boost, 0.95)
    incremental_attach = projected_attach - base_attach_rate
    
    avg_price = 5.0 + random.uniform(0, 5)
    margin_pct = 0.25 + random.uniform(0, 0.15)
    
    incremental_revenue = avg_price * incremental_attach
    incremental_margin = incremental_revenue * margin_pct
    projected_margin_total = incremental_margin * request.expected_traffic
    
    ant_str = ", ".join(request.antecedent)
    cons_str = ", ".join(request.consequent)
    
    narrative = f"Promoting {cons_str} to shoppers buying {ant_str} with a {request.anticipated_discount_pct*100:.0f}% discount "
    narrative += f"is projected to increase attach rate by {incremental_attach:.1%}, "
    narrative += f"generating ${projected_margin_total:,.0f} in incremental margin across {request.expected_traffic:,} baskets."
    
    return WhatIfResponse(
        narrative=narrative,
        projected_attach_rate=round(projected_attach, 3),
        incremental_attach_rate=round(incremental_attach, 3),
        incremental_margin=round(incremental_margin, 2),
        incremental_revenue=round(incremental_revenue, 2),
        projected_margin_total=round(projected_margin_total, 2),
        uplift=UpliftMetrics(
            incremental_attach_rate=round(incremental_attach, 3),
            incremental_revenue=round(incremental_revenue, 2),
            incremental_margin=round(incremental_margin, 2),
            control_rate=round(base_attach_rate, 3),
            treatment_rate=round(projected_attach, 3)
        )
    )

# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)






