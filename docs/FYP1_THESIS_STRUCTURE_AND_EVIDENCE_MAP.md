# MindShield — FYP-I Thesis Structure & Evidence Map

> **Document ID**: `docs/FYP1_THESIS_STRUCTURE_AND_EVIDENCE_MAP.md`  
> **Phase**: FYP-I Thesis Planning  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  
> **Scope Lock**: [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md)  

---

## 1. Official Report Requirements Discovered

### 1.1 University-Provided Templates
**No official university thesis template, formatting guide, or departmental style sheet was found in the repository.**

The only `.docx` file is the approved proposal ([`docs/MindShield_FYP_Proposal.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP_Proposal.docx)). No `.tex`, `.pdf` template, or Word `.dotx` template exists.

### 1.2 Requirements Inferred from the Proposal
The proposal (Section 21 — Expected Deliverables, FYP-II) explicitly lists:
> *"Complete final project report / thesis containing evaluation metrics, confusion matrices, and user-acceptance reports."*

The thesis defense checklist ([`Thesis_Defense_Checklist.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/Thesis_Defense_Checklist.md)) references:
- 3 bound printed copies of the Thesis Document
- 3 copies of an Executive Summary
- A post-defense git tag (`v1.0-thesis-defense`)

### 1.3 Formatting Standards — Unknown
The following are **not specified** in the repository and must be confirmed with the supervisor or department:

| Requirement | Status |
|---|---|
| Page margins | **UNKNOWN** |
| Font family and size | **UNKNOWN** |
| Line spacing | **UNKNOWN** |
| Citation style (APA / IEEE / Harvard) | **Inferred IEEE** (proposal uses numbered `[1]` style) |
| Title page format | **UNKNOWN** |
| Declaration / certificate pages | **UNKNOWN** |
| Approval / signature page | **UNKNOWN** |
| Abstract word limit | **UNKNOWN** |
| Table of contents format | **UNKNOWN** |
| List of figures / tables requirement | **UNKNOWN** |
| Appendix format | **UNKNOWN** |
| Page numbering style | **UNKNOWN** |
| Binding requirements | **UNKNOWN** (checklist mentions "3 bound copies") |

> [!IMPORTANT]
> You must obtain the official University of Sindh FYP report template from your supervisor or department before formatting the final thesis. The structure below is a standard CS/IT FYP report structure and should be adapted to match any official template.

---

## 2. Proposed Chapter Structure

The following structure follows a standard Pakistani CS/IT FYP-I report convention, mapped to MindShield's existing documentation evidence.

### Front Matter
- Title Page
- Declaration of Originality
- Certificate of Approval (Supervisor + Examiner signatures)
- Dedication (optional)
- Acknowledgments
- Abstract
- Table of Contents
- List of Figures
- List of Tables
- List of Abbreviations

### Chapter 1 — Introduction
- 1.1 Background and Motivation
- 1.2 Problem Statement
- 1.3 Research Questions
- 1.4 Aims and Objectives
- 1.5 Scope and Limitations
- 1.6 Novelty of the Proposed System
- 1.7 SDG Alignment
- 1.8 Report Organization

### Chapter 2 — Literature Review
- 2.1 SMS Spam and Smishing Detection
- 2.2 NLP-Based Cybersecurity
- 2.3 Traditional Machine Learning Approaches
- 2.4 Deep Learning and Transformer-Based Approaches
- 2.5 BERT and DistilBERT for Text Classification
- 2.6 Explainable AI (XAI) and LIME
- 2.7 Mobile-Based Cybersecurity Systems
- 2.8 Existing Systems and Comparative Analysis
- 2.9 Research Gap Analysis
- 2.10 Summary

### Chapter 3 — Requirements Specification
- 3.1 Functional Requirements
- 3.2 Non-Functional Requirements
- 3.3 Use Case Specifications
- 3.4 Data Requirements
- 3.5 API Requirements
- 3.6 ML Requirements
- 3.7 Security and Privacy Requirements
- 3.8 Hardware and Software Requirements

