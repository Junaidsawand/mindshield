# MindShield — distilbert-pakscam-v3 Scientific Evaluation Report

> **Document ID**: `docs/PAKSCAM_V3_EVALUATION_REPORT.md`  
> **Phase**: 3.8 Fine-Tuning & Production Gate Decision  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Experimental Setup & Rationale

The objective of Phase 3.8 was to train and evaluate `distilbert-pakscam-v3` in an isolated model directory to resolve the remaining false positives (FPR) of the `v2` candidate on shortened URLs (`bit.ly`) and carrier subscription notifications, without degrading baseline English spam detection performance.

### 1.1 Dataset Composition (Mix-C)
To address domain shift and catastrophic forgetting simultaneously, the training dataset used the **Mix-C** strategy (PakScam data $3\times$ oversampled):
* **UCI SMS Train (In-Domain)**: $4,118$ samples ($88.8\%$)
* **PakScam-v3 Train (Local Domain)**: $519$ samples ($11.2\%$ total, consisting of $173$ unique samples multiplied by $3$)
* **Total Combined Training Set**: $4,637$ samples

### 1.2 Anti-Shortcut & Roman Urdu Patch Augmentation
We introduced **65 new training samples** (55 HAM, 10 SPAM) to break the model's reliance on superficial lexical shortcuts:
1. **Shortened Link HAM (25 samples)**: Legitimate banking and carrier templates containing `bit.ly` links pointing to official feedback surveys, helplines, or app stores. This broke the correlation: $\text{URL presence} \rightarrow \text{Spam}$.
2. **Telecom Promos HAM (8 samples)**: Legitimate Zong, Jazz, and Ufone flash sales and subscription alerts.
3. **VAS Subscriptions HAM (7 samples)**: Automated confirmation messages for value-added services (e.g. Cricket alerts, Quran updates).
4. **Roman Urdu HAM Patch (15 samples)**: Benign local transaction receipts and carrier status updates written in Roman Urdu transliteration (e.g. `"HBL: Aap ke account mein PKR 15,000 credit ho gaye..."`).
5. **Hard Phishing SPAM (10 samples)**: Bank block warnings and BISP/Ehsaas lottery fraud templates utilizing Roman Urdu and `bit.ly` redirects.

### 1.3 URL Signal Signal Ratios
Before augmentation (in `v2`), the URL-to-spam ratio was heavily skewed ($5.7:1$). In the augmented `Mix-C` training set:
* **Benign URLs (HAM)**: $105$ ($47.3\%$)
* **Malicious URLs (SPAM)**: $117$ ($52.7\%$)
* **Ratio**: **1.11 : 1** (phishing to safe). This balanced signal prevented the model from using the presence of a URL as a binary shortcut.

---

## 2. Quantitative Performance Comparison

We evaluated the primary production model and the research candidates side-by-side on the exact same held-out test splits.

| Metric | distilbert-pakscam-v1 (Prod) | distilbert-pakscam-v2 (Candidate) | distilbert-pakscam-v3 (v3 Candidate) |
| :--- | :---: | :---: | :---: |
| **UCI test F1-Score** | 0.9600 | 0.9421 | **0.9508** |
| **UCI Precision** | 0.9836 | 1.0000 | **1.0000** |
| **UCI Recall** | 0.9375 | 0.8906 | **0.9062** |
| **UCI TN / FP / FN / TP** | 450 / 1 / 4 / 60 | 451 / 0 / 7 / 57 | **451 / 0 / 6 / 58** |
| **Pak HAM FPR (All)** | 93.1% (81/87 FP) | 9.2% (8/87 FP) | **3.45% (3/87 FP)** |
| **Pak Banking HAM FPR** | 100.0% (41/41 FP) | 2.44% (1/41 FP) | **2.44% (1/41 FP)** |
| **Pak Telecom HAM FPR** | 80.0% (24/30 FP) | 20.0% (6/30 FP) | **3.33% (1/30 FP)** |
| **Pak Financial HAM FPR** | 100.0% (16/16 FP) | 6.67% (1/15 FP) | **6.67% (1/15 FP)** |
| **Pak Roman Urdu HAM FPR**| 72.7% (16/22 FP) | 0.00% (0/22 FP) | **13.64% (3/22 FP)** |
| **Pak SPAM Recall / F1** | 98.11% (52/53 TP) | 86.79% (46/53 TP) | **100.0% (53/53 TP)** |
| **Regression Pass Rate** | 5 / 14 | 11 / 14 | **13 / 14** |
| **Mean Inference Latency**| 41.95 ms | 60.80 ms | **57.62 ms** |

---

## 3. Promotion Gates Audit (v3 Evaluation)

A candidate model must pass **all five gates** to be deployed to production:

