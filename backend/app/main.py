"""
MindShield Backend — FastAPI Application Factory (Phase 2.3).

This module is the composition root of the backend. It:
  1. Instantiates the FastAPI application with metadata.
  2. Configures structured logging.
  3. Registers middleware (CORS, request logger).
  4. Registers global exception handlers.
  5. Registers all API routers.
  6. Manages the model loader & InferenceService lifecycle via ``lifespan``.

Architecture Rationale:
    The ``create_app()`` factory pattern allows tests to construct fresh, isolated
    application instances without shared state between test cases.

    The ``lifespan`` context manager handles startup/shutdown events, initialising
    the ``ModelLoaderFactory`` and ``InferenceService`` with graceful fallback
    handling.
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
from app.core.mock_model_loader import MockModelLoader
from app.core.model_loader import BaseModelLoader, ModelLoaderFactory
from app.logging.logger import configure_logging, get_logger
from app.middleware.cors import configure_cors
from app.middleware.request_logger import RequestLoggerMiddleware
from app.routers import health as health_router
from app.routers.v1 import analysis as analysis_router
from app.services.inference_service import InferenceService

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Module-level registry singletons (populated during lifespan startup).
# ---------------------------------------------------------------------------
_model_loader: BaseModelLoader | None = None
_inference_service: InferenceService | None = None
_startup_time: float = 0.0


def get_model_loader(settings: Settings | None = None) -> BaseModelLoader:
    """Return the application-wide model loader instance.

    Guaranteed to be non-None after the lifespan startup completes.
    """
    if _model_loader is None:
        raise RuntimeError(
            "Model loader has not been initialised. "
            "Ensure the FastAPI lifespan has completed startup."
        )
    return _model_loader


def get_inference_service(settings: Settings | None = None) -> InferenceService:
    """Return the application-wide InferenceService singleton.

    Called by dependency injection providers.
    """
    if _inference_service is None:
        if _model_loader is not None:
            return InferenceService(loader=_model_loader)
        raise RuntimeError(
            "InferenceService has not been initialised. "
            "Ensure the FastAPI lifespan has completed startup."
        )
    return _inference_service


# ---------------------------------------------------------------------------
# Lifespan — Startup & Shutdown
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle (Phase 2.3).

    Startup:
        1. Configure structured logging.
        2. Resolve model backend from Settings ('mock', 'huggingface', 'placeholder').
        3. Instantiate primary model loader via ModelLoaderFactory.
        4. Load model weights & warm up.
        5. If primary loading fails and fallback is enabled, initialize MockModelLoader.
        6. Instantiate InferenceService with fallback recovery.
        7. Log server readiness and active model health.

    Shutdown:
        1. Log shutdown signal.
        2. Unload primary & fallback model loaders.
    """
    global _model_loader, _inference_service, _startup_time

    settings = get_settings()

    # Step 1 — Configure structured logging
    configure_logging(level=settings.log_level, fmt=settings.log_format)
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.app_version,
        settings.app_env,
    )

    # Step 2 & 3 — Factory instantiate primary model loader
    fallback_loader: BaseModelLoader | None = None
    if settings.model_fallback_enabled and settings.model_backend != "mock":
        fallback_loader = MockModelLoader()
        fallback_loader.load()

    try:
        _model_loader = ModelLoaderFactory.create_loader(
            backend=settings.model_backend,
            model_path=settings.model_path,
            model_version=settings.model_version,
        )
        _model_loader.load()
        logger.info(
            "Primary model loader '%s' loaded successfully.",
            _model_loader.backend_type,
        )
    except Exception as exc:
        logger.error(
            "Failed to load primary model loader backend '%s': %s",
            settings.model_backend,
            exc,
            exc_info=True,
        )
        if settings.model_fallback_enabled:
            logger.warning(
                "Activating fallback MockModelLoader due to primary load error."
            )
            _model_loader = fallback_loader or MockModelLoader()
            if not _model_loader.is_loaded:
                _model_loader.load()
        else:
            raise

    # Step 6 — Create InferenceService singleton
    _inference_service = InferenceService(
        loader=_model_loader,
        fallback_loader=fallback_loader,
        fallback_enabled=settings.model_fallback_enabled,
    )

    _startup_time = time.monotonic()
    health_info = _inference_service.health()

    logger.info(
        "InferenceService ready | backend=%s version=%s loaded=%s",
        health_info.backend_type,
        health_info.model_version,
        health_info.is_loaded,
    )
    logger.info(
        "%s is ready — listening on %s:%d",
        settings.app_name,
        settings.host,
        settings.port,
    )

    yield  # ← FastAPI handles requests here

    # Shutdown
    logger.info("Shutdown signal received — cleaning up model resources.")
    if _model_loader:
        try:
            _model_loader.unload()
        except Exception as exc:  # pragma: no cover
            logger.warning("Error unloading primary model loader: %s", exc)
    if fallback_loader:
        try:
            fallback_loader.unload()
        except Exception as exc:  # pragma: no cover
            logger.warning("Error unloading fallback model loader: %s", exc)

    _model_loader = None
    _inference_service = None
    logger.info("Shutdown complete.")


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------


def _mindshield_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all ``MindShieldException`` subclasses."""
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
    """Handle Pydantic RequestValidationError (HTTP 422)."""
    assert isinstance(exc, RequestValidationError)
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = " → ".join(str(loc) for loc in first_error.get("loc", []))
    message = f"Validation failed on '{field}': {first_error.get('msg', 'unknown')}"

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
    """Handle Starlette's HTTPException."""
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
    """Catch-all handler for unexpected exceptions."""
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
    """Construct and configure the FastAPI application."""
    cfg = settings or get_settings()

    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        description=(
            "MindShield is an AI-powered SMS cybersecurity platform. "
            "This API classifies SMS messages as safe, suspicious, or "
            "dangerous using heuristic and AI model analysis.\n\n"
            "**Phase 2.3** — AI Model Loading & Inference Architecture. "
            "Supports decoupled ModelLoaders (Mock, HuggingFace, ONNX), "
            "InferenceService orchestration, and graceful failure recovery."
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
                    "SMS classification endpoints powered by InferenceService."
                ),
            },
        ],
    )

    # Middleware
    configure_cors(app, cfg)
    app.add_middleware(RequestLoggerMiddleware)

    # Exception Handlers
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

    # Routers
    app.include_router(health_router.router)
    app.include_router(
        analysis_router.router,
        prefix=cfg.api_v1_prefix,
    )

    logger.debug("FastAPI application created with %d routes", len(app.routes))
    return app


# ASGI entry point
app = create_app()
