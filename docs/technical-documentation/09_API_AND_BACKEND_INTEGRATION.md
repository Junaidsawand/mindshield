# Chapter 9 — System Integration & Communication APIs

This chapter documents the communication layer, request serialization models, validation boundaries, and error recovery flows between the MindShield Flutter application and the FastAPI backend.

---

## 9.1 API Integration Flow

The integration pipeline coordinates local event interception, remote network transfer, server-side processing, and state serialization:

```
[Flutter App Client] ──► [Dio client] ──► [HTTP Request] ──► [FastAPI Router]
                                                                  │
                                                                  ▼ (Pydantic Schema Validation)
                                                        [Request Payload]
                                                                  │
                                                                  ▼
                                                        [AnalysisService (Server)]
                                                                  │
                                           ┌──────────────────────┴──────────────────────┐
                                           ▼ (HFA Indicators)                            ▼ (InferencePass)
                                  [Validators Engine]                           [InferenceService Core]
                                           │                                             │
                                           ▼                                             ▼
                                  [Threat Indicators]                           [DistilBERT PyTorch Model]
                                           │                                             │
                                           └──────────────────────┬──────────────────────┘
                                                                  │
                                                                  ▼
                                                        [AnalysisResult Schema]
                                                                  │
                                                                  ▼ (HTTP Response JSON)
[Flutter Presentation UI] ◄── [ChangeNotifier State] ◄── [Dart Domain Model]
```

**Implementation Evidence:**
* **Flutter client:** [`frontend/lib/core/services/analysis_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/analysis_service.dart)
* **Backend routing thin controller:** [`backend/app/routers/v1/analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/routers/v1/analysis.py)

---

## 9.2 API Versioning

All threat classification endpoints are versioned under the prefix:

```
/api/v1
```

Versioning ensures that future schema updates or changes in classification outputs (e.g. migrating from binary classification to multi-class models in Phase 3+) do not break backward compatibility with legacy client builds.

---

## 9.3 Endpoint Inventory

### Table 9.1 — Endpoint Inventory

| HTTP Method | API Endpoint | Purpose | Request Schema | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| **`GET`** | `/health` | Server operational status check | None | `HealthStatus` |
| **`POST`** | `/api/v1/analyze` | Submit SMS for threat classification | `AnalysisRequest` | `APIResponse[AnalysisResult]` |
| **`GET`** | `/api/v1/analyze/status`| API v1 metadata & loaded model health | None | `APIResponse[dict]` |

---

## 9.4 POST /api/v1/analyze

The primary POST endpoint receives SMS text and returns a classification verdict:

* **HTTP Method:** `POST`
* **Route:** `/api/v1/analyze`
* **Content-Type:** `application/json`

### 1. Analysis Request Schema
The request body is validated using the `AnalysisRequest` Pydantic model:

#### Table 9.2 — Request Fields

| Field Name | Data Type | Requirement | Default Value | Validation Constraints | Purpose |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **`message`** | String | **Required** | — | Min length: 3, Max length: 2,000 | SMS text to analyze. |
| **`sender`** | String | Optional | `None` | Max length: 50 | Sender phone number or shortcode. |
| **`metadata`**| `RequestMetadata`| Optional | `None` | Schema validated | Client app environment context. |

*Within the nested `RequestMetadata` schema, the client can optionally transmit `app_version`, `locale` (e.g. "ur-PK"), and `network` type.*

#### Request JSON Example:
```json
{
  "message": "URGENT: Your bank account is suspended. Click http://fake-ubl.example.com",
  "sender": "+923001234567",
  "metadata": {
    "app_version": "1.0.0",
    "locale": "en-US",
    "network": "mobile"
  }
}
```

### 2. Analysis Response Schema
The response payload is enclosed in a standard envelope schema `APIResponse[AnalysisResult]`:

#### Table 9.3 — Response Fields

