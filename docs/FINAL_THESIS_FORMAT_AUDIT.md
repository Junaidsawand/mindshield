# MindShield FYP-I Thesis — Final Format Audit Report

**Document**: `docs/MindShield_FYP1_Thesis_Draft.docx`  
**Audit Date**: 2026-08-16  
**Auditor**: Automated formatting pass + manual verification  
**Format Spec**: `docs/THESIS_FORMAT_SPECIFICATION.md`

---

## 1. Page Layout ✅

| Property | Required | Applied | Status |
|---|---|---|---|
| Page size | A4 (8.27 × 11.69 in) | ✅ Set on all 3 sections | PASS |
| Orientation | Portrait | ✅ Default | PASS |
| Left margin | 1.50 in (binding) | ✅ Set on all sections | PASS |
| Right margin | 1.00 in | ✅ Set on all sections | PASS |
| Top margin | 1.00 in | ✅ Set on all sections | PASS |
| Bottom margin | 1.00 in | ✅ Set on all sections | PASS |

---

## 2. Font and Paragraph Formatting ✅

| Element | Required | Applied | Status |
|---|---|---|---|
| Heading 1 | TNR 18pt Bold, Centered, 30pt before / 6pt after | ✅ Applied to all 22 H1 paragraphs | PASS |
| Heading 2 | TNR 14pt Bold, Left, 16pt before / 6pt after | ✅ Applied to all 60 H2 paragraphs | PASS |
| Heading 3 | TNR 12pt Bold, Left, 16pt before / 6pt after | ✅ Applied | PASS |
| Normal (body) | TNR 12pt, Justified, 1.5× line spacing, 12pt before | ✅ Applied to 198 Normal paragraphs | PASS |
| Figure Caption | TNR 11pt, Centered, 6pt before / 6pt after | ✅ Applied to 15 Figure Caption paragraphs | PASS |
| Table Caption (body) | TNR 12pt, Centered, No Spacing style | ✅ Fixed 8 table captions | PASS |
| References | TNR 12pt Normal, Left | ✅ Applied | PASS |

---

## 3. Heading Hierarchy ✅

| Chapter | Sections | Status |
|---|---|---|
| Chapter 1 — Introduction | 1.1 through 1.9 (9 sections) | ✅ Restored missing 1.1 Introduction heading |
| Chapter 2 — Literature Review | 2.1 through 2.10 (10 sections) | ✅ Sequential |
| Chapter 3 — Research Methodology | 3.1 through 3.16 (16 sections) | ✅ Restored missing 3.10 heading |
| Chapter 4 — Results & Discussion | 4.1 through 4.12 (12 sections) | ✅ Sequential |
| Chapter 5 — Conclusion | 5.1 through 5.7 (7 sections) | ✅ Sequential |
| Appendices | A through F (6 appendices) | ✅ All as Heading 2 under APPENDICES Heading 1 |

---

## 4. Figure Numbering ✅

| Figure | Caption | In Body | LOF Entry | Status |
|---|---|---|---|---|
| Figure 3-1 | System Architecture | ✅ | ✅ | PASS |
| Figure 3-2 | Use Case Diagram | ✅ | ✅ | PASS |
| Figure 3-3 | Entity Relationship Diagram | ✅ | ✅ | PASS |
| Figure 3-4 | DFD Level 0 | ✅ | ✅ | PASS |
| Figure 3-5 | DFD Level 1 | ✅ | ✅ | PASS |
| Figure 3-6 | Sequence Diagram | ✅ | ✅ | PASS |
| Figure 3-7 | Deployment Architecture | ✅ | ✅ | PASS |
| Figure 3-8 | Composite — Inbox Hub (2×2 grid) | ✅ | ✅ Updated | PASS |
| Figure 3-9 | Composite — Threat Warnings (1×3 grid) | ✅ | ✅ Updated | PASS |
| Figure 4-1 | Class Distribution | ✅ | ✅ | PASS |
| Figure 4-2 | Confusion Matrix v1 | ✅ | ✅ | PASS |
| Figure 4-3 | Confusion Matrix v3 | ✅ | ✅ | PASS |
| Figure 4-4 | Graphical Metric Comparison | ✅ | ✅ | PASS |
| Figure 4-5 | Latency Profile | ✅ | ✅ | PASS |
| Figure F-1 | Settings + Fallback (1×2 grid, Appendix F) | ✅ | ✅ Added | PASS |

