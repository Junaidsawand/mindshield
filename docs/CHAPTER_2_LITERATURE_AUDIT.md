# MindShield Chapter 2 Literature Audit Report

This report documents the forensic audit and rebuild of **Chapter 2 (Literature Review)** of the MindShield FYP-I thesis draft ([`docs/MindShield_FYP1_Thesis_Draft.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP1_Thesis_Draft.docx)).

---

## 1. Final Status

**`[READY FOR SUPERVISOR REVIEW]`**

---

## 2. Template Artifacts Removed
* **Figure 2-1 Placeholder**: Deleted the caption paragraph `Figure 2-1 Figure Caption (Use figure caption style)` and its empty block from Chapter 2.
* **Table 1 Placeholder Table**: Mapped and deleted the dummy table container (columns: `['1', '2', '1', '2', '1', '3', '2', '1']`) and its caption `Table ?2-1Table of Numbers` from the beginning of the chapter.

---

## 3. Sections Rebuilt and Improved
All Chapter 2 sections have been expanded with comparative academic prose, highlighting strengths, limitations, and direct relevance to MindShield:
* **2.1 SMS Spam & Smishing Detection**: Contextualized higher open rates of SMS channels (Almeida et al. [1]) and introduced Roman Urdu code-switching using academically cautious terminology.
* **2.2 NLP-Based Cybersecurity**: Outlined spelling variation, mixed-script representation, and tokenization challenges in South Asian smishing.
* **2.3 Traditional Machine Learning**: Evaluated classic models (SVM, NB, RF) using TF-IDF features (Sjarif et al. [7]), highlighting their failure to capture sequential context.
* **2.4 Deep Learning & Transformers**: Contrasted sequential bottlenecks of LSTMs/RNNs with parallelized bidirectional self-attention mechanisms (Devlin et al. [2]).
* **2.5 BERT and DistilBERT**: Audited and corrected the DistilBERT performance claim:
  > "...reduces parameter size by 40% while preserving over 95% of BERT's performance as measured on GLUE benchmarks, running 60% faster."
* **2.6 Explainable AI and LIME**: Contextualized LIME perturbation mechanics (Ribeiro et al. [4]) and explained the latency-based justification for MindShield's client-side heuristic warning highlights.
* **2.7 Mobile-Based Cybersecurity**: Justified native BroadcastReceiver intercept and SQLite persistent cache under Android sandbox limits.
* **2.8 Existing Systems and Comparative Analysis**: Replaced the absolute uniqueness claim with:
  > "Within the scope of the reviewed literature and the criteria considered in this study, MindShield combines these capabilities in a single prototype."
  Inserted the new **Table 2-1 Literature Review Comparative Matrix** comparing Truecaller, traditional rules, academic BERT, and MindShield.
* **2.9 Research Gaps**: Categorized gaps into Linguistic/Domain, Dataset, Explainability, and Mobile Integration gaps.
* **2.10 Summary**: Connected the gaps to the design requirements of Chapter 3, and inserted **Table 2-2 Research Gap Traceability Matrix** mapping `Gap` $\rightarrow$ `Limitation` $\rightarrow$ `MindShield Response`.

---

## 4. Citation and References Analysis

### A. Citations Used
* **[1] Almeida et al. (2011)**: Used to justify SMS open rates and spam datasets.
* **[2] Devlin et al. (2019)**: Used for BERT representation and bidirectional attention.
* **[3] Sanh et al. (2019)**: Used to justify DistilBERT parameter reduction and performance benchmarks.
* **[4] Ribeiro et al. (2016)**: Used to outline LIME explainability and computational constraints.
* **[7] Sjarif et al. (2019)**: Used to evaluate traditional SVM/Naive Bayes classifiers with TF-IDF.
* **[10] Cormack (2008)**: Used for traditional rule-based spam filters.

### B. Missing References Mapped
Recommendations for three (3) additional references are documented in [`docs/CHAPTER_2_REFERENCE_GAPS.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/CHAPTER_2_REFERENCE_GAPS.md):
1. **Martin (2017)** — Justification for Presentation-Domain-Data client layers.
2. **Ramirez (2024)** — Justification for asynchronous FastAPI routing.
3. **Sharaf (2005)** — Justification for Roman Urdu spelling variations.

---

## 5. Post-Rebuild Validation Checklist
- [x] Template placeholder tables and captions removed from the draft.
- [x] Figure caption placeholder `Figure 2-1` removed.
- [x] Table 2-1 and Table 2-2 successfully inserted with Times New Roman formatting.
- [x] Typographical metrics for DistilBERT corrected to match Sanh et al. source (over 95% on GLUE).
- [x] Universal dominance claims of Roman Urdu replaced with academically cautious terminology.
- [x] Total table count is **8** (including the Cover, Table 2-1, Table 2-2, Table 4-1 template placeholder, and 4 Appendix tables).
