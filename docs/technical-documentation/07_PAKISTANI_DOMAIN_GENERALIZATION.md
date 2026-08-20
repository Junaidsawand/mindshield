# Chapter 7 — Pakistani Domain Generalization & Localized Evaluation

This chapter presents the experimental design, results, and evaluation metrics surrounding the domain generalization of machine learning models deployed on the Pakistani SMS threat landscape. It analyzes the domain shift between international spam datasets and local Pakistani SMS messages, explores the root causes of base model generalization failures, and evaluates successive iterations of localized model training.

---

## 7.1 Chapter Introduction & Core Research Question

Evaluating a machine learning classifier solely on in-domain test data is insufficient when the target operational domain differs from the training distribution. Traditional SMS filtering models trained on Western corpora (such as the UCI SMS Spam Collection) perform poorly when deployed in the Pakistani SMS environment.

This research is designed to answer the following core question:
> How well do generic SMS spam detection models generalize to legitimate and malicious Pakistani SMS, and can localized Pakistani training data reduce domain-specific false positives while maintaining threat-detection capability?

To address this, the project evaluates baseline and fine-tuned models across a series of localized banking, microfinance, telecom, and Roman Urdu validation splits.

---

## 7.2 The Domain Shift Problem

**Domain Shift** occurs when the training source distribution $\mathcal{P}_{\text{source}}$ differs from the target operational distribution $\mathcal{P}_{\text{target}}$:

$$\mathcal{P}_{\text{source}}(X, Y) \neq \mathcal{P}_{\text{target}}(X, Y)$$

In MindShield's classification pipeline, this shift is characterized by distinct textual, linguistic, and structural variables:

### Table 7.1 — Domain Characteristics Comparison

| Linguistic / Structural Variable | Source Domain (Generic / UCI SMS) | Target Domain (Pakistani SMS) |
| :--- | :--- | :--- |
| **Primary Language** | English (US/UK context) | English, Roman Urdu, and Code-Switched dialects |
| **Urdu representation** | None | Roman Urdu (Latin script transcription) |
| **Currency Markers** | USD ($), GBP (£) | PKR, Rs., Rs |
| **Micro-Transaction Formats**| None | EasyPaisa, JazzCash, mobile wallet notifications |
| **Shortened URLs** | Present almost exclusively in spam class | Distributed across both spam and benign carrier promos |
| **Helpline Numbers** | Short codes (e.g. 5-digit numbers) | Local 111- banking helplines and 10-digit mobile numbers |

Because legitimate local carrier alerts and micro-transaction receipts borrow structural markers from the spam class (such as numeric values, shortened URLs, and urgent billing language), standard classifiers cannot separate benign local activity from malicious smishing vectors.

---

## 7.3 Baseline Generalization Failure

The base model, `distilbert-uci-v1`, trained strictly on generic international SMS data, demonstrates a major generalization failure when evaluated against local Pakistani messages.

The metrics reveal a critical performance drop. While the model achieves a high F1-score of **0.8890** on the in-domain UCI test set, it misclassifies legitimate Pakistani updates as threats:
* **Combined Pakistani HAM FPR:** **82.8%** (72 out of 87 benign messages flagged as phishing).
* **Pakistani Banking HAM FPR:** **95.1%** (39 out of 41 legitimate transaction notifications flagged as phishing).
* **Pakistani Financial HAM FPR:** **75.0%** (12 out of 16 mobile wallet alerts flagged as phishing).
* **Pakistani Telecom HAM FPR:** **70.0%** (21 out of 30 carrier promo alerts flagged as phishing).

### Table 7.2 — Base Model Generalization Failure Results

| Metric / Subset | Local In-Domain (UCI Test Set) | Out-of-Domain (Pakistani HAM Combined) | Out-of-Domain (Pakistani Banking HAM) |
| :--- | :---: | :---: | :---: |
| **Sample Size ($N$)** | 515 | 87 | 41 |
| **Accuracy** | 99.03% | 17.20% | 4.90% |
| **False Positives (FP)** | 1 | 72 | 39 |
| **False Positive Rate (FPR)**| **0.22%** | **82.80%** | **95.10%** |

### Mathematical Definition & Explicit Calculation:
The False Positive Rate (FPR) is defined as:

$$\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$

For the Pakistani Banking HAM subset, where the model flagged 39 messages as phishing out of 41 benign samples (meaning only 2 true negatives were correctly preserved):

$$\text{FPR}_{\text{banking}} = \frac{39}{39 + 2} = \frac{39}{41} \approx 95.12\%$$

This confirms that the generic base model is unusable in a local operational environment, as it would block nearly all transactional messages.

