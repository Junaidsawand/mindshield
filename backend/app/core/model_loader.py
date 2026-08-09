"""
MindShield Backend — AI Model Loader Architecture (Phase 2.3).

Defines the core abstract contract, prediction DTOs, health state,
concrete implementations (PlaceholderModelLoader, HuggingFaceModelLoader),
and the ModelLoaderFactory composition root for model management.

Architecture Principles (SOLID):
    Single Responsibility (S):
        Model loaders handle weight loading, tokenization, and inference passes only.
        Inference metrics, fallback logic, and service orchestration belong in
        InferenceService.

    Open/Closed (O):
        New model backends (ONNX, PyTorch, TensorRT, HuggingFace Transformers) are
        added by subclassing BaseModelLoader without altering existing service or
        API layer code.

    Liskov Substitution (L):
        All loaders strictly conform to BaseModelLoader. Swapping
        HuggingFaceModelLoader for MockModelLoader retains identical interface
        invariants.

    Interface Segregation (I):
        BaseModelLoader exposes a minimal lifecycle contract: load(), unload(),
        predict(), predict_batch(), and health().

    Dependency Inversion (D):
        Higher-level components (InferenceService, AnalysisService) depend
        exclusively on the BaseModelLoader abstraction.

Phase 2.3 Extensibility & HuggingFace Compatibility:
    The HuggingFaceModelLoader class establishes the architecture for HuggingFace
    Transformer model loading (e.g. BERT/DistilBERT/RoBERTa fine-tuned for SMS).
    It encapsulates tokenization, tensor conversion, logit calculation, and softmax
    normalization pipelines.
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from app.core.exceptions import (
    ModelInferenceException,
    ModelLoadException,
    ModelNotReadyException,
)
from app.logging.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Data Transfer Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModelPrediction:
    """Immutable result produced by a model inference pass.

    Attributes:
        label:          Classification label (e.g. "safe", "phishing", "suspicious").
        threat_level:   Normalised severity ("safe" | "suspicious" | "dangerous").
        confidence:     Model confidence score in [0.0, 1.0].
        explanation:    Human-readable rationale for the classification verdict.
        model_version:  Version string of the model/engine that produced result.
        backend_type:   Backend implementation identifier ("mock", "huggingface").
        logits:         Optional raw model output logits (for calibration & debug).
        fallback_mode:  True if prediction was produced by a fallback mechanism.
        predicted_at:   UTC timestamp of the inference execution.
    """

    label: str
    threat_level: Literal["safe", "suspicious", "dangerous"]
    confidence: float
    explanation: str
    model_version: str = "mock-heuristic-v1"
    backend_type: str = "mock"
    logits: tuple[float, ...] | None = None
    fallback_mode: bool = False
    predicted_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def __post_init__(self) -> None:
        """Validate field invariants after dataclass initialisation."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")
        if self.threat_level not in {"safe", "suspicious", "dangerous"}:
            raise ValueError(
                f"threat_level must be safe|suspicious|dangerous, "
                f"got {self.threat_level!r}"
            )


@dataclass
class ModelHealth:
    """Health report produced by a model loader's health check.

    Attributes:
        is_loaded:      True if model weights are loaded in memory and ready.
        model_version:  Version identifier of the loaded model.
        backend_type:   Backend type name ("mock" | "huggingface" | "placeholder").
        status_message: Human-readable status description.
        load_time_ms:   Time taken to load weights/architecture in milliseconds.
    """

    is_loaded: bool
    model_version: str
    backend_type: str
    status_message: str
    load_time_ms: float | None = None


# ---------------------------------------------------------------------------
# Abstract Interface
# ---------------------------------------------------------------------------


