"""
MindShield Backend — Request Logging Middleware.

Logs every HTTP request and response with timing information.
Implemented as a Starlette ``BaseHTTPMiddleware`` so it integrates
cleanly with FastAPI's middleware stack.

Logged fields per request:
    - method, path, query params
    - response status code
    - duration in milliseconds
    - client IP address
    - request ID (injected as response header ``X-Request-ID``)

Design Note:
    Request IDs are generated per-request and propagated both to the
    response header (for client-side correlation) and to the log entry.
    This enables tracing a specific request across distributed log lines.
"""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.logging.logger import get_logger

logger = get_logger(__name__)

# Paths that should not be logged at INFO level (too noisy)
_SILENT_PATHS = frozenset({"/health", "/favicon.ico", "/robots.txt"})


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log incoming HTTP requests and outgoing responses.

    Attaches an ``X-Request-ID`` header to every response for
    end-to-end request tracing.

    Attributes:
        log_silent_paths: If True, also log health-check paths.
                          Defaults to False to reduce log noise.
    """

    def __init__(self, app: object, log_silent_paths: bool = False) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._log_silent_paths = log_silent_paths

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Intercept request, call next handler, log result.

        Args:
            request:   The incoming Starlette/FastAPI request.
            call_next: The next middleware or route handler.

        Returns:
            The response from the next handler, augmented with
            ``X-Request-ID`` and ``X-Process-Time-Ms`` headers.
        """
        request_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        path = request.url.path
        is_silent = path in _SILENT_PATHS

        # Attach request ID to request state for access inside handlers
        request.state.request_id = request_id

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1_000
        status_code = response.status_code

        # Add tracing headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"

        if not is_silent or self._log_silent_paths:
            log_method = logger.warning if status_code >= 400 else logger.info
            log_method(
                "%s %s → %d (%.2f ms) [%s]",
                request.method,
                path,
                status_code,
                duration_ms,
                request_id,
            )
        else:
            logger.debug(
                "%s %s → %d (%.2f ms) [%s]",
                request.method,
                path,
                status_code,
                duration_ms,
                request_id,
            )

        return response
