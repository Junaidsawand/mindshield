# MindShield — Backend Engineering & FastAPI Viva Guide

> **Module**: Python FastAPI Backend Foundation (Phase 2.1)  
> **Focus**: FastAPI 0.115, Pydantic v2, Uvicorn, ASGI, BaseModelLoader Interface, pytest  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding

### Q1: Why did you choose FastAPI over Flask or Django REST Framework?
**Model Answer:**  
FastAPI was selected for three primary reasons:
1. **Async-Native (ASGI)**: Built on Starlette and `asyncio`, FastAPI handles non-blocking I/O natively, which is critical for serving slow machine learning inference calls without blocking incoming HTTP requests.
2. **Built-in Type Validation**: Powered by Pydantic v2 (written in Rust), request payloads are validated and sanitized at parse time before reaching business logic.
3. **Automated OpenAPI Documentation**: FastAPI automatically generates interactive OpenAPI/Swagger schemas at `/docs` directly from Python type hints, eliminating documentation drift.

---

### Q2: What is the role of ASGI versus WSGI in Python web applications?
**Model Answer:**  
WSGI (Web Server Gateway Interface) is a synchronous, single-response specification used by traditional frameworks like Flask and Django. WSGI processes block a worker thread while waiting for I/O operations (like model inference or database queries). ASGI (Asynchronous Server Gateway Interface) extends WSGI with asynchronous capabilities, allowing a single Uvicorn server worker to process thousands of concurrent connections using Python's event loop.

---

## Section B — Design Decision Justification

### Q3: Explain the purpose of the `BaseModelLoader` abstract interface.
**Model Answer:**  
`BaseModelLoader` is a direct application of the **Dependency Inversion Principle** (SOLID). `AnalysisService` depends on the abstract `BaseModelLoader` contract (`load()`, `predict()`, `health()`), rather than any concrete ML implementation. In Phase 2.1, we implemented `PlaceholderModelLoader`. In Phase 2.2, we can swap in `BertModelLoader` or `TfIdfSvmModelLoader` without changing a single line of router, service, or schema code.

- **Interface Contract**:
```python
class BaseModelLoader(abc.ABC):
    @abc.abstractmethod
    def load(self) -> None: ...
    @abc.abstractmethod
    def predict(self, text: str) -> ModelPrediction: ...
    @abc.abstractmethod
    def health(self) -> ModelHealth: ...
```

---

### Q4: Why return a generic `APIResponse[T]` envelope instead of raw JSON dictionaries?
**Model Answer:**  
The generic `APIResponse[T]` envelope standardizes response structure across all endpoints: `{"success": bool, "message": str, "data": T, "error": ErrorDetail, "timestamp": str}`. This allows the Flutter Dio client to deserialize all backend responses using a single generic parser, and allows the client to branch instantly on `success` without inspecting HTTP status codes.

---

## Section C — Implementation & Technical Depth

### Q5: How does Pydantic v2 sanitize input and handle 422 validation errors?
**Model Answer:**  
Pydantic's `@field_validator("message", mode="before")` strips leading/trailing whitespace before enforcing `min_length=3` and `max_length=2000` constraints. If a client sends an invalid payload (e.g. whitespace-only `"   "` or missing fields), FastAPI catches the `RequestValidationError` and passes it to `_validation_exception_handler` in `main.py`, which formats a clean HTTP 422 JSON response inside the standard `APIResponse` envelope.

- **Coverage Note**: The test suite includes 71 automated tests achieving 94% code coverage, verified via `pytest --cov=app`.

---

## Section D — Limitations, Risks & Future Work

### Q6: How will the backend scale when heavy ML models are introduced in Phase 2.2?
**Model Answer:**  
In Phase 2.2+, heavy PyTorch/BERT model inference could saturate CPU/GPU resources. To scale production deployment, we will:
1. Run Uvicorn workers managed by Gunicorn (`gunicorn -w 4 -k uvicorn.workers.UvicornWorker`).
2. Implement Redis-backed sliding-window rate limiting.
3. Offload inference from HTTP worker threads to a dedicated Celery/Triton worker pool via async message queues.

---
*MindShield Backend Viva Guide · Final Year Project 2026*
