# ProfitLift - AI-Friendly Completion Checklist

**Purpose**: Comprehensive, actionable task list for AI agents to complete ProfitLift project.  
**Critical Principle**: Follow BRD (`idea.md`) and abstract (`soul.md`) exactly. No deviations.

---

## 📋 Project Context

**Project Root**: `/Users/shenzc/Desktop/projects/ProfitLift`  
**Python Version**: 3.10+  
**Key Files**:
- `idea.md` - Business Requirements Document (BRD)
- `soul.md` - Abstract/Technical Requirements
- `app/api/main.py` - FastAPI entry point
- `app/ui/main.py` - Streamlit entry point
- `config/default.yaml` - Main configuration
- `requirements.txt` - Dependencies

**UI Philosophy**: Premium, classy, easy-to-understand. NO gradients, NO SaaS-style elements.

---

## 🧪 SECTION 1: Testing Suite (CRITICAL)

### Task 1.1: Setup Test Infrastructure
**File**: `app/tests/__init__.py` (exists but empty)  
**Action**: Create pytest configuration

**Steps**:
1. Create `pytest.ini` in project root:
```ini
[pytest]
testpaths = app/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
```

2. Create `app/tests/conftest.py`:
```python
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
    db = DatabaseManager(path)
    yield db
    os.close(fd)
    os.unlink(path)

@pytest.fixture
def sample_csv_path():
    """Return path to sample CSV."""
    return Path("data/sample/sample_1k.csv")
```

**Acceptance**: Run `pytest --collect-only` and see test files listed.

---

### Task 1.2: Test CSV Importer
**File**: `app/tests/test_ingest.py` (CREATE NEW)  
**Target**: `app/ingest/csv_importer.py`

**Test Cases**:
```python
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

def test_import_missing_columns(temp_db):
    """Test importing CSV with missing required columns."""
    # Create invalid CSV
    # Test that appropriate error is raised

def test_context_enrichment(temp_db, sample_csv_path):
    """Test that context fields are enriched correctly."""
    importer = CSVImporter(db_path=temp_db.db_path)
    result = importer.import_csv(str(sample_csv_path))
    # Verify context_time_bin, context_weekday_weekend, context_quarter are set

def test_duplicate_transaction_handling(temp_db):
    """Test handling of duplicate transaction IDs."""
    # Import same CSV twice, verify behavior

def test_margin_calculation(temp_db):
    """Test margin percentage calculation from price and cost."""
    # Test margin_pct calculation logic
```

**Acceptance**: All tests pass, >90% coverage of `csv_importer.py`.

---

### Task 1.3: Test Context Segmenter
**File**: `app/tests/test_mining.py` (CREATE NEW)  
**Target**: `app/mining/context_segmenter.py`

**Test Cases**:
```python
"""Tests for context-aware mining."""
import pytest
import pandas as pd
from app.mining.context_segmenter import ContextSegmenter
from app.mining.context_types import Context

def test_time_bin_segmentation():
    """Test time bin segmentation (morning, midday, afternoon, evening)."""
    # Create transactions with different timestamps
    # Verify correct time_bin assignment

def test_weekday_weekend_segmentation():
    """Test weekday vs weekend segmentation."""
    # Create transactions on different days
    # Verify weekday_weekend assignment

def test_quarter_segmentation():
    """Test quarterly segmentation."""
    # Create transactions in different quarters
    # Verify quarter assignment

def test_context_backoff():
    """Test context backoff when min_rows_per_context not met."""
    # Create sparse context data
    # Verify backoff to broader context

def test_context_combinations():
    """Test all context combinations (store × time × weekday × quarter)."""
    # Verify all combinations are generated correctly
```

**Acceptance**: All tests pass, >85% coverage of context segmentation logic.

---

### Task 1.4: Test FP-Growth Miner
**File**: `app/tests/test_mining.py` (ADD TO EXISTING)  
**Target**: `app/mining/fpgrowth.py`

