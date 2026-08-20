# MindShield — Thesis Master Outline

> **Document ID**: `docs/THESIS_MASTER_OUTLINE.md`  
> **Phase**: FYP-I Thesis Planning  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Template**: `docs/thesis-template/FYP_Thesis_Template_IMCS_2025.docx`  
> **Scope Lock**: `docs/FYP1_ACADEMIC_SCOPE_LOCK.md`  

---

## Template Compliance Note

This outline follows the official IMCS BS(CS) Thesis template, which mandates exactly **five chapters**. All MindShield content is mapped into this five-chapter structure. Section headings are project-specific; the chapter titles match the template.

Evidence annotations:
- **[FYP-I AVAILABLE]** — Evidence exists in the current repository
- **[FYP-II REQUIRED]** — Evidence requires FYP-II work to produce
- **[MISSING — SHOULD CREATE]** — Evidence can be created now from existing data
- **[SUPERVISOR CONFIRMATION REQUIRED]** — Requires supervisor input

---

## FRONT MATTER

| Page | Content | Status |
|---|---|---|
| Cover Page | University crest, department name, degree, thesis title, submission statement, student names/roll numbers, supervisor name, date | **[MISSING — SHOULD CREATE]** |
| Title Page | Repeats cover page information with formal layout | **[MISSING — SHOULD CREATE]** |
| Certificate | Supervisor/examiner certification of project completion | **[MISSING — SHOULD CREATE]** |
| Declaration | Originality statement with student signatures | **[MISSING — SHOULD CREATE]** |
| Copy Rights | Library authorization statement | **[MISSING — SHOULD CREATE]** |
| Dedication | Personal dedication | **[MISSING — SHOULD CREATE]** |
| Acknowledgements | Thanks to supervisor, department, contributors | **[MISSING — SHOULD CREATE]** |
| Abstract | ~250-word summary of the project | **[MISSING — SHOULD CREATE]** |
| Table of Contents | Auto-generated from Word headings | **[MISSING — SHOULD CREATE]** |
| List of Tables | Auto-generated from table captions | **[MISSING — SHOULD CREATE]** |
| List of Figures | Auto-generated from figure captions | **[MISSING — SHOULD CREATE]** |
| Abbreviations | Project-specific abbreviation list | **[MISSING — SHOULD CREATE]** |

---

## CHAPTER 1 — INTRODUCTION

### 1.1 Background and Motivation **[FYP-I AVAILABLE]**
- SMS fraud landscape in Pakistan (PTA statistics)
- Scale of smishing attacks
- Source: `MindShield_FYP_Proposal.docx` Section 6

### 1.2 Problem Statement **[FYP-I AVAILABLE]**
- Linguistic gap (Roman Urdu / code-switching)
- Explainability gap (black-box classifiers)
- Dataset gap (no Pakistani SMS corpus)
- Source: `MindShield_FYP_Proposal.docx` Section 5

### 1.3 Research Questions **[FYP-I AVAILABLE]**
- RQ1: Transformer fine-tuning for multilingual Pakistani SMS
- RQ2: Explainable AI for threat interpretation
- RQ3: Offline-first thread-based SMS inbox interface with native interventions
- RQ4: Privacy-preserving local SMS monitoring
- Source: `MindShield_FYP_Proposal.docx` Section 7

### 1.4 Aims and Objectives **[FYP-I AVAILABLE]**
- PROP-OBJ-01 through PROP-OBJ-12 (mapped from proposal)
- FYP-I vs FYP-II objective classification
- Source: `docs/PROPOSAL_IMPLEMENTATION_TRACEABILITY.md`

### 1.5 Scope and Limitations **[FYP-I AVAILABLE]**
- Within scope / out of scope
- FYP-I boundary
- Source: `MindShield_FYP_Proposal.docx` Section 10, `docs/FYP1_ACADEMIC_SCOPE_LOCK.md`

### 1.6 Novelty of the Proposed System **[FYP-I AVAILABLE]**
- Native Android background listener integration
- Evaluation of Roman Urdu/multilingual optimization strategies using a quarantined research candidate (v3) compared to an English-centric baseline (v1) serving model
- Source: `MindShield_FYP_Proposal.docx` Section 8

