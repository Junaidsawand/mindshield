# Chapter 12 — Testing, Validation & Quality Assurance

This chapter describes the verification, validation, and testing strategy implemented across MindShield's mobile and server applications. It details software correctness tests, integration/API tests, machine learning performance validation, and localized regression gates.

---

## 12.1 Software Testing vs. Machine Learning Validation

MindShield enforces a clear distinction between software correctness testing and machine learning validation:
* **Software Correctness Testing (Deterministic):** Evaluates whether the system functions as designed (e.g. BroadcastReceivers execute intents, Pydantic inputs are validated, and SQLite parameters are bound correctly). Success is binary (Pass/Fail).
* **Machine Learning Validation (Statistical):** Evaluates the generalization performance of trained models on out-of-distribution datasets (e.g., measuring accuracy, precision, recall, and false positive rates on Pakistani SMS). Success is measured using statistical metrics.

These two evaluation domains must be kept separate to ensure that system correctness is not inferred from model classification accuracy.

---

## 12.2 Testing Philosophy & Architecture

MindShield’s testing strategy is structured as a testing pyramid:

```
                      [ML Evaluation & Domain Generalization]
                         (statistical metrics on test splits)
                                         │
                                         ▼
                            [ML Regression Gates]
                           (test_ml_regression_v3.py)
                                         │
                                         ▼
                             [System Integration]
                          (Dio HTTP, endpoint routers)
                                         │
                                         ▼
                            [Component & Providers]
                           (inbox, database migrations)
                                         │
                                         ▼
                             [Unit Correctness Layer]
                           (validators.py, normalizers)
```

---

## 12.3 Backend Unit Testing (pytest)

The Python backend uses `pytest` for unit testing, covering validators, loaders, and services.

### Table 12.2 — Backend Unit Tests

| Test File | Component Scope | Primary Test Cases | Expected Behavior | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| **`test_validators.py`** | `validators.py` | Contains URL, urgency language, credentials, and financial key regex checks. | Flags matched indicators; NFKC normalization matches ASCII. | **PASS** |
| **`test_health.py`** | `health.py` (Router) | `/health` endpoint response status structure. | Returns 200 OK with `model_loaded` status. | **PASS** |
| **`test_inference_service.py`** | `inference_service.py` | Primary loader runtime crash recovery and fallback path triggers. | Redirects failed model predictions to `MockModelLoader`. | **PASS** |
| **`test_model_loader_factory.py`** | `model_loader.py` | Loader instantiation via factory keys (`"mock"`, `"huggingface"`). | Spawns subclass instance matching requested backend. | **PASS** |
| **`test_model_loader_real.py`**| `model_loader.py` | Weight loading, tokenizer init, and CPU/GPU device allocations. | DistilBERT transformer processes raw text tokens. | **PASS** |
| **`test_preprocessing_pipeline.py`**| `nlp/pipeline.py` | Text normalizations (Porter stemming, stopword stripping). | Output maps to expected base word stems. | **PASS** |

**Implementation Evidence:**
* **Test Directory:** [`backend/tests/`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/tests)
* **Verify:** Run command `pytest` to execute all 42 tests.

---

## 12.4 Validation & API Routing Testing

* **Validation Limits:** Tested in `test_validators.py`. Rejects whitespace strings, characters $<3$ or $>2,000$, and purely numeric strings (preventing bare OTP classifications).
* **Router Routing:** Tested in `test_analysis.py`. Submitting valid payloads returns `HTTP 200` with the envelope structure `APIResponse[AnalysisResult]`, while validation failures trigger `HTTP 422` or `HTTP 400`.

### Table 12.4 — API Routing Tests

| Endpoint Route | HTTP Method | Input Payload | Expected HTTP Code | Expected Schema |
| :--- | :--- | :--- | :---: | :--- |
| **`/api/v1/analyze`** | `POST` | Valid SMS text | **`200 OK`** | `APIResponse[AnalysisResult]` |
| **`/api/v1/analyze`** | `POST` | Whitespace or empty string | **`422 Unprocessable`** | JSON Validation details |
| **`/api/v1/analyze`** | `POST` | Purely numeric string ("1234") | **`400 Bad Request`** | JSON Business error details |
| **`/api/v1/analyze/status`**| `GET` | None | **`200 OK`** | `APIResponse[dict]` |

---

## 12.5 Local Database & Migration Testing

The mobile client database queries are validated in `dashboard_provider_test.dart`:
* **CRUD Verification:** Verifies inserting, updating, and deleting messages inside `sms_messages` using parameterized SQL statements.
* **Migration Verification:** Verifies upgrading `mindshield.db` from version 1 to version 2, checking that the deletion query successfully removes seed mockup records (`msg_001` through `msg_012`).

