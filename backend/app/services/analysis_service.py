"""
MindShield Backend — Analysis Service (Phase 2.2).

Orchestrates the SMS classification pipeline:
    1. Input validation (length, content rules).
    2. Text sanitisation (Unicode normalisation, whitespace collapse).
    3. Feature extraction (logged for observability).
    4. Model inference (delegates to injected BaseModelLoader).
    5. Indicator construction (from feature flags → ThreatIndicator list).
    6. Result mapping (ModelPrediction → AnalysisResult schema).

Phase 2.2 additions:
    - ``_build_indicators()`` — constructs a ``ThreatIndicator`` list
      from the features extracted by the validators module, providing
      per-signal transparency in the response.
    - ``processing_time_ms`` — measures and records the end-to-end
      classification duration in milliseconds.
    - ``request_id`` — propagated from the HTTP request state to the
      response for client-side log correlation.

Design Principles (SOLID):
    S — Single Responsibility: service handles orchestration only.
    O — Open/Closed: new pipeline steps added here; routers unchanged.
    D — Dependency Inversion: depends on BaseModelLoader abstraction.
"""

from __future__ import annotations

import time

from app.core.exceptions import ModelNotReadyException, ValidationException
from app.core.model_loader import BaseModelLoader, ModelPrediction
from app.logging.logger import get_logger
from app.schemas.analysis import AnalysisResult, ThreatIndicator
from app.utils.validators import (
    compute_message_features,
    is_valid_message,
    sanitise_message,
)

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Indicator Definitions
# ---------------------------------------------------------------------------

# Maps feature flag → (indicator name, weight, detail template)
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
    """Construct a ``ThreatIndicator`` list from extracted features.

    Each indicator is always included in the response — whether
    ``present=True`` or ``present=False`` — so the Flutter UI can
    display the full evidence panel including absent signals.

    Args:
        features: Feature dict from ``compute_message_features()``.

    Returns:
        Ordered list of ``ThreatIndicator`` objects.
    """
    indicators: list[ThreatIndicator] = []

    for name, weight, detail, feature_key in _INDICATOR_MAP:
        # has_credentials / has_url / etc are bool; has_uppercase_ratio is bool
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
        _model_loader: Injected ``BaseModelLoader`` implementation.
    """

    def __init__(self, model_loader: BaseModelLoader) -> None:
        """Initialise the service with a model loader.

        Args:
            model_loader: Any ``BaseModelLoader`` concrete implementation.
                          Phase 2.2 uses ``MockModelLoader``.
        """
        self._model_loader = model_loader

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
            4. Check model health; raise if not loaded.
            5. Delegate to model loader for prediction.
            6. Build ``ThreatIndicator`` list from features.
            7. Measure and record processing duration.
            8. Map ``ModelPrediction`` + indicators → ``AnalysisResult``.

        Args:
            message:    Raw SMS body text from the HTTP request.
            sender:     Optional sender identifier (logged, not classified).
            request_id: Optional UUID for end-to-end tracing.

        Returns:
            ``AnalysisResult`` schema ready for JSON serialisation.

        Raises:
            ValidationException:    If the message fails content validation.
            ModelNotReadyException: If the model loader is not initialised.
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

        # Step 4 — Model health check
        model_health = self._model_loader.health()
        if not model_health.is_loaded:
            raise ModelNotReadyException(
                f"Model '{model_health.model_version}' is not loaded."
            )

        # Step 5 — Model inference
        prediction: ModelPrediction = self._model_loader.predict(clean_text)

        # Step 6 — Build indicators
        indicators = _build_indicators(features)

        # Step 7 — Measure duration
        processing_ms = round((time.perf_counter() - pipeline_start) * 1_000, 2)

        logger.info(
            "Analysis complete | label=%s threat=%s conf=%.2f " "mock=%s ms=%.2f id=%s",
            prediction.label,
            prediction.threat_level,
            prediction.confidence,
            prediction.model_version.startswith("mock"),
            processing_ms,
            request_id or "-",
        )

        # Step 8 — Map to response schema
        mock_mode = prediction.model_version.startswith(
            "mock"
        ) or prediction.model_version.startswith("placeholder")

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
