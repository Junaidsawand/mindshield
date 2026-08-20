# Master Technical Source of Truth

This document defines the canonical technical truths, metrics, configurations, and implementation parameters for the MindShield project. All subsequent documentation, thesis chapters, and presentations must align with the parameters established herein.

---

## 1. System Architecture & Location Invariants

* **Inference Tier:** Remote server-side execution only. PyTorch and model weights are loaded into memory on the FastAPI backend on startup. No machine learning model is executed on-device.
* **Ingestion Tier:** OS-level SMS interception via Kotlin `SmsReceiver.kt` BroadcastReceiver.
* **MethodChannel Bridge:** Platform channel named `com.mindshield/sms_receiver` forwards payload parameters to Dart `SmsBackgroundService` singleton.
* **Storage Tier:** Sandboxed SQLite file `mindshield.db` accessed locally by both Kotlin and Dart.

---

## 2. Machine Learning Core Parameters

* **Base Model Checkpoint:** `distilbert-base-uncased` (fine-tuned with a Sequence Classification Head).
* **Baseline Pipeline:** Scikit-learn Linear Support Vector Machine with Count Vectorizer (`linear_svm_count`).
* **Model Class Count:** Binary classification only (`num_labels = 2`). Labels: `0` (ham) / `1` (spam/phishing).
* **Attack-Vector Mappings:** Rule-based downstream mapping (categorized as smishing, prizeScam, investmentFraud, or phishing on the client).
* **Hyperparameters (Fine-tuning):**
  - Max sequence length: 64
  - Batch size: 32
  - Learning rate: $2 \times 10^{-5}$ ($2\text{e-}5$)
  - Optimizer: `AdamW` (weight decay: 0.01)
  - Scheduler: Linear schedule with warmup ratio of 0.1
  - Epochs: 1 (with early stopping patience = 2)
  - Random seed: 42

---

## 3. Data Engineering & Curation Parameters

* **UCI SMS Spam Collection:**
  - Raw record count: **5,562**
  - Deduplicated count: **414**
  - Cleaned corpus size: **5,148**
  - Train/Val/Test Splits: **4,118 / 515 / 515**
* **PakScam-SMS localized corpus:**
  - Total templates: **205** (separated by template family to prevent data leakage)
  - Summary validation size: **87 HAM / 53 SPAM**
  - Category splits: 41 banking ham, 30 telecom ham, 22 Roman Urdu ham, 15 financial ham.

---

## 4. Evaluation Performance Metrics

* **UCI Test Set (Linear SVM Count):**
  - Accuracy: **98.25%** | Precision: **98.25%** | Recall: **87.50%** | F1-Score: **92.56%** | ROC-AUC: 99.08%
* **UCI Test Set (Fine-tuned DistilBERT):**
  - Accuracy: 97.86% | Precision: 96.49% | Recall: 85.94% | F1-Score: 90.91% | ROC-AUC: **99.51%**
* **PakScam Generalization (Generic Model):**
  - Combined HAM FPR: **82.8%** (72/87 FP) | Banking HAM FPR: **95.1%** (39/41 FP)
* **PakScam Generalization (Fine-tuned Candidate v3):**
  - Combined HAM FPR: **3.45%** (3/87 FP) | Banking HAM FPR: **2.44%** (1/41 FP) | Spam Recall: **100.0%**
* **Regression Gate Pass Rate:**
  - `distilbert-pakscam-v1` (Production): **5 / 14**
  - `distilbert-pakscam-v3` (Quarantined): **13 / 14** (Failed due to `zong_engage_prize_lang` Roman Urdu block)

---

## 5. Security & Privacy Invariants

* **Encryption Status:** SQLite local file is not encrypted; network transmission runs over plain HTTP.
* **Access Mappings:** API endpoints are exposed on port 8000 without token authentication or rate limiting.
* **Privacy Minimization:** Contact names are resolved natively on-device; backend processes SMS payloads transiently in memory with zero database retention.

---

## 6. Verification Test Scopes

* **Python Backend Tests:** **17 test files** (verifying 42 test functions under `pytest`).
* **Dart Frontend Tests:** **4 test files** (verifying 15 test cases under `flutter test`).