**Implementation Evidence:**
* **Source Logs:** [`backend/data/metadata/v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json)
* **Verify:** Logs under `"distilbert-uci-v1"` verify these counts and ratios.

---

## 7.4 Shortcut Learning in SMS Classifiers

The base model's high false alarm rate suggests **shortcut learning**. Deep neural networks often optimize for the simplest lexical correlations during training. 

In the UCI training corpus, features like URLs (especially shortened links like `bit.ly`) and financial terms (like `"bank"`, `"ATM"`, `"debit"`) appear exclusively in the spam/phishing class. As a result, the model learns a **lexical shortcut**:
$$\text{If "link" or "debit" present} \longrightarrow \text{Spam}$$
During inference on Pakistani HAM (which frequently contains these features in a benign context), the model relies on this shortcut, ignoring the overall semantic context. This shows that standard evaluation accuracy does not guarantee robustness against distribution shifts.

---

## 7.5 Localized Data Strategy & PakScam Evolution

MindShield uses the localized **PakScam-SMS** dataset to address shortcut learning. The training dataset evolved through three versions:

### Table 7.3 — PakScam Dataset Evolution

| Version | Composition | Training Strategy | Main Objective | Evaluation Focus |
| :--- | :--- | :--- | :--- | :--- |
| **`v1`** | 58 templates | Simple local spam / banking templates | Mitigate Roman Urdu spam detection limits | General localized templates |
| **`v2`** | 140 templates | Appended benign microfinance receipts | Reduce banking HAM false alarms | Legitimate local notifications |
| **`v3`** | 205 templates | Appended benign shortened URL (`bit.ly`) templates | Break the link-shortcut correlation | Benign link regression |

* **v1 Failure:** Incorporating only 58 templates was insufficient. It increased banking HAM FPR to **100%** (41/41) because the model over-associated English banking receipts with phishing.
* **v2 Failure:** Adding ~140 templates resolved basic banking false alarms but failed on benign messages containing shortened links (`bit.ly`), failing the regression test suite.
* **v3 Resolution:** Incorporating 65 benign anti-shortcut samples containing shortened links (`bit.ly`) successfully broke the URL shortcut, reducing total Pak HAM FPR to **3.45%**.

**Implementation Evidence:**
* **Report File:** [`docs/PAKISTANI_GENERALIZATION_FINAL_REPORT.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/PAKISTANI_GENERALIZATION_FINAL_REPORT.md) (Section 4)
* **Verify:** Documents the dataset version transitions and failure modes.

---

## 7.6 Hard-Negative Legitimate Banking Examples

Legitimate local financial transactions represent high-value hard negatives. These alerts contain indicators (numeric codes, links, currency tags) that mimic phishing layouts.

To force the model to learn contextual features, the training pipeline incorporates hard negatives directly into the training partition. 

### Mix-C Oversampling (Implemented)
To prevent the model from forgetting English baseline vocabulary during localized training, the training script applies **Mix-C oversampling**:
* Pakistani templates are oversampled by a factor of **$3\times$** (tripling their representation) relative to the baseline UCI dataset.
* The validation and test datasets are kept separate and are **never** augmented or oversampled, ensuring that evaluation metrics remain unbiased.

---

## 7.7 V3 Model Performance Metrics

The fine-tuned candidate model `distilbert-pakscam-v3` was evaluated against the PakScam validation splits:

### Table 7.4 — V3 Dataset Composition & Performance

| Category | Sample Size ($N$) | True Positives (TP) | False Positives (FP) | True Negatives (TN) | False Negatives (FN) | Category F1 / FPR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **UCI Test Set** | 515 | 58 | 0 | 451 | 6 | **0.9508 (F1)** |
| **Pakistani Spam** | 53 | 53 | — | — | 0 | **1.0000 (Recall)**|
| **Pakistani HAM (All)** | 87 | — | 3 | 84 | — | **3.45% (FPR)** |
| **Banking HAM** | 41 | — | 1 | 40 | — | **2.44% (FPR)** |
| **Telecom HAM** | 30 | — | 1 | 29 | — | **3.33% (FPR)** |
| **Financial HAM** | 15 | — | 1 | 14 | — | **6.67% (FPR)** |
| **Roman Urdu HAM** | 22 | — | 3 | 19 | — | **13.64% (FPR)**|

### Table 7.5 — Generic vs Localized Model Comparison

| Evaluation Metric | Generic Model (`uci-v1`) | Localized Model (`pak-v3`) | Absolute Performance Delta |
| :--- | :---: | :---: | :---: |
| **UCI test F1** | 0.8890 | 0.9508 | +6.18% |
| **Pakistani Spam Recall** | 88.40% | 100.00% | +11.60% |
| **Pakistani HAM FPR (All)**| 82.80% | 3.45% | -79.35% |
| **Banking HAM FPR** | 95.10% | 2.44% | -92.66% |
| **Telecom HAM FPR** | 70.00% | 3.33% | -66.67% |

**Implementation Evidence:**
* **Source Logs:** `v3_evaluation_results.json` (lines 266-368)
* **Verify:** Confirms the performance distribution of `distilbert-pakscam-v3`.

---

## 7.8 The Regression Testing Pipeline

