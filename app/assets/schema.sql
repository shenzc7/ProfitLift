-- Items table (NEW: avoid parsing JSON everywhere)
CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    item_name TEXT,
    category TEXT,
    avg_price REAL,
    margin_pct REAL
);

-- Transactions
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

-- Transaction items
CREATE TABLE IF NOT EXISTS transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    price REAL NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
);

-- Association rules (context-specific)
CREATE TABLE IF NOT EXISTS association_rules (
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
CREATE TABLE IF NOT EXISTS uplift_results (
    rule_id INTEGER PRIMARY KEY,
    incremental_attach_rate REAL,
    incremental_revenue REAL,
    incremental_margin REAL,
    control_rate REAL,
    treatment_rate REAL,
    FOREIGN KEY (rule_id) REFERENCES association_rules(id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_store ON transactions(store_id);
CREATE INDEX IF NOT EXISTS idx_items_transaction ON transaction_items(transaction_id);
CREATE INDEX IF NOT EXISTS idx_items_item ON transaction_items(item_id);
CREATE INDEX IF NOT EXISTS idx_rules_score ON association_rules(overall_score DESC);
CREATE INDEX IF NOT EXISTS idx_rules_context ON association_rules(context_store_id, context_time_bin);