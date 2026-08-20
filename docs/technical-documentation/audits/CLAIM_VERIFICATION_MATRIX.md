# Claim Verification Matrix

This matrix documents the verification status of all major technical, architectural, and performance claims made throughout the MindShield documentation.

| ID | Claim | Source | Evidence | Status | Confidence | Correction Required |
| :- | :--- | :--- | :--- | :--- | :---: | :--- |
| **CLM-01** | Incoming SMS are intercepted in the background on Android and pushed to Flutter. | `SmsReceiver.kt` & `MainActivity.kt` | Broadcast receiver on `SMS_RECEIVED_ACTION` sends MethodChannel call `onSmsReceived`. | **VERIFIED / IMPLEMENTED** | High | None. |
| **CLM-02** | Captured SMS are saved to a shared SQLite database. | `SmsReceiver.kt` (lines 43-90) | Opens `mindshield.db` directly in Kotlin and inserts records into `sms_messages` with `'pending'` state. | **VERIFIED / IMPLEMENTED** | High | None. |
| **CLM-03** | MindShield uses an "on-device / server-hybrid" architecture. | codebase | Android receiver & SQLite are on-device; NLP inference and feature indicators run on FastAPI backend. | **VERIFIED / IMPLEMENTED** | High | Clearly state that ML inference does *not* happen on-device (runs on backend). |
| **CLM-04** | MindShield uses Explainable AI powered by a LIME explainer. | `validators.py` & `AnalysisService` | No LIME library/explainer is present in code. Explainability is rule-based keyword indicator checks. | **CONTRADICTED** | High | Rename to **Heuristic Feature Attribution**; clarify LIME is a conceptual blueprint / FYP2 target. |
| **CLM-05** | Baseline model trained on UCI dataset has a 93.1% False Positive Rate on Pakistani legitimate banking SMS. | `PAKISTANI_GENERALIZATION_FINAL_REPORT.md` | `v3_evaluation_results.json` log shows 81 out of 87 banking/telecom ham classified as phishing. | **VERIFIED** | High | None. |
| **CLM-06** | Fine-tuned `distilbert-pakscam-v3` candidate reduces Pakistani HAM FPR to 3.45%. | `PAKISTANI_GENERALIZATION_FINAL_REPORT.md` | `v3_evaluation_results.json` shows 3 out of 87 ham misclassified (FPR = 3.45%). | **VERIFIED** | High | Document that `v3` was not promoted to production due to failing a regression test. |
| **CLM-07** | DistilBERT fine-tuning achieves 97.86% accuracy and 90.91% F1 on target test sets. | `distilbert_metrics.json` | Evaluation output metrics in metadata. | **VERIFIED** | High | Specify that this test set is the in-domain UCI test split, not the Pakistani smishing corpus. |
| **CLM-08** | MindShield implements multi-class model classification. | `config.py` & `model_loader.py` | Model config has `num_labels = 2`. The model is binary. Multi-class attack labels are heuristics. | **CONTRADICTED** | High | Revise to state that **ML model is binary**; multi-class labeling is rule-based post-processing. |
| **CLM-09** | Testing includes comprehensive regression suites. | `test_ml_regression_v3.py` | Runs 14 test templates representing distinct edge cases. | **VERIFIED** | High | None. |
