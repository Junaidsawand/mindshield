# Chapter 3 — Problem Analysis, Requirements & System Specification

This chapter provides a detailed problem analysis, system requirement specification, and design constraints matrix for the MindShield platform. It establishes the threat landscape and use case boundaries, and outlines the system parameters for both native mobile components and remote machine learning modules.

---

## 3.1 Introduction

Engineering a mobile security system that uses remote machine learning models requires a structured specification process. System failures can stem from poor model generalization (Scope B) or implementation errors in data transmission, persistence, or process lifecycles (Scope A). 

This chapter:
* Analyzes the localized smishing threat model in Pakistan.
* Compares existing system limitations with the proposed MindShield architecture.
* Identifies system stakeholders, threat scenarios, and functional/non-functional requirements.
* Defines the machine learning, data engineering, mobile, backend, explainability, security, and privacy requirements.
* Maps requirements to implemented source code components.

---

## 3.2 Problem Analysis

### 3.2.1 SMS Smishing Threat Model
The SMS protocol lack native identity verification or message integrity controls. Attackers exploit these gaps by sending fraudulent text messages that mimic legitimate services to harvest credentials, extract personal identifier data (PII), or initiate unauthorized financial transfers.

### 3.2.2 Legitimate SMS vs. Malicious SMS
In localized markets, legitimate transactional receipts and marketing updates frequently contain the same features that models associate with phishing:
* Shortened URLs (e.g. `bit.ly`, `tiny.cc`) directing users to bill payment or receipt download pages.
* Urgent imperative statements (e.g., `"verify now to avoid block"`).
* Text formats asking for credential submissions.

The similarity in features between legitimate receipts and smishing campaigns creates a classification challenge.

### 3.2.3 Domain Shift Problem
SMS threat classifiers are typically trained on Western corpora (like the UCI SMS Spam Collection). When deployed in Pakistan, these classifiers encounter a different feature distribution:
* Transliterated Urdu (Roman Urdu) written in Latin characters.
* Multilingual code-switched structures.
* Unique local banking templates and public welfare program names (e.g., BISP).

This difference in feature distribution causes models to fail to generalize, resulting in high false positive rates when processing legitimate local SMS.

### 3.2.4 Pakistani SMS Characteristics
The local SMS environment is characterized by:
1. **No Standard Roman Urdu Spellings:** Words are phonetically transliterated without standardized dictionary constraints (e.g. the word `"account"` can be written as `"acount"`, `"acnt"`, or `"a/c"`).
2. **Code-Switching:** English nouns and verbs are mixed with Urdu structures within single text strings.
3. **High Density of Transaction Alerts:** Due to limited internet penetration, local users rely on SMS notifications for bank transactions, utility alerts, and mobile wallet updates.

### 3.2.5 Hard-Negative Problem
Legitimate local banking receipt messages act as **hard negatives**. Because these messages contain numbers, transaction codes, and URLs, models that rely on simple keyword shortcuts frequently misclassify them as malicious.

### 3.2.6 Explainability Requirement
A binary classification output (e.g., displaying "Scam" or "Safe") does not provide sufficient context for the user. To establish trust, the application must identify and display the specific indicators (e.g. credential requests, urgency, link presence) that contributed to the classification.

### 3.2.7 Mobile Integration Problem
Deep learning models (like DistilBERT) are too computationally expensive to run directly on-device without causing latency or battery drain. Therefore, the system must use a hybrid architecture: running background native interception on-device, and executing inference on a remote backend.

---

## 3.3 Existing-System Limitations

Based on the literature surveyed in Chapter 2, current systems exhibit several limitations:
1. **English-Centric Benchmarking:** Existing research evaluates classifiers on generic English corpora, neglecting localized transliterated dialects like Roman Urdu.
2. **Shortcut Bias:** Systems fail to evaluate model performance on legitimate transactional hard negatives, resulting in high false alarm rates.
3. **High Explainability Latency:** Existing XAI implementations (like LIME/SHAP) add significant computational overhead, making them unsuitable for real-time mobile API constraints.
4. **Isolated Evaluation:** Most studies evaluate models offline in Jupyter notebooks, without developing mobile integration layers to verify end-to-end background processing.

---

## 3.4 Proposed System Concept

