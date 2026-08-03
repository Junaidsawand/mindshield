"""
MindShield Backend — Health Router.

Provides the ``GET /health`` endpoint which is used by:
  - Load balancers (readiness / liveness probes in Kubernetes)
  - Monitoring tools (UptimeRobot, Prometheus scrapers)
  - The Flutter app startup check

Response Codes:
    200 OK      — Server is running, model may or may not be loaded.
    503         — Would be returned if critical subsystems fail
                  (not implemented in Phase 2.1 — no DB or model required).

Design Note:
    The health endpoint deliberately does NOT require the model to be
    loaded to return 200. Model availability is reported in the
    ``model_loaded`` field. Separating server health from model health
    allows load balancers to route traffic to the server even when the
    model is loading (warm-up window).
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.model_loader import BaseModelLoader
from app.logging.logger import get_logger
from app.schemas.common import HealthStatus

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)

# Module-level startup timestamp for uptime calculation
_START_TIME: float = time.monotonic()


def _get_model_loader(
    settings: Settings = Depends(get_settings),
) -> BaseModelLoader:
    """Dependency that returns the model loader from app state.

    FastAPI resolves this at request time by pulling the loader
    from the application's state, which was populated during startup.
    """
    from app.main import get_model_loader  # noqa: PLC0415 — avoid circular import

    return get_model_loader(settings)


@router.get(
    "/health",
    response_model=HealthStatus,
    summary="Health Check",
    description=(
        "Returns the operational status of the MindShield API server. "
        "Used by load balancers and monitoring systems."
    ),
)
async def health_check(
    settings: Settings = Depends(get_settings),
    model_loader: BaseModelLoader = Depends(_get_model_loader),
) -> HealthStatus:
    """Return server health and model availability status.

    Args:
        settings:     Injected application settings.
        model_loader: Injected model loader (placeholder in Phase 2.1).

    Returns:
        ``HealthStatus`` schema with server metadata and model state.
    """
    model_health = model_loader.health()
    uptime = time.monotonic() - _START_TIME

    logger.debug(
        "Health check requested — uptime %.1fs, model_loaded=%s",
        uptime,
        model_health.is_loaded,
    )

    return HealthStatus(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        model_loaded=model_health.is_loaded,
        model_version=model_health.model_version,
        uptime_seconds=round(uptime, 2),
    )