| Field Name | Data Type | Scope | Description |
| :--- | :--- | :--- | :--- |
| **`success`** | Boolean | Envelope | `true` if the request was processed successfully. |
| **`message`** | String | Envelope | Operation summary (e.g., `"Analysis complete"`). |
| **`data`** | `AnalysisResult`| Payload | Enclosed classification metadata (see fields below). |
| **`error`** | Dict / Null | Envelope | Contains error codes and messages if `success = false`. |
| **`label`** | String | Payload | Core model classification class (`"safe"` or `"phishing"`). |
| **`threat_level`**| String | Payload | Verdict categorization: `"safe"`, `"suspicious"`, `"dangerous"`. |
| **`confidence`** | Float | Payload | Prediction probability score in `[0.0, 1.0]`. |
| **`explanation`**| String | Payload | Human-readable explanation of the verdict. |
| **`indicators`** | List[Dict] | Payload | List of HFA features checked (Pydantic `ThreatIndicator`). |
| **`model_version`**| String | Payload | Version code of the active loader (e.g. `"distilbert-pakscam-v1"`). |
| **`mock_mode`** | Boolean | Payload | `true` if prediction was generated by the heuristic engine. |
| **`processing_time_ms`**| Float | Payload | Execution duration of the backend pipeline. |
| **`predicted_at`**| DateTime | Payload | ISO-8601 UTC timestamp of execution. |

#### Successful Response JSON Example:
```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {
    "label": "phishing",
    "threat_level": "dangerous",
    "confidence": 0.9926,
    "explanation": "Fine-tuned DistilBERT model detected spam/phishing pattern (99.3% confidence).",
    "indicators": [
      {
        "name": "credential_request",
        "present": false,
        "weight": "critical",
        "detail": null
      },
      {
        "name": "url_detected",
        "present": true,
        "weight": "high",
        "detail": "Suspicious URL or shortened link detected in message body"
      },
      {
        "name": "urgency_language",
        "present": true,
        "weight": "high",
        "detail": "Urgency/imperative language detected (e.g. 'urgent', 'suspended')"
      },
      {
        "name": "financial_keywords",
        "present": true,
        "weight": "medium",
        "detail": "References financial institutions or transactions"
      },
      {
        "name": "prize_language",
        "present": false,
        "weight": "medium",
        "detail": null
      },
      {
        "name": "excessive_caps",
        "present": false,
        "weight": "low",
        "detail": null
      }
    ],
    "model_version": "distilbert-pakscam-v1",
    "mock_mode": false,
    "processing_time_ms": 58.2,
    "request_id": "8fa21e64-d3a9-4560-b18c-a980591f8682",
    "predicted_at": "2026-08-19T16:21:44Z"
  },
  "error": null,
  "timestamp": "2026-08-19T16:21:44Z"
}
```

**Implementation Evidence:**
* **Schemas File:** [`backend/app/schemas/analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/schemas/analysis.py)
* **Verify:** Schema class definitions confirm field names and properties.

---

## 9.5 Input Validation & Business Rules

FastAPI handles validation at two levels:

1. **Pydantic Schema Validation (HTTP 422):** 
   If message length constraints are violated, the request fails schema validation. FastAPI returns `HTTP 422 Unprocessable Entity` with a list of failing fields.
2. **Business-Rule Validation (HTTP 400):**
   Defined in `is_valid_message` inside `validators.py`.
   - Rejects empty messages.
   - Rejects messages composed entirely of numbers (such as bare OTP codes).
   If validation fails, the controller returns `HTTP 400 Bad Request`.

### Table 9.4 — HTTP Error Behavior

| HTTP Code | Error Code | Trigger Condition | Response Structure |
| :--- | :--- | :--- | :--- |
| **`400`** | `validation_error` | Purely numeric string or whitespace-only inputs. | `{"success": false, "message": "Message validation failed.", "data": null, ...}` |
| **`422`** | `validation_error` | Input length <3 characters or >2,000 characters. | Includes a `details` array containing specific schema violation logs. |
| **`503`** | `model_not_ready` | Model weights not loaded or initialization failed. | `{"success": false, "message": "AI model is not currently available.", ...}` |

**Implementation Evidence:**
* **validators:** [`backend/app/utils/validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py) (lines 165-199)

---

## 9.6 Backend Routing thin Controller

FastAPI uses an explicit dependency injection structure to resolve routes:

```python
# From backend/app/routers/v1/analysis.py
@router.post("", response_model=APIResponse[AnalysisResult])
async def analyse_message(
    http_request: Request,
    body: AnalysisRequest,
    service: AnalysisService = Depends(_get_analysis_service),
) -> APIResponse[AnalysisResult]:
    request_id = getattr(http_request.state, "request_id", None)
    result = service.analyse(body.message, body.sender, request_id)
    return APIResponse[AnalysisResult].ok(data=result)
```

