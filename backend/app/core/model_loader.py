"""
MindShield Backend — Model Loader Interface (Phase 2.1 Placeholder).

Defines the abstract contract that any AI model integration must fulfil.
Phase 2.1 provides a ``PlaceholderModelLoader`` that satisfies the
interface without performing any real inference, allowing the full
HTTP stack to be exercised end-to-end without a trained model.

Design Principles:
    Interface Segregation (SOLID-I):
        The ``BaseModelLoader`` defines the minimal interface: load,
        predict, and health-check. Future implementations (BERT,
        TF-IDF+SVM, GPT wrapper) implement this interface without
        changing any router or service code.

    Dependency Inversion (SOLID-D):
        Services depend on ``BaseModelLoader`` (abstraction), not on
        any concrete implementation. Swapping the model in Phase 2.2
        requires only changing the concrete class injected at startup.

    Open/Closed Principle (SOLID-O):
        New model backends can be added by creating a new subclass
        without modifying ``analysis_service.py`` or any router.

Usage (Phase 2.2+):
    class BertModelLoader(BaseModelLoader):
        def load(self) -> None:
            self._model = AutoModelForSequenceClassification.from_pretrained(...)

        def predict(self, text: str) -> ModelPrediction:
            ...
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Data Transfer Objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModelPrediction:
    """Immutable result produced by a model inference pass.

    Attributes:
        label:       Classification label (e.g. "safe", "phishing").
        threat_level: Normalised severity ("safe" | "suspicious" | "dangerous").
        confidence:  Model confidence in the prediction, range [0.0, 1.0].
        explanation: Human-readable rationale for the classification.
        model_version: Version string of the model that produced this result.
        predicted_at: UTC timestamp of the prediction.
    """

    label: str
    threat_level: str
    confidence: float
    explanation: str
    model_version: str = "placeholder-v0"
    predicted_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def __post_init__(self) -> None:
        """Validate field values after dataclass initialisation."""
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
        is_loaded:     True if the model is in memory and ready.
        model_version: Version identifier of the loaded model.
        status_message: Human-readable status description.
    """

    is_loaded: bool
    model_version: str
    status_message: str


# ---------------------------------------------------------------------------
# Abstract Interface
# ---------------------------------------------------------------------------


class BaseModelLoader(abc.ABC):
    """Abstract base class for all AI model integrations.

    Concrete subclasses must implement:
      - ``load()``    — Initialise and warm up the model.
      - ``predict()`` — Run inference on a single text input.
      - ``health()``  — Return the current operational status.

    Lifecycle:
        The FastAPI ``lifespan`` context manager calls ``load()`` once
        at startup. ``predict()`` is called per-request by the service
        layer. ``health()`` is called by the health endpoint.
    """

    @abc.abstractmethod
    def load(self) -> None:
        """Load the model into memory.

        Should be called once at application startup. Implementations
        must be idempotent — calling ``load()`` on an already-loaded
        model must not raise an error.

        Raises:
            ConfigurationException: If the model path is invalid or
                the model artefact is corrupt.
        """
        ...

    @abc.abstractmethod
    def predict(self, text: str) -> ModelPrediction:
        """Classify the given SMS message text.

        Args:
            text: Raw SMS body text (already cleaned/normalised).

        Returns:
            A ``ModelPrediction`` with label, confidence, and explanation.

        Raises:
            ModelNotReadyException:   If ``load()`` has not been called.
            ModelInferenceException:  If inference fails at runtime.
            ValidationException:      If ``text`` is empty or exceeds limits.
        """
        ...

    @abc.abstractmethod
    def health(self) -> ModelHealth:
        """Return the current health state of the model loader.

        Returns:
            ``ModelHealth`` dataclass with is_loaded flag and status.
        """
        ...


# ---------------------------------------------------------------------------
# Phase 2.1 Placeholder Implementation
# ---------------------------------------------------------------------------


class PlaceholderModelLoader(BaseModelLoader):
    """Stub implementation used in Phase 2.1.

    Satisfies the ``BaseModelLoader`` contract without performing any
    real ML inference. Returns a deterministic mock prediction so that
    the full API stack (routing → service → model → response) can be
    tested end-to-end before a real model is integrated.

    Replacement Plan (Phase 2.2):
        Replace this class with ``BertModelLoader`` or equivalent.
        No changes to routers, services, or schemas are required —
        only the concrete class injected in ``main.py`` lifespan.
    """

    _PLACEHOLDER_VERSION = "placeholder-v0"
    _PLACEHOLDER_EXPLANATION = (
        "Phase 2.1 placeholder — no real model is loaded. "
        "This response is synthetic and must not be used for security decisions."
    )

    def __init__(self) -> None:
        self._loaded: bool = False

    def load(self) -> None:
        """Simulate model loading (no-op in placeholder)."""
        self._loaded = True

    def predict(self, text: str) -> ModelPrediction:
        """Return a fixed placeholder prediction.

        The placeholder always returns ``threat_level="safe"`` with
        confidence 0.5, clearly signalling that no real analysis was
        performed.

        Args:
            text: SMS body text (unused in placeholder).

        Returns:
            A ``ModelPrediction`` with synthetic safe classification.
        """
        # Text is intentionally not analysed — this is a placeholder.
        _ = text  # Acknowledge the parameter to satisfy linters

        return ModelPrediction(
            label="safe",
            threat_level="safe",
            confidence=0.5,
            explanation=self._PLACEHOLDER_EXPLANATION,
            model_version=self._PLACEHOLDER_VERSION,
        )

    def health(self) -> ModelHealth:
        """Return the health status of the placeholder loader."""
        return ModelHealth(
            is_loaded=self._loaded,
            model_version=self._PLACEHOLDER_VERSION,
            status_message=(
                "Placeholder model active — Phase 2.1. "
                "Real model will be integrated in Phase 2.2."
            ),
        )
