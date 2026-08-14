# MindShield — FYP-I Achievements vs. FYP-II Planned Scope

> **Document ID**: `docs/FYP1_ACHIEVEMENTS_VS_FYP2.md`  
> **Phase**: FYP-I Verification Audit  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Scope and Boundary Analysis

This matrix defines the transition boundary between the completed proof-of-concept pipeline of Final Year Project I (FYP-I) and the planned research developments of Final Year Project II (FYP-II).

| Architectural Feature | Approved Proposal Target | Current FYP-I State | FYP-I Status | Planned FYP-II Action |
|---|---|---|---|---|
| **Active ML Model** | Multilingual classification of local threat vectors. | Fine-tuned **`distilbert-pakscam-v1`** (255MB weights) active in production. | **ACHIEVED (Pipeline 1)** | Fine-tune **XLM-RoBERTa** (1.1GB weights) for code-switched Roman Urdu features. |
| **Model Hosting** | Real-time classification on device or server. | Remote CPU-based FastAPI server listening on local loopback. | **ACHIEVED** | Port models to run locally on mobile devices using **ONNX Runtime**. |
| **Classification Output** | Binary threat label + manipulation classification. | Binary classification (`safe` vs `phishing`). | **ACHIEVED (Pipeline 1)** | Train **Pipeline 2** for 5-class psychological manipulation categorization (URG, AUTH, FEAR, REW, SEC). |
| **Explainability (XAI)** | Explain predicted threat flags to users. | Static, rule-based highlights mapped from local lists. | **ACHIEVED (Heuristics)** | Integrate full **LIME (Local Interpretable Model-agnostic Explanations)** perturbation pipelines on server. |
| **Local Database** | Persistent cache for message history and flags. | Single-table SQLite database targeting the `sms_messages` table. | **ACHIEVED** | Expand to a relational schema with encrypted storage (SQLCipher). |
| **Network Protocol** | Secure transmission of message hashes/payloads. | Unencrypted HTTP local loopback (`http://10.0.2.2:8000`). | **ACHIEVED (Development)** | Stage production **HTTPS (TLS 1.3)** with JWT token verification and Nginx gateways. |
| **Dataset Size** | Purpose-built localized corpus. | **205 unique samples** (140 base templates + 65 augmentations). | **ACHIEVED (Initial)** | Compile an independently annotated Pakistani SMS database of $5000+$ records. |
| **Testing Scope** | Validated performance and robust warning cards. | Unit, router, model regression, and UI smoke tests. | **ACHIEVED** | Run User Acceptance Testing (UAT) and load testing on remote networks. |

---

## 2. Boundary Rationale
* **Resource Optimization**: DistilBERT was selected for FYP-I because its 255MB size allows for fast local CPU inference ($41.95\text{ ms}$). Compiling larger multilingual models (XLM-RoBERTa, 1.1GB) requires server GPUs, which are deferred to FYP-II.
* **Latency Gates**: Generating $1000+$ text perturbations for LIME explainability takes ~30 seconds on CPU. Rule-based highlights bypass this latency in the FYP-I prototype, while optimizing LIME is deferred to FYP-II.
* **Security Staging**: Implementing TLS (HTTPS) and token authentication (JWT) requires hosting on public servers, which is scheduled for the final deployment phase in FYP-II.
