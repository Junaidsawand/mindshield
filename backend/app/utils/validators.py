"""
MindShield Backend — Input Validation & Feature Extraction Utilities.

Pure functions for validating, sanitising, and extracting features from
SMS-related inputs. These utilities supplement Pydantic schema-level
validation with business-rule validation and provide the feature flags
consumed by the MockModelLoader heuristic engine (Phase 2.2).

Phase 2.2 additions:
    - ``contains_financial_keywords()`` — detects banking/payment terms.
    - ``contains_credential_request()`` — detects password/OTP requests.
    - ``contains_prize_language()``     — detects lottery/reward language.
    - Extended ``compute_message_features()`` returns all 9 feature flags.

All functions are stateless and have no side effects, making them
independently testable without any mocking or dependency injection.

Design Principle:
    Each function has a single responsibility and returns a typed
    result (bool or the cleaned value). Exception-based validation
    is reserved for truly unexpected states.
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

# Suspicious URL patterns (heuristic)
_URL_PATTERN = re.compile(
    r"https?://\S+|www\.\S+|bit\.ly/\S+|tinyurl\.com/\S+|t\.co/\S+",
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
        "respond now",
        "action required",
        "expires today",
        "last chance",
        "click immediately",
    }
)

# Financial institution / transaction keywords
_FINANCIAL_KEYWORDS = frozenset(
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
        "invoice",
        "billing",
        "statement",
    }
)

# Credential / personal data request keywords
_CREDENTIAL_KEYWORDS = frozenset(
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
        "one-time",
        "one time",
        "secret",
    }
)

# Prize / lottery language
_PRIZE_KEYWORDS = frozenset(
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
        "you have been chosen",
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
      - Not be purely numeric (e.g., bare OTPs excluded).

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
    return len(sender) <= _MAX_SENDER_CHARS


def sanitise_message(text: str) -> str:
    """Normalise message text for safe processing.

    Steps:
      1. NFKC Unicode normalisation (converts ligatures, full-width
         characters to their ASCII equivalents).
      2. Strip leading/trailing whitespace.
      3. Collapse internal whitespace runs to single spaces.

    Does NOT remove content — only normalises representation.
    Keeps raw/processed separation for audit trails.

    Args:
        text: Raw SMS body text.

    Returns:
        Normalised text suitable for model input.
    """
    normalised = unicodedata.normalize("NFKC", text)
    stripped = normalised.strip()
    return re.sub(r"\s+", " ", stripped)


# ---------------------------------------------------------------------------
# Feature Detection Functions
# ---------------------------------------------------------------------------


def contains_url(text: str) -> bool:
    """Return True if the message contains a URL-like pattern.

    Args:
        text: Sanitised message text.

    Returns:
        True if a URL pattern is detected.
    """
    return bool(_URL_PATTERN.search(text))


def contains_urgency_language(text: str) -> bool:
    """Return True if the message contains urgency/imperative phrases.

    Case-insensitive check against the urgency keyword list.

    Args:
        text: Sanitised message text.

    Returns:
        True if urgency keywords are present.
    """
    lower = text.lower()
    return any(keyword in lower for keyword in _URGENCY_KEYWORDS)


def contains_financial_keywords(text: str) -> bool:
    """Return True if the message references financial institutions.

    Detects bank names, payment terms, and financial action words.

    Args:
        text: Sanitised message text.

    Returns:
        True if financial keywords are present.
    """
    lower = text.lower()
    return any(keyword in lower for keyword in _FINANCIAL_KEYWORDS)


def contains_credential_request(text: str) -> bool:
    """Return True if the message requests sensitive credentials.

    Detects password, OTP, PIN, and personal data requests.
    This is the highest-weight threat signal.

    Args:
        text: Sanitised message text.

    Returns:
        True if credential-request keywords are present.
    """
    lower = text.lower()
    return any(keyword in lower for keyword in _CREDENTIAL_KEYWORDS)


def contains_prize_language(text: str) -> bool:
    """Return True if the message uses prize or lottery language.

    Args:
        text: Sanitised message text.

    Returns:
        True if prize/reward language is present.
    """
    lower = text.lower()
    return any(keyword in lower for keyword in _PRIZE_KEYWORDS)


# ---------------------------------------------------------------------------
# Composite Feature Extraction
# ---------------------------------------------------------------------------


def compute_message_features(text: str) -> dict[str, bool | int]:
    """Compute the full feature map for a sanitised SMS message.

    Returns a dictionary of boolean and integer feature flags consumed
    by the ``MockModelLoader`` heuristic engine and logged by the
    ``AnalysisService`` for observability.

    Feature keys:
        has_url             — URL/shortened link detected.
        has_urgency         — Urgency/imperative language detected.
        has_financial       — Financial keywords detected.
        has_credentials     — Credential-request keywords detected.
        has_prize           — Prize/lottery language detected.
        has_uppercase_ratio — >40% of alphabetic chars are uppercase.
        char_count          — Total character count.
        word_count          — Total word count.
        has_digits          — At least one digit present.

    Args:
        text: Sanitised SMS body text.

    Returns:
        Dictionary with boolean and integer feature flags.
    """
    alpha_chars = [c for c in text if c.isalpha()]
    caps_ratio = (
        sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if alpha_chars
        else 0.0
    )

    return {
        "has_url": contains_url(text),
        "has_urgency": contains_urgency_language(text),
        "has_financial": contains_financial_keywords(text),
        "has_credentials": contains_credential_request(text),
        "has_prize": contains_prize_language(text),
        "has_uppercase_ratio": caps_ratio > 0.4,
        "char_count": len(text),
        "word_count": len(text.split()),
        "has_digits": any(c.isdigit() for c in text),
    }
