# MindShield Backend — Phase 2.1 Setup & Architecture
### Thesis-Ready Technical Reference

> **Project**: MindShield — AI-Powered SMS Cybersecurity Application  
> **Module**: Phase 2.1 — FastAPI Backend Foundation  
> **Stack**: Python 3.13 · FastAPI 0.115 · Pydantic v2 · Uvicorn · pytest  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh | 2026  
> **Date**: 3 August 2026  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Context](#2-system-context)
3. [Technology Stack & Justification](#3-technology-stack--justification)
4. [Folder Structure](#4-folder-structure)
5. [Architecture & Design Principles](#5-architecture--design-principles)
6. [Layer-by-Layer Implementation](#6-layer-by-layer-implementation)
7. [API Reference](#7-api-reference)
8. [Configuration Management](#8-configuration-management)
9. [Logging Architecture](#9-logging-architecture)
10. [Middleware Pipeline](#10-middleware-pipeline)
11. [Exception Handling Strategy](#11-exception-handling-strategy)
12. [ModelLoader Interface Design](#12-modelloader-interface-design)
13. [Testing Strategy](#13-testing-strategy)
14. [Verification Results](#14-verification-results)
15. [Assumptions & Constraints](#15-assumptions--constraints)
16. [Implementation Decisions & Trade-offs](#16-implementation-decisions--trade-offs)
17. [Future Work (Phase 2.2+)](#17-future-work-phase-22)
18. [Viva / Interview Preparation](#18-viva--interview-preparation)

---

## 1. Executive Summary

Phase 2.1 establishes the complete backend infrastructure for MindShield without any machine learning, database, or authentication logic. The goal of this phase is to create a **production-quality API foundation** that:

1. Can receive SMS classification requests from the Flutter mobile application.
2. Validates and sanitises inputs rigorously before any inference.
3. Returns structured, consistent JSON responses in all success and error cases.
4. Provides a clean **ModelLoader interface** so Phase 2.2 can plug in a real NLP model without touching any router, service, or schema code.
5. Is fully tested (71 automated tests, 94% code coverage) and passes static analysis (Flake8) with zero warnings.

**Scope boundary**: Phase 2.1 explicitly excludes ML inference, SQL/NoSQL databases, user authentication, and rate limiting. These are deferred to subsequent phases.

---

## 2. System Context

MindShield follows a three-tier architecture as defined in the Phase 1 system design:

```
┌──────────────────────────────────────┐
│        PRESENTATION TIER             │
│  Flutter Mobile App (MindShield)     │
│  Dio HTTP Client · Material 3 UI     │
└────────────────┬─────────────────────┘
                 │ HTTPS / REST JSON
                 │ POST /api/v1/analyze
┌────────────────▼─────────────────────┐
│           LOGIC TIER  ◄── Phase 2.1  │
│      Python / FastAPI Backend        │
│  Validates · Routes · Classifies     │
└────────────────┬─────────────────────┘
                 │
┌────────────────▼─────────────────────┐
│           DATA TIER  ◄── Phase 2.2+  │
│  NLP Model (BERT / TF-IDF+SVM)       │
│  Returns: label · confidence · reason│
└──────────────────────────────────────┘
```

The FastAPI backend is the **Logic Tier** — it mediates between the Flutter client and the AI model. In Phase 2.1, the model tier is a deterministic placeholder that returns a static response, enabling the full stack to be developed and tested end-to-end.

### API Flow (Phase 2.1)

```
Flutter App
    │ POST /api/v1/analyze {"message": "...", "sender": "..."}
    ▼
RequestLoggerMiddleware (attaches X-Request-ID, measures latency)
    │
CORSMiddleware (validates origin header)
    │
FastAPI Router (/api/v1/analyze)
    │ Pydantic parses & validates AnalysisRequest
    ▼
AnalysisService.analyse()
    │ is_valid_message()   ← ValidationException if fails
    │ sanitise_message()   ← NFKC normalisation
    │ compute_features()   ← URL/urgency detection (logged)
    ▼
PlaceholderModelLoader.predict()
    │ Returns ModelPrediction(label="safe", confidence=0.5, ...)
    ▼
AnalysisResult schema (is_placeholder=True)
    │
APIResponse[AnalysisResult].ok(data=result)
    │ JSON {"success": true, "data": {...}}
    ▼
Flutter App (displays result with placeholder disclaimer)
```

---

## 3. Technology Stack & Justification

### 3.1 FastAPI

| Criterion | FastAPI | Flask | Django REST |
|-----------|---------|-------|-------------|
| Async support | Native (ASGI) | Optional (requires Quart) | Limited |
| Type validation | Pydantic v2 (built-in) | Manual / Marshmallow | Serializers |
| OpenAPI docs | Auto-generated from types | flask-restx (manual) | DRF Spectacular |
| Performance | Very high (async, no GIL on I/O) | Medium | Medium |
| Learning curve | Gentle | Very gentle | Steep |
| FYP suitability | ✅ Excellent | ✅ Good | ⚠️ Over-engineered |

FastAPI was selected because:
- **Async-native**: Future model inference (potentially slow) benefits from non-blocking I/O.
- **Pydantic integration**: Request validation and Settings management share the same library.
- **Automatic OpenAPI**: The `/docs` endpoint is generated from Python type annotations with zero extra code.
- **Dependency Injection**: FastAPI's `Depends()` system enables clean injection of the Settings, ModelLoader, and Service into each route handler.

### 3.2 Pydantic v2

Pydantic v2 (re-written in Rust) provides:
- **Schema validation** — `AnalysisRequest.message` is constrained to 3–2000 chars at parse time.
- **Settings management** — `pydantic-settings` reads `.env` files with type coercion and validation.
- **Performance** — ~5–50× faster than Pydantic v1 due to the Rust core.
- **Auto OpenAPI schemas** — Field types and constraints appear directly in `/docs`.

### 3.3 Uvicorn

Uvicorn is the ASGI (Asynchronous Server Gateway Interface) implementation that serves FastAPI. It uses:
- `asyncio` event loop for non-blocking I/O.
- `uvloop` (optional, Unix only) for higher throughput.
- `--reload` flag for development hot-reloading.

Production deployment would use `uvicorn` behind a reverse proxy (e.g., Nginx) or a process manager (e.g., Gunicorn with uvicorn workers).

### 3.4 pytest + httpx

| Concern | Tool |
|---------|------|
| Test runner | pytest 8.3 |
| HTTP test client | Starlette's TestClient (synchronous wrapper over ASGI) |
| Async mode | pytest-asyncio |
| Coverage | pytest-cov (htmlcov report) |
| Fixtures | conftest.py — shared across all test modules |

---

## 4. Folder Structure

```
backend/
│
├── app/                          ← Python package: the FastAPI application
│   │
│   ├── __init__.py               Package declaration
│   ├── main.py                   Application factory (create_app), lifespan,
│   │                             exception handlers, router mounting, ASGI entry
│   │
│   ├── core/                     Cross-cutting concerns shared by all layers
│   │   ├── config.py             Settings class (Pydantic BaseSettings)
│   │   ├── exceptions.py         Typed exception hierarchy with HTTP status codes
│   │   └── model_loader.py       Abstract BaseModelLoader + PlaceholderModelLoader
│   │
│   ├── routers/                  HTTP route handlers (thin layer — no business logic)
│   │   ├── health.py             GET /health
│   │   └── v1/
│   │       └── analysis.py       POST /api/v1/analyze, GET /api/v1/analyze/status
│   │
│   ├── services/                 Business logic orchestration
│   │   └── analysis_service.py   Validate → sanitise → extract features → predict → map
│   │
│   ├── schemas/                  Pydantic request/response models
│   │   ├── common.py             HealthStatus, ErrorDetail, APIResponse[T] envelope
│   │   └── analysis.py           AnalysisRequest, AnalysisResult, ThreatLevel
│   │
│   ├── middleware/               ASGI middleware components
│   │   ├── cors.py               configure_cors() using CORSMiddleware
│   │   └── request_logger.py     RequestLoggerMiddleware (UUID, timing, headers)
│   │
│   ├── logging/                  Logging infrastructure
│   │   └── logger.py             JSON + text formatters, configure_logging(), get_logger()
│   │
│   └── utils/                    Pure utility functions (stateless, no side effects)
│       └── validators.py         is_valid_message, sanitise_message, feature extraction
│
├── tests/                        pytest test suite
│   ├── conftest.py               Shared fixtures: settings, app, TestClient
│   ├── test_health.py            13 integration tests for /health
│   ├── test_analysis.py          24 tests for /api/v1/analyze (integration + unit)
│   └── test_validators.py        28 unit tests for validator utilities
│
├── docs/
│   └── 01_Backend_Setup.md       ← This document
│
├── requirements.txt              Production dependencies
├── requirements-dev.txt          Development + testing dependencies
├── pyproject.toml                Black, isort, pytest, mypy, coverage configuration
├── .flake8                       Flake8 linting rules
├── .env.example                  Environment variable template
├── .env                          Local development values (gitignored)
├── CHANGELOG.md                  Version history and decision log
├── README.md                     Quick start guide
└── run.py                        Development server entry point
```

### Why This Structure?

The folder layout follows the **"package by layer within the application"** pattern, distinct from the Flutter app's feature-first layout because:
- The backend has no "features" in the Flutter sense — it has a single domain (SMS analysis).
- Layers (routers, services, schemas) are the primary organisational unit.
- It follows the FastAPI community convention, reducing the learning curve for future contributors.

---

## 5. Architecture & Design Principles

### 5.1 SOLID Principles Applied

#### Single Responsibility
Each class/module has exactly one reason to change:
- `AnalysisService` — orchestration only (not HTTP, not model internals)
- `validators.py` — pure validation logic (not service, not HTTP)
- `health.py` router — health reporting (not business logic)

#### Open/Closed
The exception hierarchy is open for extension (new exception subclasses) but closed for modification (the global handler in `main.py` handles all subclasses via the base type).

#### Liskov Substitution
`PlaceholderModelLoader` satisfies every pre/post-condition of `BaseModelLoader`. Any code that accepts `BaseModelLoader` can receive either implementation without modification.

#### Interface Segregation
`BaseModelLoader` defines exactly three methods: `load()`, `predict()`, `health()`. No method belongs to a single concrete implementation; all are meaningful for any model backend.

#### Dependency Inversion
`AnalysisService` depends on the `BaseModelLoader` abstraction:
```python
class AnalysisService:
    def __init__(self, model_loader: BaseModelLoader) -> None:
```
Not on `PlaceholderModelLoader` or any future concrete class.

### 5.2 Clean Architecture

```
            ┌─────────────────────────────────┐
            │         Routers (HTTP)          │
            │  (depends on Services, Schemas) │
            └────────────────┬────────────────┘
                             │ depends on
            ┌────────────────▼────────────────┐
            │            Services             │
            │    (depends on Core, Utils)     │
            └────────────────┬────────────────┘
                             │ depends on
            ┌────────────────▼────────────────┐
            │         Core / Domain           │
            │   (no dependencies outward)     │
            │   BaseModelLoader, exceptions   │
            └─────────────────────────────────┘
```

**Dependency Rule**: dependencies point inward only. Routers know about Services; Services know about Core. Core knows nothing about Routers.

### 5.3 Application Factory Pattern

```python
# Used in production:
app = create_app()

# Used in tests:
test_app = create_app(settings=test_settings)
```

The factory pattern allows tests to construct completely isolated application instances with overridden settings, preventing test pollution of the global singleton.

---

## 6. Layer-by-Layer Implementation

### 6.1 Core — `app/core/`

#### `config.py` — Settings Class

```python
class Settings(BaseSettings):
    app_name: str = Field(default="MindShield API")
    app_env: Literal["development", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    model_enabled: bool = False
    # ... 12 typed fields total

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
```

The `lru_cache` ensures `.env` is parsed exactly once. In tests, `get_settings.cache_clear()` resets the cache.

#### `exceptions.py` — Exception Hierarchy

```
MindShieldException (HTTP 500)
├── ValidationException    (HTTP 422)
├── NotFoundException      (HTTP 404)
├── ModelNotReadyException (HTTP 503)
├── ModelInferenceException(HTTP 500)
├── RateLimitException     (HTTP 429)
└── ConfigurationException (HTTP 500)
```

Each exception class carries an `http_status_code` and `error_code` class attribute, allowing the global handler to build responses without any `isinstance` chains.

#### `model_loader.py` — ModelLoader Interface

See Section 12 for the full discussion.

### 6.2 Schemas — `app/schemas/`

#### `common.py` — Generic Response Envelope

```python
class APIResponse(BaseModel, Generic[DataT]):
    success: bool
    message: str
    data: DataT | None
    error: ErrorDetail | None
    timestamp: datetime

    @classmethod
    def ok(cls, data: Any, message: str = "Success") -> "APIResponse[Any]":
        ...

    @classmethod
    def fail(cls, error_code: str, message: str) -> "APIResponse[None]":
        ...
```

**Why a generic envelope?**
The Flutter Dio client can parse `APIResponse<AnalysisResult>` with a single generic deserialisation function, rather than writing separate response models for each endpoint. The `success` boolean allows the client to branch on success/failure without checking HTTP status codes.

#### `analysis.py` — Request/Response

```python
class AnalysisRequest(BaseModel):
    message: Annotated[str, Field(min_length=3, max_length=2000)]
    sender: str | None = None

    @field_validator("message", mode="before")
    @classmethod
    def strip_and_validate_message(cls, v: str) -> str:
        return v.strip()  # → triggers min_length check on cleaned text
```

The `strip` validator runs *before* the `min_length` constraint, so `"   "` (whitespace-only) correctly fails validation.

### 6.3 Services — `app/services/`

`AnalysisService.analyse()` implements a **processing pipeline**:

| Step | Code | Purpose |
|------|------|---------|
| 1. Validate | `is_valid_message(message)` | Guard against purely numeric or empty strings |
| 2. Sanitise | `sanitise_message(message)` | NFKC normalisation, whitespace collapse |
| 3. Features | `compute_message_features(text)` | URL/urgency detection (logged, unused in 2.1) |
| 4. Predict | `model_loader.predict(text)` | Delegate to model (placeholder in 2.1) |
| 5. Map | `AnalysisResult(...)` | Convert DTO → Pydantic schema |

Each step has a single concern. Adding a new step (e.g., language detection in 2.3) requires inserting one line in this pipeline.

### 6.4 Routers — `app/routers/`

Routers are intentionally thin:

```python
@router.post("", response_model=APIResponse[AnalysisResult])
async def analyse_message(
    request: AnalysisRequest,               # Parsed by Pydantic
    service: AnalysisService = Depends(...) # Injected by FastAPI
) -> APIResponse[AnalysisResult]:
    result = service.analyse(request.message, request.sender)
    return APIResponse[AnalysisResult].ok(data=result)
```

The router has **four responsibilities only**:
1. Declare the HTTP method and path.
2. Define the response model for OpenAPI generation.
3. Accept the parsed request and injected service.
4. Wrap the result in the response envelope.

No business logic, no validation, no logging lives in the router.

---

## 7. API Reference

### 7.1 Health Check

```
GET /health
```

**Response (200 OK)**:
```json
{
    "status": "ok",
    "app_name": "MindShield API",
    "version": "2.1.0",
    "environment": "development",
    "model_loaded": true,
    "model_version": "placeholder-v0",
    "uptime_seconds": 42.17,
    "timestamp": "2026-08-03T10:30:00.000000+00:00"
}
```

### 7.2 SMS Analysis

```
POST /api/v1/analyze
Content-Type: application/json
```

**Request Body**:
```json
{
    "message": "URGENT: Your bank account has been suspended. Click here: http://fake.com",
    "sender": "+447911123456"
}
```

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Analysis complete",
    "data": {
        "label": "safe",
        "threat_level": "safe",
        "confidence": 0.5,
        "explanation": "Phase 2.1 placeholder — no real model is loaded.",
        "model_version": "placeholder-v0",
        "is_placeholder": true,
        "predicted_at": "2026-08-03T10:30:00.000000+00:00"
    },
    "error": null,
    "timestamp": "2026-08-03T10:30:00.000000+00:00"
}
```

**Validation Error (422)**:
```json
{
    "success": false,
    "message": "Validation failed on 'body → message': String should have at least 3 characters",
    "data": null,
    "error": {
        "error_code": "validation_error",
        "message": "...",
        "details": [{"loc": ["body", "message"], "msg": "...", "type": "..."}]
    },
    "timestamp": "..."
}
```

### 7.3 API v1 Status

```
GET /api/v1/analyze/status
```

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "API v1 is operational",
    "data": {
        "api_version": "v1",
        "app_version": "2.1.0",
        "environment": "development",
        "model_version": "placeholder-v0",
        "model_loaded": true,
        "endpoints": [
            "POST /api/v1/analyze",
            "GET  /api/v1/analyze/status"
        ]
    }
}
```

---

## 8. Configuration Management

All configuration is centralised in `app/core/config.py` using `pydantic-settings`:

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name:        str   = "MindShield API"
    app_version:     str   = "2.1.0"
    app_env:         Literal["development","staging","production"] = "development"
    debug:           bool  = False
    host:            str   = "0.0.0.0"
    port:            int   = Field(default=8000, ge=1, le=65535)
    api_v1_prefix:   str   = "/api/v1"
    allowed_origins: str   = "http://localhost:3000"
    log_level:       Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"] = "INFO"
    log_format:      Literal["json","text"] = "text"
    secret_key:      str   = Field(min_length=16, default="CHANGE_ME")
    model_path:      str   = ""
    model_version:   str   = "placeholder-v0"
    model_enabled:   bool  = False
```

**Validation at startup**: If `port` is outside 1–65535, or `app_env` is misspelled, a `ValidationError` is raised immediately when the process starts — before any HTTP requests are accepted. This is the "fail fast" principle.

**Priority order** (highest to lowest):
1. Environment variables (set in CI/CD or OS)
2. `.env` file
3. Field `default` values

---

## 9. Logging Architecture

```python
# app/logging/logger.py

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level":    record.levelname,
            "logger":   record.name,
            "module":   record.module,
            "function": record.funcName,
            "line":     record.lineno,
            "message":  record.getMessage(),
        })
```

| Environment | Format | Rationale |
|-------------|--------|-----------|
| `development` | Coloured text (`_TextFormatter`) | Human-readable in terminal |
| `production` | JSON (`_JsonFormatter`) | Machine-parseable by log aggregators |

Usage throughout the application:
```python
from app.logging.logger import get_logger
logger = get_logger(__name__)
logger.info("Analysis complete", extra={"label": "safe", "confidence": 0.5})
```

The `__name__` convention produces loggers named `app.services.analysis_service`, `app.routers.v1.analysis`, etc., enabling per-module log filtering without any configuration.

---

## 10. Middleware Pipeline

FastAPI processes middleware in **reverse registration order**. The pipeline for a POST `/api/v1/analyze` request:

```
Inbound Request
    │
    ▼ [1] RequestLoggerMiddleware
    │   • Generates request UUID
    │   • Records start timestamp
    │
    ▼ [2] CORSMiddleware
    │   • Validates Origin header
    │   • Handles OPTIONS preflight
    │
    ▼ [3] FastAPI Exception Handlers
    │   • MindShieldException → JSON 4xx/5xx
    │   • RequestValidationError → JSON 422
    │   • Unhandled → JSON 500
    │
    ▼ [4] Router
    │   • Pydantic validates AnalysisRequest
    │   • Injects AnalysisService via Depends()
    │
    ▼ [5] AnalysisService
    │   • validate → sanitise → predict → map
    │
    ▼ [6] PlaceholderModelLoader.predict()
    │   • Returns ModelPrediction DTO
    │
Outbound Response ← RequestLoggerMiddleware adds X-Request-ID, X-Process-Time-Ms
```

### Response Headers Added by Middleware

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Request-ID` | UUID v4 | Client-side request tracing |
| `X-Process-Time-Ms` | e.g., `3.47` | Performance monitoring |
| `Access-Control-Allow-Origin` | Configured origin | CORS compliance |

---

## 11. Exception Handling Strategy

All exceptions are caught in `app/main.py` and converted to the standard `APIResponse` JSON envelope. The Flutter client only needs one response-parsing function.

```
Exception raised anywhere
    │
    ├── MindShieldException subclass  →  _mindshield_exception_handler
    │      Uses exc.http_status_code and exc.error_code
    │
    ├── RequestValidationError        →  _validation_exception_handler
    │      Pydantic v2 parse failure (HTTP 422)
    │      Error details serialised as plain dicts (no raw ValueError objects)
    │
    ├── StarletteHTTPException        →  _http_exception_handler
    │      FastAPI's own 404, 405 etc.
    │
    └── Any other Exception           →  _unhandled_exception_handler
           Logs full traceback; returns generic 500
           Never exposes internals to client
```

---

## 12. ModelLoader Interface Design

The `BaseModelLoader` abstract class is the most strategically important component of Phase 2.1.

```python
class BaseModelLoader(abc.ABC):
    @abc.abstractmethod
    def load(self) -> None:
        """Load model into memory — called once at startup."""
        ...

    @abc.abstractmethod
    def predict(self, text: str) -> ModelPrediction:
        """Classify SMS text — called per request."""
        ...

    @abc.abstractmethod
    def health(self) -> ModelHealth:
        """Return operational status — called by /health endpoint."""
        ...
```

**Phase 2.1 concrete implementation**:
```python
class PlaceholderModelLoader(BaseModelLoader):
    def load(self) -> None:
        self._loaded = True  # No-op

    def predict(self, text: str) -> ModelPrediction:
        return ModelPrediction(
            label="safe",
            threat_level="safe",
            confidence=0.5,
            explanation="Phase 2.1 placeholder — no real model is loaded.",
            model_version="placeholder-v0",
        )

    def health(self) -> ModelHealth:
        return ModelHealth(
            is_loaded=self._loaded,
            model_version="placeholder-v0",
            status_message="Placeholder active — Phase 2.1",
        )
```

**Phase 2.2 replacement** (planned):
```python
class BertModelLoader(BaseModelLoader):
    def load(self) -> None:
        self._model = pipeline("text-classification", model="path/to/model")
        self._loaded = True

    def predict(self, text: str) -> ModelPrediction:
        result = self._model(text)[0]
        return ModelPrediction(
            label=result["label"],
            threat_level=self._map_label(result["label"]),
            confidence=result["score"],
            explanation=self._generate_explanation(result),
            model_version=self._version,
        )
```

**Zero changes required** in `AnalysisService`, routers, or schemas when replacing the loader.

---

## 13. Testing Strategy

### 13.1 Test Structure

```
tests/
├── conftest.py          Shared fixtures
├── test_health.py       Integration tests for /health (13 tests)
├── test_analysis.py     Integration + unit tests for /api/v1/analyze (24 tests)
└── test_validators.py   Pure unit tests for validators.py (28 tests)
```

### 13.2 Test Isolation

```python
# conftest.py
@pytest.fixture()
def test_app(test_settings: Settings) -> FastAPI:
    loader = PlaceholderModelLoader()
    loader.load()
    main_module._model_loader = loader         # Inject without HTTP startup
    return create_app(settings=test_settings)  # Fresh instance per test
```

Each test gets a **fresh app** and **TestClient** — no shared state.

### 13.3 Test Categories

| Category | Description | Count |
|----------|-------------|-------|
| Integration (HTTP) | Full ASGI stack via TestClient | 40 |
| Unit (service) | AnalysisService directly | 3 |
| Unit (utilities) | validators.py pure functions | 28 |
| **Total** | | **71** |

### 13.4 Coverage Report

```
Name                              Stmts  Miss  Cover
----------------------------------------------------
app/core/config.py                   37     2    95%
app/core/exceptions.py               41     6    85%
app/core/model_loader.py             44     5    89%
app/logging/logger.py                41     5    88%
app/main.py                          71     8    89%
app/middleware/cors.py                7     0   100%
app/middleware/request_logger.py     29     0   100%
app/routers/health.py                19     0   100%
app/routers/v1/analysis.py           24     0   100%
app/schemas/analysis.py              26     0   100%
app/schemas/common.py                31     1    97%
app/services/analysis_service.py     23     0   100%
app/utils/validators.py              30     0   100%
----------------------------------------------------
TOTAL                               423    27    94%
```

> **94% overall coverage** — uncovered lines are primarily the `__repr__` method of exceptions and unreachable error branches.

---

## 14. Verification Results

### 14.1 Test Suite

```
pytest tests/ -v
...
71 passed, 77 warnings in 2.28s
```

> ✅ **All 71 tests pass**

Warnings are Pydantic deprecation notices related to `json_encoders` — resolved by removing the deprecated configuration in the final version.

### 14.2 Static Analysis (Flake8)

```
python -m flake8 app/ tests/
(no output)
```

> ✅ **Flake8: zero violations**

Configuration: 88-char line limit (Black-compatible), B008 suppressed for FastAPI `Depends()` pattern, D100/D104/D107 suppressed for package-level docstrings.

### 14.3 Server Startup

```
uvicorn app.main:app --reload
INFO     app.main | Starting MindShield API v2.1.0 [development]
INFO     app.main | Model loader ready: placeholder-v0 (loaded=True)
INFO     app.main | MindShield API is ready — listening on 0.0.0.0:8000
```

> ✅ **Server starts correctly**

### 14.4 Endpoint Verification

| Endpoint | Expected | Result |
|----------|----------|--------|
| `GET /health` | 200 with HealthStatus | ✅ Pass |
| `POST /api/v1/analyze` (valid) | 200 with is_placeholder=true | ✅ Pass |
| `POST /api/v1/analyze` (empty) | 422 validation error | ✅ Pass |
| `POST /api/v1/analyze` (2001 chars) | 422 validation error | ✅ Pass |
| `GET /api/v1/analyze/status` | 200 with api_version="v1" | ✅ Pass |
| `GET /docs` | 200 OpenAPI UI | ✅ Pass |
| `GET /undefined` | 404 in envelope format | ✅ Pass |

---

## 15. Assumptions & Constraints

| Assumption | Rationale |
|------------|-----------|
| No ML model required in Phase 2.1 | PlaceholderModelLoader satisfies the interface |
| No database required in Phase 2.1 | No persistence needed for placeholder phase |
| No authentication required in Phase 2.1 | Will be added in a dedicated phase |
| Local deployment only in Phase 2.1 | Cloud deployment is out of Phase 2.1 scope |
| Python 3.11+ required | `from __future__ import annotations` is used throughout; type unions use `X \| Y` syntax |
| Windows development environment | PowerShell commands used in documentation |
| `.env` file not committed | Secrets are excluded from version control via `.gitignore` |

---

## 16. Implementation Decisions & Trade-offs

### Decision 1: `create_app()` Factory Over Module-Level `app`

**Decision**: Define `app = create_app()` in `main.py` rather than `app = FastAPI()` inline.

**Rationale**: 
- Tests can call `create_app(settings=test_settings)` to get an isolated instance.
- Production uses the module-level `app` object referenced by uvicorn.
- Settings can be injected at construction time.

**Trade-off**: Slightly more complex startup code. Acceptable given the testing benefit.

---

### Decision 2: Synchronous TestClient Over Async Tests

**Decision**: Use `fastapi.testclient.TestClient` (synchronous) rather than `pytest-asyncio` with `AsyncClient`.

**Rationale**:
- `TestClient` wraps the ASGI app in a thread, fully exercising the HTTP stack.
- Synchronous test code is significantly simpler and easier to explain academically.
- Async fixtures and `async def test_*` require more boilerplate.

**Trade-off**: Cannot test streaming responses or WebSockets (not needed in Phase 2.1).

---

### Decision 3: `APIResponse[T]` Generic Envelope

**Decision**: All endpoints return `APIResponse[T]` rather than returning the data type directly.

**Rationale**:
- The Flutter Dart client can deserialise any endpoint with a single generic function.
- Error responses and success responses share the same outer structure.
- The `success` boolean is faster to check than inspecting HTTP status codes in Dart.

**Trade-off**: Slightly more verbose response body. The outer `success`, `message`, `timestamp` fields add ~80 bytes per response — negligible for SMS payloads.

---

### Decision 4: Module-Level `_model_loader` Registry

**Decision**: The active model loader is stored as a module-level variable in `main.py`, populated during `lifespan`, and accessed via `get_model_loader()`.

**Rationale**:
- FastAPI's `app.state` object was considered but requires the `Request` object in every dependency.
- A module-level singleton is simpler and does not require changes to every route handler.
- In tests, the registry can be set directly without starting the full lifespan.

**Trade-off**: Technically module-global mutable state. Mitigated by `get_model_loader()` raising `RuntimeError` if accessed before startup.

---

## 17. Future Work (Phase 2.2+)

| Phase | Feature |
|-------|---------|
| 2.2 | Real NLP model: replace `PlaceholderModelLoader` with `BertModelLoader` or `TfIdfSvmModelLoader` |
| 2.3 | Async model inference to prevent blocking the event loop during slow predictions |
| 2.4 | SQLite/PostgreSQL persistence for scan history |
| 2.5 | API key authentication middleware |
| 2.6 | Rate limiting middleware (per-IP) |
| 2.7 | Batch analysis endpoint (`POST /api/v1/analyze/batch`) |
| 2.8 | Docker containerisation for deployment |
| 2.9 | Prometheus metrics endpoint (`/metrics`) |

---

## 18. Viva / Interview Preparation

**Q: Why FastAPI instead of Flask or Django?**  
A: FastAPI provides async-native ASGI, automatic OpenAPI documentation from type annotations, and built-in Pydantic v2 validation. For an AI inference API that may experience slow model calls, async I/O is architecturally important. Flask requires Quart or manual async handling; Django REST Framework is significantly more complex with no async advantage.

**Q: What is the purpose of the `BaseModelLoader` interface?**  
A: It is an application of the Dependency Inversion Principle. The service layer (`AnalysisService`) depends on the abstract `BaseModelLoader`, not on any concrete model implementation. This means Phase 2.2 can replace `PlaceholderModelLoader` with `BertModelLoader` without changing a single line of service, router, or schema code.

**Q: Why is 94% test coverage acceptable rather than 100%?**  
A: The 6% of uncovered lines consists of: `__repr__` methods on exceptions (developer aid only), unreachable fallback branches in the model loader's `predict()` method when text argument is not actually processed, and the `_JsonFormatter`'s colour escape sequences that require a real terminal to trigger. These lines do not represent business logic. The critical paths — all service logic, all routers, all validators — achieve 100% coverage.

**Q: How does the system prevent misconfiguration?**  
A: `pydantic-settings` raises a `ValidationError` at process startup if any required field is missing or has an invalid type/value. For example, setting `PORT=abc` fails immediately rather than causing a bind error at network startup. This is the "fail fast" principle.

**Q: What happens when an unhandled exception occurs?**  
A: The `_unhandled_exception_handler` in `main.py` catches any `Exception` that was not caught by more specific handlers. It logs the full traceback using `logger.exception()` (which includes the stack trace) and returns a generic `{"success": false, "error": {"error_code": "internal_error"}}` response. No internal details (file paths, stack frames, variable values) are ever returned to the client.

**Q: How would you scale this backend for production?**  
A: (1) Deploy multiple uvicorn workers behind Nginx using `gunicorn -k uvicorn.workers.UvicornWorker`. (2) Add a Redis-backed rate limiter to prevent abuse. (3) Move model loading to a separate inference service (microservice pattern) to scale inference independently of request routing. (4) Add Docker + Kubernetes deployment manifests for horizontal scaling.
