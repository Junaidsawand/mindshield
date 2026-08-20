# MindShield FYP-I Thesis Evidence Completion Audit

This document traces and classifies all placeholders, figures, tables, references, and appendices in the MindShield FYP-I thesis master draft ([`docs/MindShield_FYP1_Thesis_Draft.docx`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/MindShield_FYP1_Thesis_Draft.docx)) against the authoritative project files.

---

## 1. Chapter-Based Figure Inventory

### Figure 3-1 — System Architecture
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Detailed architecture diagram mapping the client-native bridge-backend topology.
* **Source**: Mermaid syntax in [`docs/design/SYSTEM_ARCHITECTURE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SYSTEM_ARCHITECTURE.md).
* **Current Status**: Mermaid code verified. Native compilation via CLI is unavailable in the local environment; requires manual compilation using an online renderer or Mermaid editor.

### Figure 3-2 — Use Case Diagram
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Mappings of 10 primary functional use cases (UC-01 to UC-10).
* **Source**: Mermaid syntax in [`docs/design/USE_CASE_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/USE_CASE_DIAGRAM.md).
* **Current Status**: Mermaid code verified. Requires external rendering to PNG.

### Figure 3-3 — Entity Relationship Diagram (ERD)
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Database schema representing `sms_messages` table mapping text, flags, confidence scores, and heuristics.
* **Source**: Mermaid syntax in [`docs/design/ERD.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/ERD.md).
* **Current Status**: Mermaid code verified. Requires external rendering to PNG.

### Figure 3-4 — Data Flow Diagram (DFD) Level 0
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Context-level boundary mapping of data flow.
* **Source**: Mermaid syntax in [`docs/design/DFD_LEVEL_0.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DFD_LEVEL_0.md).
* **Current Status**: Mermaid code verified. Requires external rendering to PNG.

### Figure 3-5 — Data Flow Diagram (DFD) Level 1
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Detailed routing flow between local db cache, native listener, logic layers, and logic server API.
* **Source**: Mermaid syntax in [`docs/design/DFD_LEVEL_1.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DFD_LEVEL_1.md).
* **Current Status**: Mermaid code verified. Requires external rendering to PNG.

### Figure 3-6 — Sequence Diagram
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Interaction timeline sequence for a newly received SMS message.
* **Source**: Mermaid syntax in [`docs/design/SEQUENCE_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SEQUENCE_DIAGRAM.md).
* **Current Status**: Mermaid code verified. Requires external rendering to PNG.

### Figure 3-7 — Deployment Diagram
* **Classification**: `[EVIDENCE FOUND — NEEDS RENDERING]`
* **Description**: Deployment topology detailing client-native modules, loopback APIs, and model servers.
* **Source**: Mermaid syntax in [`docs/design/DEPLOYMENT_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DEPLOYMENT_DIAGRAM.md).
* **Current Status**: Mermaid code verified. Requires external rendering to PNG.

### Figures 3-8 through 3-16 — Mobile UI Screenshots
* **Classification**: `[EVIDENCE FOUND — NEEDS SCREENSHOT]`
* **Description**: Material 3 Flutter application UI states, specifically:
  - Figure 3-8: Native Permissions Request dialog
  - Figure 3-9: Thread-Based SMS Inbox dashboard
  - Figure 3-10: Detailed Message Stream view
  - Figure 3-11: Normal (HAM) Transaction Message indicator
  - Figure 3-12: Suspicious English Phishing Warning card (v1 active prediction)
  - Figure 3-13: Localized Roman Urdu Phishing warning card
  - Figure 3-14: Heuristic Threat Indicators / Highlighted keywords UI card
  - Figure 3-15: Model Server Configuration settings panel
  - Figure 3-16: API Offline/No Connection fallback screen
* **Current Status**: Flutter tool output shows only Windows/Web target devices connected; native Android target (Kotlin dependencies) cannot be executed in the current console environment. Android emulator execution is required to capture authentic Material 3 UI screenshots.

### Figures 4-1 through 4-5 — Matplotlib Results Charts
* **Classification**: `[VERIFIED — READY TO INSERT]`
* **Description**: High-resolution result visualization charts:
  - Figure 4-1: Dataset Class Distribution (UCI vs PakScam-SMS)
  - Figure 4-2: v1 Confusion Matrix heatmap
  - Figure 4-3: v3 Confusion Matrix heatmap
  - Figure 4-4: v1 vs v3 Performance Comparison (F1, Recall, FPR)
  - Figure 4-5: CPU Inference Latency Comparison (Mean, Max vs SLA gate)
* **Current Status**: PNG charts have been generated directly from evaluation logs using `generate_charts.py` and are saved under [`docs/thesis-evidence/figures/`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-evidence/figures/).

---

## 2. Table Inventory

### Table 2-1 — Literature Feature Comparison Matrix
* **Classification**: `[VERIFIED — READY TO INSERT]`
* **Status**: Integrated in draft.

### Tables 3-1 through 3-5 — System Methodology Matrices
* **Classification**: `[VERIFIED — READY TO INSERT]`
* **Status**: Included in methodology text. Includes SQLite schemas and API parameters.

### Tables 4-1 through 4-4 — Quantitative Results Tables
* **Classification**: `[VERIFIED — READY TO INSERT]`
* **Status**: Included in results text. Fully cross-referenced with generated charts.

---

## 3. Metadata, References, and Appendices

### Academic Metadata
* **Classification**: `[VERIFIED — READY TO INSERT]`
* **Status**: All spellings and roll numbers for Junaid Ahmed (2K23/CSM/54), Kalpna (2K23/CSM/55), and Mudasar Ali (2K23/CSM/81) have been substituted.

### Submission Date
* **Classification**: `[SUPERVISOR CONFIRMATION REQUIRED]`
* **Status**: Preserved as `[SUBMISSION DATE — CONFIRM]`.

### Academic References
* **Classification**: `[VERIFIED — READY TO INSERT]`
* **Status**: 10 authoritative references mapped to text citations in IEEE format.

### Appendices A through E
* **Classification**: `[SUPERVISOR CONFIRMATION REQUIRED]`
* **Status**: Placeholders added. Appendix E repository layout must be dynamically generated from active folders.
