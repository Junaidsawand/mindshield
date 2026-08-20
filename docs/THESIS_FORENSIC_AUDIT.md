# MindShield FYP-I Thesis Forensic Academic Audit

This report presents a forensic academic audit of the MindShield Final Year Project (FYP-I) thesis draft ([`docs/MindShield_FYP1_Thesis_Draft.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP1_Thesis_Draft.docx)) and repository files.

---

## 1. Executive Verdict

**`[NOT READY]`**

* **Summary**: While the thesis possesses strong quantitative results and has integrated all 21 figures, it is **not ready** for submission in its current state. The audit has uncovered **critical template leakage** where the main-body tables (Chapter 2 and Chapter 4) remain dummy placeholders containing template data (`['1', '2', '1', '2', '1', '3', '2', '1']`), and the actual project tables (Literature Gap Analysis, Classical Baselines, and Model Metrics) are missing or mislabeled. Multiple typographic spelling mistakes (`CHPATER`, `DISSCUSSION`, `REFRENCES`) and template strings remain in the Table of Contents, List of Tables, and declaration clauses. A rigorous, sequential correction plan must be executed to replace placeholders with verified project evidence.

---

## 2. Discovered Forensic Issues

### A. Critical Issues (Rejection Risks)

#### ID-01: Chapter 2 Table 1 is a Template Placeholder
* **Severity**: `CRITICAL`
* **Location**: Chapter 2, following Paragraph 176.
* **Current Text**: A table with columns `['1', '2', '1', '2', '1', '3', '2', '1']`.
* **Problem**: The table is a raw template dummy placeholder. It does not display the actual project literature review comparison.
* **Evidence Required**: The Literature Review comparison table from [`docs/LITERATURE_REVIEW.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/LITERATURE_REVIEW.md).
* **Recommended Correction**: Delete the placeholder table and replace it with the 8-column Literature Review Gap Analysis table.
* **Requires**: Content rewrite + formatting correction + repository verification.

#### ID-02: Chapter 4 Table 2 is a Template Placeholder
* **Severity**: `CRITICAL`
* **Location**: Chapter 4, following Paragraph 266.
* **Current Text**: A table with columns `['1', '2', '1', '2', '1', '3', '2', '1']`.
* **Problem**: The table is a raw template dummy placeholder. It does not display the actual model comparison metrics.
* **Evidence Required**: The active model (`v1`) vs candidate (`v3`) evaluation metrics from `v3_evaluation_results.json` and [`docs/RESULTS_AND_DISCUSSION.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/RESULTS_AND_DISCUSSION.md).
* **Recommended Correction**: Delete the placeholder table and replace it with the Model Comparison Metrics table.
* **Requires**: Content rewrite + formatting correction + repository verification.

---

### B. High-Priority Issues (Serious Quality Gaps)

#### ID-03: Missing Table 4-1 (Classical ML Baselines) & Numbering Mismatch
* **Severity**: `HIGH`
* **Location**: Chapter 4 results section and List of Tables (Para 96).
* **Current Text**: List of Tables references `Table 4-1: Table of Numbers`, but in the body text (Para 295), the model comparison table is referenced as `Table 4-2`. The actual classical baselines table is completely missing.
* **Problem**: Numbering mismatch and missing content. The classical baselines table must be inserted as `Table 4-1`, and the active vs candidate model comparison table must be inserted as `Table 4-2`.
* **Evidence Required**: Classical baseline metrics from [`docs/RESULTS_AND_DISCUSSION.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/RESULTS_AND_DISCUSSION.md) (linear SVM, logistic regression, naive bayes, random forest).
* **Recommended Correction**: Insert the Classical Machine Learning Baselines table as `Table 4-1` at the beginning of the results chapter, and label the comparison table as `Table 4-2`.
* **Requires**: Content rewrite + formatting correction + repository verification.

#### ID-04: Maligned Table Caption in Chapter 2
* **Severity**: `HIGH`
* **Location**: Paragraph 176, Chapter 2.
* **Current Text**: `Table ?2-1Table of Numbers` (Style: `No Spacing`).
* **Problem**: The caption contains a broken reference marker `?` and placeholder title.
* **Recommended Correction**: Replace the text with `Table 2-1 Literature Review Gap Analysis` and apply the correct caption paragraph spacing.
* **Requires**: Formatting correction.

---

### C. Medium-Priority Issues (Typographical & Logical Gaps)

#### ID-05: Suffix `- test` in Chapter 1 Title
* **Severity**: `MEDIUM`
* **Location**: Paragraph 131 and Table of Contents (Para 83).
* **Current Text**: `CHAPTER 1 INTRODUCTION - test`
* **Problem**: Placeholder text left over from template validation.
* **Recommended Correction**: Change heading text to read exactly `CHAPTER 1 INTRODUCTION`.
* **Requires**: Formatting correction.

#### ID-06: Spelling Typos in Table of Contents Chapters
* **Severity**: `MEDIUM`
* **Location**: Table of Contents, Paragraphs 83, 86, 87, 89.
* **Current Text**: `CHPATER 2`, `CHPATER 3`, `CHPATER 4`, `CHPATER 5`.
* **Problem**: Spelling typo "CHPATER" (swapped P and A).
* **Recommended Correction**: Change to "CHAPTER" in the TOC page (or refresh fields dynamically).
* **Requires**: Formatting correction.

#### ID-07: Spelling Typo `DISSCUSSION` in Chapter 4 Heading
* **Severity**: `MEDIUM`
* **Location**: Paragraph 266 and Table of Contents (Para 87).
* **Current Text**: `RESULTS AND DISSCUSSION`
* **Problem**: Typographical spelling error (double 'S').
* **Recommended Correction**: Change to `RESULTS AND DISCUSSION`.
* **Requires**: Formatting correction.

#### ID-08: Spelling Typo `REFRENCES` in Bibliography Heading
* **Severity**: `MEDIUM`
* **Location**: Paragraph 324 and Table of Contents (Para 91).
* **Current Text**: `REFRENCES`
* **Problem**: Typographical spelling error (missing 'E').
* **Recommended Correction**: Change to `REFERENCES`.
* **Requires**: Formatting correction.

#### ID-09: Declaration Clause Spelling & Grammar Errors
* **Severity**: `MEDIUM`
* **Location**: Paragraphs 50 and 51, Declaration Page.
* **Current Text**:
  - "We here by authorize..."
  - "...to supply of our thesis..."
  - "...no any part of this thesis..."
* **Problem**: Grammatical errors and incorrect word separation.
* **Recommended Correction**:
  - Change "here by" to "hereby".
  - Change "to supply of" to "to supply".
  - Change "no any part" to "no part".
* **Requires**: Content rewrite.

#### ID-10: Device Verification State Contradiction
* **Severity**: `MEDIUM`
* **Location**: Chapter 1/3 methodology text.
* **Current Text**: States that native SMS interception is "device-dependent and pending physical target device attachment."
* **Problem**: Contradicts the fact that screenshots (Figures 3-8 to 3-16) have been successfully captured from the Pixel 6a.
* **Recommended Correction**: Update the text to state that the native broadcast receiver interception was successfully verified on a physical Pixel 6a device running Android 16.
* **Requires**: Content rewrite.

---

### D. Low/Cosmetic Issues (TOC placeholders)

#### ID-11: Template Heading Leftover in Table of Contents
* **Severity**: `LOW`
* **Location**: Paragraph 84, Table of Contents.
* **Current Text**: `2.1.1 Heading (Heading style 3)  4`
* **Problem**: Reference to a placeholder heading style from the template.
* **Recommended Correction**: Refresh TOC fields in Word to automatically remove the deleted template heading.
* **Requires**: Formatting correction.

#### ID-12: Template Figure Caption in List of Figures
* **Severity**: `LOW`
* **Location**: Paragraph 102, List of Figures.
* **Current Text**: `Figure 2-1 Figure Caption (Use figure caption style) 6`
* **Problem**: Reference to a placeholder figure caption from the template.
* **Recommended Correction**: Refresh List of Figures fields in Word to remove the deleted placeholder.
* **Requires**: Formatting correction.

---

## 3. Cross-Document Numerical Consistency Matrix

| Parameter / Metric | Codebase Source (`v3_evaluation_results.json`) | Thesis Draft Text | Status |
| :--- | :--- | :--- | :--- |
| **v1 UCI Test F1-Score** | `0.96` (96.00%) | `96.00%` | **MATCHED** |
| **v1 PakScam Recall** | `0.9811` (98.11%) | `98.11%` | **MATCHED** |
| **v1 PakScam HAM FPR** | `0.9310` (93.10%) | `93.10%` | **MATCHED** |
| **v1 Mean CPU Latency** | `41.95 ms` | `41.95 ms` | **MATCHED** |
| **v1 Max CPU Latency** | `50.74 ms` | `50.74 ms` | **MATCHED** |
| **v3 UCI Test F1-Score** | `0.9508` (95.08%) | `95.08%` | **MATCHED** |
| **v3 PakScam Recall** | `1.0000` (100.00%) | `100.00%` | **MATCHED** |
| **v3 PakScam HAM FPR** | `0.0345` (3.45%) | `3.45%` | **MATCHED** |
| **v3 Mean CPU Latency** | `57.62 ms` | `57.62 ms` | **MATCHED** |
| **v3 Max CPU Latency** | `77.51 ms` | `77.51 ms` | **MATCHED** |
| **UCI SMS Collection Count** | `5,148` records | `5,148` records | **MATCHED** |
| **PakScam-SMS Corpus Size** | `205` templates | `205` templates (140 base + 65 augmentations) | **MATCHED** |
| **PakScam HAM / SPAM Splits** | `142` HAM / `63` SPAM | `142` HAM / `63` SPAM | **MATCHED** |
| **API Backend Unit Tests** | `234` Pytest assertions | `234` assertions (mapped to Appendix A) | **MATCHED** |
| **Flutter Widget Smoke Tests**| `5` Widget tests | `5` Widget tests (mapped to Appendix A) | **MATCHED** |
| **Regression Suite Cases** | `14` (original) / `17` (v3 total) | `14` (original) / `17` (populated in App D) | **MATCHED** |

---

## 4. Objective → Evidence Matrix

| Proposal Objective | Codebase Implementation Evidence | Verification / Evaluation Evidence |
| :--- | :--- | :--- |
| **O1**: Design background SMS interception pipeline. | Kotlin `SMSBroadcastReceiver.kt`, Flutter background service binding. | Widget smoke tests (`widget_test.dart`), TC-01, TC-02, TC-05. |
| **O2**: Curate localized Pakistani smishing corpus. | `pakscam_localized_v2.csv` (140 base templates) + `V3_AUGMENTATIONS` (65 samples). | Section 4.1 class distribution mapping (Figure 4-1). |
| **O3**: Implement bilingual classification engine. | Centralized FastAPI service, fine-tuned DistilBERT models (`v1` serving, `v3` candidate). | Confusion matrices (Figures 4-2, 4-3), metrics comparison (Figure 4-4), and Latency SLA (Figure 4-5). |
| **O4**: Deliver localized visual explainability. | `lime_highlight_card.dart` rendering keyword warning tags and threat indicators on client. | UI screenshots (Figures 3-12, 3-13, 3-14), TC-07, TC-08. |

---

## 5. Figure Verification Matrix

* **Total Figures expected**: 21
* **Total Figures inserted**: 21
* All 21 figures exist in [`docs/thesis-evidence/figures/`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-evidence/figures/) and are centered with correct captions:

| Figure | Title / Caption | Source File / Type | Visual Verification |
| :--- | :--- | :--- | :--- |
| **Figure 3-1** | System Architecture | [`SYSTEM_ARCHITECTURE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SYSTEM_ARCHITECTURE.md) | OK (5.5" width, clear labels) |
| **Figure 3-2** | UML Use Case Diagram | [`USE_CASE_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/USE_CASE_DIAGRAM.md) | OK (5.5" width, flowchart) |
| **Figure 3-3** | ER Diagram | [`ERD.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/ERD.md) | OK (5.0" width, clear keys) |
| **Figure 3-4** | DFD Level 0 | [`DFD_LEVEL_0.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DFD_LEVEL_0.md) | OK (5.0" width, context) |
| **Figure 3-5** | DFD Level 1 | [`DFD_LEVEL_1.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DFD_LEVEL_1.md) | OK (5.5" width, detailed DFD) |
| **Figure 3-6** | Sequence Diagram | [`SEQUENCE_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SEQUENCE_DIAGRAM.md) | OK (5.5" width, timeline) |
| **Figure 3-7** | Deployment Diagram | [`DEPLOYMENT_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DEPLOYMENT_DIAGRAM.md) | OK (5.5" width, node topology) |
| **Figure 3-8** | Native Permissions Dialog | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-9** | Thread-Based SMS Inbox | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-10**| Detailed Message Stream | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-11**| Normal HAM Indicator | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-12**| English Phishing Warning | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-13**| Roman Urdu Phishing Warning| Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-14**| Heuristic Threat Highlights | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-15**| Model Server Settings | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 3-16**| API Offline Fallback | Mobile App UI Screenshot | OK (2.5" width, portrait) |
| **Figure 4-1** | Dataset Class Distribution | Matplotlib chart | OK (5.0" width, balanced colors) |
| **Figure 4-2** | v1 Confusion Matrix | Matplotlib chart | OK (5.0" width, confusion matrix) |
| **Figure 4-3** | v3 Confusion Matrix | Matplotlib chart | OK (5.0" width, confusion matrix) |
| **Figure 4-4** | v1 vs v3 Comparison | Matplotlib chart | OK (5.0" width, metrics comparison) |
| **Figure 4-5** | Latency Benchmarks | Matplotlib chart | OK (5.0" width, latency line chart) |

---

## 6. Table Verification Matrix

| Table | Caption / Title | Type | Source File | Status | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Table 2.1** | Literature Review Gap Analysis | Main | Literature Review | **PLACEHOLDER** | Table 1 in Chapter 2 is a template dummy; must replace it. |
| **Table 3.1** | Functional Requirements Traceability | Main | SRS | **MISSING** | Missing entirely from the body of Chapter 3. |
| **Table 4.1** | Classical Machine Learning Baselines | Main | Baselines | **MISSING** | Missing entirely from the body of Chapter 4. |
| **Table 4.2** | Model Comparison Metrics | Main | Evaluation Results | **PLACEHOLDER** | Table 2 in Chapter 4 is a template dummy; must replace it. |
| **Appendix A**| Detailed Test Case Matrix | Appendix | [`TEST_CASE_MATRIX.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/TEST_CASE_MATRIX.md) | Verified | Mapped and populated successfully. |
| **Appendix B**| FastAPI Router Endpoints | Appendix | Router schemas | Verified | Mapped and populated successfully. |
| **Appendix C**| Dataset Sample Templates | Appendix | `V3_AUGMENTATIONS` | Verified | Mapped and populated successfully. |
| **Appendix D**| Regression Test Suite Cases | Appendix | `test_ml_regression_v3.py` | Verified | Mapped and populated successfully. |

---

## 7. Scope-Lock Compliance Matrix

| Parameter / Wording | Prohibited / Misleading Wording | Compliant Thesis Text | Status |
| :--- | :--- | :--- | :--- |
| **System Interface** | Chatbot, AI Chatbot, Conversational UI | "Thread-based SMS inbox interface" (Para 281) | **COMPLIANT** |
| **LIME Explainability** | True runtime perturbation LIME | "Rule-based heuristic highlights bypassing LIME latency" | **COMPLIANT** |
| **Security Standards** | Secure production HTTPS, JWT | "Unencrypted local HTTP loopback prototype" | **COMPLIANT** |
| **ML Deployment** | Deployed locally, ONNX, XLM-RoBERTa | "Compiling to ONNX for local inference is planned" | **COMPLIANT** |
| **Candidate Model** | `v3` deployed as active serving model | "`v1` is the active model; `v3` is quarantined" | **COMPLIANT** |
| **Dataset Scale** | "Large-scale Pakistani SMS database" | "Curated custom localized corpus of 205 templates" | **COMPLIANT** |
| **System Latency** | Sub-60 ms end-to-end device latency | "Inference latency was benchmarked on CPU" | **COMPLIANT** |
| **Testing Scope** | Independent test set (regression suite) | "On the regression suite (not an independent test)" | **COMPLIANT** |

---

## 8. Final Correction Order (Plan)

To achieve 100/100 readiness, the following edits must be performed in sequence on `docs/MindShield_FYP1_Thesis_Draft.docx`:

1. **Replace Table 1 (Chapter 2)**: Replace the columns and rows of Table 1 with the actual Literature Review Gap Analysis table. Update the caption paragraph above it from `Table ?2-1Table of Numbers` to `Table 2-1 Literature Review Gap Analysis` (Style: `Table Caption`).
2. **Insert Table 3-1 (Chapter 3)**: Insert the Functional Requirements Traceability Matrix table from [`docs/SRS.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/SRS.md) after the paragraph referencing requirements. Add caption `Table 3-1 Functional Requirements Traceability Matrix` above it.
3. **Insert Table 4-1 (Chapter 4)**: Insert the Classical Machine Learning Baselines table from [`docs/RESULTS_AND_DISCUSSION.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/RESULTS_AND_DISCUSSION.md) before the neural results section. Add caption `Table 4-1 Performance of Classical Machine Learning Baselines on UCI SMS Corpus` above it.
4. **Replace Table 2 (Chapter 4) / Mapped as Table 4-2**: Replace the columns and rows of Table 2 with the actual Model Comparison Metrics table. Add caption `Table 4-2 Performance Comparison of distilbert-pakscam-v1 vs distilbert-pakscam-v3` above it.
5. **Declaration Spelling Corrections**:
   - Change "here by" to "hereby" (Para 50).
   - Change "to supply of" to "to supply" (Para 50).
   - Change "no any part" to "no part" (Para 51).
6. **Device Verification text**: Update Chapter 1/3 text to reflect that native BroadCastReceiver interception was verified on a physical Pixel 6a device running Android 16.
7. **Heading Typo Corrections**:
   - Change `CHAPTER 1 INTRODUCTION - test` -> `CHAPTER 1 INTRODUCTION`.
   - Change `CHAPTER 4 RESULTS AND DISSCUSSION` -> `CHAPTER 4 RESULTS AND DISCUSSION`.
   - Change `REFRENCES` -> `REFERENCES`.
   - Change `CHPATER` -> `CHAPTER` in Table of Contents headings.
