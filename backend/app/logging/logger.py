"""
MindShield Backend — Structured Logging.

Provides a factory for pre-configured loggers with optional JSON
formatting for production environments. All application code should
obtain a logger via `get_logger(__name__)` rather than calling
`logging.getLogger` directly, ensuring consistent formatting.

Design Decision:
    JSON logging is used in production (log_format="json") so that
    log aggregation platforms (e.g., Loki, CloudWatch, Datadog) can
    parse and index fields without custom parsing rules.
    Plain-text format is used in development for human readability.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object.

    Structured log format enables log aggregation tools to index
    individual fields (level, module, message) without regex parsing.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


class _TextFormatter(logging.Formatter):
    """Human-readable formatter for development environments."""

    _GREY = "\x1b[38;20m"
    _BLUE = "\x1b[34;20m"
    _YELLOW = "\x1b[33;20m"
    _RED = "\x1b[31;20m"
    _BOLD_RED = "\x1b[31;1m"
    _RESET = "\x1b[0m"

    _LEVEL_COLOURS: dict[str, str] = {
        "DEBUG": _GREY,
        "INFO": _BLUE,
        "WARNING": _YELLOW,
        "ERROR": _RED,
        "CRITICAL": _BOLD_RED,
    }

    _FMT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    _DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        colour = self._LEVEL_COLOURS.get(record.levelname, self._RESET)
        formatter = logging.Formatter(
            fmt=f"{colour}{self._FMT}{self._RESET}",
            datefmt=self._DATE_FMT,
        )
        return formatter.format(record)


def configure_logging(level: str = "INFO", fmt: str = "text") -> None:
    """Configure the root logger for the application.

    Should be called once at application startup (in ``main.py``).

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        fmt:   Output format — ``"json"`` or ``"text"``.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    if fmt.lower() == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(_TextFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove any existing handlers to avoid duplicate output
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party libraries in production
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given name.

    Usage:
        logger = get_logger(__name__)
        logger.info("Server started")

    Args:
        name: Typically ``__name__`` of the calling module.

    Returns:
        A ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
