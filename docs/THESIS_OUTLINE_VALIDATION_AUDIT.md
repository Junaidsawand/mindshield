# MindShield — Thesis Outline Validation & Template Compliance Audit

> **Document ID**: `docs/THESIS_OUTLINE_VALIDATION_AUDIT.md`  
> **Phase**: FYP-I Thesis Planning & Validation  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  
> **Scope Lock**: [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md)  
> **Thesis Outline**: [`docs/THESIS_MASTER_OUTLINE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/THESIS_MASTER_OUTLINE.md)  
> **DOCX Template**: `docs/thesis-template/FYP_Thesis_Template_IMCS_2025.docx`  

---

## 1. Executive Verdict

The current outline ([`docs/THESIS_MASTER_OUTLINE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/THESIS_MASTER_OUTLINE.md)) is **fully validated** and ready for the future writing phase. It complies with the official departmental template structure, implements the required corrections, and strictly respects the academic boundaries of the `FYP-I` scope lock.

---

## 2. Template Compliance Assessment

### 2.1 Front-Matter Compliance
**Status**: `[PASS]`
The proposed front matter matches the departmental template's structure exactly, in the correct order:
1. Cover Page
2. Title Page
3. Certificate
4. Declaration
5. Copy Rights
6. Dedication
7. Acknowledgements
8. Abstract
9. Table of Contents
10. List of Tables
11. List of Figures
12. Abbreviations

### 2.2 Five-Chapter Compliance
**Status**: `[PASS]`
The outline strictly adheres to the departmental five-chapter structure:
- **Chapter 1**: INTRODUCTION
- **Chapter 2**: LITERATURE REVIEW/BACKGROUND
- **Chapter 3**: RESEARCH METHODOLOGY
- **Chapter 4**: RESULTS AND DISCUSSION
- **Chapter 5**: CONCLUSION AND FUTURE DIRECTIONS
- **REFERENCES** (following Chapter 5)

### 2.3 Template-Level Structural Anomalies
**Status**: `[SUPERVISOR CONFIRMATION REQUIRED]`
- **Chapter 3 Template Copy-Paste Typo**: In the official DOCX template, Chapter 3 contains placeholder sections repeating Chapter 1's headings ("3.1 Motivation", "3.2 Contributions of the thesis", "3.3 Structure of the thesis"). In our outline, we replaced these placeholders with the actual structural methodology (Architecture, Requirements, Dataset, Preprocessing, Training, etc.). This is correct and necessary, but the supervisor should be notified of the template placeholder repetition.
- **Reference Section Typo**: The template titles the reference section as "REFRENCES" (missing the "E"). The final thesis should correct this to "REFERENCES" unless the department strictly mandates copying typos.

---

## 3. Project Member & Metadata Integration

### 3.1 Verification from Approved Proposal
**Status**: `[PASS]`
Student names, roll numbers, and supervisor details were extracted directly from Table 0 and Table 10 of the approved proposal (`docs/MindShield_FYP_Proposal.docx`):
- **Team Leader**: Junaid Ahmed (Roll No: **2K23/CSM/54**)
- **Team Member 2**: Kalpna (Roll No: **2K23/CSM/55**)
- **Team Member 3**: Mudasar Ali (Roll No: **2K23/CSM/81**)
- **Supervisor**: Mr. Zubair Kandhro
- **Department**: Institute of Mathematics and Computer Science, University of Sindh, Jamshoro
- **Degree**: Bachelor of Science in Computer Science (BSCS)
- **Program / Section**: BS Computer Science (8th Semester, Final Year) – Section: PM (Pre-Medical section)

### 3.2 Member Name Discrepancy Log
The following discrepancies exist between the informal user prompt names and the official proposal database names, and **must be corrected** to preserve academic alignment:

| User Prompt Wording | Official Proposal Wording | Resolution |
|---|---|---|
| Junaid Ahmad | **Junaid Ahmed** | Use Junaid Ahmed (Roll: 2K23/CSM/54) |
| Mudassar Ali | **Mudasar Ali** | Use Mudasar Ali (Roll: 2K23/CSM/81) |
| Kalpana | **Kalpna** | Use Kalpna (Roll: 2K23/CSM/55) |

---

## 4. Scope-Lock Verification