class BaseModelLoader(abc.ABC):
    """Abstract base class for all AI model loader implementations.

    Subclasses must implement:
      - ``load()``          — Load model weights into memory & warm up.
      - ``unload()``        — Release memory and model resources.
      - ``predict()``       — Run inference on a single text string.
      - ``predict_batch()`` — Run batch inference on a list of strings.
      - ``health()``        — Return operational status report.

    Properties:
      - ``backend_type``    — String identifier for the loader backend.
      - ``is_loaded``       — Boolean indicating whether model is ready.
    """

    @property
    @abc.abstractmethod
    def backend_type(self) -> str:
        """Return the backend engine name."""
        ...

    @property
    @abc.abstractmethod
    def is_loaded(self) -> bool:
        """Return True if model is loaded and ready for inference."""
        ...

    @abc.abstractmethod
    def load(self) -> None:
        """Load model architecture, weights, and tokenizer into memory.

        Idempotent — calling load() on an already-loaded loader must be a no-op.

        Raises:
            ModelLoadException: If loading weights, model path, or warm-up fails.
        """
        ...

    @abc.abstractmethod
    def unload(self) -> None:
        """Unload model resources and free allocated memory."""
        ...

    @abc.abstractmethod
    def predict(self, text: str) -> ModelPrediction:
        """Classify a single SMS message text string.

        Args:
            text: Sanitised SMS body text.

        Returns:
            ModelPrediction immutable object.

        Raises:
            ModelNotReadyException: If load() has not completed successfully.
            ModelInferenceException: If inference execution fails.
        """
        ...

    def predict_batch(self, texts: list[str]) -> list[ModelPrediction]:
        """Classify a batch of SMS message text strings.

        Default implementation loops over predict(). Subclasses can override
        with vectorised batch tensor operations for maximum throughput.

        Args:
            texts: List of sanitised SMS body strings.

        Returns:
            List of ModelPrediction objects corresponding to input order.
        """
        return [self.predict(t) for t in texts]

    @abc.abstractmethod
    def health(self) -> ModelHealth:
        """Return operational health status.

        Returns:
            ModelHealth dataclass.
        """
        ...


# ---------------------------------------------------------------------------
# Placeholder Implementation (Phase 2.1 Baseline)
# ---------------------------------------------------------------------------


class PlaceholderModelLoader(BaseModelLoader):
    """Stub implementation maintained for baseline reference testing."""

    _VERSION = "placeholder-v0"

    def __init__(self) -> None:
        self._is_loaded: bool = False

    @property
    def backend_type(self) -> str:
        """Return backend type identifier."""
        return "placeholder"

    @property
    def is_loaded(self) -> bool:
        """Return loading readiness status."""
        return self._is_loaded

    def load(self) -> None:
        """Load baseline placeholder loader."""
        self._is_loaded = True

    def unload(self) -> None:
        """Unload baseline placeholder loader."""
        self._is_loaded = False

    def predict(self, text: str) -> ModelPrediction:
        """Return baseline placeholder prediction."""
        if not self._is_loaded:
            raise ModelNotReadyException("Placeholder model is not loaded.")
        _ = text
        return ModelPrediction(
            label="safe",
            threat_level="safe",
            confidence=0.5,
            explanation="Placeholder prediction baseline.",
            model_version=self._VERSION,
            backend_type=self.backend_type,
        )

    def health(self) -> ModelHealth:
        """Return health status report."""
        return ModelHealth(
            is_loaded=self._is_loaded,
            model_version=self._VERSION,
            backend_type=self.backend_type,
            status_message="Placeholder model baseline.",
        )


# ---------------------------------------------------------------------------
# HuggingFace Transformer Model Loader Architecture (Phase 2.3 & 3.4)
# ---------------------------------------------------------------------------


