"""
MindShield Backend — Analysis Service (Phase 2.3).

Orchestrates the SMS classification pipeline:
    1. Input validation (length, content rules).
    2. Text sanitisation (Unicode normalisation, whitespace collapse).
    3. Feature extraction (logged for observability).
    4. Model inference pass (delegated to InferenceService).
    5. Indicator construction (from feature flags → ThreatIndicator list).
    6. Result mapping (ModelPrediction → AnalysisResult schema).

Phase 2.3 Architecture Enhancements:
    - Delegates model inference execution, batch handling, latency profiling,
      and graceful fallback recovery to ``InferenceService``.
    - Decoupled from concrete loader implementations (Mock, HuggingFace, ONNX).
    - Supports receiving either an ``InferenceService`` or a ``BaseModelLoader``.

Design Principles (SOLID):
    S — Single Responsibility: AnalysisService handles domain orchestration
        & indicator mapping only.
    O — Open/Closed: Model loaders and inference pipelines change without
        altering this service.
    D — Dependency Inversion: Depends on InferenceService / BaseModelLoader
        abstractions.
"""

from __future__ import annotations

import time

from app.core.exceptions import ValidationException
from app.core.model_loader import BaseModelLoader, ModelPrediction
from app.logging.logger import get_logger
from app.schemas.analysis import AnalysisResult, ThreatIndicator
from app.services.inference_service import InferenceService
from app.utils.validators import (
    compute_message_features,
    is_valid_message,
    sanitise_message,
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Indicator Definitions
# ---------------------------------------------------------------------------

_INDICATOR_MAP: list[tuple[str, str, str, str]] = [
    (
        "credential_request",
        "critical",
        "Requests sensitive credentials (password, OTP, PIN)",
        "has_credentials",
    ),
    (
        "url_detected",
        "high",
        "Suspicious URL or shortened link detected in message body",
        "has_url",
    ),
    (
        "urgency_language",
        "high",
        "Urgency/imperative language detected (e.g. 'urgent', 'suspended')",
        "has_urgency",
    ),
    (
        "financial_keywords",
        "medium",
        "References financial institutions or transactions",
        "has_financial",
    ),
    (
        "prize_language",
        "medium",
        "Prize, lottery, or reward language detected",
        "has_prize",
    ),
    (
        "excessive_caps",
        "low",
        "Excessive capitalisation (>40% of alphabetic characters)",
        "has_uppercase_ratio",
    ),
]


def _build_indicators(
    features: dict[str, bool | int],
) -> list[ThreatIndicator]:
    """Construct a ``ThreatIndicator`` list from extracted features."""
    indicators: list[ThreatIndicator] = []

    for name, weight, detail, feature_key in _INDICATOR_MAP:
        present = bool(features.get(feature_key, False))
        indicators.append(
            ThreatIndicator(
                name=name,
                present=present,
                weight=weight,  # type: ignore[arg-type]
                detail=detail if present else None,
            )
        )

    return indicators


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class AnalysisService:
    """Orchestrates SMS classification requests.

    Coordinates validation, sanitisation, inference, indicator
    construction, and result mapping. Stateless — safe to share
    across concurrent requests.

    Attributes:
        _inference_service: Injected ``InferenceService`` instance.
    """

    def __init__(
        self,
        model_loader_or_inference_service: (
            BaseModelLoader | InferenceService | None
        ) = None,
        model_loader: BaseModelLoader | InferenceService | None = None,
    ) -> None:
        """Initialise the service with an InferenceService or BaseModelLoader.

        Args:
            model_loader_or_inference_service: An ``InferenceService``
                or ``BaseModelLoader``.
            model_loader: Alias for model_loader_or_inference_service.
        """
        target = model_loader_or_inference_service or model_loader
        if target is None:
            raise ValueError("Must provide model_loader or inference_service")

        if isinstance(target, InferenceService):
            self._inference_service = target
        else:
            # Wrap bare BaseModelLoader in InferenceService for backwards compatibility
            self._inference_service = InferenceService(loader=target)

    @property
    def inference_service(self) -> InferenceService:
        """Return the underlying InferenceService instance."""
        return self._inference_service

    def analyse(
        self,
        message: str,
        sender: str | None = None,
        request_id: str | None = None,
    ) -> AnalysisResult:
        """Classify an SMS message and return a structured result.

        Processing pipeline:
            1. Validate raw input (length, content rules).
            2. Sanitise text (NFKC normalisation, whitespace collapse).
            3. Extract heuristic features (for indicators + logging).
            4. Delegate ML inference pass to ``InferenceService``.
            5. Build ``ThreatIndicator`` list from features.
            6. Measure and record processing duration.
            7. Map ``ModelPrediction`` + indicators → ``AnalysisResult``.

        Args:
            message:    Raw SMS body text from the HTTP request.
            sender:     Optional sender identifier (logged, not classified).
            request_id: Optional UUID for end-to-end tracing.

        Returns:
            ``AnalysisResult`` schema ready for JSON serialisation.

        Raises:
            ValidationException:    If the message fails content validation.
            ModelNotReadyException: If the model loader is not initialised.
            ModelInferenceException: If inference fails during processing.
        """
        pipeline_start = time.perf_counter()

        logger.info(
            "Analysis request received | sender=%s len=%d id=%s",
            sender or "unknown",
            len(message),
            request_id or "-",
        )

        # Step 1 — Input validation
        if not is_valid_message(message):
            raise ValidationException(
                f"Message must be between 3 and 2000 non-whitespace characters "
                f"and must not be purely numeric. Received {len(message)} chars."
            )

        # Step 2 — Sanitisation
        clean_text = sanitise_message(message)

        # Step 3 — Feature extraction
        features = compute_message_features(clean_text)
        logger.debug("Features: %s", features)

        # Step 4 — Model inference pass via InferenceService
        prediction: ModelPrediction = self._inference_service.predict(clean_text)

        # Step 5 — Build indicators
        indicators = _build_indicators(features)

        # Step 6 — Measure duration
        processing_ms = round((time.perf_counter() - pipeline_start) * 1_000, 2)

        logger.info(
            "Analysis complete | label=%s threat=%s conf=%.2f backend=%s "
            "mock=%s fallback=%s ms=%.2f id=%s",
            prediction.label,
            prediction.threat_level,
            prediction.confidence,
            prediction.backend_type,
            prediction.model_version.startswith("mock"),
            prediction.fallback_mode,
            processing_ms,
            request_id or "-",
        )

        # Step 7 — Map to response schema
        mock_mode = (
            prediction.backend_type in {"mock", "placeholder"}
            or prediction.model_version.startswith("mock")
            or prediction.model_version.startswith("placeholder")
        )

        return AnalysisResult(
            label=prediction.label,
            threat_level=prediction.threat_level,  # type: ignore[arg-type]
            confidence=prediction.confidence,
            explanation=prediction.explanation,
            indicators=indicators,
            model_version=prediction.model_version,
            mock_mode=mock_mode,
            processing_time_ms=processing_ms,
            request_id=request_id,
            predicted_at=prediction.predicted_at,
        )