The router acts as a thin controller. It extracts the `request_id` injected by the logging middleware, calls `AnalysisService.analyse`, and wraps the result in an `APIResponse` envelope.

---

## 9.7 Service Layer & Inference Pipeline

The execution sequence within the server is structured as follows:

```
FastAPI Router ──► AnalysisService.analyse()
                        │
                        ▼ (Step 1: Input Validation)
                  is_valid_message(text)
                        │
                        ▼ (Step 2: String Sanitisation)
                  sanitise_message(text)
                        │
                        ▼ (Step 3: Feature Extraction)
                  compute_message_features(clean_text)
                        │
                        ▼ (Step 4: Inference Pass)
                  InferenceService.predict(clean_text) ──► BaseModelLoader.predict()
                        │
                        ▼ (Step 5: Response Serialization)
                  _build_indicators() ──► AnalysisResult
```

### Table 9.5 — Backend Services

| Component | Class / Method | Orchestration Scope |
| :--- | :--- | :--- |
| **Analysis Core** | `AnalysisService` | Validates strings, calls inference pipelines, maps indicator arrays, and compiles results. |
| **Inference Wrapper** | `InferenceService` | Manages model loading, profiles execution latencies, and routes failed queries to fallback loaders. |
| **HFA Engine** | `compute_message_features` | Runs regular expressions and keyword checks to generate explainability indicators. |

---

## 9.8 Model Loader and Fallback Contract

The server manages models using an abstraction layer:
* **Contract:** All engines implement the `BaseModelLoader` abstract interface.
* **HuggingFace Loader:** Runs PyTorch inference on the fine-tuned DistilBERT model.
* **Mock Loader:** Runs rule-based HFA checks, returning prediction data with confidence scores in the range `[0.60, 0.97]` dynamically.
* **Fallback Behavior:** If PyTorch crashes (e.g. due to memory allocation errors), the `InferenceService` catches the exception and routes the request to the `MockModelLoader`. The prediction is returned with the flag `fallback_mode = true` set in its metadata.

