# MindShield — FYP-I Thesis Writing Foundation

## 1. Document Control
- **Document ID**: `docs/THESIS_WRITING_FOUNDATION.md`
- **Phase**: FYP-I Thesis Ingestion & Grounding
- **Status**: Completed
- **Date**: 2026-08-15
- **Author**: Junaid Ahmed | Final Year Project | University of Sindh
- **Scope Lock Baseline**: [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md)
- **Official Template**: `docs/thesis-template/FYP_Thesis_Template_IMCS_2025.docx`

---

## 2. Official Template Rules
Verified from `docs/thesis-template/FYP_Thesis_Template_IMCS_2025.docx`:
- **Page Size**: A4 (8.27 in × 11.69 in)
- **Margins**: Left: 1.50 in (binding margin), Right: 1.00 in, Top: 1.00 in, Bottom: 1.00 in.
- **Font Family**: Times New Roman (underlying Word styles define Times New Roman; ignore Aptos overrides found in template runs).
- **Font Sizes**: Body Text: 12 pt, Heading 1: 18 pt, Heading 2: 14 pt, Heading 3: 12 pt, Heading 4/5: 12 pt, Caption/Figure Caption: 11 pt/9 pt, Header/Footer/TOC: 10 pt/11 pt.
- **Heading Styles**: 
  - Heading 1: Bold, centered.
  - Heading 2: Bold, left-aligned.
  - Heading 3: Bold, left-aligned.
- **Chapter-Title Formatting**: Each chapter opens with two consecutive Heading 1 paragraphs:
  - Line 1: `CHAPTER N` (e.g., CHAPTER 1)
  - Line 2: Chapter title in ALL CAPS (e.g., INTRODUCTION)
- **Section-Heading Formatting**: Heading 2 (e.g., 1.1 Motivation).
- **Subsection Formatting**: Heading 3 (e.g., 1.2.1 Subheadings).
- **Paragraph Alignment**: Justified.
- **Line Spacing**: 1.5 lines.
- **Paragraph Spacing**: 12 pt before paragraphs in Normal style; Heading 1 has 30 pt before and 6 pt after.
- **Indentation**: None (no first-line indent).
- **Page Numbering**: Roman numerals in footer (I, II, III...) for Front Matter; Arabic numerals in footer (1, 2, 3...) for Main Body.
- **Header/Footer Formatting**: Custom footer numbering, different first page enabled for Section 0 (Cover page).
- **Table Caption Style**: Above the table, formatted as `Table {chapter}-{sequence} Caption` (using No Spacing style).
- **Figure Caption Style**: Below the figure, formatted as `Figure {chapter}-{sequence} Caption` (using Figure Caption style).
- **Reference Formatting**: IEEE numbered bracket style `[1]`, range syntax `[1-3]`.
- **Appendix Formatting**: Appendix letters (`Appendix A`, `Appendix B`) or numbers (`Appendix 1`) — **[UNKNOWN — SUPERVISOR CONFIRMATION REQUIRED]**.

---

## 3. Verified Project Identity
- **Project Title**: MindShield: An Explainable NLP-Based System for Detecting Psychological Manipulation in Pakistani Scam SMS
- **Department**: Institute of Mathematics and Computer Science (IMCS)
- **Degree**: Bachelor of Science in Computer Science (BSCS)
- **Host Institution**: University of Sindh, Jamshoro
- **Submission Date (Proposal)**: June 2026
- **Submission Date (Thesis Expected)**: December 2025  
- **Discrepancies**:
  - `[IDENTITY DISCREPANCY — SUPERVISOR/TEAM CONFIRMATION REQUIRED]`: Submission date is labeled as June 2026 in the proposal text, but the template indicates December 2025. Confirm expected submission year with department.

---

