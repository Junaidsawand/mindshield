# Chapter 5 — Data Engineering & Preprocessing

This chapter describes the data engineering, data cleaning, corpus curation, and preprocessing pipelines implemented in the MindShield SMS threat detection system. 

---

## 5.1 Chapter Introduction

In machine learning-based SMS threat detection, the quality, representativeness, and distribution of the underlying corpus directly govern model generalization. Most SMS spam filters are trained on international benchmark datasets, such as the UCI SMS Spam Collection, which contains messages collected primarily in Western regions (such as the UK and US) in 2011.

While models trained on these datasets achieve high local accuracy, they suffer from a severe **Domain Shift** when deployed in localized markets like Pakistan. The Pakistani SMS ecosystem contains distinct linguistic and structural features:
* Intensive code-switching and bilingual mixing (English and Roman Urdu).
* High frequencies of legitimate automated transactional notifications from local microfinance and banking services (e.g., EasyPaisa, JazzCash, UBL, HBL).
* Local telecom promotions containing shortened URL links (e.g. `bit.ly`).

Under international baseline training, these local markers trigger high False Positive Rates (FPR). Legitimate transaction receipts and carrier codes are misclassified as phishing attempts because the model over-associates words like "bank," "payment," and shortened links with malicious activities. Resolving this domain shift requires localized data curation and a robust, anti-shortcut preprocessing pipeline.

---

## 5.2 Dataset Architecture

MindShield combines general-purpose English datasets with custom-developed localized corpora. The system utilizes two primary datasets:
1. **UCI SMS Spam Collection:** Used to train the base classification head on core spam/ham patterns.
2. **PakScam-SMS Corpus:** A localized, template-driven dataset developed across three iterative versions to teach the model Pakistani-specific smishing vectors and legitimate transaction structures.

### Table 5.1 — Dataset Overview

| Dataset Name | Ingested Format | Total Records | Class Balance (Ham/Spam) | Language Profile | Purpose | Local File Path |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UCI SMS Spam** | TSV (Headerless) | 5,148 (Cleaned) | 4,510 / 638 | English | Base Classifier Training | [`backend/data/processed/train.csv`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/processed) |
| **PakScam-SMS** | CSV (Headered) | 205 templates | 87 / 53 (Val/Test split) | Roman Urdu / English | Local Domain Adaptation | [`backend/data/models/distilbert_pakscam_v3`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/models/distilbert_pakscam_v3) |

**Implementation Evidence:**
* **File Paths:** [`backend/app/data/config.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/data/config.py)
* **Verify:** `DatasetConfig` and `UCI_SMS_CONFIG` dataclasses declare TSV format, delimiter, and paths.

---

## 5.3 UCI SMS Spam Collection

The UCI SMS Spam Collection serves as the primary dataset for base model training.

* **Raw Ingested Records:** **5,562**
* **Deduplication:** **414** exact duplicate entries are removed to prevent overfitting and data leakage.
* **Final Cleaned Record Count:** **5,148**
* **Class Balance:** Legitimate (Ham) represents **4,510 records (87.6%)** and Spam represents **638 records (12.4%)**.
* **Imbalance Ratio:** $7.06:1$.

### Table 5.3 — Class Distribution (UCI Cleaned)

| Class | Label | Record Count | Percentage |
| :--- | :---: | :--- | :---: |
| **Ham** | 0 | 4,510 | 87.6% |
| **Spam** | 1 | 638 | 12.4% |

**Implementation Evidence:**
* **Metadata file:** [`backend/data/metadata/uci_sms_spam_metadata.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/uci_sms_spam_metadata.json)
* **Verify:** `deduplication_audit` logs: `initial_raw_records = 5562`, `exact_duplicates_removed = 414`, `final_cleaned_records = 5148`.

---

## 5.4 PakScam-SMS Dataset

The PakScam-SMS dataset is a custom localized threat corpus representing Pakistani transactional notifications, carrier codes, and smishing attacks. It evolved over three major iterations:

1. **PakScam v1 (58 templates):** Addressed baseline Roman Urdu spam and simple local bank phishing templates.
2. **PakScam v2 (140 templates):** Expanded to include legitimate local transaction formats (microfinance and commercial bank templates) to reduce False Positives.
3. **PakScam v3 (205 templates):** Augmented with 65 benign "anti-shortcut" telecom templates containing shortened links (`bit.ly`, `tinyurl`) to break the model's correlation that all links are malicious.

