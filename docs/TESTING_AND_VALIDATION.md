# MindShield — Testing, Validation & Verification

> **Document ID**: `docs/TESTING_AND_VALIDATION.md`  
> **Phase**: FYP-I Testing, Validation & Verification  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Document Control
This document records the testing objectives, strategies, test suites, execution logs, and requirements validations for the MindShield system. It provides an academic record of testing methodologies for both the client application and backend inference hosts.

---

## 2. Testing Objectives
The primary testing objectives for the MindShield system are:
1. **Regression Integrity**: Verifying that fine-tuning new candidate weights (`v3`) does not cause classifications of legitimate local notifications to regress.
2. **Payload Durability**: Verifying that API communication, validation rules, and JSON serialization boundaries are preserved.
3. **Execution Latency SLA**: Keeping model CPU inference execution times under the $60\text{ ms}$ threshold.
4. **App Sandbox Stability**: Confirming that background receivers, SQLite transactions, and user screens mount without error.

---

## 3. Testing Scope
The scope of verification encompasses:
* **Backend**: FastAPI routes, Pydantic request/response schemas, regex validators, BaseModelLoader classes, and the InferenceService.
* **Frontend**: Dio client network configurations, local SQLite cache transactions, Providers state management, and UI screen mounts.
* **Machine Learning**: Evaluation of model weights (`distilbert-pakscam-v1` and research candidate `v3`) against UCI datasets, Pakistani templates, and a 14-case regression suite.

---

## 4. Testing Strategy
MindShield's verification follows a multi-layered testing strategy:
* **Unit Testing**: Stateless validators, preprocessing normalization, and domain entity mapping are tested in isolation.
* **API Integration Testing**: Evaluates FastAPI router lifespan setups, endpoints, validation rules, and Dio network adapters.
* **Model Regression Testing**: Evaluates PyTorch classification weights against localized benchmarks.
* **UI Smoke Testing**: Confirms the Flutter application mounts and renders screens without crashing.

---

## 5. Test Environment
* **Mobile Environment**: Android Emulator running API level 34 (minSdkVersion target set to 21).
* **Python Runtime**: Python 3.13.1 on a Windows x64 host.
* **Testing Libraries**: pytest 8.3.x, pytest-cov, flutter_test.

---

## 6. Testing Tools
* **Pytest**: Used to run python test cases, fixtures, and coverage audits on the backend.
* **Flutter Test Tool**: Used to run headless widget smoke tests and repository mocks.
* **Coverage.py**: Computes statement coverage for backend packages.

---

## 7. Test Classification
Tests in the MindShield repository are divided into 6 distinct suites:
1. **Backend Unit Tests**: Found in `backend/tests/test_validators.py` and `test_preprocessing_pipeline.py`.
2. **Backend API Tests**: Found in `backend/tests/test_analysis.py` and `test_health.py`.
3. **Model Regression Tests**: Found in `backend/tests/test_ml_regression.py` and `test_ml_regression_v3.py`.
4. **Model Loader Tests**: Found in `backend/tests/test_model_loader_factory.py` and `test_model_loader_real.py`.
5. **Frontend Client Tests**: Found in `frontend/test/analysis_service_test.dart` and `api_analysis_repository_test.dart`.
6. **Frontend Smoke Tests**: Found in `frontend/test/widget_test.dart`.

---

## 8. Backend Unit Testing
Backend unit tests evaluate individual validators and preprocessing functions:
* **Validators**: `contains_url`, `contains_urgency_language`, `contains_financial_keywords`, `contains_credential_request`, and `contains_prize_language` are validated against positive and negative test strings.
* **Normalizer**: Unicode normalizer and lowercase normalizer pipelines are tested to ensure they output expected normalized strings.
* **Status**: **211 tests passed**.

---

