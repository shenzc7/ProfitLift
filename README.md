# ProfitLift 🚀

**Context-Aware, Profit-Optimized Market Basket Analysis for Indian Retail**

ProfitLift helps retailers discover product associations that actually drive profit — not just the most frequent patterns. Built for Indian retail with festival awareness and GST-linked margins.

---

## Key Features

| Feature | What It Does |
|---------|--------------|
| **Context-Aware Mining** | Discovers patterns per time-of-day, weekday/weekend, and festival (Diwali, Holi, Navratri) |
| **Profit-First Scoring** | Ranks bundles by margin contribution (40% weight), not just frequency |
| **Causal Uplift** | T-Learner estimates true incremental sales, not just correlation |
| **India-Optimized** | GST-aware margins, festival calendar, sparse-data handling for kiranas |

---

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Run Backend
```bash
uvicorn app.api.main:app --reload
```

### 3. Run Frontend
```bash
cd app/frontend
npm install
npm run dev
```

### 4. Upload Sample Data
- Open `http://localhost:5173`
- Go to **Upload** page
- Drop `data/sample/india_sample.csv`

### 5. Explore
- **Bundle Recommendations**: Ready-to-launch product bundles
- **Pattern Explorer**: All association rules with filters
- **What-If Simulator**: Test promotion scenarios

---

## Screenshots

### Bundle Recommendations
Shows top product bundles with profit impact and causal verification.

### Pattern Explorer
Filter by mode (Quick Insights / Balanced / Discovery) or advanced parameters.

### Festival Context
Automatically detects Diwali, Holi, and other Indian festivals in transaction data.

---

## One-Command Windows Install (Clone + Desktop Icon)

```powershell
$repo = "https://github.com/nonshenz007/ProfitLift.git"
powershell -ExecutionPolicy Bypass -File scripts/windows/oneclick_setup.ps1 -RepoUrl $repo
```

What this does:
- Uses winget to install Git, Python 3.11, Node.js LTS, Rust (MSVC), and Visual Studio Build Tools (for Tauri).
- Clones the repo to `%USERPROFILE%\ProfitLift` (or pulls latest if already there).
- Creates a Python virtualenv, installs backend deps, builds the Tauri desktop bundle, and packages the FastAPI backend with PyInstaller.
- Drops a **ProfitLift** icon on your Windows desktop that starts backend + desktop UI together (`scripts/windows/launch_profitlift.ps1`).

Run straight from GitHub (no initial clone):
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/nonshenz007/ProfitLift/main/scripts/windows/oneclick_setup.ps1 | iex"
```
> Winget needs admin to install build tools; if prompted, approve once.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [METHODS.md](docs/METHODS.md) | Technical methodology (algorithms, scoring) |
| [PRESENTATION_SUMMARY.md](docs/PRESENTATION_SUMMARY.md) | 5-minute presentation guide |
| [DATA_FORMAT.md](docs/DATA_FORMAT.md) | CSV format specification |
| [USER_MANUAL.md](docs/USER_MANUAL.md) | End-user guide |

---

## Windows Setup & Build (Backend + Desktop)

1. **Prereqs**: Python 3.11+, Node 18+, Rust stable, and *Visual Studio Build Tools* (Desktop development with C++) for Tauri.
2. **Backend (FastAPI)**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.api.main:app --host 0.0.0.0 --port 8000
   ```
3. **Desktop app (Tauri)**:
   ```powershell
   cd app/frontend
   npm install
   set VITE_API_URL=http://localhost:8000
   npm run tauri build   # Produces Windows exe/MSI in src-tauri/target/release/bundle
   ```
4. **Backend EXE (optional)**:
   ```powershell
   .\.venv\Scripts\activate
   pyinstaller ProfitLift.spec
   ```
   Use `installer.iss` with Inno Setup if you want a Windows installer that bundles the backend assets/config.

---

## Architecture

```
CSV → Context Enricher → SQLite → FP-Growth Miner → Multi-Obj Scorer → T-Learner → FastAPI → React UI
```

**Backend:** Python 3.11+, FastAPI, SQLite, scikit-learn  
**Frontend:** React, TypeScript, TailwindCSS, Vite

---

## Testing

```bash
pytest --cov=app
```

---

## For MTech Evaluation

This project demonstrates:

1. **Context-Aware MBA** — Novel segmentation by Indian festivals
2. **Multi-Objective Optimization** — Profit-weighted rule ranking
3. **Causal Inference** — T-Learner integration for uplift estimation
4. **End-to-End Pipeline** — From CSV to actionable recommendations

See [PRESENTATION_SUMMARY.md](docs/PRESENTATION_SUMMARY.md) for the 5-minute demo script.

---

## License

MIT License - see [LICENSE](LICENSE) file for details
