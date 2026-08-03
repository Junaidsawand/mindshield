"""
MindShield Backend — Analysis Pydantic Schemas (Phase 2.2).

Defines the complete request and response models for the
``POST /api/v1/analyze`` endpoint.

Phase 2.2 additions over Phase 2.1:
    - ``AnalysisRequest``: gains optional ``metadata`` block for
      client context (app version, device locale, network type).
    - ``AnalysisResult``: gains ``indicators`` list, ``processing_time_ms``,
      ``request_id``, and ``mock_mode`` flag.
    - ``ThreatIndicator``: new schema for individual signal reporting.
    - Multiple rich ``json_schema_extra`` examples for Swagger UI.
    - Full field-level OpenAPI ``description`` and ``examples``.

API Contract (Phase 2.2):

    POST /api/v1/analyze
    Content-Type: application/json

    Request:
    {
        "message": "URGENT: Your bank account has been suspended...",
        "sender": "+447911123456",          // optional
        "metadata": {                        // optional
            "app_version": "1.0.0",
            "locale": "en-GB",
            "network": "mobile"
        }
    }

    Response 200:
    {
        "success": true,
        "message": "Analysis complete",
        "data": {
            "label": "phishing",
            "threat_level": "dangerous",
            "confidence": 0.87,
            "explanation": "⚠️ HIGH THREAT — ...",
            "indicators": [
                {"name": "credential_request", "present": false, "weight": "critical", "detail": null},  # noqa: E501
                {"name": "url_detected",       "present": true,  "weight": "high",
                 "detail": "Suspicious URL or shortened link detected in message body"},
                {"name": "urgency_language",   "present": true,  "weight": "high",
                 "detail": "Urgency/imperative language detected (e.g. 'urgent', 'suspended')"},  # noqa: E501
                {"name": "financial_keywords", "present": true,  "weight": "medium",
                 "detail": "References financial institutions or transactions"},
                {"name": "prize_language",     "present": false, "weight": "medium", "detail": null},  # noqa: E501
                {"name": "excessive_caps",     "present": false, "weight": "low",    "detail": null}  # noqa: E501
            ],
            "model_version": "mock-heuristic-v1",
            "mock_mode": true,
            "processing_time_ms": 3.2,
            "request_id": "abc-123-...",
            "predicted_at": "2026-08-03T21:00:00Z"
        },
        "error": null,
        "timestamp": "2026-08-03T21:00:00Z"
    }
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MIN_MESSAGE_LENGTH = 3
_MAX_MESSAGE_LENGTH = 2_000

# ---------------------------------------------------------------------------
# Sub-schemas
# ---------------------------------------------------------------------------


class RequestMetadata(BaseModel):
    """Optional client context submitted alongside the analysis request.

    Allows the server to log client environment details for future
    contextual analysis (e.g., locale-specific smishing patterns).
    None of these fields affect the classification outcome in Phase 2.2.

    Attributes:
        app_version: MindShield client application version.
        locale:      BCP-47 locale tag (e.g., ``en-GB``, ``ur-PK``).
        network:     Connectivity type (``wifi``, ``mobile``, ``unknown``).
    """

    app_version: str | None = Field(
        default=None,
        max_length=20,
        description="MindShield client app version (e.g. '1.0.0').",
        examples=["1.0.0"],
    )
    locale: str | None = Field(
        default=None,
        max_length=10,
        description="BCP-47 locale tag of the device (e.g. 'en-GB').",
        examples=["en-GB"],
    )
    network: Literal["wifi", "mobile", "unknown"] | None = Field(
        default=None,
        description="Network connectivity type at time of request.",
        examples=["mobile"],
    )


class ThreatIndicator(BaseModel):
    """A single detected signal contributing to the threat classification.

    Indicators are returned in the analysis result to provide
    transparency into the classification decision. The Flutter UI
    renders these as an expandable evidence list below the verdict.

    The service always returns all 6 indicators (both ``present=True``
    and ``present=False``), in this fixed order:

    1. credential_request (critical)
    2. url_detected       (high)
    3. urgency_language   (high)
    4. financial_keywords (medium)
    5. prize_language     (medium)
    6. excessive_caps     (low)

    Attributes:
        name:    Machine-readable signal identifier (snake_case).
        present: Whether this signal was detected in the message.
        weight:  Relative importance of this signal to the verdict.
        detail:  Human-readable annotation when ``present=True``, else null.
    """

    name: str = Field(
        description="Machine-readable indicator name (snake_case).",
        examples=["url_detected"],
    )
    present: bool = Field(
        description="True if this indicator was detected in the message.",
    )
    weight: Literal["critical", "high", "medium", "low"] = Field(
        description="Relative contribution weight of this indicator.",
    )
    detail: str | None = Field(
        default=None,
        description=(
            "Human-readable annotation when ``present=True``; "
            "``null`` when the signal is absent."
        ),
        examples=["Suspicious URL or shortened link detected in message body"],
    )


# ---------------------------------------------------------------------------
# Request Schema
# ---------------------------------------------------------------------------


class AnalysisRequest(BaseModel):
    """Request body for the POST /api/v1/analyze endpoint.

    Only ``message`` is required. All other fields are optional and
    are used for logging, future contextual analysis, or display.

    Attributes:
        message:  Raw SMS body text to classify. Required.
        sender:   Optional sender identifier (E.164 number or display name).
        metadata: Optional client context block (app version, locale, network).
    """

    message: Annotated[
        str,
        Field(
            min_length=_MIN_MESSAGE_LENGTH,
            max_length=_MAX_MESSAGE_LENGTH,
            description=(
                "The raw SMS body text to classify. "
                f"Must be between {_MIN_MESSAGE_LENGTH} and "
                f"{_MAX_MESSAGE_LENGTH} characters after stripping whitespace. "
                "Must not consist solely of digits."
            ),
            examples=[
                "URGENT: Your bank account has been suspended. Click here: "
                "http://fake-bank.example.com",
                "Hi! Are you coming to the meeting tomorrow?",
            ],
        ),
    ]
    sender: Annotated[
        str | None,
        Field(
            default=None,
            max_length=50,
            description=(
                "Optional sender identifier. Accepts E.164 phone numbers "
                "(e.g. '+447911123456') or alphanumeric sender IDs "
                "(e.g. 'MyBank'). Logged but not used for classification "
                "in Phase 2.2."
            ),
            examples=["+447911123456", "HSBC", "MyBank"],
        ),
    ] = None
    metadata: RequestMetadata | None = Field(
        default=None,
        description=(
            "Optional client context block. All fields are optional. "
            "Used for logging and future contextual analysis."
        ),
    )

    @field_validator("message", mode="before")
    @classmethod
    def strip_and_validate_message(cls, v: str) -> str:
        """Strip surrounding whitespace before length validation.

        After stripping, Pydantic's ``min_length`` constraint will
        correctly reject whitespace-only inputs.
        """
        if not isinstance(v, str):
            raise ValueError("message must be a string")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Dangerous — phishing SMS",
                    "description": (
                        "A realistic smishing message impersonating a bank, "
                        "containing a suspicious URL and urgency language. "
                        "Triggers url_detected + urgency_language + financial_keywords."
                    ),
                    "value": {
                        "message": (
                            "URGENT: Your Lloyds Bank account has been suspended. "
                            "Verify your identity immediately to avoid permanent "
                            "closure: http://lloydssecure-verify.example.com"
                        ),
                        "sender": "LLOYDS",
                        "metadata": {
                            "app_version": "1.0.0",
                            "locale": "en-GB",
                            "network": "mobile",
                        },
                    },
                },
                {
                    "summary": "Suspicious — prize/lottery scam",
                    "description": (
                        "A message using prize language only — no URL or urgency. "
                        "Scores a single medium-weight signal → suspicious."
                    ),
                    "value": {
                        "message": (
                            "You have won a prize! "
                            "Reply WIN to claim your reward."
                        ),
                        "sender": "+447700900123",
                    },
                },
                {
                    "summary": "Safe — normal conversation",
                    "description": (
                        "A benign, conversational message with no threat signals."
                    ),
                    "value": {
                        "message": "Hi! Are you coming to lunch tomorrow?",
                        "sender": "+447700900456",
                    },
                },
                {
                    "summary": "Dangerous — credential harvest",
                    "description": (
                        "A message requesting OTP and password — "
                        "highest-weight signal (credential_request=critical) "
                        "combined with URL detection."
                    ),
                    "value": {
                        "message": (
                            "Security alert: someone tried to access your account. "
                            "Enter your password and OTP here to verify: "
                            "http://secure-verify.example.com"
                        ),
                        "sender": "SecureAlert",
                    },
                },
            ]
        }
    }


# ---------------------------------------------------------------------------
# Response Schema
# ---------------------------------------------------------------------------

ThreatLevel = Literal["safe", "suspicious", "dangerous"]


class AnalysisResult(BaseModel):
    """Classification result returned by the analysis endpoint.

    All fields are populated for every response. The ``mock_mode`` flag
    indicates whether the result was produced by the heuristic mock
    engine (Phase 2.2) or a real NLP model (Phase 2.3+).

    The ``indicators`` list always contains exactly 6 entries in the
    order defined by ``_INDICATOR_MAP`` in ``analysis_service.py``:
    credential_request, url_detected, urgency_language, financial_keywords,
    prize_language, excessive_caps.

    Attributes:
        label:              Raw classifier label (e.g. ``phishing``, ``safe``).
        threat_level:       Normalised severity bucket (safe|suspicious|dangerous).
        confidence:         Model confidence in [0.0, 1.0].
        explanation:        Human-readable rationale for the verdict.
        indicators:         All 6 threat signals (present=True or False).
        model_version:      Version identifier of the active model/mock.
        mock_mode:          True when produced by the mock engine, not real AI.
        processing_time_ms: Server-side classification time in milliseconds.
        request_id:         UUID echoed from the request for tracing.
        predicted_at:       UTC datetime of inference.
    """

    label: str = Field(
        description=(
            "Raw classifier label. Possible values: "
            "``safe``, ``suspicious``, ``phishing``, ``spam``."
        ),
        examples=["phishing", "safe", "suspicious"],
    )
    threat_level: ThreatLevel = Field(
        description=(
            "Normalised threat severity bucket. One of: "
            "``safe`` | ``suspicious`` | ``dangerous``."
        ),
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Model confidence score in [0.0, 1.0]. "
            "Values ≥ 0.85 indicate high confidence."
        ),
        examples=[0.87, 0.65, 0.89],
    )
    explanation: str = Field(
        description=(
            "Human-readable explanation of the classification decision, "
            "listing the specific signals that contributed to the verdict."
        ),
    )
    indicators: list[ThreatIndicator] = Field(
        default_factory=list,
        description=(
            "All 6 threat signals checked for this message. "
            "Each indicator is always present with ``present=True`` or "
            "``present=False``. Rendered as an expandable evidence panel "
            "in the Flutter UI."
        ),
    )
    model_version: str = Field(
        description="Version identifier of the model or mock engine used.",
        examples=["mock-heuristic-v1", "bert-sms-v1"],
    )
    mock_mode: bool = Field(
        default=True,
        description=(
            "True when this result was produced by the Phase 2.2 mock "
            "engine rather than a trained NLP model. "
            "The Flutter UI displays a disclaimer when mock_mode is True."
        ),
    )
    processing_time_ms: float | None = Field(
        default=None,
        ge=0.0,
        description=(
            "Server-side classification duration in milliseconds. "
            "Populated by the service layer before returning the response."
        ),
        examples=[2.41, 15.7],
    )
    request_id: str | None = Field(
        default=None,
        description=(
            "UUID of the originating HTTP request, echoed for client-side "
            "correlation with server logs."
        ),
        examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    )
    predicted_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC datetime when the classification was performed.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                # ── Example 1: Dangerous — phishing SMS ─────────────────────
                # Live-verified from MockModelLoader against:
                # "URGENT: Your Lloyds Bank account has been suspended.
                #  Verify your identity immediately to avoid permanent
                #  closure: http://lloydssecure-verify.example.com"
                {
                    "summary": "Dangerous result — phishing SMS",
                    "value": {
                        "label": "phishing",
                        "threat_level": "dangerous",
                        "confidence": 0.87,
                        "explanation": (
                            "\u26a0\ufe0f HIGH THREAT \u2014 "
                            "contains a URL or shortened link; "
                            "uses urgency/imperative language; "
                            "references financial institutions or transactions. "
                            "[Mock heuristic \u2014 not a real AI prediction]"
                        ),
                        "indicators": [
                            {
                                "name": "credential_request",
                                "present": False,
                                "weight": "critical",
                                "detail": None,
                            },
                            {
                                "name": "url_detected",
                                "present": True,
                                "weight": "high",
                                "detail": (
                                    "Suspicious URL or shortened link "
                                    "detected in message body"
                                ),
                            },
                            {
                                "name": "urgency_language",
                                "present": True,
                                "weight": "high",
                                "detail": (
                                    "Urgency/imperative language detected "
                                    "(e.g. 'urgent', 'suspended')"
                                ),
                            },
                            {
                                "name": "financial_keywords",
                                "present": True,
                                "weight": "medium",
                                "detail": (
                                    "References financial institutions "
                                    "or transactions"
                                ),
                            },
                            {
                                "name": "prize_language",
                                "present": False,
                                "weight": "medium",
                                "detail": None,
                            },
                            {
                                "name": "excessive_caps",
                                "present": False,
                                "weight": "low",
                                "detail": None,
                            },
                        ],
                        "model_version": "mock-heuristic-v1",
                        "mock_mode": True,
                        "processing_time_ms": 2.41,
                        "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "predicted_at": "2026-08-03T21:00:00Z",
                    },
                },
                # ── Example 2: Suspicious — prize language only ──────────────
                # Live-verified: "You have won a prize! Reply WIN to claim."
                # threat_level=suspicious conf=0.65
                {
                    "summary": "Suspicious result — prize/lottery language",
                    "value": {
                        "label": "suspicious",
                        "threat_level": "suspicious",
                        "confidence": 0.65,
                        "explanation": (
                            "\U0001f7e1 MODERATE RISK \u2014 "
                            "uses prize, lottery, or reward language. "
                            "[Mock heuristic \u2014 not a real AI prediction]"
                        ),
                        "indicators": [
                            {
                                "name": "credential_request",
                                "present": False,
                                "weight": "critical",
                                "detail": None,
                            },
                            {
                                "name": "url_detected",
                                "present": False,
                                "weight": "high",
                                "detail": None,
                            },
                            {
                                "name": "urgency_language",
                                "present": False,
                                "weight": "high",
                                "detail": None,
                            },
                            {
                                "name": "financial_keywords",
                                "present": False,
                                "weight": "medium",
                                "detail": None,
                            },
                            {
                                "name": "prize_language",
                                "present": True,
                                "weight": "medium",
                                "detail": (
                                    "Prize, lottery, or reward language detected"
                                ),
                            },
                            {
                                "name": "excessive_caps",
                                "present": False,
                                "weight": "low",
                                "detail": None,
                            },
                        ],
                        "model_version": "mock-heuristic-v1",
                        "mock_mode": True,
                        "processing_time_ms": 1.92,
                        "request_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
                        "predicted_at": "2026-08-03T21:00:02Z",
                    },
                },
                # ── Example 3: Safe — normal conversation ────────────────────
                # Live-verified: "Hi! Are you coming to lunch tomorrow?"
                # threat_level=safe conf=0.89 all indicators present=False
                {
                    "summary": "Safe result — normal conversation",
                    "value": {
                        "label": "safe",
                        "threat_level": "safe",
                        "confidence": 0.89,
                        "explanation": (
                            "\u2705 LOW RISK \u2014 "
                            "uses casual, friendly language; "
                            "no suspicious indicators detected. "
                            "[Mock heuristic \u2014 not a real AI prediction]"
                        ),
                        "indicators": [
                            {
                                "name": "credential_request",
                                "present": False,
                                "weight": "critical",
                                "detail": None,
                            },
                            {
                                "name": "url_detected",
                                "present": False,
                                "weight": "high",
                                "detail": None,
                            },
                            {
                                "name": "urgency_language",
                                "present": False,
                                "weight": "high",
                                "detail": None,
                            },
                            {
                                "name": "financial_keywords",
                                "present": False,
                                "weight": "medium",
                                "detail": None,
                            },
                            {
                                "name": "prize_language",
                                "present": False,
                                "weight": "medium",
                                "detail": None,
                            },
                            {
                                "name": "excessive_caps",
                                "present": False,
                                "weight": "low",
                                "detail": None,
                            },
                        ],
                        "model_version": "mock-heuristic-v1",
                        "mock_mode": True,
                        "processing_time_ms": 1.83,
                        "request_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                        "predicted_at": "2026-08-03T21:00:01Z",
                    },
                },
                # ── Example 4: Dangerous — credential harvest ────────────────
                # Live-verified:
                # "Security alert: … Enter your password and OTP here to verify:
                #  http://secure-verify.example.com"
                # threat_level=dangerous conf=0.88
                {
                    "summary": "Dangerous result — credential harvest",
                    "value": {
                        "label": "phishing",
                        "threat_level": "dangerous",
                        "confidence": 0.88,
                        "explanation": (
                            "\u26a0\ufe0f HIGH THREAT \u2014 "
                            "requests sensitive credentials (password, OTP, PIN); "
                            "contains a URL or shortened link; "
                            "references financial institutions or transactions. "
                            "[Mock heuristic \u2014 not a real AI prediction]"
                        ),
                        "indicators": [
                            {
                                "name": "credential_request",
                                "present": True,
                                "weight": "critical",
                                "detail": (
                                    "Requests sensitive credentials "
                                    "(password, OTP, PIN)"
                                ),
                            },
                            {
                                "name": "url_detected",
                                "present": True,
                                "weight": "high",
                                "detail": (
                                    "Suspicious URL or shortened link "
                                    "detected in message body"
                                ),
                            },
                            {
                                "name": "urgency_language",
                                "present": False,
                                "weight": "high",
                                "detail": None,
                            },
                            {
                                "name": "financial_keywords",
                                "present": True,
                                "weight": "medium",
                                "detail": (
                                    "References financial institutions "
                                    "or transactions"
                                ),
                            },
                            {
                                "name": "prize_language",
                                "present": False,
                                "weight": "medium",
                                "detail": None,
                            },
                            {
                                "name": "excessive_caps",
                                "present": False,
                                "weight": "low",
                                "detail": None,
                            },
                        ],
                        "model_version": "mock-heuristic-v1",
                        "mock_mode": True,
                        "processing_time_ms": 3.14,
                        "request_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
                        "predicted_at": "2026-08-03T21:00:03Z",
                    },
                },
            ]
        }
    }
