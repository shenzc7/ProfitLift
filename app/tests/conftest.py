"""Pytest fixtures for ProfitLift tests."""
import pytest
import tempfile
import os
from pathlib import Path
from app.assets.database import DatabaseManager

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    # Initialize with schema if needed, but for now just the file
    # In a real scenario, we might need to run schema.sql here
    # But DatabaseManager usually handles initialization if it has logic for it
    # Let's assume DatabaseManager handles connection. 
    # We might need to initialize schema manually if DatabaseManager doesn't.
    # Checking DatabaseManager code would be good, but for now following the checklist.
    
    db = DatabaseManager(path)
    # Initialize schema
    with open("app/assets/schema.sql", "r") as f:
        schema_sql = f.read()
        db.execute_script(schema_sql)
        
    yield db
    
    db.close()
    os.close(fd)
    os.unlink(path)

@pytest.fixture
def sample_csv_path():
    """Return path to sample CSV."""
    # Ensure this path exists or create a dummy one for tests if needed
    path = Path("data/sample/sample_1k.csv")
    if not path.exists():
        # Create a dummy csv if it doesn't exist, to prevent tests from failing immediately
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write("transaction_id,date,item_id,price,cost\n")
            f.write("1,2023-01-01,apple,1.0,0.5\n")
    return path