MindShield resolves these limitations using a hybrid system architecture:

```
[Incoming SMS] ──► [Android BroadcastReceiver] ──► [Write to SQLite Cache]
                                                          │
                                                          ▼
                                                  [MethodChannel]
                                                          │
                                                          ▼
                                            [SmsBackgroundService (Dart)]
                                                          │
                                                          ▼ (Dio POST /api/v1/analyze)
                                                [FastAPI Backend Tier]
                                                          │
                                      ┌───────────────────┴───────────────────┐
                                      ▼                                       ▼
                            [DistilBERT Inference]                   [HFA Indicators Engine]
                                      │                                       │
                                      └───────────────────┬───────────────────┘
                                                          │
                                                          ▼ (JSON Response Payload)
                                                    [Flutter Client]
                                                          │
                                                          ▼ (UI Highlights & Warn Card)
                                                    [User Screen]
```

This architecture separates native on-device interception and caching from remote machine learning classification.

---

## 3.5 Stakeholder Analysis

The system supports three primary stakeholder roles:

* **1. Mobile User (SMS Recipient):**
  * *Needs:* Real-time, low-latency background SMS threat classification and explainable warnings.
  * *Security/Privacy Concern:* SMS messages must be processed securely, and contact lists must remain private.
* **2. Developer / System Administrator:**
  * *Needs:* A stable backend deployment, Pydantic request validation, and API logging.
  * *Security/Privacy Concern:* Prevention of server resource exhaustion and model replacement attacks.
* **3. Security Researcher / Evaluator:**
  * *Needs:* Reproducible training runs, regression gates, and comparison baselines.
  * *Security/Privacy Concern:* Data leakage during validation splits.

---

## 3.6 Threat Scenarios

The following scenarios represent common smishing vectors targeted by MindShield:

### Table 3.6 — Target Threat Scenarios

| Threat Vector | Representative Scenario | Potential Victim Action | Security Consequence | Detection Relevance |
| :--- | :--- | :--- | :--- | :--- |
| **Credential Harvesting** | SMS claiming a bank account is blocked, directing the user to a cloned login portal link. | User enters password, username, and OTP on the fake website. | Account compromise and identity theft. | Highly relevant; triggers URL and credential request HFA indicators. |
| **Urgent Account Verification** | SMS urging the user to verify mobile wallet registration to prevent immediate service suspension. | User clicks link and submits mobile PIN. | Financial asset extraction. | Triggers urgency language and credentials indicators. |
| **Lottery / Prize Scam** | SMS claiming the user won a cash prize, urging them to call a number or transfer registration fees. | User calls number and transfers money to the fraudster. | Financial loss. | Triggers prize language indicators. |
| **Roman Urdu Impersonation** | Social engineering message in Roman Urdu (*"BISP ki taraf se 25000 rupay"*). | User calls the sender to claim cash. | Financial fraud. | Triggers localized dataset mapping. |

---

## 3.7 Functional Requirements

The functional requirements specify the actions the system must perform:

### Table 3.7 — Functional Requirements Specification

| ID | Requirement Name | Description | Priority | Verification Method |
| :--- | :--- | :--- | :---: | :--- |
| **`FR-01`** | **Background Interception**| The app must intercept incoming SMS broadcasts at the OS level using native Android components. | **High** | Verify receiver logs in `SmsReceiver.kt`. |
| **`FR-02`** | **Local Storage Cache** | Intercepted messages must be cached in a local database before sending for analysis. | **High** | Verify insertions inside SQLite `mindshield.db`. |
| **`FR-03`** | **Inference Request** | The client must submit the SMS payload to the remote FastAPI backend over HTTP. | **High** | Verify Dio POST requests inside `analysis_service.dart`. |
| **`FR-04`** | **Threat Classification**| The server must run binary threat classification, mapping text to `safe` or `phishing`. | **High** | Verify DistilBERT outputs in `inference_service.py`. |
| **`FR-05`** | **HFA Indicators** | The server must run parallel regex checks to return matched feature indicators and weights. | **High** | Verify indicator lists inside `validators.py`. |
| **`FR-06`** | **Attack Categorization** | The client must run rule-based categorization to map threat verdicts to specific attack vectors. | **High** | Verify categorization maps in `api_analysis_repository.dart`. |
| **`FR-07`** | **In-App Inbox** | The client must display a thread-based SMS inbox. | **High** | Verify presentation views under the `inbox/` feature folder. |
| **`FR-08`** | **Spam Isolation** | Malicious messages must be automatically quarantined in a separate Spam folder. | **High** | Verify queries where `is_spam = 1` inside `SpamScreen`. |
| **`FR-09`** | **Heuristic Visuals** | The analysis view must display matched HFA indicators and highlight related substrings. | **High** | Verify highlights rendering in `AnalysisScreen`. |
| **`FR-10`** | **Settings Config** | The client must allow configuration of the remote API base URL. | **Medium**| Verify settings state changes in `SettingsScreen`. |

