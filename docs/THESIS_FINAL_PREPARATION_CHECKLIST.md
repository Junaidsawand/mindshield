# MindShield — Final Thesis Preparation Checklist

> **Document ID**: `docs/THESIS_FINAL_PREPARATION_CHECKLIST.md`  
> **Phase**: FYP-I Thesis Planning & Validation  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  
> **Scope Lock**: [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md)  

---

## FRONT MATTER

- [ ] **Cover page**: Layout matching IMCS 2025 template, including official university crest, department name (Institute of Mathematics and Computer Science), program (BS Computer Science), project title, supervisor name (Mr. Zubair Kandhro), student names/roll numbers, and submission date.
- [ ] **Title page**: Identical metadata layout as cover page, verified for formal spacing.
- [ ] **Certificate**: Filled with correct project title and student names/roll numbers matching proposal spelling.
- [ ] **Declaration**: Originality text matches template exactly, student names/roll numbers checked.
- [ ] **Copyrights**: Jamshoro library permission statement filled out with correct student names.
- [ ] **Dedication**: Personal dedication text written.
- [ ] **Acknowledgements**: Mentions supervisor (Mr. Zubair Kandhro), IMCS department head, and other contributors.
- [ ] **Abstract**: Written within typical word limits (~250 words), highlighting binary smishing detection and local Roman Urdu validation findings (v1 vs v3).
- [ ] **TOC**: Auto-generated from Microsoft Word Heading styles.
- [ ] **List of Tables**: Auto-generated from table captions.
- [ ] **List of Figures**: Auto-generated from figure captions.
- [ ] **Abbreviations**: Contains project terms (e.g. NLP, XAI, SQLite, DFD, ERD, PTA, FIA, API, SMS, roll-number/member notations).

---

## CHAPTER 1 — INTRODUCTION

- [ ] **Structure verified**: Structure matches the five-chapter template format.
- [ ] **Scope claims verified**: Explicitly limits FYP-I to proof-of-concept; defers federated learning, local ONNX, 5-class categorization, and true LIME to FYP-II.
- [ ] **Research questions verified**: RQ1 through RQ4 match the proposal objectives exactly.
- [ ] **Objectives verified**: Mapped to the approved proposal objectives.
- [ ] **Novelty claims verified**: Clearly states active serving baseline is English-centric, with localized Roman Urdu research evaluated in quarantined candidate model.
- [ ] **SDG alignment**: Table mapping to UN SDGs included.

---

## CHAPTER 2 — LITERATURE REVIEW/BACKGROUND

- [ ] **Literature sources verified**: Section 2.1 to 2.10 completed.
- [ ] **References expanded if required**: Verified reference database.
- [ ] **Research gap verified**: Gap analysis explicitly targets Roman Urdu text lack and black-box explanation limits.

---

## CHAPTER 3 — RESEARCH METHODOLOGY

- [ ] **Architecture diagrams**: Figures 3-1 through 3-7 rendered to PNG and inserted.
  - [ ] Figure 3-1: System Architecture Diagram
  - [ ] Figure 3-2: Use Case Diagram
  - [ ] Figure 3-3: ER Diagram
  - [ ] Figure 3-4: DFD Level 0
  - [ ] Figure 3-5: DFD Level 1
  - [ ] Figure 3-6: Sequence Diagram
  - [ ] Figure 3-7: Deployment Diagram
- [ ] **Requirements**: Functional and non-functional requirements match `docs/SRS.md`.
- [ ] **Use cases**: 10 use cases documented.
- [ ] **ERD**: Single-table SQLite database schema mapped.
- [ ] **DFDs**: Information flows mapped across client, SQLite cache, and API.
- [ ] **Sequence diagram**: Interception and backend API classification flow documented.
- [ ] **Deployment diagram**: Deployed client and FastAPI local server mapped.
- [ ] **Dataset methodology**: UCI SMS Spam and custom PakScam-SMS (205 templates) datasets detailed.
- [ ] **Preprocessing**: NFKC normalization and WordPiece tokenization described.
- [ ] **Data splitting**: Stratified template-family grouping strategy detailed (leakage prevention).
- [ ] **Model methodology**: DistilBERT fine-tuning pipeline and Mix-C oversampling detailed.
- [ ] **Implementation**: Kotlin BroadcastReceiver, Clean Flutter client structure, and FastAPI service described.
- [ ] **Testing methodology**: Pytest backend tests, widget frontend tests, and regression suite (14 cases) documented.

---

## CHAPTER 4 — RESULTS AND DISCUSSION

- [ ] **Dataset statistics**: Sample volumes verified (5,148 UCI, 205 PakScam templates).
- [ ] **Baseline results**: UCI baseline model outcomes included.
- [ ] **v1 results**: Active serving model test performance documented (UCI F1: 96.00%, Pak HAM FPR: 93.10%, Pak SPAM Recall: 98.11%).
- [ ] **v3 research candidate results**: Quarantined candidate performance documented (UCI F1: 95.08%, Pak HAM FPR: 3.45%, Pak SPAM Recall: 100.00%).
- [ ] **Comparison**: Comparative table of v1 vs v3 included.
- [ ] **Domain shift analysis**: Detailed description of v1 transaction alert failures.
- [ ] **Latency**: Model CPU inference latency benchmarked (v1: 41.95 ms, v3: 57.62 ms), clearly labeled as non-end-to-end.
- [ ] **Regression testing**: 14-case regression outcomes documented (v1: 5/14, v3: 13/14).
- [ ] **Testing results**: 234 Pytest runs (75% coverage) and 5 Flutter widget tests documented.
- [ ] **Limitations**: Clear discussion of small localized corpus, HTTP development transport, and heuristic highlighting.
- [ ] **Discussion**: Direct comparison of model behaviors.

---

## CHAPTER 5 — CONCLUSION AND FUTURE DIRECTIONS

- [ ] **FYP-I achievements**: Summary of completed system objectives.
- [ ] **Objective achievement**: Detailed mapping table showing PROP-OBJ achievement states.
- [ ] **Contributions**: Engineering, Machine Learning, and Security contributions catalogued.
- [ ] **Limitations**: Detailed dataset and system limitations.
- [ ] **Recommendations**: Next-step code improvements.
- [ ] **FYP-II future work**: Multilingual XLM-RoBERTa, 5-class categorization, HTTPS/JWT, local ONNX, and true LIME explicitly deferred to FYP-II.

---

## FINAL ASSEMBLY & FORMATTING

- [ ] **Figures numbered correctly**: Hyphenated chapter-based numbering format checked (`Figure 3-1`, `Figure 4-1`).
- [ ] **Tables numbered correctly**: Hyphenated chapter-based numbering format checked (`Table 2-1`, `Table 3-1`).
- [ ] **References verified**: IEEE numbering format matches text citations.
- [ ] **Appendices verified**: Appendices A through E included with correct supporting files.
- [ ] **Formatting verified against DOCX**: A4 size, 1.5 in left margin, 1.0 in top/right/bottom margins, Times New Roman 12 pt justified, 1.5 line spacing, and section breaks.
- [ ] **No unsupported claims**: No claims of "large-scale dataset", "conversational AI", "production deployment", or "true LIME runtime calculations".
- [ ] **No FYP-II work presented as completed**: Scope boundaries strictly respected.
- [ ] **Team-member information verified**: Junaid Ahmed (2K23/CSM/54), Kalpna (2K23/CSM/55), and Mudasar Ali (2K23/CSM/81) spellings and roll numbers match proposal.
- [ ] **Supervisor information verified**: Mr. Zubair Kandhro.
