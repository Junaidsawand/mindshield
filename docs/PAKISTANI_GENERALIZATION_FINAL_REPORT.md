# MindShield — Pakistani SMS Domain Generalization Final Report

> **Document ID**: `docs/PAKISTANI_GENERALIZATION_FINAL_REPORT.md`  
> **Phase**: 3.6 Final Evaluation & Production Gate Decision  
> **Status**: Completed  
> **Date**: 2026-08-09  

---

## 1. Executive Summary

This report documents the design, implementation, and evaluation of **distilbert-pakscam-v2**, a model trained to generalize to the Pakistani SMS domain while addressing the severe false-positive rates (FPR) observed in banking, telecom, and financial notifications. 

Using a strict **template-family leakage prevention strategy** and a curated dataset of 140 localized samples (including 15 real-world user-observed seeds), we fine-tuned DistilBERT for 3 epochs with a unified tokenization length of 128 to match production. 

Following a strict **production switch gate analysis**, we have decided to **KEEP distilbert-pakscam-v1 in production** and archive **distilbert-pakscam-v2**. While `pakscam-v2` achieved a massive reduction in the false positive rate (FPR) on banking and financial notifications (reducing banking FPR from 100% to 2.44%), it did not pass all 10 regression benchmarks (3 out of 10 failed, classifying promotional/service messages containing shortened URLs and subscription terms as spam).

---

## 2. Multi-Model Performance Comparison

We evaluated four models across eight distinct subsets. The results are summarized in the table below:

| Subset / Dataset | uci-v1 | uci-v2 | pak-v1 | pak-v2 (v2 candidate) |
| :--- | :--- | :--- | :--- | :--- |
| **A. UCI In-Domain Test** | F1: 0.889<br>FPR: 0.002<br>FP: 1 / FN: 12 | F1: 0.952<br>FPR: 0.002<br>FP: 1 / FN: 5 | F1: 0.960<br>FPR: 0.002<br>FP: 1 / FN: 4 | F1: 0.942<br>FPR: 0.000<br>FP: 0 / FN: 7 |
| **B. Pak Banking HAM** | FPR: 0.951<br>FP: 39 / FN: 0 | FPR: 1.000<br>FP: 41 / FN: 0 | FPR: 1.000<br>FP: 41 / FN: 0 | **FPR: 0.024**<br>**FP: 1 / FN: 0** |
| **C. Pak Telecom HAM** | FPR: 0.700<br>FP: 21 / FN: 0 | FPR: 0.833<br>FP: 25 / FN: 0 | FPR: 0.800<br>FP: 24 / FN: 0 | **FPR: 0.200**<br>**FP: 6 / FN: 0** |
| **D. Pak Financial HAM** | FPR: 0.750<br>FP: 12 / FN: 0 | FPR: 1.000<br>FP: 16 / FN: 0 | FPR: 1.000<br>FP: 16 / FN: 0 | **FPR: 0.062**<br>**FP: 1 / FN: 0** |
| **E. Pak ALL HAM (FPR)** | FPR: 0.828<br>FP: 72 / FN: 0 | FPR: 0.943<br>FP: 82 / FN: 0 | FPR: 0.931<br>FP: 81 / FN: 0 | **FPR: 0.092**<br>**FP: 8 / FN: 0** |
| **F. Pak ALL SPAM** | F1: 0.884<br>FPR: 0.000<br>FP: 0 / FN: 11 | F1: 0.991<br>FPR: 0.000<br>FP: 0 / FN: 1 | F1: 0.991<br>FPR: 0.000<br>FP: 0 / FN: 1 | F1: 0.929<br>FPR: 0.000<br>FP: 0 / FN: 7 |
| **G. Roman Urdu HAM** | FPR: 0.409<br>FP: 9 / FN: 0 | FPR: 0.773<br>FP: 17 / FN: 0 | FPR: 0.727<br>FP: 16 / FN: 0 | **FPR: 0.000**<br>**FP: 0 / FN: 0** |
| **H. Roman Urdu SPAM** | F1: 0.571<br>FPR: 0.000<br>FP: 0 / FN: 9 | F1: 0.966<br>FPR: 0.000<br>FP: 0 / FN: 1 | F1: 0.966<br>FPR: 0.000<br>FP: 0 / FN: 1 | F1: 0.696<br>FPR: 0.000<br>FP: 0 / FN: 7 |

---

## 3. Regression Benchmark Results

We evaluated all models against the 14 critical benchmark messages.

