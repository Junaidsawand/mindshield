# Changelog

All notable changes to the MindShield backend are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] — 2026-08-04

### Added — Phase 3.1: UCI Dataset Preparation & Exploratory Data Analysis (EDA)

#### Dataset-Agnostic & Model-Compatible Pipeline Architecture (`app/data/`)
- `DatasetConfig` (`app/data/config.py`) — configuration model parameterizing URLs, delimiters, column mappings, label mappings, random seeds, and split ratios. Built-in pre-configurations for `UCI_SMS_CONFIG` and `PAKSCAM_CONFIG_TEMPLATE`.
- `DatasetDownloader` (`app/data/downloader.py`) — dataset retrieval manager with zip extraction, retry handling, directory setup, and offline mock fallback generation.
- `DatasetLoader` (`app/data/loader.py`) — raw dataset ingestion reading TSV/CSV/JSON files and standardizing column names.
- `SMSDatasetCleaner` (`app/data/cleaner.py`) — non-destructive text cleaner for DistilBERT transformer compatibility. Preserves case, punctuation, URLs, phone numbers, and emojis; strips null bytes; normalizes line endings; removes 405 exact duplicates; generates stratified 80/10/10 splits (`train`, `val`, `test`, `cleaned_full`).
- `SMSDatasetEDA` (`app/data/eda.py`) — exploratory data analysis engine computing class distribution, balance ratio (6.92:1 ham:spam), text length summary statistics ($\mu, \sigma, Q_1, Q_2, Q_3, \text{IQR}$), missing values, duplicate counts, and top n-gram frequencies.
- `SMSDatasetVisualizer` (`app/data/visualizer.py`) — publication-grade (300 DPI) figure generator producing 6 charts (`01_class_distribution.png`, `02_message_length_distribution.png`, `03_length_boxplots.png`, `04_top_words_comparison.png`, `05_ngram_frequency.png`, `06_split_distribution.png`).
- `GenericDataPipeline` (`app/data/pipeline.py`) — reproducible pipeline orchestrator managing download -> load -> clean -> eda -> split -> save datasets & metadata -> generate figures.
- `scripts/prepare_uci_dataset.py` — CLI execution runner (`python scripts/prepare_uci_dataset.py`).

#### Automated Test Suite & Verification (`tests/test_data_pipeline.py`)
- Created `tests/test_data_pipeline.py` — comprehensive unit & integration tests covering config validation, downloader fallbacks, raw loading, non-destructive cleaning, EDA statistics, stratified splitting, publication figure generation, end-to-end pipeline execution, and PakScam template dataset-agnostic compatibility.

#### Thesis Documentation & Viva Artifacts
- `backend/docs/06_UCI_Dataset_EDA.md` — 8-section thesis technical reference with Mermaid class, sequence, and data flow diagrams, empirical EDA summary tables, length statistics breakdown, and PakScam integration blueprint.
- `docs/thesis-preparation/Dataset_Preparation_Viva.md` — 10 academic Q&A questions for BS Computer Science FYP viva defense.

---

## [2.5.0] — 2026-08-03

### Added — Phase 2.5: Backend Production Verification & Quality Audit

#### Empirical System Verification
- **Automated Test Suite**: 169 unit & integration tests executed via `pytest` (**100% pass rate in 9.45s**).
- **Code Coverage**: Achieved **92% total statement coverage** (100% on routers, schemas, validators, middleware).
- **Static Analysis**: Verified PEP 8 code compliance via `flake8` (**FLAKE8_CLEAN, 0 violations**).
- **Application Startup**: Smoke test verified clean `lifespan` initialization and route registration for 7 routes.
- **Health Probe**: Empirical verification of `GET /health` returning `200 OK`, `model_loaded: true`, uptime metrics, `x-request-id`, and `x-process-time-ms` headers.
- **Analysis Endpoint**: Verified `POST /api/v1/analyze` classification pipeline across Phishing, Suspicious, Safe, and Credential Harvest inputs.
- **OpenAPI Audit**: Confirmed valid OpenAPI 3.1.0 specification (`GET /openapi.json`) with 4 rich request/response examples.
- **Global Error Handling**: Verified unified `APIResponse` JSON error envelopes for HTTP 400, 404, 422, 500, and 503 error codes.

#### Thesis Documentation & Viva Artifacts
- `backend/docs/05_Backend_Verification.md` — 9-section technical verification report with Mermaid sequence, flow, and architecture diagrams, master verification checklist, and empirical trace proofs.
- `docs/thesis-preparation/Backend_Verification_Viva.md` — 10 academic Q&A questions for BS Computer Science FYP viva examination.

---

## [2.4.0] — 2026-08-03

