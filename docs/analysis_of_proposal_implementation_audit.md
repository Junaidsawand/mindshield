# Internal Proposal Audit & Viva Stress Test Guide

> **Document ID**: `docs/analysis_of_proposal_implementation_audit.md`  
> **Phase**: FYP-I Thesis & Viva Preparation  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Quality & Compliance Audit

This audit evaluates the current implementation against the approved proposal targets to identify gaps, verify claims, and ensure defensibility during the viva.

### 1.1 Strongest Achieved Areas
* **FASTAPI-to-Flutter pipeline**: The decoupled network client interface mapping and JSON serialization are fully implemented and verified via unit tests.
* **Template-family Data Splitting**: Grouping splits by family prevents direct template leakage during training and validation.
* **Optimized Inference Latency**: Active model CPU execution averages $41.95\text{ ms}$, satisfying latency requirements.

### 1.2 Identified Gaps and Implementation Weaknesses
* **Local HTTP Loopback**: Development loopback uses unencrypted HTTP. Production HTTPS and JWT authentication are deferred to FYP-II.
* **Heuristic Explainability (LIME placeholder)**: Client highlighting uses static rule-based checks instead of true perturbation-based LIME calculations.
* **Telemetry and Device Hook Verification**: Telephony receiver interception is device-dependent and lacks automated unit test logs.

---

## 2. Academic Viva Stress Test (25 Crucial Q&As)

### Q1. Which proposal objective is strongest?
* **Answer**: The decoupled REST analysis pipeline (exposing `/analyze` on FastAPI and querying via Dio with retry handling), which is fully implemented, verified via unit/network mock tests, and documented.
* **Evidence**: [`analysis_service_test.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/test/analysis_service_test.dart) and `test_analysis.py`.
* **Dangerous Answer**: *"The dataset is our strongest objective because it contains 205 templates."* (The dataset is small and template-derived, making it a weaker research contribution).

### Q2. Which objective is weakest?
* **Answer**: Real-time native interception verification. telecommunication hook receivers are device-dependent and cannot be verified in automated headless environments.
* **Evidence**: [`IncomingSmsReceiver.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/android/app/src/main/kotlin/com/example/mindshield/IncomingSmsReceiver.kt) lacks active test runner output logs.
* **Dangerous Answer**: *"Nothing is weak; all components are fully completed and verified."* (This claim will be rejected by examiners).

### Q3. What did you fail to implement?
* **Answer**: True LIME explainability, HTTPS transmission channels, token-based JWT authorization, and Pipeline 2 (5-class psychological manipulation categorization). These are defined in the proposal boundary as FYP-II deliverables.
* **Evidence**: [`docs/design/FYP1_VS_FYP2_BOUNDARY.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/FYP1_VS_FYP2_BOUNDARY.md) Section 1.
* **Dangerous Answer**: *"We forgot to implement those files or ran out of time."* (Frame it as planned scope separation).

### Q4. Why did you not implement it?
* **Answer**: True LIME perturbations take over ~30 seconds on CPU. Multilingual XLM-RoBERTa models require GPU resources, and HTTPS requires public hosting. These constraints led us to focus on a binary DistilBERT proof-of-concept for FYP-I.
* **Evidence**: `docs/design/FYP1_VS_FYP2_BOUNDARY.md` Section 2.
* **Dangerous Answer**: *"The package libraries did not work in our IDE environment."* (Suggests technical inability; always cite engineering and performance constraints).

### Q5. Why is v1 active when v3 performs much better locally?
* **Answer**: `distilbert-pakscam-v1` satisfies the CPU latency SLA ($41.95\text{ ms}$ mean vs $57.62\text{ ms}$ for `v3`) and retains high UCI F1 ($96.00\%$). `v3` is kept as a quarantined research candidate because it requires testing on a larger, independent corpus.
* **Evidence**: `v3_evaluation_results.json` latency profiles.
* **Dangerous Answer**: *"v3 has bugs or is unstable."* (v3 is stable; it is quarantined due to evaluation sample constraints).

### Q6. Why is your Pakistani dataset only 205 samples?
* **Answer**: Telecommunications privacy regulations prevent developers from accessing user SMS streams. Thus, the corpus was manually built from 15 real seeds, 125 synthetic variations, and 65 targeted augmentations.
* **Evidence**: [`docs/DATASET_DOCUMENTATION.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/DATASET_DOCUMENTATION.md) Section 4.
* **Dangerous Answer**: *"205 samples are enough to cover all Pakistani SMS."* (This claims excessive generalization).