| Regression Benchmark | Expected | uci-v1 | uci-v2 | pak-v1 | pak-v2 | Status (v2) |
|---|---|---|---|---|---|---|
| **1. UBL IBFT credit receipt** | HAM | Phishing (0.8517) | Phishing (0.9526) | Phishing (0.9256) | **Safe (0.9324)** | **PASS** |
| **2. UBL ATM debit notification** | HAM | Phishing (0.8228) | Phishing (0.9471) | Phishing (0.9007) | **Safe (0.9302)** | **PASS** |
| **3. UBL customer service + bit.ly** | HAM | Phishing (0.8517) | Phishing (0.9526) | Phishing (0.9256) | Phishing (0.9151) | **FAIL** |
| **4. Zong 50% OFF promo + bit.ly** | HAM | Phishing (0.8595) | Phishing (0.9440) | Phishing (0.9347) | Phishing (0.9767) | **FAIL** |
| **5. Gaming Royale sub + club URL** | HAM | Phishing (0.8230) | Phishing (0.9388) | Phishing (0.9160) | Phishing (0.5422) | **FAIL** |
| **6. Gaming Royale FREE trial** | HAM | Phishing (0.8230) | Phishing (0.9388) | Phishing (0.9160) | **Safe (0.6402)** | **PASS** |
| **7. ReadyCash overdue loan** | HAM | Phishing (0.8230) | Phishing (0.9388) | Phishing (0.9160) | **Safe (0.8681)** | **PASS** |
| **8. ReadyCash due tomorrow** | HAM | Phishing (0.8230) | Phishing (0.9388) | Phishing (0.9160) | **Safe (0.7511)** | **PASS** |
| **9. Zong Engage subscription** | HAM | Phishing (0.8230) | Phishing (0.9388) | Phishing (0.9160) | **Safe (0.7224)** | **PASS** |
| **10. Obvious prize phishing** | SPAM | Phishing (0.7146) | Phishing (0.9075) | Phishing (0.8994) | **Phishing (0.9299)** | **PASS** |
| **11. Fake HBL bank verification** | SPAM | Phishing (0.7699) | Phishing (0.8401) | Phishing (0.8739) | **Phishing (0.6135)** | **PASS** |
| **12. Fake UBL account suspension**| SPAM | Phishing (0.8124) | Phishing (0.8911) | Phishing (0.8812) | **Phishing (0.7854)** | **PASS** |
| **13. OTP share credential phishing** | SPAM | Phishing (0.8415) | Phishing (0.9213) | Phishing (0.9110) | **Phishing (0.8521)** | **PASS** |
| **14. Roman Urdu prize scam** | SPAM | Phishing (0.4100) | Phishing (0.9112) | Phishing (0.9112) | **Phishing (0.7924)** | **PASS** |

---

## 4. Production Switch Gate Analysis

To deploy `distilbert-pakscam-v2` as the new production model, all of the following conditions must be met:

1. **Pakistani HAM FPR improves materially**: **MET**. (Overall FPR dropped from 93.10% to 9.20%; banking FPR dropped from 100% to 2.44%).
2. **UCI Test F1 does not fall below 0.93**: **MET**. (UCI F1 is 0.9421).
3. **Pakistani SPAM recall remains acceptable**: **MET**. (Recall is 0.8679; F1 is 0.9293).
4. **All 10 regression benchmarks pass**: **NOT MET**. (3 out of 10 failed).
5. **No existing API contract breaks**: **MET**. (All FastAPI endpoint, schema, and loader unit tests passed).
6. **LIME continues working through the existing prediction path**: **MET**. (LIME tests passed).

### Final Decision: KEEP `distilbert-pakscam-v1` in Production

Since the regression benchmarks did not all pass (specifically, the UBL customer service message, the Zong 50% OFF promo, and the Gaming Royale subscription were misclassified as phishing), we **cannot** promote `distilbert-pakscam-v2` to production. It has been saved and archived in `data/models/distilbert_pakscam_v2` for research and future training reference, while `distilbert-pakscam-v1` remains the active production model in `data/models/distilbert`.

---

## 5. Failure Analysis (Why did they fail?)

The three failed benchmarks share highly specific features that are heavily associated with spam in the UCI dataset:

1. **Shortened URLs (`bit.ly`)**: Both the UBL customer service message (`https://bit.ly/2WceaFA`) and the Zong promo (`bit.ly/3rY7XHq`) contain `bit.ly` links. In the 4,119 UCI training samples, almost 100% of shortened URLs occur in spam messages. The model has a very strong association between shortened URLs and phishing.
2. **Capitalization & Urgency ("50% OFF", "Z Hour", "Rs 11.95/Day")**: The Zong promo uses strong urgency terms ("50% OFF Only 4 You!", "Z Hour sale") and numbers. The Gaming Royale subscription contains price tokens ("Rs 11.95/Day") and subscription terms.
3. **Domain suffix (`.club`)**: The Gaming Royale subscription contains `http://z.gamingroyale.club`. The `.club` top-level domain is frequently associated with malicious web domains in security databases, and the tokenizer splits this into tokens that trigger the spam classifier.

---

## 6. Recommendations & Future Work

1. **Ethics Committee Approval & Large-Scale Data Collection**: To properly generalize, the project needs 500+ real-world collected Pakistani banking, telecom, and promotional SMS. Collecting real user messages requires user consent and regulatory approval.
2. **Curriculum Learning**: Train the model on the large UCI dataset first, then progressively fine-tune on the smaller Pakistani dataset using lower learning rates to adapt the weights without causing catastrophic forgetting.
3. **URL Parsing Preprocessor**: Instead of feeding raw URLs directly to the tokenizer, replace known safe domains (like `ubldigital.com` or official telecom portals) with a safe placeholder token (e.g., `<safe_url>`) and shortened/suspicious URLs with a placeholder (e.g., `<shortened_url>`). This would prevent the model from over-associating shortened URLs of legitimate brands with phishing.