## 4. Verified Team Members and Supervisor
Information verified directly from the approved proposal database (`Table 0` and `Table 10` of `docs/MindShield_FYP_Proposal.docx`):
- **Group Leader**: Junaid Ahmed (Roll No: **2K23/CSM/54**)
- **Team Member**: Kalpna (Roll No: **2K23/CSM/55**)
- **Team Member**: Mudasar Ali (Roll No: **2K23/CSM/81**)
- **Supervisor**: Mr. Zubair Kandhro (Institute of Mathematics and Computer Science)

*Note: Use these exact spellings for all formal documents. Discrepancies like "Ahmed" to "Ahmad", "Kalpna" to "Kalpana", and "Mudasar" to "Mudassar" must be rejected in favor of this baseline.*

---

## 5. Five-Chapter Thesis Structure
The departmental template mandates exactly **five chapters**. No sixth chapter may be created. Chapter titles match the template:
- **CHAPTER 1 — INTRODUCTION**
- **CHAPTER 2 — LITERATURE REVIEW/BACKGROUND**
- **CHAPTER 3 — RESEARCH METHODOLOGY**
- **CHAPTER 4 — RESULTS AND DISCUSSION**
- **CHAPTER 5 — CONCLUSION AND FUTURE DIRECTIONS**
- **REFERENCES** (following Chapter 5)

Chapter 3 utilizes three non-numbered parts to structure the methodology logically:
- ***PART A — SOFTWARE ENGINEERING & SYSTEM DESIGN*** (3.1 to 3.7)
- ***PART B — ML ENGINEERING & DATASET PIPELINE*** (3.8 to 3.12)
- ***PART C — VERIFICATION & EVALUATION METHODOLOGY*** (3.13 to 3.16)

*Caution: PART labels must remain plain bold markdown text, and must NOT be styled as Heading levels or numbered chapters.*

---

## 6. Front-Matter Structure
Front matter pages must appear in this exact order:
1. **Cover Page**: Title, student names/roll numbers, supervisor name, department, university, crest area.
2. **Title Page**: Duplicates cover page with formal certificate borders.
3. **Certificate**: Formal Supervisor/Examiner certificate.
4. **Declaration**: Academic originality statement with student signatures.
5. **Copyrights**: Jamshoro Library release authorization.
6. **Dedication**: Student personal dedications.
7. **Acknowledgements**: Thanks to supervisor, department, family, and peers.
8. **Abstract**: ~250-word text summarizing background, binary DistilBERT model training, performance logs, and local Roman Urdu validation findings.
9. **Table of Contents**: Heading hierarchy mapping.
10. **List of Tables**: Tabular captions mapping.
11. **List of Figures**: Diagrammatic captions mapping.
12. **Abbreviations**: Tab-separated acronym registry.

---

## 7. Chapter 1 Evidence Map
- **1.1 Background and Motivation**: Smishing landscape in Pakistan, PTA advisory statistics, vulnerability of mobile networks.  
  *Source*: `docs/MindShield_FYP_Proposal.docx` Section 6.1-6.5. `[FYP-I AVAILABLE]`
- **1.2 Problem Statement**: Lack of Roman Urdu protection, black-box AI outputs, missing Pakistani dataset.  
  *Source*: `docs/MindShield_FYP_Proposal.docx` Section 5. `[FYP-I AVAILABLE]`
- **1.3 Research Questions**: RQ1 (Transformer tuning), RQ2 (Explainability), RQ3 (Thread-based SMS interface), RQ4 (Local SMS privacy).  
  *Source*: `docs/MindShield_FYP_Proposal.docx` Section 7. `[FYP-I AVAILABLE]`
- **1.4 Aims and Objectives**: PROP-OBJ-01 to 12.  
  *Source*: `docs/PROPOSAL_IMPLEMENTATION_TRACEABILITY.md`. `[FYP-I AVAILABLE]`
- **1.5 Scope and Limitations**: Scope limits for FYP-I.  
  *Source*: `docs/FYP1_ACADEMIC_SCOPE_LOCK.md` Section N. `[FYP-I AVAILABLE]`
