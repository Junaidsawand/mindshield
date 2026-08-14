# Internal Conclusion Audit & Viva Stress Test

> **Document ID**: `docs/analysis_of_conclusion_and_recommendations.md`  
> **Phase**: FYP-I Conclusion Verification  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Quality & Boundary Audit

This audit evaluates the Conclusion findings against the repository's files to ensure boundary alignment and prevent requirement inflation.

### 1.1 Boundary Matrix Verification
* **Active Model**: `distilbert-pakscam-v1` remains the active serving model. XLM-RoBERTa is classified as a planned FYP-II extension.
* **Explainability (XAI)**: Rule-based highlights are confirmed to be a temporary placeholder; true LIME explanations are deferred to FYP-II due to latency constraints on CPU-bound servers.
* **Network Protocol**: The loopback prototype is confirmed to communicate over unencrypted HTTP. HTTPS and JWT token authentication are deferred to FYP-II.

---

## 2. Academic Viva Stress Test (20 Crucial Examiner Q&As)

### Q1. Why is v1 active if v3 has dramatically lower Pakistani HAM FPR?
* **Answer**: `distilbert-pakscam-v1` serves as the baseline production model because it satisfies the CPU latency SLA ($41.95\text{ ms}$ mean vs $57.62\text{ ms}$ for `v3`) and retains high UCI F1 ($96.00\%$). `v3` is quarantined as a research candidate because it requires extensive user-acceptance and load testing to confirm that the oversampling weights do not cause regression on other unseen messaging configurations.
* **Dangerous Answer**: *"v3 is buggy and was quarantined because it failed the UCI test."* (The F1-score of v3 on UCI is $95.08\%$, which is stable. The quarantine is a standard safety procedure due to evaluation sample constraints).

### Q2. Why did UCI performance remain high while Pakistani HAM performance collapsed?
* **Answer**: `v1` was trained primarily on the English UCI dataset, where features like banking links (`bit.ly`) and numeric transaction codes act as strong spam indicators. In Pakistani communications, these features are common in legitimate alerts, leading the model to misclassify them due to domain shift.
* **Dangerous Answer**: *"Pakistani banks use bad formatting that looks like spam."* (Avoid criticizing regional messaging formats; frame it as a dataset-specific domain shift).

### Q3. Why is v3 not deployed?
* **Answer**: It is kept as a quarantined candidate because of SLA latency concerns ($57.62\text{ ms}$ approaching the $60\text{ ms}$ gate) and minor regressions on carrier promotional language.
* **Dangerous Answer**: *"We did not have time to update the configuration file."* (Always cite engineering constraints like latency gates and validation metrics).

### Q4. Why is 205 samples insufficient?
* **Answer**: A small sample size limits the evaluation's statistical power and may not cover all formatting, language, and spelling variations in real-world SMS.
* **Dangerous Answer**: *"It is enough for a prototype and handles all main banks."* (Acknowledge dataset limitations professionally).

### Q5. How did you prevent template leakage?
* **Answer**: Splits were grouped at the `template_family` level before training. This ensures no variants of the same base template appear in both the training and testing datasets.
* **Dangerous Answer**: *"We shuffled the dataset randomly before splitting."* (Random splits lead to severe template leakage).

### Q6. Is the regression suite independent?
* **Answer**: No. The 14 regression cases are derived from the base templates, meaning they serve as a regression benchmark gating suite to check for model degradation on critical targets, rather than an unseen test set.
* **Dangerous Answer**: *"Yes, it is a completely independent test set we compiled from scratch."* (This is inaccurate and represents a major academic vulnerability).

### Q7. What exactly does 41.95 ms measure?
* **Answer**: It measures model CPU inference latency, including NFKC normalization, WordPiece tokenization, and the forward PyTorch execution pass.
* **Dangerous Answer**: *"It measures end-to-end response times on mobile devices."* (Inference latency is CPU-bound and excludes transit overheads).

### Q8. What exactly does 57.62 ms measure?
* **Answer**: Model CPU inference latency for the `v3` candidate, which is higher due to oversampling weights and augmented vocabularies.
* **Dangerous Answer**: *"The server processing time including network calls."* (It is CPU execution only).