**Implementation Evidence:**
* **Source File:** [`frontend/test/dashboard_provider_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/dashboard_provider_test.dart)

---

## 12.6 Frontend State & Service Testing

### Table 12.3 — Frontend Tests

| Dart Test File | Component tested | Responsibility | Execution Result |
| :--- | :--- | :--- | :---: |
| **`analysis_service_test.dart`**| `AnalysisService` | Validates JSON payload parsing, Dio timeouts, retry loop execution, and database updates. | **PASS** |
| **`api_analysis_repository_test.dart`**| `ApiAnalysisRepository`| Validates country prefix extraction and parsing, and checks that null carrier and line type chips are hidden. | **PASS** |
| **`dashboard_provider_test.dart`**| `DashboardProvider` | Queries total messages, safe counts, and spam counts from SQLite. | **PASS** |
| **`widget_test.dart`** | `MindShieldApp` | Evaluates basic smoke tests to ensure startup views compile and mount. | **PASS** |

**Implementation Evidence:**
* **Test Directory:** [`frontend/test/`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test)

---

## 12.7 ML Performance & Baseline Comparison

The machine learning metrics are verified against the raw metadata logs:

### Table 12.7 — ML Evaluation Metrics (UCI In-Domain Test Split)

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM (`linear_svm_count`)**| **98.25%** | **98.25%** | **87.50%** | **92.56%** | 99.08% | **0.19 MB** |
| **DistilBERT (`distilbert-base`)**| 97.86% | 96.49% | 85.94% | 90.91% | **99.51%** | 255.42 MB |

### Confusion Matrix Invariants:
* **Linear SVM:** $\text{TP} = 56$, $\text{TN} = 450$, $\text{FP} = 1$, $\text{FN} = 8$ (Total: 515 test samples).
* **DistilBERT:** $\text{TP} = 55$, $\text{TN} = 449$, $\text{FP} = 2$, $\text{FN} = 9$ (Total: 515 test samples).

### Mathematical Definitions:

$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}} \quad \text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

$$\text{F1-Score} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

$$\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$

In smishing filtering, **False Positives are critical**. Flagging a bank transaction alert as a scam blocks the message, disrupting the user's workflow. Therefore, precision must be prioritized alongside recall.

---

## 12.8 Pakistani Domain Generalization & Regression Gates

The model's generalization capabilities are validated using **regression testing**:
* **Test File:** [`test_ml_regression_v3.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/tests/test_ml_regression_v3.py)
* **Scope:** Evaluates models against 14 templates representing local bank alerts, Roman Urdu messages, and benign/malicious shortened links.
* **Regression Gate:** The candidate model must achieve a False Positive Rate of **$\le 2.0\%$** and pass **14/14** regression cases to be promoted to production.

### Promotion Gate Audit:
* **Model version:** `distilbert-pakscam-v3`
* **Result:** Achieved $3.45\%$ combined HAM FPR and passed 13/14 regression cases.
* **Failure Point:** Misclassified `zong_engage_prize_lang` containing the Roman Urdu phrase `"jeeto bade inaam"` ("win big prizes") as phishing (99.29% confidence).
* **Promotion Decision:** **Rejected.** The model failed the promotion gate and remains in quarantine. The production system continues to load `distilbert-pakscam-v1` until this regression is resolved.

---

## 12.9 Mock and Fallback Pipeline Verification

The `MockModelLoader` is tested in `test_inference_service.py` to ensure high availability:
* **Failure Trigger:** If the primary transformer loader throws loading exceptions, the service redirects queries to the mock engine.
* **Response Output:** The mock response is flagged with `fallback_mode = true` and `mock_mode = true`, notifying the Flutter client to display a disclaimer warning.

---

## 12.10 Technical Quality Assurance Workflow

The quality assurance pipeline is structured as follows:

```
[Code modifications] ──► [pytest Unit & Preprocessing checks]
                                   │
                                   ▼
                      [test_ml_regression_v3.py checks]
                                   │
                                   ▼
                      [Flutter Dart unit & provider checks]
                                   │
                                   ▼
                      [Verify compilation & metadata updates]
```

---

## 12.11 Testing Limitations

* **No Production-scale Load Testing:** The API server has not been profiled under high concurrent request volumes.
* **No Native Android Sandbox Testing:** Native background permissions are validated manually via physical debugging; automated integration tests for `SmsReceiver.kt` are not implemented.
* **Unmeasured Coverage:** Code coverage percentage was not formally measured in the current repository.
* **Battery & Resource Profiling:** *Mobile battery consumption under continuous SMS background events has not been experimentally profiled in the current implementation.*

---

## 12.12 Chapter Summary

This chapter has detailed the testing and quality assurance strategies implemented in MindShield. By separating software unit tests from machine learning validation and enforcing regression gates, the testing pipeline prevents regression issues from impacting production builds.

The research conclusions, limitations, and recommendations for future phases are detailed in **Chapter 13 — Conclusions & Recommendations**.

---

## Testing Verification Summary

### Strongly Verified Tests (Proven):
* 42 backend Python tests (covering validators, routers, fallback lifecycles, and regression templates).
* 15 frontend Dart tests (covering Dio client requests, migrations, and model parsing).
* Model performance metrics and confusion matrices matching repository metadata logs.
* Quarantined status of `distilbert-pakscam-v3` due to failing the promotion gate.

### Missing Tests / Limitations:
* **No automated Android Native UI tests:** Lacks espresso/robolectric coverage.
* **No resource profiling:** Battery, RAM, and network consumption are unprofiled.
* **No performance load testing:** Server behavior under high request load is unmeasured.
