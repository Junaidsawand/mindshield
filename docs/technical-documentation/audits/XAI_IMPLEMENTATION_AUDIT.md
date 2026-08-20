# Explainable AI (XAI) Implementation Audit

This document audits the exact technical details and algorithmic implementation of Explainable AI (XAI) and "LIME" features in MindShield.

---

## 1. Core Technical Findings

### Is the official LIME library used?
**No.** There is no import of the official `lime` package (e.g. `lime_text.py` or `LimeTextExplainer`) in any Python file in the backend. There is also no custom perturbation loop (generating variations of the input SMS, feeding them to DistilBERT, and training a sparse linear model as a local surrogate explainer).

### What is actually implemented?
1. **Rule-Based Indicator Extraction:** On the backend in [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py), text is evaluated using static regex patterns and keyword dictionaries for six distinct indicators:
   - `credential_request`
   - `url_detected`
   - `urgency_language`
   - `financial_keywords`
   - `prize_language`
   - `excessive_caps`
2. **Heuristic Indicator Weights:** The indicators are assigned static weights (`critical`, `high`, `medium`, `low`) defined in `_INDICATOR_MAP` inside [`analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py). 
3. **Response Packaging:** The backend returns these indicators (stating whether they are `present` in the SMS or not) as a list in the JSON response payload.
4. **UI Highlighting Fallback:** In the frontend inside [`lime_highlight_card.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart), the app searches the message text for substring matches matching the flagged indicators and highlights them locally.

---

## 2. Architectural Representation & Verification

```
[Raw SMS Text] ──► [Heuristic Detection] ──► [Static Weights] ──► [Threat Indicators]
                         (Regex/Keywords)        (critical/high/...)      (Returned to UI)
                                                                                │
                                                                                ▼
[In-Text Highlighting] ◄── [Substring Search] ◄─────────────────────────────────┘
 (Fails to match raw            (Fallback)
  words dynamically)
```

---

## 3. Discrepancies and Gap Analysis

* **No True Model Attribution:** The highlight card and indicator weights are based on static heuristics, not the actual outputs of the fine-tuned DistilBERT model. For example, if DistilBERT classifies a message as "phishing" based on an unexpected semantic combination, the explanation will still only list whatever basic keywords (like "bank" or "lottery") are caught by the regex/keyword rules.
* **Highlighting Limitations:** Because the backend returns the category names (e.g. `url_detected`) rather than character offset spans or exact highlighted tokens, the UI uses a fallback substring search. This means it cannot highlight specific contextual words dynamically if they do not match the static dictionaries.

---

## 4. Defensible Thesis Terminology

To remain technically honest and defensible during a thesis presentation/viva:

* **Inaccurate/Dangerous Claim:** *"MindShield uses a real-time LIME explainer model to explain DistilBERT's deep learning predictions."* (An examiner will quickly find that the LIME library is missing and challenge this).
* **Accurate/Defensible Claim:** *"MindShield employs a **Hybrid Explainable AI (XAI)** framework combining a deep-learning classification head with a **Heuristic Feature Attribution (HFA)** module. While the ML model generates the core threat verdict, the HFA module acts as a local rule-based explainer to map the presence of critical security indicators (e.g. url detection, credentials requests) to visual highlighting components."*
* **LIME Contextualization:** Refer to the LIME framework as a **conceptual design blueprint** or **planned FYP2 integration**. Explain that the current Phase 3 implementation establishes the end-to-end data pipelines and UI cards, which will be fully integrated with a true local surrogate explainer model (returning exact token weights and character spans) in the next phase.
