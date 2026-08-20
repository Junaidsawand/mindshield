# Chapter 5 Conclusion and Future Directions Audit

This document traces the academic audits and corrections applied to **Chapter 5 (Conclusion and Future Directions)** of `docs/MindShield_FYP1_Thesis_Draft.docx`.

## 1. Audit Matrix and Corrections Applied

| Section | Original Text Summary | Corrected Text Focus | Justification |
| :--- | :--- | :--- | :--- |
| **5.1 Summary of FYP-I Achievements** | Described broad mobile smishing filtration design without specific validation. | Explicitly details the FastAPI centralized logical tier, local SQLite caches, and binary DistilBERT model. Documents localized FPR reduction from 93.10% to 3.45%. | Aligns summary with actual implementation and Pakistani domain shift results. |
| **5.2 Achievement of Objectives** | Asserted Objectives 1-8 were successfully completed without clear scope boundaries. | Iterates through Objectives 1-8 individually, detailing accomplishments, and explicitly notes deferral of HTTPS, JWT, and runtime LIME to FYP-II. | Establishes scientific honesty regarding incomplete production goals in FYP-I. |
| **5.3 Contributions** | General description of architecture contributions. | Categorized contributions into: Engineering (Kotlin capture + SQLite + FastAPI + Flutter client), Research/Evaluation (Pakistani domain shift empirical analysis), Dataset (205-template PakScam-SMS corpus), and Explainability (decoupled heuristic threat cards). | Provides clear taxonomic organization as expected in undergraduate defenses. |
| **5.4 Limitations** | Broad claims of minor limitations. | Specifically documents: limited dataset volume (205 templates), non-independent regression tests (14 cases), unencrypted network transit, client-side heuristic card bypass of live LIME, and single physical device testing scope. | Conforms to rigorous academic style by stating precise constraints. |
| **5.5 Recommendations** | Simple recommendations on framework improvements. | Recommends segmentation of preprocessors (classical vs neural presets), localized templates oversampling (Mix-C), client-side explainability, and worst-case SLA latency monitoring. | Derives recommendations directly from experimental findings in Chapter 4. |
| **5.6 FYP-II Scope & Future Directions** | Mixed future goals with current accomplishments. | Isolates JWT/OAuth security, ONNX/TFLite model conversion, multilingual expansion (XLM-RoBERTa), multi-class classification, true runtime LIME computations, and large-scale validation into FYP-II future work. | Maintains academic integrity by locking current progress within FYP-I bounds. |
| **5.7 Summary** | General template closing statement. | Concludes by summarizing achievements, highlighting the reduction of FPR to 3.45%, and framing it as a solid foundation for FYP-II. | Summarizes Chapter 5 findings concisely. |

## 2. Verification Outcomes
* **Paragraph Matching Verification**: Successfully updated all 7 normal content paragraphs in Chapter 5 corresponding to sections 5.1 to 5.7.
* **Scope Lock Conformance**: Verified that no claims of JWT, HTTPS, ONNX/TFLite, or XLM-R are represented as completed. All of these are categorized as future scope.
