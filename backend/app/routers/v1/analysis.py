"""
MindShield Backend — Analysis API v1 Router (Phase 2.2).

Handles the core SMS classification endpoint:
    POST /api/v1/analyze

Phase 2.2 enhancements:
    - Request body now supports optional ``metadata`` block.
    - Response includes ``indicators``, ``processing_time_ms``,
      ``request_id``, and ``mock_mode``.
    - Full OpenAPI documentation: descriptions, multiple examples,
      all response codes documented with schemas.
    - ``request_id`` extracted from middleware state and propagated
      to the service for end-to-end log correlation.
    - ``openapi_extra`` used to attach additional Swagger UI metadata.

API Versioning:
    Registered under ``/api/v1`` prefix. Breaking changes will introduce
    ``/api/v2``; this router remains frozen for backward compatibility.

Router Design (Thin Controller):
    All business logic lives in ``AnalysisService``. This router:
      1. Declares HTTP method, path, and OpenAPI metadata.
      2. Extracts request_id from Starlette middleware state.
      3. Calls the service with the validated request data.
      4. Wraps the result in the ``APIResponse`` envelope.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

from app.core.config import Settings, get_settings
from app.core.model_loader import BaseModelLoader
from app.logging.logger import get_logger
from app.schemas.analysis import AnalysisRequest, AnalysisResult
from app.schemas.common import APIResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analyze", tags=["Analysis"])
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared OpenAPI response documentation
# ---------------------------------------------------------------------------

_ANALYZE_RESPONSES = {
    200: {
        "description": (
            "**Analysis successful.** Returns the full classification result "
            "including threat level, confidence score, explanation, and "
            "per-signal indicator list."
        ),
    },
    400: {
        "description": (
            "**Bad Request.** The message content passes schema validation "
            "but fails business-rule validation (e.g., purely numeric input)."
        ),
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": (
                        "Message must be between 3 and 2000 non-whitespace "
                        "characters and must not be purely numeric."
                    ),
                    "data": None,
                    "error": {
                        "error_code": "validation_error",
                        "message": "Message validation failed.",
                    },
                }
            }
        },
    },
    422: {
        "description": (
            "**Unprocessable Entity.** Pydantic schema validation failed. "
            "The ``error.details`` field lists each failing field with its "
            "constraint and the value that was rejected."
        ),
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": (
                        "Validation failed on 'body → message': "
                        "String should have at least 3 characters"
                    ),
                    "data": None,
                    "error": {
                        "error_code": "validation_error",
                        "message": "...",
                        "details": [
                            {
                                "loc": ["body", "message"],
                                "msg": "String should have at least 3 characters",
                                "type": "string_too_short",
                            }
                        ],
                    },
                }
            }
        },
    },
    503: {
        "description": (
            "**Service Unavailable.** The AI model or mock engine is not "
            "yet loaded. Clients should retry after a brief delay."
        ),
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "AI model is not currently available.",
                    "data": None,
                    "error": {
                        "error_code": "model_not_ready",
                        "message": "Model 'mock-heuristic-v1' is not loaded.",
                    },
                }
            }
        },
    },
}

# ---------------------------------------------------------------------------
# Dependency providers
# ---------------------------------------------------------------------------


def _get_model_loader(
    settings: Settings = Depends(get_settings),
) -> BaseModelLoader:
    """Resolve the active model loader from application state."""
    from app.main import get_model_loader  # noqa: PLC0415

    return get_model_loader(settings)


def _get_analysis_service(
    model_loader: BaseModelLoader = Depends(_get_model_loader),
) -> AnalysisService:
    """Construct a stateless ``AnalysisService`` for this request."""
    return AnalysisService(model_loader=model_loader)


# ---------------------------------------------------------------------------
# POST /api/v1/analyze
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=APIResponse[AnalysisResult],
    status_code=status.HTTP_200_OK,
    summary="Analyse SMS Message",
    description="""
Classifies an SMS message body as **safe**, **suspicious**, or **dangerous**
using the active analysis engine.

### Phase 2.2 Behaviour
This phase uses a **heuristic mock engine** (`MockModelLoader`) instead of a
trained NLP model. The engine analyses message text using rule-based signals:

| Signal | Weight | Description |
|--------|--------|-------------|
| Credential request | Critical | Password, OTP, PIN keywords |
| URL / link detected | High | HTTP URLs, shortened links |
| Urgency language | High | "urgent", "suspended", "act now" |
| Financial keywords | Medium | Bank names, payment terms |
| Prize language | Medium | "won", "lottery", "claim your" |
| Excessive CAPS | Low | >40% uppercase character ratio |

