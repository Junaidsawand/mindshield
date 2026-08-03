# Changelog

All notable changes to the MindShield backend are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] — 2026-08-03

### Added — Phase 2.1: FastAPI Backend Foundation

#### Project Infrastructure
- `requirements.txt` — production dependencies: FastAPI 0.115.6, Uvicorn 0.32.1, Pydantic v2, python-dotenv
- `requirements-dev.txt` — development dependencies: pytest 8.3.4, pytest-cov, flake8, black, isort, mypy
- `pyproject.toml` — unified project configuration for Black, isort, pytest, mypy, and coverage
- `.flake8` — linting configuration aligned with Black (88 char line length, B008 ignore for FastAPI patterns)
- `.env.example` — complete environment variable template with documentation
- `.env` — local development environment (gitignored)

#### Application Layer (`app/`)
- `app/__init__.py` — Application package declaration
- `app/main.py` — FastAPI application factory (`create_app()`), lifespan context manager, global exception handlers (MindShieldException, RequestValidationError, HTTPException, unhandled), router registration, ASGI entry point

#### Core Layer (`app/core/`)
- `app/core/config.py` — `Settings` class using `pydantic-settings` BaseSettings; reads from `.env` with type validation; `get_settings()` singleton via `lru_cache`; includes `cors_origins`, `is_production`, `is_development` properties
- `app/core/exceptions.py` — Typed exception hierarchy: `MindShieldException` (root), `ValidationException` (422), `NotFoundException` (404), `ModelNotReadyException` (503), `ModelInferenceException` (500), `RateLimitException` (429), `ConfigurationException` (500)
- `app/core/model_loader.py` — `BaseModelLoader` abstract interface with `load()`, `predict()`, `health()` methods; `ModelPrediction` and `ModelHealth` frozen dataclasses; `PlaceholderModelLoader` stub implementation for Phase 2.1

#### Logging (`app/logging/`)
- `app/logging/logger.py` — Structured logging: `_JsonFormatter` (single-line JSON per record), `_TextFormatter` (ANSI-coloured human-readable), `configure_logging()` factory, `get_logger()` helper

#### Schemas (`app/schemas/`)
- `app/schemas/common.py` — `HealthStatus`, `ErrorDetail`, `APIResponse[T]` generic envelope with `.ok()` and `.fail()` class methods
- `app/schemas/analysis.py` — `AnalysisRequest` (Pydantic model with `message` validator, length constraints), `AnalysisResult`, `ThreatLevel` literal type

#### Middleware (`app/middleware/`)
- `app/middleware/cors.py` — `configure_cors()`: CORSMiddleware with explicit method/header allowlists, 24h preflight cache
- `app/middleware/request_logger.py` — `RequestLoggerMiddleware`: per-request UUID injection, `X-Request-ID` / `X-Process-Time-Ms` headers, silent-path filtering

#### Services (`app/services/`)
- `app/services/analysis_service.py` — `AnalysisService`: validates → sanitises → extracts features → delegates to model loader → maps to response schema; fully decoupled from HTTP layer

#### Utilities (`app/utils/`)
- `app/utils/validators.py` — Pure validation/sanitisation functions: `is_valid_message`, `is_valid_sender`, `sanitise_message` (NFKC Unicode), `contains_url`, `contains_urgency_language`, `compute_message_features`

#### Routers (`app/routers/`)
- `app/routers/health.py` — `GET /health`: returns `HealthStatus` with uptime, model status, environment; dependency-injected settings and model loader
- `app/routers/v1/analysis.py` — `POST /api/v1/analyze`: SMS classification endpoint; `GET /api/v1/analyze/status`: API version information

#### Tests (`tests/`)
- `tests/conftest.py` — Shared fixtures: `test_settings`, `test_app`, `client` (TestClient)
- `tests/test_health.py` — 13 integration tests for `/health` endpoint
- `tests/test_analysis.py` — 24 integration + unit tests for `/api/v1/analyze`
- `tests/test_validators.py` — 28 unit tests for pure validation utilities

#### Documentation (`backend/docs/`)
- `docs/01_Backend_Setup.md` — Thesis-ready documentation: architecture, folder structure, implementation decisions, technology justification, API reference, verification results

#### Runtime
- `run.py` — Uvicorn entry point with settings-driven host/port/reload configuration
- `README.md` — Quick start guide, project structure overview, API reference

### Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI over Flask | Async-native, automatic OpenAPI docs, Pydantic integration |
| Pydantic BaseSettings | Type-safe config, validated at startup, zero misconfiguration |
| `create_app()` factory | Enables test isolation without global state |
| Lifespan context manager | FastAPI 0.93+ recommended pattern over `@app.on_event` |
| `BaseModelLoader` interface | Dependency Inversion — swap model without touching router/service |
| Generic `APIResponse[T]` envelope | Consistent parsing on Flutter client side |
| Per-request UUID | End-to-end request tracing across distributed logs |
| `lru_cache` on `get_settings()` | Parse `.env` once; consistent config across all modules |

### Verification Results

- **Tests**: All tests pass (pytest)
- **Linting**: Clean (flake8)  
- **Server**: Starts successfully, all endpoints reachable
- **OpenAPI**: `/docs` and `/redoc` available in development mode

---

## [Unreleased] — Phase 2.2 (Planned)

### Planned
- Real NLP model integration replacing `PlaceholderModelLoader`
- Model warm-up with timeout handling
- Confidence calibration post-processing
- Batch analysis endpoint (`POST /api/v1/analyze/batch`)