### Q9. Why isn't this end-to-end latency?
* **Answer**: End-to-end latency includes network transit times, API request routing, database caches, and UI rendering, which are excluded from CPU inference metrics.
* **Dangerous Answer**: *"We don't measure it because the simulator has no network."* (The simulator communicates locally; latency metrics are separated to ensure profiling accuracy).

### Q10. Why isn't the current explainability system true LIME?
* **Answer**: True LIME requires fitting a linear surrogate model by generating and predicting $1000+$ text perturbations, taking over $30\text{ seconds}$ on standard CPU hosts. The system uses static, rule-based indicators to approximate term highlights.
* **Dangerous Answer**: *"LIME is too complicated to implement in Flutter."* (XAI pipeline execution is a server-side processing limit, not a client-side limitation).

### Q11. Why use DistilBERT?
* **Answer**: DistilBERT (66 million parameters, 255MB) retains $97\%$ of BERT's performance while being $40\%$ smaller and $60\%$ faster, satisfying mobile latency and hosting requirements.
* **Dangerous Answer**: *"It was the only model available on HuggingFace."* (This implies a lack of research depth).

### Q12. Why not XLM-R?
* **Answer**: XLM-RoBERTa (270 million parameters, 1.1GB) requires substantial memory resources. Implementing it requires model quantization and compression, which is planned for FYP-II.
* **Dangerous Answer**: *"XLM-R doesn't support Roman Urdu."* (It is a multilingual model; the limitation is model size).

### Q13. Why use synthetic/template-derived data?
* **Answer**: Telecommunications privacy constraints prevent access to user SMS streams, making synthetic template generation a practical approach to building a localized corpus.
* **Dangerous Answer**: *"It is easier than collecting real messages."* (Frame it as a privacy and accessibility constraint).

### Q14. How would you collect a real Pakistani dataset?
* **Answer**: We plan to implement anonymized user feedback loops in FYP-II, allowing users to submit flagged smishing messages to a secure repository.
* **Dangerous Answer**: *"We will scrape private user databases online."* (Scraping private user databases violates privacy regulations).

### Q15. What would happen under temporal drift?
* **Answer**: The model's classification accuracy would decline as fraudsters develop new smishing campaigns. This requires regular retraining loops and temporal validation splits.
* **Dangerous Answer**: *"The model will automatically adjust to new layouts."* (Supervised transformers cannot classify unseen structures without retraining).

### Q16. Why is HTTPS not currently implemented?
* **Answer**: Setting up public domain endpoints and SSL certificates requires active hosting, which is planned for final cloud staging in FYP-II.
* **Dangerous Answer**: *"FastAPI does not support HTTPS."* (FastAPI supports TLS via reverse proxies like Nginx).

### Q17. Why does the prototype use a server instead of on-device inference?
* **Answer**: Porting a PyTorch model to run locally on Android requires compiling runtime binaries (like ONNX or TensorFlow Lite) and optimizing execution weights to prevent battery drain. This is deferred to FYP-II.
* **Dangerous Answer**: *"Android devices cannot run deep learning models."* (Modern mobile devices run quantized models via ONNX).

### Q18. How would you improve generalization?
* **Answer**: By training on a larger, independently annotated Pakistani SMS dataset ($5000+$ records) and testing against out-of-vocabulary variations.
* **Dangerous Answer**: *"By adding more epochs during training."* (Over-training on a small dataset leads to overfitting).

### Q19. How would you prove statistical significance?
* **Answer**: By evaluating the model on a larger test corpus and executing statistical hypothesis tests (e.g. McNemar's test) on classification outcomes.
* **Dangerous Answer**: *"Our $100\%$ recall rate already proves statistical significance."* (Recall rates on a small test split are not statistically significant).

### Q20. What is the strongest weakness of the project?
* **Answer**: The reliance on a small, template-derived dataset and CPU-based inference hosted on a central server, which introduces network latency and hosting dependencies.
* **Dangerous Answer**: *"The system does not have any weaknesses."* (An examiner will reject claims of a perfect system).

---

## 3. Conclusion
The audit is complete. The results, metric tables, and limitations have been verified against the repository's files. The 20 viva questions cover key architectural and ML design decisions, ensuring academic viability.
