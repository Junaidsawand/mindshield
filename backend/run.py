"""
MindShield Backend — Development Server Entry Point.

Run the FastAPI application using Uvicorn for local development.

Usage:
    python run.py

Or directly via uvicorn:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import uvicorn

from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=False,  # We use our own RequestLoggerMiddleware
    )