### Chapter 4 — System Design and Architecture
- 4.1 System Architecture Overview
- 4.2 Component Diagram
- 4.3 Data Flow Diagrams (Level 0 and Level 1)
- 4.4 Sequence Diagrams
- 4.5 Entity Relationship Diagram (ERD)
- 4.6 Deployment Diagram
- 4.7 API Data Flow
- 4.8 Design Decisions and Traceability

### Chapter 5 — Dataset and Experimental Methodology
- 5.1 Dataset Sources
- 5.2 UCI SMS Spam Collection
- 5.3 PakScam-SMS Dataset Construction
- 5.4 Data Cleaning and Preprocessing
- 5.5 Train / Validation / Test Splitting
- 5.6 Oversampling Strategy
- 5.7 Data Leakage Prevention
- 5.8 Evaluation Metrics

### Chapter 6 — Implementation
- 6.1 Android Native SMS Interception (Kotlin)
- 6.2 Flutter Client Architecture
- 6.3 Local SQLite Persistence
- 6.4 FastAPI Backend
- 6.5 Model Loading and Inference Pipeline
- 6.6 Heuristic Explainability Highlights
- 6.7 Background Synchronization Workflow
- 6.8 Tools and Technologies

### Chapter 7 — Testing and Validation
- 7.1 Testing Strategy
- 7.2 Backend Unit and Integration Tests
- 7.3 Frontend Widget Tests
- 7.4 ML Regression Testing
- 7.5 Test Case Matrix
- 7.6 Coverage Analysis
- 7.7 Testing Limitations

### Chapter 8 — Results and Discussion
- 8.1 Dataset Statistics
- 8.2 Baseline Model Results
- 8.3 DistilBERT v1 Results
- 8.4 DistilBERT v3 Research Candidate Results
- 8.5 Domain Shift Analysis
- 8.6 Latency Benchmarks
- 8.7 Regression Suite Results
- 8.8 v1 vs v3 Comparison
- 8.9 Discussion of Findings
- 8.10 Limitations

### Chapter 9 — Conclusion and Recommendations
- 9.1 Summary of FYP-I Achievements
- 9.2 Achievement of Objectives
- 9.3 Contributions
- 9.4 Limitations
- 9.5 Recommendations
- 9.6 FYP-II Scope and Future Work

### Chapter 10 — References

### Appendices
- Appendix A — Test Case Matrix
- Appendix B — API Endpoint Specifications
- Appendix C — Dataset Sample Templates
- Appendix D — Regression Suite Cases
- Appendix E — Code Repository Structure

---

## 3. Existing-Document-to-Chapter Mapping

| Thesis Chapter | Existing Source Document | Evidence Status |
|---|---|---|
| **Ch 1 — Introduction** | `MindShield_FYP_Proposal.docx` (Sections 1, 5, 6, 7, 8, 9, 10, 12) | Available (extract and rewrite) |
| **Ch 2 — Literature Review** | `docs/LITERATURE_REVIEW.md` | Complete (13 sections, 10 references) |
| **Ch 3 — Requirements** | `docs/SRS.md` | Complete (20 sections, 10 use cases, 8 FRs) |
| **Ch 4 — System Design** | `docs/SYSTEM_DESIGN.md` + 13 files in `docs/design/` | Complete (Mermaid diagrams for all major views) |
| **Ch 5 — Dataset** | `docs/DATASET_DOCUMENTATION.md` | Complete |
| **Ch 6 — Implementation** | `docs/01_mindshield_architecture_documentation.md` through `docs/09_sms_background_service.md`, `docs/ML_SYSTEM_DOCUMENTATION.md`, `backend/docs/` | Available (needs consolidation into narrative prose) |
| **Ch 7 — Testing** | `docs/TESTING_AND_VALIDATION.md`, `docs/TEST_CASE_MATRIX.md` | Complete |
| **Ch 8 — Results** | `docs/RESULTS_AND_DISCUSSION.md` | Complete |
| **Ch 9 — Conclusion** | `docs/CONCLUSION_AND_RECOMMENDATIONS.md` | Complete |
| **Ch 10 — References** | `LITERATURE_REVIEW.md` (Section 13), Proposal (Section 26) | Partial (10 references; may need expansion) |
| **Front Matter** | None | Not yet created |
| **Appendices** | `TEST_CASE_MATRIX.md`, `SRS.md` API section, dataset samples | Partial (raw content exists, not formatted as appendices) |

