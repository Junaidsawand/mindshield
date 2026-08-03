"""
MindShield Backend — Input Validation Utilities.

Pure functions for validating and sanitising SMS-related inputs.
These utilities supplement Pydantic's schema-level validation with
business-rule validation that requires imperative logic.

All functions are stateless and have no side effects, making them
independently testable without any mocking or dependency injection.

Design Principle:
    Each function has a single responsibility and returns a typed
    result (bool or the cleaned value), avoiding side-effect-driven
    patterns like raising exceptions for expected validation failures.
    Exception-based validation is reserved for truly unexpected states.
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MIN_MESSAGE_CHARS = 3
_MAX_MESSAGE_CHARS = 2_000
_MAX_SENDER_CHARS = 50

# E.164 phone number pattern (international format)
_E164_PATTERN = re.compile(r"^\+[1-9]\d{6,14}$")

# Suspicious URL indicators (heuristic — no ML in this phase)
_URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+|bit\.ly/\S+|tinyurl\.com/\S+",
    re.IGNORECASE,
)

# Urgency language keywords
_URGENCY_KEYWORDS = frozenset(
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
        "won",
        "prize",
        "free",
        "congratulations",
    }
)


# ---------------------------------------------------------------------------
# Validation Functions
# ---------------------------------------------------------------------------


def is_valid_message(text: str) -> bool:
    """Return True if the message meets length and content requirements.

    A valid message must:
      - Have at least ``_MIN_MESSAGE_CHARS`` non-whitespace characters.
      - Not exceed ``_MAX_MESSAGE_CHARS`` characters.
      - Not be purely numeric (e.g., OTPs need contextual analysis only).

    Args:
        text: Raw SMS body text.

    Returns:
        True if the message is valid for analysis.
    """
    stripped = text.strip()
    return bool(
        _MIN_MESSAGE_CHARS <= len(stripped) <= _MAX_MESSAGE_CHARS
        and not stripped.isdigit()
    )


def is_valid_sender(sender: str | None) -> bool:
    """Return True if the sender identifier is valid.

    Accepts:
      - None / empty string (sender is optional)
      - E.164 international phone numbers (e.g. +44791112345)
      - Short alphanumeric sender IDs (e.g. "MyBank", up to 50 chars)

    Args:
        sender: Sender phone number or display name, or None.

    Returns:
        True if sender is acceptable.
    """
    if sender is None or sender.strip() == "":
        return True
    if len(sender) > _MAX_SENDER_CHARS:
        return False
    return True


def sanitise_message(text: str) -> str:
    """Normalise message text for safe processing.

    Steps:
      1. NFKC Unicode normalisation (converts ligatures, full-width
         chars to their ASCII equivalents).
      2. Strip leading/trailing whitespace.
      3. Collapse internal sequences of whitespace to single spaces.

    This does NOT remove content — only normalises representation.
    Sanitisation is separate from classification to maintain
    an audit trail between raw and processed input.

    Args:
        text: Raw SMS body text.

    Returns:
        Normalised text suitable for model input.
    """
    normalised = unicodedata.normalize("NFKC", text)
    stripped = normalised.strip()
    # Collapse runs of whitespace (spaces, tabs, newlines) to single space
    collapsed = re.sub(r"\s+", " ", stripped)
    return collapsed


def contains_url(text: str) -> bool:
    """Return True if the message contains a URL-like pattern.

    Used as a feature flag in the analysis response (Phase 2.2+).
    Currently informational only — no ML inference in Phase 2.1.

    Args:
        text: Sanitised message text.

    Returns:
        True if a URL pattern is detected.
    """
    return bool(_URL_PATTERN.search(text))


def contains_urgency_language(text: str) -> bool:
    """Return True if the message contains common urgency phrases.

    Checks against a curated keyword list. Case-insensitive.
    Used as a feature flag in Phase 2.2+ model input engineering.

    Args:
        text: Sanitised message text (lower-cased internally).

    Returns:
        True if urgency keywords are present.
    """
    lower = text.lower()
    return any(keyword in lower for keyword in _URGENCY_KEYWORDS)


def compute_message_features(text: str) -> dict[str, bool | int]:
    """Compute a dictionary of heuristic features for a message.

    Returns a feature map that will be passed to the model in Phase 2.2.
    In Phase 2.1 these features are computed but not used for prediction.

    Args:
        text: Sanitised SMS body text.

    Returns:
        Dictionary with boolean and integer feature flags.
    """
    return {
        "has_url": contains_url(text),
        "has_urgency": contains_urgency_language(text),
        "char_count": len(text),
        "word_count": len(text.split()),
        "has_digits": any(c.isdigit() for c in text),
        "has_uppercase_ratio": (
            sum(1 for c in text if c.isupper()) / max(len(text), 1) > 0.3
        ),
    }