- **1.6 Novelty of the Proposed System**: Native background SMS listeners; Urdu/bilingual optimization evaluation of candidate models compared to active English-centric serving baseline.  
  *Source*: `docs/MindShield_FYP_Proposal.docx` Section 8. `[FYP-I AVAILABLE]`
- **1.7 SDG Alignment**: Target SDG mappings (SDG 9, 16).  
  *Source*: `docs/MindShield_FYP_Proposal.docx` Section 12. `[FYP-I AVAILABLE]`
- **1.8 Structure of the Thesis**: Brief chapter roadmap. `[MISSING — SHOULD CREATE]`
- **1.9 Summary**: Introductory chapter summary. `[MISSING — SHOULD CREATE]`

---

## 8. Chapter 2 Evidence Map
- **2.1 SMS Spam and Smishing Detection**: Context, timeline, and domain shifts to transliterated Urdu.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 2. `[FYP-I AVAILABLE]`
- **2.2 NLP-Based Cybersecurity**: Normalization and subword tokenization overview.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 3. `[FYP-I AVAILABLE]`
- **2.3 Traditional Machine Learning**: TF-IDF and classical classification models.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 4. `[FYP-I AVAILABLE]`
- **2.4 Deep Learning and Transformers**: RNN/LSTM limits and Transformer architecture.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 5. `[FYP-I AVAILABLE]`
- **2.5 BERT and DistilBERT**: BERT vs DistilBERT (Knowledge distillation).  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 6. `[FYP-I AVAILABLE]`
- **2.6 Explainable AI (XAI)**: Black-box issues and LIME methodology.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 7. `[FYP-I AVAILABLE]`
- **2.7 Mobile Cybersecurity Systems**: Client-side monitoring constraints.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 8. `[FYP-I AVAILABLE]`
- **2.8 Existing Systems and Comparative Analysis**: Feature matrix comparison.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 9. `[FYP-I AVAILABLE]`
- **2.9 Research Gap Analysis**: Detailed gaps identified.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 10. `[FYP-I AVAILABLE]`
- **2.10 Summary**: Literature summary.  
  *Source*: `docs/LITERATURE_REVIEW.md` Section 12. `[FYP-I AVAILABLE]`

---

## 9. Chapter 3 Evidence Map

### PART A — SOFTWARE ENGINEERING & SYSTEM DESIGN
- **3.1 System Architecture**: Clean architecture layers.  
  *Source*: `docs/SYSTEM_DESIGN.md` Section 4.1. `[FYP-I AVAILABLE]`
- **3.2 Software Requirements**: Functional FR-01 to FR-08, non-functional rules.  
  *Source*: `docs/SRS.md` Section 7-8. `[FYP-I AVAILABLE]`
- **3.3 Use Case Specifications**: UC-01 to UC-10.  
  *Source*: `docs/SRS.md` Section 9. `[FYP-I AVAILABLE]`
- **3.4 Database Design**: Consolidated SQLite schema.  
  *Source*: `docs/design/ERD.md` Section 2. `[FYP-I AVAILABLE]`
- **3.5 Data Flow Design**: DFD Level 0 & Level 1.  
  *Source*: `docs/design/DFD_LEVEL_0.md` & `DFD_LEVEL_1.md`. `[FYP-I AVAILABLE]`
- **3.6 Sequence Diagrams**: API and native intercept flows.  
  *Source*: `docs/design/SEQUENCE_DIAGRAM.md`. `[FYP-I AVAILABLE]`
- **3.7 Deployment Architecture**: Client and FastAPI local server.  
  *Source*: `docs/design/DEPLOYMENT_DIAGRAM.md`. `[FYP-I AVAILABLE]`

### PART B — ML ENGINEERING & DATASET PIPELINE
- **3.8 Dataset Construction**: 5,148 UCI records, 205 PakScam templates.  
  *Source*: `docs/DATASET_DOCUMENTATION.md` Section 3-5. `[FYP-I AVAILABLE]`