---

## 3.8 Non-Functional Requirements

The non-functional requirements specify the quality constraints of the system:

### Table 3.8 — Non-Functional Requirements

| ID | NFR Category | Target Target Constraint | Actual Prototype State | Measured Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **`NFR-01`** | **Performance** | Return analysis verdicts within the measured prototype latency envelope (no formal SLA threshold established; bounded by prototype performance of mean 57.62 ms, p95 72.34 ms). | **Met:** Average server inference latency is 57.62 ms. | [`v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json) (line 334) |
| **`NFR-02`** | **Reliability** | The system must handle primary server errors using local caches. | **Met:** Uses `MockModelLoader` as a fallback inference engine. | `inference_service.py` (lines 114-135) |
| **`NFR-03`** | **Availability** | Remote server is required for full ML threat analysis. | **Constraint:** Displays "Pending" loader state when offline. | `analysis_service.dart` |
| **`NFR-04`** | **Security** | Inputs must be validated to prevent buffer issues. | **Met:** Backend validates text length (3-2,000 chars) via Pydantic. | `analysis.py` (schemas) |
| **`NFR-05`** | **Privacy** | Sensitive user data must not be permanently stored on the server. | **Met:** Server processes messages transiently in memory. | `analysis_service.py` |

---

## 3.9 Machine Learning Requirements

* **MLR-01: Binary classification:** The core model must output a probability distribution mapping inputs to binary classes (0 = safe, 1 = phishing).
* **MLR-02: Baseline Comparison:** The model must be benchmarked against a classical pipeline (Linear SVM).
* **MLR-03: Localization:** The model must be evaluated on local Pakistani SMS structure.
* **MLR-04: Regression Gate:** Model updates must pass regression testing with a False Positive Rate (FPR) of $\le 2.0\%$ on Pakistani transactional HAM.

Accuracy alone is an insufficient metric for smishing detection. If a model has 98% accuracy but misclassifies legitimate bank transaction alerts as spam, it disrupts user access. Thus, **False Positive Rate (FPR)** and **Precision** must be prioritized.

---

## 3.10 Dataset Requirements

* **UCI SMS Spam Collection:** Raw corpus must be cleaned of null values and deduplicated to generate clean train, validation, and test splits.
* **PakScam-SMS localized corpus:** Must contain templates representing local bank alerts, telecom promotions, and Roman Urdu spam.
* **Template-family separation:** To prevent data leakage, messages must be split by template family rather than random division.

---

## 3.11 Mobile Application Requirements

* **Interception Hook:** Must register a native Android BroadcastReceiver in the manifest.
* **Local persistence:** Must use SQLite (`mindshield.db`) to cache messages.
* **UI Views:** Must provide dashboard metrics, thread-based inbox, spam folder, and analysis detail views.
* **API Client:** Must use a pre-configured Dio instance with set connection and receive timeouts.
* **Inference constraint:** The mobile client does **not** run the DistilBERT model locally.

---

## 3.12 Backend Requirements

* **Framework:** Python-based FastAPI backend.
* **APIs:** Versioned API endpoints (e.g. `/api/v1/analyze`).
* **Request Validation:** Strict type checking using Pydantic schemas.
* **Model Management:** Centralized model loading lifecycle and error fallback routing.

---

## 3.13 Explainability Requirements

* **HFA Indicators:** The server must return matched indicators (e.g. `urgency_language`, `url_detected`) and weights (`low`, `medium`, `high`, `critical`).
* **Visual Rendering:** The client must display the verdict, confidence score, and highlight matching terms locally in the UI.

*LIME/SHAP dynamic local surrogate models are not supported in the current implementation.*

---

## 3.14 Security Requirements

* **Input Validation:** Reject empty inputs and validate message lengths.
* **SQL Parameterization:** Use parameterized queries in `sqflite` to prevent SQL injection.
* **Permission control:** Limit permissions to those requested in `AndroidManifest.xml`.
* **Security Gaps:** The prototype lacks HTTPS encryption, API authentication tokens, rate limiting, and local database encryption.

---

## 3.15 Privacy Requirements

* **Local Contact Resolution:** Query contact details on-device using native APIs, preventing contact lists from leaking to the server.
* **Transient backend processing:** Process messages in memory on the backend with zero server-side retention.

---

## 3.16 Use Cases

* **UC-05: Analyze SMS:**
  * *Actor:* Mobile User / Background Service.
  * *Preconditions:* SMS received and written as `'pending'` in SQLite; network connection available.
  * *Main Flow:* Client sends POST request to `/api/v1/analyze`; server runs inference and HFA; returns JSON; client updates local database and UI.
  * *Alternative Flow:* Network timeout; client retries up to 2 times; if connection fails, message remains `'pending'`.
  * *Postconditions:* Message state updated in SQLite (`safe` or `phishing`); Spam folder updated if verdict is malicious.

---

## 3.17 System Constraints

* **Remote Inference Dependency:** SMS analysis requires an active internet connection to query the FastAPI backend.
* **No On-Device ML:** DistilBERT model weights are loaded and computed exclusively on the backend server.
* **No Official LIME:** Explainability is based on HFA rule checks, not dynamic local surrogate models.
* **No API Authentication / Rate-Limiting:** APIs run on open ports without access tokens or rate limiting.
* **No Database Encryption:** Local SQLite databases are stored in plaintext.
* **No Local Notifications:** Spam alerts are handled within the app UI; background push notifications are not implemented.

---

## 3.18 Assumptions

* **Device Permission:** The user grants necessary system permissions (e.g. `RECEIVE_SMS`, `READ_SMS`).
* **Network Connectivity:** The device can reach the FastAPI backend port.
* **Model Weight Availability:** The model weights exist and are accessible on the backend server on startup.

---

## 3.19 Requirement-to-Component Traceability

### Table 3.19 — Requirement-to-Component Traceability

| ID | Targeted Requirement | Implemented Component | Source Code File | Verification Test Reference | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **`FR-01`** | **SMS Interception** | `SmsReceiver` | `SmsReceiver.kt` | Manual verification (ADB broadcast test) | **IMPLEMENTED** |
| **`FR-02`** | **Local Cache** | `DatabaseHelper` | `database_helper.dart` | `dashboard_provider_test.dart` | **IMPLEMENTED** |
| **`FR-03`** | **Inference Request**| `AnalysisService` (Dart) | `analysis_service.dart` | `analysis_service_test.dart` | **IMPLEMENTED** |
| **`FR-04`** | **Model Inference** | `InferenceService` | `inference_service.py` | `test_inference_service.py` | **IMPLEMENTED** |
| **`FR-05`** | **HFA Indicators** | `compute_message_features`| `validators.py` | `test_validators.py` | **IMPLEMENTED** |
| **`FR-06`** | **API Health** | `/health` route | `main.py` | `test_health.py` | **IMPLEMENTED** |

---

## 3.20 Scope Boundary

### Table 3.20 — Scope Boundary Matrix

| In Scope (Implemented in Prototype) | Out of Scope (Future Work / FYP2) |
| :--- | :--- |
| Background SMS interception on Android. | On-device model execution (e.g. ONNX/TFLite). |
| SQLite message persistence and migrations. | Local database encryption (SQLCipher). |
| Remote binary DistilBERT classification. | True LIME token attribution. |
| Heuristic Feature Attribution (HFA) checks. | API token authentication & rate limiting. |
| Remote FastAPI backend server routes. | System notifications & background SMS blocking. |

---

## 3.21 Chapter Summary

This chapter has defined the problem analysis, stakeholder roles, functional/non-functional requirements, use cases, and system constraints for MindShield. By establishing the boundaries between implemented components and future work, this specification forms the design foundation for the architecture detailed in **Chapter 4 — System Architecture & Design**.
