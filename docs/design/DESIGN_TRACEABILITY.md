# MindShield — Design Traceability Matrix

> **Document ID**: `docs/design/DESIGN_TRACEABILITY.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Traceability Matrix

This matrix maps each requirement defined in the Software Requirements Specification (SRS) to its corresponding architectural diagrams, code files, and test suites.

| Requirement ID | Component / Module | Architectural Diagrams | Code Implementation | Verification / Test Evidence | Status |
|---|---|---|---|---|---|
| **FR-01** (Permissions Onboarding) | Onboarding / UI Flow | `USE_CASE_DIAGRAM.md`, `SEQUENCE_DIAGRAM.md` | [`permissions_provider.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/permissions/presentation/permissions_provider.dart) | `widget_test.dart` (app smoke test) | **IMPLEMENTED** |
| **FR-02** (SMS Interception) | Native Binder / Background Daemon | `SYSTEM_ARCHITECTURE.md`, `DFD_LEVEL_1.md` | [`sms_background_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/sms_background_service.dart) | Verified via runtime device tests | **IMPLEMENTED** |
| **FR-03** (Thread Rendering) | Presentation Layer Inbox | `SYSTEM_ARCHITECTURE.md`, `ERD.md` | [`inbox_screen.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/inbox/presentation/inbox_screen.dart) | `widget_test.dart` (app smoke test) | **IMPLEMENTED** |
| **FR-04** (Query REST API) | Network Client | `SEQUENCE_DIAGRAM.md`, `API_DATA_FLOW.md` | [`api_analysis_repository.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/data/api_analysis_repository.dart), [`dio_client.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/network/dio_client.dart) | [`api_analysis_repository_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/api_analysis_repository_test.dart), [`analysis_service_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/analysis_service_test.dart) | **IMPLEMENTED** |
| **FR-05** (Visual Highlights) | Explainability presentation | `COMPONENT_DIAGRAM.md`, `SEQUENCE_DIAGRAM.md` | [`lime_highlight_card.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart) | `widget_test.dart` (app smoke test) | **IMPLEMENTED** |
| **FR-06** (Request Validation) | API Schemas / validators | `DFD_LEVEL_1.md`, `API_DATA_FLOW.md` | [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py), [`analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/schemas/analysis.py) | `test_validators.py` | **IMPLEMENTED** |
| **FR-07** (Lifespan Startup) | Inference Composition Root | `SYSTEM_ARCHITECTURE.md`, `DEPLOYMENT_DIAGRAM.md` | [`main.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/main.py), [`model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py) | `test_health.py` | **IMPLEMENTED** |
| **FR-08** (Inference execution) | PyTorch Model Loader | `SYSTEM_ARCHITECTURE.md`, `COMPONENT_DIAGRAM.md` | [`model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py) | `test_model_loader_real.py` | **IMPLEMENTED** |
| **NFR-01** (Inference Latency) | InferenceService / Host | `DEPLOYMENT_DIAGRAM.md` | [`inference_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/inference_service.py) | `test_ml_regression.py` (v1 benchmark metrics) | **IMPLEMENTED** |
| **NFR-02** (DB Latency target) | Local SQLite DB Helper | `ERD.md` | [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart) | Target of <15ms is unverified | **PLANNED / NOT YET VERIFIED** |
| **NFR-03** (Payload HTTPS) | API Gateway | `DEPLOYMENT_DIAGRAM.md` | [`app_constants.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/constants/app_constants.dart) (Dev connection uses HTTP) | Scheduled for cloud staging | **PLANNED / FYP-II** |
| **NFR-04** (Unicode sanitisation) | Validators | `DFD_LEVEL_1.md` | [`validators.py:sanitise_message`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py#L177-L198) | `test_validators.py` | **IMPLEMENTED** |
| **NFR-05** (PII Scrubbing) | Logger service | `API_DATA_FLOW.md` | [`analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) (does not write user sender numbers to logs) | Verified in log audits | **IMPLEMENTED** |
| **NFR-06** (Urdu Alerts) | Visual presenter | `USE_CASE_DIAGRAM.md` | [`risk_level_badge.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/spam/presentation/widgets/risk_level_badge.dart) | Warn UI renders safety labels | **PARTIALLY IMPLEMENTED / FYP-I** |
| **NFR-07** (Android Target SDK) | Android Gradle configuration | `DEPLOYMENT_DIAGRAM.md` | `frontend/android/app/build.gradle` (`minSdkVersion` set to `21`) | Verified on OS startup passes | **IMPLEMENTED** |

---

## 2. Use Case Mapping

| Use Case ID | Trigger Event | Primary Actor | Associated Functional Requirements | Status |
|---|---|---|---|---|
| **UC-01** | App launch / onboarding | Mobile User | FR-01 | **IMPLEMENTED** |
| **UC-02** | Incoming SMS Broadcast | Android OS | FR-02 | **IMPLEMENTED** |
| **UC-03** | App opened to Home | Mobile User | FR-03 | **IMPLEMENTED** |
| **UC-04** | Click "Analyze Thread" | Mobile User | FR-04, FR-06, FR-08 | **IMPLEMENTED** |
| **UC-05** | Display of Verdict details | Mobile User | FR-05 | **IMPLEMENTED** |
| **UC-06** | Navigating to Spam Folder | Mobile User | FR-02, FR-03 | **IMPLEMENTED** |
| **UC-07** | Navigating to History | Mobile User | FR-04 | **IMPLEMENTED** |
| **UC-08** | Navigating to Dashboard | Mobile User | FR-03, FR-04 | **IMPLEMENTED** |
| **UC-09** | Navigating to Settings | Mobile User | FR-04 | **IMPLEMENTED** |
| **UC-10** | Async header trigger | Flutter app | FR-07 | **IMPLEMENTED** |
