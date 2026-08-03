"""
MindShield Backend — Analysis Service.

The service layer sits between the HTTP routers and the model loader.
It is responsible for:
  1. Coordinating input sanitisation (via validators).
  2. Delegating inference to the injected ``BaseModelLoader``.
  3. Mapping the ``ModelPrediction`` DTO to the ``AnalysisResult`` schema.
  4. Logging the outcome for observability.

Design Principles:
    Single Responsibility (SOLID-S):
        This service handles only analysis orchestration.
        It does not concern itself with HTTP details (status codes,
        request parsing) — those are the router's responsibility.

    Dependency Inversion (SOLID-D):
        The service depends on ``BaseModelLoader`` (abstract), not on
        any concrete implementation. This is injected via FastAPI's
        dependency injection system.

    Open/Closed (SOLID-O):
        Adding new pre/post-processing steps (e.g., language detection,
        PII masking) requires only adding new validator calls here —
        the router and model loader are not touched.
"""

from __future__ import annotations

from app.core.exceptions import ModelNotReadyException, ValidationException
from app.core.model_loader import BaseModelLoader, ModelPrediction
from app.logging.logger import get_logger
from app.schemas.analysis import AnalysisResult
from app.utils.validators import (
    compute_message_features,
    is_valid_message,
    sanitise_message,
)

logger = get_logger(__name__)


class AnalysisService:
    """Orchestrates SMS classification requests.

    This class coordinates validation, sanitisation, inference,
    and result mapping. It is instantiated once and shared across
    requests via FastAPI's dependency injection.

    Attributes:
        _model_loader: The injected model loader implementation.
    """

    def __init__(self, model_loader: BaseModelLoader) -> None:
        """Initialise the service with a model loader.

        Args:
            model_loader: Any concrete ``BaseModelLoader`` implementation.
                          In Phase 2.1 this will be ``PlaceholderModelLoader``.
        """
        self._model_loader = model_loader

    def analyse(self, message: str, sender: str | None = None) -> AnalysisResult:
        """Classify an SMS message and return a structured result.

        Processing pipeline:
            1. Validate raw input length and content.
            2. Sanitise text (Unicode normalisation, whitespace collapse).
            3. Extract heuristic features (logged for observability).
            4. Delegate to model loader for prediction.
            5. Map ``ModelPrediction`` → ``AnalysisResult``.

        Args:
            message: Raw SMS body text from the request.
            sender:  Optional sender identifier (logged, not classified).

        Returns:
            ``AnalysisResult`` schema ready for JSON serialisation.

        Raises:
            ValidationException:    If the message fails content validation.
            ModelNotReadyException: If the model loader is not loaded.
        """
        logger.info(
            "Analysis request received",
            extra={
                "sender": sender or "unknown",
                "message_length": len(message),
            },
        )

        # Step 1 — Input validation
        if not is_valid_message(message):
            raise ValidationException(
                f"Message must be between 3 and 2000 non-whitespace characters "
                f"and must not be purely numeric. Received {len(message)} chars."
            )

        # Step 2 — Sanitisation
        clean_text = sanitise_message(message)

        # Step 3 — Feature extraction (informational in Phase 2.1)
        features = compute_message_features(clean_text)
        logger.debug("Message features extracted", extra={"features": features})

        # Step 4 — Model inference
        model_health = self._model_loader.health()
        if not model_health.is_loaded:
            raise ModelNotReadyException(
                f"Model '{model_health.model_version}' is not loaded. "
                "The server may still be warming up."
            )

        prediction: ModelPrediction = self._model_loader.predict(clean_text)

        logger.info(
            "Analysis complete",
            extra={
                "label": prediction.label,
                "threat_level": prediction.threat_level,
                "confidence": prediction.confidence,
                "model_version": prediction.model_version,
            },
        )

        # Step 5 — Map to response schema
        return AnalysisResult(
            label=prediction.label,
            threat_level=prediction.threat_level,  # type: ignore[arg-type]
            confidence=prediction.confidence,
            explanation=prediction.explanation,
            model_version=prediction.model_version,
            is_placeholder=prediction.model_version.startswith("placeholder"),
            predicted_at=prediction.predicted_at,
        )
