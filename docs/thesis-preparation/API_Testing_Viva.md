# MindShield — Phase 2.4: API Testing & Verification Viva Q&A
## Thesis Preparation — Interview & Examination Guide

> **Module**: Phase 2.4 — Comprehensive API Testing & Verification  
> **Audience**: Final Year Project Supervisor / External Examiner  
> **Level**: BS Computer Science — Final Year Project Defence  

---

## Section 1: Testing Philosophy & Methodology

---

**Q1. What is the objective of Phase 2.4 in the MindShield backend development lifecycle?**

Phase 2.4 establishes the **Comprehensive API Testing Infrastructure**. Its purpose is to systematically verify:
1. **HTTP Contract Invariants**: Ensuring every endpoint conforms to standard response envelopes (`APIResponse[T]` or `HealthStatus`).
2. **Input Validation & Boundary Safety**: Verifying semantic and schema constraints using Equivalence Partitioning and Boundary Value Analysis.
3. **HTTP Status Code Mapping**: Confirming correct status code returns (200 OK, 400 Bad Request, 404 Not Found, 422 Unprocessable Entity, 500 Internal Error, 503 Service Unavailable).
4. **Service Level Agreement (SLA) Benchmarks**: Asserting that single SMS analysis completes in `< 500ms` and health probes complete in `< 200ms`.
5. **Continuous Integration Readiness**: Providing dual execution modes via Postman (Schema v2.1.0 JSON) and automated Pytest test suites.

---

**Q2. Explain how Equivalence Partitioning (EP) was applied to the `POST /api/v1/analyze` input validation.**

Equivalence Partitioning divides input domain data into valid and invalid equivalence classes to minimize redundant test cases:
- **Valid Message Class**: Any string between 3 and 2,000 non-whitespace characters containing non-digit text.
- **Invalid Short Class**: Strings with length `< 3` (e.g. `""`, `"ab"`).
- **Invalid Long Class**: Strings with length `> 2000` characters.
- **Invalid Content Class**: Strings consisting solely of numeric digits (e.g. `"123456789"`).

---

**Q3. How was Boundary Value Analysis (BVA) used to test string length constraints?**

Defects frequently cluster at boundaries. We explicitly test the boundary conditions around `min_length=3` and `max_length=2000`:
- **Length 0** (`""`): Tested → `422 Unprocessable Entity`
- **Length 2** (`"ab"`): Tested → `422 Unprocessable Entity`
- **Length 3** (`"abc"`): Tested → `200 OK` (Min valid boundary)
- **Length 2,000**: Tested → `200 OK` (Max valid boundary)
- **Length 2,001**: Tested → `422 Unprocessable Entity` (Max + 1 boundary violation)

---

## Section 2: Postman Collection & Test Automation

---

**Q4. Describe the structure of the `MindShield_API_v1.postman_collection.json` file.**

The Postman collection is organized into four logical test folders:
1. **1. Health & Operations**: `GET /health` and `GET /api/v1/analyze/status`.
2. **2. SMS Classification (Happy Path)**: `POST /api/v1/analyze` for Phishing, Suspicious, Safe, and Credential Harvest scenarios.
3. **3. Validation & Boundary Tests**: `POST /api/v1/analyze` for missing, empty, whitespace-only, short, long, and numeric payloads.
4. **4. Route & Protocol Errors**: `GET /api/v1/non_existent_route` (404 verification).

Each request embeds JavaScript `pm.test(...)` assertions that validate HTTP status codes, envelope schemas, indicator arrays, headers, and SLA response times.

---

**Q5. How do Postman test scripts validate latency SLAs?**

Postman scripts access `pm.response.responseTime` (in milliseconds) and assert thresholds using Chai.js assertions:
```javascript
pm.test("Response time is under 500ms SLA", function () {
    pm.expect(pm.response.responseTime).to.be.below(500);
});
```

---

**Q6. What environment variables are defined in `MindShield_Dev_Environment.postman_environment.json`?**

The environment configuration parametrizes:
- `{{base_url}}`: `http://localhost:8000` (allows target switching to staging/production without editing requests).
- `{{api_version}}`: `v1`
- `{{auth_token}}`: Secret token placeholder prepared for Phase 2.5 API key authentication.

---

## Section 3: HTTP Status Codes & Error Envelopes

---

**Q7. What is the difference between a 400 Bad Request and a 422 Unprocessable Entity in MindShield?**

- **HTTP 422 Unprocessable Entity**: Returned when Pydantic schema validation or business-rule validation fails (e.g. missing required field `message`, length `< 3`, or purely numeric text).
- **HTTP 400 Bad Request**: Returned when the request body contains malformed JSON syntax that cannot be parsed into a JSON object by the ASGI server.

---

**Q8. How does MindShield ensure consistent error handling across all HTTP status codes?**

All custom application exceptions inherit from `MindShieldException`. Global exception handlers in `main.py` catch all exceptions and format them into a unified `APIResponse` JSON envelope:
```json
{
  "success": false,
  "message": "Validation failed on 'body -> message': String should have at least 3 characters",
  "data": null,
  "error": {
    "error_code": "validation_error",
    "message": "...",
    "details": [...]
  },
  "timestamp": "2026-08-03T23:00:00Z"
}
```

---

## Section 4: CI/CD & Automated Verification

---

**Q9. How can the Postman test collection be executed automatically in a Continuous Integration (CI) pipeline?**

Using **Newman**, the official Postman CLI runner:
```bash
npx newman run tests/MindShield_API_v1.postman_collection.json \
  -e tests/MindShield_Dev_Environment.postman_environment.json \
  --reporters cli,junit
```
This enables GitHub Actions or GitLab CI to run all 12 Postman request suites and generate JUnit XML reports on every pull request.

---

**Q10. What test coverage was achieved in Phase 2.4?**

The automated Pytest suite achieved:
- **169 Passed Tests (100% Pass Rate)**
- **92% Total Line Coverage**
- **100% Coverage** on API routers (`health.py`, `analysis.py`), schemas, validators, CORS, and request logger middleware.

---

*End of Phase 2.4 API Testing Viva Q&A*