### Table 5.2 — Dataset Version Comparison

| Dataset Version | Active Templates | Local Banking Ham | Roman Urdu Smishing | Benign Link Samples | Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **PakScam v1** | 58 | Implemented | Implemented | None | Archived |
| **PakScam v2** | 140 | Expanded | Expanded | None | Archived |
| **PakScam v3** | 205 | Expanded | Expanded | 65 | Quarantined / Research |

The dataset is partitioned into specific categories to evaluate domain limits:
* **`banking_ham` (41 samples):** Benign transactional updates from commercial banks (e.g. UBL, HBL) containing PKR amounts.
* **`telecom_ham` (30 samples):** Subscriptions and package updates from local telecom operators (Zong, Jazz).
* **`roman_urdu_ham` (22 samples):** Legitimate personal text messages written in Roman Urdu.
* **`financial_ham` (15 samples):** Microfinance and wallet receipt notices (EasyPaisa, JazzCash).
* **`pak_spam` (53 samples):** SMS phishing, OTP request scams, BISP/Ehsaas Roman Urdu grants fraud.

**Implementation Evidence:**
* **Metadata file:** [`backend/data/metadata/v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json)
* **Verify:** Declares categories under `pak_ham_categories` (banking_ham: 41, telecom_ham: 30, roman_urdu_ham: 22, financial_ham: 15) and `pak_spam` (53).

---

## 5.5 Hard-Negative Ham

In classification tasks, **Hard-Negatives** are benign samples that share a high density of lexical features with the positive (spam) class. Ordinary ham examples (e.g. "Hi honey, see you at dinner!") are insufficient because they do not contain security markers. 

Legitimate Pakistani banking SMS (e.g. `"Your A/C *5034 is debited with PKR 5,000 from ATM. Info: 111-825-888"`) resemble phishing messages because they contain:
* Numeric references (PKR currency values, account numbers, and support helpline numbers).
* Shortened URLs (e.g., bit.ly links pointing to terms of service).
* Action-oriented imperatives ("repay loan," "dial code").

If models are trained only on standard datasets, they develop **shortcut learning** (using easy-to-learn markers like links or currency notations as absolute proxy signals for spam). MindShield addresses this by introducing custom hard-negative templates directly into the training partition. This forces the model to attend to the semantic context (e.g., formal transactional phrasing vs. urgent credential-request patterns) rather than raw keyword triggers.

**Implementation Evidence:**
* **Test file:** [`backend/tests/test_ml_regression_v3.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/tests/test_ml_regression_v3.py)
* **Verify:** Defines Parametrized regression tests for banking receipts (`ubl_ibft_receipt`, `ubl_atm_debit`, `readycash_overdue`) which are expected to return `safe` despite containing links and credit/debit keywords.

---

## 5.6 Pakistani Language Characteristics

MindShield operates on bilingual SMS streams. This presents distinct natural language processing (NLP) challenges:

* **Roman Urdu:** Urdu written using Latin characters (e.g., `"aap ke account mein PKR 25,000 credit ho gaye"`). Roman Urdu lacks standardized spelling conventions (e.g., the word "Inaam" can be spelled *inam*, *enaam*, or *enaam*), creating sparse vocabulary representation.
* **Code-Switching:** Rapid alternation between English and Roman Urdu within the same message (e.g., `"Jeetne ke liye reply 1 to subscribe"`).
* **Pakistani Terminology:** Frequent references to local institutions (HBL, UBL, BISP, EasyPaisa) and abbreviations.

Due to the lack of pre-trained Roman Urdu transformers, the system fine-tunes DistilBERT to build subword representations for these localized spelling variants. *Note: Support for Arabic-script Urdu (Urdu alphabet) is NOT IMPLEMENTED in this version; the language scope is strictly limited to English and Latin-script Roman Urdu.*

### Table 5.4 — Language Distribution (PakScam v3)

