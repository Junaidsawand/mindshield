# MindShield FYP-I Thesis Chapter 1 Correction Report

This report documents the verification and completion of academic corrections applied to **Chapter 1** of the MindShield FYP-I thesis draft ([`docs/MindShield_FYP1_Thesis_Draft.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP1_Thesis_Draft.docx)).

---

## 1. Corrections Applied & Verified

All five (5) authorized academic and scope-lock corrections were successfully applied to the paragraphs of Chapter 1:

| # | Section / Para | Original Text (Draft) | Corrected Text (Applied) | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **1.1 Background** (Para 143) | `Developing an intelligent, explainable on-device monitoring system...` | `Developing an intelligent, explainable on-device monitoring client connected to a centralized classification backend...` | **VERIFIED** |
| **2** | **1.2 Problem Statement** (Para 145) | `3) Dataset scarcity: there is no public repository of Pakistani scam SMS templates.` | `3) Dataset scarcity: No publicly accessible dataset matching the specific bilingual Roman Urdu smishing requirements identified in this study was found during the dataset review.` | **VERIFIED** |
| **3** | **1.3 Research Questions** (Para 149) | `To what extent can a distilled transformer architecture... classify... on low-resource client devices?` | `To what extent can a distilled transformer architecture... classify... when deployed on a local server logic tier?` | **VERIFIED** |
| **4** | **1.4 Objectives** (Para 156) | `- Objective 2: Build a native Android background SMS receiver to intercept incoming messages (device verification pending).` | `- Objective 2: Build a native Android background SMS receiver to intercept incoming messages (verified on physical Pixel 6a device).` | **VERIFIED** |
| **5** | **1.4 Objectives** (Para 161) | `- Objective 7: Execute latency tests ensuring model inference runs under 60 ms.` | `- Objective 7: Execute latency tests to ensure mean model CPU inference latency remains below the 60 ms SLA threshold.` | **VERIFIED** |

---

## 2. Post-Correction Verification & Integrity Checks

1. **Document Corruption & Headings**:
   - The document opens successfully and has been parsed without error.
   - Total paragraphs: **354** (additional formatting spacing verified).
   - Total tables: **7** tables present (main-body tables are preserved as placeholders for subsequent chapter edits; appendix tables are fully populated).
2. **Emulated vs. Device-Level Interception**:
   - Objective 2 is updated to reflect that native BroadcastReceiver SMS interception has been verified on a physical Pixel 6a device, matching the screen captures in Chapter 3.
3. **Latency SLA Alignment**:
   - Objective 7 is updated to reflect that the SLA gate limits the **mean** CPU latency to under 60 ms (v3 achieved `57.62 ms` mean on CPU), while accurately accommodating the measured maximum latency of `77.51 ms`.
4. **Scope-Lock Enforcement**:
   - Programmatic search verified **zero** occurrences of chatbot or conversational AI claims.
   - The distinction between the local background client (Flutter/Kotlin) and the centralized classification engine (FastAPI + DistilBERT) is explicitly clear.
   - All XLM-R, ONNX, and 5-class tactical classification terms are correctly positioned as future work (FYP-II).

---

## 3. Scope and Limitations (Paragraph 164)
The locked academic scope remains intact:
* **Implemented in FYP-I**: Background receiver structure, SQLite cache, unencrypted local loopback HTTP, FastAPI backend, DistilBERT classification engine (v1 serving, v3 candidate), and rule-based visual threat indicators.
* **Deferred to FYP-II**: Production HTTPS/JWT, XLM-R 5-class classification, perturbation-based LIME calculations, ONNX compilation, and nationwide validation.

---

## 4. Final Verdict

**`[READY FOR SUPERVISOR REVIEW]`**

Chapter 1 is now fully corrected, academically defensible, and internally consistent with the codebase and hardware/software setup.