**Test Cases**:
```python
def test_fpgrowth_itemset_mining():
    """Test FP-Growth finds frequent itemsets."""
    from app.mining.fpgrowth import FPGrowthMiner
    # Create transaction dataset
    # Verify itemsets are found correctly

def test_fpgrowth_rule_generation():
    """Test FP-Growth generates association rules."""
    # Verify rules have support, confidence, lift

def test_fpgrowth_min_support_filtering():
    """Test min_support threshold filtering."""
    # Verify only itemsets above threshold are returned

def test_fpgrowth_empty_transactions():
    """Test handling of empty transaction list."""
    # Should return empty list, not crash
```

**Acceptance**: All tests pass, >80% coverage of `fpgrowth.py`.

---

### Task 1.5: Test Eclat Miner
**File**: `app/tests/test_mining.py` (ADD TO EXISTING)  
**Target**: `app/mining/eclat.py`

**Test Cases**:
```python
def test_eclat_vertical_format():
    """Test Eclat uses vertical format correctly."""
    from app.mining.eclat import EclatMiner
    # Verify vertical format conversion

def test_eclat_validation():
    """Test Eclat results match FP-Growth (validation)."""
    # Run both algorithms on same data
    # Verify similar results (within tolerance)
```

**Acceptance**: All tests pass, >75% coverage of `eclat.py`.

---

### Task 1.6: Test Scoring Functions
**File**: `app/tests/test_scoring.py` (CREATE NEW)  
**Target**: `app/score/` directory

**Test Cases**:
```python
"""Tests for scoring functions."""
import pytest
from app.score.profit_calculator import ProfitCalculator
from app.score.diversity_scorer import DiversityScorer
from app.score.multi_objective import MultiObjectiveScorer

def test_profit_calculation():
    """Test profit score calculation."""
    calculator = ProfitCalculator()
    # Test with known margin values
    # Verify profit score formula

def test_diversity_within_context():
    """Test diversity scoring only within same context."""
    scorer = DiversityScorer()
    # Create rules in same context
    # Verify diversity penalty applied correctly

def test_diversity_cross_context():
    """Test diversity scoring does NOT penalize cross-context."""
    # Create same rule in different contexts
    # Verify no penalty applied

def test_multi_objective_scoring():
    """Test multi-objective score combines all factors."""
    scorer = MultiObjectiveScorer()
    # Test with known weights
    # Verify final score calculation

def test_score_normalization():
    """Test per-context score normalization."""
    # Verify scores normalized within context groups
```

**Acceptance**: All tests pass, >85% coverage of scoring modules.

---

### Task 1.7: Test Causal Estimator
**File**: `app/tests/test_causal.py` (CREATE NEW)  
**Target**: `app/causal/causal_estimator.py`

**Test Cases**:
```python
"""Tests for causal uplift estimation."""
import pytest
from app.causal.causal_estimator import CausalEstimator
from app.mining.context_types import ContextualRule, Context

def test_t_learner_initialization():
    """Test T-Learner can be instantiated."""
    estimator = CausalEstimator()
    assert estimator is not None

def test_uplift_estimation():
    """Test uplift estimation on known rule."""
    estimator = CausalEstimator()
    # Create rule and transaction data
    # Verify uplift result structure

def test_min_incremental_lift_threshold():
    """Test min_incremental_lift threshold filtering."""
    # Test that low uplift is filtered out

def test_insufficient_data_handling():
    """Test handling of insufficient data for estimation."""
    # Should return None or default, not crash

def test_confidence_interval_calculation():
    """Test confidence interval is calculated correctly."""
    # Verify CI is tuple of (lower, upper)
```

**Acceptance**: All tests pass, >80% coverage of causal modules.

---

### Task 1.8: Test API Endpoints
**File**: `app/tests/test_api.py` (CREATE NEW)  
**Target**: `app/api/routes.py`

**Test Cases**:
```python
"""Tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.api.main import create_app

@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)

def test_health_endpoint(client):
    """Test /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_upload_csv_endpoint(client, sample_csv_path):
    """Test /api/upload endpoint."""
    with open(sample_csv_path, "rb") as f:
        response = client.post("/api/upload", files={"file": f})
    assert response.status_code == 200
    assert "rows_imported" in response.json()

def test_rules_endpoint(client):
    """Test /api/rules endpoint."""
    response = client.get("/api/rules")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_bundles_endpoint(client):
    """Test /api/bundles endpoint."""
    response = client.get("/api/bundles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_whatif_endpoint(client):
    """Test /api/whatif endpoint."""
    payload = {
        "antecedent": ["milk"],
        "consequent": ["cereal"],
        "anticipated_discount_pct": 0.1
    }
    response = client.post("/api/whatif", json=payload)
    assert response.status_code == 200
    assert "projected_attach_rate" in response.json()

def test_api_error_handling(client):
    """Test API error handling."""
    # Test invalid requests
    # Verify meaningful error messages
```