The outline was checked against the authoritative boundaries in [`docs/FYP1_ACADEMIC_SCOPE_LOCK.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/FYP1_ACADEMIC_SCOPE_LOCK.md):

| Outline Section | Stated Claim / Content | Scope Lock Status | Verdict & Wording |
|---|---|---|---|
| **1.3 RQ3** | "thread-based SMS inbox interface" | `[CORRECTED]` | **Corrected**: Removed "conversational UI" to prevent examiner confusion. |
| **1.6** | "Evaluation of Roman Urdu/multilingual optimization strategies" | `[CORRECTED]` | **Corrected**: Novelty statements updated to clearly state that v1 serving model is English-centric, with Urdu optimization evaluated on quarantined v3 candidate. |
| **3.8** | "PakScam-SMS dataset (205 unique templates)" | `[PASS]` | Correctly lists 205 unique templates. Avoids using "large-scale Pakistani dataset." |
| **3.12** | "Heuristic explainability highlights" | `[PASS]` | Correctly identifies highlights as rule-based heuristics rather than active runtime LIME. |
| **4.3 & 4.4** | Model Performance Metrics (v1 vs v3) | `[PASS]` | Numbers match the verified evaluation logs exactly (v1: 93.10% FPR, 98.11% recall; v3: 3.45% FPR, 100.00% recall). |
| **4.7** | Latency Benchmarks | `[PASS]` | Correctly specifies CPU inference latency (v1: 41.95 ms, v3: 57.62 ms) and highlights that this is *not* end-to-end application response latency. |
| **4.8** | Regression Suite Results | `[PASS]` | Correctly specifies that the 14-case regression suite is *not* an independent test set. |
| **5.6** | Future Directions (XLM-RoBERTa, 5-class categorization, true LIME, HTTPS/JWT, ONNX, etc.) | `[FYP-II REQUIRED]` | Correctly classifies all unverified or advanced security features as FYP-II deferred tasks. |

---

## 5. Chapter-by-Chapter Audit

### Chapter 1 — Introduction
- **Verdict**: `[PASS]`
- **Status**: Corrected. RQ3 renamed to "thread-based SMS inbox interface" and novelty claims aligned with v1/v3 limits.

### Chapter 2 — Literature Review/Background
- **Verdict**: `[PASS]`
- **Status**: Complete. Maps cleanly to existing audited literature review documentation.

### Chapter 3 — Research Methodology
- **Verdict**: `[PASS]`
- **Status**: Corrected. Chapter 3 organized into three distinct parts:
  - **PART A** — SOFTWARE ENGINEERING & SYSTEM DESIGN
  - **PART B** — ML ENGINEERING & DATASET PIPELINE
  - **PART C** — VERIFICATION & EVALUATION METHODOLOGY

### Chapter 4 — Results and Discussion
- **Verdict**: `[PASS]`
- **Status**: Complete. Performance matrices, latency numbers, and testing outputs match repository benchmarks exactly.

### Chapter 5 — Conclusion and Future Directions
- **Verdict**: `[PASS]`
- **Status**: Complete. Clean mapping of achievements and deferred FYP-II roadmap items.

---

## 6. Figures and Tables Audit

Hyphenated chapter-based numbering format (`Figure 3-1`, `Figure 4-1`) is **fully enforced** in the outline:

| Figure # | Description | Status | Source |
|---|---|---|---|
| **Figure 3-1** | System Architecture Diagram | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-2** | Use Case Diagram | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-3** | ER Diagram (SQLite schema) | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-4** | DFD Level 0 | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-5** | DFD Level 1 | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-6** | Sequence Diagram | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-7** | Deployment Diagram | `[FYP-I AVAILABLE]` | Render Mermaid to PNG |
| **Figure 3-8 to 3-16** | Mobile UI Screenshots (9 screens) | `[MISSING EVIDENCE]` | Capture screenshots from device/emulator |
| **Figure 4-1** | Dataset Distribution Chart | `[MISSING EVIDENCE]` | Compile bar chart from CSV data |
| **Figure 4-2** | Confusion Matrix v1 | `[MISSING EVIDENCE]` | Generate heatmap from json outputs |
| **Figure 4-3** | Confusion Matrix v3 | `[MISSING EVIDENCE]` | Generate heatmap from json outputs |
| **Figure 4-4** | v1 vs v3 Performance Bar Chart | `[MISSING EVIDENCE]` | Generate grouped bar chart |
| **Figure 4-5** | Latency Comparison Bar Chart | `[MISSING EVIDENCE]` | Generate bar chart comparing means/maxes |

---

## 7. References Audit
- **Count**: 10 references exist.
- **Verdict**: `[SUPERVISOR CONFIRMATION REQUIRED]`
- **Details**: No explicit minimum reference count was identified in the departmental template. However, 10 references are likely insufficient for a BSCS thesis, and supervisor feedback is required regarding database expansion.

---

## 8. Appendices Audit
The proposed appendices are justified:
- **Appendix A — Test Case Matrix**: `[FYP-I AVAILABLE]` (from `docs/TEST_CASE_MATRIX.md`).
- **Appendix B — API Endpoint Specifications**: `[FYP-I AVAILABLE]` (from `docs/SRS.md` Section 11).
- **Appendix C — Dataset Sample Templates**: `[FYP-I AVAILABLE]` (from `docs/DATASET_DOCUMENTATION.md`).
- **Appendix D — Regression Suite Cases**: `[FYP-I AVAILABLE]` (from `backend/tests/test_ml_regression.py`).
- **Appendix E — Repository Structure**: `[MISSING EVIDENCE]` (needs compilation).
- **Appendix Formatting & Numbering**: `[SUPERVISOR CONFIRMATION REQUIRED]` (not explicitly defined in the departmental template).

---

## 9. Supervisor Confirmation Items
1. Confirm if the template's copy-paste duplication of headings in Chapter 3 should be ignored (as proposed in our structure).
2. Confirm if the reference count (10) must be expanded to meet departmental standards.
3. Confirm if the spelling of "REFRENCES" should be corrected to "REFERENCES".
4. Request official guidelines for Appendix numbering and formatting.

---

## 10. Final Thesis Outline Readiness Assessment

**STATUS**: `[READY]`

**Justification**: The outline matches the mandatory IMCS 2025 five-chapter requirements perfectly. All data and metrics are mathematically consistent with the code and evaluation files. All name and roll number discrepancies have been resolved against the approved proposal, and figure numbering conventions conform to the departmental template.
