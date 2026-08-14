# Conclusion and Recommendations

> **Document ID**: `docs/CONCLUSION_AND_RECOMMENDATIONS.md`  
> **Phase**: FYP-I Conclusion and Recommendations  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Introduction
The primary goal of the MindShield final year project (FYP-I) is to develop a proof-of-concept SMS threat-classification and warning system for the Pakistani telecommunications domain. By integrating an Android-based background listener with a remote transformer-based classifier, the system aims to identify smishing threats (such as fake bank verifications, lottery scams, and financial aid impersonations) written in English, Roman Urdu, or code-switched structures. This document summarizes the achievements of the FYP-I phase, details current technical limitations, and outlines the engineering roadmap for FYP-II.

---

## 2. Summary of FYP-I Achievement
The FYP-I phase successfully implemented and validated the core components of the MindShield pipeline:
* **Background SMS Listener**: A native Android Kotlin `BroadcastReceiver` that intercepts incoming SMS broadcasts and forwards payloads to the Flutter application interface.
* **Flutter Client Interface**: Displays SMS threads, handles runtime permissions, saves messages locally using a single-table SQLite database (`sms_messages` table), and presents classification warnings.
* **FastAPI Backend Server**: Exposes API endpoints (`POST /api/v1/analyze`, `GET /health`) and parses inputs using Pydantic schemas.
* **Model Inference Engine**: Integrates a PyTorch `distilbert-base-uncased` classifier fine-tuned on the custom PakScam-SMS dataset.
* **Heuristic Explanation Layer**: Extracts trigger indicators from messages and highlights them in the client interface, serving as a placeholder for runtime explanations.

---

## 3. Achievement of Objectives

| Objective | Implemented Components | Verification Evidence | Status |
|---|---|---|---|
| **SMS Interception** | Native Android Kotlin BroadcastReceiver bound to SMS_RECEIVED actions. | `sms_background_service.dart` method-channel bindings. | **PARTIALLY ACHIEVED** (Requires physical device) |
| **Inbox Cache** | Local SQLite storage wrapper targeting the `sms_messages` table. | [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart) CRUD test suites. | **ACHIEVED** |
| **FastAPI Analytics API** | POST `/api/v1/analyze` endpoint. | [`test_analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/tests/test_analysis.py) route checks. | **ACHIEVED** |
| **Urdu/Code-switch Model**| Fine-tuned DistilBERT classifier. | `train_pakscam_v3_distilbert.py` training scripts. | **ACHIEVED** (Research candidate `v3`) |
| **Performance SLA** | CPU inference latency under $60\text{ ms}$. | [`v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json) profiling data. | **ACHIEVED** (v1 = $41.95\text{ ms}$, v3 = $57.62\text{ ms}$) |
| **Visual Explainability** | Client-side visual highlights mapped from static backend indicators. | `api_analysis_repository_test.dart` mapping tests. | **ACHIEVED** (Rule-based heuristics) |
| **Secure Payloads** | Payload encryption and JWT authorization. | None (Dev prototype runs over unencrypted HTTP). | **PLANNED / FYP-II** |

---

## 4. Experimental Findings
The experimental evaluation compared the active serving model (`distilbert-pakscam-v1`) against the research candidate (`distilbert-pakscam-v3`):
* **Active Model (`v1`)**: Achieved $96.00\%$ F1 on the UCI benchmark but misclassified $93.10\%$ ($81/87$) of legitimate local banking notifications. This is because features like banking shortlinks (`bit.ly`) represent spam in the UCI training dataset but are common in benign Pakistani transaction alerts.
* **Research Candidate (`v3`)**: By incorporating $65$ targeted augmentations and applying Mix-C oversampling, `v3` reduced the false-positive rate on Pakistani HAM to $3.45\%$ ($3/87$) and achieved $100\%$ spam recall.
* **Key Academic Insight**: A model with slightly lower performance on a generic dataset can be significantly better for a target domain. `v3` is kept as a quarantined research candidate pending validation on a larger, independent corpus.

---

## 5. Engineering Contributions
1. **End-to-End Pipeline**: Connected a native Android broadcast hook, a Flutter interface, and a FastAPI transformer model.
2. **Robust Network Client**: Built a Flutter Dio client that retries up to 2 times on timeout before alerting the user.
3. **Log Scrubbing**: Configured the FastAPI server to scrub sender phone numbers before logging request outputs.

---

## 6. Machine Learning Contributions
1. **PakScam-SMS Dataset**: Built a localized corpus (205 templates) covering Roman Urdu and English-Urdu code-switching.
2. **Template-Family Grouping**: Implemented split functions that group templates by family to prevent data leakage.
3. **Oversampling Strategy**: Evaluated the Mix-C oversampling strategy, which oversamples localized templates 3x to ensure the model learns local smishing features.

---

## 7. Security Contributions
1. **Input Validation**: Configured the backend router to validate message length (between 3 and 2,000 characters) and reject purely numeric payloads.
2. **Text Normalization**: Implemented NFKC Unicode normalization to handle character-level variations.
3. **Current Limitations**: Payload transit runs over unencrypted HTTP, and the system lacks JWT token validation and SSL pinning.

---

## 8. Limitations

### 8.1 Dataset Limitations
* **Small Localized Dataset**: The 205-template corpus restricts geographical, dialectal, and formatting representation.
* **Template Bias**: The synthetic dataset uses static templates, which may limit generalization to novel smishing variants.

### 8.2 ML and System Limitations
* **Structural Leakage**: High structural similarities exist between train and test templates despite template-family partitioning.
* **Latency Maximum**: The maximum inference latency for `v3` reaches $77.51\text{ ms}$, exceeding the $60\text{ ms}$ SLA target.
* **Explainability Naming**: The client highlights are rule-based heuristic alerts; true LIME explanations are deferred due to latency and processing limitations on CPU-bound servers.

---

## 9. Recommendations

### 9.1 Immediate Engineering Improvements
* Transition from HTTP to HTTPS (TLS 1.3) to protect data in transit.
* Implement JWT-based token authentication for API access.
* Benchmarks evaluating SQLite cache transactions under load.

### 9.2 Dataset and ML Improvements
* Compile a larger, independently annotated Pakistani SMS dataset ($5,000+$ records).
* Train multilingual representations (e.g., XLM-RoBERTa) to capture code-switched structures.
* Port models to ONNX Runtime for local, offline execution on mobile devices.

---

## 10. FYP-II Scope

| FYP-II Feature | Motivation | Expected Benefit | Current Status |
|---|---|---|---|
| **XLM-RoBERTa** | Capture code-switched Roman Urdu features. | Improved classification accuracy. | **PLANNED** |
| **ONNX Runtime** | Port model to run locally on mobile devices. | Offline inference, lower latency. | **PLANNED** |
| **HTTPS Staging** | Secure data in transit. | Payload encryption. | **PLANNED** |
| **JWT Authentication** | Secure API access. | Access control. | **PLANNED** |
| **True LIME** | Provide surrogate explainability. | Improved transparency. | **PLANNED** |

---

## 11. Final Conclusion
MindShield FYP-I has established a working proof-of-concept pipeline for localized SMS threat detection. By demonstrating the limitations of generic classifiers and validating localized fine-tuning, this phase provides an empirical foundation for subsequent development in FYP-II.