**Implementation Evidence:**
* **Fallback Logic:** [`backend/app/services/inference_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/inference_service.py) (lines 114-135)

---

## 9.9 Heuristic Feature Attribution (HFA) & Attack Mapping

HFA and model inference are executed **sequentially and synchronously** on the server.
* The model returns a binary verdict (`safe` or `phishing`).
* The HFA engine returns a list of matched security indicators (e.g., `url_detected`, `credential_request`).
* **Categorization Mapping:** If the message is classified as malicious, the system maps it to a specific attack category based on the present HFA indicators.

### Attack Vector Mapping Logic:
```python
# Mapped in api_analysis_repository.dart
if (keywordNames.any((k) => k.contains('prize'))) return AttackType.prizeScam;
if (keywordNames.any((k) => k.contains('financial'))) return AttackType.investmentFraud;
if (keywordNames.any((k) => k.contains('credential'))) return AttackType.piiHarvesting;
if (label == 'phishing') return AttackType.phishing;
return AttackType.smishing;
```

**Attack-vector categorization is rule-based and is NOT a multi-class DistilBERT classifier.** It acts as a descriptive post-processing step on the client side.

---

## 9.10 Flutter client API Integration

The mobile client communicates with the backend using the **Dio** HTTP client:

### Table 9.6 — Flutter API Integration

| Parameter | Value / Implementation |
| :--- | :--- |
| **HTTP client** | `Dio` singleton pre-configured via `DioClient`. |
| **Base URL** | `http://10.250.110.244:8000/api/v1` (configurable via `--dart-define=API_BASE_URL`). |
| **Endpoints** | `/analyze` (Classification), `/health` (Health Probe). |
| **Headers** | `{"Content-Type": "application/json", "Accept": "application/json"}` |
| **Timeouts** | `connectTimeout: 15s`, `receiveTimeout: 30s` |
| **Retry Loop** | Up to **2 retries** on timeout/network loss with exponential backoff. |

```dart
// Request loop inside AnalysisService (Dart)
final response = await _dio.post(
  AppConstants.analyzeEndpoint,
  data: payload,
);
```

**Response Deserialization:** The client parses the JSON response into Dart domain models, updating the local SQLite database state and triggering UI provider updates.

**Implementation Evidence:**
* **Dio Config:** [`frontend/lib/core/network/dio_client.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/network/dio_client.dart)
* **Constants Config:** [`frontend/lib/core/constants/app_constants.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/constants/app_constants.dart) (lines 26-32)

---

## 9.11 CORS & Server Settings

* **CORS Settings:** Allowed origins, headers, and methods are configured in `main.py` using FastAPI's `CORSMiddleware`.
* **Deployment Port:** Listening on port `8000` (host: `0.0.0.0` to support remote LAN device requests).
* **Logging:** Intercepts incoming requests to record response status codes and elapsed processing times (`RequestLoggerMiddleware`).

---

## 9.12 API Security & Privacy

* **Authentication:** **Authentication is not currently implemented in the prototype.** No API tokens, keys, or OAuth checks are enforced.
* **CORS Invariant:** CORS configurations restrict cross-origin browser requests but do not act as an API authentication mechanism.
* **Privacy Boundary:** Messages are transmitted over plain HTTP in development environments. The message body is processed in memory and is **never** persisted to server-side logs. Native contact lists are kept on-device and are not sent to the server.

---

## 9.13 Performance & Processing-Time Logging

The response payload contains the `processing_time_ms` metric:
* **Measurement Scope:** Calculated using Python's `time.perf_counter` within the server's service layer.
* **Inclusions:** Includes text sanitization, HFA rule execution, and PyTorch model weight inference.
* **Exclusions:** Excludes network transmission delay and client-side deserialization overhead.

---

## 9.14 API Execution Sequences

### 1. Integration Sequence Diagram

```
Flutter Client             FastAPI Router           AnalysisService          InferenceService        DistilBERT Model
      │                           │                        │                        │                       │
      │──(POST /analyze)─────────►│                        │                        │                       │
      │                           │──(Validate Pydantic)──►│                        │                       │
      │                           │                        │──(Sanitise string)────►│                       │
      │                           │                        │──(HFA Extraction)─────►│                       │
      │                           │                        │                        │──(predict())─────────►│
      │                           │                        │                        │◄─(Return Logits)──────│
      │                           │                        │◄─(Assemble Response)───│                       │
      │◄─(JSON Response)──────────│                        │                        │                       │
```

### 2. Error Recovery Flow

```
Flutter Client             FastAPI Router           AnalysisService          InferenceService        HuggingFaceLoader
      │                           │                        │                        │                       │
      │──(POST /analyze)─────────►│                        │                        │                       │
      │                           │                        │                        │──(predict())─────────►│
      │                           │                        │                        │◄─(Runtime Error/OOM)──│
      │                           │                        │◄─(Trigger Fallback)────│                       │
      │                           │                        │   (Mock Heuristic Engine)                      │
      │◄─(JSON Response)──────────│                        │                        │                       │
      │   (fallback_mode=true)
```

---

## 9.15 Architectural Trade-offs

* **REST API vs. On-Device Execution:** Remote inference keeps the mobile application lightweight (~40MB) but makes SMS analysis dependent on network connectivity.
* **Pydantic Validation vs. Raw JSON:** Strict schema validation prevents malformed requests from crashing the model pipeline, but increases processing overhead (~3-5ms validation cost).
* **Decoupled Fallback:** The fallback mechanism prevents user alerts from failing on server errors, but can return mock verdicts if the primary model crashes.

---

## 9.16 Chapter Summary

This chapter has detailed the system integration and API communication interfaces of MindShield. By leveraging pre-configured Dio clients, thin routing FastAPI controllers, Pydantic schemas, and fallback architectures, MindShield establishes a robust network bridge between local interception widgets and server-side NLP models.

The validation testing suite and deployment guidelines are detailed in **Chapter 10 — Verification, Validation & Testing**.

---

## API Verification Summary

### Strongly Verified Implementation (Code Proven):
* API endpoints (`POST /api/v1/analyze`, `GET /api/v1/analyze/status`, `GET /health`).
* Request and response schemas, including metadata blocks and indicator weight classes.
* Service-level validation constraints (isdigit, character lengths).
* Platform HTTP configurations (Dio client, timeouts, base URLs, retry loops).
* Fallback prediction mappings (`fallback_mode = true`).

### Limitations & Future Work:
* **No Authentication:** Prototype lacks OAuth, API keys, or JWT controls.
* **No Gateway or Rate-Limiting:** Lacks middleware defenses like rate limiting or web application firewalls.
* **Encryption Constraints:** Operates over plain HTTP in local testing environments (requires HTTPS configuration for production).
