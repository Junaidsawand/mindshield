# MindShield — FYP-I Academic Scope Lock

> **Document ID**: `docs/FYP1_ACADEMIC_SCOPE_LOCK.md`  
> **Phase**: FYP-I Academic Verification  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## A. Purpose
This document establishes the final academic scope lock for MindShield Final Year Project I (FYP-I). It serves as the authoritative boundary mapping implemented modules, validation results, and experimental metrics to the approved project proposal, preventing requirement inflation and ensuring defensibility under aggressive viva examination.

---

## B. Approved Proposal Baseline
* **Authoritative Reference**: [`docs/MindShield_FYP_Proposal.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP_Proposal.docx) (Synopsis baseline, August 2026).
* **Research Focus**: Localized Roman Urdu and code-switched SMS smishing classification, model explainability benchmarks, and native Android background listeners.

---

## C. FYP-I Completed Objectives

The following objectives are implemented in code, validated in testing, and documented:
1. **PROP-OBJ-02 (Responsive UI)**: Material 3 screen layouts for permission onboarding, thread histories, warning detail screens, and settings.
2. **PROP-OBJ-03 (SQLite persistence)**: consolidated single-table SQLite database cache (`sms_messages`).
3. **PROP-OBJ-04 (FastAPIREST API)**: Exposes routes for analysis (`POST /api/v1/analyze`) and liveness checks (`GET /health`).
4. **PROP-OBJ-05 (Transformer Classifier)**: Fine-tuned DistilBERT engine executing binary threat analysis.
5. **PROP-OBJ-07 (Latency SLA)**: Model CPU inference latency satisfies the sub-$60\text{ ms}$ SLA target.
6. **PROP-OBJ-08 (Heuristic XAI)**: Rule-based indicator highlights mapped to client badge views.
7. **PROP-OBJ-09 (Regression Gating)**: 14-case regression suite executed during test suites.

---

## D. Implemented-but-Unverified Objectives
1. **PROP-OBJ-01 (SMS Interception)**: Kotlin `IncomingSmsReceiver` code is implemented, but active telecommunication broadcast hooks require physical target environments or emulator simulation settings, making them device-dependent for validation.

---

## E. Partially Achieved Objectives
1. **PROP-OBJ-06 (Localized Roman Urdu support)**: Evaluated on the `distilbert-pakscam-v3` research candidate (reduces HAM FPR to $3.45\%$, recall at $100.00\%$), which remains quarantined. The active serving model `v1` lacks localized optimization, yielding a high local HAM false-positive rate ($93.10\%$).

---

## F. FYP-II Deferred Objectives
The following objectives are outside the FYP-I scope:
1. **PROP-OBJ-10 (HTTPS/JWT)**: Payload transit encryption (TLS 1.3) and token authentication.
2. **PROP-OBJ-11 (5-Class Manipulation Classifier)**: Fine-tuning a multilingual classifier (XLM-RoBERTa) for threat categorization (URG, AUTH, FEAR, REW, SEC).
3. **PROP-OBJ-12 (True LIME explainability)**: Perturbation-based surrogate modeling.

---

## G. Quantitative Evidence Baseline

### G.1 Dataset Volumes
* **UCI SMS Spam (Deduplicated)**: **5,148 records** (4,506 HAM, 642 SPAM).
  * *Splits*: Train = 4,118 records; Val = 515 records; Test = 515 records.
* **PakScam Base templates (v2)**: **140 unique records** (87 HAM, 53 SPAM).
  * Includes 125 synthetic templates and 15 real-world seeds (seeds are included *within* the 140, not in addition).
* **PakScam Augmentations (v3)**: **65 unique records** (55 HAM, 10 SPAM).
* **Combined PakScam Dataset (v3)**: **205 unique records** (142 HAM, 63 SPAM).

### G.2 Model Results

#### Active Serving Model (`distilbert-pakscam-v1`)
* UCI Test F1: **$96.00\%$** (Precision: $98.36\%$, Recall: $93.75\%$, FPR: $0.22\%$)
* Pak Ham FPR: $93.10\%$ ($81/87$ false positives on localized transaction notifications)
* Pak Spam Recall: $98.11\%$ ($52/53$ smishing alerts captured)
* Regression Pass Rate: $35.71\%$ ($5/14$ benchmark cases passed)
* CPU Inference Latency (Mean): **$41.95\text{ ms}$** (Max: $50.74\text{ ms}$)

#### Research Candidate Model (`distilbert-pakscam-v3`)
* UCI Test F1: $95.08\%$ (Precision: $100.00\%$, Recall: $90.62\%$, FPR: $0.00\%$)
* Pak Ham FPR: **$3.45\%$** ($3/87$ false positives, representing a major drop)
* Pak Spam Recall: **$100.00\%$** ($53/53$ smishing alerts captured)
* Regression Pass Rate: **$92.86\%$** ($13/14$ benchmark cases passed)
* CPU Inference Latency (Mean): $57.62\text{ ms}$ (Max: $77.51\text{ ms}$)

### G.3 Verification Metrics
* **Backend Pytest**: 234 tests executed (230 passed, 4 failed regressions matching model metrics).
* **Frontend Flutter**: 5 tests executed (5 passed).
* **Coverage**: $75\%$ backend statement coverage.

---

## H. Thesis-Safe Achievement Statements
* *"MindShield implements a Flutter-based mobile client integrated with a FastAPI inference backend and a transformer-based binary SMS classification pipeline."*
* *"The system evaluates classification performance using a fine-tuned DistilBERT active production engine, achieving a $96.00\%$ F1-score on standard English benchmarks."*
* *"To mitigate local domain shift, a quarantined candidate model fine-tuned on custom Roman Urdu templates demonstrated directional improvements, reducing false-positive rates to $3.45\%$."*
* *"Model CPU inference processing latency was verified at $41.95\text{ ms}$ for the active model and $57.62\text{ ms}$ for the candidate, satisfying the $60\text{ ms}$ SLA gate."*

---

## I. Qualified Claims
* **Near-Real-Time**: Describe threat alerts as near-real-time to account for network transit overheads.
* **Inference Latency Only**: Do not claim end-to-end response times under $60\text{ ms}$; the metric is strictly model CPU inference execution.
* **Rule-based Highlight Approximations**: Describe visual term highlights as rule-based heuristics rather than perturbation LIME.
* **Directional Trends**: Discuss local smishing generalizations as positive directional trends evaluated on a small test split.

---

## J. Forbidden Claims
* **"Production-ready security product"**: Prototype communicates over HTTP and lacks JWT authentication.
* **"100% accurate warning system"**: Avoid claims of absolute detection.
* **"True runtime LIME"**: Perturbations are not calculated at runtime.
* **"Large-scale Pakistani dataset"**: The custom corpus contains 205 templates.
* **"Fully verified on physical devices"**: Kotlin receiver hooks are device-dependent.
* **"v3 is the active deployed model"**: `v3` remains quarantined.
* **"Independent test set"**: The 14-case regression suite is derived from base templates.
* **"5-class threat categorization"**: Pipeline 2 is planned for FYP-II.

---

## K. Major Limitations
* **Small Localized Corpus**: 205 templates limit demographic, geographical, and formatting representation.
* **Template Bias**: The synthetic dataset uses static templates, which may limit generalization.
* **Structural Leakage**: Structural similarities remain between the train and test subsets.
* **Local HTTP Communication**: Payload transit runs over unencrypted HTTP.
* **Heuristic Explanations**: The highlight cards use static rule-based checks. True LIME explanations are deferred due to latency and processing limitations on CPU-bound servers.

---

## L. Viva-Critical Vulnerabilities
* **High false-positive rate in `v1`**: Deployed model misclassifies localized transaction alerts as spam.
* **No End-to-End Latency**: Metrics measure CPU operations only. Network transit adds substantial overhead, which is not verified.
* **Heuristic XAI Naming**: The client highlights are rule-based heuristic alerts; true LIME explanations are deferred.

---

## M. Evidence/Source Mapping

* **Android Interception Receiver**: [`IncomingSmsReceiver.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/android/app/src/main/kotlin/com/example/mindshield/IncomingSmsReceiver.kt).
* **UI Screens**: `frontend/lib/presentation/`.
* **SQLite persistence schema**: `frontend/lib/core/database/database_helper.dart`.
* **FastAPI Routers**: `backend/app/main.py`.
* **Model Loader**: `backend/app/distilbert/model_loader.py`.
* **Training and Oversampling**: `backend/scripts/train_pakscam_v3_distilbert.py`.
* **Pytest Verification**: `backend/tests/` (run command: `pytest`).
* **Flutter Verification**: `frontend/test/` (run command: `flutter test`).
* **Metric Outputs**: `backend/data/metadata/v3_evaluation_results.json`.

---

## N. Final FYP-I Scope Statement
MindShield FYP-I is a functional proof-of-concept integrating background SMS interception infrastructure, a Flutter Material 3 client, local SQLite cache persistence, a FastAPI inference backend, a DistilBERT binary classification engine, localized SMS experimentation datasets, and heuristic threat indicator warning cards. Secure production HTTPs transit channels, 5-class psychological manipulation categorization, true runtime perturbation LIME, large-scale Pakistani real-world SMS validation, and full physical device integration verification remain outside the scope of FYP-I and are deferred to FYP-II.
