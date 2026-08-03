"""
MindShield Backend — Comprehensive API Test Suite (Phase 2.4).

Executes automated end-to-end API testing across:
  1. Health & Liveness Endpoints (/health)
  2. Operational Metadata & Versioning (/api/v1/analyze/status)
  3. SMS Classification Happy Path (Dangerous, Suspicious, Safe)
  4. Boundary Value Analysis & Invalid Input Rules (Missing, short, numeric)
  5. HTTP Protocol & Route Errors (404 Not Found, 422 Unprocessable Entity)
  6. SLA Performance Verification (Response latency threshold assertions)
"""

from __future__ import annotations

import time

from fastapi.testclient import TestClient


class TestAPIHealthAndStatus:
    """Tests health check and operational status endpoints."""

    def test_health_check_returns_200_and_headers(self, client: TestClient) -> None:
        start = time.perf_counter()
        response = client.get("/health")
        latency_ms = (time.perf_counter() - start) * 1_000

        assert response.status_code == 200
        assert latency_ms < 200.0  # SLA < 200ms for health check

        data = response.json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is True
        assert isinstance(data["version"], str)
        assert "x-request-id" in response.headers
        assert "x-process-time-ms" in response.headers

    def test_api_v1_status_returns_200_meta(self, client: TestClient) -> None:
        response = client.get("/api/v1/analyze/status")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["api_version"] == "v1"
        assert data["data"]["mock_mode"] is True
        assert isinstance(data["data"]["endpoints"], list)


class TestSMSAnalysisHappyPath:
    """Tests valid classification requests across threat levels."""

    def test_analyze_phishing_dangerous(self, client: TestClient) -> None:
        payload = {
            "message": (
                "URGENT: Your Lloyds Bank account has been suspended. "
                "Verify identity immediately: http://lloydssecure-verify.example.com"
            ),
            "sender": "LLOYDS",
            "metadata": {
                "app_version": "1.0.0",
                "locale": "en-GB",
                "network": "mobile",
            },
        }

        start = time.perf_counter()
        response = client.post("/api/v1/analyze", json=payload)
        latency_ms = (time.perf_counter() - start) * 1_000

        assert response.status_code == 200
        assert latency_ms < 500.0  # SLA < 500ms for single analysis

        res_json = response.json()
        assert res_json["success"] is True
        data = res_json["data"]
        assert data["threat_level"] == "dangerous"
        assert data["label"] == "phishing"
        assert data["confidence"] >= 0.75
        assert len(data["indicators"]) == 6
        assert data["request_id"] is not None
        assert "x-request-id" in response.headers

    def test_analyze_suspicious_prize(self, client: TestClient) -> None:
        payload = {
            "message": "You have won a prize! Reply WIN to claim your reward.",
            "sender": "+447700900123",
        }
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["threat_level"] == "suspicious"
        assert 0.60 <= data["confidence"] <= 0.85

    def test_analyze_safe_conversation(self, client: TestClient) -> None:
        payload = {
            "message": "Hi! Are you coming to lunch tomorrow?",
            "sender": "+447700900456",
        }
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["threat_level"] == "safe"
        assert data["confidence"] >= 0.70
        assert all(ind["present"] is False for ind in data["indicators"])

    def test_analyze_credential_harvest(self, client: TestClient) -> None:
        payload = {
            "message": (
                "Security alert: someone accessed your account. "
                "Enter your password and OTP here: http://secure-verify.example.com"
            ),
            "sender": "SecureAlert",
        }
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["threat_level"] == "dangerous"
        cred_ind = next(
            i for i in data["indicators"] if i["name"] == "credential_request"
        )
        assert cred_ind["present"] is True
        assert cred_ind["weight"] == "critical"


class TestBoundaryAndValidationErrorSuite:
    """Tests schema validation, boundary conditions, and invalid inputs."""

    def test_missing_message_field(self, client: TestClient) -> None:
        payload = {"sender": "+447700900123"}
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 422

        res_json = response.json()
        assert res_json["success"] is False
        assert res_json["error"]["error_code"] == "validation_error"
        assert isinstance(res_json["error"]["details"], list)

    def test_empty_message_string(self, client: TestClient) -> None:
        response = client.post("/api/v1/analyze", json={"message": ""})
        assert response.status_code == 422

    def test_whitespace_only_message(self, client: TestClient) -> None:
        response = client.post("/api/v1/analyze", json={"message": "        "})
        assert response.status_code == 422

    def test_message_too_short(self, client: TestClient) -> None:
        response = client.post("/api/v1/analyze", json={"message": "ab"})
        assert response.status_code == 422

    def test_message_too_long(self, client: TestClient) -> None:
        long_msg = "A" * 2001
        response = client.post("/api/v1/analyze", json={"message": long_msg})
        assert response.status_code == 422

    def test_purely_numeric_message(self, client: TestClient) -> None:
        response = client.post("/api/v1/analyze", json={"message": "123456789"})
        assert response.status_code == 422
        res_json = response.json()
        assert res_json["success"] is False
        assert res_json["error"]["error_code"] == "validation_error"

    def test_sender_string_too_long(self, client: TestClient) -> None:
        long_sender = "S" * 51
        payload = {"message": "Valid SMS message body text", "sender": long_sender}
        response = client.post("/api/v1/analyze", json=payload)
        assert response.status_code == 422


class TestHTTPAndRoutingErrorSuite:
    """Tests 404 Not Found envelopes and routing errors."""

    def test_non_existent_route_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/non_existent_route")
        assert response.status_code == 404

        res_json = response.json()
        assert res_json["success"] is False
        assert res_json["error"]["error_code"] == "http_404"
