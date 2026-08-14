# MindShield — Test Case Matrix

> **Document ID**: `docs/TEST_CASE_MATRIX.md`  
> **Phase**: FYP-I Testing, Validation & Verification  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Test Case Specifications

This table indexes the verified test cases implemented across the backend (pytest) and frontend (flutter_test) suites.

| Test ID | Requirement | Component | Test Type | Input / Condition | Expected Result | Actual Result | Status | Evidence File | Remarks |
|---|---|---|---|---|---|---|---|---|---|
| **TC-01** | FR-06 | Validators | Unit (Pytest) | Message: "a", "123", "normal message" | Reject empty/numeric, pass normal. | Match expected validations. | **PASSED** | `test_validators.py` | Core API text validation rules. |
| **TC-02** | FR-06 | Preprocessing | Unit (Pytest) | Whitespace strings, normalisation inputs. | Normalise Unicode NFKC, strip spaces. | Message cleaned correctly. | **PASSED** | `test_validators.py` | Unicode sanitisation pipeline. |
| **TC-03** | FR-07 | Health Router | API (Pytest) | HTTP GET `/health` request. | Return 200 OK and model ready. | Return healthy status payload. | **PASSED** | `test_health.py` | Lifespan weight loader liveness. |
| **TC-04** | FR-08 | Model Loader | ML Model | "Verify your identity http://fake.bank" | Label = "phishing", confidence >= 0.85. | Return high threat classification. | **PASSED** | `test_model_loader_real.py` | Fine-tuned weight model loader verification. |
| **TC-05** | FR-04 | Network Client | API (Flutter) | SMS Body: "URGENT: Verify account" | HTTP POST payload has correct JSON. | Client sends correct POST. | **PASSED** | `analysis_service_test.dart` | Dio request schema verification. |
| **TC-06** | FR-04 | Network Client | Integration | Simulating connection timeout. | Retries up to 2 times on timeout. | Retried twice, then fails. | **PASSED** | `analysis_service_test.dart` | Client-side network retry resilience. |
| **TC-07** | FR-05 | Analysis Map | Integration | Phishing response JSON payload. | Maps to threatScore >= 85, phishing. | Returns mapped model. | **PASSED** | `api_analysis_repository_test.dart` | Dangerous result entity mapper. |
| **TC-08** | FR-05 | Analysis Map | Integration | Benign response JSON payload. | Maps to threatScore <= 15, benign. | Returns mapped model. | **PASSED** | `api_analysis_repository_test.dart` | Safe result entity mapper. |
| **TC-09** | FR-01, FR-03 | Presentation | UI Smoke | Launching the Flutter app. | App mounts and renders splash. | App mounted without errors. | **PASSED** | `widget_test.dart` | Basic application layout smoke test. |
| **TC-10** | FR-08 | Model weights | Regression | 9 HAM benchmark SMS on `v2` weights. | All classified as `safe`. | 6 passed, 3 failed (FPR mismatch). | **EXPECTED FAILURE** | `test_ml_regression.py` | Shows v2 classification limitations. |
| **TC-11** | FR-08 | Model weights | Regression | 9 HAM benchmark SMS on `v3` weights. | All classified as `safe`. | 8 passed, 1 failed (FPR mismatch). | **EXPECTED FAILURE** | `test_ml_regression_v3.py` | Shows v3 classification limitations. |
| **TC-12** | FR-08 | Model weights | Regression | 5 SPAM benchmark SMS on `v2` weights. | All classified as `phishing`. | 5 passed. | **PASSED** | `test_ml_regression.py` | Verification of spam recall. |

---

## 2. Status Legends
* **PASSED**: The test case executed successfully and matched all expectations.
* **EXPECTED FAILURE**: The test case failed due to known model/algorithm boundaries that are documented as research candidates (e.g. regression failures on `v2` or `v3` models).
* **DEVICE DEPENDENT / NOT VERIFIED**: The test case requires physical target device attachment and was not executable in headless automated testing.
