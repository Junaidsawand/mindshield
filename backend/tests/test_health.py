"""
MindShield Backend — Health Endpoint Tests.

Tests the GET /health endpoint for:
  - Correct HTTP status code (200)
  - Response schema completeness
  - Model availability reporting
  - Content-Type header
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Integration tests for GET /health."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint must return HTTP 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_content_type(self, client: TestClient) -> None:
        """Response must be JSON."""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_health_response_has_status_ok(self, client: TestClient) -> None:
        """``status`` field must be 'ok'."""
        data = client.get("/health").json()
        assert data["status"] == "ok"

    def test_health_response_has_app_name(self, client: TestClient) -> None:
        """``app_name`` field must be present and non-empty."""
        data = client.get("/health").json()
        assert "app_name" in data
        assert len(data["app_name"]) > 0

    def test_health_response_has_version(self, client: TestClient) -> None:
        """``version`` field must be present and follow semver pattern."""
        data = client.get("/health").json()
        assert "version" in data
        parts = data["version"].split(".")
        assert len(parts) == 3, f"Expected semver, got: {data['version']}"

    def test_health_response_has_model_info(self, client: TestClient) -> None:
        """``model_loaded`` and ``model_version`` must be present."""
        data = client.get("/health").json()
        assert "model_loaded" in data
        assert "model_version" in data

    def test_health_model_loaded_is_true(self, client: TestClient) -> None:
        """Placeholder model should report as loaded after startup."""
        data = client.get("/health").json()
        assert data["model_loaded"] is True

    def test_health_model_version_is_placeholder(self, client: TestClient) -> None:
        """Model version must identify the placeholder in Phase 2.1."""
        data = client.get("/health").json()
        assert "placeholder" in data["model_version"]

    def test_health_response_has_uptime(self, client: TestClient) -> None:
        """``uptime_seconds`` must be a non-negative number."""
        data = client.get("/health").json()
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0

    def test_health_response_has_timestamp(self, client: TestClient) -> None:
        """``timestamp`` must be an ISO 8601 UTC string."""
        data = client.get("/health").json()
        assert "timestamp" in data
        ts = data["timestamp"]
        # Should contain date separators
        assert "T" in ts or "-" in ts

    def test_health_has_request_id_header(self, client: TestClient) -> None:
        """Response must include ``X-Request-ID`` header from middleware."""
        response = client.get("/health")
        assert "x-request-id" in response.headers

    def test_health_has_process_time_header(self, client: TestClient) -> None:
        """Response must include ``X-Process-Time-Ms`` header."""
        response = client.get("/health")
        assert "x-process-time-ms" in response.headers

    def test_health_environment_field(self, client: TestClient) -> None:
        """``environment`` field must be one of the known values."""
        data = client.get("/health").json()
        assert data["environment"] in {"development", "staging", "production"}