- **3.9 Data Preprocessing**: NFKC normalization and tokenization.  
  *Source*: `docs/DATASET_DOCUMENTATION.md` Section 11. `[FYP-I AVAILABLE]`
- **3.10 Train/Validation/Test Splitting**: Stratified family grouping.  
  *Source*: `docs/DATASET_DOCUMENTATION.md` Section 13-15. `[FYP-I AVAILABLE]`
- **3.11 Model Training Methodology**: DistilBERT fine-tuning pipeline, Mix-C oversampling.  
  *Source*: `docs/DATASET_DOCUMENTATION.md` Section 14. `[FYP-I AVAILABLE]`
- **3.12 Implementation Details**: Kotlin SmsReceiver details, Clean Flutter directories, FastAPI endpoints, heuristic warning card alerts.  
  *Source*: `docs/01_mindshield_architecture_documentation.md` to `09_sms_background_service.md`. `[FYP-I AVAILABLE]`

### PART C — VERIFICATION & EVALUATION METHODOLOGY
- **3.13 Testing Methodology**: Pytest runs, widget tests, regression suit.  
  *Source*: `docs/TESTING_AND_VALIDATION.md` Section 7. `[FYP-I AVAILABLE]`
- **3.14 Evaluation Metrics**: Precision, Recall, F1, FPR, latency setup.  
  *Source*: `docs/DATASET_DOCUMENTATION.md` Section 13. `[FYP-I AVAILABLE]`
- **3.15 Tools and Technologies**: Stack summary.  
  *Source*: `MindShield_FYP_Proposal.docx` Section 20. `[FYP-I AVAILABLE]`
- **3.16 Summary**: Methodology summary. `[MISSING — SHOULD CREATE]`

---

## 10. Chapter 4 Evidence Map
- **4.1 Dataset Statistics**: UCI and PakScam distribution tables.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 1. `[FYP-I AVAILABLE]`
- **4.2 Baseline Model Results**: Baseline model performance metrics.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 2. `[FYP-I AVAILABLE]`
- **4.3 DistilBERT v1 Results (Active serving)**: Test metrics for active model.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 3. `[FYP-I AVAILABLE]`
- **4.4 DistilBERT v3 Results (Research candidate)**: Evaluation metrics for candidate.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 3. `[FYP-I AVAILABLE]`
- **4.5 Model Performance Comparison**: v1 vs v3 comparative table.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 3.1. `[FYP-I AVAILABLE]`
- **4.6 Domain Shift Analysis**: Failure vectors of v1 on transaction texts.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 4.1. `[FYP-I AVAILABLE]`
- **4.7 Latency Benchmarks**: Mean CPU latencies.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 4.2. `[FYP-I AVAILABLE]`
- **4.8 Regression Suite Results**: 14-case regression outcomes.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 3. `[FYP-I AVAILABLE]`
- **4.9 Testing and Validation Results**: 234 Pytest, 5 widget tests, 75% coverage.  
  *Source*: `docs/TESTING_AND_VALIDATION.md` Section 7.6. `[FYP-I AVAILABLE]`
- **4.10 Discussion of Findings**: Contextual analysis.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 4. `[FYP-I AVAILABLE]`
- **4.11 Limitations**: Dataset bounds, unencrypted HTTP, heuristic highlights.  
  *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 6. `[FYP-I AVAILABLE]`
- **4.12 Summary**: Results summary. `[MISSING — SHOULD CREATE]`

---

## 11. Chapter 5 Evidence Map
- **5.1 Summary of FYP-I Achievements**: Summary of completed requirements.  
  *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 2. `[FYP-I AVAILABLE]`
- **5.2 Achievement of Objectives**: Status mappings of proposal objectives.  
  *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 3. `[FYP-I AVAILABLE]`
