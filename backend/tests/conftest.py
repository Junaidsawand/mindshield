"""
MindShield Backend — Test Configuration & Fixtures (Phase 2.2).

Provides shared pytest fixtures available to all test modules:
  - ``test_settings`` — test-mode Settings override.
  - ``test_app``      — isolated FastAPI application instance.
  - ``client``        — synchronous TestClient for HTTP assertions.

The ``test_app`` fixture injects a loaded ``MockModelLoader``
(Phase 2.2 heuristic engine) into the module-level registry so tests
exercise the full classification pipeline without starting uvicorn.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.main as main_module
from app.core.config import Settings, get_settings
from app.core.mock_model_loader import MockModelLoader
from app.main import create_app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Return settings configured for the test environment."""
    get_settings.cache_clear()
    return Settings(
        app_env="development",
        debug=True,
        log_level="DEBUG",
        log_format="text",
        allowed_origins="http://localhost:3000",
        secret_key="test-secret-key-32-chars-minimum!",
        model_enabled=False,
    )


@pytest.fixture()
def test_app(test_settings: Settings) -> FastAPI:
    """Return a fresh FastAPI application instance with MockModelLoader."""
    loader = MockModelLoader()
    loader.load()
    main_module._model_loader = loader
    return create_app(settings=test_settings)


@pytest.fixture()
def client(test_app: FastAPI) -> TestClient:
    """Return a synchronous TestClient wrapping the test app."""
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c