**Acceptance**: All tests pass, >80% coverage of API routes.

---

### Task 1.9: Test Integration Pipeline
**File**: `app/tests/test_integration.py` (CREATE NEW)

**Test Cases**:
```python
"""End-to-end integration tests."""
import pytest
from app.ingest.csv_importer import CSVImporter
from app.api.services import AnalyticsService

def test_full_pipeline(temp_db, sample_csv_path):
    """Test CSV → mining → scoring → uplift pipeline."""
    # 1. Import CSV
    importer = CSVImporter(db_path=temp_db.db_path)
    importer.import_csv(str(sample_csv_path))
    
    # 2. Mine rules
    service = AnalyticsService()
    rules = service.get_rules(RuleFilter())
    
    # 3. Verify rules have scores
    assert len(rules) > 0
    assert all(r.overall_score is not None for r in rules)

def test_api_to_ui_flow():
    """Test API responses work with UI."""
    # Verify API response format matches UI expectations
```

**Acceptance**: All integration tests pass.

---

### Task 1.10: Run Coverage Report
**Command**: `pytest --cov=app --cov-report=html --cov-report=term`  
**Action**: Verify >80% coverage, fix any gaps.

**Acceptance**: Coverage report shows >80% overall coverage.

---

## 📚 SECTION 2: Documentation (CRITICAL)

### Task 2.1: Create METHODS.md
**File**: `docs/METHODS.md` (CREATE NEW)  
**Reference**: `soul.md` (abstract)

**Content Structure**:
```markdown
# ProfitLift Methodology

## 1. Context-Aware Rule Mining

### FP-Growth Algorithm
[Explain FP-Growth with equations]

### Eclat Algorithm
[Explain Eclat as validation]

### Context Segmentation
[Explain time bins, weekday/weekend, quarters]

## 2. Multi-Objective Scoring

### Score Formula
[Mathematical formula combining lift, profit, diversity, confidence]

### Profit Calculation
[How profit_score is calculated]

### Diversity Scoring
[How diversity_score works within context]

## 3. Causal Uplift Estimation

### T-Learner Approach
[Explain T-Learner methodology]

### Treatment Simulation
[How treatment groups are simulated]

### Uplift Metrics
[Incremental attach rate, margin, confidence intervals]
```

**Acceptance**: Document exists, contains all equations from abstract.

---

### Task 2.2: Create DESIGN.md
**File**: `docs/DESIGN.md` (CREATE NEW)

**Content Structure**:
```markdown
# ProfitLift System Design

## Architecture Overview
[High-level architecture diagram description]

## Component Structure
- `app/ingest/` - Data ingestion
- `app/mining/` - Rule mining
- `app/score/` - Scoring functions
- `app/causal/` - Uplift estimation
- `app/api/` - FastAPI backend
- `app/ui/` - Streamlit frontend

## Data Flow
[Describe: CSV → Database → Mining → Scoring → API → UI]

## Database Schema
[Reference schema.sql, explain tables]

## API Design
[Document all endpoints, request/response formats]
```

**Acceptance**: Document exists, explains system architecture clearly.

---

### Task 2.3: Create METRICS.md
**File**: `docs/METRICS.md` (CREATE NEW)

**Content Structure**:
```markdown
# Evaluation Metrics

## Metrics Definitions
- Attach Rate Uplift
- Incremental Margin per Basket
- Time to Insight
- Team Adoption

## Evaluation Protocol
[How to run evaluation on benchmark datasets]

## Baseline Comparison
[Comparison with traditional MBA (Apriori)]
```

**Acceptance**: Document exists, defines all success metrics from BRD.

---

### Task 2.4: Create DECISIONS.md
**File**: `docs/DECISIONS.md` (CREATE NEW)