| Language Class | Verified Support State | Typical Phrasing Pattern |
| :--- | :---: | :--- |
| **English** | **IMPLEMENTED** | "OTP code to stop unauthorized transaction of PKR 45,000." |
| **Roman Urdu** | **IMPLEMENTED** | "BISP ki taraf se 25,000 rupay approved hain." |
| **Code-Switched** | **IMPLEMENTED** | "Jeetne ke liye tayyar ho jao... 6PKR/Day, Reply 1." |
| **Urdu (Arabic Script)**| **NOT IMPLEMENTED** | — |

**Implementation Evidence:**
* **Test cases:** `test_ml_regression_v3.py` (lines 44, 65, 85).
* **Verify:** Parametrized checks verify Roman Urdu templates like `"Jeetne ke liye tayyar ho jao..."` and `"HBL: Aap ke account..."`.

---

## 5.7 Data Cleaning

The data cleaning pipeline is divided into raw deduplication and runtime sanitization:

1. **Duplicate Removal:** Done offline. Exact string duplicates are pruned using pandas deduplication routines before splitting.
2. **Missing-Value Handling:** Empty rows or inputs with purely whitespace characters are dropped during dataset ingestion.
3. **Unicode Normalization:** NFKC normalizer converts ligatures and full-width/half-width characters to standard ASCII forms.
4. **Whitespace Normalization:** Leading/trailing whitespaces are trimmed, and multiple internal spacing runs are collapsed to a single space.
5. **Length Constraints:** Inputs under 3 characters or over 2,000 characters are rejected at the API layer.
6. **Purely Numeric Filter:** Purely numeric messages (e.g., bare OTP codes like "123456") are blocked from analysis to prevent classifier bias.

### Table 5.5 — Preprocessing Operations

| Operation | Implemented Level | Implementation Technique | Target Output |
| :--- | :---: | :--- | :--- |
| **Unicode Normalization**| Runtime | `unicodedata.normalize("NFKC", text)` | Standard ASCII equivalent |
| **Whitespace Collapse** | Runtime | `re.sub(r"\s+", " ", text)` | Single space separators |
| **Length Filter** | API Validator | `3 <= len(text.strip()) <= 2000` | Rejection of short/long SMS |
| **Numeric Block** | API Validator | `not stripped.isdigit()` | Rejection of bare OTPs |
| **Punctuation Stripping** | TF-IDF / Baselines | Handled during Vectorization | Cleaned token tokens |
| **Case Lowering** | Baseline Only | Enabled via Config | Lowercased terms |

**Implementation Evidence:**
* **Source File:** [`backend/app/utils/validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py)
* **Verify:** `sanitise_message(text)` applies NFKC normalization and whitespace sub. `is_valid_message(text)` enforces character length limits and `.isdigit()` exclusions.

---

## 5.8 Text Normalization

The NLP pipeline maintains two separate normalizations depending on the execution stage:

### 1. Training-Time Preprocessing
During model training and validation, the pipeline applies stemmer and lemmatizer normalization options to evaluate vocab reductions:
* **Stemming:** Porter Stemmer reduces inflected words to their word stems (e.g., "connecting" -> "connect").
* **Lemmatization:** WordNet Lemmatizer uses part-of-speech taggings to return dictionary headwords.
* **Stopword Removal:** NLTK English stopwords are stripped.

### 2. Inference-Time Preprocessing
To maximize performance and maintain real-time throughput, inference preprocessing is kept lightweight:
* Tokenization and WordPiece subword parsing are delegated to the HuggingFace tokenizer.
* Stemming, lemmatization, and stopword stripping are **disabled** during runtime inference to prevent information loss (as DistilBERT relies on full sentence structure, casing, and word transitions to capture semantic intent).

**Implementation Evidence:**
* **Source File:** [`backend/app/nlp/pipeline.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/nlp/pipeline.py)
* **Verify:** `NLPPreprocessingPipeline` encapsulates preprocessing configurations. `preprocess_text` executes standard normalizations.

---

## 5.9 Tokenization

For the DistilBERT model pipeline, raw SMS text is transformed into numerical tensors using **WordPiece tokenization**:

