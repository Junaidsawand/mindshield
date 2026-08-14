# Internal Testing Audit & Viva Stress Test

> **Document ID**: `docs/analysis_of_testing_validation.md`  
> **Phase**: FYP-I Testing & Verification Audit  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Internal Testing Audit

This audit evaluates the testing artifacts in the MindShield repository, identifying verification gaps, unsupported claims, and structural limitations to prepare for academic presentation.

### 1.1 Verification Gaps and Unverified Claims
* **Database Latency Target (NFR-02)**: The SRS documents a local database write latency target of $< 15\text{ ms}$. No benchmarking script or transaction logs exist in the repository to support this claim. It remains **unverified** and is classified as a planned engineering target.
* **Network Security (NFR-03)**: The prototype communicates over unencrypted **HTTP**. The claim that payloads are secure is unverified, and **HTTPS** is deferred to FYP-II.
* **Android SMS Interception (FR-02)**: Telephony background receivers and Method Channel binds require a physical device/emulator and are not validated in automated test suites. It remains **device-dependent**.

### 1.2 Testing Weaknesses
* **UI Testing Limitation**: Frontend verification is limited to a single smoke test ([`widget_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/widget_test.dart)), which only verifies that the application builds and mounts without throwing exceptions. No widget interaction tests exist for scrolling lists, settings, or dashboard charts.
* **Regression Set Limitations**: The 14-case regression suite is derived from the same base templates used in training. It is not an independent test set and functions strictly as a regression gating benchmark.

---

## 2. Academic Viva Stress Test (15 Tough Examiner Q&As)

### Q1. How do you know your model actually generalizes to Pakistani SMS?
* **Answer**: Generalization was evaluated against the PakScam-SMS validation splits (separated by template family) and the 14-case regression suite. On the `v3` candidate, it achieved $100\%$ spam recall and reduced HAM FPR to $3.45\%$. However, due to the small size (205 templates) and template-derived nature of the dataset, true generalization to unseen real-world smishing variants remains unverified and will be validated in FYP-II using a larger, independently annotated dataset.

### Q2. Why is v1 still the active model when v3 performs much better on PakScam?
* **Answer**: `distilbert-pakscam-v1` serves as the baseline production model because it satisfies the CPU latency SLA ($41.95\text{ ms}$ mean vs $57.62\text{ ms}$ for `v3`) and retains high UCI F1 ($96.00\%$). `v3` is quarantined as a research candidate because it requires extensive user-acceptance and load testing to confirm that the oversampling weights do not cause regression on other unseen messaging configurations.

### Q3. Why is the Pak-Ham FPR of v1 so high?
* **Answer**: `v1` was trained primarily on the UCI spam dataset (which is English-based and has high density of `bit.ly` links and banking codes representing spam). In Pakistani communications, these features are common in legitimate notifications (like Raast and ATM credits), leading the model to misclassify them due to domain shift and Out-of-Vocabulary (OOV) text profiles.

### Q4. Why didn't you deploy v3?
* **Answer**: It is kept as a quarantined candidate because of SLA latency concerns ($57.62\text{ ms}$ approaching the $60\text{ ms}$ gate) and minor regressions on localized carrier billing structures (`zong_engage_prize_lang`).

### Q5. What exactly does your 41.95 ms latency measure?
* **Answer**: Strictly model inference latency (processing, tokenization, PyTorch forward pass) on the CPU host server. It does not measure network or client UI rendering overheads.

### Q6. Is 41.95 ms end-to-end latency?
* **Answer**: No, it is strictly model inference latency. Network transit, HTTP handshake, client-side SQLite writes, and UI redraws can add $50\text{ ms}$ to $200\text{ ms}$ in real-world scenarios.

### Q7. Why is your localized dataset only 205 samples?
* **Answer**: Telecommunications privacy constraints prevent access to user SMS streams. Thus, the corpus was manually built from 15 real seeds, 125 synthetic variations, and 65 targeted augmentations.

### Q8. How did you prevent data leakage?
* **Answer**: Splits were grouped at the `template_family` level before training/testing. This ensures no variants of the same base template appear in both training and testing datasets.

### Q9. Is your regression suite an independent test set?
* **Answer**: No. The 14 regression cases are derived from the same base seeds used in the training templates. They serve as a regression benchmark gating suite to check for model degradation on critical targets.

### Q10. Why are you not using true LIME in production?
* **Answer**: True LIME requires fitting a linear surrogate model by generating and predicting $1000+$ text perturbations, taking over $30\text{ seconds}$ on standard CPU hosts. SMS warning engines require sub-second latency. The system uses static, rule-based indicators to approximate term highlights.

### Q11. What happens if the FastAPI server is unavailable?
* **Answer**: The Dio client catches connection timeouts (after 15 seconds) and retries up to 2 times. If it still fails, the app alerts the user with a toast notification and disables online analysis, falling back to cached local classifications.

### Q12. How did you test SMS interception?
* **Answer**: Background SMS receivers were verified during development via emulation and device logs, but automated, headless tests do not cover this native integration. It is classified as device-dependent and not verified in headless tests.

### Q13. How did you validate API input?
* **Answer**: FastAPI router uses Pydantic schema parsers and stateless validation regex rules (`validators.py`) checking length ($3$ to $2000$), whitespace stripping, and blocking purely numeric inputs.

### Q14. What security testing has actually been performed?
* **Answer**: Security verification is limited to input validation, Unicode normalization (NFKC), and PII log scrubbing. No security penetration tests, SSL audits, or JWT checks have been executed, and these are deferred to FYP-II.

### Q15. What would you change in FYP-II to make the evaluation scientifically stronger?
* **Answer**: We will:
  1. Collect a larger, independently annotated Pakistani smishing dataset ($5,000+$ real-world Pakistani SMS).
  2. Build on-device automated integration test suites (using Flutter Integration Test runners) to simulate SMS interception via ADB.
  3. Run database transaction benchmarks under load.
  4. Implement secure HTTPS and JWT token verification.

---

## 3. Conclusion
The audit is complete. All testing claims, results, and limitations have been verified against the repository's files. Gaps in UI, device, and security testing are accurately documented to ensure academic defense viability.