The response always includes:
- A **`threat_level`** bucket: `safe` | `suspicious` | `dangerous`
- A **`confidence`** score calibrated to `[0.60, 0.97]`
- A **human-readable `explanation`** listing detected signals
- A **`indicators`** list enumerating all signals checked
- `mock_mode: true` to signal the Flutter client to display a disclaimer

### Important
All results in Phase 2.2 are **mock** — `mock_mode` will be `true`.
Do not use these results for real security decisions.
Real NLP inference will be activated in **Phase 2.3**.
""",
    responses=_ANALYZE_RESPONSES,
    openapi_extra={
        "x-codeSamples": [
            {
                "lang": "Dart (Flutter / Dio)",
                "source": (
                    "final response = await dio.post(\n"
                    "  '/api/v1/analyze',\n"
                    "  data: {\n"
                    "    'message': smsBody,\n"
                    "    'sender': sender,\n"
                    "  },\n"
                    ");\n"
                    "final result = AnalysisResult.fromJson(response.data['data']);"
                ),
            },
            {
                "lang": "cURL",
                "source": (
                    "curl -X POST http://localhost:8000/api/v1/analyze \\\n"
                    '  -H "Content-Type: application/json" \\\n'
                    '  -d \'{"message": "URGENT: Your account is suspended. '
                    "Click http://fake.example.com\"}'"
                ),
            },
        ]
    },
)
async def analyse_message(
    http_request: Request,
    body: AnalysisRequest,
    service: AnalysisService = Depends(_get_analysis_service),
) -> APIResponse[AnalysisResult]:
    """Classify an SMS message and return a structured threat verdict.

    The endpoint is intentionally thin — it extracts the ``request_id``
    from middleware state and delegates all classification logic to
    ``AnalysisService``.

    Args:
        http_request: Starlette request (used to extract ``request_id``).
        body:         Validated and parsed ``AnalysisRequest``.
        service:      Injected ``AnalysisService`` instance.

    Returns:
        ``APIResponse[AnalysisResult]`` envelope containing the
        classification result, indicators, and timing information.

    Raises:
        ValidationException:    If message fails business-rule validation.
        ModelNotReadyException: If the mock engine is not initialised.
    """
    # Extract request_id injected by RequestLoggerMiddleware
    request_id: str | None = getattr(http_request.state, "request_id", None)

    result: AnalysisResult = service.analyse(
        message=body.message,
        sender=body.sender,
        request_id=request_id,
    )

    logger.info(
        "POST /analyze → %s (conf=%.2f mock=%s id=%s)",
        result.threat_level,
        result.confidence,
        result.mock_mode,
        request_id or "-",
    )

    return APIResponse[AnalysisResult].ok(
        data=result,
        message="Analysis complete",
    )


# ---------------------------------------------------------------------------
# GET /api/v1/analyze/status
# ---------------------------------------------------------------------------


@router.get(
    "/status",
    response_model=APIResponse[dict],  # type: ignore[type-arg]
    summary="API v1 Status",
    description=(
        "Returns metadata about the API v1 operational status, "
        "active model/mock version, and available endpoints."
    ),
)
async def api_status(
    settings: Settings = Depends(get_settings),
    model_loader: BaseModelLoader = Depends(_get_model_loader),
) -> APIResponse[dict]:  # type: ignore[type-arg]
    """Return metadata about API v1 availability.

    Args:
        settings:     Injected application settings.
        model_loader: Injected model loader for health data.

    Returns:
        ``APIResponse`` with version, model, and endpoint information.
    """
    model_health = model_loader.health()
    return APIResponse[dict].ok(  # type: ignore[type-arg]
        data={
            "api_version": "v1",
            "app_version": settings.app_version,
            "environment": settings.app_env,
            "model_version": model_health.model_version,
            "model_loaded": model_health.is_loaded,
            "mock_mode": "mock" in model_health.model_version,
            "endpoints": [
                {
                    "method": "POST",
                    "path": "/api/v1/analyze",
                    "description": "Classify an SMS message",
                    "phase": "2.2 — mock heuristic engine",
                },
                {
                    "method": "GET",
                    "path": "/api/v1/analyze/status",
                    "description": "API v1 operational status",
                    "phase": "2.1+",
                },
            ],
        },
        message="API v1 is operational",
    )
