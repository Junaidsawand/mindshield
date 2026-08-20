# MindShield — Thesis Format Specification

> **Document ID**: `docs/THESIS_FORMAT_SPECIFICATION.md`  
> **Phase**: FYP-I Thesis Planning  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Source**: Extracted from `docs/thesis-template/FYP_Thesis_Template_IMCS_2025.docx`  

---

## 1. Page Layout

| Property | Value |
|---|---|
| **Page size** | A4 (8.27 in x 11.69 in / 210 mm x 297 mm) |
| **Orientation** | Portrait |
| **Left margin** | 1.50 in (3.81 cm) — serves as binding margin |
| **Right margin** | 1.00 in (2.54 cm) |
| **Top margin** | 1.00 in (2.54 cm) |
| **Bottom margin** | 1.00 in (2.54 cm) |
| **Gutter** | Not explicitly set (left margin is enlarged instead) |

---

## 2. Font Specifications

### 2.1 Style Definitions (from Word Styles)

| Style Name | Font Family | Font Size | Bold | Alignment |
|---|---|---|---|---|
| **Normal** (body text) | Times New Roman | 12 pt | No | Justified |
| **Heading 1** (chapter titles) | Times New Roman | 18 pt | Yes | Center |
| **Heading 2** (sections) | Times New Roman | 14 pt | Yes | Left (inherited) |
| **Heading 3** (subsections) | Times New Roman | 12 pt | Yes | Left (inherited) |
| **Heading 4** | Times New Roman | 12 pt | Yes | Left (inherited) |
| **Heading 5** | Times New Roman | 12 pt | Yes | Left (inherited) |
| **Title** | Times New Roman | 28 pt | Yes | — |
| **Figure Caption** | (inherited) | 11 pt | No | — |
| **Caption** | (inherited) | 9 pt | No | — |
| **table of figures** | (inherited) | 10 pt | No | — |
| **toc 1** | (inherited) | (inherited) | No | — |
| **toc 2** | (inherited) | 11 pt | No | — |
| **toc 3** | (inherited) | 11 pt | No | — |
| **No Spacing** (table captions) | Times New Roman | 12 pt | No | — |
| **Footer Odd** | (inherited) | 10 pt | No | — |
| **Body Text** | Times New Roman | 10 pt | No | — |

### 2.2 Runtime Font Override
The actual document content uses **Aptos** font in many paragraphs as a run-level override. The underlying style definitions specify **Times New Roman**. The style-level definitions (Times New Roman) should be treated as the authoritative font family.

> [!IMPORTANT]
> Use **Times New Roman** throughout the thesis. The Aptos font appearing in the template is a Word default override and should not be followed.

---

## 3. Paragraph Formatting

### 3.1 Normal Style (Body Text)

| Property | Value |
|---|---|
| **Line spacing** | 1.5 lines |
| **Line spacing rule** | ONE_POINT_FIVE |
| **Space before** | 12 pt (152400 EMU) |
| **Space after** | None (inherited) |
| **First-line indent** | None |
| **Alignment** | Justified |

### 3.2 Heading 1 Style

| Property | Value |
|---|---|
| **Space before** | 30 pt (381000 EMU) |
| **Space after** | 6 pt (76200 EMU) |
| **Alignment** | Center |
| **Keep with next** | Yes |
| **Page break before** | Not set |

### 3.3 Heading 2 Style

| Property | Value |
|---|---|
| **Space before** | 16 pt (203200 EMU) |
| **Space after** | 6 pt (76200 EMU) |
| **Alignment** | Left (inherited) |
| **Keep with next** | Yes |

### 3.4 Heading 3 Style

| Property | Value |
|---|---|
| **Space before** | 16 pt (203200 EMU) |
| **Space after** | 6 pt (76200 EMU) |
| **Alignment** | Left (inherited) |
| **Keep with next** | Yes |

---

## 4. Page Numbering

| Section | Number Format | Evidence |
|---|---|---|
| Front matter (Certificate through Abbreviations) | **Roman numerals** (I, II, III, IV...) | TOC shows: CERTIFICATE I, DEDICATION II, ACKNOWLEDGEMENTS III, ABSTRACT IV, TABLE OF CONTENTS V, LIST OF TABLES VII, LIST OF FIGURES VIII, ABBREVIATIONS IX |
| Chapter content (Chapter 1 through References) | **Arabic numerals** (1, 2, 3...) | TOC shows: CHAPTER 1 INTRODUCTION 1, CHAPTER 2... 4, etc. |
| Cover page / Title page | **Not numbered** | No footer content |

### 4.1 Footer Placement
- Page numbers appear in the **footer**
- Footer text uses the **Footer** or **Footer Odd** style
- Section breaks control the transition from Roman to Arabic numbering
- The template uses 5 Word sections to manage page numbering transitions

---

## 5. Section Breaks

The template contains **5 Word sections**:

| Section | Purpose | Start Type | Footer Linked |
|---|---|---|---|
| Section 0 | Cover/title pages | Continuous | No (different first page enabled) |
| Section 1 | Certificate through Abstract | Continuous | Yes (linked to previous) |
| Section 2 | TOC through Abbreviations | Continuous | No (independent footer) |
| Section 3 | Chapter content | Continuous | Yes (linked to previous) |
| Section 4 | References | Continuous | No (independent footer) |

---

## 6. Table Formatting

| Property | Value |
|---|---|
| **Caption position** | Above the table |
| **Caption style** | No Spacing |
| **Caption numbering** | `Table {chapter}-{sequence}` (e.g., Table 2-1) |
| **Table style** | Table Grid |
| **Table alignment** | [VERIFY IN ORIGINAL TEMPLATE] |
| **Cell font** | Inherits from Normal |

---

## 7. Figure Formatting

| Property | Value |
|---|---|
| **Caption position** | Below the figure |
| **Caption style** | Figure Caption (11 pt) |
| **Caption numbering** | `Figure {chapter}-{sequence}` (e.g., Figure 2-1) |
| **Figure alignment** | [VERIFY IN ORIGINAL TEMPLATE] |

---

## 8. Reference Formatting

| Property | Value |
|---|---|
| **Citation style** | IEEE numbered `[1]`, `[2]`, `[3]` |
| **In-text ranges** | `[1-3]` for consecutive references |
| **Reference list style** | Normal paragraph style |
| **Reference section title** | REFERENCES (Heading 1) |
| **Ordering** | Sequential numbered list |
| **EndNote styles present** | Yes (EndNote Bibliography, EndNote Bibliography Title) |

---

## 9. Cover Page Layout

| Element | Formatting |
|---|---|
| University name area | [VERIFY IN ORIGINAL TEMPLATE — likely includes logo] |
| Department name | 16 pt, Bold, Center |
| Degree type | 24 pt, Bold, Center: "BS(CS) Thesis" |
| Thesis title | 18 pt, Bold, Center |
| Submission statement | 11 pt, Bold |
| Student names + roll numbers | 14 pt, Bold, Left-aligned with tabs |
| Date (month/year) | 20 pt, Bold, Center |

---

## 10. Title Page Layout

The template appears to include a second page repeating the cover information with the "University of Sindh, Jamshoro" header (19 pt, Bold, Center) and "CERTIFICATE" section.

---

## 11. Abbreviation Format

| Property | Value |
|---|---|
| **Style** | Normal (Bold) |
| **Format** | `ABBR\t\tFull Form` (tab-separated) |
| **Example** | `ADL\t\tArchitecture Description Language` |