class HuggingFaceModelLoader(BaseModelLoader):
    """HuggingFace / PyTorch DistilBERT Model Loader implementation.

    Loads fine-tuned Transformer models (e.g., DistilBERT fine-tuned on SMS dataset)
    from local disk artifacts or the HuggingFace Model Hub for real-time inference.

    Attributes:
        model_path: Local path or HF Hub ID.
        model_version: Model version identifier string.
        backend_name: Active backend identifier string ("distilbert" or "huggingface").
    """

    _DEFAULT_VERSION = "distilbert-uncased-v1"

    def __init__(
        self,
        model_path: str = "data/models/distilbert",
        model_version: str | None = None,
        backend_name: str = "distilbert",
    ) -> None:
        self._model_path = model_path.strip() or "data/models/distilbert"
        self._model_version = model_version or self._DEFAULT_VERSION
        self._backend_name = (
            backend_name.strip().lower() if backend_name else "distilbert"
        )
        from app.nlp.config import NLPPreprocessingConfig
        from app.nlp.pipeline import NLPPreprocessingPipeline

        self._preprocessor = NLPPreprocessingPipeline(
            NLPPreprocessingConfig.create_transformer_config()
        )
        self._is_loaded: bool = False
        self._load_time_ms: float | None = None
        self._tokenizer: Any | None = None
        self._model: Any | None = None
        self._device: str = "cpu"
        self._id2label: dict[int, str] = {0: "ham", 1: "spam"}

    @property
    def backend_type(self) -> str:
        """Return backend type identifier."""
        return self._backend_name

    @property
    def is_loaded(self) -> bool:
        """Return loading readiness status."""
        return self._is_loaded

    def _resolve_model_path(self) -> str:
        """Resolve model path to string on disk or HF hub ID."""
        from pathlib import Path

        p = Path(self._model_path)
        if p.exists():
            return str(p.resolve())

        # Try relative to backend directory
        backend_dir = Path(__file__).resolve().parents[2]
        rel_p = backend_dir / self._model_path
        if rel_p.exists():
            return str(rel_p.resolve())

        return self._model_path

    def load(self) -> None:
        """Load HuggingFace architecture, tokenizer, and fine-tuned weights.

        Raises:
            ModelLoadException: If model path does not exist or weight loading fails.
        """
        if self._is_loaded:
            return

        start = time.perf_counter()
        logger.info(
            "Initialising HuggingFace model loader | "
            "path='%s' version='%s' backend='%s'",
            self._model_path,
            self._model_version,
            self._backend_name,
        )

        resolved_path = self._resolve_model_path()

        try:
            import os
            import json
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            if not os.path.exists(resolved_path) and not resolved_path.count("/") == 1:
                raise ModelLoadException(
                    f"Specified model path '{resolved_path}' does not exist."
                )

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(
                "Loading tokenizer and model from '%s' on device '%s'...",
                resolved_path,
                self._device,
            )

            self._tokenizer = AutoTokenizer.from_pretrained(resolved_path)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                resolved_path
            )
            self._model.to(self._device)
            self._model.eval()

            # Load label mapping if label_mapping.json exists
            map_file = os.path.join(resolved_path, "label_mapping.json")
            if os.path.exists(map_file):
                with open(map_file, "r", encoding="utf-8") as f:
                    map_data = json.load(f)
                    if "id2label" in map_data:
                        self._id2label = {
                            int(k): str(v) for k, v in map_data["id2label"].items()
                        }
            elif (
                hasattr(self._model.config, "id2label")
                and self._model.config.id2label
            ):
                self._id2label = {
                    int(k): str(v) for k, v in self._model.config.id2label.items()
                }

            # Perform warmup pass
            warmup_inputs = self._tokenizer(
                "MindShield initialisation warmup pass",
                return_tensors="pt",
                truncation=True,
                max_length=64,
            )
            warmup_inputs = {
                k: v.to(self._device) for k, v in warmup_inputs.items()
            }
            with torch.no_grad():
                _ = self._model(**warmup_inputs)

            self._is_loaded = True
            self._load_time_ms = round((time.perf_counter() - start) * 1_000, 2)

            logger.info(
                "DistilBERT Transformer model loaded successfully | "
                "load_time=%.2fms device=%s",
                self._load_time_ms,
                self._device,
            )
        except Exception as exc:
            self._is_loaded = False
            raise ModelLoadException(
                f"Failed to load DistilBERT model weights from '{resolved_path}': {exc}"
            ) from exc

    def unload(self) -> None:
        """Release HuggingFace model resources."""
        self._model = None
        self._tokenizer = None
        self._is_loaded = False
        self._load_time_ms = None
        logger.info("HuggingFace model loader unloaded.")

    def predict(self, text: str) -> ModelPrediction:
        """Classify input string using fine-tuned DistilBERT transformer."""
        if not self._is_loaded or self._model is None or self._tokenizer is None:
            raise ModelNotReadyException("HuggingFace model loader is not loaded.")

        if not text or not text.strip():
            raise ModelInferenceException("Cannot infer prediction on empty text.")

        try:
            import torch

            clean_text = self._preprocessor.preprocess_text(text)[
                "final_processed_text"
            ]
            inputs = self._tokenizer(
                clean_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128,
            )
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model(**inputs)

            logits_tensor = outputs.logits[0]
            probs_tensor = torch.softmax(logits_tensor, dim=-1)

            p_ham = float(probs_tensor[0].item())
            p_spam = (
                float(probs_tensor[1].item())
                if probs_tensor.shape[0] > 1
                else 1.0 - p_ham
            )
            pred_class = int(torch.argmax(probs_tensor).item())

            raw_logits = tuple(float(x.item()) for x in logits_tensor)

            if pred_class == 1:
                label = "phishing"
                threat_level = "dangerous" if p_spam >= 0.50 else "suspicious"
                confidence = round(p_spam, 4)
                explanation = (
                    f"Fine-tuned DistilBERT model detected spam/phishing pattern "
                    f"({p_spam:.1%} confidence)."
                )
            else:
                label = "safe"
                threat_level = "safe"
                confidence = round(p_ham, 4)
                explanation = (
                    f"Fine-tuned DistilBERT model classified message as benign "
                    f"({p_ham:.1%} confidence)."
                )

            return ModelPrediction(
                label=label,
                threat_level=threat_level,  # type: ignore[arg-type]
                confidence=confidence,
                explanation=explanation,
                model_version=self._model_version,
                backend_type=self.backend_type,
                logits=raw_logits,
                fallback_mode=False,
            )
        except Exception as exc:
            if isinstance(exc, (ModelNotReadyException, ModelInferenceException)):
                raise
            raise ModelInferenceException(
                f"DistilBERT inference pass failed: {exc}"
            ) from exc

    def predict_batch(self, texts: list[str]) -> list[ModelPrediction]:
        """Vectorised batch inference for HuggingFace Transformer architecture."""
        if not self._is_loaded:
            raise ModelNotReadyException("HuggingFace model loader is not loaded.")

        return [self.predict(t) for t in texts]

    def health(self) -> ModelHealth:
        """Return HuggingFace model operational health report."""
        status_msg = (
            f"HuggingFace transformer model '{self._model_version}' ready."
            if self._is_loaded
            else "HuggingFace loader uninitialised."
        )
        return ModelHealth(
            is_loaded=self._is_loaded,
            model_version=self._model_version,
            backend_type=self.backend_type,
            status_message=status_msg,
            load_time_ms=self._load_time_ms,
        )


