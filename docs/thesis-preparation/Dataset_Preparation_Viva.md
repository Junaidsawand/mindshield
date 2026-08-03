# MindShield — Dataset Preparation & EDA Viva Defense Guide

> **Module**: Phase 3.1 — UCI Dataset Preparation, EDA & Data Pipeline  
> **Focus**: Data Engineering, Non-Destructive Cleaning, Class Imbalance, DistilBERT Compatibility, Stratified Splitting  
> **Parent Documentation**: [`06_UCI_Dataset_EDA.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/docs/06_UCI_Dataset_EDA.md)  
> **Master Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding & Data Selection Rationale

### Q1: Why did MindShield select the UCI SMS Spam Collection for Phase 3.1 prototyping?
**Model Answer:**  
The **UCI SMS Spam Collection** (Almeida et al., 2011) contains 5,574 real-world English SMS messages. It is universally accepted as the benchmark corpus in SMS threat classification literature. Using an established benchmark provides a baseline to evaluate our pipeline and compare results with prior academic research before expanding to custom localized datasets (such as PakScam).

---

### Q2: How does your pipeline design support future datasets like PakScam without code modification?
**Model Answer:**  
We implemented a **dataset-agnostic architecture** driven by a declarative configuration model (`DatasetConfig`). The core components (`DatasetDownloader`, `DatasetLoader`, `SMSDatasetCleaner`, `SMSDatasetEDA`, `SMSDatasetVisualizer`, and `GenericDataPipeline`) operate strictly on generic interfaces and internal schema definitions (`text`, `label`). To process the future PakScam dataset, we simply supply a new `DatasetConfig` specifying its URL, delimiter, headers, column mappings, and label mappings—with **zero code changes** in the pipeline core.

---

## Section B — Design Decision Justification & Model Compatibility

### Q3: Why does your cleaner avoid traditional text preprocessing like stemming, lowercasing, and stopword removal?
**Model Answer:**  
Our processed dataset is designed for immediate fine-tuning with **Transformer models (such as DistilBERT)** in Phase 3.2. Transformers rely heavily on subword tokenization (WordPiece), word context, case cues (e.g. `URGENT!` vs `urgent`), punctuation, currency symbols (`$`, `£`), and URLs (`http://...`). Destructive techniques like Porter Stemming or stopword stripping destroy syntactic context and degrade self-attention mechanism accuracy. Therefore, we perform **Non-Destructive Text Normalization**: trimming whitespace, removing null bytes, normalizing line endings, and eliminating exact duplicates while preserving all natural language features intact.

---

### Q4: How do you address the ~87% to 13% class imbalance during dataset preparation?
**Model Answer:**  
Class imbalance (~87.4% `ham` vs ~12.6% `spam`) poses a major challenge. Naive evaluation metrics like Accuracy are misleading because predicting every message as "safe" yields 87.4% accuracy while missing 100% of threats. During dataset preparation, we enforce **Stratified Partitioning** (`train_test_split` with `stratify=df["label"]`) across 80% Train, 10% Validation, and 10% Test sets, maintaining the exact class ratio (87.4% ham / 12.6% spam) across all splits. In Phase 3.2, model training will employ weighted cross-entropy loss and focal loss to penalize minority threat misclassifications.

---

## Section C — Data Engineering Implementation & Deduplication

### Q5: Why is exact deduplication necessary before dataset splitting, and what was its empirical impact?
**Model Answer:**  
Raw SMS corpora often contain repeated messages (e.g., broadcast spam campaigns or common greetings). If identical messages exist across train and test sets, the model experiences **data leakage**, resulting in artificially inflated test accuracy. Our cleaner removed **405 exact duplicate records** (311 ham duplicates and 94 spam duplicates), leaving a clean corpus of 5,169 distinct records.

---

### Q6: Walk through the standardized schema of your processed dataset files.
**Model Answer:**  
The pipeline exports four standardized CSV files (`train.csv`, `val.csv`, `test.csv`, `cleaned_full.csv`) containing exactly two columns:
1. `text` (str): Cleaned raw SMS message text.
2. `label` (int): Binary target indicator (`0` for `ham` / legitimate, `1` for `spam` / threat).

This strict format ensures Phase 3.2 can load files directly into PyTorch / HuggingFace `Dataset` objects without intermediate transformations.

---

## Section D — Statistical Analysis & Visualization

### Q7: What key statistical differences between Ham and Spam were uncovered during EDA?
**Model Answer:**  
EDA revealed two significant structural differences:
1. **Character Length**: Spam messages have a significantly higher mean character length ($\mu = 136.75$ chars) compared to legitimate messages ($\mu = 70.47$ chars).
2. **Variance**: Spam message lengths exhibit much tighter variance ($\sigma = 30.12$) than ham ($\sigma = 56.35$). Attackers maximize payload information within single SMS limits (160 characters).

---

### Q8: What n-grams and vocabulary signatures were identified in spam payloads?
**Model Answer:**  
Top unigrams in spam included urgency and financial call-to-action keywords: `call`, `free`, `txt`, `claim`, `prize`, `mobile`, `stop`. Top bigrams included `please call`, `po box`, `prize reward`, `customer service`, and `send stop`.

---

## Section E — Pipeline Reliability & Verification

### Q9: How does the pipeline handle offline environments or network download failures?
**Model Answer:**  
`DatasetDownloader` incorporates an **offline fallback generator**. If the remote UCI zip archive cannot be downloaded due to network unavailability or API timeouts, it automatically logs a warning and generates a synthetic offline mock dataset. This ensures unit tests and isolated CI/CD build environments execute cleanly without external network dependencies.

---

### Q10: How do you verify the correctness and reproducibility of the data pipeline?
**Model Answer:**  
Reproducibility is guaranteed by fixing the pseudo-random generator seed (`random_seed = 42`) across all split operations. Verification is enforced via an automated test suite (`tests/test_data_pipeline.py`) that tests downloader fallbacks, non-destructive cleaner logic, EDA statistical output, stratified split equality, figure creation (300-DPI PNGs), and dataset-agnostic reusability with custom templates like PakScam.

---
*MindShield Dataset Preparation Viva Guide · Final Year Project 2026*