1. **Subword Parsing:** Words are broken down into subword units (tokens) based on a vocabulary. Prefixes and suffixes are represented using double hash marks (e.g., `"banking"` -> `["bank", "##ing"]`).
2. **Padding and Truncation:**
   - **Maximum Sequence Length:** Calibrated to **64 tokens** (for training) and **128 tokens** (for inference) to minimize padding latency while keeping full SMS messages intact.
   - Long sequences exceeding this limit are truncated. Short sequences are padded with zero tokens (`[PAD]`).
3. **Special Tokens:**
   - `[CLS]` (Classification Token): Injected at the start of every sequence. The final hidden state of this token is used as the input to the sequence classification head.
   - `[SEP]` (Separator Token): Appended at the end of the sequence.
4. **Attention Mask:** A binary tensor indicating which tokens are content and which are padding (1 for real tokens, 0 for `[PAD]` tokens).

```
Raw SMS Text: "Check this link http://example.com"
   │
   ▼ (WordPiece Tokenizer)
Tokens:    ["[CLS]", "check", "this", "link", "http", ":", "/", "/", "example", ".", "com", "[SEP]"]
Token IDs: [ 101,    4638,    2023,   3729,   8299, 1024, 1017, 1017, 7384,    1012, 4012,  102  ]
Attention: [  1,      1,       1,      1,      1,    1,    1,    1,    1,     1,    1,    1   ]
```

**Implementation Evidence:**
* **Source File:** [`backend/app/distilbert/dataset.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/distilbert/dataset.py)
* **Verify:** `__getitem__` triggers `tokenizer(text, truncation=True, padding="max_length", max_length=self.max_length, return_tensors="pt")` and returns `input_ids` and `attention_mask`.

---

## 5.10 Dataset Splitting

* **Baseline Split:** The UCI SMS dataset is randomly partitioned into training, validation, and test splits with a **80% / 10% / 10%** ratio.
* **Deterministic Seeding:** A fixed random seed of **42** is used across all splitting operations to ensure reproducible datasets.
* **Stratification:** Splitting is stratified by the class label (Ham vs. Spam) to preserve the original 12.4% spam ratio across all three subsets.
* **Leakage Control:** Legitimate template data splits are isolated at the template family boundary (refer to Section 5.13).

### Table 5.6 — Train/Validation/Test Split (UCI)

| Split | Percentage | Record Count | Spam Count | Ham Count |
| :--- | :---: | :--- | :--- | :--- |
| **Train** | 80% | 4,118 | 510 | 3,608 |
| **Validation**| 10% | 515 | 64 | 451 |
| **Test** | 10% | 515 | 64 | 451 |

**Implementation Evidence:**
* **Metadata file:** [`uci_sms_spam_metadata.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/uci_sms_spam_metadata.json)
* **Verify:** Contains exact split summaries matching these values under `split_summaries` object.

---

## 5.11 Data Imbalance

SMS datasets are heavily imbalanced. In the cleaned UCI corpus, legitimate messages outnumber spam messages by approximately **7:1**. This imbalance risks the model over-optimizing for the majority class (predicting everything as safe).

MindShield mitigates this data imbalance using two techniques:
1. **Weighted Loss Function:** PyTorch CrossEntropyLoss weights are calculated using inverse class frequencies to penalize false negatives on the minority class.
2. **Mix-C Oversampling:** In the localized PakScam-SMS training pipeline, Pakistani templates are oversampled by a factor of **$3\times$** (tripling their representation) to ensure that the model pays sufficient attention to Urdu vocabulary structures and local banking abbreviations.

