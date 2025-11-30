# ProfitLift - Tauri Edition 🚀

The UI has been migrated to a premium **React + Tauri** architecture.

## Prerequisites
- Node.js (v18+)
- Rust (stable)

## Quick Start

1. **Start the Backend**
   ```bash
   # Terminal 1
   source .venv_run/bin/activate
   uvicorn app.api.main:app --reload --port 8000
   ```

2. **Start the Frontend (Tauri)**
   ```bash
   # Terminal 2
   cd app/frontend
   npm install # (first time only)
   npm run tauri dev
   ```

### Windows notes
- Install Visual Studio Build Tools (Desktop development with C++) so Rust/Tauri can link.
- Set the API target if your backend runs elsewhere: `set VITE_API_URL=http://localhost:8000`.
- Build a Windows bundle: `npm run tauri build` (outputs under `src-tauri/target/release/bundle`).

## Architecture
- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons, Recharts, TanStack Table.
- **Backend**: FastAPI (Python).
- **Desktop Shell**: Tauri (Rust).

## Features
- **Dashboard**: Real-time health check and metrics.
- **Rules Explorer**: High-performance data grid with filters.
- **Bundles**: Card-based recommendation view.
- **What-If**: Interactive simulation form.
- **Upload**: Drag-and-drop CSV ingestion.
