# MindShield — Phase 2.2: API Layer Viva Q&A
## Thesis Preparation — Interview / Examination Questions

> **Module**: Phase 2.2 — REST API Layer with Mock Analysis Engine  
> **Audience**: Final Year Project Supervisor / External Examiner  
> **Level**: BS Computer Science — Final Year Project Defence  

---

## Section 1: API Design Fundamentals

---

**Q1. What does REST stand for and why did you choose a RESTful API for MindShield?**

REST stands for **Representational State Transfer** — an architectural style defined by Roy Fielding in 2000 that uses HTTP as a stateless communication protocol with standard methods (GET, POST, PUT, DELETE).

MindShield uses REST because:
- The Flutter mobile client uses the Dio HTTP library, which is natively suited to REST/JSON.
- REST is stateless — each request from the Flutter app carries all necessary information, eliminating the need for session management at this phase.
- HTTP status codes provide a universal error signalling mechanism understood by all client frameworks.
- REST/JSON is universally supported and does not require special tooling (unlike GraphQL or gRPC).

---

**Q2. Why is the endpoint `POST /api/v1/analyze` rather than `GET`?**

Classification of an SMS message requires the client to **submit the message body in the request**. The HTTP GET method has no request body by convention (RFC 9110), so GET is unsuitable.

POST is appropriate because:
- It carries a request body (`message`, `sender`, `metadata`).
- The operation is not idempotent — repeated identical requests may produce different results when the real model is active (Phase 2.3).
- POST signals to intermediate infrastructure (proxies, CDNs) that the request should not be cached by default.
- POST aligns with the REST convention of "submit data for processing."

---

**Q3. What is the purpose of API versioning (`/api/v1/`)?**

Versioning allows the API to **evolve without breaking existing clients**. Once the Flutter app is deployed to users, the client code cannot be instantly updated — users may run older app versions.

With `/api/v1/analyze`, if Phase 2.4 introduces breaking schema changes (e.g., renames `threat_level` to `severity`), a new `/api/v2/analyze` endpoint can be created while `/api/v1/analyze` continues serving older clients unchanged.

The current implementation uses a URL-path prefix (`/api/v1`), which is the most explicit versioning strategy and is easily validated in routing middleware.

---

**Q4. What is Pydantic and why is it used for schema validation?**

Pydantic is a Python data validation library that uses **type annotations and runtime validation** to enforce data contracts. FastAPI integrates Pydantic natively for request/response parsing.

Benefits:
- **Automatic HTTP 422**: If the request body fails validation, FastAPI returns a 422 response with detailed field-level error messages, without any manual validation code.
- **Type safety**: Pydantic v2 is compiled in Rust, providing ~5–50× faster validation than Pydantic v1.
- **Schema generation**: Pydantic models are automatically converted to OpenAPI/JSON Schema, populating the Swagger UI documentation.
- **Declarative**: Constraints (`min_length`, `max_length`, `ge`, `le`) are co-located with the field definition, not scattered in imperative code.

---

**Q5. What is the difference between schema-level validation and business-rule validation in MindShield?**

**Schema-level validation** (Pydantic) enforces syntactic constraints:
- Field type (`message` must be a string)
- Length bounds (`min_length=3`, `max_length=2000`)
- Enum values (`threat_level` must be `safe|suspicious|dangerous`)