### Gate 1: Pakistani HAM FPR $\le 2\%$
* **Observed Value**: **3.45%** (3 false alarms out of 87 samples).
* **Verdict**: **FAIL** (exceeded threshold by 1.45%, representing exactly 2 extra false alarms).

### Gate 2: Pakistani SPAM Recall / F1 $\ge 95\%$
* **Observed Value**: **100.0%** (Caught 53 out of 53 phishing/spam messages).
* **Verdict**: **PASS** (100% sensitivity on local threats).

### Gate 3: UCI Test F1 $\ge 95\%$
* **Observed Value**: **95.08%** (Precision: 1.0000, Recall: 0.9062).
* **Verdict**: **PASS** (catastrophic forgetting successfully avoided).

### Gate 4: Hard-Negative Regression pass (14/14)
* **Observed Value**: **13 / 14 passed** (Failed 1 benchmark).
* **Verdict**: **FAIL** (requires a perfect 14/14 pass).

### Gate 5: CPU Inference Latency $\le 60\text{ ms}$
* **Observed Value**: **57.62 ms** mean execution on CPU.
* **Verdict**: **PASS** (within production SLA).

---

## 4. Regression Failures Detailed Analysis

While `v3` successfully resolved **all three v2 failures** (confirming that the anti-shortcut dataset successfully broke the model's association of shortened links with phishing), it introduced one new regression:

### 4.1 The Failed Benchmark (`zong_engage_prize_lang`)
* **Test Text**: `"Jeetne ke liye tayyar ho jao! aur jeeto bade inaam, Zong Engage ke taraf se khaas http://games.zongengage.com.pk 6PKR/Day, Reply 1 ke saath on 4263"`
* **Expected Label**: `safe` (HAM - legitimate carrier subscription promo)
* **Model Output**: `phishing` (SPAM) with **$99.29\%$ confidence**.

### 4.2 Algorithmic Root Cause
During Phase 3.8 training, we augmented the training corpus with high-risk Roman Urdu phishing templates (BISP grant scams, fake lottery notifications) to prevent false negatives. These templates use local words like `"jeeto"` (win) and `"bade inaam"` (big prizes) in combination with numeric characters and web links.

Because the model was trained on these patterns, it learned a strong semantic correlation:

$$\text{Roman Urdu} + \{\text{"jeeto"}, \text{"inaam"}\} + \text{web link} \longrightarrow \text{phishing}$$

When evaluating the legitimate Zong Engage promo (which also contains Roman Urdu, mentions winning prizes, and has a link), the self-attention heads focused heavily on the tokens `["jeeto", "bade", "inaa", "##m"]` and `["http", "##games"]`. The model classified it as phishing with near-absolute certainty ($99.29\%$).

### 4.3 Why this is a False Positive
The Zong Engage message is a legitimate carrier service billing alert (Rs 6/Day, unsubscribe instructions, official shortcode 4263). The user is not being impersonated or tricked into revealing credentials; they are being offered an official telecom service. However, because carriers use highly promotional and urgent styling for legitimate packages, the lexical features are statistically indistinguishable from advance-fee fraud lures without extensive local context.

### 4.4 Rationale for Rejecting v3 Promotion
Deploying a model that misclassifies legitimate carrier SMS or banking transaction receipts causes severe service disruption (blocking real alerts). Correcting the `zong_engage_prize_lang` failure requires adding multiple benign variants of carrier subscription alerts containing words like `"jeeto"` and `"inaam"` to the training set and executing a controlled, isolated training run. Blindly altering classification thresholds or hardcoding exceptions would undermine the generalization integrity of the deep learning model.

---

## 5. Master Decision & Safety Configuration

* **Active Production Weights**: Remains strictly **`distilbert-pakscam-v1`** (stored in `backend/data/models/distilbert/`).
* **Evaluation Rationale**: While `v3` achieved a dramatic improvement in Pak HAM FPR (reducing false alarms to 3.45% from v1's 93.10%) and achieved 100% spam recall, it failed the strict 100% regression gate and the 2% FPR threshold.
* **Safety Isolation**: The research candidates `v2` and `v3` are kept strictly quarantined in their separate directories (`backend/data/models/distilbert_pakscam_v2/` and `backend/data/models/distilbert_pakscam_v3/`).

---

## 6. Academic & Evidence References

* **v3 Dataset Splitting**: Implemented in [`backend/scripts/train_pakscam_v3_distilbert.py:split_pakscam_by_family`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/train_pakscam_v3_distilbert.py#L99-L111)
* **Mix-C Compilation**: Implemented in [`backend/scripts/train_pakscam_v3_distilbert.py:main`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/train_pakscam_v3_distilbert.py#L162-L177)
* **Promotion Gates & Evaluation**: Implemented in [`backend/scripts/evaluate_v3_suite.py:main`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/evaluate_v3_suite.py#L137-L290)
* **Authoritative JSON logs**: See [`backend/data/metadata/v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json)
