# ProfitLift 🚀

**Context-Aware, Profit-Optimized Market Basket Analysis for Indian Retail**

ProfitLift helps retailers discover product associations that actually drive profit — not just the most frequent patterns. Built for Indian retail with festival awareness and GST-linked margins.

> **🎯 Windows Users:** Copy-paste this **one command** to install everything:
> ```powershell
> powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/shenzc7/ProfitLift/main/scripts/windows/oneclick_setup.ps1 | iex"
> ```
> Creates a desktop icon - just double-click to launch! ✨

---

## Key Features

| Feature | What It Does |
|---------|--------------|
| **Context-Aware Mining** | Discovers patterns per time-of-day, weekday/weekend, and festival (Diwali, Holi, Navratri) |
| **Profit-First Scoring** | Ranks bundles by margin contribution (40% weight), not just frequency |
| **Causal Uplift** | T-Learner estimates true incremental sales, not just correlation |
| **India-Optimized** | GST-aware margins, festival calendar, sparse-data handling for kiranas |

---

## 🚀 One-Command Windows Install

**Copy-paste this single command in PowerShell (admin recommended):**

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/shenzc7/ProfitLift/main/scripts/windows/oneclick_setup.ps1 | iex"
```

**What it does:**
- ✅ Installs Git, Python 3.11, Node.js LTS, Rust, Visual Studio Build Tools
- ✅ Clones ProfitLift repository
- ✅ Creates virtual environment & installs dependencies
- ✅ Builds Tauri desktop app + packages backend
- ✅ **Creates desktop icon** - just double-click to launch!

**That's it!** One command → desktop icon → done. Works on any Windows machine.

---

## Quick Start (After Install)

1. **Double-click the "ProfitLift" icon** on your desktop
2. Upload sample data: `data/sample/india_sample.csv`
3. Explore bundle recommendations & insights!

---

## What You'll Get

| Feature | Description |
|---------|-------------|
| **Context-Aware Mining** | Patterns by time-of-day, weekday/weekend, festivals |
| **Profit-First Scoring** | Ranks by margin contribution, not just frequency |
| **Causal Uplift** | T-Learner estimates true incremental sales |
| **India-Optimized** | GST-aware margins, festival calendar |

---

## Screenshots

### Bundle Recommendations
Top product bundles with profit impact and causal verification.

### Pattern Explorer
Filter by mode (Quick Insights / Balanced / Discovery) or advanced parameters.

### Festival Context
Automatically detects Diwali, Holi, and other Indian festivals.

---

## 📚 Documentation

- **[USER_MANUAL.md](docs/USER_MANUAL.md)** - Complete user guide
- **[METHODS.md](docs/METHODS.md)** - Technical methodology & algorithms
- **[DATA_FORMAT.md](docs/DATA_FORMAT.md)** - CSV format specification
- **[PRESENTATION_SUMMARY.md](docs/PRESENTATION_SUMMARY.md)** - 5-minute demo guide

---

## 🛠️ Manual Setup (Advanced Users)

For developers who prefer manual setup:

### Prerequisites
- Python 3.11+, Node.js 18+, Rust stable
- Visual Studio Build Tools (for Tauri desktop app)

### Quick Manual Install
```bash
# Backend
pip install -r requirements.txt
uvicorn app.api.main:app --reload

# Frontend (new terminal)
cd app/frontend
npm install
npm run dev

# Then open http://localhost:5173
```

### Full Desktop Build (Advanced)
```powershell
# Backend packaging
pyinstaller ProfitLift.spec

# Desktop app build
cd app/frontend
npm install
npm run tauri build
```

**Note:** The one-command installer above handles all of this automatically!

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
