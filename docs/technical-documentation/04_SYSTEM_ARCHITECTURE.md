# Chapter 4 — System Architecture & Design

This chapter describes the system architecture, component dependencies, data boundaries, and communication contracts implemented in MindShield. It details the hybrid architecture linking local Android interception components with a remote FastAPI-based deep learning inference engine.

---

## 4.1 Architectural Overview

MindShield utilizes a hybrid mobile-server architecture designed to balance local message persistence with server-side deep learning classification:

```
[Android Operating System]
           │ (SMS Received Broadcast Intent)
           ▼
[SmsReceiver (BroadcastReceiver)]
           │ (1. Write Pending SMS to local db)
           ├──────────────────────────────────────────────┐
           ▼                                              ▼
    [SQLite Persistence]                        [Local Broadcast Intent]
      (mindshield.db)                                     │
           ▲                                              ▼
           │ (Query / Sync)                     [MainActivity (Activity)]
           │                                              │
           │                                              ▼ (MethodChannel invocation)
           │                                    [SmsBackgroundService (Dart)]
           │                                              │
           │ (3. Write Final Verdict)                     ▼
           └────────────────────────────────────[AnalysisService (Dart Client)]
                                                          │
                                                          ▼ (HTTP POST /api/v1/analyze)
                                                [FastAPI Backend Application]
                                                          │
                                                          ▼ (RoutingThin Controller)
                                                [AnalysisService (Python Service)]
                                                          │
                                                          ├──────────────────────────────┐
                                                          ▼ (HFA Rule Engine)            ▼ (InferencePass)
                                                 [Validators (Regex/Keywords)]  [InferenceService (ML Core)]
                                                          │                              │
                                                          ▼                              ▼
                                                 [Security Indicators]          [DistilBERT Model / Weights]
                                                          │                              │
                                                          └──────────────┬───────────────┘
                                                                         │
                                                                         ▼
                                                              [AnalysisResult Payload]
                                                                         │
                                                                         ▼ (JSON HTTP Response)
                                                              [Flutter Presentation UI]
```

---

## 4.2 Architectural Style

MindShield implements four primary software architectural styles:

1. **Client-Server Architecture:** The frontend mobile application (Flutter client) acts as a consumer requesting CPU-heavy natural language processing (NLP) classifications from the remote backend (FastAPI application server).
2. **Layered Architecture:** The FastAPI backend is structured into clear, decoupled horizontal layers:
   - **Routing Layer (薄控制器/Thin Controllers):** Exposes HTTP paths and manages serialization.
   - **Service Layer (Orchestration):** Validates input, sanitizes strings, and coordinates inference steps.
   - **Core Engine (Inference & Loaders):** Manages model weights, loading contexts, and fallback pathways.
3. **Feature-Based Flutter Organization:** The frontend is partitioned into domain-specific features (e.g. `inbox`, `analysis`, `history`, `settings`), isolating presentation widgets, repository maps, and state providers from unrelated domains.
4. **Strategy / Adapter Pattern (Model Loaders):** The backend defines an abstract `BaseModelLoader` class. Concrete implementations (`HuggingFaceModelLoader`, `MockModelLoader`, `PlaceholderModelLoader`) conform to this contract, allowing runtime model-loader swapping.

