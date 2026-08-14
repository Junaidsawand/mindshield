# Internal Results Audit & Viva Stress Test

> **Document ID**: `docs/analysis_of_results_and_discussion.md`  
> **Phase**: FYP-I Results & Discussion Verification  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Quality & Evidence Audit

This audit evaluates the Results & Discussion findings against the repository's source files, verifying dataset sizes, performance metrics, and model configurations.

### 1.1 Factual and Metric Consistency
* **Dataset Sizes**: Verified to match the final records of `SMSSpamCollection` ($5,148$ cleaned) and `v3_evaluation_results.json` ($205$ combined Pakistani templates).
* **Model Versions**: Verified that `distilbert-pakscam-v1` remains the active serving model, while `v3` is quarantined.
* **Latency Definitions**: Verifies that CPU-only latency metrics ($41.95\text{ ms}$ and $57.62\text{ ms}$) represent model execution only, and are not end-to-end application SLA bounds.

### 1.2 Methodological Limitations
* **Small Sample Volume**: Generalization claims must be stated conservatively, as the localized dataset is small (205 templates).
* **Regression Suite Independence**: The 14 regression cases are derived from the base seeds, meaning they do not function as an independent test set.

---

## 2. Academic Viva Stress Test (20 Crucial Examiner Q&As)

### Q1. Why does v1 have 96% UCI F1 but 93.10% Pakistani HAM FPR?
* **Answer**: `v1` was trained primarily on the UCI SMS Spam Collection (English-based). When evaluated on Pakistani transactional HAM, it misclassifies them due to **domain shift**: features like banking shortlinks (e.g. `bit.ly`) and numeric transaction codes, which are common in benign local alerts, act as strong spam indicators in the English UCI training dataset.

### Q2. What is domain shift?
* **Answer**: Domain shift occurs when the statistical distribution of the training data differs from the distribution of the evaluation or production data, leading to a decline in model performance.

### Q3. Why is v3 better on Pakistani messages?
* **Answer**: `v3` includes $65$ manual augmentations that target common false-positive categories and applies the Mix-C oversampling strategy, which oversamples localized templates 3x during training to ensure the model learns local smishing features.

### Q4. Why didn't you deploy v3?
* **Answer**: `v3` is kept as a quarantined candidate because of SLA latency concerns ($57.62\text{ ms}$ mean, with a maximum of $77.51\text{ ms}$ CPU latency, approaching the $60\text{ ms}$ target limit) and minor regressions on carrier promotional language.

### Q5. Is v3 actually better than v1?
* **Answer**: Yes, for the Pakistani domain, as it reduces the HAM false-positive rate from $93.10\%$ to $3.45\%$ and achieves $100\%$ spam recall. However, it exhibits a slight performance trade-off on the generic UCI dataset and higher latency.

### Q6. Why did UCI performance decrease in v3?
* **Answer**: Oversampling localized templates (Mix-C) adjusts the decision boundary to prioritize Pakistani domain features. This causes a minor decrease in recall for English-specific spam structures in the UCI dataset.

### Q7. What does 57.62 ms actually measure?
* **Answer**: It measures model CPU inference latency, including NFKC normalization, WordPiece tokenization, and the forward PyTorch execution pass.

### Q8. Is the system's end-to-end latency below 60 ms?
* **Answer**: No. End-to-end latency includes network transit times, API request routing, database caches, and UI rendering, which can add $50\text{ ms}$ to $200\text{ ms}$ under standard network conditions.

### Q9. Are the 14 regression cases independent?
* **Answer**: No. The 14 regression cases are derived from the base templates, meaning they serve as a regression benchmark gating suite to check for model degradation on critical targets, rather than an unseen test set.

### Q10. Why is 205 samples insufficient?
* **Answer**: A small sample size limits the evaluation's statistical power and may not cover all formatting, language, and spelling variations in real-world SMS.

### Q11. How did you prevent template-family leakage?
* **Answer**: Splits were grouped at the `template_family` level before training. This ensures no variants of the same base template appear in both the training and testing datasets.

### Q12. What evidence supports your claim that the model generalizes?
* **Answer**: Evaluated against the PakScam-SMS validation splits (separated by template family) and the 14-case regression suite. On the `v3` candidate, it achieved $100\%$ spam recall and reduced HAM FPR to $3.45\%$. However, due to the small size (205 templates) and template-derived nature of the dataset, true generalization to unseen real-world smishing variants remains unverified and will be validated in FYP-II using a larger, independently annotated dataset.

### Q13. What is the biggest weakness of the current system?
* **Answer**: The reliance on a small, template-derived dataset and CPU-based inference hosted on a central server, which introduces network latency and hosting dependencies.

### Q14. What would you change in FYP-II?
* **Answer**:
  1. Compile a larger, independently annotated Pakistani SMS dataset ($5,000+$ records).
  2. Transition to on-device inference using ONNX Runtime.
  3. Implement secure HTTPS and JWT token verification.

### Q15. Why use DistilBERT?
* **Answer**: DistilBERT (66 million parameters, 255MB) retains $97\%$ of BERT's performance while being $40\%$ smaller and $60\%$ faster, satisfying mobile latency and hosting requirements.

### Q16. Why not XLM-RoBERTa?
* **Answer**: XLM-RoBERTa (270 million parameters, 1.1GB) is too large for CPU-bound environments. Implementing it requires model quantization and compression, which is planned for FYP-II.

### Q17. Why not deploy the model completely on-device?
* **Answer**: Porting a PyTorch model to run locally on Android requires compiling runtime binaries (like ONNX or TensorFlow Lite) and optimizing execution weights to prevent battery drain. This is deferred to FYP-II.

### Q18. Is the explainability layer actually LIME?
* **Answer**: No. The client highlights are rule-based heuristic alerts; true pertubation-based LIME calculations are deferred to FYP-II due to latency and processing limitations on CPU-bound servers.

### Q19. What makes this system useful despite its limitations?
* **Answer**: It provides a functioning proof-of-concept pipeline, demonstrating background SMS interception, cache management, and threat-classification routing in the Pakistani domain.

### Q20. What is the strongest contribution of FYP-I?
* **Answer**: The integration of background SMS interception with a Transformer-based inference pipeline optimized for Roman Urdu and code-switched smishing patterns.

---

## 3. Conclusion
The audit is complete. The results, metric tables, and limitations have been verified against the repository's files. The 20 viva questions cover key architectural and ML design decisions, ensuring academic viability.
