# MindShield Chapter 3 Forensic Audit & Reconciliation Report

This report documents the verification and reconciliation of system design parameters, dataset splits, hyperparameters, figures, and testing hierarchies in **Chapter 3 (Research Methodology)** of the thesis draft.

---

## 1. Final Status

**`[READY FOR SUPERVISOR REVIEW]`**

---

## 2. Reconciled Dataset Statistics

All dataset volume parameters have been verified and reconciled against repository evidence (`train_pakscam_v3_distilbert.py` and processing scripts):

* **UCI SMS Spam Collection**: **5,148 records** (4,500 HAM, 648 SPAM).
* **PakScam-SMS Corpus Size**: **205 unique templates**, composed of:
  - *Base Templates (`v2`)*: **140 unique templates** (87 HAM, 53 SPAM).
  - *Augmentations (`v3_aug`)*: **65 manual templates** (55 HAM, 10 SPAM).
  - *Combined Dataset (`v3`)*: **205 templates** (142 HAM, 63 SPAM).
* **Class Balance Verification**:
  $$\text{Total HAM} = 87 \text{ (Base)} + 55 \text{ (Augmentations)} = 142 \text{ HAM}$$
  $$\text{Total SPAM} = 53 \text{ (Base)} + 10 \text{ (Augmentations)} = 63 \text{ SPAM}$$
  $$\text{Combined Size} = 142 + 63 = 205 \text{ unique templates}$$

---

## 3. Reconciled Training Hyperparameters

Every hyperparameter documented in Chapter 3 aligns exactly with the values defined in `train_pakscam_v3_distilbert.py`:

* **Optimizer**: `AdamW` (HuggingFace Trainer default, weight decay=0.01).
* **Optimizer Learning Rate**: `2e-5` (using linear learning rate decay).
* **Batch Size**: `32` (training and evaluation batch size).
* **Max Sequence Length**: `128` (padding/truncation WordPiece tokens).
* **Training Epochs**: `4` (utilizing early stopping with patience of 3).
* **Loss Function**: Binary `CrossEntropyLoss` (model-default objective).
* **Model Initialization**: Pre-trained `distilbert-base-uncased` weights.

---

## 4. Reconciled Preprocessing Presets

The text normalization engine in `app/nlp/normalizer.py` implements two distinct presets:

1. **Classical ML Pipeline**: Case folding, URL/Email/Phone regex-to-placeholder masking (`[URL]`, `[EMAIL]`, `[PHONE]`), stopword removal, lemmatization, and TF-IDF sparse matrix construction.
2. **Transformer Preset**: Light normalization (whitespace trimming, null byte stripping) preserving case, punctuation, emojis, and URLs to support `distilbert-base-uncased` WordPiece subword tokenization.

---

## 5. Reconciled Split & Oversampling Strategies

* **Template-Family Grouping**: To prevent data leakage, splits are grouped by `template_family` (ensuring that variations of the same transactional SMS template do not appear in both the training split and the testing split).
* **Mix-C Oversampling**: A project-specific experimental strategy combining $1 \times \text{UCI Training Corpus} + 3 \times \text{PakScam-SMS Training Split}$ to mitigate geographical domain imbalance and catastrophic vocabulary forgetting.

---

## 6. Figure Order & UI Formatting

* **Figure 3-4 (DFD Level 0)**: Successfully swapped and positioned first as `Figure 3-4 Data Flow Diagram - Level 0 (Context Level)`.
* **Figure 3-5 (DFD Level 1)**: Successfully positioned second as `Figure 3-5 Data Flow Diagram - Level 1 (Process Level)`.
* **Mobile UI Screenshots**: Center-aligned and set to uniform `2.5"` width, with captions matched to Section 3.12 (Figures 3-8 to 3-16).

---

## 7. Testing & SLA Metrics Reconciliation

* **Testing Hierarchy**:
  - *Backend Unit/Integration Tests*: **234 Pytest assertions** (routing, schemas, ML loaders).
  - *Frontend Widget Tests*: **5 Flutter widget tests** (dashboard, inbox, analysis rendering).
  - *Regression Suite*: **14-case regression suite** (static assertion benchmark, not an independent test set).
* **Metric Formulations**: LaTeX formulations for Accuracy, Precision, Recall, F1-Score, and False Positive Rate (FPR) have been inserted in Section 3.14.
* **Latency SLA**: The under-60-ms SLA applies strictly to the **mean CPU inference latency** (v1: 41.95 ms, v3: 57.62 ms), whereas worst-case maximum latency can exceed the SLA (v3 max: 77.51 ms).