---

## 4. Evidence Available for Every Chapter

### Chapter 1 — Introduction
| Item | Source | Status |
|---|---|---|
| Problem statement text | Proposal Section 5 | Available |
| Motivation / background | Proposal Sections 6.1-6.5 | Available |
| Research questions | Proposal Section 7 (RQ1-RQ4) | Available |
| Scope definition | Proposal Section 10 | Available |
| Novelty statement | Proposal Section 8 | Available |
| SDG alignment table | Proposal Section 12 | Available |

### Chapter 2 — Literature Review
| Item | Source | Status |
|---|---|---|
| Full narrative prose | `LITERATURE_REVIEW.md` | Available |
| Comparative system matrix | `LITERATURE_REVIEW.md` Section 9.1 | Available |
| References (10 entries) | `LITERATURE_REVIEW.md` Section 13 | Available |

### Chapter 3 — Requirements
| Item | Source | Status |
|---|---|---|
| 8 functional requirements | `SRS.md` Section 7 | Available |
| 5 non-functional categories | `SRS.md` Section 8 | Available |
| 10 use case specifications | `SRS.md` Section 9 | Available |
| API contracts | `SRS.md` Section 11 | Available |
| Requirements traceability | `SRS.md` Section 15 | Available |

### Chapter 4 — System Design
| Item | Source | Status |
|---|---|---|
| System architecture (Mermaid) | `SYSTEM_ARCHITECTURE.md` | Available |
| Use case diagram (Mermaid) | `USE_CASE_DIAGRAM.md` | Available |
| DFD Level 0 (Mermaid) | `DFD_LEVEL_0.md` | Available |
| DFD Level 1 (Mermaid) | `DFD_LEVEL_1.md` | Available |
| ERD (Mermaid) | `ERD.md` | Available |
| Sequence diagrams (Mermaid) | `SEQUENCE_DIAGRAM.md` | Available |
| Component diagram (Mermaid) | `COMPONENT_DIAGRAM.md` | Available |
| Deployment diagram (Mermaid) | `DEPLOYMENT_DIAGRAM.md` | Available |
| API data flow (Mermaid) | `API_DATA_FLOW.md` | Available |

### Chapter 5 — Dataset
| Item | Source | Status |
|---|---|---|
| Dataset inventory and volumes | `DATASET_DOCUMENTATION.md` Sections 3-5 | Available |
| Linguistic characteristics | `DATASET_DOCUMENTATION.md` Section 6 | Available |
| Splitting methodology | `DATASET_DOCUMENTATION.md` Section 13 | Available |
| Leakage prevention | `DATASET_DOCUMENTATION.md` Section 15 | Available |

### Chapter 6 — Implementation
| Item | Source | Status |
|---|---|---|
| Architecture overview | `docs/01_mindshield_architecture_documentation.md` | Available |
| Permissions module | `docs/03_permissions_module_documentation.md` | Available |
| Inbox module | `docs/04_inbox_module_documentation.md` | Available |
| Analysis module | `docs/05_analysis_module_documentation.md` | Available |
| Spam folder | `docs/06_spam_folder.md` | Available |
| History module | `docs/07_history_module.md` | Available |
| Settings module | `docs/08_settings_module.md` | Available |
| SMS background service | `docs/09_sms_background_service.md` | Available |
| ML system documentation | `docs/ML_SYSTEM_DOCUMENTATION.md` | Available |
| Backend setup docs | `backend/docs/01_Backend_Setup.md` through `backend/docs/10_Production_Inference.md` | Available |

