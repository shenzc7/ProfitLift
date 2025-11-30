"""FastAPI application entry point for ProfitLift."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List

import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.realtime import manager

CONFIG_PATH = Path("config/default.yaml")


def _resolve_path(relative: str) -> Path:
    """Resolve a config path, supporting frozen (PyInstaller) bundles."""
    candidates = [
        Path(relative),
        Path(__file__).resolve().parents[2] / relative,
        Path(getattr(sys, "_MEIPASS", "")) / relative,  # type: ignore[attr-defined]
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path(relative)


def _load_api_settings() -> dict:
    """Load API settings from the default configuration file."""
    config_path = _resolve_path(str(CONFIG_PATH))
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
            return data.get("api", {}) if isinstance(data, dict) else {}
    return {}


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    api_settings = _load_api_settings()
    title = "ProfitLift API"
    description = (
        "Context-aware profit-optimized market basket analytics serving the "
        "Streamlit front-end."
    )

    app = FastAPI(
        title=title,
        description=description,
        version="1.0.0",
    )

    # Enable CORS for local Streamlit UI and default localhost clients
    allowed_origins: List[str] = api_settings.get("allowed_origins", [])
    if not allowed_origins:
        allowed_origins = [
            "http://localhost",
            "http://localhost:8000",
            "http://localhost:8501",  # Streamlit
            "http://localhost:5173",  # Vite Dev
            "http://localhost:1420",  # Tauri
            "tauri://localhost",      # Tauri Production
            "http://127.0.0.1",
            "http://127.0.0.1:8501",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/api/health", tags=["health"])
    def healthcheck() -> dict:
        """Basic health check endpoint."""
        return {"status": "ok"}

    @app.websocket("/ws/soul")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    return app


app = create_app()


def run():
    """Run the FastAPI app with uvicorn."""
    api_settings = _load_api_settings()
    host = api_settings.get("host", "127.0.0.1")
    port = int(api_settings.get("port", 8000))

    logging.basicConfig(level=logging.INFO)

    import uvicorn

    uvicorn.run("app.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
