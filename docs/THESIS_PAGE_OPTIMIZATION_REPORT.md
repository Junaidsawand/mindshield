# MindShield Thesis Page Optimization Report

This report documents the page reductions, layout optimizations, and visual compression metrics achieved on the thesis draft.

---

## 1. Page & Structural Reductions

*   **Original Figures (Chapter 3 Screenshots)**: 9 standalone mobile UI screenshots (each occupying a separate page, adding 9 pages of template inflation).
*   **Optimized Figures (Chapter 3 & Appendix F)**:
    *   **Figure 3-8**: 2x2 Composite Image (Android permission dialog, inbox dashboard, detailed message stream, and normal HAM classification).
    *   **Figure 3-9**: 1x3 Composite Image (English phishing, Roman Urdu phishing, and heuristic keyword highlighting).
    *   **Figure F-1**: 1x2 Composite Image (Model settings and offline API fallback in Appendix F).
*   **Net Reduction**: **6 pages** of layout-induced whitespace inflation removed while preserving 100% of the visual evidence.

---

## 2. Layout & Image Size Matrix

| Figure | Image Path | Layout Grid | Stated Width | Aspect Ratio | Readability Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Figure 3-8** | `Figure_3-8_Composite_Inbox_Hub.png` | 2x2 Grid | 3.2 inches | 0.45 (vertical subfigures) | Aligned side-by-side, preserves screen text |
| **Figure 3-9** | `Figure_3-9_Composite_Threat_Warnings.png` | 1x3 Grid | 5.5 inches | 1.35 (horizontal composition) | Full-width spanning, high legibility |
| **Figure F-1** | `Figure_F-1_Composite_Settings_Fallback.png` | 1x2 Grid | 4.5 inches | 0.90 (balanced composition) | Placed in Appendix F, compact layout |

---

## 3. Formatting Adjustments

*   **Centered Alignment**: All composite figures are centered inside the text boundaries.
*   **Keep-With-Next Pagination**: Dynamic OpenXML formatting is injected on all figure caption runs (`keep_with_next`) to prevent caption text from splitting across pages.
*   **Table Pagination**: Row properties (`cantSplit` and `tblHeader`) remain active to prevent table cells from splitting across page boundaries.
