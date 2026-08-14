# MindShield — API Contracts & Data Flow

> **Document ID**: `docs/design/API_DATA_FLOW.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. POST `/api/v1/analyze` Contract

The core API endpoint is hosted by the FastAPI analysis router to perform text classification.

### 1.1 HTTP Request Specification
* **HTTP Method**: `POST`
* **Route**: `/api/v1/analyze`
* **Headers**: `Content-Type: application/json`
* **Request Payload Schema** (`AnalysisRequest`):

```json
{
  "message": "String (min_length: 3, max_length: 2000, required)",
  "sender": "String (max_length: 50, optional)",
  "metadata": {
    "app_version": "String (max_length: 20, optional)",
    "locale": "String (max_length: 10, optional)",
    "network": "String (wifi | mobile | unknown, optional)"
  }
}
```

### 1.2 Validation Rules
Executed inside [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py) and Pydantic field validators:
1. **Whitespace Normalisation**: The input message is stripped of leading and trailing whitespaces before length check.
2. **Length Validation**: Rejects messages with length less than 3 or greater than 2,000 characters.
3. **Digit Check**: Rejects messages composed entirely of numbers to block empty numeric entries.

---

## 2. POST Analysis Backend Data Flow

The following sequence details how the backend parses the API payload:

```
[HTTP POST Client]
       │
       ▼
[FastAPI Router Controller] ──> [Pydantic Schema Parsing]
                                         │
       ┌─────────────────────────────────┴────────────────────────────────┐
       ▼ (Validates schema types)                                         ▼ (Fails checks)
[Validators Module]                                             [HTTP 422 Unprocessable]
       │
       ├─> Unicode Normalisation (NFKC)
       │
       ▼ (Validates content rules)
[InferenceService]
       │
       ├─> [HuggingFaceModelLoader] ──> Tokenize (WordPiece) ──> Predict (distilbert-pakscam-v1)
       │                                                                  │
       ├─> [AnalysisService] <── [Heuristics checkers] <──────────────────┘
       │          │
       │          ▼ (Aggregates indicators checklist)
       │   1. credential_request (critical)
       │   2. url_detected       (high)
       │   3. urgency_language   (high)
       │   4. financial_keywords (medium)
       │   5. prize_language     (medium)
       │   6. excessive_caps     (low)
       ▼
[APIResponse Envelope] ──> [HTTP 200 OK JSON]
```

---

## 3. API Response Specification

### 3.1 HTTP Success Response (200 OK)
Returns a generic envelope mapping the classification verdict details.

```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {
    "label": "phishing",
    "threat_level": "dangerous",
    "confidence": 0.9852,
    "explanation": "⚠️ HIGH THREAT — requests sensitive credentials (password, OTP, PIN); contains a URL or shortened link.",
    "indicators": [
      {
        "name": "credential_request",
        "present": true,
        "weight": "critical",
        "detail": "Requests sensitive credentials (password, OTP, PIN)"
      },
      {
        "name": "url_detected",
        "present": true,
        "weight": "high",
        "detail": "Suspicious URL or shortened link detected in message body"
      },
      {
        "name": "urgency_language",
        "present": false,
        "weight": "high",
        "detail": null
      },
      {
        "name": "financial_keywords",
        "present": false,
        "weight": "medium",
        "detail": null
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
    "processing_time_ms": 12.5,
    "request_id": "8b9a202c-7b4d-4a1e-8e8c-1a2d3e4f5a6b",
    "predicted_at": "2026-08-14T11:45:00Z"
  },
  "error": null,
  "timestamp": "2026-08-14T11:45:00Z"
}
```

### 3.2 HTTP Error Response Envelopes

#### Schema Validation Failure (HTTP 422 Unprocessable Entity)
```json
{
  "success": false,
  "message": "Validation error",
  "data": null,
  "error": {
    "error_code": "validation_error",
    "message": "Input validation failed: message length must be at least 3 characters."
  },
  "timestamp": "2026-08-14T11:45:01Z"
}
```

#### Content Policy Failure (HTTP 400 Bad Request)
```json
{
  "success": false,
  "message": "Bad request",
  "data": null,
  "error": {
    "error_code": "bad_request_error",
    "message": "Invalid message: text cannot consist solely of digits."
  },
  "timestamp": "2026-08-14T11:45:02Z"
}
```
