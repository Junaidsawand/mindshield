"""
MindShield Backend — Model Loader & Factory Unit Tests (Phase 2.3).

Tests the ``ModelLoaderFactory``, ``HuggingFaceModelLoader`` stub,
``PlaceholderModelLoader``, and model loader contracts.
"""

from __future__ import annotations

import pytest

from app.core.exceptions import (
    ModelInferenceException,
    ModelLoadException,
    ModelNotReadyException,
)
from app.core.mock_model_loader import MockModelLoader
from app.core.model_loader import (
    HuggingFaceModelLoader,
    ModelLoaderFactory,
    PlaceholderModelLoader,
)


class TestModelLoaderFactory:
    """Tests ModelLoaderFactory instantiation for all supported backends."""

    def test_creates_mock_loader(self) -> None:
        loader = ModelLoaderFactory.create_loader("mock")
        assert isinstance(loader, MockModelLoader)
        assert loader.backend_type == "mock"

    def test_creates_huggingface_loader(self) -> None:
        loader = ModelLoaderFactory.create_loader(
            "huggingface",
            model_path="cardiffnlp/twitter-roberta-base-sentiment-latest",
        )
        assert isinstance(loader, HuggingFaceModelLoader)
        assert loader.backend_type == "huggingface"

    def test_creates_placeholder_loader(self) -> None:
        loader = ModelLoaderFactory.create_loader("placeholder")
        assert isinstance(loader, PlaceholderModelLoader)
        assert loader.backend_type == "placeholder"

    def test_unknown_backend_raises_exception(self) -> None:
        with pytest.raises(ModelLoadException):
            ModelLoaderFactory.create_loader("invalid_backend_type")


class TestHuggingFaceModelLoader:
    """Tests HuggingFaceModelLoader lifecycle and predictions."""

    def test_load_and_predict_dangerous(self) -> None:
        loader = HuggingFaceModelLoader()
        loader.load()
        assert loader.is_loaded is True

        msg = "URGENT: Enter your password and OTP immediately at http://fake.com"
        pred = loader.predict(msg)
        assert pred.threat_level == "dangerous"
        assert pred.backend_type == "huggingface"
        assert pred.logits is not None

    def test_predict_suspicious(self) -> None:
        loader = HuggingFaceModelLoader()
        loader.load()

        pred = loader.predict("Click here http://example.com")
        assert pred.threat_level == "suspicious"

    def test_predict_safe(self) -> None:
        loader = HuggingFaceModelLoader()
        loader.load()

        pred = loader.predict("Hi, are we meeting at 3pm today?")
        assert pred.threat_level == "safe"

    def test_predict_batch(self) -> None:
        loader = HuggingFaceModelLoader()
        loader.load()

        results = loader.predict_batch([
            "Hi mom!",
            "URGENT: Click http://phish.com and enter your password",
        ])
        assert len(results) == 2
        assert results[0].threat_level == "safe"
        assert results[1].threat_level == "dangerous"

    def test_predict_unloaded_raises_exception(self) -> None:
        loader = HuggingFaceModelLoader()
        with pytest.raises(ModelNotReadyException):
            loader.predict("Test message")

    def test_predict_empty_text_raises_exception(self) -> None:
        loader = HuggingFaceModelLoader()
        loader.load()
        with pytest.raises(ModelInferenceException):
            loader.predict("")

    def test_invalid_local_path_raises_model_load_exception(self) -> None:
        loader = HuggingFaceModelLoader(model_path="C:/non_existent_path_xyz_123")
        with pytest.raises(ModelLoadException):
            loader.load()

    def test_unload(self) -> None:
        loader = HuggingFaceModelLoader()
        loader.load()
        assert loader.is_loaded is True

        loader.unload()
        assert loader.is_loaded is False


class TestPlaceholderModelLoader:
    """Tests PlaceholderModelLoader baseline behavior."""

    def test_placeholder_lifecycle(self) -> None:
        loader = PlaceholderModelLoader()
        assert loader.is_loaded is False
        assert loader.backend_type == "placeholder"

        loader.load()
        assert loader.is_loaded is True

        pred = loader.predict("Any text string")
        assert pred.threat_level == "safe"
        assert pred.confidence == 0.5

        loader.unload()
        assert loader.is_loaded is False