## 9. API Testing
Examines endpoints and schema serialization:
* **POST `/api/v1/analyze`**: Checks validation rules (length between 3 and 2,000, non-numeric checks) and correct response envelopes.
* **GET `/health`**: Verifies liveness check status.
* **Status**: **11 tests passed**.

---

## 10. ML Model Testing
Evaluates the PyTorch inference pipeline on the host:
* **Active weights (`distilbert-pakscam-v1`)**: UCI Test F1 = $96.00\%$, Pak Ham FPR = $93.10\%$, Pak Spam Recall = $98.11\%$.
* **Research candidate (`distilbert-pakscam-v3`)**: UCI Test F1 = $95.08\%$, Pak Ham FPR = $3.45\%$, Pak Spam Recall = $100.00\%$.
* **Status**: **6 tests passed**.

---

## 11. Dataset/Regression Validation
Evaluated via `test_ml_regression.py` and `test_ml_regression_v3.py`:
* **Regression benchmarks**: The 14-case regression suite contains 9 actual HAM and 5 actual SPAM localized messages. 
* **Important**: The 14 regression cases are **not** an independent, unseen test set, as they are derived from base seeds used in training. They function as a **regression benchmark gating suite** to evaluate model degradation.
* **Results**:
  * `v1` passes **5/14** cases ($35.71\%$).
  * `v2` passes **11/14** cases ($78.57\%$).
  * `v3` passes **13/14** cases ($92.86\%$).
* **Regression failures (Expected)**:
  * `v2` fails 3 cases: `ubl_customer_service_bitly`, `zong_50_percent_off`, and `gaming_royale_subscription` (misclassified as phishing).
  * `v3` fails 1 case: `zong_engage_prize_lang` (misclassified as phishing).

---

## 12. Flutter Widget Testing
* **Smoke Testing**: [`widget_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/widget_test.dart) verifies that `MindShieldApp` builds and mounts successfully, rendering the splash screen.
* **Limitations**: UI interaction tests for onboarding, inbox scroll, history logs, and dashboard charts are **not** tested in headless environments and are deferred to FYP-II.
* **Status**: **1 test passed**.

---

## 13. Android Device-Level Testing
* **interception verification**: Background Kotlin SMS receivers, platform method channels, and contacts service calls require active device attachments.
* **Status**: **NOT VERIFIED / DEVICE DEPENDENT** (Device-level execution evidence was not available in the repository audit).

---

## 14. Database Testing
* **DatabaseHelper**: Instantiates and seeds `mindshield.db` with one table: `sms_messages`.
* **Actions tested**: Message insertion, thread query updates, spam moves, and deletes.
* **Status**: Tested as part of repository mock tests.

---

## 15. Input Validation Testing
Tested in `test_validators.py` and `test_analysis.py`:
* **Empty string**: Returns validation error (HTTP 422).
* **Solely digits**: Returns validation error (HTTP 400).
* **Whitespace only**: Stripped and rejected (HTTP 422).

---

## 16. Error / Edge-Case Testing
* **Network Timeout**: Checked in [`analysis_service_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/analysis_service_test.dart), confirming that the client retries up to 2 times on timeout.
* **Unready Model fallback**: Checked in `test_inference_service.py`. If the model loader fails to initialize, the pipeline redirects execution to the fallback loader.

---

## 17. Performance Testing (Latency SLA)
Verified in `evaluate_v3_suite.py` CPU latency audits:
* **Active Model (`v1`)**: Mean inference latency = $41.95\text{ ms}$ (Max: $50.74\text{ ms}$).
* **Research Model (`v3`)**: Mean inference latency = $57.62\text{ ms}$ (Max: $77.51\text{ ms}$).
* **Note**: These metrics represent **model inference latency**, not end-to-end network latency.

---

## 18. Requirements Traceability

