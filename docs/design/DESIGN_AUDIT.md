# MindShield — Design Audit & Discrepancies Report

> **Document ID**: `docs/design/DESIGN_AUDIT.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Audited Discrepancies Log

This audit logs contradictions discovered between historical documentation drafts, the approved project scope, and the actual implementation evidence within the repository.

### Audit Item 1: SQLite Table Count
* **Historical Claim**: The SRS draft claimed that `mindshield.db` consists of three relational tables: `sms_messages`, `analysis_logs`, and `settings`.
* **Actual Code Evidence**: Verified in [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart#L36-L53) that only a single table (`sms_messages`) is created. Settings are persisted in XML format via Android `SharedPreferences`. History logs are queried dynamically from the classification columns of `sms_messages`.
* **Severity**: Medium
* **Action Taken**: Audited and corrected in the finalized `docs/SRS.md` and `docs/design/ERD.md` to reflect the single-table architecture.

### Audit Item 2: LIME Explainability Engine
* **Historical Claim**: Multiple reports implied that true runtime LIME surrogate perturbations and linear model fitting are executed on the backend request path.
* **Actual Code Evidence**: Confirmed in [`analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) that no surrogate modeling or random word masking is executed. Visual explainability highlights are mapped from static regex indicators in [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py). The term `LimeHighlightCard` in Flutter is strictly a UI rendering convention.
* **Severity**: High
* **Action Taken**: Explicitly documented in the Literature Review, SRS, and boundary guides that true LIME is a future research candidate, and current visual Highlights are heuristic-based.

### Audit Item 3: Local Network Security
* **Historical Claim**: Some design notes stated that request payloads are transmitted over secure HTTPS.
* **Actual Code Evidence**: Confirmed in `app_constants.dart` that connections utilize unencrypted `http://10.0.2.2:8000` or local WiFi loops.
* **Severity**: Medium
* **Action Taken**: Updated all documentation to state that the current FYP-I prototype runs over unencrypted HTTP, while HTTPS is defined as a target production roadmap requirement.

### Audit Item 4: Served ML Model Version
* **Historical Claim**: Earlier notes mentioned that the newer candidate model `distilbert-pakscam-v3` is served by the backend router.
* **Actual Code Evidence**: The backend loaders point to `backend/data/models/distilbert/` which serves the **`distilbert-pakscam-v1`** weights. The research model `v3` remains quarantined in `backend/data/models/distilbert_pakscam_v3/` for validation.
* **Severity**: High
* **Action Taken**: Standardized all references to state that `v1` is the active serving model, and `v3` is archived.

---

## 2. Conclusion
The audit is complete. All discrepancies between specifications, earlier drafts, and the active codebase have been resolved and aligned. No further architectural contradictions exist.