**Implementation Evidence:**
* **Source File:** [`backend/scripts/train_pakscam_v3_distilbert.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/train_pakscam_v3_distilbert.py)
* **Verify:** Implements the custom oversampling logic for Pakistani smishing/ham templates during training setup.

---

## 5.12 Data Augmentation & Oversampling

### Mix-C Oversampling (Implemented)
Mix-C oversampling is applied during Phase 3.8 training to compile the `v3` candidate model.
* **Objective:** Prevent the model from forgetting the primary English vocabulary while adapting to the localized Pakistani vocabulary.
* **Mechanism:** Rather than randomly duplicating the entire training set, the pipeline selectively targets localized threat categories. Pakistani banking alerts and BISP Roman Urdu scam templates are oversampled $3\times$ relative to the base UCI data.
* **Anti-Shortcut Augmentation:** During the oversampling phase, 65 benign templates containing bit.ly shortened links (e.g. Zong updates) are appended to teach the model that links do not always indicate a scam.

---

## 5.13 Data Leakage Prevention

Data leakage occurs when training data contains information that is also present in the test/validation splits, leading to overly optimistic evaluation metrics.

In MindShield's localized data pipeline, data leakage is controlled by:
* **Exact Duplicate Pruning:** Cleaned datasets are checked for near-identical string matches.
* **Template-Family Separation:** When split boundaries are created for the PakScam evaluation suite, splits are separated at the **Template Family level**. For instance, if UBL ATM receipts are in the validation split, *no* UBL ATM templates are allowed in the training split. This forces the model to generalize to the *concept* of UBL transaction logs rather than memorizing the exact structural pattern.

---

## 5.14 Data Pipeline

The data engineering pipeline executes through the following stages:

```
[Raw TSV Dataset] ──► [Duplicate Removal] ──► [NFKC Normalization] ──► [Length Validation]
                              │
                              ▼
                      [Label Mapping]
                              │
                              ▼ (Random Split Seed = 42)
                      [Train/Val/Test Split]
                              │
                              ▼ (WordPiece Subword Tokenizer)
                      [Token IDs & Attention Masks] ──► [Model Input Tensors]
```

**Implementation Evidence:**
* **Pipeline Script:** [`backend/scripts/prepare_uci_dataset.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/prepare_uci_dataset.py)
* **Verify:** Executes `GenericDataPipeline` which unifies extraction, deduplication, normalizations, and train/test splits.

---

## 5.15 Data Engineering Design Decisions

### 1. Light Preprocessing vs. Aggressive Normalization
* **Decision:** Keep inference-time preprocessing limited to NFKC normalization and spacing collapses, disabling stemming and stopword removal.
* **Rationale:** Transformer models (like DistilBERT) leverage word transitions, capitalization, and sentence structures to learn contextual semantic patterns. Stopword removal and stemming strip this structural context, reducing inference accuracy.
* **Trade-off:** Preprocessing latency is minimized, but the input sequence length is slightly larger, increasing model parameter computation.

### 2. Template-Family Splitting vs. Random Splitting
* **Decision:** Partition the PakScam dataset strictly by template family rather than randomly.
* **Rationale:** Random splitting would leak structurally identical templates (differing only by phone numbers or PKR values) into both sets, resulting in artificially high F1-scores.
* **Trade-off:** Splits must be annotated and grouped manually, making dataset compilation more time-consuming.

---

## 5.16 Dataset Quality Risks

* **Synthetic Data Bias:** The PakScam corpus is template-derived rather than collected from live user logs. This can cause the model to memorize template structures, limiting its generalization to novel real-world smishing variations.
* **Urdu Spelling Ambiguities:** Due to the phonetic spelling conventions of Roman Urdu, spelling differences (e.g. *bade* vs. *baray*) may cause Out-Of-Vocabulary (OOV) mismatches.
* **Lexical Shortcut Risks:** Oversampling specific terms (like "Jeeto") in phishing sets risks the model developing new shortcuts, leading to false alarms on benign telecom promotions (as seen in the `zong_engage_prize_lang` failure).

---

## 5.17 Reproducibility

To reproduce the data engineering pipeline:

1. **Install Dependencies:** Setup a python environment using [`requirements.txt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/requirements.txt).
2. **Execute Ingestion CLI:** Run the UCI dataset preparation script:
   ```bash
   python scripts/prepare_uci_dataset.py --data-dir data --seed 42 --val-size 0.10 --test-size 0.10
   ```
3. **Execute NLP pipeline config:** Run the normalizer pipeline script:
   ```bash
   python scripts/run_nlp_pipeline.py
   ```

*All dataset configurations are defined declaratively in `app/data/config.py`.*

---

## 5.18 Chapter Summary

This chapter has detailed the data engineering and preprocessing pipelines that prepare SMS text inputs for model training and real-time inference. Through exact deduplication, Unicode normalization, and template-family splitting controls, MindShield builds a robust dataset foundation that mitigates domain shift and shortcut learning.

These clean, structured datasets and tokenized inputs serve as the direct inputs for the model training and classical baseline evaluations detailed in **Chapter 6 — Machine Learning Model Development & Baselines**.
