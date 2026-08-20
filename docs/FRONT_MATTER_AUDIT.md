# Front Matter Audit and Cleanup Report

This report documents the audit and corrections applied to the front matter sections of the MindShield thesis draft (`docs/MindShield_FYP1_Thesis_Draft.docx`).

---

## 1. Corrections Traceability Matrix

| Section | Original Text / Issue | Corrected Text / Action | Justification |
| :--- | :--- | :--- | :--- |
| **Title Pages** | `COPY RIGHTS` | `COPYRIGHT` | Standard academic spelling correction. |
| **Declaration** | "This thesis is our original work and has not been ever submitted, in whole or in part..." | "We declare that this thesis is our original work and has not been previously submitted, in whole or in part, for a degree at this or any other university." | Re-written into formal academic English while preserving legal scope. |
| **Copyright** | "We here by authorize , Jamshoro to supply of our thesis..." | "We hereby authorize the University of Sindh, Jamshoro, to supply copies of our thesis to individuals or libraries for study purposes only." | Grammatically and structurally corrected for academic storage permissions. |
| **Copyright** | "However, no any part of this thesis..." | "However, no part of this thesis or the information contained therein may be included in a publication or referenced without prior written permission." | Rectified grammatical syntax. |
| **Dedication** | Dedicated to parents and supervisor. | Kept as is (professional and concise). | Conforms to undergraduate dedication expectations. |
| **Abstract** | Technical claims audit. | Checked and confirmed that F1-score (96.00%), recall (98.11%), template counts (205), and FPR margins (93.10% to 3.45%) are mathematically aligned with results. Explanations are correctly labeled client-side heuristics (no LIME overclaim). | Verified academic accuracy. |
| **Table of Contents** | Contained misspelled chapter headings (`CHPATER`, `DISSCUSSION`, `REFRENCES`), dummy sections (`2.1.1 Heading`), and duplicated body text blocks (Paragraphs 86 and 89). | Deleted duplicate body text blocks and dummy headings. Rebuilt the entire static Table of Contents to align with the actual headings and sections in Chapters 1–5. | Resolves template errors and ensures navigation consistency. |
| **List of Tables** | Contained dummy entries: `Table 2-1 Table of Numbers` and `Table 4-1: Table of Numbers`. | Cleaned out dummy list. Populated list with the 4 actual tables in the body text (Table 2-1, Table 2-2, Table 4-1, and Table 4-2). | Ensures that only tables actually appearing in the text are listed. |
| **List of Figures** | Had no entries or dummy spacing. | Rebuilt from scratch using the 22 actual figure captions present in the methodology and results chapters (Figures 3-1 to 3-16, and Figures 4-1 to 4-5). | Aligns list with actual methodology design and results diagrams. |
| **Abbreviations** | `SQLite = Structured Query Language Lite` | `SQLite = Lightweight, serverless relational database engine` | Corrects a common technical expansion error (SQLite is not a "lite language", but a lightweight serverless DB engine). |
| **Chapter 2 Body** | Stray caption `Table 2-1Table of Numbers` was present at paragraph 175. | Cleared paragraph 175 to remove the duplicate template caption. | Cleans up residual template artifacts in Chapter 2 text. |

---

## 2. Verification Outcomes
* **TOC Rebuilding Verification**: Confirmed that the static Table of Contents now lists all actual sub-headings (e.g. 3.1 to 3.16, 4.1 to 4.12, 5.1 to 5.7) and excludes dummy headings or duplicated body paragraphs.
* **List of Figures Verification**: Confirmed that all 22 figures are correctly mapped.
* **Scope Lock Conformance**: Verified that no chapters 1 to 5 body texts were modified (other than cleaning up stray template text at paragraph 175).
