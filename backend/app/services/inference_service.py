"""
MindShield Backend — AI Inference Service (Phase 2.3).

Orchestrates ML model inference operations, batch execution pipelines,
latency profiling, and graceful error recovery/fallback mechanisms.

Design Principles (SOLID):
    Single Responsibility (S):
        InferenceService focuses exclusively on model execution logistics,
        latency profiling, batching, and error recovery. Higher-level domain
        concerns (e.g., ThreatIndicator mapping) reside in AnalysisService.

    Dependency Inversion (D):
        InferenceService depends entirely on the BaseModelLoader abstract interface.
        It is agnostic to whether the primary loader is MockModelLoader,
        HuggingFaceModelLoader, or an ONNX model runtime.

    Graceful Failure Recovery:
        If the primary AI model loader fails (e.g. GPU OOM, unhandled runtime
        inference error, uninitialised model weights), InferenceService catches
        the exception and redirects execution to a fallback loader. The returned
        prediction carries ``fallback_mode=True`` for full system transparency.
"""

from __future__ import annotations

import time

from app.core.exceptions import ModelInferenceException, ModelNotReadyException
from app.core.model_loader import BaseModelLoader, ModelHealth, ModelPrediction
from app.logging.logger import get_logger

logger = get_logger(__name__)


class InferenceService:
    """Orchestrates AI model inference passes and fallback execution pipelines.

    Attributes:
        _loader: Primary ``BaseModelLoader`` concrete instance.
        _fallback_loader: Optional fallback ``BaseModelLoader`` instance.
        _fallback_enabled: Boolean flag indicating if fallback recovery is active.
    """

    def __init__(
        self,
        loader: BaseModelLoader,
        fallback_loader: BaseModelLoader | None = None,
        fallback_enabled: bool = True,
    ) -> None:
        """Initialise InferenceService with primary and optional fallback loaders.

        Args:
            loader: Primary model loader backend.
            fallback_loader: Secondary fallback model loader.
            fallback_enabled: True if fallback recovery should be attempted.
        """
        self._loader = loader
        self._fallback_loader = fallback_loader
        self._fallback_enabled = fallback_enabled

    @property
    def loader(self) -> BaseModelLoader:
        """Return the active primary model loader."""
        return self._loader

    @property
    def fallback_loader(self) -> BaseModelLoader | None:
        """Return the fallback model loader instance if configured."""
        return self._fallback_loader

    def _has_active_fallback(self) -> bool:
        """Return True if fallback is enabled and fallback loader is ready."""
        return bool(
            self._fallback_enabled
            and self._fallback_loader
            and self._fallback_loader.is_loaded
        )

    def predict(self, text: str) -> ModelPrediction:
        """Run single-text model inference with latency tracking & fallback.

        Args:
            text: Sanitised SMS message text string.

        Returns:
            ModelPrediction immutable DTO.

        Raises:
            ModelNotReadyException: If model is unready and no fallback succeeds.
            ModelInferenceException: If inference fails and no fallback succeeds.
        """
        start = time.perf_counter()

        # Step 1 — Primary loader status check
        if not self._loader.is_loaded:
            if self._has_active_fallback():
                fb_type = (
                    self._fallback_loader.backend_type
                    if self._fallback_loader
                    else "-"
                )
                logger.warning(
                    "Primary model loader '%s' unready. Activating fallback '%s'.",
                    self._loader.backend_type,
                    fb_type,
                )
                return self._execute_fallback(text, reason="primary_unready")
            raise ModelNotReadyException(
                f"Model loader '{self._loader.backend_type}' is not loaded."
            )

        # Step 2 — Execute primary inference pass
        try:
            prediction = self._loader.predict(text)
            elapsed_ms = (time.perf_counter() - start) * 1_000
            logger.debug(
                "Inference completed | backend=%s version=%s ms=%.2f",
                prediction.backend_type,
                prediction.model_version,
                elapsed_ms,
            )
            return prediction
        except Exception as exc:
            logger.error(
                "Primary model inference failed [%s]: %s",
                exc.__class__.__name__,
                str(exc),
                exc_info=True,
            )
            if self._has_active_fallback():
                logger.warning("Attempting graceful fallback recovery.")
                return self._execute_fallback(text, reason=str(exc))
            raise ModelInferenceException(f"Inference pass failed: {exc}") from exc

    def predict_batch(self, texts: list[str]) -> list[ModelPrediction]:
        """Run batch inference on multiple input strings.

        Args:
            texts: List of sanitised SMS body strings.

        Returns:
            Ordered list of ModelPrediction instances.
        """
        if not texts:
            return []

        if not self._loader.is_loaded:
            if self._has_active_fallback():
                logger.warning("Primary loader unready for batch. Using fallback.")
                return [
                    self._execute_fallback(t, reason="primary_unready")
                    for t in texts
                ]
            raise ModelNotReadyException(
                f"Model loader '{self._loader.backend_type}' is not loaded."
            )

        try:
            return self._loader.predict_batch(texts)
        except Exception as exc:
            logger.error("Batch inference failed: %s", exc, exc_info=True)
            if self._has_active_fallback():
                return [self._execute_fallback(t, reason=str(exc)) for t in texts]
            raise ModelInferenceException(f"Batch inference failed: {exc}") from exc

    def _execute_fallback(self, text: str, reason: str) -> ModelPrediction:
        """Execute fallback loader prediction and attach fallback metadata.

        Args:
            text: SMS text string.
            reason: Description of the trigger reason.

        Returns:
            ModelPrediction tagged with fallback_mode=True.
        """
        if not self._fallback_loader:
            raise ModelNotReadyException("No fallback loader configured.")

        fallback_pred = self._fallback_loader.predict(text)
        explanation = (
            f"{fallback_pred.explanation} [Fallback mode active: {reason}]"
        )

        return ModelPrediction(
            label=fallback_pred.label,
            threat_level=fallback_pred.threat_level,
            confidence=fallback_pred.confidence,
            explanation=explanation,
            model_version=fallback_pred.model_version,
            backend_type=fallback_pred.backend_type,
            logits=fallback_pred.logits,
            fallback_mode=True,
            predicted_at=fallback_pred.predicted_at,
        )

    def health(self) -> ModelHealth:
        """Return operational health status report for active pipeline."""
        primary_health = self._loader.health()
        if primary_health.is_loaded:
            return primary_health

        if self._fallback_loader and self._fallback_loader.is_loaded:
            fb_health = self._fallback_loader.health()
            return ModelHealth(
                is_loaded=True,
                model_version=fb_health.model_version,
                backend_type=f"{primary_health.backend_type}->{fb_health.backend_type}",
                status_message=(
                    f"Primary loader '{primary_health.backend_type}' unavailable. "
                    f"Fallback loader '{fb_health.backend_type}' active."
                ),
            )

        return primary_health
