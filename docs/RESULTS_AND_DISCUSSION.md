# MindShield — Results and Discussion

> **Document ID**: `docs/RESULTS_AND_DISCUSSION.md`  
> **Phase**: FYP-I Results and Discussion  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Dataset Results and Summary

The MindShield system was evaluated using two primary datasets: the public UCI SMS Spam Collection and the custom-curated PakScam-SMS corpus.

### 1.1 Dataset Statistics
* **UCI SMS Spam Collection (Cleaned & Deduplicated)**: **5,148 records** (4,506 HAM, 642 SPAM).
  * *Splits*: Train = 4,118 records; Val = 515 records; Test = 515 records.
* **PakScam Base templates (v2)**: **140 unique records** (87 HAM, 53 SPAM).
  * *Note*: This base set includes 125 synthetic templates and 15 real-world user-observed seeds (the 15 seeds are included *within* the 140 base templates, not in addition).
* **PakScam Augmentations (v3)**: **65 unique records** (55 HAM, 10 SPAM).
* **Combined PakScam Dataset (v3)**: **205 unique records** (142 HAM, 63 SPAM).

---

## 2. Baseline Model Evaluation

To establish a benchmark, several classical machine learning classifiers were evaluated on the UCI test split (515 records).

| Model ID | Vectorizer | Accuracy | Precision | Recall | F1-Score | Training Time | Model Size |
|---|---|---|---|---|---|---|---|
| **linear_svm_count** (Best) | Count | **$98.25\%$** | $98.25\%$ | **$87.50\%$** | **$92.56\%$** | $0.1183\text{ s}$ | $0.19\text{ MB}$ |
| **logistic_regression_count** | Count | $97.86\%$ | $98.18\%$ | $84.38\%$ | $90.76\%$ | $0.0226\text{ s}$ | $0.04\text{ MB}$ |
| **linear_svm_tfidf** | TF-IDF | $97.67\%$ | $93.33\%$ | $87.50\%$ | $90.32\%$ | $0.0557\text{ s}$ | $0.19\text{ MB}$ |
| **multinomial_nb_count** | Count | $97.28\%$ | $89.06\%$ | $89.06\%$ | $89.06\%$ | $0.0019\text{ s}$ | $0.15\text{ MB}$ |
| **random_forest_tfidf** | TF-IDF | $96.89\%$ | $98.00\%$ | $76.56\%$ | $85.96\%$ | $0.3546\text{ s}$ | $4.43\text{ MB}$ |
| **multinomial_nb_tfidf** | TF-IDF | $96.31\%$ | **$100.00\%$** | $70.31\%$ | $82.57\%$ | $0.0019\text{ s}$ | $0.15\text{ MB}$ |
| **logistic_regression_tfidf** | TF-IDF | $95.92\%$ | $92.16\%$ | $73.44\%$ | $81.74\%$ | $0.0271\text{ s}$ | $0.03\text{ MB}$ |

### 2.1 Interpretation
While the classical best baseline (`linear_svm_count`) achieves a strong $92.56\%$ F1-score on the English UCI dataset, it relies on static bag-of-words configurations. This prevents it from capturing contextual structures, Roman Urdu transliterations, and code-switched variations, motivating the transition to a Transformer-based classifier (DistilBERT).

---

## 3. DistilBERT Model Results Comparison

The active production model (`distilbert-pakscam-v1`) was compared against the research candidate (`distilbert-pakscam-v3`) across three test subsets.

### 3.1 Model Performance Matrix

