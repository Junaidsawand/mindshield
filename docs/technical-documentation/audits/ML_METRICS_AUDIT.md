# Machine Learning Metrics Audit

This document verifies the exact metrics, training times, model sizes, and latency profiles of the machine learning models implemented in MindShield.

---

## 1. Verified Model Benchmarks

The following benchmarks are verified against [`distilbert_metrics.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/distilbert_metrics.json) and [`baseline_models_comparison.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/baseline_models_comparison.json):

| Metric / Parameter | Fine-Tuned DistilBERT | Linear SVM (Count Vectorizer) | Delta (SVM vs. DistilBERT) |
| :--- | :---: | :---: | :---: |
| **Accuracy** | 97.86% (0.9786) | **98.25% (0.9825)** | +0.39% |
| **Precision** | 96.49% (0.9649) | **98.25% (0.9825)** | +1.76% |
| **Recall** | 85.94% (0.8594) | **87.50% (0.8750)** | +1.56% |
| **F1-Score** | 90.91% (0.9091) | **92.56% (0.9256)** | +1.65% |
| **ROC-AUC** | **99.51% (0.9951)** | 99.08% (0.9908) | -0.43% |
| **Matthews Corr (MCC)** | 0.8990 | **0.9177** | +1.87% |
| **Model Size** | 255.425 MB | **0.1936 MB** | -99.92% |
| **Training Time** | 1,101.61 seconds | **0.1183 seconds** | -99.98% |
| **Prediction Latency** | 57.62 ms (mean) | **5.00 ms (mean)** | -91.32% |
| **Confusion Matrix** | TP: 55, FP: 2, TN: 449, FN: 9 | TP: 56, FP: 1, TN: 450, FN: 8 | — |

---

## 2. Technical Evaluation Conditions & Discrepancies

### The "Winner" Contradiction:
* **The Facts:** The classical baseline model (`linear_svm_count`) outperforms the deep learning model (`distilbert-base-uncased`) on almost all metrics on the test dataset. In addition, the SVM is **$1,300\times$ smaller** in size (0.19 MB vs. 255 MB) and **$10\times$ faster** in inference.
* **Why DistilBERT is still used:** While SVM works exceptionally well on simple, keyword-heavy in-domain test splits (since it can memorize token associations), it lacks semantic context modeling. Transformers are much better suited to capture structural, contextual, and word-order variations in unseen or spoofed smishing messages where keywords might be obfuscated. 
* **Action for Thesis:** When documenting the results, explicitly state this trade-off. Do not hide the fact that SVM scored higher. Explain it in terms of **generalization capacity vs. local over-optimization**.

### Evaluation Set Context:
These metrics are calculated on the in-domain test split (composed of **515 samples** extracted from the cleaned UCI SMS dataset), not the Pakistani PakScam dataset. The PakScam performance metrics are analyzed separately under the regression and domain failure reports.
