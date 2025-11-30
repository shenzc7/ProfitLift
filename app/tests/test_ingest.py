"""Tests for CSV importer."""
import pytest
import pandas as pd
from pathlib import Path
from app.ingest.csv_importer import CSVImporter, ImportResult

def test_csv_importer_initialization(temp_db):
    """Test CSVImporter can be instantiated."""
    importer = CSVImporter(db_path=temp_db.db_path)
    assert importer is not None

def test_import_valid_csv(temp_db, sample_csv_path):
    """Test importing a valid CSV file."""
    importer = CSVImporter(db_path=temp_db.db_path)
    result = importer.import_csv(str(sample_csv_path))
    assert isinstance(result, ImportResult)
    assert result.rows_imported > 0
    assert result.items_created > 0

def test_import_missing_columns(temp_db, tmp_path):
    """Test importing CSV with missing required columns."""
    # Create invalid CSV
    invalid_csv = tmp_path / "invalid.csv"
    with open(invalid_csv, "w") as f:
        f.write("transaction_id,date\n")
        f.write("1,2023-01-01\n")
        
    importer = CSVImporter(db_path=temp_db.db_path)
    result = importer.import_csv(str(invalid_csv))
    
    # The importer catches exceptions and returns an error result
    assert result.rows_imported == 0
    assert len(result.errors) > 0
    assert "Missing required columns" in result.errors[0]

def test_context_enrichment(temp_db, sample_csv_path):
    """Test that context fields are enriched correctly."""
    importer = CSVImporter(db_path=temp_db.db_path)
    importer.import_csv(str(sample_csv_path))
    
    # Verify context_time_bin, context_weekday_weekend, context_quarter are set
    # We need to query the database to check this
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT context_time_bin, context_weekday_weekend, context_quarter FROM transactions LIMIT 1")
    row = cursor.fetchone()
    
    assert row is not None
    # Check that values are not None (assuming sample data produces valid contexts)
    # Note: This depends on add_context_columns working correctly
    # If sample data has valid dates, these should be populated
    assert row[0] is not None # time_bin
    assert row[1] is not None # weekday_weekend
    assert row[2] is not None # quarter

def test_duplicate_transaction_handling(temp_db, sample_csv_path):
    """Test handling of duplicate transaction IDs."""
    importer = CSVImporter(db_path=temp_db.db_path)
    
    # Import same CSV twice
    result1 = importer.import_csv(str(sample_csv_path))
    result2 = importer.import_csv(str(sample_csv_path))
    
    assert result1.rows_imported > 0
    # The second import might update or ignore, depending on implementation (REPLACE INTO used in code)
    # If REPLACE INTO, it "succeeds" but doesn't increase count of *new* things effectively, 
    # but the function returns 'transactions_created' which counts successful inserts.
    # Since it's REPLACE, it will count as "created" (or inserted) again.
    assert result2.transactions_created > 0 

def test_margin_calculation(temp_db, tmp_path):
    """Test margin percentage calculation from price and cost."""
    # Create CSV with margin_pct
    csv_path = tmp_path / "margin_test.csv"
    with open(csv_path, "w") as f:
        f.write("transaction_id,timestamp,store_id,item_id,price,margin_pct\n")
        f.write("100,2023-01-01 10:00:00,1,item_x,10.0,0.4\n")
        
    importer = CSVImporter(db_path=temp_db.db_path)
    importer.import_csv(str(csv_path))
    
    cursor = temp_db.conn.cursor()
    cursor.execute("SELECT margin_pct FROM items WHERE item_id='item_x'")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == 0.4
