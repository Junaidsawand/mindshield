"""
MindShield Backend — FastAPI Application Factory.

This module is the composition root of the backend. It:
  1. Instantiates the FastAPI application with metadata.
  2. Configures structured logging.
  3. Registers middleware (CORS, request logger).
  4. Registers global exception handlers.
  5. Registers all API routers.
  6. Manages the model loader lifecycle via ``lifespan``.

Architecture Rationale:
    The ``create_app()`` factory pattern (rather than a module-level
    ``app = FastAPI()``) allows tests to construct fresh, isolated
    application instances without shared state between test cases.

    The ``lifespan`` context manager handles startup/shutdown events
    as recommended by FastAPI 0.93+ (replaces ``@app.on_event``).
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import Settings, get_settings
from app.core.exceptions import MindShieldException
from app.core.model_loader import BaseModelLoader, PlaceholderModelLoader
from app.logging.logger import configure_logging, get_logger
from app.middleware.cors import configure_cors
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import health as health_router
from app.routers.v1 import analysis as analysis_router

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level model loader registry (application singleton).
# Populated during lifespan startup, accessed via get_model_loader().
# ---------------------------------------------------------------------------
_model_loader: BaseModelLoader | None = None
_startup_time: float = 0.0


def get_model_loader(settings: Settings | None = None) -> BaseModelLoader:
    """Return the application-wide model loader instance.

    Called by router dependencies. Guaranteed to be non-None after
    the lifespan startup completes.

    Args:
        settings: Unused in Phase 2.1 — signature kept for forward
                  compatibility when different loader types are chosen
                  based on settings.

    Returns:
        The active ``BaseModelLoader`` implementation.

    Raises:
        RuntimeError: If called before application startup completes.
    """
    if _model_loader is None:
        raise RuntimeError(
            "Model loader has not been initialised. "
            "Ensure the FastAPI lifespan has completed startup."
        )
    return _model_loader


# ---------------------------------------------------------------------------
# Lifespan — Startup & Shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Startup:
        1. Configure logging.
        2. Load model (PlaceholderModelLoader in Phase 2.1).
        3. Log server-ready message.

    Shutdown:
        1. Log shutdown signal.
        2. Release any model resources (no-op in Phase 2.1).

    The ``yield`` statement is where FastAPI handles requests.
    """
    global _model_loader, _startup_time

    settings = get_settings()

    # Step 1 — Configure structured logging
    configure_logging(level=settings.log_level, fmt=settings.log_format)
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )

    # Step 2 — Initialise model loader
    _model_loader = PlaceholderModelLoader()
    _model_loader.load()
    model_health = _model_loader.health()

    _startup_time = time.monotonic()

    logger.info(
        "Model loader ready: %s (loaded=%s)",
        model_health.model_version,
        model_health.is_loaded,
    )
    logger.info(
        "%s is ready — listening on %s:%d",
        settings.app_name,
        settings.host,
        settings.port,
    )

    yield  # ← FastAPI handles all requests here

    # Shutdown
    logger.info("Shutdown signal received — cleaning up.")
    _model_loader = None
    logger.info("Shutdown complete.")


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------


def _mindshield_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all ``MindShieldException`` subclasses.

    Converts application exceptions into a consistent JSON envelope
    matching the ``APIResponse.fail()`` structure. The HTTP status
    code is read from the exception class attribute set in
    ``app/core/exceptions.py``.
    """
    assert isinstance(exc, MindShieldException)
    logger.warning(
        "Application exception [%s]: %s",
        exc.error_code,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.http_status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "error": {
                "error_code": exc.error_code,
                "message": exc.message,
            },
        },
    )


def _validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Pydantic RequestValidationError (HTTP 422).

    Rewrites Pydantic's default validation error into the standard
    ``APIResponse`` envelope format for consistent client parsing.

    Note:
        Pydantic v2 may embed raw ``ValueError`` objects inside the
        ``ctx`` key of error dicts. These are not JSON-serialisable,
        so we serialise the details list to plain strings here.
    """
    assert isinstance(exc, RequestValidationError)
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = " → ".join(str(loc) for loc in first_error.get("loc", []))
    message = f"Validation failed on '{field}': {first_error.get('msg', 'unknown')}"

    # Pydantic v2 may include non-serialisable objects (e.g. ValueError)
    # inside `ctx`. Stringify each error dict to guarantee JSON safety.
    safe_details = [
        {
            "loc": list(e.get("loc", [])),
            "msg": str(e.get("msg", "")),
            "type": str(e.get("type", "")),
        }
        for e in errors
    ]

    logger.info("Request validation error: %s", message)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": message,
            "data": None,
            "error": {
                "error_code": "validation_error",
                "message": message,
                "details": safe_details,
            },
        },
    )


