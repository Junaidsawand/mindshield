# MindShield Technical Source of Truth

This document establishes the final, code-verified technical truth about the MindShield system architecture, models, datasets, and execution.

---

## 1. System Architecture & Boundaries

* **Interception:** Native Android BroadcastReceiver intercepts incoming SMS at the OS level (`SMS_RECEIVED`).
* **Database sharing:** Kotlin writes pending SMS records directly to SQLite (`mindshield.db`). Flutter reads from the same database.
* **Communication:** Flutter UI notifies providers via MethodChannels. Providers invoke HTTP calls to a FastAPI backend on port 8000.
* **ML Execution:** PyTorch model inference executes **on the FastAPI backend server only** (never on the mobile client).

---

## 2. Machine Learning Core

* **Model Architecture:** HuggingFace `DistilBERT` (`distilbert-base-uncased` fine-tuned with a Sequence Classification Head).
* **Baseline Comparison:** Scikit-learn Linear Support Vector Machine with Count Vectorizer (`linear_svm_count`).
* **Hyperparameters:**
  - Batch size: 32
  - Epochs: 1
  - Max sequence length: 64
  - Optimizer: `AdamW` (learning rate: 2e-5, weight decay: 0.01)
  - Scheduler: Linear schedule with warmup ratio of 0.1
* **In-Domain Test Metrics (UCI):**
  - DistilBERT: Accuracy = 97.86%, Precision = 96.49%, Recall = 85.94%, F1 = 90.91%.
  - Linear SVM: Accuracy = 98.25%, Precision = 98.25%, Recall = 87.50%, F1 = 92.56%.
* **Model Size Trade-off:** DistilBERT = 255.4 MB; Linear SVM = 0.19 MB.
* **Latencies:** DistilBERT ≈ 57.6ms; Linear SVM ≈ 5.0ms.

---

## 3. Data Engineering & Splits

* **UCI SMS Spam Collection:** TSV format, 5,562 raw records reduced to 5,148 unique records post-deduplication. 
* **PakScam-SMS Corpus:** Custom Pakistani smishing dataset composed of **205 templates** (split by template family to prevent data leakage).
* **Domain Generalization Failure:** UCI-trained base model suffers **82.8% False Positive Rate (FPR)** on Pakistani Legitimate HAM notifications (FPR rises to **100%** on banking alerts containing numbers/amounts).
* **Mitigation:** Fine-tuning with Mix-C oversampling and anti-shortcut benign URL link samples reduces the Pakistani HAM FPR to **3.45%** on `distilbert-pakscam-v3`.
* **Production Status:** `distilbert-pakscam-v1` remains active in production because `v3` failed the promotion gates (specifically by misclassifying `zong_engage_prize_lang` containing Roman Urdu prize words as phishing, exceeding the 2.0% threshold).

---

## 4. API & Integration Contracts

* **Main endpoint:** `POST /api/v1/analyze`
  - Validates input length (3 to 2,000 chars) and filters out purely numeric inputs.
  - Returns `threat_level` (`safe`/`suspicious`/`dangerous`), `confidence`, `indicators` list, `modelVersion`, and a `mock_mode` boolean.
* **Explainability (XAI):**
  - **Concept:** Conceptualized as LIME.
  - **Implementation:** Custom Heuristic Feature Attribution on the backend mapping 6 indicator feature flags. Text highlighting is rendered locally on the Flutter app via substring matching.

---

## 5. Security, Database & Testing

* **Database Schema:** `sms_messages` table stores raw content and predictions. Migrated from v1 to v2 to erase all mock/seed data.
* **Testing Coverage:** 42 passed tests on the Python backend (including a 14-case regression suite) and 15 passed tests on Flutter.
* **Privacy Boundary:** Message payloads are sent via HTTP requests to the backend for analysis. Only the raw messages, metadata, and local contact names are cached locally on-device. No PII is retained on the server.
