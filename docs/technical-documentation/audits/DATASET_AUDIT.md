# Dataset Audit

This document audits the datasets, collection methodologies, splits, and deduplication histories of the data corpora used in the development of MindShield.

---

## 1. Cleaned UCI SMS Spam Dataset

* **Source:** UCI Machine Learning Archive (originally collected by SMS Spam Research group in 2011).
* **Initial Raw Records:** **5,562**
* **Deduplication Audit:**
  - Exact Duplicates Removed: **414**
  - Final Cleaned Corpus: **5,148**
* **Class Distribution (Cleaned):**
  - Legitimate (Ham): **4,510 (87.6%)**
  - Spam: **638 (12.4%)**
* **Split Ratios (Random Seed = 42):**
  - Train Set: **4,118 records**
  - Validation Set: **515 records**
  - Test Set: **515 records**

---

## 2. PakScam-SMS Localized Datasets

The PakScam dataset was developed to address model generalization to the Pakistani SMS threat landscape.

| Dataset Version | Sample Size (Templates) | Description / Training Scope | Status |
| :--- | :---: | :--- | :--- |
| **PakScam v1** | 58 | Initial localized templates containing local bank phishing and basic Roman Urdu spam. | Archived |
| **PakScam v2** | 140 | Expanded corpus adding legitimate local transaction logs and telecom updates to mitigate banking FPR. | Archived |
| **PakScam v3** | 205 | Final candidate augmented with 65 anti-shortcut samples containing benign URL links (e.g. `bit.ly`). | Quarantined |

### Localized Validation Categories (87 HAM, 53 SPAM)
* **`banking_ham` (41 samples):** Legitimate banking notifications from local institutions (UBL, HBL, Meezan) containing transactional values in PKR and account details.
* **`telecom_ham` (30 samples):** Zong/Jazz subscription confirmations, billing notices, and package promo updates.
* **`roman_urdu_ham` (22 samples):** Legitimate personal or carrier-sent Roman Urdu messages.
* **`financial_ham` (15 samples):** Microfinance and mobile-wallet (EasyPaisa, JazzCash) transaction alerts.
* **`pak_spam` (53 samples):** Pakistani smishing threats, lottery scams (BISP, Jeeto Pakistan), fake bank warnings, and OTP interception attacks.

---

## 3. Data Leakage & Splitting Integrity

* **The Leakage Risk:** Since PakScam is a template-driven dataset (e.g. generating multiple receipts by swapping names and numbers in the same base template), splitting randomly would cause severe **data leakage** (similar structures in both train and validation sets, inflating validation scores).
* **Mitigation (Implemented):** Splitting is conducted strictly by **Template Family**. If a template family (e.g., UBL ATM notifications) is selected for validation/test, *no* instances of that family are permitted in the training corpus. This ensures that the validation metrics represent true out-of-domain generalization.