def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle Starlette's HTTPException (e.g., 404 Not Found).

    Wraps FastAPI's built-in HTTP errors in the standard envelope.
    """
    assert isinstance(exc, StarletteHTTPException)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None,
            "error": {
                "error_code": f"http_{exc.status_code}",
                "message": exc.detail,
            },
        },
    )


def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions.

    Logs the full traceback and returns a generic 500 response.
    Never exposes internal details to the client.
    """
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred.",
            "data": None,
            "error": {
                "error_code": "internal_error",
                "message": "An internal server error occurred.",
            },
        },
    )


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------


def create_app(settings: Settings | None = None) -> FastAPI:
    """Construct and configure the FastAPI application.

    The factory pattern allows tests to call ``create_app()`` with
    custom ``settings`` (e.g., ``DEBUG=True``, test origins) without
    affecting the global singleton used in production.

    Args:
        settings: Optional ``Settings`` override. Defaults to the
                  cached production settings from ``get_settings()``.

    Returns:
        A fully configured ``FastAPI`` application instance.
    """
    cfg = settings or get_settings()

    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        description=(
            "MindShield is an AI-powered SMS cybersecurity platform. "
            "This API classifies SMS messages as safe, suspicious, or "
            "dangerous using NLP-based machine learning models.\n\n"
            "**Phase 2.1** — Backend foundation with placeholder model. "
            "Real inference will be activated in Phase 2.2."
        ),
        contact={
            "name": "Junaid Ahmed",
            "email": "junaid@mindshield.app",
        },
        license_info={"name": "MIT"},
        docs_url="/docs" if cfg.debug or not cfg.is_production else None,
        redoc_url="/redoc" if cfg.debug or not cfg.is_production else None,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "Health",
                "description": "Server liveness and readiness endpoints.",
            },
            {
                "name": "Analysis",
                "description": (
                    "SMS classification endpoints. " "Placeholder in Phase 2.1."
                ),
            },
        ],
    )

    # ------------------------------------------------------------------
    # Middleware (order matters — registered in reverse execution order)
    # ------------------------------------------------------------------
    configure_cors(app, cfg)

    # RequestLoggerMiddleware must be added AFTER CORSMiddleware
    app.add_middleware(RequestLoggerMiddleware)

    # ------------------------------------------------------------------
    # Exception Handlers
    # ------------------------------------------------------------------
    app.add_exception_handler(  # type: ignore[arg-type]
        MindShieldException, _mindshield_exception_handler
    )
    app.add_exception_handler(  # type: ignore[arg-type]
        RequestValidationError, _validation_exception_handler
    )
    app.add_exception_handler(  # type: ignore[arg-type]
        StarletteHTTPException, _http_exception_handler
    )
    app.add_exception_handler(Exception, _unhandled_exception_handler)

    # ------------------------------------------------------------------
    # Routers
    # ------------------------------------------------------------------
    app.include_router(health_router.router)
    app.include_router(
        analysis_router.router,
        prefix=cfg.api_v1_prefix,
    )

    logger.debug("FastAPI application created with %d routes", len(app.routes))
    return app


# ---------------------------------------------------------------------------
# ASGI entry point (used by uvicorn)
# ---------------------------------------------------------------------------
app = create_app()
