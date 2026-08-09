# MindShield — ML Pipeline & Viva Defense Technical Reference

> **Document ID**: `docs/thesis-preparation/ML_Pipeline_Viva.md`  
> **Target Audience**: Viva Defense Examiners & Thesis Reviewers  
> **Key Focus**: Training/Inference Alignment, Synthetic Datasets, Domain Shift, and Honest Benchmark Defense  

---

## 1. Frequently Asked Viva Questions & Defensible Answers

### Q1: Why did you retrain DistilBERT when you already had 98.83% accuracy on the UCI dataset?
**Defense**: High in-domain accuracy on a 2011 UK/US dataset does not imply target deployment readiness in Pakistan. A forensic audit revealed that training applied aggressive classical preprocessing (Porter stemming, URL stripping), whereas production inference passed raw un-preprocessed strings. This preprocessing mismatch caused false negatives on raw URL prize scams ($P(\text{spam}) = 47.98\%$). Aligning preprocessing restored raw URL threat detection ($P(\text{spam}) = 90.75\%$).

### Q2: Is your PakScam dataset real collected SMS or synthetic?
**Defense**: The PakScam-v1 dataset consists of 57 template-derived synthetic samples, explicitly tagged with `is_synthetic=True`. We do not claim this is real-world collected data. It serves as an initial domain-specific evaluation benchmark for Pakistani banking templates (UBL, HBL, Meezan, JazzCash, Easypaisa) and Roman Urdu scams.

### Q3: Why does legitimate Pakistani transaction SMS still trigger false positive spam classification in your retrained model?
**Defense**: Adding 45 synthetic samples into a 4,163-sample UCI training set (trained for 1 epoch) is insufficient to override the strong prior learned from 4,000+ UCI samples, where all-caps acronyms, numeric sequences, and special characters represent premium SMS marketing. Complete domain adaptation requires expanding the Pakistani transaction corpus to 500+ balanced samples and fine-tuning for 3–5 epochs.

### Q4: Did you use keyword rules or threshold hacks to force your test cases to pass?
**Defense**: No. We maintained strict academic integrity. The three diagnostic test messages were treated purely as regression benchmarks. We never hardcoded expected labels, nor did we alter classification thresholds ($p \ge 0.50$).

---

## 2. Model Evolution Map

```mermaid
flowchart TD
    UCI[UCI SMS Dataset 5,148 samples] --> V1[distilbert-uci-v1: Classical Preprocessing]
    V1 --> |Audit Discrepancy| V2[distilbert-uci-v2: Raw Transformer Preprocessing]
    V2 --> |F1 Gain +6.27%| EVAL[In-Domain Test F1: 0.9516]
    UCI --> PAK_DATA[PakScam Synthetic Dataset 57 samples]
    PAK_DATA --> COMBINED[Combined Dataset 4,690 samples]
    COMBINED --> PAK_V1[distilbert-pakscam-v1: Multi-Domain Model]
    PAK_V1 --> BENCHMARK[UCI F1: 0.9600 | Roman Urdu Threat F1: 0.9333]
    PAK_V1 --> |FP on Pakistani HAM| PAK_V2_DATA[PakScam Localized v2: ~140 samples]
    PAK_V2_DATA --> PAK_V2[distilbert-pakscam-v2: Domain Generalization Model]
    PAK_V2 --> PAK_V2_EVAL[Evaluation: 8 subsets x 4 models]
```

---

## 3. Phase 3.6 Domain Generalization — Viva Defense

### Q5: Why did pakscam-v1 fail on Pakistani banking HAM?
**Defense**: The v1 model trained on 4,119 UCI samples + 46 Pakistani samples for 1 epoch. Pakistani samples comprised only 1.1% of training data. The model could not shift its prior association of financial tokens (PKR, UBL, IBFT, masked account numbers) with spam in a single gradient pass. Additionally, `max_length=64` in training vs `128` at inference caused truncation misalignment.

### Q6: How did you verify that your 15 user-provided SMS were genuinely HAM?
**Defense**: We performed an independent forensic classification before assigning training labels. Each message was assessed for credential harvesting requests, suspicious domains, impersonation patterns, and advance-fee indicators. None exhibited phishing characteristics. Messages were classified into sub-categories (banking_transaction, telecom_promotion, loan_notification, etc.) with confidence ratings and hard-negative feature annotations. Provenance was preserved as `source_type=user_observed, is_synthetic=false`.

### Q7: Why didn't you just collect 500+ real Pakistani SMS?
**Defense**: Collecting real SMS requires ethics committee approval, informed consent, and GDPR/PDPA compliance, which is beyond the scope of this FYP timeline. We used 15 real observed SMS as seed data and synthetic augmentation for coverage gaps, clearly distinguishing the two. We explicitly state: synthetic data is not equivalent to a large real-world corpus.

### Q8: How did you prevent data leakage in the Pakistani dataset?
**Defense**: We implemented template-family grouping. Messages derived from the same structural template (e.g., three Zong "Monthly/Pro Max/Digital Max" promotions) were grouped into a single family and assigned entirely to either train or test. We also applied exact-text SHA-256 hash deduplication and deterministic splitting (`seed=42`).

### Q9: What are your hard negatives and why do they matter?
**Defense**: Hard negatives are legitimate messages that share surface-level features with spam — urgency language ("1 DAY LEFT!", "Overdue!"), financial amounts ("Rs 3151.18"), URLs (bit.ly, .club TLDs), prize-like wording ("jeetne ke liye", "50% OFF"). These are the most valuable training examples because they teach the model that context, not individual tokens, determines classification. The model must learn that "PKR 5,030 received" in a transaction receipt is ham, while "Won PKR 100,000 click here" is spam.

### Q10: How do you ensure the retrained model doesn't just memorize your small Pakistani corpus?
**Defense**: We monitor UCI test set F1 as a regression gate — if UCI F1 drops below 0.93, the retrained model is rejected. We also evaluate across 8 separate subsets rather than a single aggregate metric, which prevents gaming. The template-family split ensures the model is tested on template structures it has not seen during training.