### Chapter 7 — Testing
| Item | Source | Status |
|---|---|---|
| Testing strategy | `TESTING_AND_VALIDATION.md` | Available |
| Test case matrix | `TEST_CASE_MATRIX.md` | Available |
| Pytest execution results | `analysis_of_testing_validation.md` | Available |
| Flutter test results | `analysis_of_testing_validation.md` | Available |
| Coverage data | `analysis_of_testing_validation.md` | Available |

### Chapter 8 — Results
| Item | Source | Status |
|---|---|---|
| Model performance matrix | `RESULTS_AND_DISCUSSION.md` Section 3.1 | Available |
| Domain shift analysis | `RESULTS_AND_DISCUSSION.md` Section 4.1 | Available |
| Latency benchmarks | `RESULTS_AND_DISCUSSION.md` Section 4.2 | Available |
| v1 vs v3 comparison | `RESULTS_AND_DISCUSSION.md` Section 3 | Available |

### Chapter 9 — Conclusion
| Item | Source | Status |
|---|---|---|
| Achievement summary | `CONCLUSION_AND_RECOMMENDATIONS.md` Section 2 | Available |
| Contributions | `CONCLUSION_AND_RECOMMENDATIONS.md` Sections 5-7 | Available |
| Limitations | `CONCLUSION_AND_RECOMMENDATIONS.md` Section 8 | Available |
| FYP-II scope | `CONCLUSION_AND_RECOMMENDATIONS.md` Section 10 | Available |

---

## 5. Missing Evidence

The following items are **not currently available** in the repository and would strengthen the thesis:

### 5.1 Front Matter (All Missing)
| Item | Status | Priority |
|---|---|---|
| Title page | Not created | **HIGH** |
| Declaration of originality | Not created | **HIGH** |
| Certificate of approval | Not created | **HIGH** |
| Abstract (~250 words) | Not created | **HIGH** |
| Acknowledgments | Not created | MEDIUM |
| List of abbreviations | Not created | MEDIUM |

### 5.2 Rendered Figures (Mermaid Exists, Rendered Images Do Not)
| Figure | Mermaid Source | Rendered Image | Priority |
|---|---|---|---|
| System architecture diagram | `SYSTEM_ARCHITECTURE.md` | Not rendered | **HIGH** |
| Use case diagram | `USE_CASE_DIAGRAM.md` | Not rendered | **HIGH** |
| DFD Level 0 | `DFD_LEVEL_0.md` | Not rendered | **HIGH** |
| DFD Level 1 | `DFD_LEVEL_1.md` | Not rendered | **HIGH** |
| ERD | `ERD.md` | Not rendered | **HIGH** |
| Sequence diagram | `SEQUENCE_DIAGRAM.md` | Not rendered | **HIGH** |
| Component diagram | `COMPONENT_DIAGRAM.md` | Not rendered | MEDIUM |
| Deployment diagram | `DEPLOYMENT_DIAGRAM.md` | Not rendered | MEDIUM |

### 5.3 Application Screenshots
| Screenshot | Status | Priority |
|---|---|---|
| Splash / onboarding screen | Not captured | **HIGH** |
| Permission request screen | Not captured | **HIGH** |
| Inbox thread list | Not captured | **HIGH** |
| Message detail / analysis view | Not captured | **HIGH** |
| Threat warning card with highlights | Not captured | **HIGH** |
| Spam quarantine folder | Not captured | MEDIUM |
| History / logs screen | Not captured | MEDIUM |
| Settings screen | Not captured | MEDIUM |
| Dashboard screen | Not captured | MEDIUM |