### 1.7 SDG Alignment **[FYP-I AVAILABLE]**
- SDG mapping table
- Source: `MindShield_FYP_Proposal.docx` Section 12

### 1.8 Structure of the Thesis **[MISSING — SHOULD CREATE]**
- Brief overview of each chapter

### 1.9 Summary **[MISSING — SHOULD CREATE]**

---

## CHAPTER 2 — LITERATURE REVIEW/BACKGROUND

### 2.1 SMS Spam and Smishing Detection **[FYP-I AVAILABLE]**
- Evolution of SMS threat vectors
- Domain shifts and transliterated Urdu
- Source: `docs/LITERATURE_REVIEW.md` Sections 2.1-2.2

### 2.2 NLP-Based Cybersecurity **[FYP-I AVAILABLE]**
- Preprocessing and text normalization
- Subword tokenization vs traditional tokenization
- Source: `docs/LITERATURE_REVIEW.md` Sections 3.1-3.2

### 2.3 Traditional Machine Learning Approaches **[FYP-I AVAILABLE]**
- TF-IDF methodology
- Classical classifiers (SVM, Naive Bayes, Random Forest)
- Source: `docs/LITERATURE_REVIEW.md` Sections 4.1-4.2

### 2.4 Deep Learning and Transformer-Based Approaches **[FYP-I AVAILABLE]**
- RNN/LSTM limitations
- Transformer architecture
- Source: `docs/LITERATURE_REVIEW.md` Sections 5.1-5.2

### 2.5 BERT and DistilBERT for Text Classification **[FYP-I AVAILABLE]**
- BERT architecture
- DistilBERT knowledge distillation
- Source: `docs/LITERATURE_REVIEW.md` Sections 6.1-6.2

### 2.6 Explainable AI (XAI) and LIME **[FYP-I AVAILABLE]**
- Black-box problem in security
- LIME methodology
- Source: `docs/LITERATURE_REVIEW.md` Sections 7.1-7.2

### 2.7 Mobile-Based Cybersecurity Systems **[FYP-I AVAILABLE]**
- Source: `docs/LITERATURE_REVIEW.md` Section 8

### 2.8 Existing Systems and Comparative Analysis **[FYP-I AVAILABLE]**
- Comparative feature matrix
- Source: `docs/LITERATURE_REVIEW.md` Section 9

### 2.9 Research Gap Analysis **[FYP-I AVAILABLE]**
- Source: `docs/LITERATURE_REVIEW.md` Section 10

### 2.10 Summary **[FYP-I AVAILABLE]**
- Source: `docs/LITERATURE_REVIEW.md` Section 12

---

## CHAPTER 3 — RESEARCH METHODOLOGY

***PART A — SOFTWARE ENGINEERING & SYSTEM DESIGN***

### 3.1 System Architecture **[FYP-I AVAILABLE]**
- Three-tier architecture (Android client, Flutter engine, FastAPI backend)
- Source: `docs/design/SYSTEM_ARCHITECTURE.md`
- Figure required: System architecture diagram (Figure 3-1) **[FYP-I AVAILABLE — Mermaid exists, render to PNG]**

### 3.2 Software Requirements **[FYP-I AVAILABLE]**
- Functional requirements (FR-01 through FR-08)
- Non-functional requirements
- Source: `docs/SRS.md` Sections 7-8

### 3.3 Use Case Specifications **[FYP-I AVAILABLE]**
- UC-01 through UC-10
- Source: `docs/SRS.md` Section 9, `docs/design/USE_CASE_DIAGRAM.md`
- Figure required: Use case diagram (Figure 3-2) **[FYP-I AVAILABLE — Mermaid exists, render to PNG]**

### 3.4 Database Design **[FYP-I AVAILABLE]**
- SQLite single-table schema (`sms_messages`)
- Source: `docs/design/ERD.md`
- Figure required: ER diagram (Figure 3-3) **[FYP-I AVAILABLE — Mermaid exists, render to PNG]**

### 3.5 Data Flow Design **[FYP-I AVAILABLE]**
- DFD Level 0 and Level 1
- Source: `docs/design/DFD_LEVEL_0.md`, `docs/design/DFD_LEVEL_1.md`
- Figures required: DFD Level-0 diagram (Figure 3-4) and DFD Level-1 diagram (Figure 3-5) **[FYP-I AVAILABLE — Mermaid exists, render to PNG]**