**Content Structure**:
```markdown
# Design Decisions

## Why Streamlit (not PyQt6)
[Rationale: faster development, easier packaging]

## Why T-Learner (not DR-Learner)
[Rationale: baseline approach, well-documented]

## Why FP-Growth + Eclat (not Apriori)
[Rationale: performance, validation]

## Why Context-Aware Mining
[Rationale: addresses abstract requirements]

## Why Multi-Objective Scoring
[Rationale: balances frequency and profit]
```

**Acceptance**: Document exists, explains all major design choices.

---

### Task 2.5: Create DEMO_SCRIPT.md
**File**: `docs/DEMO_SCRIPT.md` (CREATE NEW)

**Content Structure**:
```markdown
# ProfitLift Demo Script (1-minute walkthrough)

## Step 1: Launch Application
[Commands to start API and UI]

## Step 2: Upload Sample Data
[How to upload CSV]

## Step 3: View Rules
[Navigate to Rules page, show filters]

## Step 4: View Bundles
[Navigate to Bundles page, explain cards]

## Step 5: Run What-If
[Simulate a promotion scenario]

## Step 6: Export Results
[Download CSV/PDF]
```

**Acceptance**: Document exists, can be followed step-by-step.

---

### Task 2.6: Create USER_MANUAL.md
**File**: `docs/USER_MANUAL.md` (CREATE NEW)

**Content Structure**:
```markdown
# ProfitLift User Manual

## Installation
[Windows installer instructions]

## Getting Started
[First-time setup]

## Using the Dashboard
### Rules Page
[How to filter, interpret results]

### Bundles Page
[How to read bundle cards, understand priorities]

### What-If Simulator
[How to set up scenarios, interpret projections]

## Exporting Data
[How to export CSV/PDF]

## Troubleshooting
[Common issues and solutions]
```

**Acceptance**: Document exists, written for non-technical users.

---

### Task 2.7: Create QUICK_START.md
**File**: `docs/QUICK_START.md` (CREATE NEW)

**Content**: 5-minute tutorial for new users.

**Acceptance**: Document exists, gets users running quickly.

---

### Task 2.8: Create HOW_TO_GET_DATA.md
**File**: `docs/HOW_TO_GET_DATA.md` (CREATE NEW)

**Content**: Instructions for downloading Instacart and Dunnhumby datasets.

**Acceptance**: Document exists, includes download links and format conversion steps.

---

### Task 2.9: Create DATA_FORMAT.md
**File**: `docs/DATA_FORMAT.md` (CREATE NEW)

**Content**: CSV format specification with required/optional columns.

**Acceptance**: Document exists, includes example CSV.

---

### Task 2.10: Update README.md
**File**: `README.md` (MODIFY EXISTING)

**Add Sections**:
- Architecture overview
- Troubleshooting
- Development setup
- Testing instructions

**Acceptance**: README is comprehensive and helpful.

---

## 📦 SECTION 3: Windows Packaging (CRITICAL)

### Task 3.1: Create PyInstaller Spec File
**File**: `ProfitLift.spec` (CREATE NEW)

**Content**:
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/ui/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('data/sample', 'data/sample'),
    ],
    hiddenimports=[
        'streamlit',
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'scikit-learn',
        'mlxtend',
        'reportlab',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ProfitLift',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if available
)
```

**Acceptance**: Spec file exists, can build EXE with `pyinstaller ProfitLift.spec`.

---

### Task 3.2: Create Inno Setup Script
**File**: `installer.iss` (CREATE NEW)

**Content**:
```ini
[Setup]
AppName=ProfitLift
AppVersion=1.0.0
AppPublisher=ProfitLift Team
DefaultDirName={pf}\ProfitLift
DefaultGroupName=ProfitLift
OutputDir=Output
OutputBaseFilename=ProfitLift-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\ProfitLift.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config\*.yaml"; DestDir: "{app}\config"; Flags: ignoreversion
Source: "data\sample\*.csv"; DestDir: "{app}\data\sample"; Flags: ignoreversion