# ---------------------------------------------------------------------------
# Model Loader Factory
# ---------------------------------------------------------------------------


class ModelLoaderFactory:
    """Factory for instantiating model loader instances based on configuration.

    Encapsulates loader creation so application startup code and tests
    can select backends declaratively.
    """

    @staticmethod
    def create_loader(
        backend: str = "mock",
        model_path: str = "",
        model_version: str | None = None,
    ) -> BaseModelLoader:
        """Instantiate a concrete BaseModelLoader implementation.

        Args:
            backend: Engine type ("mock", "huggingface", "distilbert", "placeholder").
            model_path: Path or hub identifier for weights.
            model_version: Optional version string override.

        Returns:
            Configured BaseModelLoader concrete instance.

        Raises:
            ModelLoadException: If backend type is unrecognized.
        """
        backend_clean = backend.strip().lower()

        if backend_clean == "mock":
            from app.core.mock_model_loader import MockModelLoader  # noqa: PLC0415
            return MockModelLoader()

        if backend_clean in {"huggingface", "distilbert"}:
            return HuggingFaceModelLoader(
                model_path=model_path,
                model_version=model_version,
                backend_name=backend_clean,
            )

        if backend_clean == "placeholder":
            return PlaceholderModelLoader()

        raise ModelLoadException(
            f"Unknown model backend '{backend}'. Supported backends: "
            "'mock', 'huggingface', 'distilbert', 'placeholder'."
        )
