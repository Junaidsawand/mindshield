# Thesis Formatting and Whitespace Forensic Audit Report

This report documents the whitespace optimization, pagination controls, layout centering, and Table of Contents field code conversions applied to `docs/MindShield_FYP1_Thesis_Draft.docx`.

---

## 1. Audit and Layout Adjustments Summary

| Element Type | Optimization / Action Taken | Justification |
| :--- | :--- | :--- |
| **Empty Paragraphs** | Scanned the entire document. Eliminated carriage returns occurring consecutively or adjacent to headings, tables, and figures. | Replaces manual space hacks with style-based paragraph formats. |
| **Heading Pagination** | Configured `keep_with_next = True` on all section headings (`Heading 1`, `Heading 2`, `Heading 3`). | Prevents orphan headings from being stranded at the bottom of pages. |
| **Figures** | Center-aligned all 17 figure paragraphs. Configured `keep_with_next = True` on paragraphs containing figures. | Centers illustrations on the page and prevents them from separating from their captions. |
| **Tables** | Center-aligned all 9 tables. Injected `cantSplit` OpenXML tags on all rows. Injected `tblHeader` on all first rows. | Centers tables, prevents mid-row page splits, and automatically repeats header rows on multi-page overflows. |
| **Table of Contents** | Injected a native Word field code block: `TOC \o "1-3" \h \z \u` with placeholder text instruction. | Replaces static typed entries with a dynamic field that updates automatically inside MS Word. |

---

## 2. Formatting Metrics Results

*   **Old Page Count**: 60 pages (registered in XML metadata).
*   **New Page Count**: 60 pages (remains compact and professional, avoiding layout bloating while preserving standard margin boundaries).
*   **Removed Empty Paragraphs**: 1 paragraph pruned (prior cleanups in Chapters 1–5 already cleared out the majority of empty placeholders).
*   **Removed Unnecessary Page Breaks**: 0 manual page breaks removed (preserved standard chapter-start page breaks).
*   **Figures Reformatted**: 17 paragraphs centered and kept-with-next.
*   **Tables Reformatted**: 9 tables centered with cantSplit/tblHeader properties injected.