[Icons]
Name: "{group}\ProfitLift"; Filename: "{app}\ProfitLift.exe"
Name: "{group}\Uninstall ProfitLift"; Filename: "{uninstallexe}"
Name: "{commondesktop}\ProfitLift"; Filename: "{app}\ProfitLift.exe"

[Run]
Filename: "{app}\ProfitLift.exe"; Description: "Launch ProfitLift"; Flags: nowait postinstall skipifsilent
```

**Acceptance**: Installer script exists, can create installer with Inno Setup.

---

### Task 3.3: Create GitHub Actions Workflow
**File**: `.github/workflows/windows-build.yml` (CREATE NEW)

**Content**:
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
          pip install pyinstaller
      
      - name: Build with PyInstaller
        run: |
          pyinstaller ProfitLift.spec
      
      - name: Install Inno Setup
        uses: amake/innosetup-action@v1
        with:
          path-to-iss: installer.iss
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: ProfitLift-Installer
          path: Output/ProfitLift-Setup.exe
```

**Acceptance**: Workflow file exists, can trigger builds.

---

### Task 3.4: Test EXE Build Locally
**Command**: `pyinstaller ProfitLift.spec`  
**Action**: Verify EXE is created in `dist/` directory.

**Acceptance**: EXE file exists and is executable.

---

### Task 3.5: Test Installer Creation
**Command**: Build installer using Inno Setup with `installer.iss`.  
**Action**: Verify installer is created in `Output/` directory.

**Acceptance**: Installer file exists.

---

## 🎨 SECTION 4: UI/UX Polish (IMPORTANT)

### Task 4.1: Review and Remove Gradients
**Files**: 
- `app/ui/pages/bundles_page.py` (lines 31-61)
- `app/ui/main.py`
- All UI pages