### Q7. How do you defend synthetic/template-derived data?
* **Answer**: Template-derived curation is a standard approach when privacy constraints prevent real-world collection. It provides consistent formatting to evaluate model behavior before launching user-feedback collection.
* **Evidence**: `docs/DATASET_DOCUMENTATION.md` provenance note.
* **Dangerous Answer**: *"The dataset is composed of real-world messages we collected."* (Claiming synthetic data is real-world is academically dishonest).

### Q8. How did you prevent data leakage?
* **Answer**: Splits were grouped at the `template_family` level before training. This ensures no variants of the same base template appear in both the training and testing datasets.
* **Evidence**: `train_pakscam_v3_distilbert.py` split functions.
* **Dangerous Answer**: *"We did a random split and got high scores."* (Random splits lead to severe template leakage).

### Q9. Is your test set independent?
* **Answer**: The UCI test split is independent. However, the localized test split (41 samples) is template-derived, meaning it shares structural patterns with the training templates despite template-family partitioning.
* **Evidence**: `docs/analysis_of_dataset_documentation.md` Section 4.
* **Dangerous Answer**: *"Yes, it is completely independent of the training templates."* (Ignore structural similarities at your own peril).

### Q10. Why is your regression suite not an independent test set?
* **Answer**: The 14 regression cases are derived from the base templates, meaning they serve as a regression benchmark gating suite to check for model degradation on critical targets, rather than an unseen test set.
* **Evidence**: `test_ml_regression.py`.
* **Dangerous Answer**: *"It is an independent test set."* (This will be flagged by examiners).

### Q11. What does your latency number actually measure?
* **Answer**: Model CPU inference latency, including NFKC normalization, WordPiece tokenization, and the forward PyTorch execution pass.
* **Evidence**: `v3_evaluation_results.json` latency profiles.
* **Dangerous Answer**: *"It measures end-to-end response times on mobile devices."* (Inference latency is CPU-bound and excludes transit overheads).

### Q12. Why isn't it end-to-end?
* **Answer**: End-to-end latency includes network transit times, API request routing, database caches, and UI rendering, which are excluded from CPU inference metrics.
* **Evidence**: `docs/analysis_of_testing_validation.md` Section 1.1.
* **Dangerous Answer**: *"We did not think it was important to measure network latency."* (Acknowledge network latency as a key production profiling target).

### Q13. Is your system really real-time?
* **Answer**: Yes. Model inference is sub-second ($41.95\text{ ms}$). However, network transit can add $50\text{ ms}$ to $200\text{ ms}$, meaning the complete pipeline is near-real-time.
* **Evidence**: `docs/RESULTS_AND_DISCUSSION.md` latency metrics.
* **Dangerous Answer**: *"Yes, it is 100% real-time under any network condition."* (Transit overheads are network-dependent).

### Q14. Is your explainability system actually LIME?
* **Answer**: No. The client highlights are rule-based heuristic alerts; true LIME explanations are deferred to FYP-II due to latency and processing limitations on CPU-bound servers.
* **Evidence**: `docs/design/FYP1_VS_FYP2_BOUNDARY.md` Section 2.2.
* **Dangerous Answer**: *"Yes, LIME runs on the backend for every message."* (False; backend does not run perturbation loops).

### Q15. Why isn't HTTPS implemented?
* **Answer**: Setting up public domain endpoints and SSL certificates requires active hosting, which is planned for final cloud staging in FYP-II.
* **Evidence**: `docs/design/FYP1_VS_FYP2_BOUNDARY.md` Section 2.3.
* **Dangerous Answer**: *"We did not know how to generate local certificates."* (TLS setup is deferred to production staging).

