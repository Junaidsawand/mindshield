# MindShield — REST API & Schema Validation Viva Guide

> **Module**: REST API Specification & Pydantic Schema Contracts  
> **Focus**: Endpoint Contracts, Payload Validation, OpenAPI 3.0, Error Schemas  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding

### Q1: What endpoint contracts form the core MindShield REST API?
**Model Answer:**  
MindShield Phase 2.1 exposes three primary HTTP endpoints:
1. `GET /health`: Returns system health, server uptime, environment, and model loader status.
2. `POST /api/v1/analyze`: Accepts SMS text and sender metadata; returns structured threat verdicts and explanations.
3. `GET /api/v1/analyze/status`: Returns operational status of the v1 analysis pipeline.

---

### Q2: How does Pydantic v2 enforce type safety between Flutter Dio and FastAPI?
**Model Answer:**  
FastAPI uses Pydantic schemas (`AnalysisRequest`, `AnalysisResult`) to parse JSON request bodies. Pydantic validates types at the API boundary before passing data to services. If a request is invalid (e.g. missing `message` field), FastAPI automatically returns a structured `HTTP 422 Unprocessable Entity` response. The Flutter Dio client mirrors these Pydantic contracts using typed Dart DTOs, ensuring end-to-end schema alignment.

---

## Section B — Design Decision Justification

### Q3: Why place versioning in the URL path (`/api/v1/analyze`) rather than request headers?
**Model Answer:**  
URL path versioning (`/api/v1/`) provides explicit, immutable contract definitions that are easy to route, inspect in logs, test via Curl/Postman, and document in OpenAPI schemas. Header-based versioning (`Accept: application/vnd.mindshield.v1+json`) adds unnecessary complexity for mobile HTTP clients without providing tangible architectural benefits for our single-client application.

---

## Section C — Implementation & Technical Depth

### Q4: Detail the exact JSON schema contract for `POST /api/v1/analyze`.
**Model Answer:**  

**Request Schema (`AnalysisRequest`)**:
```json
{
  "message": "URGENT: Your account has been compromised. Verify here: http://fake-bank.com",
  "sender": "+18882205530"
}
```

**Success Response Schema (`APIResponse[AnalysisResult]`)**:
```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {
    "label": "scam",
    "threat_level": "scam",
    "confidence": 0.97,
    "explanation": "High-urgency trigger word combined with unverified URL shortener.",
    "model_version": "placeholder-v0",
    "is_placeholder": true,
    "predicted_at": "2026-08-03T10:30:00Z"
  },
  "error": null,
  "timestamp": "2026-08-03T10:30:00Z"
}
```

---

## Section D — Limitations, Risks & Future Work

### Q5: How will the API handle batch analysis requests for processing large inboxes?
**Model Answer:**  
Currently, `/api/v1/analyze` accepts one message per request. To optimize network round-trips when scanning a device inbox with hundreds of messages, Phase 2.7 will introduce `POST /api/v1/analyze/batch`, accepting a JSON array `{"messages": [...]}` and utilizing Python's `asyncio.gather()` to run parallel inference over bulk payloads.

---
*MindShield API Viva Guide · Final Year Project 2026*