### 3.6 Sequence Diagrams **[FYP-I AVAILABLE]**
- SMS interception and analysis flow
- Source: `docs/design/SEQUENCE_DIAGRAM.md`
- Figure required: Sequence diagram (Figure 3-6) **[FYP-I AVAILABLE — Mermaid exists, render to PNG]**

### 3.7 Deployment Architecture **[FYP-I AVAILABLE]**
- Source: `docs/design/DEPLOYMENT_DIAGRAM.md`
- Figure required: Deployment diagram (Figure 3-7) **[FYP-I AVAILABLE — Mermaid exists, render to PNG]**

***PART B — ML ENGINEERING & DATASET PIPELINE***

### 3.8 Dataset Construction **[FYP-I AVAILABLE]**
- UCI SMS Spam Collection (5,148 records)
- PakScam-SMS dataset (205 unique templates)
- Dataset provenance and linguistic characteristics
- Source: `docs/DATASET_DOCUMENTATION.md` Sections 2-10

### 3.9 Data Preprocessing **[FYP-I AVAILABLE]**
- NFKC normalization
- WordPiece tokenization
- Source: `docs/DATASET_DOCUMENTATION.md` Section 11

### 3.10 Train/Validation/Test Splitting **[FYP-I AVAILABLE]**
- Template-family grouping strategy
- Data leakage prevention
- Source: `docs/DATASET_DOCUMENTATION.md` Sections 13-15

### 3.11 Model Training Methodology **[FYP-I AVAILABLE]**
- DistilBERT fine-tuning pipeline
- Oversampling strategy (Mix-C, 3x local)
- Source: `docs/DATASET_DOCUMENTATION.md` Section 14, `docs/ML_SYSTEM_DOCUMENTATION.md`

### 3.12 Implementation Details **[FYP-I AVAILABLE]**
- Android native SMS interception (Kotlin BroadcastReceiver)
- Flutter client architecture (Feature-First Clean Architecture)
- FastAPI backend endpoints
- Model loading and inference pipeline
- Heuristic explainability highlights
- Source: `docs/01_mindshield_architecture_documentation.md` through `docs/09_sms_background_service.md`
- UI screenshots required (Figures 3-8 through 3-16) **[MISSING — SHOULD CREATE]**

***PART C — VERIFICATION & EVALUATION METHODOLOGY***

### 3.13 Testing Methodology **[FYP-I AVAILABLE]**
- Backend testing strategy (Pytest)
- Frontend testing strategy (Flutter test)
- ML regression testing
- Source: `docs/TESTING_AND_VALIDATION.md`

### 3.14 Evaluation Metrics **[FYP-I AVAILABLE]**
- Precision, Recall, F1-score, FPR, Accuracy
- CPU inference latency measurement methodology
- Source: `docs/DATASET_DOCUMENTATION.md`, `docs/RESULTS_AND_DISCUSSION.md`

### 3.15 Tools and Technologies **[FYP-I AVAILABLE]**
- Source: `MindShield_FYP_Proposal.docx` Section 20

### 3.16 Summary **[MISSING — SHOULD CREATE]**

---

## CHAPTER 4 — RESULTS AND DISCUSSION

### 4.1 Dataset Statistics **[FYP-I AVAILABLE]**
- UCI and PakScam corpus distributions
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 1
- Figure required: Dataset class distribution chart (Figure 4-1) **[MISSING — SHOULD CREATE]**

### 4.2 Baseline Model Results **[FYP-I AVAILABLE]**
- UCI-only DistilBERT baseline
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 2

### 4.3 DistilBERT v1 Results (Active Serving Model) **[FYP-I AVAILABLE]**
- UCI test performance (F1 = 96.00%)
- Pakistani SMS performance (HAM FPR = 93.10%, SPAM Recall = 98.11%)
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 3
- Figure required: Confusion matrix v1 (Figure 4-2) **[MISSING — SHOULD CREATE]**

### 4.4 DistilBERT v3 Results (Research Candidate) **[FYP-I AVAILABLE]**
- UCI test performance (F1 = 95.08%)
- Pakistani SMS performance (HAM FPR = 3.45%, SPAM Recall = 100%)
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 3
- Figure required: Confusion matrix v3 (Figure 4-3) **[MISSING — SHOULD CREATE]**

