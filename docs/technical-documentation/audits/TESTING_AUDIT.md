# Testing & Validation Audit

This document audits the test suites, categories, coverage scopes, and regression gates executed across the MindShield codebase.

---

## 1. Test Suite Categories

MindShield's test strategy is split into backend Python verification and frontend Dart/Flutter verification.

### Backend Python Tests (`backend/tests/`)
* **Core Unit Tests:**
  - `test_validators.py`: Verifies Unicode normalizations, whitespace collapses, URL matches, and key heuristic indicators.
  - `test_model_loader_factory.py`: Verifies compositional factories correctly map load backends.
  - `test_health.py`: Validates FastAPI operational status models.
* **Service Integration Tests:**
  - `test_inference_service.py`: Verifies loading sequences, prediction caches, and model load fallback pathways.
  - `test_analysis.py`: Verifies thin routing endpoints and request ID tracing.
* **ML Regression Suites:**
  - `test_ml_regression.py` & `test_ml_regression_v3.py`: Evaluates fine-tuned HuggingFace models against 14 distinct mock scenarios (Benign transaction alerts vs. Roman Urdu phishing) to ensure models do not regress during training.

### Frontend Dart Tests (`frontend/test/`)
* **Unit & Migration Tests:**
  - `dashboard_provider_test.dart`: Evaluates v1 $\rightarrow$ v2 database migrations, metrics calculations, recent analysis updates, and permission validation gates.
  - `api_analysis_repository_test.dart`: Verifies JSON responses are mapped correctly to AnalysisResult domains, and country prefixes are parsed.
  - `analysis_service_test.dart`: Validates retry counts and dio timeout handling.

---

## 2. Test Execution & Coverage Summary

All test suites execute successfully with 100% pass rates:

### Python pytest Execution Output:
```bash
============================= test session starts =============================
plugins: cov-5.0.0, anyio-4.3.0
collected 42 items

tests/test_validators.py .............                                   [ 30%]
tests/test_health.py ...                                                 [ 38%]
tests/test_model_loader_factory.py ..                                    [ 42%]
tests/test_inference_service.py .....                                    [ 54%]
tests/test_analysis.py .......                                           [ 71%]
tests/test_ml_regression_v3.py ............                             [100%]
============================== 42 passed in 14.2s =============================
```

### Flutter test Execution Output:
```bash
00:00 +0: C:/.../test/analysis_service_test.dart: analyzeMessage sends payload...
00:01 +4: C:/.../test/analysis_service_test.dart: retries up to 2 times...
00:01 +11: C:/.../test/dashboard_provider_test.dart: Database Migration Tests...
00:02 +13: C:/.../test/widget_test.dart: MindShieldApp smoke test
00:10 +15: All tests passed! (15 tests)
```

---

## 3. Discrepancies and Gap Analysis

* **Frontend UI Widget Coverage:** There are no isolated widget unit tests validating specific screens (like `AnalysisScreen` widgets rendering details). Testing is focused heavily on service layers and providers.
* **Android Native Instrumentation Testing:** There are no native instrumentation tests (Espresso or Robolectric) validating `SmsReceiver.kt` or `MainActivity.kt`. Local integrations rely entirely on manual verification.
