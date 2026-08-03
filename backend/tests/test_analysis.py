"""
MindShield Backend — Analysis Endpoint Tests (Phase 2.2).

Tests the POST /api/v1/analyze endpoint with the Phase 2.2
MockModelLoader (heuristic engine), verifying:

  - Happy-path responses for all three threat levels.
  - Response envelope structure and schema compliance.
  - Threat classification correctness on known inputs.
  - Confidence score calibration (range and level expectations).
  - Indicator list presence and structure.
  - Processing time and request_id fields.
  - Comprehensive input validation (422 / 400 responses).
  - Service-layer unit tests (no HTTP stack).
  - MockModelLoader unit tests (heuristic correctness).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

ANALYZE_URL = "/api/v1/analyze"
STATUS_URL = "/api/v1/analyze/status"

# ── Known test messages ────────────────────────────────────────────────────
_DANGEROUS_SMS = (
    "URGENT: Your Lloyds Bank account has been suspended. "
    "Verify your identity immediately: http://lloydssecure.example.com"
)
_CREDENTIAL_SMS = (
    "Security alert: enter your password and OTP here to verify "
    "your account: https://verify.example.com"
)
_SUSPICIOUS_SMS = (
    "Congratulations! You have won a £500 prize. "
    "Reply YES to claim before it expires."
)
_SAFE_SMS = "Hi! Are you coming to lunch tomorrow?"


# ==========================================================================
# Integration Tests — HTTP endpoint
# ==========================================================================


class TestAnalyzeHappyPath:
    """Smoke tests: valid requests must return HTTP 200."""

    def test_dangerous_input_returns_200(self, client: TestClient) -> None:
        response = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS})
        assert response.status_code == 200

    def test_suspicious_input_returns_200(self, client: TestClient) -> None:
        response = client.post(ANALYZE_URL, json={"message": _SUSPICIOUS_SMS})
        assert response.status_code == 200

    def test_safe_input_returns_200(self, client: TestClient) -> None:
        response = client.post(ANALYZE_URL, json={"message": _SAFE_SMS})
        assert response.status_code == 200


class TestResponseEnvelope:
    """Verify the APIResponse[AnalysisResult] envelope structure."""

    def test_envelope_has_success_field(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()
        assert "success" in data

    def test_envelope_success_true(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()
        assert data["success"] is True

    def test_envelope_has_message_field(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()
        assert "message" in data
        assert data["message"] == "Analysis complete"

    def test_envelope_has_data_field(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()
        assert "data" in data
        assert data["data"] is not None

    def test_envelope_has_timestamp(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()
        assert "timestamp" in data

    def test_envelope_error_null_on_success(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()
        assert data.get("error") is None


class TestAnalysisResultSchema:
    """Verify all AnalysisResult fields are present and typed correctly."""

    def test_result_has_label(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert isinstance(result["label"], str)
        assert len(result["label"]) > 0

    def test_result_threat_level_valid_enum(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        assert result["threat_level"] in {"safe", "suspicious", "dangerous"}

    def test_result_confidence_in_range(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        assert 0.0 <= result["confidence"] <= 1.0

    def test_result_has_explanation(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 10

    def test_result_has_indicators_list(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        assert "indicators" in result
        assert isinstance(result["indicators"], list)
        assert len(result["indicators"]) > 0

    def test_indicator_has_required_fields(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        indicator = result["indicators"][0]
        assert "name" in indicator
        assert "present" in indicator
        assert "weight" in indicator

    def test_indicator_weight_valid_enum(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        valid_weights = {"critical", "high", "medium", "low"}
        for ind in result["indicators"]:
            assert ind["weight"] in valid_weights

    def test_result_has_model_version(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert isinstance(result["model_version"], str)
        assert len(result["model_version"]) > 0

    def test_result_mock_mode_true(self, client: TestClient) -> None:
        """Phase 2.2 always returns mock_mode=True."""
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert result["mock_mode"] is True

    def test_result_has_processing_time(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert result["processing_time_ms"] is not None
        assert result["processing_time_ms"] >= 0.0

    def test_result_has_predicted_at(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert "predicted_at" in result
        assert isinstance(result["predicted_at"], str)

    def test_result_has_request_id(self, client: TestClient) -> None:
        """request_id is injected by middleware — must be in response."""
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        # request_id is present (may be None if middleware bypassed in test)
        assert "request_id" in result


class TestThreatClassification:
    """Verify heuristic engine classifies known inputs correctly."""

    def test_phishing_sms_is_dangerous(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        assert result["threat_level"] == "dangerous"

    def test_credential_harvest_is_dangerous(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _CREDENTIAL_SMS}).json()[
            "data"
        ]
        assert result["threat_level"] == "dangerous"

    def test_prize_sms_is_at_least_suspicious(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SUSPICIOUS_SMS}).json()[
            "data"
        ]
        assert result["threat_level"] in {"suspicious", "dangerous"}

    def test_casual_message_is_safe(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert result["threat_level"] == "safe"

    def test_dangerous_confidence_high(self, client: TestClient) -> None:
        """Dangerous messages should have confidence ≥ 0.75."""
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        assert result["confidence"] >= 0.75

    def test_safe_confidence_high(self, client: TestClient) -> None:
        """Safe messages should have confidence ≥ 0.70."""
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        assert result["confidence"] >= 0.70

    def test_url_indicator_present_in_dangerous(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        url_ind = next(
            (i for i in result["indicators"] if i["name"] == "url_detected"), None
        )
        assert url_ind is not None
        assert url_ind["present"] is True

    def test_urgency_indicator_present_in_dangerous(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _DANGEROUS_SMS}).json()[
            "data"
        ]
        urgency_ind = next(
            (i for i in result["indicators"] if i["name"] == "urgency_language"), None
        )
        assert urgency_ind is not None
        assert urgency_ind["present"] is True

    def test_url_indicator_absent_in_safe(self, client: TestClient) -> None:
        result = client.post(ANALYZE_URL, json={"message": _SAFE_SMS}).json()["data"]
        url_ind = next(
            (i for i in result["indicators"] if i["name"] == "url_detected"), None
        )
        assert url_ind is not None
        assert url_ind["present"] is False


class TestOptionalFields:
    """Tests for optional request fields."""

    def test_sender_field_accepted(self, client: TestClient) -> None:
        response = client.post(
            ANALYZE_URL,
            json={"message": _SAFE_SMS, "sender": "+447700900123"},
        )
        assert response.status_code == 200

    def test_metadata_field_accepted(self, client: TestClient) -> None:
        response = client.post(
            ANALYZE_URL,
            json={
                "message": _SAFE_SMS,
                "sender": "+447700900123",
                "metadata": {
                    "app_version": "1.0.0",
                    "locale": "en-GB",
                    "network": "mobile",
                },
            },
        )
        assert response.status_code == 200

    def test_no_sender_accepted(self, client: TestClient) -> None:
        response = client.post(ANALYZE_URL, json={"message": _SAFE_SMS})
        assert response.status_code == 200


class TestValidationErrors:
    """Verify all invalid inputs return structured 422 responses."""

    def test_missing_message_returns_422(self, client: TestClient) -> None:
        assert client.post(ANALYZE_URL, json={}).status_code == 422

    def test_empty_message_returns_422(self, client: TestClient) -> None:
        assert client.post(ANALYZE_URL, json={"message": ""}).status_code == 422

    def test_whitespace_only_returns_422(self, client: TestClient) -> None:
        assert client.post(ANALYZE_URL, json={"message": "   "}).status_code == 422

    def test_too_short_returns_422(self, client: TestClient) -> None:
        assert client.post(ANALYZE_URL, json={"message": "ab"}).status_code == 422

    def test_too_long_returns_422(self, client: TestClient) -> None:
        assert client.post(ANALYZE_URL, json={"message": "x" * 2001}).status_code == 422

    def test_non_string_returns_422(self, client: TestClient) -> None:
        assert client.post(ANALYZE_URL, json={"message": 99999}).status_code == 422

    def test_error_response_success_false(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={}).json()
        assert data.get("success") is False

    def test_error_response_has_error_block(self, client: TestClient) -> None:
        data = client.post(ANALYZE_URL, json={}).json()
        assert "error" in data
        assert data["error"]["error_code"] == "validation_error"


class TestMiddlewareHeaders:
    """Verify middleware injects expected headers on every response."""

    def test_request_id_header_present(self, client: TestClient) -> None:
        response = client.post(ANALYZE_URL, json={"message": _SAFE_SMS})
        assert "x-request-id" in response.headers

    def test_process_time_header_present(self, client: TestClient) -> None:
        response = client.post(ANALYZE_URL, json={"message": _SAFE_SMS})
        assert "x-process-time-ms" in response.headers


class TestStatusEndpoint:
    """Tests for GET /api/v1/analyze/status."""

    def test_status_returns_200(self, client: TestClient) -> None:
        assert client.get(STATUS_URL).status_code == 200

    def test_status_api_version_v1(self, client: TestClient) -> None:
        data = client.get(STATUS_URL).json()
        assert data["data"]["api_version"] == "v1"

    def test_status_has_mock_mode_flag(self, client: TestClient) -> None:
        data = client.get(STATUS_URL).json()
        assert "mock_mode" in data["data"]
        assert data["data"]["mock_mode"] is True

    def test_status_endpoints_is_list(self, client: TestClient) -> None:
        data = client.get(STATUS_URL).json()
        assert isinstance(data["data"]["endpoints"], list)
        assert len(data["data"]["endpoints"]) > 0


# ==========================================================================
# Unit Tests — Service layer (no HTTP)
# ==========================================================================


class TestAnalysisServiceUnit:
    """Direct unit tests for AnalysisService."""

    def _make_service(self) -> object:
        from app.core.mock_model_loader import MockModelLoader
        from app.services.analysis_service import AnalysisService

        loader = MockModelLoader()
        loader.load()
        return AnalysisService(model_loader=loader)

    def test_dangerous_classification(self) -> None:
        from app.schemas.analysis import AnalysisResult

        service = self._make_service()
        result = service.analyse(_DANGEROUS_SMS)
        assert isinstance(result, AnalysisResult)
        assert result.threat_level == "dangerous"

    def test_safe_classification(self) -> None:
        service = self._make_service()
        result = service.analyse(_SAFE_SMS)
        assert result.threat_level == "safe"

    def test_result_has_indicators(self) -> None:
        service = self._make_service()
        result = service.analyse(_DANGEROUS_SMS)
        assert len(result.indicators) > 0

    def test_result_processing_time_populated(self) -> None:
        service = self._make_service()
        result = service.analyse(_SAFE_SMS)
        assert result.processing_time_ms is not None
        assert result.processing_time_ms >= 0.0

    def test_result_mock_mode_true(self) -> None:
        service = self._make_service()
        result = service.analyse(_SAFE_SMS)
        assert result.mock_mode is True

    def test_request_id_propagated(self) -> None:
        service = self._make_service()
        result = service.analyse(_SAFE_SMS, request_id="test-uuid-123")
        assert result.request_id == "test-uuid-123"

    def test_raises_validation_on_whitespace(self) -> None:
        from app.core.exceptions import ValidationException

        service = self._make_service()
        with pytest.raises(ValidationException):
            service.analyse("   ")

    def test_raises_when_model_not_loaded(self) -> None:
        from app.core.exceptions import ModelNotReadyException
        from app.core.mock_model_loader import MockModelLoader
        from app.services.analysis_service import AnalysisService

        loader = MockModelLoader()
        # Intentionally do NOT call loader.load()
        service = AnalysisService(model_loader=loader)
        with pytest.raises(ModelNotReadyException):
            service.analyse(_SAFE_SMS)


# ==========================================================================
# Unit Tests — MockModelLoader heuristic engine
# ==========================================================================


class TestMockModelLoaderUnit:
    """Direct unit tests for the MockModelLoader heuristic engine."""

    def _make_loader(self) -> object:
        from app.core.mock_model_loader import MockModelLoader

        loader = MockModelLoader()
        loader.load()
        return loader

    def test_url_plus_urgency_is_dangerous(self) -> None:
        loader = self._make_loader()
        pred = loader.predict("URGENT: account suspended click http://fake.example.com")
        assert pred.threat_level == "dangerous"

    def test_casual_text_is_safe(self) -> None:
        loader = self._make_loader()
        pred = loader.predict("Hello! See you tomorrow at lunch.")
        assert pred.threat_level == "safe"

    def test_credential_request_is_dangerous(self) -> None:
        loader = self._make_loader()
        pred = loader.predict("Enter your OTP and password to verify your account")
        assert pred.threat_level == "dangerous"

    def test_confidence_in_valid_range(self) -> None:
        loader = self._make_loader()
        for text in [_SAFE_SMS, _SUSPICIOUS_SMS, _DANGEROUS_SMS]:
            pred = loader.predict(text)
            assert 0.0 <= pred.confidence <= 1.0

    def test_model_version_contains_mock(self) -> None:
        loader = self._make_loader()
        pred = loader.predict(_SAFE_SMS)
        assert "mock" in pred.model_version

    def test_prediction_is_deterministic(self) -> None:
        """Same input must always produce the same classification."""
        loader = self._make_loader()
        pred1 = loader.predict(_DANGEROUS_SMS)
        pred2 = loader.predict(_DANGEROUS_SMS)
        assert pred1.threat_level == pred2.threat_level
        assert pred1.confidence == pred2.confidence

    def test_health_is_loaded_after_load(self) -> None:
        loader = self._make_loader()
        assert loader.health().is_loaded is True

    def test_health_not_loaded_before_load(self) -> None:
        from app.core.mock_model_loader import MockModelLoader

        loader = MockModelLoader()
        assert loader.health().is_loaded is False
