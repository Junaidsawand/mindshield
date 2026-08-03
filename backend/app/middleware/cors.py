"""
MindShield Backend — CORS Configuration.

Cross-Origin Resource Sharing (CORS) must be configured before the
Flutter mobile application (or any web client) can communicate with
the API from a different origin.

Security Rationale:
    In production, ``allowed_origins`` is restricted to known client
    origins (e.g., the Flutter web build URL or internal services).
    Using ``allow_origins=["*"]`` is explicitly avoided in production
    as it exposes the API to arbitrary cross-origin requests.

    ``allow_credentials=True`` is omitted because Phase 2.1 has no
    session cookies or authentication headers. It will be added when
    auth is implemented in a future phase.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Register CORSMiddleware on the FastAPI application.

    Should be called in the application factory (``create_app``) before
    any routers are registered so CORS headers appear on all responses
    including error responses generated before route matching.

    Args:
        app:      The FastAPI application instance.
        settings: Application settings containing CORS origin list.
    """
    origins = settings.cors_origins

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,  # No auth cookies in Phase 2.1
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID", "Accept"],
        expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
        max_age=86_400,  # Cache preflight for 24 h
    )
