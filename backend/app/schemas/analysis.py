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
            "confidence": 0.94,
            "explanation": "⚠️ HIGH THREAT — ...",
            "indicators": [
                {"name": "url_detected",       "present": true,  "weight": "high"},
                {"name": "urgency_language",   "present": true,  "weight": "high"},
                {"name": "financial_keywords", "present": true,  "weight": "medium"}
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

    Attributes:
        name:    Machine-readable signal identifier (snake_case).
        present: Whether this signal was detected in the message.
        weight:  Relative importance of this signal to the verdict.
        detail:  Optional human-readable annotation for this signal.
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
        description="Optional human-readable annotation.",
        examples=["Shortened URL detected: bit.ly/abc123"],
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
                        "containing a suspicious URL and urgency language."
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
                        "A message using prize language without a direct URL — "
                        "classified as suspicious rather than dangerous."
                    ),
                    "value": {
                        "message": (
                            "Congratulations! You have won a £500 gift card. "
                            "Reply YES to claim your prize before it expires."
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
                        "A message requesting OTP / password — "
                        "highest threat signal weight."
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

    Attributes:
        label:              Raw classifier label (e.g. ``phishing``, ``safe``).
        threat_level:       Normalised severity bucket (safe|suspicious|dangerous).
        confidence:         Model confidence in [0.0, 1.0].
        explanation:        Human-readable rationale for the verdict.
        indicators:         List of individual signals detected in the message.
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
        examples=[0.94, 0.73, 0.82],
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
            "List of individual threat signals detected in the message. "
            "Rendered as an expandable evidence list in the Flutter UI."
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
                {
                    "summary": "Dangerous result",
                    "value": {
                        "label": "phishing",
                        "threat_level": "dangerous",
                        "confidence": 0.94,
                        "explanation": (
                            "⚠️ HIGH THREAT — contains a URL or shortened link; "
                            "uses urgency/imperative language; references financial "
                            "institutions or transactions. "
                            "[Mock heuristic — not a real AI prediction]"
                        ),
                        "indicators": [
                            {
                                "name": "url_detected",
                                "present": True,
                                "weight": "high",
                                "detail": "Suspicious URL detected in message body",
                            },
                            {
                                "name": "urgency_language",
                                "present": True,
                                "weight": "high",
                                "detail": "Keywords: 'urgent', 'suspended'",
                            },
                            {
                                "name": "financial_keywords",
                                "present": True,
                                "weight": "medium",
                                "detail": "Keywords: 'bank', 'account'",
                            },
                            {
                                "name": "credential_request",
                                "present": False,
                                "weight": "critical",
                            },
                            {
                                "name": "prize_language",
                                "present": False,
                                "weight": "medium",
                            },
                        ],
                        "model_version": "mock-heuristic-v1",
                        "mock_mode": True,
                        "processing_time_ms": 2.41,
                        "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                        "predicted_at": "2026-08-03T21:00:00Z",
                    },
                },
                {
                    "summary": "Safe result",
                    "value": {
                        "label": "safe",
                        "threat_level": "safe",
                        "confidence": 0.89,
                        "explanation": (
                            "✅ LOW RISK — uses casual, friendly language; "
                            "no suspicious indicators detected. "
                            "[Mock heuristic — not a real AI prediction]"
                        ),
                        "indicators": [
                            {
                                "name": "url_detected",
                                "present": False,
                                "weight": "high",
                            },
                            {
                                "name": "urgency_language",
                                "present": False,
                                "weight": "high",
                            },
                        ],
                        "model_version": "mock-heuristic-v1",
                        "mock_mode": True,
                        "processing_time_ms": 1.83,
                        "request_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
                        "predicted_at": "2026-08-03T21:00:01Z",
                    },
                },
            ]
        }
    }