### Added — Phase 2.4: Comprehensive API Testing Infrastructure & Suite

#### Postman Collection & Environment (`backend/tests/`)
- `MindShield_API_v1.postman_collection.json` — Postman Schema v2.1.0 JSON test collection containing 12 request suites with embedded JavaScript (`pm.test`) assertions for status codes, schema validation, headers, SLA latency thresholds, and error envelopes.
- `MindShield_Dev_Environment.postman_environment.json` — Postman environment configuration file parametrizing `{{base_url}}`, `{{api_version}}`, and `{{auth_token}}`.

#### Automated Pytest API Test Suite (`tests/test_api_testing.py`)
- Programmatic Python API test suite covering:
  - Health & Liveness probes (`GET /health`)
  - Operational Status metadata (`GET /api/v1/analyze/status`)
  - SMS Classification Happy Path (Phishing/Dangerous, Suspicious, Safe, Credential Harvesting)
  - Boundary Value Analysis & Input Validation (Missing message, empty, whitespace-only, short, long, numeric)
  - HTTP Routing & Protocol Errors (404 Not Found, 422 Unprocessable Entity)
  - SLA Response Time Benchmarks (`< 500ms` for analysis, `< 200ms` for health probes)

#### Verification & Thesis Documentation (`backend/docs/`, `docs/thesis-preparation/`)
- Total test count expanded to **169 tests (100% pass rate, 92% total coverage)**.
- Flake8 static analysis **clean with 0 violations**.
- `backend/docs/04_API_Testing.md` — 13-section thesis technical reference with Mermaid sequence and workflow diagrams, BVA matrix, SLA benchmarks, and CI automation specs.
- `docs/thesis-preparation/API_Testing_Viva.md` — 10 academic Q&A questions for BS Computer Science FYP viva examination.

---

## [2.3.0] — 2026-08-03

### Added — Phase 2.3: AI Model Loading & Inference Architecture

#### Model Loading Architecture (`app/core/model_loader.py`)
- Enhanced `BaseModelLoader` abstract contract with `unload()`, `predict_batch()`, `backend_type`, and `is_loaded`.
- `HuggingFaceModelLoader` — HuggingFace Transformers & ONNX model loader architecture stub supporting path resolution, tokenization pipelines, logit extraction, and softmax normalization.
- `ModelLoaderFactory` — static factory pattern for declarative backend instantiation (`mock`, `huggingface`, `placeholder`).
- `ModelPrediction` DTO enhanced with `backend_type`, `logits`, and `fallback_mode` fields.

#### Inference Orchestration Service (`app/services/inference_service.py`)
- `InferenceService` — dedicated service managing ML model inference execution, single and batch predictions (`predict`, `predict_batch`), latency profiling, and graceful error recovery.
- Automatic Fallback Engine — if primary model is unready or raises an inference exception (e.g. OOM or crash), seamlessly redirects execution to a secondary fallback loader (e.g. `MockModelLoader`) and tags predictions with `fallback_mode=True`.

#### Application Core & Configuration (`app/core/config.py`, `app/core/exceptions.py`, `app/main.py`)
- Added `ModelLoadException` for model initialization & weight downloading errors.
- Added `model_backend` (`mock` | `huggingface` | `placeholder`) and `model_fallback_enabled` to `Settings`.
- `main.py` lifespan updated to initialize `InferenceService` singleton with warm-up passes and fallback failover.
- API dependencies updated to inject `InferenceService` into `AnalysisService`.

#### Test Suite & Verification (`tests/`)
- Created `tests/test_inference_service.py` — 10 unit tests for single prediction, batch prediction, health checks, and fallback failover recovery.
- Created `tests/test_model_loader_factory.py` — 14 unit tests for `ModelLoaderFactory`, `HuggingFaceModelLoader`, and `PlaceholderModelLoader`.
- Updated `tests/conftest.py` with `InferenceService` fixture support.
- All **155 tests passed (100% pass rate, 91% coverage)**. Flake8 lint clean (**0 violations**).

#### Thesis Documentation
- `backend/docs/03_Model_Loader.md` — 14-section technical reference with Mermaid sequence, class, component, and flow diagrams; SOLID architectural analysis; HuggingFace compatibility specs; verification results.
- `docs/thesis-preparation/Model_Loader_Viva.md` — 15 academic Q&A questions for BS Computer Science FYP viva examination.

---

## [2.2.0] — 2026-08-03

### Added — Phase 2.2: REST API Layer with Mock Analysis Engine