### 4.5 Model Performance Comparison **[FYP-I AVAILABLE]**
- v1 vs v3 comparison table
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 3.1
- Figure required: v1 vs v3 bar chart (Figure 4-4) **[MISSING — SHOULD CREATE]**

### 4.6 Domain Shift Analysis **[FYP-I AVAILABLE]**
- Why v1 fails on Pakistani HAM messages
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 4.1

### 4.7 Latency Benchmarks **[FYP-I AVAILABLE]**
- v1 mean = 41.95 ms, v3 mean = 57.62 ms
- CPU inference latency definition (NOT end-to-end)
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 4.2
- Figure required: Latency comparison chart (Figure 4-5) **[MISSING — SHOULD CREATE]**

### 4.8 Regression Suite Results **[FYP-I AVAILABLE]**
- v1: 5/14 passed; v3: 13/14 passed
- NOT an independent test set
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 3

### 4.9 Testing and Validation Results **[FYP-I AVAILABLE]**
- 234 backend tests (230 passed, 4 known regressions)
- 5 frontend tests passed
- 75% backend coverage
- Source: `docs/TESTING_AND_VALIDATION.md`

### 4.10 Discussion of Findings **[FYP-I AVAILABLE]**
- Source: `docs/RESULTS_AND_DISCUSSION.md` Sections 4-5

### 4.11 Limitations **[FYP-I AVAILABLE]**
- Dataset size constraints
- Template bias
- HTTP development transport
- Heuristic highlights vs true LIME
- Source: `docs/RESULTS_AND_DISCUSSION.md` Section 6

### 4.12 Summary **[MISSING — SHOULD CREATE]**

---

## CHAPTER 5 — CONCLUSION AND FUTURE DIRECTIONS

### 5.1 Summary of FYP-I Achievements **[FYP-I AVAILABLE]**
- Source: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 2

### 5.2 Achievement of Objectives **[FYP-I AVAILABLE]**
- Objective-by-objective status mapping
- Source: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 3

### 5.3 Contributions **[FYP-I AVAILABLE]**
- Engineering contributions
- Machine learning contributions
- Security contributions
- Source: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Sections 5-7

### 5.4 Limitations **[FYP-I AVAILABLE]**
- Source: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 8

### 5.5 Recommendations **[FYP-I AVAILABLE]**
- Source: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 9

### 5.6 FYP-II Scope and Future Directions **[COMBINED]**
- XLM-RoBERTa multilingual training **[FYP-II REQUIRED]**
- 5-class psychological manipulation classification **[FYP-II REQUIRED]**
- True LIME perturbation explanations **[FYP-II REQUIRED]**
- HTTPS/JWT secure transport **[FYP-II REQUIRED]**
- ONNX on-device inference **[FYP-II REQUIRED]**
- Larger Pakistani SMS dataset (5000+ records) **[FYP-II REQUIRED]**
- Source: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 10, `docs/FYP1_ACHIEVEMENTS_VS_FYP2.md`

### 5.7 Summary **[MISSING — SHOULD CREATE]**

---

## REFERENCES **[FYP-I AVAILABLE]**
- IEEE numbered format [1], [2], [3]
- Current count: 10 references
- Source: `docs/LITERATURE_REVIEW.md` Section 13
- **[SUPERVISOR CONFIRMATION REQUIRED — REFERENCE EXPANSION]** — may need expansion beyond 10 references

---

## APPENDICES **[SUPERVISOR CONFIRMATION REQUIRED — APPENDICES FORMATTING/NUMBERING]**

### Appendix A — Test Case Matrix **[FYP-I AVAILABLE]**
- Source: `docs/TEST_CASE_MATRIX.md`

### Appendix B — API Endpoint Specifications **[FYP-I AVAILABLE]**
- Source: `docs/SRS.md` Section 11

### Appendix C — Dataset Sample Templates **[FYP-I AVAILABLE]**
- Source: `docs/DATASET_DOCUMENTATION.md`

### Appendix D — Regression Suite Cases **[FYP-I AVAILABLE]**
- Source: `backend/tests/test_ml_regression.py`

### Appendix E — Repository Structure **[MISSING — SHOULD CREATE]**
