"""
MindShield Backend — Core Settings.

Centralises all configuration using Pydantic BaseSettings.
Values are read from environment variables / .env file with
type validation, making misconfiguration detectable at startup.

Design Decision:
    Using a singleton `get_settings()` with `lru_cache` ensures the
    .env file is parsed exactly once and the same Settings object is
    shared across the entire process lifetime — avoiding repeated
    disk I/O and guaranteeing consistency.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables.

    Pydantic BaseSettings reads from:
      1. Environment variables (highest priority)
      2. .env file
      3. Field defaults (lowest priority)

    Every attribute is type-checked at startup. A missing required
    variable raises a ValidationError immediately, preventing the
    server from starting in a misconfigured state.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application Metadata
    # ------------------------------------------------------------------
    app_name: str = Field(default="MindShield API", description="Human-readable name")
    app_version: str = Field(default="2.3.0", description="Semantic version")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # ------------------------------------------------------------------
    # Server
    # ------------------------------------------------------------------
    host: str = Field(default="0.0.0.0", description="Bind address")
    port: int = Field(default=8000, ge=1, le=65535, description="Bind port")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 route prefix")

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Minimum logging level",
    )
    log_format: Literal["json", "text"] = Field(
        default="text",
        description="Log output format",
    )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------
    secret_key: str = Field(
        default="CHANGE_ME",
        min_length=16,
        description="Secret key for signing (Phase 2.2+)",
    )

    # ------------------------------------------------------------------
    # Model (Phase 2.3 AI Model Loading Architecture)
    # ------------------------------------------------------------------
    model_backend: Literal["mock", "huggingface", "placeholder"] = Field(
        default="mock",
        description="Active model loader backend implementation",
    )
    model_path: str = Field(
        default="",
        description="Path or HF hub ID for model weights",
    )
    model_version: str = Field(
        default="mock-heuristic-v1",
        description="Model version identifier",
    )
    model_enabled: bool = Field(
        default=True,
        description="Whether model inference is enabled",
    )
    model_fallback_enabled: bool = Field(
        default=True,
        description="Whether to fall back to mock loader if primary loader fails",
    )

    # ------------------------------------------------------------------
    # Derived helpers
    # ------------------------------------------------------------------
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def normalise_origins(cls, v: str) -> str:
        """Ensure no trailing whitespace around each origin."""
        return ",".join(o.strip() for o in str(v).split(","))

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS allowed origins as a Python list."""
        return [o for o in self.allowed_origins.split(",") if o]

    @property
    def is_production(self) -> bool:
        """True when running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """True when running in development environment."""
        return self.app_env == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    Using lru_cache(maxsize=1) ensures the .env file is read and
    parsed once, and the same object is returned on every call.
    In tests, call get_settings.cache_clear() to reset.
    """
    return Settings()
