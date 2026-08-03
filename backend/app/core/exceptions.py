"""
MindShield Backend — Custom Exception Hierarchy.

Defines a typed exception tree rooted at ``MindShieldException``.
All application-specific errors inherit from this root, enabling
blanket catching in exception handlers while still allowing targeted
handling of specific error subtypes.

Design Principle (SOLID — Open/Closed):
    New exception types can be added by subclassing without modifying
    existing exception handlers. The FastAPI exception handlers in
    ``main.py`` register handlers for base types, automatically
    catching all subclasses.

HTTP Status Mapping:
    Each exception class carries an ``http_status_code`` that the
    global exception handler uses to build the HTTP response. This
    keeps HTTP concerns out of the business logic layer.
"""

from __future__ import annotations

from http import HTTPStatus


class MindShieldException(Exception):
    """Root exception for all MindShield application errors.

    All custom exceptions should inherit from this class so that
    the global exception handler can catch them with a single
    handler registration.

    Attributes:
        message:         Human-readable error description.
        http_status_code: HTTP status code to return to the client.
        error_code:      Machine-readable error identifier (snake_case).
    """

    http_status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code: str = "internal_error"

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        """Return developer-friendly string representation."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"http_status_code={self.http_status_code})"
        )


# ---------------------------------------------------------------------------
# Validation Errors (HTTP 422)
# ---------------------------------------------------------------------------


class ValidationException(MindShieldException):
    """Raised when request payload fails semantic validation.

    Distinct from Pydantic's own ValidationError (HTTP 422) — this
    covers business-rule validation (e.g., message exceeds max length
    after cleaning) that cannot be expressed purely in type annotations.
    """

    http_status_code = HTTPStatus.UNPROCESSABLE_ENTITY.value
    error_code = "validation_error"

    def __init__(self, message: str = "Request validation failed.") -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# Not Found Errors (HTTP 404)
# ---------------------------------------------------------------------------


class NotFoundException(MindShieldException):
    """Raised when a requested resource does not exist."""

    http_status_code = HTTPStatus.NOT_FOUND.value
    error_code = "not_found"

    def __init__(self, resource: str = "Resource", message: str | None = None) -> None:
        super().__init__(message or f"{resource} not found.")
        self.resource = resource


# ---------------------------------------------------------------------------
# Model Errors (HTTP 503 / 500)
# ---------------------------------------------------------------------------


class ModelNotReadyException(MindShieldException):
    """Raised when the AI model is not loaded or initialised.

    Returns HTTP 503 Service Unavailable because the server is running
    but the model dependency is not yet available. Clients should retry.

    Note:
        In Phase 2.1 this is always raised since MODEL_ENABLED=false.
        In Phase 2.2+ the ModelLoader will populate the model on startup.
    """

    http_status_code = HTTPStatus.SERVICE_UNAVAILABLE.value
    error_code = "model_not_ready"

    def __init__(self, message: str = "AI model is not currently available.") -> None:
        super().__init__(message)


class ModelInferenceException(MindShieldException):
    """Raised when model inference fails during a prediction request."""

    http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "model_inference_error"

    def __init__(self, message: str = "Model inference failed.") -> None:
        super().__init__(message)


class ModelLoadException(MindShieldException):
    """Raised when model loading, weight downloading, or warm-up fails."""

    http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "model_load_error"

    def __init__(
        self,
        message: str = "Failed to load model weights or architecture.",
    ) -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# Rate Limiting / Abuse Prevention (HTTP 429)
# ---------------------------------------------------------------------------


class RateLimitException(MindShieldException):
    """Raised when a client exceeds the allowed request rate.

    Phase 2.1 placeholder — rate limiting middleware will be added
    in a future phase.
    """

    http_status_code = HTTPStatus.TOO_MANY_REQUESTS.value
    error_code = "rate_limit_exceeded"

    def __init__(self, message: str = "Too many requests. Please slow down.") -> None:
        super().__init__(message)


# ---------------------------------------------------------------------------
# Configuration Errors (HTTP 500 — server-side misconfiguration)
# ---------------------------------------------------------------------------


class ConfigurationException(MindShieldException):
    """Raised when the application detects a fatal configuration error.

    This should only occur at startup, not during request handling.
    If raised during a request, it indicates a server-side bug.
    """

    http_status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
    error_code = "configuration_error"

    def __init__(self, message: str = "Server configuration error.") -> None:
        super().__init__(message)