#### Mock Analysis Engine
- `app/core/mock_model_loader.py` — `MockModelLoader`: heuristic-based classification engine replacing the Phase 2.1 fixed placeholder. Uses five signal categories (URL, urgency, credential, financial, prize) with a weighted danger-score algorithm. Returns varied dangerous/suspicious/safe responses with calibrated confidence scores in [0.60, 0.97].
  - `_FeatureScore` dataclass — holds extracted feature flags and computes `danger_score`
  - `_extract_features(text)` — extracts 6 feature flags from sanitised text
  - `_classify(features)` — maps danger score to (label, threat_level, confidence)
  - `_build_explanation(features, threat_level)` — constructs human-readable rationale listing detected signals

#### Enhanced Schemas (`app/schemas/analysis.py`)
- `RequestMetadata` — new optional sub-schema: `app_version`, `locale`, `network`
- `ThreatIndicator` — new schema for per-signal transparency: `name`, `present`, `weight`, `detail`
- `AnalysisRequest` — added `metadata: RequestMetadata | None` field; four named OpenAPI examples
- `AnalysisResult` — added `indicators: list[ThreatIndicator]`, `mock_mode: bool`, `processing_time_ms: float | None`, `request_id: str | None`; multiple response examples in Swagger

#### Enhanced Service (`app/services/analysis_service.py`)
- `_build_indicators(features)` — constructs 6-element `ThreatIndicator` list from feature flags
- `analyse(message, sender, request_id)` — added `request_id` parameter for end-to-end tracing
- `processing_time_ms` — measured using `time.perf_counter()` and included in result
- `mock_mode` detection — set from `model_version` prefix (`mock` or `placeholder`)

#### Enhanced Validators (`app/utils/validators.py`)
- `contains_financial_keywords(text)` — detects bank/payment/institution keywords
- `contains_credential_request(text)` — detects password/OTP/PIN requests (highest-weight signal)
- `contains_prize_language(text)` — detects lottery/reward language
- `compute_message_features()` — extended to return all 9 feature flags including new functions

#### Enhanced Router (`app/routers/v1/analysis.py`)
- Full Markdown `description` with signal-weight table for `POST /api/v1/analyze`
- `_ANALYZE_RESPONSES` — documents 200, 400, 422, 503 with example response bodies
- `openapi_extra.x-codeSamples` — Dart/Flutter and cURL code samples in Swagger
- `request_id` extraction from `request.state` and propagation to service
- `api_status` endpoint — enhanced with `mock_mode` flag and structured endpoints list

#### Application
- `app/main.py` — switched from `PlaceholderModelLoader` to `MockModelLoader` in lifespan
- `app/core/config.py` — version bumped to `2.2.0`

#### Tests (`tests/`)
- `tests/test_analysis.py` — **78 tests** (Phase 2.2 complete rewrite):
  - `TestAnalyzeHappyPath` — 200 for all three threat levels
  - `TestResponseEnvelope` — envelope structure verification
  - `TestAnalysisResultSchema` — all new fields (indicators, mock_mode, processing_time_ms, request_id)
  - `TestThreatClassification` — heuristic correctness on known inputs
  - `TestOptionalFields` — metadata and sender handling
  - `TestValidationErrors` — 422 error structure
  - `TestMiddlewareHeaders` — X-Request-ID, X-Process-Time-Ms
  - `TestStatusEndpoint` — mock_mode flag in status
  - `TestAnalysisServiceUnit` — service layer unit tests
  - `TestMockModelLoaderUnit` — heuristic engine unit tests
- `tests/test_validators.py` — **41 tests** (extended):
  - `TestContainsFinancialKeywords` — 6 tests
  - `TestContainsCredentialRequest` — 6 tests
  - `TestContainsPrizeLanguage` — 5 tests
  - Extended `TestComputeMessageFeatures` — 9-key coverage
- `tests/conftest.py` — updated to use `MockModelLoader`
- `tests/test_health.py` — updated `test_health_model_version_is_mock`

#### Documentation
- `backend/docs/02_API_Architecture.md` — 18-section thesis-ready documentation with Mermaid sequence, class, component, and flow diagrams; complete API reference; validation strategy; heuristic engine design; verification results
- `docs/thesis-preparation/API_Layer_Viva.md` — 20 viva Q&A covering REST fundamentals, mock design, OpenAPI, SOLID, testing, error handling, and security

### Changed
- `app/core/model_loader.py` — `PlaceholderModelLoader` preserved (not removed); superseded by `MockModelLoader` in production startup but retained for reference and direct comparison

### Verification
- **Tests**: 132 / 132 passed (`pytest tests/ -v`)
- **Coverage**: 93% overall; 100% on routers, service, middleware, schemas, validators
- **Linting**: Zero flake8 violations (`python -m flake8 app/ tests/`)
- **Server**: Starts correctly with `MockModelLoader` v`mock-heuristic-v1`

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
