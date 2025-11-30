import sqlite3
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


class DatabaseManager:
    """SQLite database manager for ProfitLift."""

    def __init__(self, db_path: str = "profitlift.db"):
        self.db_path = str(db_path)
        self._conn: Optional[sqlite3.Connection] = None
        self._initialized = False

    @property
    def conn(self) -> sqlite3.Connection:
        """Return a shared SQLite connection (lazy-initialized)."""
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _schema_path(self) -> Path:
        """Locate schema file, supporting frozen (PyInstaller) builds."""
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
        candidate = base / "schema.sql"
        return candidate if candidate.exists() else Path(__file__).parent / "schema.sql"

    def _ensure_database(self):
        """Create database and tables if they don't exist."""
        if self._initialized:
            return
        
        schema_path = self._schema_path()
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding="utf-8") as f:
            schema = f.read()

        # Use IF NOT EXISTS for tables to avoid errors
        self.conn.executescript(schema)
        self.conn.commit()
        self._initialized = True

    def execute_script(self, script: str):
        """Execute a raw SQL script (used by tests/maintenance)."""
        self._ensure_database()
        self.conn.executescript(script)
        self.conn.commit()

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        self._ensure_database()
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def execute_insert(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT query and return the last row ID."""
        self._ensure_database()
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        self.conn.commit()
        return cursor.lastrowid

    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute multiple INSERT/UPDATE queries."""
        self._ensure_database()
        cursor = self.conn.cursor()
        cursor.executemany(query, params_list)
        self.conn.commit()

    def clear_tables(self, tables: Optional[List[str]] = None):
        """Clear data from specified tables (or all known tables by default)."""
        self._ensure_database()
        targets = tables or ["uplift_results", "association_rules", "transaction_items", "transactions", "items"]
        cursor = self.conn.cursor()
        for table in targets:
            cursor.execute(f"DELETE FROM {table}")
        self.conn.commit()

    def get_table_count(self, table: str) -> int:
        """Get row count for a table."""
        result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
        return result[0]['count'] if result else 0

    def get_last_transaction_timestamp(self) -> Optional[str]:
        """Get the most recent transaction timestamp, if available."""
        result = self.execute_query("SELECT MAX(timestamp) as latest FROM transactions")
        if result and result[0].get("latest"):
            return str(result[0]["latest"])
        return None

    def close(self):
        """Close the shared connection (primarily for tests)."""
        if self._conn:
            self._conn.close()
            self._conn = None
        self._initialized = False
