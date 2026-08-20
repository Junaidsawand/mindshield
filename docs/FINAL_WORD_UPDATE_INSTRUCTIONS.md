# MindShield FYP-I Thesis — Final Word Update and PDF Export Instructions

**File**: `docs/MindShield_FYP1_Thesis_Draft.docx`  
**Date**: 2026-08-16  
**Status**: DOCX EDITING COMPLETE — Awaiting Word field refresh + PDF export

---

## Why These Steps Are Needed

The thesis DOCX contains Word field codes for:
- **Table of Contents** (TOC)
- **List of Figures** (LOF)
- **List of Tables** (LOT)

These fields display page numbers that are cached from the last time they were updated in Word.
Because python-docx cannot render page layout, the cached page numbers may be incorrect.
**These must be refreshed in Microsoft Word before PDF export.**

---

## Step-by-Step Final Submission Sequence

### Step 1 — Open the DOCX

Open this file in Microsoft Word (version 2016 or later):

```
c:\Users\n tech\OneDrive\Desktop\mindshield\docs\MindShield_FYP1_Thesis_Draft.docx
```

### Step 2 — Update All Fields (TOC / LOF / LOT / Page Numbers)

1. Press **Ctrl+A** to select the entire document
2. Press **F9** to update all fields
3. When prompted: select **"Update entire table"** for each TOC/LOF/LOT dialog
4. Do this for every dialog box that appears (typically 3: TOC, LOF, LOT)

### Step 3 — Visual Inspection Checklist

Work through the document page by page and verify:

**Front Matter:**
- [ ] Title page is correct
- [ ] Declaration, Copyright, Dedication, Acknowledgements are present
- [ ] Abstract contains the XAI clarification sentence (heuristic keyword highlighting)
- [ ] Table of Contents page numbers are correct
- [ ] List of Figures shows 15 entries (Figure 3-1 through 3-9, 4-1 through 4-5, F-1)
- [ ] List of Tables shows 4 entries (Table 2-1, 2-2, 4-1, 4-2)
- [ ] Front matter uses Roman numeral page numbers (i, ii, iii…)

**Chapter Body:**
- [ ] Chapter 1 starts at page 1 (Arabic numerals)
- [ ] All chapter headings are consistent (bold, Times New Roman 16pt)
- [ ] Section 1.1 Introduction has body text paragraph
- [ ] No "PART C" text appears anywhere
- [ ] No "17-case" appears anywhere
- [ ] No "[SUPERVISOR CONFIRMATION REQUIRED]" appears anywhere

**Chapter 3 Figures:**
- [ ] Figure 3-8 is a 2×2 composite (Permissions, Inbox, Message Stream, HAM Indicator)
- [ ] Figure 3-9 is a 1×3 composite (English Phishing, Roman Urdu Phishing, Heuristic Highlights)
- [ ] Both composites are readable at thesis scale
- [ ] No individual screenshot occupies a full page alone

**Chapter 4:**
- [ ] Figures 4-1 through 4-5 are embedded and captioned
- [ ] All numerical values match Table 4-1 / Table 4-2
- [ ] The 100% recall qualification sentence is present in Section 4.4

**References:**
- [ ] References [1] through [10] are present
- [ ] Reference [6] (Devlin) includes DOI: 10.18653/v1/N19-1423

**Appendices:**
- [ ] Appendix A has body text (Test Case Matrix)
- [ ] Appendix B has body text (API Endpoint Specifications)
- [ ] Appendix C has body text (Dataset Sample Templates)
- [ ] Appendix D has body text (14-case Regression Suite)
- [ ] Appendix E has body text (Repository Structure tree)
- [ ] Appendix F has Figure F-1 composite

### Step 4 — Section Page Numbering Verification

The template requires 5 Word sections. The current thesis has 3. This may cause:
- Front matter pages to show Arabic numerals instead of Roman
- Or page 1 to begin at the wrong point

**To verify:**
1. Click in the front matter (Table of Contents page) — the footer should show a Roman numeral (i, ii, etc.)
2. Click on page 1 of Chapter 1 — the footer should show "1"
3. If page numbers are wrong, manual section restructuring is required (see note below)

**If page numbering is correct:** proceed to Step 5.

**If page numbering is wrong:** 
The 5-section structure cannot be safely added by python-docx without risking content loss.
To fix manually in Word:
1. Place cursor at the end of the List of Abbreviations / before Chapter 1
2. Insert → Break → Section Break (Next Page)
3. Double-click the footer in Chapter 1
4. Click "Link to Previous" to UNLINK it from front matter
5. Set page number format to Arabic starting at 1

### Step 5 — Export to PDF

1. File → Export → Create PDF/XPS  
   OR  
   File → Save As → PDF

2. Use the filename:
   ```
   MindShield_FYP1_Thesis_Final.pdf
   ```

3. Settings: High quality print; include all pages

### Step 6 — PDF Page-by-Page QA

Open the PDF and check:
- [ ] No blank pages between chapters
- [ ] No heading appears alone at the bottom of a page (orphan heading)
- [ ] Composite figures are readable (zoom to 100% to check)
- [ ] Tables do not overflow the margins
- [ ] All equations render correctly (especially LaTeX in Section 3.14)
- [ ] References section is complete
- [ ] Appendices A–F are present and have content

---

## Known Remaining Manual Items

| Issue | Action Required |
|---|---|
| Word section count is 3 (template requires 5) | Verify page numbers in Word; fix if incorrect |
| Composite figure readability | Zoom to 100% in Word to verify Figure 3-8 and 3-9 are legible |
| PDF has not been generated | Required before submission |

---

## What Was Automated

Everything else has already been applied to the DOCX:
- All 5 appendices completed with evidence-based content
- All [SUPERVISOR CONFIRMATION REQUIRED] tags removed
- All ??? artifacts removed
- PART C artifact corrected
- 17-case corrected to 14-case
- Duplicate methodology paragraph removed
- Section 1.1 body text added
- 100% recall qualification added
- Abstract XAI clarification added
- Devlin [6] DOI added
- All 16 locked numerical values verified present
- All forbidden claim strings verified absent
- Screenshot composites (3-8, 3-9, F-1) embedded
- References [1]–[10] renumbered with DOIs