**Action**: 
1. Search for `gradient`, `linear-gradient`, `radial-gradient` in UI files
2. Replace with solid colors
3. Use simple color palette: white, light gray (#f5f5f5), dark gray (#333), accent blue (#1565c0)

**Acceptance**: No gradients found in UI code.

---

### Task 4.2: Simplify Color Palette
**Files**: All UI pages

**Action**:
1. Define color constants at top of files:
```python
COLORS = {
    'background': '#ffffff',
    'surface': '#f5f5f5',
    'text': '#333333',
    'text_secondary': '#666666',
    'accent': '#1565c0',
    'border': '#e0e0e0',
}
```

2. Replace all color values with constants
3. Remove any bright/vibrant colors

**Acceptance**: Consistent color palette used throughout.

---

### Task 4.3: Improve Form Layouts
**Files**: 
- `app/ui/pages/rules_page.py` (lines 21-60)
- `app/ui/pages/bundles_page.py` (lines 64-99)
- `app/ui/pages/whatif_page.py` (lines 44-75)

**Action**:
1. Add clear section headers
2. Improve spacing between form elements
3. Add helpful placeholders and hints
4. Group related fields together

**Acceptance**: Forms are clear and easy to understand.

---

### Task 4.4: Improve Error Messages
**Files**: All UI pages

**Action**:
1. Review all `st.error()` calls
2. Make messages user-friendly (no technical jargon)
3. Add suggestions for fixing errors

**Example**:
```python
# Bad
st.error(f"API error: {exc}")

# Good
st.error("Could not connect to the backend. Please make sure the API is running.")
```

**Acceptance**: All error messages are clear and helpful.

---

### Task 4.5: Add Helpful Tooltips
**Files**: All UI pages with form inputs

**Action**: Add `help` parameter to all inputs:
```python
st.text_input("Store", help="Enter store ID or leave blank for all stores")
```

**Acceptance**: All inputs have helpful tooltips.

---

### Task 4.6: Review Typography
**Files**: All UI pages

**Action**:
1. Ensure consistent font sizes
2. Use clear hierarchy (h1 > h2 > h3)
3. Ensure sufficient line spacing
4. Use readable font (Streamlit default is fine)

**Acceptance**: Typography is consistent and readable.

---

## 🔍 SECTION 5: Error Handling & Validation (IMPORTANT)

### Task 5.1: Validate CSV Format
**File**: `app/ingest/csv_importer.py`

**Action**: Add validation for:
- Required columns exist
- Data types are correct
- No empty required fields
- Timestamp format is valid

**Acceptance**: Invalid CSV shows clear error message.

---

### Task 5.2: Validate API Inputs
**File**: `app/api/routes.py`

**Action**: Add validation for:
- Filter parameters
- What-if request payload
- File upload format

**Acceptance**: Invalid API requests return 400 with clear error.

---

### Task 5.3: Handle Empty Results
**Files**: All UI pages

**Action**: Add friendly messages when no results found:
```python
if not rules:
    st.info("No rules found. Try adjusting your filters or uploading more data.")
```

**Acceptance**: Empty results show helpful messages.

---

### Task 5.4: Handle API Connection Failures
**File**: `app/ui/api_client.py`

**Action**: Improve error handling in `get_health()` and all API methods.

**Acceptance**: Connection failures show user-friendly messages.

---

## 📊 SECTION 6: Evaluation Framework (OPTIONAL BUT RECOMMENDED)

### Task 6.1: Create Evaluation Script
**File**: `scripts/evaluate.py` (CREATE NEW)

**Content**: Script to run evaluation on benchmark datasets.

**Acceptance**: Script exists and can run evaluation.

---

### Task 6.2: Implement Evaluation Metrics
**File**: `scripts/evaluate.py` (ADD TO EXISTING)

**Metrics**:
- Profit contribution
- Click-through rate (CTR)
- Basket size
- Incremental revenue

**Acceptance**: All metrics are calculated correctly.

---

### Task 6.3: Generate Evaluation Report
**File**: `scripts/evaluate.py` (ADD TO EXISTING)

**Action**: Generate markdown report with results and comparisons.

**Acceptance**: Report is generated in `docs/EVALUATION_REPORT.md`.

---

## ✅ SECTION 7: Final Verification

### Task 7.1: Run Full Test Suite
**Command**: `pytest --cov=app --cov-report=html`  
**Acceptance**: All tests pass, coverage >80%.

---

### Task 7.2: Build Windows Installer
**Commands**:
1. `pyinstaller ProfitLift.spec`
2. Build installer with Inno Setup
**Acceptance**: Installer created successfully.

---

### Task 7.3: Verify All Documentation
**Checklist**:
- [ ] `docs/METHODS.md` exists
- [ ] `docs/DESIGN.md` exists
- [ ] `docs/METRICS.md` exists
- [ ] `docs/DECISIONS.md` exists
- [ ] `docs/DEMO_SCRIPT.md` exists
- [ ] `docs/USER_MANUAL.md` exists
- [ ] `docs/QUICK_START.md` exists
- [ ] `README.md` is complete

**Acceptance**: All documentation files exist and are complete.

---

### Task 7.4: Verify UI Design
**Checklist**:
- [ ] No gradients found
- [ ] Consistent color palette
- [ ] Clear typography
- [ ] Helpful error messages
- [ ] All inputs have tooltips

**Acceptance**: UI meets premium, classy design requirements.

---

### Task 7.5: Verify BRD Compliance
**Reference**: `idea.md`

**Checklist**:
- [ ] Windows desktop app (packaged)
- [ ] Rules page
- [ ] Bundles page
- [ ] What-If simulator
- [ ] Help/Explanations page
- [ ] CSV import
- [ ] CSV export
- [ ] PDF export
- [ ] Plain-English explanations

**Acceptance**: All BRD requirements met.

---

## 🚀 Quick Reference: File Locations

**Key Files to Modify**:
- `app/tests/` - All test files (CREATE)
- `docs/` - All documentation (CREATE)
- `ProfitLift.spec` - PyInstaller config (CREATE)
- `installer.iss` - Inno Setup script (CREATE)
- `.github/workflows/windows-build.yml` - CI/CD (CREATE)
- `app/ui/pages/*.py` - UI polish (MODIFY)
- `README.md` - Update (MODIFY)

**Key Commands**:
```bash
# Run tests
pytest --cov=app

# Build EXE
pyinstaller ProfitLift.spec

# Start API
python -m app.api.main

# Start UI
streamlit run app/ui/main.py
```

---

**Last Updated**: [Auto-update on save]  
**Status**: Ready for AI agent execution  
**Priority**: Testing → Documentation → Packaging → UI Polish
