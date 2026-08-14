# MindShield — Software Requirements Specification (SRS)

> **Document ID**: `docs/SRS.md`  
> **Phase**: FYP-I Requirements & Specifications  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Introduction
MindShield is a real-time, explainable mobile application designed to defend users in Pakistan against Short Message Service (SMS) phishing (smishing) and advance-fee social engineering fraud. South Asian telecommunications fraud utilizes distinct bilingual features—such as Roman Urdu transliteration, English-Urdu code-switching, local bank names, and carrier-specific billing codes—which are not addressed by traditional spam filters or international machine learning datasets. This document defines the comprehensive software, hardware, functional, and non-functional requirements of the MindShield platform, establishing the development, integration, and evaluation boundary for the Final Year Project (FYP-I).

---

## 2. Purpose
The purpose of this Software Requirements Specification (SRS) is to establish the complete, verified functional and non-functional requirements for the MindShield system. It serves as the primary technical specification for:
1. **Academic Evaluation**: Demonstrating that the FYP-I proof of concept satisfies the University's software engineering and architectural standards.
2. **Development Invariants**: Defining the exact interfaces, database schemas, APIs, and ML pipelines that must be preserved during subsequent development phases.
3. **Verification Scope**: Defining the exact test cases and traceability paths used to audit the platform before viva presentation.

---

## 3. Scope
The scope of the MindShield platform encompasses:
* **Flutter Mobile Client**: A cross-platform Android mobile interface providing conversation threading, settings control, a dashboard, a quarantined spam folder, an analysis log history, and threat highlight cards.
* **Android Native Integrations**: Background Kotlin SMS receivers, method channels for reading system contacts, and triggers to open native dialers or messaging threads.
* **Local Persistence**: An offline-first SQLite database managing cached inbox threads, quarantined spam items, user logs, and settings.
* **FastAPI Backend Server**: A high-performance Python REST API exposing health metrics, system statuses, and SMS threat analysis routes.
* **AI Inference Pipeline**: A fine-tuned DistilBERT classification engine executing tokenization, forward inference passes, and returning threat severity buckets and classification probabilities.

---

## 4. Product Perspective
MindShield operates as a client-server security platform. It intercepts incoming SMS streams on the mobile device, queries a central FastAPI server for deep learning classifications, caches results locally, and presents interactive warning visualizers to the user.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                MOBILE CLIENT                                 │
│                                                                              │
│  Incoming SMS ──> [Kotlin SMS Interceptor] ──> [Dart Thread Manager]        │
│                                                     │                        │
│  User Interface <── [SQLite Local DB] <─────────────┴──> [Dio Client]        │
└─────────────────────────────────────────────────────────────┬────────────────┘
                                                              │
                                                         POST /analyze (HTTP)
                                                              │
┌─────────────────────────────────────────────────────────────▼────────────────┐
│                                BACKEND SERVER                                │
│                                                                              │
│  [FastAPI Endpoint] ──> [InferenceService] ──> [DistilBERT Transformer]       │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Stakeholders and Actors

### 5.1 Mobile User
* **Description**: The end-user running the MindShield application on an Android mobile device.
* **Responsibilities**: Grant required Android system permissions, view SMS lists, trigger detail analyses, and inspect threat highlights.

### 5.2 Android Operating System
* **Description**: The mobile OS hosting the application sandbox.
* **Responsibilities**: Dispatch SMS incoming broadcasts via intents, enforce runtime permission gates, and allow dialer/SMS method channel execution.

### 5.3 Flutter Application (Client Engine)
* **Description**: The client-side application logic (state managers, repository interfaces, local SQLite managers).
* **Responsibilities**: Capture intercepted SMS payloads, coordinate local persistence, manage background channel synchronization, query APIs, and render threat details.

### 5.4 Backend/API Service (FastAPI)
* **Description**: The Python REST server hosting request controllers.
* **Responsibilities**: Validate requests via Pydantic, normalise text inputs, route text to the inference service, and return standard JSON API envelopes.

### 5.5 ML Classification Service
* **Description**: The PyTorch model wrapper executing transformer predictions.
* **Responsibilities**: Tokenize clean text strings, execute model forward passes, evaluate softmax probabilities, and map outputs to classification labels.

---