To prevent model updates from regressing on resolved edge cases, the backend uses a regression testing suite (`test_ml_regression_v3.py`) containing 14 templates:

### Table 7.6 — Regression Test Categories

| ID | Test Name | Expected Label | v3 Prediction | Status |
| :--- | :--- | :---: | :--- | :---: |
| **1** | `ubl_ibft_receipt` | safe | **Safe (0.9926)** | **PASS** |
| **2** | `ubl_atm_debit` | safe | **Safe (0.9930)** | **PASS** |
| **3** | `ubl_customer_service_bitly` | safe | **Safe (0.9971)** | **PASS** |
| **4** | `zong_50_percent_off` | safe | **Safe (0.7440)** | **PASS** |
| **5** | `gaming_royale_subscription` | safe | **Safe (0.9950)** | **PASS** |
| **6** | `gaming_royale_free_trial` | safe | **Safe (0.9968)** | **PASS** |
| **7** | `readycash_overdue` | safe | **Safe (0.9879)** | **PASS** |
| **8** | `readycash_1_day_left` | safe | **Safe (0.9968)** | **PASS** |
| **9** | `zong_engage_prize_lang` | safe | Phishing (0.9929) | **FAIL** |
| **10** | `prize_phishing` | phishing | **Phishing (0.9947)** | **PASS** |
| **11** | `fake_bank_verification` | phishing | **Phishing (0.9951)** | **PASS** |
| **12** | `fake_account_suspension` | phishing | **Phishing (0.9900)** | **PASS** |
| **13** | `otp_phishing` | phishing | **Phishing (0.9938)** | **PASS** |
| **14** | `bisp_roman_urdu_scam` | phishing | **Phishing (0.9969)** | **PASS** |

The `v3` candidate failed a critical promotion gate because it misclassified `zong_engage_prize_lang` (predicting phishing with 99.29% confidence). This was caused by the model over-associating the Roman Urdu phrase `"jeeto bade inaam"` ("win big prizes") with BISP scams added during training. As a result, the production environment currently uses `distilbert-pakscam-v1` until this regression is resolved.

---

## 7.9 Out-of-Domain Generalization vs. In-Domain Performance

High in-domain evaluation metrics do not guarantee real-world generalization:
* The base model (`uci-v1`) achieved **99.03% in-domain accuracy** on the UCI test split but dropped to **17.20% accuracy** on Pakistani HAM.
* This discrepancy highlights the impact of **Domain Shift**. Models optimize for the specific features of their training sets; without local validation, their real-world performance can drop significantly.

---

## 7.10 Classical SVM vs. DistilBERT Localized Generalization

In Chapter 6, the classical baseline SVM model outperformed DistilBERT on standard test sets. However, classical models are limited in their generalization capabilities:
* **The Comparison Gap:** *The classical SVM model was not evaluated on the Pakistani smishing corpus, as the project's domain-adaptation pipeline is designed exclusively for deep-learning transformers.*
* **Contextual Generalization:** DistilBERT is preferred because it can model sentence-level context, which is necessary to distinguish benign transaction receipts from phishing attempts.

---

## 7.11 Research Contributions & Verification Matrix

### Table 7.7 — Research Contribution Evidence Matrix

| Research Claim | Support State | Evidence (Source Files) | Details / Invariants |
| :--- | :---: | :--- | :--- |
| **Pakistani SMS Localization**| **IMPLEMENTED** | `test_ml_regression_v3.py` | Validated against local banking, telecom, and wallet templates. |
| **Roman Urdu Phishing** | **IMPLEMENTED** | `v3_evaluation_results.json` | Catch rate tracked on Roman Urdu scam classes. |
| **FPR Reduction** | **DEMONSTRATED** | `PAKISTANI_GENERALIZATION_FINAL_REPORT.md`| FPR on banking HAM dropped from 95.10% to 2.44%. |
| **Regression-Gated Promotion** | **IMPLEMENTED** | `main.py` lifespan setup | Prevents model deployment if regression tests fail. |

---

## 7.12 Methodological Limitations

* **Limited Dataset Size:** The PakScam corpus contains 205 templates. While it captures common smishing structures, it does not represent the full variety of real-world SMS spam.
* **Lack of Real-world Field Validation:** Evaluation is restricted to synthetic templates. Live user-acceptance testing is required to verify real-world performance.
* **No Statistical Significance Testing:** Experiments were not repeated across multiple random seeds, so the metrics represent single training runs.

---

## 7.13 Chapter Summary

This chapter has detailed the domain shift and generalization challenges associated with deploying SMS classifiers in the Pakistani SMS environment. By introducing localized PakScam-SMS training data and regression gates, MindShield reduced false positive rates on local banking receipts from **95.10% to 2.44%**.

This localized, regression-gated ML classification engine integrates with the frontend mobile architecture via the API contracts detailed in **Chapter 8 — Backend/API Architecture & Implementation**.
