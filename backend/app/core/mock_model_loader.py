"""
MindShield Backend — Mock Model Loader (Phase 2.2).

Provides a ``MockModelLoader`` that replaces the fixed Phase 2.1
placeholder with a realistic, heuristic-driven mock engine.

The mock engine analyses message text using rule-based heuristics
(URL patterns, urgency language, financial keywords, sender patterns)
to produce varied, contextually appropriate responses across the full
threat spectrum (safe / suspicious / dangerous).

Design Goals:
    1. Enable end-to-end integration testing with realistic varied data.
    2. Allow Flutter UI development to exercise all threat-level states.
    3. Document the signal categories that the real NLP model will use.
    4. Preserve the ``BaseModelLoader`` interface contract for zero-change
       swap-in of the real model in Phase 2.3.

Heuristics Used (not ML — purely rule-based):
    - URL / shortened link presence
    - Urgency/imperative language
    - Financial / banking keywords
    - Personal data requests (password, OTP, PIN)
    - Prize / lottery language
    - ALL-CAPS ratio
    - Exclamation mark density
    - Sender pattern (numeric, alphanumeric, international)

Confidence Calibration:
    Scores are generated from weighted feature sums, then mapped to
    the [0.60, 0.99] range so the mock results feel realistic without
    reaching the 1.0 floor (which the real model will also avoid).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.model_loader import BaseModelLoader, ModelHealth, ModelPrediction

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

_MOCK_VERSION = "mock-heuristic-v1"

# ---------------------------------------------------------------------------
# Keyword / Pattern Banks
# ---------------------------------------------------------------------------

_URL_RE = re.compile(
    r"https?://\S+|www\.\S+|bit\.ly/\S+|tinyurl\.com/\S+|t\.co/\S+",
    re.IGNORECASE,
)

_URGENCY_TERMS = frozenset(
    {
        "urgent",
        "immediately",
        "act now",
        "verify now",
        "suspended",
        "expires",
        "limited time",
        "click here",
        "confirm now",
        "account locked",
        "click immediately",
        "respond now",
        "action required",
        "expires today",
        "last chance",
    }
)

_FINANCIAL_TERMS = frozenset(
    {
        "bank",
        "account",
        "debit",
        "credit",
        "card",
        "payment",
        "transaction",
        "refund",
        "transfer",
        "balance",
        "atm",
        "paypal",
        "western union",
        "wire transfer",
        "lloyds",
        "barclays",
        "natwest",
        "hsbc",
        "amazon pay",
    }
)

_CREDENTIAL_TERMS = frozenset(
    {
        "password",
        "otp",
        "pin",
        "passcode",
        "verification code",
        "social security",
        "national insurance",
        "date of birth",
        "security question",
        "username",
        "login",
        "credentials",
    }
)

_PRIZE_TERMS = frozenset(
    {
        "won",
        "winner",
        "prize",
        "congratulations",
        "lottery",
        "lucky draw",
        "selected",
        "claim your",
        "free gift",
        "cash reward",
        "jackpot",
    }
)

_SAFE_TERMS = frozenset(
    {
        "hi",
        "hello",
        "see you",
        "thanks",
        "thank you",
        "okay",
        "sounds good",
        "meeting",
        "tomorrow",
        "lunch",
        "dinner",
        "how are you",
        "good morning",
        "good night",
        "birthday",
    }
)


# ---------------------------------------------------------------------------
# Feature Score Dataclass
# ---------------------------------------------------------------------------


@dataclass
class _FeatureScore:
    """Internal scoring record for mock classification."""

    has_url: bool = False
    has_urgency: bool = False
    has_financial: bool = False
    has_credentials: bool = False
    has_prize: bool = False
    has_safe_language: bool = False
    caps_ratio: float = 0.0
    exclamation_count: int = 0
    word_count: int = 0

    @property
    def danger_score(self) -> float:
        """Compute a raw danger score from weighted features."""
        score = 0.0
        if self.has_url:
            score += 0.35
        if self.has_urgency:
            score += 0.30
        if self.has_credentials:
            score += 0.40
        if self.has_financial:
            score += 0.20
        if self.has_prize:
            score += 0.25
        if self.caps_ratio > 0.4:
            score += 0.10
        if self.exclamation_count >= 2:
            score += 0.05
        if self.has_safe_language:
            score -= 0.50
        return max(0.0, min(score, 1.5))  # cap before normalisation


# ---------------------------------------------------------------------------
# Classification Logic
# ---------------------------------------------------------------------------


def _extract_features(text: str) -> _FeatureScore:
    """Extract heuristic features from sanitised SMS text."""
    lower = text.lower()
    alpha_chars = [c for c in text if c.isalpha()]
    caps_ratio = (
        sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if alpha_chars
        else 0.0
    )

    return _FeatureScore(
        has_url=bool(_URL_RE.search(text)),
        has_urgency=any(term in lower for term in _URGENCY_TERMS),
        has_financial=any(term in lower for term in _FINANCIAL_TERMS),
        has_credentials=any(term in lower for term in _CREDENTIAL_TERMS),
        has_prize=any(term in lower for term in _PRIZE_TERMS),
        has_safe_language=any(term in lower for term in _SAFE_TERMS),
        caps_ratio=caps_ratio,
        exclamation_count=text.count("!"),
        word_count=len(text.split()),
    )


def _build_explanation(features: _FeatureScore, threat_level: str) -> str:
    """Construct a human-readable explanation from active features."""
    signals: list[str] = []

    if features.has_url:
        signals.append("contains a URL or shortened link")
    if features.has_urgency:
        signals.append("uses urgency/imperative language")
    if features.has_credentials:
        signals.append("requests sensitive credentials or personal data")
    if features.has_financial:
        signals.append("references financial institutions or transactions")
    if features.has_prize:
        signals.append("uses prize or lottery language")
    if features.caps_ratio > 0.4:
        signals.append("contains excessive capitalisation")
    if features.exclamation_count >= 2:
        signals.append("uses multiple exclamation marks")
    if features.has_safe_language and threat_level == "safe":
        signals.append("uses casual, friendly language")

    if not signals:
        if threat_level == "safe":
            signals.append("no suspicious indicators detected")
        else:
            signals.append("general anomaly pattern detected")

    signal_str = "; ".join(signals)

    prefix = {
        "dangerous": (
            "⚠️ HIGH THREAT — This message exhibits multiple phishing indicators: "
        ),
        "suspicious": ("⚡ CAUTION — This message shows potential smishing signals: "),
        "safe": ("✅ LOW RISK — This message appears benign: "),
    }

    return (
        prefix.get(threat_level, "")
        + signal_str
        + ". [Mock heuristic — not a real AI prediction]"
    )


def _classify(features: _FeatureScore) -> tuple[str, str, float]:
    """Return (label, threat_level, confidence) from feature scores."""
    raw = features.danger_score

    if raw >= 0.55:
        # Dangerous — map raw to [0.82, 0.97]
        confidence = 0.82 + (min(raw, 1.5) - 0.55) / (1.5 - 0.55) * 0.15
        return "phishing", "dangerous", round(min(confidence, 0.97), 4)

    if raw >= 0.25:
        # Suspicious — map raw to [0.65, 0.81]
        confidence = 0.65 + (raw - 0.25) / (0.55 - 0.25) * 0.16
        return "suspicious", "suspicious", round(confidence, 4)

    # Safe — map raw to [0.60, 0.89] inverted (lower danger = higher safe confidence)
    confidence = 0.89 - raw * (0.89 - 0.60) / 0.25
    return "safe", "safe", round(max(confidence, 0.60), 4)


# ---------------------------------------------------------------------------
# MockModelLoader
# ---------------------------------------------------------------------------


class MockModelLoader(BaseModelLoader):
    """Realistic mock loader using heuristic classification (Phase 2.2).

    Produces varied, contextually appropriate responses across the full
    threat spectrum. Replaces the fixed Phase 2.1 placeholder.

    The mock engine is deterministic given the same input text, making
    test assertions against specific known inputs reliable and repeatable.

    Key improvements over ``PlaceholderModelLoader``:
        - Returns dangerous/suspicious/safe based on message content.
        - Provides meaningful explanations listing detected signals.
        - Returns calibrated confidence scores (not always 0.5).
        - Includes detected feature flags in the prediction metadata.
        - Labels are domain-appropriate (phishing, spam, safe, suspicious).
    """

    _VERSION = _MOCK_VERSION

    def __init__(self) -> None:
        """Initialise the mock loader."""
        self._loaded: bool = False

    def load(self) -> None:
        """Simulate model loading."""
        self._loaded = True

    def predict(self, text: str) -> ModelPrediction:
        """Classify SMS text using heuristic rules.

        The classification is deterministic: the same text always
        produces the same prediction. This enables reliable testing.

        Args:
            text: Sanitised SMS body text.

        Returns:
            ``ModelPrediction`` with heuristic-based classification.
        """
        features = _extract_features(text)
        label, threat_level, confidence = _classify(features)
        explanation = _build_explanation(features, threat_level)

        return ModelPrediction(
            label=label,
            threat_level=threat_level,
            confidence=confidence,
            explanation=explanation,
            model_version=self._VERSION,
            predicted_at=datetime.now(tz=timezone.utc),
        )

    def health(self) -> ModelHealth:
        """Return the health status of the mock loader."""
        return ModelHealth(
            is_loaded=self._loaded,
            model_version=self._VERSION,
            status_message=(
                "Mock heuristic model active — Phase 2.2. "
                "Real NLP model will replace this in Phase 2.3."
            ),
        )