### 5.4 ML / Results Figures
| Figure | Status | Priority |
|---|---|---|
| Confusion matrix (v1 on UCI test) | Not generated | **HIGH** |
| Confusion matrix (v1 on PakScam) | Not generated | **HIGH** |
| Confusion matrix (v3 on PakScam) | Not generated | **HIGH** |
| v1 vs v3 bar chart (F1, FPR, Recall) | Not generated | **HIGH** |
| Dataset class distribution bar chart | Not generated | MEDIUM |
| Latency comparison chart (v1 vs v3) | Not generated | MEDIUM |
| UCI vs PakScam performance comparison | Not generated | MEDIUM |
| ROC curve (if data available) | Not generated | LOW |

### 5.5 Other Missing Items
| Item | Status | Priority |
|---|---|---|
| Consolidated reference list | 10 references exist; may need expansion | MEDIUM |
| Tools and technologies table | Available in proposal Table 8 | LOW |
| Gantt chart / timeline | Available in proposal Section 22 | LOW |
| Team member roles table | Available in proposal Section 23 | LOW |

---

## 6. Figures and Tables Required

### 6.1 Minimum Required Figures

| Figure # | Description | Source | Type |
|---|---|---|---|
| Fig 1 | System architecture overview | `SYSTEM_ARCHITECTURE.md` | Mermaid to rendered PNG |
| Fig 2 | Use case diagram | `USE_CASE_DIAGRAM.md` | Mermaid to rendered PNG |
| Fig 3 | DFD Level 0 | `DFD_LEVEL_0.md` | Mermaid to rendered PNG |
| Fig 4 | DFD Level 1 | `DFD_LEVEL_1.md` | Mermaid to rendered PNG |
| Fig 5 | ERD | `ERD.md` | Mermaid to rendered PNG |
| Fig 6 | Sequence diagram (SMS analysis flow) | `SEQUENCE_DIAGRAM.md` | Mermaid to rendered PNG |
| Fig 7 | Deployment diagram | `DEPLOYMENT_DIAGRAM.md` | Mermaid to rendered PNG |
| Fig 8 | Model pipeline diagram | To be created | New diagram |
| Fig 9 | Dataset class distribution | To be generated | Bar chart |
| Fig 10 | v1 vs v3 performance comparison | To be generated | Grouped bar chart |
| Fig 11 | Confusion matrix - v1 on UCI | To be generated | Heatmap |
| Fig 12 | Confusion matrix - v1 on PakScam | To be generated | Heatmap |
| Fig 13 | Confusion matrix - v3 on PakScam | To be generated | Heatmap |
| Fig 14-22 | Application UI screenshots (9 screens) | To be captured | Screenshots |

### 6.2 Minimum Required Tables

| Table # | Description | Source |
|---|---|---|
| Table 1 | Feature comparison (MindShield vs existing systems) | `LITERATURE_REVIEW.md` Section 9.1 |
| Table 2 | Functional requirements summary | `SRS.md` Section 7 |
| Table 3 | Non-functional requirements | `SRS.md` Section 8 |
| Table 4 | SQLite schema specification | `ERD.md` Section 2 |
| Table 5 | Dataset inventory | `DATASET_DOCUMENTATION.md` Section 3 |
| Table 6 | PakScam class distribution | `DATASET_DOCUMENTATION.md` Section 5 |
| Table 7 | Model performance comparison (v1 vs v3) | `RESULTS_AND_DISCUSSION.md` Section 3.1 |
| Table 8 | Latency benchmarks | `RESULTS_AND_DISCUSSION.md` Section 4.2 |
| Table 9 | Test case matrix summary | `TEST_CASE_MATRIX.md` |
| Table 10 | Tools and technologies | Proposal Table 8 |
| Table 11 | API endpoint specifications | `SRS.md` Section 11 |
| Table 12 | FYP-I vs FYP-II boundary | `FYP1_ACHIEVEMENTS_VS_FYP2.md` |

---

## 7. Academic Claim Restrictions

All thesis prose must comply with [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md). The following restrictions are locked:

| Term | Correct Usage | Forbidden Usage |
|---|---|---|
| `distilbert-pakscam-v1` | Active serving / baseline model | — |
| `distilbert-pakscam-v3` | Quarantined research candidate | Active / deployed / production model |
| 205 samples | Localized template-derived corpus | Large-scale Pakistani SMS dataset |
| 14 regression cases | Regression benchmark gating suite | Independent unseen test set |
| 41.95 ms / 57.62 ms | CPU model inference latency | End-to-end latency |
| Highlight cards | Heuristic rule-based indicators | True LIME / perturbation-based LIME |
| HTTP loopback | Current development transport | Secure production channel |
| HTTPS / JWT | FYP-II planned work | Currently implemented |
| Binary classification | Current FYP-I classifier | 5-class active classifier |
| SMS interception | Implemented (device-dependent verification) | Fully verified on all devices |

---

## 8. Recommended Writing Order

Writing order is optimized to avoid forward-reference problems and to maximize reuse of existing documentation:

| Order | Chapter | Rationale |
|---|---|---|
| 1 | Ch 2 — Literature Review | Already complete; copy and adapt from `LITERATURE_REVIEW.md` |
| 2 | Ch 3 — Requirements | Already complete; adapt from `SRS.md` |
| 3 | Ch 4 — System Design | Already complete; adapt from `SYSTEM_DESIGN.md` + design files |
| 4 | Ch 5 — Dataset | Already complete; adapt from `DATASET_DOCUMENTATION.md` |
| 5 | Ch 6 — Implementation | Consolidate from module docs (01-09) + ML docs |
| 6 | Ch 7 — Testing | Already complete; adapt from `TESTING_AND_VALIDATION.md` |
| 7 | Ch 8 — Results | Already complete; adapt from `RESULTS_AND_DISCUSSION.md` |
| 8 | Ch 9 — Conclusion | Already complete; adapt from `CONCLUSION_AND_RECOMMENDATIONS.md` |
| 9 | Ch 1 — Introduction | Write last (requires knowledge of all other chapters) |
| 10 | Front Matter | Abstract, acknowledgments, and lists written after all chapters |
| 11 | Ch 10 — References | Consolidate from all chapters |
| 12 | Appendices | Format supporting material |

---

## 9. Final Thesis Assembly Checklist

- [ ] Obtain official University of Sindh FYP report template from supervisor
- [ ] Confirm citation style (IEEE numbered assumed)
- [ ] Confirm page margins, font, spacing requirements
- [ ] Confirm title page format and required signatures
- [ ] Create title page
- [ ] Create declaration of originality
- [ ] Create certificate of approval page
- [ ] Write acknowledgments
- [ ] Write abstract (~250 words)
- [ ] Create list of abbreviations
- [ ] Render all Mermaid diagrams to PNG images
- [ ] Capture all UI screenshots from running application
- [ ] Generate confusion matrix figures
- [ ] Generate performance comparison charts
- [ ] Generate dataset distribution charts
- [ ] Write Chapter 1 (Introduction)
- [ ] Adapt Chapter 2 (Literature Review) from `LITERATURE_REVIEW.md`
- [ ] Adapt Chapter 3 (Requirements) from `SRS.md`
- [ ] Adapt Chapter 4 (System Design) from design docs
- [ ] Adapt Chapter 5 (Dataset) from `DATASET_DOCUMENTATION.md`
- [ ] Write Chapter 6 (Implementation) from module docs
- [ ] Adapt Chapter 7 (Testing) from `TESTING_AND_VALIDATION.md`
- [ ] Adapt Chapter 8 (Results) from `RESULTS_AND_DISCUSSION.md`
- [ ] Adapt Chapter 9 (Conclusion) from `CONCLUSION_AND_RECOMMENDATIONS.md`
- [ ] Consolidate all references into Chapter 10
- [ ] Format appendices
- [ ] Generate table of contents
- [ ] Generate list of figures
- [ ] Generate list of tables
- [ ] Apply page numbering
- [ ] Cross-check all claims against `FYP1_ACADEMIC_SCOPE_LOCK.md`
- [ ] Final proofreading pass
- [ ] Print 3 bound copies