**Implementation Evidence:**
* **Model Loader Class:** [`backend/app/core/model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py)
* **Factory Class:** `ModelLoaderFactory` (lines 530-576)

---

## 4.3 System Boundaries

The application enforces strict data boundaries:

### 1. Mobile Boundary (On-Device Client)
* **Components:** Android `SmsReceiver.kt`, Flutter application, and `SQLite` local storage.
* **Invariant:** Raw SMS payload content, sender logs, and resolved contact metadata are persisted locally within this boundary. Message bodies are sent externally only to request classification.

### 2. Backend Boundary (FastAPI Server)
* **Components:** Uvicorn web server, FastAPI application factory, Pydantic schemas, and PyTorch ML inference context.
* **Invariant:** Message content is received in memory, processed through DistilBERT inference, and discarded. The server does not maintain databases or logs containing message text.

### 3. Data Boundary
* **SQLite:** Shared local database file (`mindshield.db`) accessed by Kotlin (interception writes) and Dart (UI reads/updates).
* **Remote:** PyTorch model weights (`distilbert-base-uncased` fine-tuned checkpoints) loaded into memory on server startup.

### 4. External Communication Boundary
* **Protocol:** HTTP REST APIs over TLS (port 8000 in local debug environments).
* **Payload:** Structured JSON objects representing `AnalysisRequest` and `AnalysisResult` Pydantic schemas.

---

## 4.4 Component Architecture

### Table 4.1 — System Component Inventory

| Component Name | Execution Layer | Dependency Scope | Source File Reference |
| :--- | :--- | :--- | :--- |
| **`SmsReceiver`** | Android Native | `Telephony.Sms.Intents`, `SQLite` | [`SmsReceiver.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/SmsReceiver.kt) |
| **`MainActivity`** | Android Native | `MethodChannel`, `ContactsContract` | [`MainActivity.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/MainActivity.kt) |
| **`SmsBackgroundService`**| Flutter Dart | `MethodChannel`, `DatabaseHelper` | [`sms_background_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/sms_background_service.dart) |
| **`DatabaseHelper`** | Flutter Dart | `sqflite`, `path` | [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart) |
| **`AnalysisService (Client)`**| Flutter Dart | `Dio`, `DatabaseHelper` | [`analysis_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/analysis_service.dart) |
| **`AnalysisRouter`** | FastAPI Backend | `AnalysisService (Server)`, `Depends`| [`v1/analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/routers/v1/analysis.py) |
| **`AnalysisService (Server)`**| FastAPI Backend | `InferenceService`, `validators` | [`analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) |
| **`InferenceService`** | FastAPI Backend | `BaseModelLoader` | [`inference_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/inference_service.py) |
| **`HuggingFaceModelLoader`**| FastAPI Backend | `transformers`, `torch` | [`model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py) |

---

## 4.5 SMS Ingestion Pipeline

When a new SMS arrives, it flows through the following pipeline:

1. **Interception:** The Android OS triggers `SmsReceiver.onReceive` upon catching the `SMS_RECEIVED_ACTION` broadcast intent.
2. **Local Write:** `SmsReceiver` extracts the message fields and inserts a new message into SQLite `mindshield.db` with `ai_status = "pending"`, ensuring data preservation if the Flutter app is suspended.
3. **Local Intent:** `SmsReceiver` sends a local broadcast (`com.mindshield.SMS_RECEIVED`) within the app domain.
4. **Dart Notification:** `MainActivity` catches the broadcast and sends a MethodChannel call `onSmsReceived` containing the message payload back to Dart.
5. **Background Sync:** In Dart, `SmsBackgroundService` handles `onSmsReceived`, notifies UI providers to show the "Analyzing..." state, and triggers `AnalysisService.instance.analyzeMessage`.
6. **API Analysis:** `AnalysisService` submits the SMS to the FastAPI backend `/api/v1/analyze` endpoint.
7. **Verdicts & Update:** The server returns the final threat analysis JSON payload. `AnalysisService` updates the message's database columns with classification metadata and changes `ai_status` to the final verdict (`safe`, `suspicious`, or `scam`).

---

## 4.6 MethodChannel Communication

The bridge between Android and Dart uses a designated platform channel:

* **Channel Name:** `com.mindshield/sms_receiver`
* **Inbound Call Method:** `onSmsReceived`
* **JSON Arguments:**
  - `id`: String (UUID)
  - `sender`: String (raw number or alphanumeric code)
  - `body`: String (message text)
  - `timestamp`: Long (epoch milliseconds)
* **Lifecycle Behavior:** Registered during `MainActivity.onCreate` using `receiver_exported` permissions on Android 13+ to intercept SMS intents in the background.

**Implementation Evidence:**
* **Source File:** `MainActivity.kt` (lines 21-33, 149-166) and `sms_background_service.dart` (lines 12, 40-60).

---

## 4.7 Local Database Architecture

SQLite holds a single table `sms_messages` managed via the `sqflite` Dart wrapper:

```
┌──────────────────────────────────────────────┐
│                 sms_messages                 │
├──────────────────────────────────────────────┤
│ id: TEXT (PK)                                │
│ sender: TEXT                                 │
│ body: TEXT                                   │
│ timestamp: INTEGER                           │
│ ai_status: TEXT                              │
│ is_read: INTEGER                             │
│ confidence_score: REAL                       │
│ detected_threats: TEXT                       │
│ is_spam: INTEGER                             │
│ spam_risk_level: TEXT                        │
│ spam_attack_type: TEXT                       │
│ spam_status: TEXT                            │
│ quarantined_at: INTEGER                      │
└──────────────────────────────────────────────┘
```

*There are no foreign-key relationships in this table schema; all message logs and metadata are stored in flat rows.*

---

## 4.8 Message State Lifecycle

Messages flow through the following state transitions:

```
[SMS Arrived] ──► [pending] ──► [analyzing] ──► [safe]
                                    │
                                    ├──────────► [suspicious (medium risk)]
                                    │
                                    └──────────► [scam (high/critical risk)]
```

### Table 4.6 — Message Lifecycle States

| State | `ai_status` | `is_spam` | `spam_status` | Description |
| :--- | :--- | :---: | :--- | :--- |
| **Pending** | `'pending'` | 0 | `null` | SMS intercepted; awaiting API backend response. |
| **Safe** | `'safe'` | 0 | `null` | Verified benign (Ham). Preserved in the inbox. |
| **Suspicious**| `'suspicious'`| 1 | `'quarantined'`| Evaluated as suspicious (e.g. low-confidence spam). |
| **Scam** | `'scam'` | 1 | `'quarantined'`| Verified high-threat smishing. Blocked in Spam. |

---

## 4.9 Flutter Application Architecture

The mobile client is built on **Feature-based layered development** using **Provider / ChangeNotifier** for state management:

* **Presentation Layer:** Contains stateless/stateful Flutter screens (e.g., [`analysis_screen.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/analysis_screen.dart)) consuming providers.
* **State/Provider Layer:** Classes subclassing `ChangeNotifier` (e.g., `InboxProvider`, `DashboardProvider`) query the SQLite database and call analysis services, triggering `notifyListeners()` to rebuild widgets when state changes.
* **Network/Client Layer:** Dio HTTP configuration root handling header assemblies and request lifecycle.

