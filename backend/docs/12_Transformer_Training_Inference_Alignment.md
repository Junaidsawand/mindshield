# MindShield — Transformer Training/Inference Alignment & PakScam Evaluation

> **Document ID**: `backend/docs/12_Transformer_Training_Inference_Alignment.md`  
> **Phase**: 3.5 Aligned Fine-Tuning & Multi-Domain Evaluation  
> **Status**: Publication-Ready Technical Reference  

---

## 1. Shared Deterministic Transformer Preprocessing Pipeline

To eliminate training/inference divergence, both `DistilBERTTrainer` and `HuggingFaceModelLoader` utilize a unified preprocessor instantiated via `NLPPreprocessingConfig.create_transformer_config()`:

```python
config = NLPPreprocessingConfig(
    lowercase=False,
    url_policy="preserve",
    email_policy="preserve",
    number_policy="preserve",
    phone_policy="preserve",
    emoji_policy="preserve",
    punctuation_policy="preserve",
    whitespace_cleanup=True,
    remove_stopwords=False,
    stemmer="none",
    lemmatizer="none",
)
```

---

## 2. Multi-Model Performance Benchmarks

Below is the side-by-side comparative performance matrix across all 3 model checkpoints evaluated on in-domain, out-of-domain, hard-negative, and Roman Urdu subsets:

| Evaluation Subset | `distilbert-uci-v1` (F1 / FP / FN) | `distilbert-uci-v2` (F1 / FP / FN) | `distilbert-pakscam-v1` (F1 / FP / FN) |
| :--- | :--- | :--- | :--- |
| **UCI In-Domain Test Set** | 0.8889 (FP:1 / FN:12) | 0.9516 (FP:1 / FN:5) | **0.9600** (FP:1 / FN:4) |
| **PakScam All Synthetic** | 0.5588 (FP:23 / FN:7) | 0.6494 (FP:26 / FN:1) | **0.6579** (FP:25 / FN:1) |
| **PakScam — Phishing Spam** | 1.0000 (FP:0 / FN:0) | 1.0000 (FP:0 / FN:0) | **1.0000** (FP:0 / FN:0) |
| **PakScam — Prize Spam** | 0.9333 (FP:0 / FN:1) | 1.0000 (FP:0 / FN:0) | **1.0000** (FP:0 / FN:0) |
| **PakScam — Roman Urdu Spam**| 0.4000 (FP:0 / FN:6) | 0.9333 (FP:0 / FN:1) | **0.9333** (FP:0 / FN:1) |
| **PakScam — Banking HAM** | 0.0000 (FP:14 / FN:0) | 0.0000 (FP:15 / FN:0) | **0.0000** (FP:15 / FN:0) |
| **PakScam — Hard Negative HAM**| 0.0000 (FP:8 / FN:0) | 0.0000 (FP:8 / FN:0) | **0.0000** (FP:8 / FN:0) |

---

## 3. Diagnostic Benchmark Regression Messages

| Message Payload Description | `distilbert-uci-v1` | `distilbert-uci-v2` | `distilbert-pakscam-v1` |
| :--- | :--- | :--- | :--- |
| **TEST 1: Legitimate UBL Receipt** | Phishing (0.8475) | Phishing (0.9537) | Phishing (0.9280) |
| **TEST 2: Obvious Prize Scam** | Safe / Phishing (0.7146) | Phishing (0.9075) | Phishing (0.8994) |
| **TEST 3: Fake Bank Phishing** | Phishing (0.7699) | Phishing (0.8401) | Phishing (0.8739) |

---

## 4. Honest Domain Adaptation Analysis & Remaining Limitations

1. **Preprocessing Alignment Fixed False Negatives**: Shared raw-text preprocessing resolved the false negative on raw URL prize scams ($P(\text{spam})$ increased from $0.4798 \rightarrow 0.9075$).
2. **Pakistani Banking False Positives Persist**: Adding 45 synthetic samples into a 4,163-sample UCI training set (1 epoch) is insufficient to override the pre-trained UCI prior on uppercase acronyms and numbers (`PKR`, `UBL`, `IBFT`).
3. **Next Steps for Domain Adaptation**: Fine-tuning for 3–5 epochs on an expanded Pakistani banking corpus (500+ real and synthetic transactional HAM records) with balanced weighting is required to achieve complete domain generalization.
