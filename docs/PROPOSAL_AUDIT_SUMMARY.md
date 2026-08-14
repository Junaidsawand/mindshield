# MindShield — Proposal Audit Summary

> **Document ID**: `docs/PROPOSAL_AUDIT_SUMMARY.md`  
> **Phase**: FYP-I Thesis & Audit Summary  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Approved Proposal Identity
* **Authoritative Document**: [`docs/MindShield_FYP_Proposal.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP_Proposal.docx) (Modified/Approved August 2026).
* **Scope Definition**: Defines the baseline objectives and deliverables for both the FYP-I and FYP-II phases.

---

## 2. Objective Status Summary

* **Total Objectives Evaluated**: 12
  * **Fully Achieved**: 7
  * **Partially Achieved**: 1 (Interception permissions/UI flow verified, but receiver loop is device-dependent)
  * **Implemented but Unverified (Headless)**: 1 (Native Android Kotlin receiver code is present but requires active devices)
  * **Not Achieved**: 0
  * **Deferred to FYP-II**: 3 (Secure HTTPS/JWT endpoints, 5-class manipulation classification, and true perturbation LIME explanations)

---

## 3. Key Achievements and Weaknesses

### 3.1 Strongest FYP-I Achievements
* Working FastAPI server integration with Pydantic routes.
* WordPiece tokenizer mapping matching DistilBERT configuration targets.
* CPU model inference latency of $41.95\text{ ms}$, satisfying the $<60\text{ ms}$ SLA gate.
* Template-family group splitting to prevent data leakage during training.
* Comprehensive testing with 234 Pytest cases and 5 Flutter test cases, achieving $75\%$ backend coverage.

### 3.2 Weakest Areas
* **HTTP Development loopback**: paylods transit unencrypted.
* **Heuristic highlights**: rule-based indicator highlights used instead of true LIME.
* **SMS Interception Verification**: telecommunication receiver checks are device-dependent and lack automated headless unit test logs.

---

## 4. Thesis Claims Guidelines

### 4.1 Safe Claims for Thesis
* Functional proof-of-concept pipeline (Android Kotlin interceptor to FastAPI transformer).
* Responsive Material 3 application UI screens.
* Fine-tuned binary classification results on local Pakistani templates.
* Template-family data split pipeline.
* Passing API route, schema validation, and unit test suites.

### 4.2 Claims Requiring Qualification
* **Real-time SMS detection**: Should be described as near-real-time to account for network transit overheads.
* **Latency SLA**: Should be specified as model CPU inference latency rather than end-to-end response time.
* **LIME Explainability**: Highlights are rule-based heuristics to bypass CPU latency limits.
* **Generalization**: Model improvements show directional trends but are evaluated on a small test split (41 samples).

### 4.3 Claims to Avoid
* **"Production-ready security"**: Prototype communicates over unencrypted HTTP and lacks JWT authentication.
* **"100% accurate warning system"**: No machine learning model is 100% accurate.
* **"True runtime LIME"**: Perturbations are not calculated at runtime.
* **"Large-scale Pakistani dataset"**: The custom corpus contains 205 templates.

---

## 5. Final Academic Judgment

### 5.1 Scores and Rationale

* **Implementation Completeness: 9/10**  
  Core components (Android receiver, Flutter UI screens, SQLite inbox cache, FastAPI router, model loader) are fully implemented.
* **Objective Achievement: 8/10**  
  Achieved all baseline objectives planned for FYP-I. Deferred items (HTTPS/JWT, 5-class manipulation, true LIME) are clearly partitioned as FYP-II scope.
* **Testing Maturity: 8/10**  
  234 backend Pytests and 5 frontend Flutter tests are implemented, achieving $75\%$ coverage. Gaps include automated native telephony receiver checks and SQLite cache benchmarks.
* **ML Evidence Quality: 9/10**  
  Fine-tuning runs, tokenization metrics, and candidate comparisons are well-documented.
* **Dataset Quality: 6/10**  
  The 205-template corpus is small and template-derived, which limits demographic and dialectical representation.
* **Security Maturity: 4/10**  
  Security is limited to input validation, NFKC normalization, and PII log scrubbing. Payload transit uses unencrypted HTTP.
* **Academic Defensibility: 9/10**  
  Pushed documentations maintain absolute integrity, with clear boundary matrices and audit files that avoid exaggeration.
* **FYP-I Readiness Assessment: 9/10**  
  Highly prepared for thesis submission and supervisor viva checks. Technical limitations are documented to ensure defensibility.