| Evaluation Subset | Metric | active model (`v1`) | research candidate (`v3`) |
|---|---|---|---|
| **UCI Test Split** (515 samples) | F1-Score | **$96.00\%$** | $95.08\%$ |
| | Precision | $98.36\%$ | **$100.00\%$** |
| | Recall | **$93.75\%$** | $90.62\%$ |
| | FPR | $0.22\%$ | **$0.00\%$** |
| **PakScam Test Split** (87 samples) | HAM False Positive Rate (FPR) | $93.10\%$ ($81/87$ failed) | **$3.45\%$** ($3/87$ failed) |
| | SPAM Recall (53 samples) | $98.11\%$ ($52/53$ passed) | **$100.00\%$** ($53/53$ passed) |
| **14-Case Regression Suite** | Pass Rate | $35.71\%$ ($5/14$ passed) | **$92.86\%$** ($13/14$ passed) |
| **Performance SLA** | CPU Inference Latency (Mean) | **$41.95\text{ ms}$** | $57.62\text{ ms}$ |
| | CPU Inference Latency (Max) | **$50.74\text{ ms}$** | $77.51\text{ ms}$ |

---

## 4. Discussion and Key Findings

### 4.1 Domain Shift Analysis
The evaluation reveals a significant domain shift:
* **Active model (`v1`)**: Achieves $96.00\%$ F1 on the UCI benchmark but fails on Pakistani HAM, misclassifying $93.10\%$ ($81/87$) of legitimate local alerts. This is because features like banking links (e.g. `bit.ly`) and numeric codes act as strong spam indicators in the English UCI dataset, but are common in benign Pakistani transaction and carrier notifications.
* **Research candidate (`v3`)**: By incorporating $65$ targeted augmentations and applying Mix-C oversampling, `v3` reduces the false-positive rate on Pakistani HAM to $3.45\%$ ($3/87$) and achieves $100\%$ spam recall. This improvement comes with a minor trade-off in UCI test performance (F1 drops from $96.00\%$ to $95.08\%$) and increased CPU inference latency (mean latency increases from $41.95\text{ ms}$ to $57.62\text{ ms}$).

### 4.2 Latency Definitions
The reported latencies ($41.95\text{ ms}$ and $57.62\text{ ms}$) represent **model CPU inference latency** (including text tokenization and PyTorch forward passes). They do **not** represent end-to-end latency, as network transit times and client-side UI rendering are excluded.

---

## 5. Why v3 is Kept as a Research Candidate
Although `v3` shows improved performance in the Pakistani domain, it remains a quarantined research candidate for the following reasons:
1. **Limited Localized Corpus**: Evaluated on $205$ unique templates. Promoting it to production requires testing on a larger, independent corpus.
2. **SLA Threshold Gating**: Maximum inference latency reaches $77.51\text{ ms}$, exceeding the $60\text{ ms}$ SLA target and requiring optimization.
3. **Regression Suite Overlap**: The 14-case regression suite is derived from base templates, meaning it does not function as an independent test set.

---

## 6. Limitations of the Current Prototype (FYP-I)
1. **Small Localized Dataset**: The 205-template corpus restricts geographical, dialectal, and formatting representation.
2. **Template Bias**: The synthetic generator uses static templates, which may limit generalization to novel real-world spam formats.
3. **Local HTTP Communication**: Payload transit runs over unencrypted HTTP.
4. **Heuristic Explanations**: The highlight cards use static rule-based checks. True LIME explanations are deferred due to CPU latency constraints.

---

## 7. FYP-I Accomplishments
* Developed a Flutter Android client with background SMS interception.
* Configured local SQLite caching (`sms_messages` table) and XML-based user configurations (`SharedPreferences`).
* Built a FastAPI inference server with a fine-tuned DistilBERT classification pipeline.
* Constructed the PakScam-SMS localized template dataset (205 records).
* Implemented a template-family splitting process to prevent data leakage.

---

## 8. FYP-II Research Roadmap
1. **Scale local data**: Compile a larger, independently annotated Pakistani SMS dataset ($5,000+$ records).
2. **Multilingual Models**: Train multilingual representations (e.g., XLM-RoBERTa) to capture code-switched structures.
3. **On-Device Inference**: Port models to ONNX Runtime for local, offline execution.
4. **Explainability**: Implement optimized LIME approximations suitable for sub-second execution on mobile devices.
5. **Secure Channels**: Deploy models using production HTTPS and token-based JWT authorization.