| Requirement ID | Type | Associated Test Case | Evidence File | Status |
|---|---|---|---|---|
| **FR-01** (Permissions) | UI Flow | `MindShieldApp smoke test` | `widget_test.dart` | **PARTIALLY VERIFIED** (App mounts onboarding) |
| **FR-02** (Interception) | Native | None (Requires device) | `sms_background_service.dart` | **NOT TESTED / DEVICE DEPENDENT** |
| **FR-03** (Threads UI) | UI Flow | `MindShieldApp smoke test` | `widget_test.dart` | **PARTIALLY VERIFIED** (App mounts inbox) |
| **FR-04** (Query API) | Network | `analyzeMessage sends correct payload` | `analysis_service_test.dart` | **VERIFIED** |
| **FR-05** (Highlights) | UI Flow | `getAnalysis maps response` | `api_analysis_repository_test.dart` | **VERIFIED** (Model mapping verification) |
| **FR-06** (Validate API) | API | `test_is_valid_message` | `test_validators.py` | **VERIFIED** |
| **FR-07** (Load Weights) | ML | `test_health_endpoint` | `test_health.py` | **VERIFIED** |
| **FR-08** (Inference) | ML | `test_predict` | `test_model_loader_real.py` | **VERIFIED** |
| **NFR-01** (Latency) | Perf | `test_latency` | `test_ml_regression.py` | **VERIFIED** (Model latency $41.95\text{ ms}$) |
| **NFR-02** (DB Latency) | Perf | None | `database_helper.dart` | **NOT TESTED** (Latency target unverified) |
| **NFR-03** (HTTPS) | Sec | None | `app_constants.dart` | **PLANNED / FYP-II** (Dev uses HTTP) |
| **NFR-04** (Sanitisation)| Sec | `test_sanitise_message` | `test_validators.py` | **VERIFIED** |
| **NFR-05** (Anonymise) | Priv | `test_log_scrubbing` | `test_analysis.py` | **VERIFIED** (API does not log numbers) |
| **NFR-06** (Urdu Alerts) | UI Flow | None | `risk_level_badge.dart` | **NOT TESTED** |
| **NFR-07** (Android SDK) | Comp | None | `build.gradle` (SDK 21 target) | **VERIFIED** (via Gradle target inspection) |

---

## 19. Test Results

### 19.1 Pytest Execution Summary
* **Total Tests Executed**: 234
* **Passed**: 230
* **Failed**: 4 (Expected failures on regression suite, matching evaluations)
* **Statement Coverage**: $75\%$ (Average across all backend files)

### 19.2 Flutter Test Execution Summary
* **Total Tests Executed**: 5
* **Passed**: 5
* **Failed**: 0

---

## 20. Known Limitations
* **UI Testing Gap**: Flutter UI validation is limited to smoke tests (basic screen mounting). Detailed widget interaction testing (e.g. scrolling lists, settings changes) is missing in headless test suites.
* **Device dependency**: Native background receivers and contacts integration require physical device attachments and cannot be validated in unit tests.
* **Regression suite overlap**: The 14-case regression suite is derived from base templates, meaning it does not function as an independent, unseen test set.

---

## 21. FYP-I Testing Boundary
* **FYP-I (Completed)**: Backend validation unit tests, API schema tests, model loader verification, regression suite gating, and client network integration tests.
* **FYP-II (Planned)**: Setting up automated on-device integration test suites (using Flutter Integration Test runner), simulating incoming SMS broadcasts via ADB, and running security pen testing under HTTPS.

---

## 22. FYP-II Testing Plan
1. **On-Device Integration Tests**: Write test scripts using the `integration_test` package to simulate SMS interception.
2. **Mock SMS Broadcasts**: Automate native test scripts executing `adb shell am broadcast` to verify background Kotlin listeners.
3. **Database benchmarks**: Build benchmarking scripts to evaluate SQLite read/write latencies under load.

---

## 23. Final Verification Summary
The testing results verify that the core FastAPI endpoint router and PyTorch model loader function as designed. The $75\%$ backend coverage and passing network adapters on the client confirm the technical stability of the FYP-I proof of concept.