**Business-rule validation** (`is_valid_message()`) enforces semantic constraints:
- A purely numeric string (e.g., `"123456"`) passes schema validation (it's a valid string of length 6) but fails the business rule because a bare OTP number without context cannot be meaningfully classified.

Separating these layers keeps the Pydantic schema focused on type-level contracts while the service layer enforces domain knowledge. This follows the **Single Responsibility Principle** — Pydantic does not know what constitutes a "meaningful" SMS.

---

## Section 2: Mock Engine Design

---

**Q6. Why implement a mock engine rather than a real model in Phase 2.2?**

Four engineering reasons:

1. **Full-stack integration**: The Flutter app needs a working backend to test API calls, response parsing, and UI rendering. A fixed placeholder (Phase 2.1) returns the same response regardless of input; the mock engine returns varied responses that exercise all UI code paths.

2. **Test reliability**: The mock engine is deterministic (same input → same output) and does not require a trained model binary, Python ML dependencies, or GPU resources. Tests run in ~7 seconds on any machine.

3. **Interface stability**: By implementing `MockModelLoader` as a subclass of `BaseModelLoader`, the interface contract is validated before the real model exists. Phase 2.3 only needs to implement the same three methods.

4. **Academic scope**: A Final Year Project demonstrating clean architecture, API design, testing, and documentation is academically complete at this stage. ML integration is a subsequent, documented enhancement.

---

**Q7. How does the MockModelLoader heuristic classify a message as dangerous?**

The mock engine computes a weighted **danger score** from five signal categories:

| Signal | Score Added |
|--------|-------------|
| URL/link detected | +0.35 |
| Urgency language | +0.30 |
| Credential request (OTP/PIN/password) | +0.40 |
| Financial keywords | +0.20 |
| Prize/lottery language | +0.25 |
| Safe/casual language | −0.50 |

If the total score ≥ 0.55, the message is classified as **dangerous**. If 0.25–0.54, it is **suspicious**. Below 0.25, **safe**.

For example, the message *"URGENT: Your bank account has been suspended. Click here: http://x.com"* scores:
- URL (+0.35) + Urgency (+0.30) + Financial (+0.20) = **0.85 → dangerous**

---

**Q8. Is the MockModelLoader's classification accurate?**

No — and by design. The mock engine is a **rule-based heuristic**, not a trained statistical model. It has known limitations:

- It cannot understand context (e.g., a bank's legitimate service message may contain financial keywords).
- It does not understand semantics — it only pattern-matches against keyword lists.
- It is English-only.
- It will misclassify creative phishing attempts that avoid known keywords.

All API responses in Phase 2.2 include `"mock_mode": true`, and the Flutter UI displays a visible disclaimer. The mock is a development tool, not a deployed security product.

---

**Q9. Why is the MockModelLoader deterministic? What is the benefit?**

Determinism means the same input text always produces the same output (label, confidence, explanation). This is achieved because:
- The classification logic is purely based on keyword matching (no randomness).
- No model weights, sampling, or probabilistic inference is involved.

**Benefits**:
- **Reproducible tests**: `assert result.threat_level == "dangerous"` is a reliable assertion.
- **Debugging**: If a regression occurs, the same input will reproduce the same failure.
- **Documentation**: Test cases serve as a precise specification of heuristic behaviour.

The real NLP model (Phase 2.3) will not be fully deterministic (dropout in transformer models produces slight variance during inference), so test assertions will need to use threshold-based checks rather than exact equality.

---

## Section 3: OpenAPI and Documentation

---

**Q10. What is OpenAPI and how does FastAPI generate it automatically?**

**OpenAPI** (formerly Swagger) is a machine-readable specification for REST APIs, defined in JSON or YAML. It describes every endpoint, request schema, response schema, and status code.

FastAPI generates the OpenAPI specification **automatically** from Python type annotations:
- `AnalysisRequest` (Pydantic model) → OpenAPI request body schema
- `AnalysisResult` (Pydantic model) → OpenAPI response schema
- `response_model=APIResponse[AnalysisResult]` → links endpoint to its response schema
- `Field(description=..., examples=[...])` → OpenAPI field metadata

The generated specification is served at `/openapi.json` and rendered interactively at `/docs` (Swagger UI) and `/redoc`.

---

**Q11. What is the `openapi_extra` parameter used for in MindShield?**

`openapi_extra` is a FastAPI mechanism to inject arbitrary OpenAPI specification fields that are not derivable from Python type annotations. In MindShield, it is used to add **`x-codeSamples`** — vendor extension fields that display code examples in the Swagger UI.

```python
openapi_extra={
    "x-codeSamples": [
        {"lang": "Dart (Flutter / Dio)", "source": "..."},
        {"lang": "cURL", "source": "..."},
    ]
}
```

This allows developers viewing the API documentation to see copy-pasteable examples in their preferred language without reading the full request schema.

---

**Q12. What are multiple examples in OpenAPI and how are they defined?**

OpenAPI 3.1 supports **multiple named examples** for both request and response schemas. In MindShield, four named examples are defined in `AnalysisRequest.model_config`:

```python
"examples": [
    {"summary": "Dangerous — phishing SMS",    "value": {...}},
    {"summary": "Suspicious — prize/lottery",  "value": {...}},
    {"summary": "Safe — normal conversation",  "value": {...}},
    {"summary": "Dangerous — credential harvest", "value": {...}},
]
```

In Swagger UI, a dropdown menu allows developers to select each named example and execute the request directly, enabling interactive exploration of all threat-level scenarios.

---

## Section 4: Architecture and Patterns

---

**Q13. Explain the Dependency Injection pattern used in MindShield's API.**

FastAPI uses `Depends()` to implement **constructor-based DI**. Instead of the router importing and instantiating `AnalysisService` directly, it declares:

```python
async def analyse_message(
    service: AnalysisService = Depends(_get_analysis_service),
) -> APIResponse[AnalysisResult]:
    ...
```

FastAPI resolves the dependency graph at startup, calling `_get_analysis_service()` which calls `_get_model_loader()` which calls `get_model_loader()`.

**Benefits**:
- **Testability**: Tests override `_get_model_loader` by injecting a test loader into `main_module._model_loader`.
- **Decoupling**: The router does not know whether it is using `MockModelLoader` or `BertModelLoader`.
- **Lifecycle management**: FastAPI ensures dependencies are resolved in the correct order.

---

**Q14. How does the `request_id` flow from the client to the response?**

The `request_id` is generated by `RequestLoggerMiddleware` on every inbound request:

```
1. Middleware: request_id = uuid4().hex → request.state.request_id
2. Router:    request_id = request.state.request_id
3. Service:   analyse(message, sender, request_id=request_id)
4. Result:    AnalysisResult(request_id=request_id, ...)
5. Response:  {"data": {"request_id": "abc-123...", ...}}
   Headers:   X-Request-ID: abc-123...
```

The client receives the `request_id` in both the response body and the `X-Request-ID` header. If the user reports a problem, they can copy the `request_id` and the developer can `grep` the server logs for that exact UUID to find the full trace.

---

**Q15. What SOLID principles are demonstrated in the API layer?**

| Principle | Application |
|-----------|-------------|
| **S** — Single Responsibility | Router does only HTTP handling; Service does only orchestration; Validators are pure functions |
| **O** — Open/Closed | `BaseModelLoader` is closed for modification; adding `BertModelLoader` extends without changing existing code |
| **L** — Liskov Substitution | `MockModelLoader` can be used anywhere `BaseModelLoader` is expected without breaking the contract |
| **I** — Interface Segregation | `BaseModelLoader` defines exactly `load()`, `predict()`, `health()` — no extraneous methods |
| **D** — Dependency Inversion | `AnalysisService` depends on `BaseModelLoader` (abstraction), not `MockModelLoader` (concrete) |

---

## Section 5: Testing and Quality

---

**Q16. How many tests were written for Phase 2.2 and what do they cover?**

Phase 2.2 includes **132 automated tests** across three test modules:

| Module | Tests | Coverage Area |
|--------|-------|---------------|
| `test_analysis.py` | 78 | HTTP integration, classification, indicators, service unit, MockModelLoader unit |
| `test_validators.py` | 41 | Pure validator functions (URL, urgency, financial, credentials, prize) |
| `test_health.py` | 13 | Health endpoint integration |
| **Total** | **132** | |

Overall coverage: **93%** — all critical paths (routers, service, middleware, schemas, validators) at 100%.

---

**Q17. How do you test HTTP endpoints without running a real server?**

The tests use `fastapi.testclient.TestClient`, which wraps the FastAPI ASGI application in a thread and uses `httpx` to make synchronous HTTP calls. This exercises the complete HTTP stack — routing, middleware, exception handlers, Pydantic validation — without binding to a network port.

```python
@pytest.fixture()
def client(test_app: FastAPI) -> TestClient:
    with TestClient(test_app, raise_server_exceptions=True) as c:
        yield c

def test_dangerous_input_returns_200(self, client: TestClient) -> None:
    response = client.post("/api/v1/analyze", json={"message": phishing_sms})
    assert response.status_code == 200
```

The `test_app` fixture injects a loaded `MockModelLoader` directly into `main_module._model_loader`, bypassing the lifespan context manager.

---

**Q18. What is flake8 and why is achieving zero violations important?**

**Flake8** is a Python static analysis tool that checks for:
- **PEP 8 style violations** (line length, whitespace, indentation)
- **F-errors**: Unused imports, undefined names (from pyflakes)
- **D-errors**: Missing docstrings (from pydocstyle)
- **B-errors**: Bugbear patterns (mutable default arguments, etc.)

Zero violations signal that the code:
- Follows community-standard style (readable by any Python developer)
- Has no obvious bugs (undefined variables, unused imports indicating dead code)
- Has complete documentation (every public function has a docstring)

For an academic submission, zero violations demonstrate professional-grade code quality and attention to detail.

---

## Section 6: Error Handling and Security

---

**Q19. Why does MindShield use a custom `APIResponse` envelope instead of returning data directly?**

Direct responses (e.g., returning `AnalysisResult` JSON) require the client to inspect HTTP status codes to determine success or failure. The Flutter Dio client handles status codes, but a consistent envelope provides additional benefits:

```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {...},
  "error": null,
  "timestamp": "..."
}
```

1. **`success` flag**: Allows the client to branch without checking status codes.
2. **`message`**: Human-readable context for display or logging.
3. **`error` block**: Structured error detail with `error_code` for programmatic handling.
4. **`timestamp`**: UTC time for client-side log correlation.
5. **Generic `APIResponse[T]`**: The Flutter Dart client uses one generic deserialisation function for all endpoints.

---

**Q20. What security considerations are addressed in Phase 2.2?**

Phase 2.2 implements several defensive measures:

| Consideration | Implementation |
|---------------|---------------|
| Input length limit | `max_length=2000` prevents memory exhaustion |
| Type validation | `field_validator` rejects non-string inputs |
| Unicode normalisation | NFKC prevents homograph attacks (e.g., full-width characters bypassing keyword matching) |
| Internal error hiding | Unhandled exceptions return generic 500; no stack traces sent to client |
| No credential logging | `sender` and `message` are not logged at INFO level in production |
| CORS restriction | `allowed_origins` from `.env` restricts cross-origin requests |
| `mock_mode` disclaimer | Clients informed results are not real security decisions |

**Not yet implemented** (deferred phases): Rate limiting, authentication, input sanitisation beyond Unicode, injection prevention (no SQL/NoSQL in Phase 2.2).

---

*End of Phase 2.2 API Viva Q&A*