- **5.3 Contributions**: ML, software engineering, and security contributions.  
  *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 5-7. `[FYP-I AVAILABLE]`
- **5.4 Limitations**: Data sizes, HTTP, and heuristic constraints.  
  *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 8. `[FYP-I AVAILABLE]`
- **5.5 Recommendations**: Refactoring recommendations.  
  *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 9. `[FYP-I AVAILABLE]`
- **5.6 FYP-II Scope and Future Directions**: Multilingual training, 5-class tactical modeling, true perturbation LIME, local ONNX, secure JWT endpoints, larger Pakistani corpus (5,000+ texts).  
  *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 10, `docs/FYP1_ACHIEVEMENTS_VS_FYP2.md`. `[COMBINED]`
- **5.7 Summary**: Chapter 5 summary. `[MISSING — SHOULD CREATE]`

---

## 12. References Plan
- **Current Count**: 10 documented references.
- **Verdict**: `[SUPERVISOR CONFIRMATION REQUIRED — REFERENCE EXPANSION]`
- **Acquisition Targets (Legitimate/Scholarly)**:
  - *SMS Spam/Smishing*: Almeida et al. [1], Cormack [10].
  - *Transformers/BERT*: Devlin et al. [2], Sanh et al. [3], Wolf et al. [8].
  - *Explainable AI*: Ribeiro et al. [4], Lundberg & Lee [5].
  - *South Asian Cybersecurity / Transliteration*: PTA Annual Reports [9], research papers on Roman Urdu tokenization/sentiment analysis (needs expansion).
- *Strict Rule*: Do NOT add fabricated citations or invent paper titles.

---

## 13. Appendices Plan
- **Appendix A — Test Case Matrix**: Mapped to `docs/TEST_CASE_MATRIX.md`. `[FYP-I AVAILABLE]`
- **Appendix B — API Endpoint Specifications**: Mapped to `docs/SRS.md` Section 11. `[FYP-I AVAILABLE]`
- **Appendix C — Dataset Sample Templates**: Mapped to `docs/DATASET_DOCUMENTATION.md`. `[FYP-I AVAILABLE]`
- **Appendix D — Regression Suite Cases**: Mapped to `backend/tests/test_ml_regression.py`. `[FYP-I AVAILABLE]`
- **Appendix E — Repository Structure**: Tree directory map. `[MISSING — SHOULD CREATE]`
- **Appendix Formatting & Numbering**: `[SUPERVISOR CONFIRMATION REQUIRED]`

---

## 14. Figure Inventory
- **Figure 3-1**: System Architecture Diagram (System design block diagram) — *Source*: `docs/design/SYSTEM_ARCHITECTURE.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-2**: Use Case Diagram (Actor relations) — *Source*: `docs/design/USE_CASE_DIAGRAM.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-3**: ER Diagram (SQLite schema) — *Source*: `docs/design/ERD.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-4**: DFD Level 0 (High-level flows) — *Source*: `docs/design/DFD_LEVEL_0.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-5**: DFD Level 1 (Sub-system flows) — *Source*: `docs/design/DFD_LEVEL_1.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-6**: Sequence Diagram (Message analysis timeline) — *Source*: `docs/design/SEQUENCE_DIAGRAM.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-7**: Deployment Architecture Diagram (Hardware/Node setup) — *Source*: `docs/design/DEPLOYMENT_DIAGRAM.md` `[FYP-I AVAILABLE — Mermaid]`
- **Figure 3-8 to 3-16**: Mobile UI Screenshots (9 screens: Splash, Permissions, Onboarding, Inbox Thread List, Message Details, Threat Badge Highlights, Quarantined Folder, Settings, Analytics Dashboard) — *Source*: Client running UI. `[MISSING — SHOULD CREATE]`
- **Figure 4-1**: Dataset Distribution Chart (Bar chart of labels across sets) — *Source*: Dataset counts. `[MISSING — SHOULD CREATE]`
- **Figure 4-2**: Confusion Matrix v1 (Active model heatmap) — *Source*: `v3_evaluation_results.json` performance. `[MISSING — SHOULD CREATE]`
- **Figure 4-3**: Confusion Matrix v3 (Quarantined model heatmap) — *Source*: `v3_evaluation_results.json` performance. `[MISSING — SHOULD CREATE]`
- **Figure 4-4**: v1 vs v3 Performance Comparison (Grouped bar chart: F1, FPR, Recall) — *Source*: Evaluation metrics. `[MISSING — SHOULD CREATE]`
- **Figure 4-5**: Latency Comparison Chart (CPU latency comparison) — *Source*: Latency benchmarks. `[MISSING — SHOULD CREATE]`

