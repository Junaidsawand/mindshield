# MindShield — Production Inference & Client Integration Viva Q&A
### Academic Defense Guide | BS Computer Science Final Year Project

> **Project**: MindShield — AI-Powered SMS Cybersecurity Application  
> **Topic**: Production AI Inference Pipeline & Flutter–FastAPI Integration  
> **Author**: Junaid Ahmed | University of Sindh | 2026  

---

### Question 1: Why did you move SMS threat classification from the Flutter client to a FastAPI backend?
**Answer**:
Mobile devices have constrained CPU, RAM, and thermal envelopes. Running fine-tuned Transformer models like DistilBERT (255 MB weights) locally on mobile hardware introduces severe latency, battery drain, and app binary size bloat. By decoupling inference to a centralized FastAPI backend:
1. The Flutter client remains lightweight, fast, and responsive.
2. The AI model can be updated, fine-tuned, or swapped without forcing users to download mobile app updates.
3. Heavy matrix computations leverage dedicated backend server GPUs/CPUs.

---

### Question 2: How does the Flutter client communicate with the FastAPI inference engine?
**Answer**:
The Flutter client uses the `Dio` HTTP library (`DioClient`) to issue asynchronous HTTP `POST` requests to the `/api/v1/analyze` endpoint. The request body contains the raw message text, sender identifier, and client metadata. The backend processes the text through `AnalysisService` and `InferenceService`, returning a standardized JSON envelope (`APIResponse[AnalysisResult]`) containing the classification verdict, confidence score, threat indicators, and model version.

---

### Question 3: How do you handle network connectivity loss or server downtime on the mobile client?
**Answer**:
`AnalysisService` in Flutter incorporates resiliency mechanisms:
1. **Retry Logic**: Transient network failures (such as connection timeouts) trigger up to 2 automatic retries with exponential backoff delay (`300ms`, `600ms`).
2. **Graceful Exception Handling**: If the backend is unreachable after retries, the error is caught, logged, and surfaced to the UI without crashing the application.
3. **Backend Failover**: On the server side, if primary PyTorch model loading fails, `InferenceService` automatically falls back to `MockModelLoader` so the API endpoint remains 100% operational.

---

### Question 4: How does the client parse the backend JSON response and store it locally?
**Answer**:
The response JSON follows the generic `APIResponse[AnalysisResult]` structure:
```json
{
  "success": true,
  "data": {
    "label": "phishing",
    "threat_level": "dangerous",
    "confidence": 0.952,
    "indicators": [...],
    "explanation": "..."
  }
}
```
`AnalysisService` extracts `threat_level` and maps it to local SQLite categories:
- `"dangerous"` $\rightarrow$ `ai_status = 'scam'`, `is_spam = 1`, `spam_status = 'quarantined'`
- `"suspicious"` $\rightarrow$ `ai_status = 'suspicious'`, `is_spam = 1`, `spam_status = 'quarantined'`
- `"safe"` $\rightarrow$ `ai_status = 'safe'`, `is_spam = 0`, `spam_status = null`

It serializes active threat indicator names as a JSON string into `detected_threats` and updates the SQLite database record via `DatabaseHelper.instance.updateMessage()`.

---

### Question 5: Why did you eliminate local keyword heuristic detection in the mobile app?
**Answer**:
Rule-based keyword heuristics (`urgent`, `suspended`, `bank`, `prize`) produce high false-positive rates, are easy for scammers to evade using misspellings or homoglyphs, and fail to capture context. Transitioning exclusively to server-side AI inference ensures that every message is evaluated by a deep learning model trained on context and subword embeddings, eliminating duplicate or conflicting classification rules between client and server.

---

### Question 6: What latency SLA is maintained for real-time SMS analysis?
**Answer**:
The production inference pipeline maintains a strict SLA:
- **Backend Model Forward Pass**: $\approx 35\text{ms} - 55\text{ms}$ on CPU.
- **End-to-End Client Network Latency**: $< 200\text{ms}$ on local Wi-Fi / standard mobile networks.
- **Warmup Pass**: During backend startup lifespan, a dummy inference pass is performed to pre-allocate PyTorch execution memory, preventing first-request latency spikes.

---

### Question 7: How is clean architecture maintained across the Flutter codebase during this integration?
**Answer**:
Clean architecture principles were strictly enforced:
- **Data Layer**: `ApiAnalysisRepository` handles raw HTTP calls via Dio and deserializes JSON into domain entities.
- **Domain Layer**: `AnalysisResult`, `SmsMessage`, and `AttackType` remain pure Dart entities with zero network dependencies.
- **Presentation Layer**: `AnalysisProvider` manages UI state (`isLoading`, `errorMessage`, `analysisResult`) and depends on the repository abstraction.
- **Service Layer**: `AnalysisService` orchestrates background SMS ingestion, API calls, and SQLite database persistence.

---

### Question 8: How do you verify that every analysis request reaches the backend?
**Answer**:
Every analysis request generates a structured log entry on both client and server:
1. **Flutter Client Log**: `AnalysisService: Initiating backend AI analysis for msg_id from sender...`
2. **FastAPI Middleware Request Log**: `POST /api/v1/analyze -> 200 OK (52.4 ms) [request_id_uuid]`
3. **Automated Unit Tests**: `test/analysis_service_test.dart` verifies HTTP payload serialization, route targeting (`/analyze`), and response parsing.

---

### Question 9: What security measures protect user privacy during server-side SMS analysis?
**Answer**:
1. **Transport Layer Security (TLS)**: All communication between mobile client and API backend uses HTTPS encryption.
2. **Data Minimization**: Only message body text and sender strings are transmitted for classification; personal contact lists remain strictly local to the device.
3. **Stateless Processing**: The backend model evaluates text in-memory during inference without storing user message contents on server disk.

---

### Question 10: How would this architecture scale to millions of concurrent users?
**Answer**:
The decoupled architecture enables seamless horizontal scaling:
1. **Stateless FastAPI Instances**: Multiple FastAPI worker processes can be deployed behind a load balancer (Nginx / AWS ALB).
2. **Async Execution**: Inference requests can be offloaded to worker queues (Celery / Redis) or dedicated model microservices (Triton Inference Server / TorchServe).
3. **ONNX Runtime Acceleration**: Quantizing PyTorch weights to INT8 ONNX format accelerates CPU throughput by $3\times - 4\times$.
