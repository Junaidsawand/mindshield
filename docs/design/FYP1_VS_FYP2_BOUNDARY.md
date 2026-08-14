# MindShield — FYP-I vs FYP-II Scope Boundary

> **Document ID**: `docs/design/FYP1_VS_FYP2_BOUNDARY.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Boundary Matrix

To maintain project transparency and prevent requirement inflation during academic audits, this document establishes a clear separation between the completed FYP-I deliverables and the planned FYP-II extensions.

| Architectural Component | Completed FYP-I Prototype | Future FYP-II / Research Extensions |
|---|---|---|
| **Active ML Model** | Fine-tuned **`distilbert-pakscam-v1`** (255MB weights) executing binary classification. | Multilingual **XLM-RoBERTa** (1.1GB weights) fine-tuned for code-switched Roman Urdu. |
| **Model Hosting** | Remote CPU-based FastAPI server listening on local HTTP. | Hybrid execution: Local on-device ONNX runtime fallback with cloud GPU servers. |
| **Classification Output** | Binary prediction: `safe` vs `phishing`. | Pipeline 2: **5-class multi-label categorization** of threat vectors (Urgency, Scarcity, Fear, Authority, Reward). |
| **Explainability (XAI)** | Client-side visual highlights mapped from static backend indicators list. | True **LIME (Local Interpretable Model-agnostic Explanations)** executing surrogate modeling on server hosts. |
| **Local Database** | Consolidated single-table **SQLite** (`sms_messages` table). | Relational SQLite schema with encrypted storage (SQLCipher). |
| **Network Protocol** | Unencrypted HTTP local loopback (`http://10.0.2.2:8000`). | Production **HTTPS (TLS 1.3)** with JWT token verification and Nginx gateways. |
| **Dataset Size** | **205 unique samples** (140 base templates + 65 augmentations). | Annotated real-world SMS database of $5000+$ localized smishing records. |
| **Testing Scope** | Heuristic unit tests, model regression suites, and app smoke tests. | User Acceptance Testing (UAT) and load/stress testing on remote cloud networks. |

---

## 2. Rationale for Phase Partitioning

### 2.1 Model Size Constraints
DistilBERT was selected for FYP-I because its 255MB file size fits easily within typical developer workstations. XLM-RoBERTa, while offering improved bilingual Urdu representations, requires substantial hardware memory and is deferred to FYP-II to keep local development fast.

### 2.2 Latency Safeguards
Running true LIME at runtime (generating and predicting 1000+ text variations) takes ~30 seconds on standard CPU hosts, which breaks the real-time requirements of SMS processing. Visual explanation highlights represent a practical intermediate step for FYP-I, while optimizing LIME pipelines is scheduled for FYP-II.

### 2.3 Secure Infrastructure
Setting up public domain endpoints, SSL certificates (HTTPS), and API authentication (JWT) requires active hosting. Using unencrypted HTTP over local loopback is appropriate for local testing, while security configurations are scheduled for final cloud staging.
