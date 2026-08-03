"""
MindShield Backend — InferenceService Unit & Integration Tests (Phase 2.3).

Tests the ``InferenceService`` layer:
  - Single and batch prediction delegation.
  - Latency profiling & model metadata propagation.
  - Graceful fallback recovery when primary model is unready or raises error.
  - Exception propagation when fallback is disabled or unavailable.
  - Health report reporting and fallback aggregation.
"""

from __future__ import annotations

import pytest

from app.core.exceptions import ModelInferenceException, ModelNotReadyException
from app.core.mock_model_loader import MockModelLoader
from app.core.model_loader import BaseModelLoader, ModelHealth, ModelPrediction
from app.services.inference_service import InferenceService


class FailingModelLoader(BaseModelLoader):
    """Failing stub loader for testing error recovery paths."""

    def __init__(self, loaded: bool = True) -> None:
        self._loaded = loaded

    @property
    def backend_type(self) -> str:
        return "failing_stub"

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        self._loaded = True

    def unload(self) -> None:
        self._loaded = False

    def predict(self, text: str) -> ModelPrediction:
        if not self._loaded:
            raise ModelNotReadyException("Failing stub is unready.")
        raise ModelInferenceException("Simulated runtime inference crash.")

    def health(self) -> ModelHealth:
        return ModelHealth(
            is_loaded=self._loaded,
            model_version="failing-v1",
            backend_type=self.backend_type,
            status_message="Simulated error state.",
        )


class TestInferenceServiceHappyPath:
    """Tests normal inference execution with active primary loader."""

    def test_single_prediction(self) -> None:
        mock_loader = MockModelLoader()
        mock_loader.load()
        service = InferenceService(loader=mock_loader)

        pred = service.predict("URGENT: account suspended click http://fake.com")
        assert pred.threat_level == "dangerous"
        assert pred.backend_type == "mock"
        assert pred.fallback_mode is False

    def test_batch_prediction(self) -> None:
        mock_loader = MockModelLoader()
        mock_loader.load()
        service = InferenceService(loader=mock_loader)

        messages = [
            "Hi, see you tomorrow!",
            "URGENT: account locked click http://fake.com",
        ]
        results = service.predict_batch(messages)
        assert len(results) == 2
        assert results[0].threat_level == "safe"
        assert results[1].threat_level == "dangerous"

    def test_empty_batch_returns_empty_list(self) -> None:
        mock_loader = MockModelLoader()
        mock_loader.load()
        service = InferenceService(loader=mock_loader)

        assert service.predict_batch([]) == []

    def test_health_reporting(self) -> None:
        mock_loader = MockModelLoader()
        mock_loader.load()
        service = InferenceService(loader=mock_loader)

        health = service.health()
        assert health.is_loaded is True
        assert health.backend_type == "mock"


class TestInferenceServiceFallbackRecovery:
    """Tests graceful fallback recovery mechanisms."""

    def test_fallback_when_primary_unready(self) -> None:
        primary = FailingModelLoader(loaded=False)
        fallback = MockModelLoader()
        fallback.load()

        service = InferenceService(
            loader=primary,
            fallback_loader=fallback,
            fallback_enabled=True,
        )

        pred = service.predict("URGENT: bank account suspended click http://fake.com")
        assert pred.threat_level == "dangerous"
        assert pred.fallback_mode is True
        assert "Fallback mode active" in pred.explanation

    def test_fallback_when_primary_predict_raises_exception(self) -> None:
        primary = FailingModelLoader(loaded=True)
        fallback = MockModelLoader()
        fallback.load()

        service = InferenceService(
            loader=primary,
            fallback_loader=fallback,
            fallback_enabled=True,
        )

        pred = service.predict("Hello, how are you?")
        assert pred.threat_level == "safe"
        assert pred.fallback_mode is True
        assert "Simulated runtime inference crash" in pred.explanation

    def test_batch_fallback_when_primary_unready(self) -> None:
        primary = FailingModelLoader(loaded=False)
        fallback = MockModelLoader()
        fallback.load()

        service = InferenceService(
            loader=primary,
            fallback_loader=fallback,
            fallback_enabled=True,
        )

        results = service.predict_batch(["Hello world"])
        assert len(results) == 1
        assert results[0].fallback_mode is True

    def test_health_shows_fallback_status_when_primary_unready(self) -> None:
        primary = FailingModelLoader(loaded=False)
        fallback = MockModelLoader()
        fallback.load()

        service = InferenceService(
            loader=primary,
            fallback_loader=fallback,
            fallback_enabled=True,
        )

        health = service.health()
        assert health.is_loaded is True
        assert "failing_stub->mock" in health.backend_type


class TestInferenceServiceErrorsWithoutFallback:
    """Tests exception throwing when fallback is disabled or unready."""

    def test_raises_unready_when_no_fallback(self) -> None:
        primary = FailingModelLoader(loaded=False)
        service = InferenceService(loader=primary, fallback_enabled=False)

        with pytest.raises(ModelNotReadyException):
            service.predict("Test message")

    def test_raises_inference_error_when_no_fallback(self) -> None:
        primary = FailingModelLoader(loaded=True)
        service = InferenceService(loader=primary, fallback_enabled=False)

        with pytest.raises(ModelInferenceException):
            service.predict("Test message")
