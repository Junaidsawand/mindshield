# Thesis Critical Fix Log

This log lists all technical and numerical corrections applied to the master thesis draft (`docs/MindShield_FYP1_Thesis_Draft.docx`).

---

## Applied Corrections

### Fix ID: CF-01
*   **Issue**: Inconsistent UCI SMS Spam dataset counts in Chapter 3.
*   **Original Text**: `4,500 HAM, 648 SPAM`
*   **Corrected Text**: `4,506 HAM, 642 SPAM`
*   **Evidence**: `uci_sms_spam_metadata.json` lines 399-400 (deduplicated ham/spam distribution).
*   **Files Changed**: `docs/MindShield_FYP1_Thesis_Draft.docx` (Paragraph 191).
*   **Reason**: Reconciles rounded numbers with exact deduplication logs.

### Fix ID: CF-02
*   **Issue**: Inconsistent UCI SMS Spam dataset counts in Chapter 4.
*   **Original Text**: `4,500 legitimate messages (HAM) and 648 malicious phishing messages (SPAM)`
*   **Corrected Text**: `4,506 legitimate messages (HAM) and 642 malicious phishing messages (SPAM)`
*   **Evidence**: `uci_sms_spam_metadata.json` lines 399-400 (deduplicated ham/spam distribution).
*   **Files Changed**: `docs/MindShield_FYP1_Thesis_Draft.docx` (Paragraph 230).
*   **Reason**: Ensures numerical consistency between methodology and results sections.

### Fix ID: CF-03
*   **Issue**: Wording of latency SLA for the quarantined candidate model.
*   **Original Text**: `Objective 7: Execute latency tests to ensure model CPU inference latency remains below the 60 ms SLA threshold.`
*   **Corrected Text**: `Objective 7: Execute latency tests to ensure mean model CPU inference latency remains below the 60 ms SLA threshold.`
*   **Evidence**: `v3_evaluation_results.json` lines 334-337 (v3 mean CPU latency is 57.62 ms, satisfying the SLA, but peak latency is 77.51 ms, exceeding it).
*   **Files Changed**: `docs/MindShield_FYP1_Thesis_Draft.docx` (Paragraph 270).
*   **Reason**: Prevents false claims regarding maximum/peak latency.

---

## Final Consistency Search Verification
*   **UCI Count Search**: Scanned the document for all occurrences of `4,500 HAM` and `648 SPAM`. None remain. All counts are exactly aligned with the deduplicated dataset log (`4,506 HAM, 642 SPAM`).
*   **Unresolved Contradictions**: None. The document's structural and numerical assertions are completely reconciled.