## 6. System Overview
The MindShield system architecture integrates the local client-side persistence pipeline with a centralized AI inference server. Incoming SMS messages are captured by a Kotlin broadcast receiver, written to the local SQLite database, and listed within a thread layout. When a user navigates to a specific thread, the application fetches security classifications from the FastAPI backend.

The backend is configured with a dual-pipeline architecture:
1. **Pipeline 1 (Binary Classification - Implemented)**: Fine-tuned DistilBERT model classifying messages into `safe` or `phishing` categories. The active production weights are **`distilbert-pakscam-v1`**. Research candidates `v2` and `v3` are archived in an isolated sandbox.
2. **Pipeline 2 (Psychological Categorization - Planned)**: A 5-class multi-label model classifying text based on threat strategies (Urgency, Authority, Fear, Reward, Scarcity).

---

## 7. Functional Requirements

### 7.1 Client-Side Requirements

#### FR-01 — Request SMS Permissions
* **Description**: The application shall request required SMS permissions from the Android OS at startup.
* **Actor**: Mobile User, Flutter Application, Android OS
* **Preconditions**: Application is launched for the first time.
* **Main Flow**:
  1. Application checks permission status of `RECEIVE_SMS` and `READ_SMS`.
  2. If not granted, the UI presents a permissions onboarding screen.
  3. User clicks "Grant Permissions".
  4. System prompts the native permission dialog.
  5. User selects "Allow".
* **Alternative Flow**:
  * If the user selects "Deny", the application disables background automatic interception and displays a warning banner indicating that manual check remains the only active security mode.
* **Postconditions**: Permission flags are updated in application state.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`frontend/lib/features/permissions/presentation/permissions_provider.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/permissions/presentation/permissions_provider.dart)

#### FR-02 — Intercept Incoming SMS
* **Description**: The system shall intercept incoming SMS messages in the background and write them to the local database.
* **Actor**: Android OS, Flutter Application
* **Preconditions**: SMS permissions are granted; background service is registered.
* **Main Flow**:
  1. Device receives an SMS broadcast intent.
  2. Kotlin `SMSBroadcastReceiver` catches the intent payload.
  3. Payload (sender, body, timestamp) is sent through the method channel.
  4. Dart receiver parses variables and writes them to SQLite database.
  5. Inbox thread state is updated.
* **Alternative Flow**:
  * If the method channel is disconnected, the Kotlin listener caches the incoming SMS data in an intent bundle until the Flutter engine restarts, avoiding message loss.
* **Postconditions**: The message is stored in `mindshield.db` and rendered on UI.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`frontend/lib/core/services/sms_background_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/sms_background_service.dart)

#### FR-03 — Render Conversation Threads
* **Description**: The application shall aggregate SMS records by sender and display them as grouped conversation threads.
* **Actor**: Mobile User, Flutter Application
* **Preconditions**: Local database has SMS records.
* **Main Flow**:
  1. User navigates to the Inbox screen.
  2. Inbox provider queries local SQLite repository for grouped threads.
  3. Contacts provider resolves phone numbers to contact names.
  4. UI renders the list using a Material 3 ListView.
* **Alternative Flow**:
  * If no contacts match, the raw sender address (phone number or alphanumeric string) is shown as the thread title.
* **Postconditions**: Active inbox is rendered.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`frontend/lib/features/inbox/presentation/inbox_screen.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/inbox/presentation/inbox_screen.dart)

#### FR-04 — Query Threat Analysis API
* **Description**: The application shall query the FastAPI backend server to analyze specific message text.
* **Actor**: Flutter Application, Backend/API Service
* **Preconditions**: Network connection is active; backend is reachable.
* **Main Flow**:
  1. User selects a message thread or opens detail analysis.
  2. Dio client compiles `AnalysisRequest` JSON containing body text and sender.
  3. Client executes `POST /api/v1/analyze` to the configured backend IP.
  4. Backend returns `APIResponse[AnalysisResult]`.
  5. Provider parses JSON and stores threat level and confidence in local history.
* **Alternative Flow**:
  * If the server is unreachable or returns HTTP error (e.g. 503), the repository catches the exception and updates the UI state with a retry option, keeping previous cached results if available.
* **Postconditions**: Analysis state is populated.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`frontend/lib/features/analysis/data/api_analysis_repository.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/data/api_analysis_repository.dart)

