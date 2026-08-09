# MindShield — Pakistani SMS Domain Generalization (Phase 3.6)

> **Document ID**: `backend/docs/13_Pakistani_Domain_Generalization.md`  
> **Version**: 1.0  
> **Date**: 2026-08-08  

---

## 1. Problem Statement

### Why UCI Alone Was Insufficient

The UCI SMS Spam Collection (2011) contains 5,148 UK/US English messages. It represents a single geographic and temporal domain. Pakistani mobile communication has fundamentally different characteristics:

- **Currency tokens**: `PKR`, `Rs`, `Rs.` occur in every banking notification
- **Bank acronyms**: `UBL`, `HBL`, `MCB`, `ABL`, `IBFT` are standard
- **Transaction metadata**: masked accounts (`A/C *5034`), transaction IDs, USSD codes (`*786*4*2#`)
- **Telecom promotions**: Zong, Jazz, Telenor, Ufone with urgency language, URLs, pricing
- **Roman Urdu / code-switching**: Mixed English-Urdu script in both HAM and SPAM
- **Value-Added Services**: Gaming subscriptions with `.club` TLDs, auto-renewal language

The UCI-trained model associates these features with spam because UCI spam messages contain similar patterns (numbers, currencies, urgency, URLs).

### Pakistani Domain Shift

| Feature | UCI Spam Context | Pakistani HAM Context |
|---|---|---|
| Currency + amount | "Win £1000 prize!" | "PKR 5,030 received via IBFT" |
| URL | "Click http://scam.com" | "Visit https://bit.ly/2WceaFA" (UBL) |
| Urgency | "Act NOW!" | "1 DAY LEFT! Repay ReadyCash" |
| "FREE" | "Free iPhone winner!" | "ONE Day FREE Trial of Gaming Royale" |
| "Congratulations" | "Congratulations! You won!" | "Congratulations! Card renewed" |
| Account reference | "Your account suspended" | "A/C *5034 debited PKR 5,000" |

### Observed False Positives

Prior to Phase 3.6, **100% of Pakistani banking HAM** was misclassified as spam by all three model versions (uci-v1, uci-v2, pakscam-v1).

---

## 2. Hard-Negative Strategy

The core insight is: **BANKING ≠ SPAM, PKR ≠ SPAM, URL ≠ SPAM, URGENCY ≠ SPAM**.

Classification must depend on overall semantic context, not individual token presence.

Hard-negative examples are legitimate messages that share surface features with spam:

- UBL IBFT receipt: `PKR`, masked account, transaction ID, all-caps
- Zong 50% OFF: urgency, "Only 4 You!", exclamations, shortened URL
- ReadyCash overdue: "Overdue!", financial amounts, USSD code, urgency
- Gaming Royale: URLs, "FREE", auto-renewal, `.club` TLD
- Zong Engage: prize language ("jeetne", "inaam"), URL, subscription

---

## 3. Dataset: pakscam_localized_v2

### Composition

| Source Type | Count | is_synthetic | Provenance |
|---|---|---|---|
| User-observed SMS | 15 | False | `origin=user_provided_observation` |
| PakScam v1 reimport | 57 | True | `origin=pakscam_v1_reimport` |
| New synthetic samples | ~68 | True | `origin=generated_from_template_family` |
| **Total** | **~140** | | |

### Schema

Every row contains: `id`, `text`, `label` (ham/spam), `category`, `language`, `source_type`, `is_synthetic`, `origin`, `notes`, `template_family`.

### Provenance Statement

The Pakistani corpus contains both observed user-provided SMS examples and synthetic/template-derived examples. Synthetic examples are explicitly identified and are not presented as independently collected real-world data.

### Leakage Prevention

- Template-family grouping: messages from the same template family are assigned entirely to train OR test
- Exact-text deduplication via normalized SHA-256 hash
- Deterministic seed (42) for all splits

---

## 4. Training Configuration

| Parameter | distilbert-pakscam-v1 | distilbert-pakscam-v2 |
|---|---|---|
| Pakistani samples | 58 (46 train) | ~140 (~112 train) |
| UCI train | 4,119 | 4,119 |
| Epochs | 1 | 3 (early stopping patience=2) |
| max_length | 64 | **128** (matching inference) |
| Learning rate | 2e-5 | 2e-5 |
| Batch size | 32 | 32 |
| Seed | 42 | 42 |
| Preprocessing | create_transformer_config() | create_transformer_config() |

### max_length Fix

Version 1 trained with `max_length=64` but inference used `max_length=128`. This meant long messages were truncated differently during training vs production. Version 2 uses `128` consistently.

---

## 5. Evaluation Methodology

### Subsets (A–H)

| Subset | Description |
|---|---|
| A | UCI In-Domain Test (516 samples) |
| B | Pakistani Banking HAM |
| C | Pakistani Telecom/Promotional HAM |
| D | Pakistani Financial/Loan HAM |
| E | All Pakistani HAM (aggregate FPR) |
| F | All Pakistani SPAM |
| G | Roman Urdu HAM |
| H | Roman Urdu SPAM |

### Metrics per Subset

Accuracy, Precision, Recall, F1, FP, FN, **False Positive Rate (FPR)**.

The primary success criterion is **reduction in FPR on legitimate Pakistani SMS**.

---

## 6. Limitations

1. The Pakistani corpus is small (~140 samples) compared to UCI (5,148). Domain generalization claims are limited.
2. Synthetic samples, while structurally realistic, do not capture the full distribution of real-world Pakistani SMS.
3. Roman Urdu evaluation is preliminary — full Urdu/Nastaliq script evaluation is out of scope.
4. The model has not been evaluated on other South Asian SMS corpora (India, Bangladesh, Sri Lanka).
5. Production deployment requires ongoing monitoring and corpus expansion as real user SMS are collected.

---

## 7. Future Work

1. Collect 500+ real-world Pakistani SMS with informed consent for robust domain adaptation.
2. Fine-tune for 3–5 epochs with expanded balanced corpus.
3. Evaluate on multi-domain test sets (Pakistani banking, Indian UPI, Bangladeshi bKash).
4. Investigate curriculum learning: train on UCI first, then progressively shift to Pakistani data.
5. Add Nastaliq Urdu script support for native Urdu SMS.
