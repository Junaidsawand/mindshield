"""
MindShield Backend — Test Configuration & Fixtures.

Provides shared pytest fixtures available to all test modules:
  - ``test_settings`` — test-mode Settings override.
  - ``test_app``      — isolated FastAPI application instance.
  - ``client``        — synchronous TestClient for HTTP assertions.

Design Note:
    Each test module receives a fresh app instance via the ``test_app``
    fixture, preventing state leakage between test runs. The Settings
    cache is cleared in the ``test_settings`` fixture to ensure test
    values don't pollute production config.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.main as main_module
from app.core.config import Settings, get_settings
from app.core.model_loader import PlaceholderModelLoader
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
    """Return a fresh FastAPI application instance for each test."""
    # Inject a loaded placeholder into the module-level registry
    loader = PlaceholderModelLoader()
    loader.load()
    main_module._model_loader = loader

    application = create_app(settings=test_settings)
    return application


@pytest.fixture()
def client(test_app: FastAPI) -> TestClient:
    """Return a synchronous TestClient wrapping the test app.

    Using TestClient (synchronous) avoids the complexity of async
    test fixtures while still exercising the full ASGI stack.
    """
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c
