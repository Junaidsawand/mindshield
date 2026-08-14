# MindShield — ML Pipeline Forensic Audit & Root Cause Analysis

> **Document ID**: `backend/docs/11_ML_Pipeline_Audit.md`  
> **Phase**: 3.5 ML Pipeline Alignment & Domain Adaptation  
> **Status**: Verified Forensic Audit  

---

## 1. Executive Overview

This document presents the technical forensic audit of the MindShield machine learning inference and fine-tuning pipeline. A full end-to-end investigation was conducted across data preparation (`app/data/`), NLP normalization (`app/nlp/`), DistilBERT fine-tuning (`app/distilbert/`), and model loading (`app/core/model_loader.py`).

---

## 2. Confirmed Root Causes

### 2.1 Preprocessing Discrepancy (Training vs. Inference Divergence)
- **Training Path**: `DistilBERTTrainer.train_and_evaluate()` applied `NLPPreprocessingPipeline(create_classical_config())`. This transformed raw SMS payloads into porter-stemmed, stopword-filtered strings where URLs were replaced with `url` and numbers with `number`.
- **Inference Path**: `HuggingFaceModelLoader.predict()` fed raw, un-normalized SMS text directly into `AutoTokenizer`.
- **Consequence**: The fine-tuned weights never observed raw URL tokens (`http://example.com` tokenized into `['http', ':', '/', '/', 'example', '.', 'com']`) during training. Raw prize scams failed detection ($P(\text{spam}) = 0.4798 \rightarrow \text{safe}$).

### 2.2 Domain Out-of-Distribution Shift (UCI Only)
- The baseline model `distilbert-uci-v1` was fine-tuned exclusively on 5,148 samples from the 2011 UK/US UCI SMS Spam Collection.
- Legitimate Pakistani bank receipts (`PKR`, `UBL`, `IBFT`, `Tx ID`) were out-of-distribution, triggering false positive spam classifications ($P(\text{spam}) = 0.7944 \rightarrow \text{phishing}$).

---

## 3. Comparative Forensic Benchmark of Legacy Baseline (`distilbert-uci-v1`)

| Benchmark Input Payload | Logits $[z_0, z_1]$ | $P(\text{spam})$ | Predicted Class | Application Label | Threat Level | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST 1 (UBL Receipt)** | `(-0.9845, 0.7304)` | $0.8475$ | Class 1 (Spam) | `phishing` | `dangerous` | False Positive |
| **TEST 2 (Prize Scam)** | `(-0.4570, 0.4610)` | $0.7146$ (raw: $0.4798$) | Class 0 (Ham) | `safe` | `safe` | False Negative |
| **TEST 3 (Bank Phishing)** | `(-0.6347, 0.5730)` | $0.7699$ | Class 1 (Spam) | `phishing` | `dangerous` | True Positive |

---

## 4. Architectural Mitigation Blueprint

1. **Shared Deterministic Preprocessor**: Mandate `NLPPreprocessingConfig.create_transformer_config()` across training, validation, testing, and production inference.
2. **Model Versioning**: Preserve `distilbert-uci-v1` as legacy baseline, build `distilbert-uci-v2` for raw-text aligned evaluation, and fine-tune `distilbert-pakscam-v1` on multi-domain data.
