"""
MindShield Backend — Analysis Endpoint Tests.

Tests the POST /api/v1/analyze endpoint for:
  - Valid request → 200 with placeholder result
  - Invalid request bodies → 422 validation errors
  - Empty / too-short messages → 422
  - Response schema structure
  - Placeholder flag signalling
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


ANALYZE_URL = "/api/v1/analyze"
STATUS_URL = "/api/v1/analyze/status"

# A realistic, moderately-long smishing message
_VALID_SMS = (
    "URGENT: Your Lloyds Bank account has been suspended. "
    "Verify your details immediately at http://fake-bank.example.com"
)


class TestAnalyzeEndpoint:
    """Integration tests for POST /api/v1/analyze."""

    def test_valid_request_returns_200(self, client: TestClient) -> None:
        """A valid analysis request must return HTTP 200."""
        response = client.post(ANALYZE_URL, json={"message": _VALID_SMS})
        assert response.status_code == 200

    def test_response_envelope_structure(self, client: TestClient) -> None:
        """Response must conform to the APIResponse envelope."""
        data = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()
        assert "success" in data
        assert "message" in data
        assert "data" in data
        assert "timestamp" in data

    def test_response_success_true(self, client: TestClient) -> None:
        """``success`` must be True for a valid request."""
        data = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()
        assert data["success"] is True

    def test_result_contains_label(self, client: TestClient) -> None:
        """``data.label`` must be a non-empty string."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert "label" in result
        assert isinstance(result["label"], str)
        assert len(result["label"]) > 0

    def test_result_contains_threat_level(self, client: TestClient) -> None:
        """``data.threat_level`` must be one of the allowed values."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert result["threat_level"] in {"safe", "suspicious", "dangerous"}

    def test_result_confidence_in_range(self, client: TestClient) -> None:
        """``data.confidence`` must be between 0.0 and 1.0."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_result_has_explanation(self, client: TestClient) -> None:
        """``data.explanation`` must be a non-empty string."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 0

    def test_result_is_placeholder_true(self, client: TestClient) -> None:
        """``data.is_placeholder`` must be True in Phase 2.1."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert result["is_placeholder"] is True

    def test_result_has_model_version(self, client: TestClient) -> None:
        """``data.model_version`` must contain 'placeholder' in Phase 2.1."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert "placeholder" in result["model_version"]

    def test_result_has_predicted_at(self, client: TestClient) -> None:
        """``data.predicted_at`` must be an ISO timestamp string."""
        result = client.post(ANALYZE_URL, json={"message": _VALID_SMS}).json()["data"]
        assert "predicted_at" in result
        assert isinstance(result["predicted_at"], str)

    def test_optional_sender_accepted(self, client: TestClient) -> None:
        """Request with optional ``sender`` field must succeed."""
        response = client.post(
            ANALYZE_URL,
            json={"message": _VALID_SMS, "sender": "+447911123456"},
        )
        assert response.status_code == 200

    # ------------------------------------------------------------------
    # Validation — invalid inputs
    # ------------------------------------------------------------------

    def test_missing_message_field_returns_422(self, client: TestClient) -> None:
        """Omitting the required ``message`` field must return 422."""
        response = client.post(ANALYZE_URL, json={})
        assert response.status_code == 422

    def test_empty_message_returns_422(self, client: TestClient) -> None:
        """An empty string message must return 422."""
        response = client.post(ANALYZE_URL, json={"message": ""})
        assert response.status_code == 422

    def test_whitespace_only_message_returns_422(self, client: TestClient) -> None:
        """A whitespace-only message must return 422 after stripping."""
        response = client.post(ANALYZE_URL, json={"message": "   "})
        assert response.status_code == 422

    def test_too_short_message_returns_422(self, client: TestClient) -> None:
        """A message with fewer than 3 characters must return 422."""
        response = client.post(ANALYZE_URL, json={"message": "ab"})
        assert response.status_code == 422

    def test_too_long_message_returns_422(self, client: TestClient) -> None:
        """A message exceeding 2000 characters must return 422."""
        response = client.post(ANALYZE_URL, json={"message": "x" * 2001})
        assert response.status_code == 422

    def test_non_string_message_returns_422(self, client: TestClient) -> None:
        """A non-string ``message`` field must return 422."""
        response = client.post(ANALYZE_URL, json={"message": 12345})
        assert response.status_code == 422

    def test_error_response_envelope_on_422(self, client: TestClient) -> None:
        """Error responses must include the ``error`` envelope field."""
        data = client.post(ANALYZE_URL, json={}).json()
        assert data.get("success") is False
        assert "error" in data

    # ------------------------------------------------------------------
    # Status endpoint
    # ------------------------------------------------------------------

    def test_status_endpoint_returns_200(self, client: TestClient) -> None:
        """GET /api/v1/analyze/status must return 200."""
        response = client.get(STATUS_URL)
        assert response.status_code == 200

    def test_status_response_has_api_version(self, client: TestClient) -> None:
        """Status response ``data.api_version`` must equal 'v1'."""
        data = client.get(STATUS_URL).json()
        assert data["data"]["api_version"] == "v1"

    def test_status_response_has_endpoints_list(self, client: TestClient) -> None:
        """Status response ``data.endpoints`` must list available routes."""
        data = client.get(STATUS_URL).json()
        assert isinstance(data["data"]["endpoints"], list)
        assert len(data["data"]["endpoints"]) > 0


class TestAnalyzeUnit:
    """Unit tests for the AnalysisService without HTTP layer."""

    def test_service_returns_valid_result(self) -> None:
        """AnalysisService.analyse() must return an AnalysisResult."""
        from app.core.model_loader import PlaceholderModelLoader
        from app.services.analysis_service import AnalysisService
        from app.schemas.analysis import AnalysisResult

        loader = PlaceholderModelLoader()
        loader.load()
        service = AnalysisService(model_loader=loader)
        result = service.analyse(_VALID_SMS)

        assert isinstance(result, AnalysisResult)
        assert result.threat_level in {"safe", "suspicious", "dangerous"}
        assert 0.0 <= result.confidence <= 1.0

    def test_service_raises_on_empty_message(self) -> None:
        """Service must raise ValidationException for empty messages."""
        from app.core.exceptions import ValidationException
        from app.core.model_loader import PlaceholderModelLoader
        from app.services.analysis_service import AnalysisService

        loader = PlaceholderModelLoader()
        loader.load()
        service = AnalysisService(model_loader=loader)

        with pytest.raises(ValidationException):
            service.analyse("  ")

    def test_service_raises_on_unloaded_model(self) -> None:
        """Service must raise ModelNotReadyException if model not loaded."""
        from app.core.exceptions import ModelNotReadyException
        from app.core.model_loader import PlaceholderModelLoader
        from app.services.analysis_service import AnalysisService

        loader = PlaceholderModelLoader()
        # Intentionally do NOT call loader.load()
        service = AnalysisService(model_loader=loader)

        with pytest.raises(ModelNotReadyException):
            service.analyse(_VALID_SMS)
