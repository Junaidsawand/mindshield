# MindShield — AI, Machine Learning & LIME Viva Guide

> **Module**: Artificial Intelligence, Smishing NLP Classifier & LIME Explainability  
> **Focus**: Threat Taxonomy, Psychological Manipulation Tactics, LIME Algorithm, Feature Weighting  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding

### Q1: What is LIME and why is explainability critical in mobile cybersecurity?
**Model Answer:**  
LIME (Local Interpretable Model-Agnostic Explanations) is a post-hoc explainability algorithm (Ribeiro et al., 2016). Complex deep learning classifiers (like DistilBERT or Bi-LSTM) act as black boxes, outputting a prediction without explaining why. In cybersecurity, black-box verdicts fail to build user trust (Suarez-Tangil et al., 2014). LIME perturbs the input text (masking tokens), measures prediction changes on perturbed samples, and fits a simple interpretable linear surrogate model locally around the prediction. This outputs token-level feature importance weights (0.0 to 1.0) that MindShield uses to highlight suspicious keywords directly in the UI.

- **UI Visual Mapping**:

| LIME Weight Range | Highlight Intensity | Visual Effect |
|---|---|---|
| 0.80 – 1.00 | High (35% alpha) | Deep orange-red background + bold text |
| 0.50 – 0.79 | Medium (25% alpha) | Moderate orange highlight |
| 0.08 – 0.49 | Subtle (15% alpha) | Light highlight + dotted underline |

---

### Q2: What is the distinction between Threat Score and Confidence Score in MindShield?
**Model Answer:**  
- **Threat Score (0–100)**: Quantifies the *severity* of the attack vector based on identified threat indicators (e.g. malicious URLs, impersonation, urgency).
- **Confidence Score (0–100%)**: Measures the machine learning model's *certainty* in its classification.
- **UX Semantics**: In `AnalysisScreen`, high confidence (e.g. 99% scam certainty) is rendered in red/orange. The progress indicator communicates threat severity rather than positive achievement.

---

## Section B — Design Decision Justification

### Q3: Why combine DistilBERT with heuristic psychological tactic classification?
**Model Answer:**  
Smishing attacks rely heavily on social engineering rather than technical exploits alone. DistilBERT captures contextual semantics (detecting paraphrased phishing lures), while our NLP pipeline categorizes detected manipulation strategies into 10 psychological tactics (Urgency, Fear Induction, Authority, Scarcity, Social Proof, Reciprocity, Curiosity, Greed, Trust Building, Isolation). This dual approach educates the user on *how* they are being manipulated, turning a security warning into an intuitive learning moment.

---

## Section C — Implementation & Technical Depth

### Q4: Walk through the end-to-end AI classification pipeline for an incoming SMS payload.
**Model Answer:**  
1. **Payload Ingestion**: Text passes through `is_valid_message()` validation and `sanitise_message()` unicode NFKC normalization.
2. **Feature Extraction**: Regex filters detect URLs, short-codes, and urgency triggers.
3. **Model Inference**: Transformer pipeline processes tokenized text, generating probability distribution over threat classes.
4. **LIME Perturbation**: Explainer masks tokens to compute local surrogate feature weights.
5. **Entity Assembly**: Resulting label, score, confidence, LIME spans, and recommendations are encapsulated into an `AnalysisResult` entity.

---

## Section D — Limitations, Risks & Future Work

### Q5: What are the main limitations of on-device vs cloud AI models for SMS classification?
**Model Answer:**  
Cloud models (e.g. full BERT-base or Gemini API) offer higher accuracy but require network connectivity, incur server hosting costs, and transmit sensitive SMS text over the network. On-device models (e.g. Quantized TFLite / ONNX DistilBERT) preserve privacy and function offline, but are constrained by mobile CPU/RAM limits. MindShield's clean architecture supports a hybrid approach: local heuristics handle offline detection, while cloud APIs perform deep LIME explainability when online.

---
*MindShield AI & LIME Viva Guide · Final Year Project 2026*