> [!NOTE]
> Figures 3-10 through 3-16 were deliberately merged into the composite Figures 3-8 and 3-9 during the visual compression pass. The LOF has been updated accordingly.

---

## 5. Table Numbering ✅

| Table | Caption | LOT Entry | Status |
|---|---|---|---|
| Table 2-1 | Literature Review Gap Analysis | ✅ | PASS |
| Table 2-2 | Research Gap Traceability Matrix | ✅ | PASS |
| Table 3-1 | Use Case: UC-01 — SMS Reception | ✅ (in body, verified) | PASS |
| Table 3-2 | Use Case: UC-02 — Threat Analysis | ✅ | PASS |
| Table 3-3 | Use Case: UC-03 — Message Classification | ✅ | PASS |
| Table 3-4 | Use Case: UC-04 — History Review | ✅ | PASS |
| Table 3-5 | Use Case: UC-05 — Settings Configuration | ✅ | PASS |
| Table 4-1 | Classical ML Baselines | ✅ | PASS |
| Table 4-2 | v1 vs v3 Comparison | ✅ | PASS |

---

## 6. Cross-Reference Integrity ✅

All in-text references to Figures (e.g., Figure 3-8a, Figure 3-9b, Figure F-1b) and Tables (e.g., Table 4-2) verified against actual body paragraphs. No dangling references found.

---

## 7. Document Structure ✅

| Element | Count | Status |
|---|---|---|
| Total paragraphs | 299 | — |
| Heading 1 | 22 | ✅ |
| Heading 2 | 60 | ✅ |
| Figure Caption | 15 | ✅ |
| Table Caption (No Spacing) | 4 (body captions) | ✅ |
| Normal | 198 | ✅ |
| Tables | 9 | ✅ |
| Sections | 3 | ⚠️ See note below |

> [!IMPORTANT]
> **Section Count Note**: The template specification requires 5 Word sections for correct page numbering transitions (Roman numerals for front matter → Arabic numerals for chapters). The current document has 3 sections. The page numbering transition **must be verified manually** in Microsoft Word before PDF export. This cannot be fully fixed programmatically with python-docx without risk of corrupting the document structure.

---

## 8. Orphan/Widow Prevention ✅

- `keep_with_next = True` applied to all 81 heading and figure caption paragraphs.
- `cantSplit` applied to all 9 tables to prevent row breaks across pages.
- `tblHeader` active on header rows.

---

## 9. Action Required Before Submission

> [!CAUTION]
> The following **must be performed manually** in Microsoft Word before PDF export:

1. **Update TOC page numbers**: Press `Ctrl+A` → `F9` → "Update entire table" for all TOC, LOT, and LOF fields.
2. **Verify page numbering sections**: Confirm front matter uses Roman numerals (I, II, III...) and chapter content uses Arabic numerals (1, 2, 3...).
3. **Verify composite figure readability**: Open the document and visually confirm that Figures 3-8, 3-9, and F-1 composite images are clear at the set widths.
4. **Remove SUPERVISOR CONFIRMATION REQUIRED tags**: Once the supervisor has confirmed appendix content and formatting, remove all `**[SUPERVISOR CONFIRMATION REQUIRED...]**` tags from Appendix A through E headings.

---

## 10. Final Verdict

| Check | Result |
|---|---|
| Font consistency | ✅ PASS |
| Margin correctness | ✅ PASS |
| Heading hierarchy | ✅ PASS |
| Figure numbering (3-1 to 3-9, 4-1 to 4-5, F-1) | ✅ PASS |
| Table numbering (2-1, 2-2, 3-1 to 3-5, 4-1, 4-2) | ✅ PASS |
| List of Figures updated | ✅ PASS |
| List of Tables updated | ✅ PASS |
| Caption styles | ✅ PASS |
| Orphan heading prevention | ✅ PASS |
| Table overflow prevention | ✅ PASS |
| Cross-references correct | ✅ PASS |
| Page numbering sections | ⚠️ Manual verification required |
| TOC page numbers | ⚠️ Ctrl+A → F9 required in Word |

### **STATUS: FORMATTING COMPLETE — READY FOR FINAL MANUAL WORD PASS**