#### FR-05 — Render Heuristic Threat Highlights
* **Description**: The client shall highlight suspicious keywords in the message detail view using backend feature indicators.
* **Actor**: Flutter Application
* **Preconditions**: `AnalysisResult` is successfully parsed.
* **Main Flow**:
  1. Application checks `indicators` array in the result.
  2. For each active indicator (e.g., `url_detected`, `urgency_language`), the parser extracts matching terms from the text.
  3. `LimeHighlightCard` renders the text using a `RichText` span, applying a yellow/red warning overlay (scaled to indicator weight).
* **Postconditions**: Highlight spans are rendered.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart)

---

### 7.2 Backend & ML Requirements

#### FR-06 — Validate API Request
* **Description**: The FastAPI server shall validate incoming REST payloads against length, format, and type constraints.
* **Actor**: Backend/API Service
* **Preconditions**: REST API receives a request on `/api/v1/analyze`.
* **Main Flow**:
  1. Pydantic parser validates schema types.
  2. Service checks `is_valid_message` rules (length in `[3, 2000]`, non-whitespace, not purely numeric).
  3. If valid, request is forwarded to the inference chain.
* **Alternative Flow**:
  * If Pydantic fails, returns HTTP 422 with validation details.
  * If business rules fail, returns HTTP 400 with a validation error description.
* **Postconditions**: Request is parsed into a validated domain object.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`backend/app/utils/validators.py:is_valid_message`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py#L137-L156)

#### FR-07 — Load Active ML Weights
* **Description**: The server shall instantiate and warm up the PyTorch transformer weights on startup.
* **Actor**: ML Classification Service
* **Preconditions**: FastAPI server executes startup lifespan context.
* **Main Flow**:
  1. Server reads settings to resolve model path (`backend/data/models/distilbert/`).
  2. `AutoModelForSequenceClassification` loads model weights into memory.
  3. Tokenizer loads WordPiece vocab files.
  4. Warmup pass checks inference readiness.
* **Alternative Flow**:
  * If weight loading fails (e.g., directory missing), the lifespan context catches the error, logs a critical alert, and registers `MockModelLoader` as a fallback backend if `model_fallback_enabled` is active, maintaining service availability.
* **Postconditions**: InferenceService is marked ready.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`backend/app/core/model_loader.py:HuggingFaceModelLoader.load`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py#L331-L420)

#### FR-08 — Transformer Classification Inference
* **Description**: The system shall process text through the fine-tuned DistilBERT model and return classification probabilities.
* **Actor**: ML Classification Service
* **Preconditions**: inference engine is loaded; input text is sanitised.
* **Main Flow**:
  1. Preprocessor normalises text using NFKC.
  2. Tokenizer encodes text into subword token tensors (`max_length=128`, padding, truncation).
  3. PyTorch model performs forward pass.
  4. Sigmoid/Softmax extracts class probability scores ($P_{	ext{safe}}, P_{	ext{phishing}}$).
  5. Outputs are compiled into a `ModelPrediction` object.
