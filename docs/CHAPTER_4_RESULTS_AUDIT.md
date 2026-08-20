# MindShield Chapter 4 Results Audit & Reconciliation Report

This report documents the verification, mapping, and audit trail of every numerical metric in **Chapter 4 (Results and Discussion)** of the thesis draft.

---

## 1. Final Audit Status

**`[READY FOR SUPERVISOR REVIEW]`**

---

## 2. Metric Verification Table

All metrics presented in Chapter 4 are verified and mapped to their exact source:

| Document Metric | Value in Text | Math Denominator / Samples | Source / Evidence Location | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **UCI Cleaned Corpus size** | 5,148 | - | `uci_sms_spam_clean.csv` | **Verified** |
| **UCI legitimate HAM** | 4,500 | - | `uci_sms_spam_clean.csv` | **Verified** |
| **UCI spam SPAM** | 648 | - | `uci_sms_spam_clean.csv` | **Verified** |
| **UCI Test Split size** | 515 | 10% of UCI clean | `train_pakscam_v3_distilbert.py` | **Verified** |
| **PakScam v3 unique templates** | 205 | - | `train_pakscam_v3_distilbert.py` | **Verified** |
| **PakScam base templates (v2)** | 140 | 87 HAM, 53 SPAM | `v3_evaluation_results.json` | **Verified** |
| **PakScam augmentations** | 65 | 55 HAM, 10 SPAM | `train_pakscam_v3_distilbert.py` | **Verified** |
| **PakScam combined HAM** | 142 | - | `train_pakscam_v3_distilbert.py` | **Verified** |
| **PakScam combined SPAM** | 63 | - | `train_pakscam_v3_distilbert.py` | **Verified** |
| **Baseline linear_svm F1** | 92.56% | 515 UCI Test | `scikit_baseline_comparison.json` | **Verified** |
| **v1 UCI F1-score** | 96.00% | 515 UCI Test | `v1_evaluation_results.json` | **Verified** |
| **v1 PakScam SPAM Recall** | 98.11% | 52 / 53 passed | `v1_evaluation_results.json` | **Verified** |
| **v1 Localized HAM FPR** | 93.10% | 81 / 87 failed | `v1_evaluation_results.json` | **Verified** |
| **v3 UCI F1-score** | 95.08% | 515 UCI Test | `v3_evaluation_results.json` | **Verified** |
| **v3 PakScam SPAM Recall** | 100.00% | 53 / 53 passed | `v3_evaluation_results.json` | **Verified** |
| **v3 Localized HAM FPR** | 3.45% | 3 / 87 failed | `v3_evaluation_results.json` | **Verified** |
| **v1 Mean CPU Latency** | 41.95 ms | 30 runs | `v1_latency_benchmark.json` | **Verified** |
| **v1 Max CPU Latency** | 50.74 ms | 30 runs | `v1_latency_benchmark.json` | **Verified** |
| **v3 Mean CPU Latency** | 57.62 ms | 30 runs | `v3_latency_benchmark.json` | **Verified** |
| **v3 Max CPU Latency** | 77.51 ms | 30 runs | `v3_latency_benchmark.json` | **Verified** |
| **v1 Regression Suite Pass** | 35.71% | 5 / 14 passed | `v1_regression_test.json` | **Verified** |
| **v3 Regression Suite Pass** | 92.86% | 13 / 14 passed | `v3_regression_test.json` | **Verified** |
| **Pytest Backend Assertions** | 234 | - | `backend/tests/` pytest run | **Verified** |
| **Flutter Widget Smoke Tests** | 5 | - | `frontend/test/` widget run | **Verified** |

---

## 3. Discrepancy Reconciliation Summary

* **FPR Denominator**: Reconciled local bank transaction HAM test set to exactly **87 samples** across both v1 and v3 evaluations. The fraction is mathematically consistent ($81/87 = 93.10\%$, $3/87 = 3.45\%$).
* **Pytest Assertions**: Clarified terminology in Section 4.9. "234" represents the total number of validation test assertions executed by the Pytest pipeline, rather than distinct test files.
* **SLA Latency Bounds**: Clarified that v3 candidate mean latency ($57.62\text{ ms}$) satisfies the sub-60 ms SLA threshold, whereas its maximum latency ($77.51\text{ ms}$) is a documented bottleneck.
* **Regression Wording**: Standardized academic text to say "substantially improved performance on the evaluated regression templates" rather than claiming it "proves" stability, keeping it in line with peer-review standards.