**Implementation Evidence:**
* **Provider Example:** [`frontend/lib/features/dashboard/presentation/providers/dashboard_provider.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/dashboard/presentation/providers/dashboard_provider.dart)

---

## 4.10 API Client Architecture

The mobile frontend executes HTTP requests using the **Dio** client library:
* **Timeouts:** Configured with a `connectTimeout` of 10 seconds and `receiveTimeout` of 15 seconds.
* **Retry Loop:** `AnalysisService` wraps requests in a retry loop that retries up to **2 times** on network loss using exponential backoff (e.g., waiting $300\text{ms} \times \text{attempt}$).
* **Serialization:** Parses JSON strings into strongly typed Dart classes, catching model loading validation errors.

---

## 4.11 FastAPI Backend Architecture

The Python server acts as the composition root, managing startup lifespans, logging, routing, and inference services:

* **Lifespan Manager:** Resolves Settings configurations, instantiates `BaseModelLoader` concrete targets via `ModelLoaderFactory`, loads model weights, runs warm-up passes, and instantiates the `InferenceService`.
* **thin Controllers:** Routers validate JSON inputs against Pydantic request schemas and pass variables to `AnalysisService`.
* **CORS Middleware:** Enabled for request traffic mapping.

**Implementation Evidence:**
* **composition root:** `main.py` (lifespan method, lines 86-192).

---

## 4.12 API Endpoints

The API router exposes three primary endpoints:

### Table 4.4 — API Endpoints

| HTTP Method | Path Route | Description | Input Schema | Output Schema |
| :--- | :--- | :--- | :--- | :--- |
| **`GET`** | `/health` | Server operational status | None | `HealthStatus` |
| **`POST`** | `/api/v1/analyze` | Classify SMS message | `AnalysisRequest` | `APIResponse[AnalysisResult]` |
| **`GET`** | `/api/v1/analyze/status`| API v1 metadata & loaded model | None | `APIResponse[dict]` |

---

## 4.13 Backend Analysis Pipeline

When the server receives an analysis request, it executes the following steps:

```
[POST /api/v1/analyze] ──► [Input Validation] ──► [NFKC Normalisation]
                                                          │
                                                          ▼ (compute_message_features)
                                                [HFA Heuristics Extraction]
                                                          │
                                                          ▼ (inference_service.predict)
                                                [DistilBERT PyTorch Inference]
                                                          │
                                                          ▼ (post-processing mapping)
                                                [_build_indicators] ──► [JSON Response]
```

*Note: HFA rule-checking and model inference are executed **sequentially and synchronously** on the thread pool.*

---

## 4.14 Model Loader and Fallback Architecture

To ensure high availability, the server uses a **decoupled fallback loading architecture**:

* **Base Class:** `BaseModelLoader` enforces the interface lifecycles (`load()`, `predict()`, `health()`).
* **Fallback Activation:** If the primary loader (`HuggingFaceModelLoader`) fails to load weights during startup (e.g. due to missing files or GPU memory issues), the lifespan manager catches the exception and instantiates the `MockModelLoader`.
* **Transparency:** When a fallback prediction occurs, the prediction returns `fallback_mode: true` in its response payload.

---

## 4.15 Real Mode vs. Mock Mode

The system maintains two operational modes:

1. **Real Mode (`huggingface`/`distilbert`):** Loads the PyTorch tokenizers and model weights into memory, executing neural network inference.
2. **Mock Mode (`mock`):** Runs the text through regular expressions and keyword checks, returning categorical indicator lists and generating confidence scores in the range `[0.60, 0.97]` dynamically.

*`mock_mode: true` is included in all mock-engine responses, prompting the client UI to display a disclaimer warning.*

---

## 4.16 Inference Location

**The DistilBERT model does NOT run on the Android/Flutter mobile client.** All machine learning inference is executed on the remote FastAPI backend server.

### Architectural Implications:
* **Network Dependency:** The client app must have an active internet connection to analyze SMS messages.
* **Latency Overhead:** Analysis is subject to network latency (averaging ~57ms for inference, plus 100-200ms for HTTP transmission).
* **Privacy Boundary:** Message text must be transmitted across the network, requiring secure communication channels.

---

## 4.17 Security and Privacy Controls

MindShield implements the following security controls:
* **Local Sandboxing:** Database caches are stored in sandboxed partitions, inaccessible to other Android apps.
* **Local Contact Resolution:** Contact details are resolved locally in `MainActivity.kt` using native APIs; contact names are **never** transmitted to the remote backend.
* **In-Memory Analysis:** The FastAPI server processes messages in memory, discarding payloads immediately after response construction.

---

## 4.18 Failure and Recovery Flows

### Table 4.7 — Failure Handling

| Failure Vector | Trigger Condition | System Recovery Behavior |
| :--- | :--- | :--- |
| **API Backend Down** | HTTP 503 or connect timeout | Dio client triggers retries; if all fail, status remains `'pending'` in SQLite to re-sync later. |
| **Input Validation Failure**| Empty string or numeric OTP | API returns 422/400; client updates message to `'safe'` to prevent quarantine loops. |
| **Inference Engine Crash** | PyTorch unhandled exception | `InferenceService` catches exception, falls back to `MockModelLoader`, and logs warning. |

---

## 4.19 Architectural Design Trade-offs

### Table 4.8 — Architectural Trade-offs

| Architectural Decision | Advantages | Disadvantages |
| :--- | :--- | :--- |
| **Remote Server Inference** | - Small app package size (~40MB)<br>- Centralized model updates without app store releases | - Requires network connection<br>- Higher network transmission latency |
| **Local Broadcast Receiver**| - Captures SMS in the background<br>- Preserves data locally during app suspensions | - Dependent on OS-level Android permissions |
| **Stateless API** | - High server scalability<br>- Minimal user-data leakage risks | - Prevents multi-message contextual analysis |

---

## 4.20 Architectural Limitations

* **Offline Limitations:** SMS received while offline are kept as `pending` and cannot be analyzed until a connection is restored.
* **No Native Android Sandbox Bypass:** Interception depends on Android's permission model. If permission is revoked, the app cannot filter messages.
* **Stateless Explanations:** The explanations describe found indicators rather than mathematically tracing DistilBERT's internal decision weights.

---

## 4.21 Chapter Summary

This chapter has detailed the system architecture of MindShield. By decoupling native Android interception components from remote server-side DistilBERT classification engines, MindShield ensures background message capture and local data sandboxing.

The data structures, deduplication routines, and localized corpus versions processed by this architecture are detailed in **Chapter 5 — Data Engineering & Preprocessing**.

---

## Architecture Verification Summary

### Strongly Verified Implementation (Code Proven):
* Native background SMS interception (`SmsReceiver.kt`) and shared SQLite storage (`mindshield.db`).
* MethodChannel registration (`com.mindshield/sms_receiver`) and local broadcast invocation.
* Thin controller FastAPI architecture (`main.py` composition root) and thin routers (`routers/v1/analysis.py`).
* BaseModelLoader abstract pattern and InferenceService fallback recovery loops (`inference_service.py`).
* Parallel execution of HFA extraction and model inference.

### Partially Verified Implementation:
* Resource footprint profiles on production mobile hardware (not fully profiled).

### Resolved Documentation Contradictions:
* Explicitly clarified that **LIME is not mathematically implemented** (explainability relies on HFA).
* Clarified that **on-device ML inference is not implemented** (inference is remote).
* Clarified that **multi-class ML classification is not implemented** (model is binary).