---

## 15. Table Inventory
- **Table 2-1**: Feature comparison matrix (MindShield vs existing systems) — *Source*: `docs/LITERATURE_REVIEW.md` Section 9.1. `[FYP-I AVAILABLE]`
- **Table 3-1**: Functional requirements summary — *Source*: `docs/SRS.md` Section 7. `[FYP-I AVAILABLE]`
- **Table 3-2**: Non-functional requirements summary — *Source*: `docs/SRS.md` Section 8. `[FYP-I AVAILABLE]`
- **Table 3-3**: SQLite database schema specification — *Source*: `docs/design/ERD.md` Section 2. `[FYP-I AVAILABLE]`
- **Table 3-4**: API Endpoint parameters and contracts — *Source*: `docs/SRS.md` Section 11. `[FYP-I AVAILABLE]`
- **Table 3-5**: Tools and technologies stack — *Source*: Proposal Section 20. `[FYP-I AVAILABLE]`
- **Table 4-1**: Dataset inventory (volume details) — *Source*: `docs/DATASET_DOCUMENTATION.md` Section 3. `[FYP-I AVAILABLE]`
- **Table 4-2**: Model performance comparison matrix (v1 vs v3 details) — *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 3.1. `[FYP-I AVAILABLE]`
- **Table 4-3**: Latency benchmarks (CPU execution logs) — *Source*: `docs/RESULTS_AND_DISCUSSION.md` Section 4.2. `[FYP-I AVAILABLE]`
- **Table 4-4**: Test case matrix summary (passing statistics) — *Source*: `docs/TEST_CASE_MATRIX.md` summary. `[FYP-I AVAILABLE]`
- **Table 5-1**: Project objectives fulfillment status mapping — *Source*: `docs/CONCLUSION_AND_RECOMMENDATIONS.md` Section 3. `[FYP-I AVAILABLE]`

---

## 16. Missing Evidence
The following must be generated/captured before final thesis compilation:
- **PNG Diagrams**: Convert Figures 3-1 through 3-7 from Mermaid notation to high-resolution PNG images. `[MISSING — SHOULD CREATE]`
- **UI Screenshots**: Capture 9 screen screenshots from a running instance of the Flutter client. `[MISSING — SHOULD CREATE]`
- **Plot Charts**: Generate Figures 4-1 to 4-5 using matplotlib or similar plotting tools. `[MISSING — SHOULD CREATE]`
- **Repository Structure Appendix**: Compile the final repository directory map. `[MISSING — SHOULD CREATE]`

---

## 17. FYP-I vs FYP-II Boundary
- **FYP-I Scope (Locked and Completed)**: Clean Flutter front-end interface, native Kotlin BroadcastReceiver receiver hooks (verification device-dependent), single-table SQLite storage cache, unencrypted local loopback HTTP transit, local FastAPI backend server, fine-tuned DistilBERT binary classification serving model (`v1`), candidate model evaluations (`v3`), 205-template Pakistani SMS dataset, and rule-based heuristic highlights warning card UI.
- **FYP-II Scope (Deferred Future Work)**: Multilingual Transformer model fine-tuning (XLM-RoBERTa), 5-class psychological manipulation categorization (URG, AUTH, FEAR, REW, SEC), true runtime perturbation-based LIME model explanations, secure payloads (HTTPS transit and JWT authentication), local ONNX mobile compiled inference, and large-scale (5,000+ records) real-world Pakistani SMS collection.