* **Postconditions**: Prediction probabilities are logged and returned.
* **Priority**: Must Have
* **Implementation Status**: **IMPLEMENTED**
* **Evidence**: [`backend/app/core/model_loader.py:HuggingFaceModelLoader.predict`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py#L429-L500)

---

## 8. Non-Functional Requirements

### 8.1 Performance
* **NFR-01 — Model Inference Latency**: The mean backend pipeline duration for a single message classification shall be under **$60	ext{ ms}$** on CPU.
  * *Evidence*: Verified in [`backend/data/metadata/v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json), where `distilbert-pakscam-v1` achieved a mean latency of **`41.95 ms`** (Max: `50.74 ms`) and `v3` achieved a mean latency of **`57.62 ms`** (Max: `77.51 ms`).
  * *Status*: **IMPLEMENTED**
* **NFR-02 — DB Transaction Latency**: All local SQLite database reads/writes should execute within **$15	ext{ ms}$** under normal operating loads to prevent main-thread blockage in the Flutter UI.
  * *Evidence*: No exact transaction benchmark file is present in the repository. This is classified as a **planned engineering target (not yet verified)**.
  * *Status*: **PLANNED / NOT YET VERIFIED**

### 8.2 Security
* **NFR-03 — Network Payload Security**: All request payloads transmitted between the client and server shall use standard HTTP over TLS (HTTPS) in production to prevent eavesdropping.
  * *Evidence*: The current FYP-I local development configurations in `app_constants.dart` default strictly to unencrypted **HTTP** (`http://10.0.2.2:8000`). HTTPS is a production deployment requirement.
  * *Status*: **PLANNED / FYP-II**
* **NFR-04 — Input Sanitisation**: The backend shall normalise all SMS text strings using NFKC Unicode normalization to prevent malicious injection attacks.
  * *Evidence*: Verified in [`backend/app/utils/validators.py:sanitise_message`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py#L177-L198).
  * *Status*: **IMPLEMENTED**

### 8.3 Privacy
* **NFR-05 — Anonymized Transmission**: The API shall not record or write to disk any sender phone numbers or personally identifiable information (PII) during the classification logging.
  * *Evidence*: Confirmed in `backend/app/services/analysis_service.py` where only length and metrics are written to backend server logs.
  * *Status*: **IMPLEMENTED**

### 8.4 Usability
* **NFR-06 — Localized Urdu Support**: The user-facing threat highlights, warnings, and explanations shall provide localized indicators to support low-literacy users.
  * *Evidence*: Basic threat badges (danger labels) are implemented. Full bilingual translation templates are scheduled.
  * *Status*: **PARTIALLY IMPLEMENTED / FYP-I**

### 8.5 Compatibility
* **NFR-07 — Mobile OS Target**: The mobile client application shall target Android API level **`21`** (Lollipop 5.0) and above, ensuring coverage for the majority of active local devices.
  * *Evidence*: Verified in `frontend/android/app/build.gradle` (minSdkVersion is set to 21).
  * *Status*: **IMPLEMENTED**

---

## 9. Use Cases

### UC-01 — Grant System Permissions
* **Primary Actor**: Mobile User
* **Goal**: Enable the application to monitor and read system SMS text blocks.
* **Preconditions**: App is launched and running.
* **Trigger**: Permissions screen or onboarding layout is loaded.
* **Main Success Scenario**:
  1. Application checks permissions (`RECEIVE_SMS`, `READ_SMS`).
  2. UI displays onboarding request.
  3. User clicks "Grant".
  4. OS displays native authorization modal.
  5. User selects "Allow".
* **Alternative Flows**:
  * User selects "Deny". App records status and disables background receiver, prompting a notification banner that manual check remains the only active security mode.
* **Postconditions**: On-device SMS broadcast receiver is registered.
* **Related FRs**: FR-01
* **Status**: **IMPLEMENTED**

### UC-02 — Intercept Incoming SMS
* **Primary Actor**: Android Operating System
* **Goal**: Forward incoming message details to the application.
* **Preconditions**: Permissions are active; background receiver registered.
* **Trigger**: Telephony provider broadcast intent.
* **Main Success Scenario**:
  1. OS broadcasts intent payload containing sender and body.
  2. Kotlin `SMSBroadcastReceiver` catches intent.
  3. Data is sent to Flutter via Native Method Channel.
  4. App writes parsed message into SQLite database.
* **Postconditions**: Message is cached locally and thread state updates.
* **Related FRs**: FR-02
* **Status**: **IMPLEMENTED**

### UC-03 — View Inbox Conversations
* **Primary Actor**: Mobile User
* **Goal**: View a grouped list of SMS conversations.
* **Preconditions**: Local database has message records.
* **Trigger**: App is opened to the main Inbox view.
* **Main Success Scenario**:
  1. User navigates to Inbox screen.
  2. Inbox Provider queries SQLite repository for threads.
  3. Contacts service resolves phone numbers to contact names.
  4. UI renders the list of grouped threads.
* **Postconditions**: Mobile screen displays active conversation items.
* **Related FRs**: FR-03
* **Status**: **IMPLEMENTED**

### UC-04 — Analyze Message Threat
* **Primary Actor**: Mobile User
* **Goal**: Request a security classification for a specific message thread.
* **Preconditions**: Network connection is active; FastAPI server is online.
* **Trigger**: User opens thread details and clicks "Analyze".
* **Main Success Scenario**:
  1. Client sends a POST request `/api/v1/analyze` containing SMS text.
  2. API validates input, normalises text, and executes DistilBERT inference.
  3. API returns threat classification and indicators.
  4. Flutter client maps JSON to domain models.
  5. UI displays threat gauge, highlights, and warning banners.
* **Alternative Flows**:
  * **Network offline / Timeout**: Dio client catches connection error, displays retry toast, and retains local cached classification.
* **Postconditions**: Classification results are saved in local history logs.
* **Related FRs**: FR-04, FR-06, FR-08
* **Status**: **IMPLEMENTED**

### UC-05 — Inspect Visual Explainability Highlights
* **Primary Actor**: Mobile User
* **Goal**: Understand why a message was marked suspicious.
* **Preconditions**: `AnalysisResult` has been returned and mapped.
* **Trigger**: User views analysis details screen.
* **Main Success Scenario**:
  1. UI checks the `indicators` array in the mapped model.
  2. For every active indicator (e.g., `url_detected`, `financial_keywords`), the regex parser maps terms.
  3. `LimeHighlightCard` renders visual highlight spans over the terms.
* **Postconditions**: User is shown term-level warnings.
* **Related FRs**: FR-05
* **Status**: **IMPLEMENTED**

### UC-06 — Manage Quarantined Spam Messages
* **Primary Actor**: Mobile User
* **Goal**: Inspect and delete/restore messages in the Spam folder.
* **Preconditions**: Messages exist in the quarantined spam table.
* **Trigger**: User opens the Spam folder view.
* **Main Success Scenario**:
  1. User opens Spam Screen.
  2. Spam Provider loads items from SQLite spam repository.
  3. User selects a message and triggers "Restore" or "Delete".
  4. Repository updates SQLite flags and refreshes view.
* **Postconditions**: Message state is updated in local DB.
* **Related FRs**: FR-02, FR-03
* **Status**: **IMPLEMENTED**

### UC-07 — Inspect Historical Logs
* **Primary Actor**: Mobile User
* **Goal**: Audit previous analysis decisions.
* **Preconditions**: Local analysis logs exist.
* **Trigger**: User navigates to the History screen.
* **Main Success Scenario**:
  1. User opens History screen.
  2. History Provider loads cached logs.
  3. UI renders log list sorted by analyzed timestamp.
* **Postconditions**: History logs display on UI.
* **Related FRs**: FR-04
* **Status**: **IMPLEMENTED**

### UC-08 — View Dashboard Analytics
* **Primary Actor**: Mobile User
* **Goal**: Inspect security metrics and analysis statistics.
* **Preconditions**: Database contains active message logs.
* **Trigger**: User navigates to the Dashboard screen.
* **Main Success Scenario**:
  1. Dashboard view queries local SQLite statistics helper.
  2. App aggregates count of safe, suspicious, and dangerous detections.
  3. UI displays structured pie charts or metrics.
* **Postconditions**: Dashboard statistics display.
* **Related FRs**: FR-03, FR-04
* **Status**: **IMPLEMENTED**

### UC-09 — Modify System Settings
* **Primary Actor**: Mobile User
* **Goal**: Adjust notification preferences and API host endpoints.
* **Preconditions**: App is running.
* **Trigger**: User opens the Settings view.
* **Main Success Scenario**:
  1. Settings screen loads cached configurations (e.g. API base URL).
  2. User modifies values and clicks "Save".
  3. Settings Provider updates database and re-initializes Dio Client.
* **Postconditions**: Settings flags are updated in DB.
* **Related FRs**: FR-04
* **Status**: **IMPLEMENTED**

### UC-10 — Query API Operational Health
* **Primary Actor**: Flutter Application
* **Goal**: Verify that the backend server is running and model weights are ready.
* **Preconditions**: Server is running.
* **Trigger**: App startup lifecycle checks.
* **Main Success Scenario**:
  1. Client sends a GET query to `/health`.
  2. Server returns application status, model version, and loaded flags.
  3. UI badges render operational states accordingly.
* **Postconditions**: Server health status is updated.
* **Related FRs**: FR-07
* **Status**: **IMPLEMENTED**

---

## 10. Data Requirements

### 10.1 Local Persistence Schema (`mindshield.db`)
Stored locally within the application's secure sandbox directory:
* **SMS Messages Table**: Fields: `id` (int), `body` (text), `sender` (text), `timestamp` (text), `thread_id` (int), `is_spam` (int).
* **Analysis Log Table**: Fields: `id` (int), `message_id` (int), `label` (text), `threat_level` (text), `confidence` (real), `explanation` (text), `analyzed_at` (text).
* **Settings Table**: Fields: `key` (text), `value` (text).

### 10.2 API Request/Response Data Contract
* **API Payload**: The client transmits only the text body, sender identifier (optional), and RequestMetadata block.
* **PII Bounds**: In compliance with privacy guidelines, the backend only logs the message text length, label, and confidence score on disk; no telephone numbers are retained in server logs.

---

## 11. API Requirements

### 11.1 POST `/api/v1/analyze`
* **HTTP Method**: POST
* **Purpose**: Classify SMS text and extract threat indicator signals.
* **Request Schema** (`AnalysisRequest`):
```json
{
  "message": "String (Length: 3 to 2000)",
  "sender": "Optional String (Max: 50)",
  "metadata": {
    "app_version": "Optional String",
    "locale": "Optional String",
    "network": "Optional wifi|mobile|unknown"
  }
}
```
* **Response Schema** (`APIResponse[AnalysisResult]`):
```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {
    "label": "phishing",
    "threat_level": "dangerous",
    "confidence": 0.9852,
    "explanation": "Human-readable verdict string",
    "indicators": [
      {
        "name": "url_detected",
        "present": true,
        "weight": "high",
        "detail": "Suspicious URL or shortened link detected in message body"
      }
    ],
    "model_version": "distilbert-pakscam-v1",
    "mock_mode": false,
    "processing_time_ms": 12.50,
    "request_id": "UUID-string",
    "predicted_at": "ISO-8601-datetime"
  },
  "error": null,
  "timestamp": "ISO-8601-datetime"
}
```

### 11.2 GET `/api/v1/analyze/status`
* **HTTP Method**: GET
* **Purpose**: Return operational status, settings, and active model loader health.
* **Response Schema**:
```json
{
  "success": true,
  "message": "API v1 is operational",
  "data": {
    "api_version": "v1",
    "app_version": "1.0.0",
    "environment": "development",
    "model_version": "distilbert-pakscam-v1",
    "model_loaded": true,
    "mock_mode": false,
    "endpoints": [
      {
        "method": "POST",
        "path": "/api/v1/analyze",
        "description": "Classify an SMS message",
        "phase": "2.3"
      }
    ]
  },
  "error": null,
  "timestamp": "ISO-8601-datetime"
}
```

---

## 12. ML Requirements

### 12.1 Tokenization and Encoding
* **Subword Vocabulary**: WordPiece tokenizer configured with $30,522$ base English tokens.
* **Sequence Alignment**: Input texts are truncated and padded to a fixed length of **$128$ tokens** to match training configurations, avoiding truncate-alignment bias.

### 12.2 Fine-Tuned Models
* **Production weights (`distilbert-pakscam-v1`)**: Serves as the primary production engine, achieving a balance of $96.00\%$ UCI test F1.
* **Research candidates (`v2` and `v3`)**: Kept strictly isolated in separate candidate directories.
* **Dataset Composition**:
  * Curated PakScam-SMS dataset of **205 unique samples** (140 base templates which include the 15 real-world seeds, plus 65 manual augmentations).
  * Train/Val/Test splitting is grouped by template family to prevent data leakage.

---

## 13. Security and Privacy Requirements

### 13.1 Implemented Controls
* **SQLite Sandbox**: The database `mindshield.db` is stored inside the sandboxed native storage directory (`/data/data/com.example.mindshield/databases`), preventing access by other third-party applications.
* **Input Validation**: Pure functions validate message character configurations (length, character digits) before sending queries, reducing the risk of API overload.
* **PII Scrubbing**: Backend logs do not write phone numbers or user data; only classification metadata is retained for logging.

### 13.2 Recommended Future Controls (Planned)
* **API Authentication**: Integrating JSON Web Tokens (JWT) using OAuth2 to secure the FastAPI routes against public misuse.
* **End-to-End Encryption**: Encrypting SQLite databases on-device using SQLCipher to protect locally cached SMS content.

---

## 14. System Requirements

### 14.1 Hardware Requirements
* **Mobile Client**: Android device with ARMv7/ARM64 processor, minimum 1GB RAM (2GB recommended).
* **API Server (CPU Host)**: CPU with minimum 2 Cores, 2GB RAM (4GB recommended). No dedicated GPU is required to serve DistilBERT inference.

### 14.2 Software Requirements
* **OS Environment**: Android API Level 21 (Lollipop 5.0) or higher.
* **Python Runtime**: Python 3.8 to 3.13.
* **Framework SDKs**: Flutter SDK 3.x, FastAPI 0.111.x, PyTorch 2.x, HuggingFace Transformers 4.x.

---

## 15. Requirements Traceability

| Requirement ID | Proposal Objective | System Module | Code Implementation Evidence | Test verification Evidence | Status |
|---|---|---|---|---|---|
| **FR-01** | Onboarding Design | Permissions | [`permissions_provider.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/permissions/presentation/permissions_provider.dart) | `widget_test.dart` (smoke-test verified) | **IMPLEMENTED** |
| **FR-02** | Message Interception | Background Service | [`sms_background_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/sms_background_service.dart) | Device-level tested (not headless unit testable) | **IMPLEMENTED** |
| **FR-03** | Interface Layout | Inbox Module | [`inbox_screen.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/inbox/presentation/inbox_screen.dart) | `widget_test.dart` (smoke-test verified) | **IMPLEMENTED** |
| **FR-04** | API Communication | Network Module | [`api_analysis_repository.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/data/api_analysis_repository.dart) | `api_analysis_repository_test.dart` | **IMPLEMENTED** |
| **FR-05** | Explainable UI | Analysis Module | [`lime_highlight_card.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart) | `widget_test.dart` (smoke-test verified) | **IMPLEMENTED** |
| **FR-06** | Request Validation | API Validation | [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py) | `test_validators.py` | **IMPLEMENTED** |
| **FR-07** | Lifespan Startup | Inference Root | [`main.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/main.py) | `test_health.py` | **IMPLEMENTED** |
| **FR-08** | Model Classification| Classification Engine| [`model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py) | `test_model_loader_real.py` | **IMPLEMENTED** |

---

## 16. Prioritization
* **Must Have**: FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08, NFR-01, NFR-04, NFR-05, NFR-07.
* **Should Have**: NFR-06 (Urdu descriptions), Dashboard statistics, settings configuration.
* **Could Have**: Background database backups, offline heuristic validation fallback.
* **Out of Scope (FYP-I)**: Real-time network sandboxing, native PTA spam reporting, automatic message deletion.

---

## 17. FYP-I / FYP-II Scope Boundary

### 17.1 FYP-I Completed Deliverables (Proof of Concept)
* curating the custom PakScam-SMS dataset templates.
* Fine-tuning, validating, and testing the `distilbert-pakscam-v1` production weights.
* Setting up the 14-case hard-negative regression testing suite.
* Creating the FastAPI backend architecture with request logging, validation, and lifespans.
* Developing the Flutter client app integrated with Android permission handlers, background receivers, and SQLite thread repositories.

### 17.2 FYP-II Planned Deliverables
* Fine-tuning multilingual transformers (XLM-RoBERTa) for Pipeline 2 (psychological categorization).
* Curing and annotating larger real-world Roman Urdu threat corpora.
* Running live user-acceptance testing (UAT).
* Optimizing inference latency and investigating ONNX/TFLite models to support offline, local predictions.

---

## 18. Assumptions and Constraints
* **Assumption**: The target Android device maintains connection with the internet to perform transformer-based inference.
* **Constraint**: The application cannot block or delete SMS records directly from the system provider databases without being explicitly designated as the default SMS client by the user.

---

## 19. Acceptance Criteria
1. **SMS Interception**: The app must successfully intercept incoming SMS messages in the background and insert them into local threads.
2. **API Latency**: Average server-side classification response time must remain below $60	ext{ ms}$ on CPU hosts.
3. **Traceability**: All functional requirements must map to verified modules and pytest/widget testing suites.
4. **Accuracy Baseline**: The production model must achieve $\ge 95\%$ F1-score on the UCI test split.

---

## 20. Summary
This Software Requirements Specification (SRS) establishes a complete, verified baseline for the MindShield platform. By defining actors, use cases, functional/non-functional constraints, and the strict boundaries between FYP-I and FYP-II, this specification aligns the current proof-of-concept codebase with the academic requirements of the Final Year Project.