### Q16. Why isn't authentication implemented?
* **Answer**: To simplify prototype testing, the endpoints are unauthenticated. Implementing secure access tokens (JWT) is scheduled for the production deployment phase in FYP-II.
* **Evidence**: `docs/design/FYP1_VS_FYP2_BOUNDARY.md` Section 1.
* **Dangerous Answer**: *"FastAPI does not have security features."* (FastAPI has security sub-modules; authentication is deferred to production staging).

### Q17. Why use server-based inference?
* **Answer**: Deep learning inference requires substantial CPU and RAM resources. A server-based architecture keeps the mobile client lightweight and allows for centralized model updates.
* **Evidence**: [`SYSTEM_ARCHITECTURE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SYSTEM_ARCHITECTURE.md).
* **Dangerous Answer**: *"Flutter cannot run deep learning models."* (Avoid claiming software limitations; frame it as client resource optimization).

### Q18. Why not on-device inference?
* **Answer**: Porting models to run on-device requires ONNX compilation and quantization to prevent battery drain. This is deferred to FYP-II to simplify prototype testing in FYP-I.
* **Evidence**: `docs/FYP1_ACHIEVEMENTS_VS_FYP2.md` Section 1.
* **Dangerous Answer**: *"ONNX doesn't work on Android."* (ONNX works on Android; optimization is deferred to FYP-II).

### Q19. Why DistilBERT?
* **Answer**: DistilBERT (66 million parameters, 255MB) retains $97\%$ of BERT's performance while being $40\%$ smaller and $60\%$ faster, satisfying mobile latency and hosting requirements.
* **Evidence**: `docs/LITERATURE_REVIEW.md` Section 13.2.
* **Dangerous Answer**: *"It is the easiest model to train."* (DistilBERT is selected for size and performance, not training difficulty).

### Q20. Why not XLM-R?
* **Answer**: XLM-RoBERTa (270 million parameters, 1.1GB) requires substantial memory resources. Implementing it requires model quantization and compression, which is planned for FYP-II.
* **Evidence**: `docs/design/FYP1_VS_FYP2_BOUNDARY.md` Section 2.1.
* **Dangerous Answer**: *"XLM-R doesn't support Roman Urdu."* (Multilingual models support Roman Urdu; the constraint is model size).

### Q21. What happens when scammers change wording?
* **Answer**: The model's classification accuracy would decline as fraudsters develop new smishing campaigns. This requires regular retraining loops and temporal validation splits.
* **Evidence**: `docs/DATASET_DOCUMENTATION.md` Section 23.2.
* **Dangerous Answer**: *"The model will automatically adjust to new layouts."* (Supervised transformers cannot classify unseen structures without retraining).

### Q22. What is your strongest limitation?
* **Answer**: The small, template-derived dataset (205 samples), which limits validation of statistical significance.
* **Evidence**: `docs/analysis_of_results_and_discussion.md` Section 1.2.
* **Dangerous Answer**: *"The server setup is our biggest limitation."* (Dataset constraints represent the primary ML bottleneck).

### Q23. What is your strongest contribution?
* **Answer**: The integration of background SMS interception with a Transformer-based inference pipeline optimized for Roman Urdu and code-switched smishing patterns.
* **Evidence**: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 11.
* **Dangerous Answer**: *"Our visual explainability LIME card."* (Visual explainability is heuristic, not true LIME).

### Q24. What exactly is novel about your project?
* **Answer**: Developing a localized, bilingual classifier that targets Roman Urdu smishing patterns and integrates with native Android background listeners.
* **Evidence**: `docs/LITERATURE_REVIEW.md` Section 6.2.
* **Dangerous Answer**: *"Our deep learning model architecture."* (We use standard DistilBERT; novelty lies in localized training and native integration).

### Q25. If you had another six months, what would you fix first?
* **Answer**: Set up secure HTTPS communication with JWT access tokens, compile a larger Pakistani SMS dataset ($5000+$ records), and port the model to run locally using ONNX.
* **Evidence**: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 9.
* **Dangerous Answer**: *"We would build a iOS version first."* (Frame it as engineering and ML improvements).

---

## 3. Conclusion
This guide audit provides a technically honest baseline to help the candidate defend the FYP-I prototype during the viva. Acknowledging limitations professionally is key to a successful defense.
