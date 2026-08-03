"""
MindShield Backend — Analysis API v1 Router.

Handles the core SMS classification endpoint:
    POST /api/v1/analyze

The router is intentionally thin — it validates HTTP-level concerns
(request parsing, authentication headers in future phases) and
delegates all business logic to ``AnalysisService``.

API Versioning:
    This router is registered under the ``/api/v1`` prefix defined in
    ``Settings.api_v1_prefix``. When the API surface changes in a
    breaking way, a new ``/api/v2`` prefix will be introduced, and
    this module will remain frozen, preserving backwards compatibility
    for existing Flutter clients.

Phase 2.1 Behaviour:
    The endpoint returns a valid ``AnalysisResult`` with
    ``is_placeholder=True``, clearly signalling to clients that no
    real AI inference was performed. The Flutter app can display a
    disclaimer accordingly.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.config import Settings, get_settings
from app.core.model_loader import BaseModelLoader
from app.logging.logger import get_logger
from app.schemas.analysis import AnalysisRequest, AnalysisResult
from app.schemas.common import APIResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyze", tags=["Analysis"])
logger = get_logger(__name__)


def _get_model_loader(
    settings: Settings = Depends(get_settings),
) -> BaseModelLoader:
    """Resolve model loader from application state."""
    from app.main import get_model_loader  # noqa: PLC0415

    return get_model_loader(settings)


def _get_analysis_service(
    model_loader: BaseModelLoader = Depends(_get_model_loader),
) -> AnalysisService:
    """Construct and return an ``AnalysisService`` instance.

    FastAPI creates this per-request by default. Because the service
    is stateless (it holds only the model_loader reference), this is
    efficient — no shared mutable state, no concurrency issues.
    """
    return AnalysisService(model_loader=model_loader)


@router.post(
    "",
    response_model=APIResponse[AnalysisResult],
    status_code=status.HTTP_200_OK,
    summary="Analyse SMS Message",
    description=(
        "Classifies an SMS message body as safe, suspicious, or dangerous. "
        "In Phase 2.1 returns a placeholder response. "
        "Real AI inference will be active from Phase 2.2."
    ),
    responses={
        200: {"description": "Analysis successful"},
        422: {"description": "Invalid request payload"},
        503: {"description": "AI model not available"},
    },
)
async def analyse_message(
    request: AnalysisRequest,
    service: AnalysisService = Depends(_get_analysis_service),
) -> APIResponse[AnalysisResult]:
    """Classify an SMS message and return a structured verdict.

    Args:
        request: Validated ``AnalysisRequest`` parsed from request body.
        service: Injected ``AnalysisService`` instance.

    Returns:
        ``APIResponse[AnalysisResult]`` envelope with classification data.

    Raises:
        ValidationException:    If message content fails business validation.
        ModelNotReadyException: If the model loader is not initialised.
    """
    result: AnalysisResult = service.analyse(
        message=request.message,
        sender=request.sender,
    )

    logger.info(
        "POST /analyze → %s (confidence=%.2f, placeholder=%s)",
        result.threat_level,
        result.confidence,
        result.is_placeholder,
    )

    return APIResponse[AnalysisResult].ok(
        data=result,
        message="Analysis complete",
    )


@router.get(
    "/status",
    response_model=APIResponse[dict],  # type: ignore[type-arg]
    summary="API v1 Status",
    description="Returns the operational status of API version 1.",
)
async def api_status(
    settings: Settings = Depends(get_settings),
    model_loader: BaseModelLoader = Depends(_get_model_loader),
) -> APIResponse[dict]:  # type: ignore[type-arg]
    """Return metadata about the API v1 availability.

    Args:
        settings:     Injected application settings.
        model_loader: Injected model loader for health data.

    Returns:
        ``APIResponse`` with API version information.
    """
    model_health = model_loader.health()
    return APIResponse[dict].ok(  # type: ignore[type-arg]
        data={
            "api_version": "v1",
            "app_version": settings.app_version,
            "environment": settings.app_env,
            "model_version": model_health.model_version,
            "model_loaded": model_health.is_loaded,
            "endpoints": [
                "POST /api/v1/analyze",
                "GET  /api/v1/analyze/status",
            ],
        },
        message="API v1 is operational",
    )
