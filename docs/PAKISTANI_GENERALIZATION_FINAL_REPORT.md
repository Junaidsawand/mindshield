# MindShield — Pakistani SMS Domain Generalization Final Report

> **Document ID**: `docs/PAKISTANI_GENERALIZATION_FINAL_REPORT.md`  
> **Phase**: 3.8 Multi-Model Domain Evaluation  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Executive Summary

This report documents the design, implementation, and multi-version evaluation of MindShield's machine learning models fine-tuned to generalize to the Pakistani SMS domain. SMS phishing (smishing) in Pakistan has distinct features—such as bilingual phrasing (English and Roman Urdu), local banking templates, carrier-specific billing codes, and intensive promotional language—that are absent in international baseline datasets like the UCI SMS Spam corpus.

Through consecutive iterations (`distilbert-pakscam-v1`, `v2`, and `v3`), we investigated domain generalization, shortcut learning mitigation, and evaluation metrics validation. Following strict production switch gate audits, we have decided to **KEEP distilbert-pakscam-v1 in production** and archive `v2` and `v3` as quarantined research candidates.

---

## 2. Multi-Model Performance Comparison

We evaluated the four primary models across eight distinct validation subsets. The results are summarized below (refer to `backend/data/metadata/v3_evaluation_results.json` for verified raw logs):

| Evaluation Subset | uci-v1 (Base) | pak-v1 (Production) | pak-v2 (Candidate) | pak-v3 (Candidate) |
| :--- | :---: | :---: | :---: | :---: |
| **UCI test F1** | 0.889 | **0.9600** | 0.9421 | **0.9508** |
| **UCI Precision** | 0.9836 | 0.9836 | 1.0000 | **1.0000** |
| **UCI Recall** | 0.9375 | 0.9375 | 0.8906 | **0.9062** |
| **UCI TN / FP / FN / TP** | 450/1/4/60 | 450/1/4/60 | 451/0/7/57 | **451/0/6/58** |
| **Pak HAM FPR (All)** | 82.8% (72/87 FP) | **93.1% (81/87 FP)** | 9.2% (8/87 FP) | **3.45% (3/87 FP)** |
| **Pak Banking HAM FPR** | 95.1% (39/41 FP) | 100.0% (41/41 FP) | 2.44% (1/41 FP) | **2.44% (1/41 FP)** |
| **Pak Telecom HAM FPR** | 70.0% (21/30 FP) | 80.0% (24/30 FP) | 20.0% (6/30 FP) | **3.33% (1/30 FP)** |
| **Pak Financial HAM FPR** | 75.0% (12/16 FP) | 100.0% (16/16 FP) | 6.67% (1/15 FP) | **6.67% (1/15 FP)** |
| **Pak Roman Urdu HAM FPR**| 40.9% (9/22 FP) | 72.7% (16/22 FP) | 0.00% (0/22 FP) | **13.64% (3/22 FP)** |
| **Pak SPAM Recall / F1** | 88.4% (FN: 11) | 98.11% (FN: 1) | 86.79% (FN: 7) | **100.0% (FN: 0)** |
| **Regression Pass Rate** | — | 5 / 14 | 11 / 14 | **13 / 14** |
| **Mean Inference Latency**| — | 41.95 ms | 60.80 ms | **57.62 ms** |

---

## 3. Regression Benchmarks Evaluation

We tracked the models' classification output across 14 critical regression messages representing edge-case scenarios:

| Regression Benchmark | Expected | pak-v1 | pak-v2 | pak-v3 | Status (v3) |
|---|---|---|---|---|---|
| **1. UBL IBFT receipt** | HAM | Phishing (0.9256) | Safe (0.9324) | **Safe (0.9926)** | **PASS** |
| **2. UBL ATM notification** | HAM | Phishing (0.9007) | Safe (0.9302) | **Safe (0.9930)** | **PASS** |
| **3. UBL CS + bit.ly link** | HAM | Phishing (0.9142) | Phishing (0.9151) | **Safe (0.9971)** | **PASS** |
| **4. Zong 50% OFF promo + bit.ly** | HAM | Phishing (0.9347) | Phishing (0.9767) | **Safe (0.7440)** | **PASS** |
| **5. Gaming Royale subscription**| HAM | Phishing (0.9216) | Phishing (0.5422) | **Safe (0.9950)** | **PASS** |
| **6. Gaming Royale FREE trial** | HAM | Phishing (0.9231) | Safe (0.6402) | **Safe (0.9968)** | **PASS** |
| **7. ReadyCash overdue loan** | HAM | Phishing (0.9160) | Safe (0.8681) | **Safe (0.9879)** | **PASS** |
| **8. ReadyCash due tomorrow** | HAM | Phishing (0.8994) | Safe (0.7511) | **Safe (0.9968)** | **PASS** |
| **9. Zong Engage prize lang** | HAM | Phishing (0.8599) | Safe (0.7224) | Phishing (0.9929) | **FAIL** |
| **10. Obvious prize phishing** | SPAM | Phishing (0.8994) | Phishing (0.9299) | **Phishing (0.9947)**| **PASS** |
| **11. Fake HBL bank verification**| SPAM | Phishing (0.8739) | Phishing (0.6135) | **Phishing (0.9951)**| **PASS** |
| **12. Fake UBL account suspend** | SPAM | Phishing (0.8812) | Phishing (0.7854) | **Phishing (0.9900)**| **PASS** |
| **13. OTP share phishing** | SPAM | Phishing (0.9110) | Phishing (0.8521) | **Phishing (0.9938)**| **PASS** |
| **14. Roman Urdu prize scam** | SPAM | Phishing (0.9112) | Phishing (0.7924) | **Phishing (0.9969)**| **PASS** |

---

## 4. The Generalization Story (v1 $\rightarrow$ v2 $\rightarrow$ v3)

1. **`distilbert-pakscam-v1` (Production Baseline)**: Trained on UCI data + 58 Pakistani samples. Fails to generalize. It categorizes almost all local HAM notifications as phishing (Banking FPR: $100\%$, Telecom FPR: $80\%$). The root cause was the model learning a "lexical shortcut" that **any message containing a link is spam** (since $100\%$ of links in the UCI training corpus belong to spam).
2. **`distilbert-pakscam-v2` (Research Candidate)**: Fine-tuned on ~140 Pakistani samples to teach the model that banking transactions and Roman Urdu text can be benign. This reduced banking FPR to $2.44\%$ and Roman Urdu FPR to $0.0\%$. However, it still failed on messages containing `bit.ly` shortened URLs (`ubl_customer_service_bitly` and `zong_50_percent_off`), because it had not seen shortened links in a benign context.
3. **`distilbert-pakscam-v3` (Research Candidate)**: Fine-tuned using **Mix-C oversampling** ($3\times$ oversampling of Pakistani templates) and augmented with 65 anti-shortcut samples (including legitimate surveys and telecom codes containing `bit.ly` links). This successfully broke the URL shortcut, resolving all `bit.ly` regression failures. However, it failed on `zong_engage_prize_lang` (predicting phishing with $99.29\%$ confidence) due to a new generalization bias: it over-associated the Roman Urdu phrase `"jeeto bade inaam"` ("win big prizes") with phishing grants (BISP/Ehsaas scams) added during training.

---

## 5. Production Decision & Status

* **Status**: **`distilbert-pakscam-v1` remains in production.**
* **Rationale**: Although `v3` demonstrates substantially better performance on Pakistani HAM FPR ($3.45\%$ vs. v1's $93.1\%$) and catches $100\%$ of Pakistani spam, it failed two critical promotion gates (exceeding the $2.0\%$ FPR threshold and failing 1 regression test). In a production cybersecurity environment, false alarms that block critical transactional messages (such as OTPs or credit notifications) are unacceptable.
* **Quarantine**: Both `v2` and `v3` weights remain archived in their isolated directories (`backend/data/models/distilbert_pakscam_v2/` and `backend/data/models/distilbert_pakscam_v3/`) and are **not** loaded by the FastAPI application wrapper.

---

## 6. Evidence References

* **v3 Training Configuration**: [`backend/data/models/distilbert_pakscam_v3/training_config.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/models/distilbert_pakscam_v3/training_config.json)
* **v3 Evaluation Metrics logs**: [`backend/data/metadata/v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json)
* **v3 Regression Test cases**: [`backend/tests/test_ml_regression_v3.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/tests/test_ml_regression_v3.py)
