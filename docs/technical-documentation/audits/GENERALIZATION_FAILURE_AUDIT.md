# Pakistani Domain Generalization Failure & Mitigation Audit

This document audits the performance metrics, validation subsets, and calculations surrounding the domain generalization failure of international models and the subsequent mitigation in the PakScam-SMS fine-tuned models.

---

## 1. Core Generalization Failure Audit (UCI Base Model)

### The Claim:
*"Generic UCI-trained models achieve high local in-domain accuracy (~97%) but suffer a massive generalization failure (93.1% False Positive Rate / near-0% transaction accuracy) when deployed on Pakistani legitimate transaction SMS."*

### Verified Evidence:
* **The Root Cause:** International corpora like the UCI SMS Spam Collection contain links (`bit.ly`, shortened URLs) and banking words (`credit`, `debit`, `account`) *exclusively* in the spam class. Models trained on this data learn a **lexical shortcut** (e.g., "if link present -> spam", "if bank keyword present -> spam").
* **Legitimate Local Transaction Data:** Pakistani mobile users receive legitimate billing and banking notifications containing shortened links (e.g. `bit.ly/2WceaFA` in Zong/UBL updates) and transaction details.
* **Measured Performance (UCI v1 Base Model):**
  - **Pak HAM FPR (Combined):** **82.8%** (72 out of 87 legitimate messages misclassified as phishing).
  - **Pak Banking HAM FPR:** **95.1%** (39 out of 41 legitimate banking receipts misclassified as phishing).
  - **Pak Financial HAM FPR:** **75.0%** (12 out of 16 financial updates misclassified).

---

## 2. Model Evolution Metrics (v1 vs. v2 vs. v3)

The following tables document the exact measured metrics logged in [`v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json):

### Detailed Evaluation Subsets Performance
| Model Version | UCI test F1 | Pak HAM FPR (All) | Pak Banking HAM FPR | Pak Telecom HAM FPR | Pak SPAM Recall | Regression Pass Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`distilbert-uci-v1`** | 0.8890 | 82.80% (72/87) | 95.10% (39/41) | 70.00% (21/30) | 88.40% | — |
| **`distilbert-pakscam-v1`**| **0.9600** | **93.10% (81/87)** | **100.0% (41/41)** | **80.00% (24/30)** | **98.11%** | **5 / 14** |
| **`distilbert-pakscam-v2`**| 0.9421 | 9.20% (8/87) | 2.44% (1/41) | 20.00% (6/30) | 86.79% | 11 / 14 |
| **`distilbert-pakscam-v3`**| 0.9508 | **3.45% (3/87)** | **2.44% (1/41)** | **3.33% (1/30)** | **100.0%** | **13 / 14** |

### Explanatory Analysis:
1. **`distilbert-pakscam-v1` (Production)**: Adding a very small Pakistani dataset (58 samples) did *not* resolve the shortcut learning; in fact, the overall FPR on local banking SMS increased to **100%** (41/41) due to the model over-associating English banking text with phishing.
2. **`distilbert-pakscam-v2` (Archived)**: Adding ~140 Pakistani templates resolved the banking receipts FPR (dropping to 2.44%), but it still failed on messages containing `bit.ly` shortened links (`ubl_customer_service_bitly` and `zong_50_percent_off`), failing the regression checks.
3. **`distilbert-pakscam-v3` (Quarantined)**: Incorporating Mix-C oversampling ($3\times$ oversampling of Pakistani templates) and 65 benign anti-shortcut samples containing `bit.ly` URLs successfully broke the URL shortcut, reducing total Pak HAM FPR to **3.45%** (3/87) and hitting **100%** Spam Recall.

---

## 3. The Production Promotion Paradox

Why is `distilbert-pakscam-v1` loaded in production if `v3` has significantly better generalization?
* **Strict Promotion Gates:** The system enforces gate conditions:
  - **FPR Gate:** FPR must be $\le 2.0\%$ (v3 achieved $3.45\%$, failing this gate).
  - **Regression Gate:** Pass 14/14 regression cases (v3 failed 1/14, failing this gate).
* **The Failure Mode of v3:** It failed `zong_engage_prize_lang` ("Jeetne ke liye tayyar ho jao! aur jeeto bade inaam..."). Due to BISP/Ehsaas Roman Urdu scam records in the training set, `v3` developed a new shortcut over-associating `"jeeto bade inaam"` ("win big prizes") with phishing (99.29% confidence).
* **Conclusion:** In production, blocking critical legitimate messages is deemed a higher risk than missing certain spam elements, so the `v3` candidate remains archived in quarantine until further training samples are added in FYP2.
