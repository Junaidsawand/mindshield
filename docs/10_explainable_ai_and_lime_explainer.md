# MindShield – Explainable AI (XAI) & LIME Explainer Documentation

This document serves as the official technical and academic documentation for the **Explainable AI (XAI)** and **LIME (Local Interpretable Model-agnostic Explanations)** components of the MindShield SMS cybersecurity system. It is structured for use in project reports, thesis documentation, and defense preparation.

---

## 1. Introduction to Explainable AI (XAI) in MindShield

Traditional machine learning models, especially Deep Learning models like **DistilBERT**, act as "black boxes." While they can predict whether an SMS is spam or a scam with high accuracy, they do not inherently provide the reasoning behind their decisions.

In cybersecurity, a lack of explanation leads to:
* **User Skepticism:** Users may ignore warnings if they do not understand why a message is flagged.
* **Lack of Actionability:** Simply knowing a message is dangerous does not tell the user *what* to watch out for (e.g., a suspicious URL vs. credentials harvesting).

**MindShield** addresses this by incorporating XAI principles. When a message is analyzed, the app presents the model's verdict along with feature attribution values indicating *why* the message was flagged.

---

## 2. Concept: How LIME Works in MindShield

**LIME (Local Interpretable Model-agnostic Explanations)** is an explainability framework that explains predictions of any classifier by learning an interpretable model locally around the prediction.

```
       +-----------------------------------------------------+
       |               Global Black-Box Model                |
       |                   (DistilBERT)                      |
       +--------------------------+--------------------------+
                                  |
                   Select Local SMS for Analysis
                                  |
                                  v
       +-----------------------------------------------------+
       |                LIME Local Explainer                 |
       |  Perturbs inputs -> Measures changes in predictions |
       +--------------------------+--------------------------+
                                  |
                     Feature Attribution Weights
                                  |
                                  v
       +-----------------------------------------------------+
       |                    Interpretable                    |
       |                Explanation (UI)                     |
       +-----------------------------------------------------+
```

In the context of MindShield's SMS analysis:
1. **Global Model (DistilBERT):** Classifies the message.
2. **Local Explanation (LIME):** Analyzes the specific sentence and identifies which keywords or semantic features (e.g., urgent keywords, suspicious link structures) had the highest positive contribution (feature importance weight) toward the classification of "scam" or "suspicious."

---

## 3. Data Flow & Integration Architecture

The following diagram illustrates how LIME data flows from the backend model to the Flutter UI:

```
[Real SMS Message]
        │
        ▼
[FastAPI /analyze] ──► [DistilBERT Inference]
        │                      │
        │                      ▼
        │              [LIME Feature Weights]
        │                      │
        ▼                      ▼
[JSON Response Data] ──────────────────────────────────────────────┐
  {                                                                │
    "threat_level": "dangerous",                                   │
    "confidence": 0.952,                                           │
    "indicators": [                                                │
      {"name": "url_detected", "present": true, "weight": "high"},  │
      {"name": "urgency_language", "present": true, "weight": "high"}
    ]                                                              │
  }                                                                │
                                                                   ▼
                                                       [ApiAnalysisRepository]
                                                                   │
                                                       Maps JSON to Domain Entity:
                                                       - SuspiciousKeyword
                                                       - PsychologicalTactic
                                                                   │
                                                                   ▼
                                                       [SenderInfoCard & LIME Card]
                                                       Renders:
                                                       - Verdict Badges
                                                       - Highlight Legend
                                                       - Feature Importance list
```

---

## 4. Current Architecture vs. FYP2 Roadmap

For the **FYP1 Prototype**, the explainability pipeline maps the backend-derived indicators to frontend presentation layers cleanly. Below is the transition plan to a fully production-ready XAI system in **FYP2**.

### FYP1 Status (Current)
* **Real ML Indicators:** The list of flagged features (like `URL DETECTED`, `CRENDENTIAL REQUEST`, `URGENCY LANGUAGE`) and their severity weight scales (Critical, High, Medium, Low) are dynamically fetched from the model.
* **Psychological Mapping:** The app maps these indicators to psychological tactics (Fear Induction, Urgency, Greed) dynamically based on what the model flags.
* **Heuristic/Generic Recommendations:** Action items are loaded based on the threat level.
* **Highlighting:** Handled via local substring matching (which acts as a fallback/placeholder when character indexes are not provided by the API).

### FYP2 Scope (Future)
* **Server-Side Token Spans:** The FastAPI backend will return the exact start/end character offsets for the words that triggered LIME feature importances.
* **Fine-Grained Highlighting:** The Flutter frontend will use these character spans to highlight exactly the words inside the text body, eliminating placeholder index lookups.
* **LLM-Based Explanations:** Integrate a local lightweight LLM (e.g., Llama-3-8B-Instruct) on the backend to consume LIME metrics and write natural-language, human-readable explanations explaining *why* the message was suspicious.

---

## 5. Viva / Thesis Defense Q&A Preparation

These are common questions examiners ask regarding XAI/LIME implementations:

### Q1: What is the difference between global and local explainability?
> **Answer:** Global explainability describes how the model behaves across the entire dataset (e.g., overall feature weights in a training set). Local explainability (what MindShield does using LIME) explains a *single, specific prediction*—telling the user why *this particular SMS* was classified as a threat.

### Q2: Why did you choose LIME over SHAP?
> **Answer:** LIME is model-agnostic and computationally faster for small text sequences (like SMS messages). SHAP (SHapley Additive exPlanations) provides mathematically optimal game-theory values, but is significantly more computationally expensive to run in real-time on a FastAPI server serving mobile clients. LIME fits the real-time requirements of an SMS filter better.

### Q3: How does the model distinguish between a genuine bank URL and a phishing link?
> **Answer:** The DistilBERT model is trained on structural and semantic features. Indicators look for spelling anomalies, subdomains, and the presence of credential requests in the surrounding context. The presence of the `url_detected` indicator alone does not trigger a warning, but its combination with `urgency_language` or `credential_request` increases the threat score.

### Q4: If the highlighting text is a placeholder, is the explainability still real?
> **Answer:** Yes, the explainability metrics (the indicators and feature weights) are computed directly by the machine learning pipeline. The placeholder is strictly in the *visual rendering* (highlighting the exact words in-place in the text). The data itself represents genuine explainable feature attributions from the model.
