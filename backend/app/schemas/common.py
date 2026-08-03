"""
MindShield Backend — Common Pydantic Schemas.

Defines response envelope models shared across all API endpoints.
Using a consistent response structure enables client-side SDK
generation and simplifies error handling in the Flutter application.

Design Decision — Envelope Pattern:
    Every response is wrapped in a typed envelope:
        {
            "success": true,
            "data": { ... },
            "message": "OK",
            "timestamp": "2026-08-03T10:30:00Z"
        }
    Error responses share the same envelope with "success": false
    and an "error" field, eliminating the need for clients to parse
    different schemas for success vs. failure.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class HealthStatus(BaseModel):
    """Response schema for the /health endpoint."""

    status: str = Field(
        description="Server status indicator ('ok' | 'degraded' | 'error')"
    )
    app_name: str = Field(description="Application name")
    version: str = Field(description="Application semantic version")
    environment: str = Field(description="Deployment environment")
    model_loaded: bool = Field(description="Whether the AI model is active")
    model_version: str = Field(description="Model version identifier")
    uptime_seconds: float = Field(
        description="Seconds elapsed since the server started"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC timestamp of this health check",
    )

    model_config = {"populate_by_name": True}


class ErrorDetail(BaseModel):
    """Detail block embedded in error responses."""

    error_code: str = Field(description="Machine-readable error identifier")
    message: str = Field(description="Human-readable error description")


class APIResponse(BaseModel, Generic[DataT]):
    """Generic response envelope for all API endpoints.

    Type parameter ``DataT`` allows callers to specify the expected
    data payload type for auto-generated OpenAPI docs and client SDKs.

    Example:
        APIResponse[AnalysisResult]
    """

    success: bool = Field(description="True if the request succeeded")
    message: str = Field(description="Short status message")
    data: DataT | None = Field(default=None, description="Response payload")
    error: ErrorDetail | None = Field(
        default=None, description="Error details (only present on failure)"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="UTC timestamp of this response",
    )

    model_config = {
        "populate_by_name": True,
    }

    @classmethod
    def ok(cls, data: Any, message: str = "Success") -> "APIResponse[Any]":
        """Construct a successful response envelope.

        Args:
            data:    The payload to embed.
            message: Short description of the result.

        Returns:
            ``APIResponse`` with ``success=True``.
        """
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(
        cls,
        error_code: str,
        message: str,
    ) -> "APIResponse[None]":
        """Construct a failure response envelope.

        Args:
            error_code: Machine-readable identifier (e.g. "validation_error").
            message:    Human-readable description shown to the client.

        Returns:
            ``APIResponse`` with ``success=False`` and ``error`` populated.
        """
        return cls(
            success=False,
            message=message,
            data=None,
            error=ErrorDetail(error_code=error_code, message=message),
        )