---

## 18. Forbidden / Unsafe Academic Claims
Every section must strictly avoid these claims:
- **"conversational UI", "AI chatbot", "conversational assistant"**: Prohibited. The client uses a thread-based SMS inbox interface.
- **"Large-scale Pakistani dataset"**: Prohibited. The custom dataset contains 205 synthetic templates.
- **"Production-ready security system"**: Prohibited. Communication is unencrypted HTTP, and authentication is missing.
- **"True runtime LIME"**: Prohibited. Explainability calculations at runtime are rule-based heuristics; perturbation LIME calculations are deferred due to latency bounds.
- **"v3 is the serving model"**: Prohibited. `v3` remains quarantined.
- **"14 cases are an independent test set"**: Prohibited. The 14 regression cases represent a benchmark testing suite.
- **"Sub-60 ms end-to-end response time"**: Prohibited. Benchmarks represent model CPU inference execution only; network overheads are unverified.

---

## 19. Citation and Evidence Rules
- **Citation Format**: Numbered IEEE brackets `[N]`. Sequential numbering. No fabricated citations.
- **Evidence Integrity**: All quantitative metrics, performance stats, and latency benchmarks must copy their exact values from [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md) without rounding, smoothing, or inflation.

---

## 20. Thesis Writing Order
To avoid reference errors and streamline composition:
1. **Chapter 2 (Literature Review)**: Copy and refine `LITERATURE_REVIEW.md` content.
2. **Chapter 3 (Methodology — Part A & B)**: Compile system designs, databases, datasets, and preprocessing steps.
3. **Chapter 4 (Results)**: Input baseline, v1, v3, and latency performance matrices.
4. **Chapter 5 (Conclusion)**: Document achievements and future roadmaps.
5. **Chapter 1 (Introduction)**: Write after completing Chapters 2-5.
6. **Front Matter**: Compile title pages, declarations, abstracts, and abbreviations.
7. **Chapter 3 (Methodology — Part C)**: Complete testing and verification tables.
8. **Appendices & References**: Consolidate and format reference lists.

---

## 21. Final Pre-Writing Gate

- **Is the official template identified?**  
  Yes (`docs/thesis-template/FYP_Thesis_Template_IMCS_2025.docx`).
- **Is the five-chapter structure locked?**  
  Yes. Chapters 1-5 follow template guidelines, using a three-part division in Chapter 3.
- **Are team names and roll numbers verified?**  
  Yes. Junaid Ahmed (2K23/CSM/54), Kalpna (2K23/CSM/55), Mudasar Ali (2K23/CSM/81) verified against proposal database.
- **Is the supervisor verified?**  
  Yes (Mr. Zubair Kandhro).
- **Is every thesis section mapped to evidence?**  
  Yes (detailed in Chapters 1-5 maps).
- **Are FYP-I/FYP-II boundaries enforced?**  
  Yes (boundary splits and forbidden claims are locked).
- **Are figure/table numbering conventions verified?**  
  Yes. Chapter-based hyphenated style used (e.g. `Figure 3-1`, `Table 4-1`).
- **Are missing figures identified?**  
  Yes (7 Mermaid conversions, 9 screenshots, 5 plot charts).
- **Are missing tables identified?**  
  Yes (11 tables mapped).
- **Are reference gaps identified?**  
  Yes (10 references present; expansion mapped under supervisor confirmation).
- **Are appendix rules identified?**  
  Yes (Appendices A-E mapped under supervisor confirmation).
- **Are prohibited claims documented?**  
  Yes (7 forbidden claims listed).
- **Pre-Writing Validation Verdict**: `[PASSED]`
  *MindShield FYP-I Thesis Writing Foundation is fully established and locked.*
