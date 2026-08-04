# ==============================================================================
# MindShield Backend — Real DistilBERT Model Loader Test Suite
# Phase 3.4 Integration: Real HuggingFace Transformer Inference Verification
# ==============================================================================

from pathlib import Path

import pytest
from app.core.model_loader import (
    HuggingFaceModelLoader,
    ModelLoaderFactory,
    ModelPrediction,
)
from app.services.analysis_service import AnalysisService
from app.services.inference_service import InferenceService


@pytest.fixture(scope="module")
def distilbert_loader():
    """Module-level fixture to load fine-tuned DistilBERT weights once."""
    backend_dir = Path(__file__).resolve().parents[1]
    model_dir = backend_dir / "data" / "models" / "distilbert"

    if not model_dir.exists():
        pytest.skip(f"DistilBERT model directory not found at {model_dir}")

    loader = HuggingFaceModelLoader(
        model_path=str(model_dir),
        model_version="distilbert-uncased-v1",
        backend_name="distilbert",
    )
    loader.load()
    yield loader
    loader.unload()


def test_distilbert_loader_initialisation(distilbert_loader):
    """Verify HuggingFaceModelLoader loads weights and reports ready state."""
    assert distilbert_loader.is_loaded is True
    assert distilbert_loader.backend_type == "distilbert"

    health = distilbert_loader.health()
    assert health.is_loaded is True
    assert health.backend_type == "distilbert"
    assert health.model_version == "distilbert-uncased-v1"
    assert health.load_time_ms is not None and health.load_time_ms > 0


def test_distilbert_loader_real_predictions(distilbert_loader):
    """Verify real inference predictions on benign vs threat text payloads."""
    # 1. Benign Ham SMS
    ham_pred = distilbert_loader.predict("Hey mom, I am heading home now for dinner.")
    assert isinstance(ham_pred, ModelPrediction)
    assert ham_pred.label == "safe"
    assert ham_pred.threat_level == "safe"
    assert ham_pred.confidence > 0.5
    assert ham_pred.backend_type == "distilbert"
    assert ham_pred.fallback_mode is False
    assert ham_pred.logits is not None

    # 2. Threat Spam SMS
    spam_pred = distilbert_loader.predict(
        "URGENT! Account suspended. Claim prize at http://spam.link"
    )
    assert isinstance(spam_pred, ModelPrediction)
    assert spam_pred.backend_type == "distilbert"
    assert spam_pred.fallback_mode is False
    assert spam_pred.logits is not None


def test_distilbert_loader_batch_predictions(distilbert_loader):
    """Verify vectorised batch prediction capability."""
    messages = [
        "See you at the office tomorrow morning.",
        "Win £1000 cash prize instantly by calling 0800123456!",
    ]

    preds = distilbert_loader.predict_batch(messages)
    assert len(preds) == 2
    assert preds[0].backend_type == "distilbert"
    assert preds[1].backend_type == "distilbert"


def test_model_loader_factory_distilbert():
    """Verify ModelLoaderFactory instantiates DistilBERT loader correctly."""
    loader = ModelLoaderFactory.create_loader(
        backend="distilbert",
        model_path="data/models/distilbert",
        model_version="distilbert-uncased-v1",
    )

    assert loader.backend_type == "distilbert"
    assert isinstance(loader, HuggingFaceModelLoader)


def test_analysis_service_integration_with_real_distilbert(distilbert_loader):
    """Verify AnalysisService end-to-end classification with real DistilBERT."""
    inference_service = InferenceService(loader=distilbert_loader)
    analysis_service = AnalysisService(inference_service)

    res = analysis_service.analyse(
        message="Hey friend, let's play tennis at 5 PM today.",
        sender="Friend",
        request_id="test-req-1234",
    )

    assert res.label == "safe"
    assert res.threat_level == "safe"
    assert res.mock_mode is False
    assert res.model_version == "distilbert-uncased-v1"
    assert res.request_id == "test-req-1234"
    assert res.processing_time_ms > 0
