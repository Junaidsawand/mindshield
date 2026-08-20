# Chapter 8 — Explainable AI & Heuristic Feature Attribution (HFA)

This chapter describes the implementation, design, and visualization of the explainability layer in MindShield. It distinguishes between the machine learning classification process (which yields a binary threat verdict) and the **Heuristic Feature Attribution (HFA)** process (which extracts and represents interpretable risk indicators). Finally, it details the integration of these features in the backend API and frontend Flutter interface.

---

## 8.1 Explainable AI Motivation

In cybersecurity, deep learning sequence classifiers (such as fine-tuned DistilBERT models) act as "black box" models. While they can identify threats with high accuracy, they do not natively explain their internal decision boundaries. 

For SMS threat detection, simply showing a generic warning like `"Dangerous"` or `"Spam"` is insufficient for the following reasons:
* **User Skepticism:** Users frequently ignore security warnings if they cannot verify why a message was flagged.
* **Lack of Actionability:** Different threats require different user mitigations. For example, a credentials-harvesting message requires password security, while a prize scam requires financial vigilance.
* **False Alarm Verification:** By displaying the specific indicators that triggered an alert, users can quickly identify false positives (such as legitimate banking receipts that resemble scams).

To establish user trust, MindShield separates the threat classification task from the explanation generation task, presenting the user with a list of verifiable security indicators.

---

## 8.2 Explainability Architecture

In MindShield, explainability is implemented through a hybrid architecture where the model prediction pipeline and the feature attribution pipeline operate in parallel:

```
                      [Incoming SMS Message Body]
                                   │
            ┌──────────────────────┴──────────────────────┐
            ▼ (ML Classification)                         ▼ (Heuristic Extraction)
    [DistilBERT Model]                               [HFA Rule Engine]
            │                                             │
            ▼                                             ▼
    [Binary Threat Logits]                           [Security Indicators]
            │                                             │
            ▼                                             ▼
    [Verdict & Confidence]                           [Threat Indicators]
            │                                             │
            └──────────────────────┬──────────────────────┘
                                   │
                                   ▼
                         [AnalysisResult Schema]
                                   │
                                   ▼ (HTTP Response JSON)
                         [Flutter Mobile App]
                       Renders Verdict Speedometer
                       & Highlight Legend
```

* **The ML Classification Pipeline:** Focuses strictly on predicting whether the text is `ham` or `spam` using self-attention features.
* **The HFA Pipeline:** Operates independently of the transformer layers, evaluating the text against regex patterns and keyword banks to extract user-facing indicators.

**Implementation Evidence:**
* **Source File:** [`backend/app/services/analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) (lines 183-246)
* **Verify:** `analyse(message)` calls `inference_service.predict(clean_text)` to fetch the ML model prediction, and calls `compute_message_features(clean_text)` to generate HFA indicators.

---

## 8.3 HFA Feature Inventory

The HFA rule engine evaluates SMS text against six distinct security feature categories.

### Table 8.1 — HFA Feature Inventory

| Feature Name | Severity / Weight | Underlying Threat Signal |
| :--- | :---: | :--- |
| **`credential_request`** | `critical` | Requests for passwords, OTP codes, PINs, or sensitive login credentials. |
| **`url_detected`** | `high` | Presence of HTTP/HTTPS URLs, shortened links, or numeric IP links. |
| **`urgency_language`** | `high` | Imperative words demanding immediate action (e.g. "suspended", "verify now"). |
| **`financial_keywords`** | `medium` | References to financial transactions, credit/debit alerts, or banking brands. |
| **`prize_language`** | `medium` | Lottery, jackpot, reward, or congratulatory payout language. |
| **`excessive_caps`** | `low` | High ratio of uppercase characters (capitalization >40%). |

**Implementation Evidence:**
* **Source File:** [`backend/app/services/analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) (lines 48-85)
* **Verify:** `_INDICATOR_MAP` defines the key names, weights, and detail text for the six features.

---

## 8.4 Feature Detection Logic

The extraction of HFA features from text is performed using regular expressions and keyword checks:

### Table 8.2 — Feature Detection Rules

| Feature Key | Input Parameter | Extraction Rule / Regex Pattern | Output Class |
| :--- | :--- | :--- | :---: |
| **`has_url`** | Sanitized text | `re.compile(r"https?://\S+\|www\.\S+\|bit\.ly/\S+\|tinyurl\.com/\S+\|t\.co/\S+")` | Boolean |
| **`has_urgency`** | Sanitized text | Case-insensitive match against a set of 16 urgency terms (e.g., `"account locked"`, `"expires"`, `"immediately"`). | Boolean |
| **`has_financial`** | Sanitized text | Case-insensitive match against 22 financial terms (e.g., `"bank"`, `"ATM"`, `"debit"`, `"payment"`). | Boolean |
| **`has_credentials`**| Sanitized text | Case-insensitive match against 15 credentials terms (e.g., `"password"`, `"otp"`, `"pin"`, `"login"`). | Boolean |
| **`has_prize`** | Sanitized text | Case-insensitive match against 12 reward terms (e.g., `"won"`, `"lottery"`, `"claim your"`). | Boolean |
| **`has_uppercase_ratio`**| Sanitized text | Ratio calculation: `upper_chars / alpha_chars > 0.40`. | Boolean |

**Implementation Evidence:**
* **Source File:** [`backend/app/utils/validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py) (lines 201-322)
* **Verify:** Functions `contains_url`, `contains_urgency_language`, `contains_financial_keywords`, `contains_credential_request`, and `contains_prize_language` implement these rules.

---

## 8.5 Heuristic Scoring

MindShield's HFA pipeline **does not calculate numerical score weights** or aggregate values to modify the model's output. The indicators are **purely categorical**. 

The system returns the presence (`true`/`false`) and severity category (`critical`/`high`/`medium`/`low`) for each indicator. The final threat level classification (`safe`, `suspicious`, `dangerous`) is governed entirely by the DistilBERT logits, while the HFA indicators are used only to describe the decision to the user.

**Implementation Evidence:**
* **Source File:** `analysis_service.py` (lines 207-246)
* **Verify:** Maps `prediction.threat_level` directly to `AnalysisResult.threat_level` without scaling it by indicator counts.

---

## 8.6 Relationship Between HFA and DistilBERT

The HFA rule engine and the DistilBERT sequence classifier operate independently.
* **No Direct Feedback Loop:** The HFA extraction does not alter the transformer model weights or input tensors.
* **No Classification Interference:** The DistilBERT classification logits are not scaled or modified by HFA outputs.
* **Decoupled Verification:** A message can be classified as `"safe"` by DistilBERT while still listing HFA indicators (e.g., a transaction alert with a link will report `url_detected: true` and `financial_keywords: true`, but remain classified as safe).

---

## 8.7 Attack-Vector Categorization

To present the user with a specific attack category (e.g., smishing vs. lottery scams), the system uses a rule-based mapper on the classification output:

```python
# Mapped in api_analysis_repository.dart (frontend)
if (keywordNames.any((k) => k.contains('prize'))) return AttackType.prizeScam;
if (keywordNames.any((k) => k.contains('financial'))) return AttackType.investmentFraud;
if (keywordNames.any((k) => k.contains('credential'))) return AttackType.piiHarvesting;
if (label == 'phishing') return AttackType.phishing;
return AttackType.smishing;
```

**Attack-vector categorization is rule-based and is NOT a multi-class DistilBERT classifier.** It acts as a descriptive post-processing step on the frontend.

**Implementation Evidence:**
* **Source File:** [`frontend/lib/features/analysis/data/api_analysis_repository.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/data/api_analysis_repository.dart) (lines 180-188)
* **Verify:** `_parseAttackType` maps the enum categories.

---

## 8.8 API Representation

HFA indicator flags are serialized into the JSON response payload under the `"indicators"` list:

### Table 8.3 — API ThreatIndicator Schema

| Property | Data Type | Nullability | Description / Value Range |
| :--- | :--- | :---: | :--- |
| **`name`** | String | Non-Nullable | The indicator key (e.g. `"url_detected"`, `"credential_request"`). |
| **`present`** | Boolean | Non-Nullable | `true` if the feature rule was met, otherwise `false`. |
| **`weight`** | String | Non-Nullable | Severity category: `"critical"`, `"high"`, `"medium"`, `"low"`. |
| **`detail`** | String | Nullable | Descriptive explanation of the indicator (null if `present = false`). |

### Example API Response Block:
```json
{
  "name": "credential_request",
  "present": true,
  "weight": "critical",
  "detail": "Requests sensitive credentials (password, OTP, PIN)"
}
```

**Implementation Evidence:**
* **Schema File:** [`backend/app/schemas/analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/schemas/analysis.py)
* **Verify:** Class `ThreatIndicator` declares these properties.

---

## 8.9 Flutter Visualization & Highlighting Fallback

The Flutter application parses the threat indicators in the API response to render the analysis screen UI:

1. **Highlighting Card:** Rendered in [`lime_highlight_card.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart). 
2. **The Highlighting Method:** The card uses a **local substring search** to highlight matching terms. For instance, if `credential_request` is flagged, the frontend searches the text for words like "OTP" or "password" and highlights them.
3. **Attribution Boundary:** *This substring highlighting is a visual heuristic. It does not represent true model-level token attribution (i.e., it does not prove that those specific highlighted words drove DistilBERT's decision).*

---

## 8.10 HFA vs. LIME (Local Interpretable Model-agnostic Explanations)

While the UI refers conceptually to explainability metrics as "LIME," the system implements HFA. The differences are summarized below:

### Table 8.4 — HFA vs. LIME Comparison

| Architectural Property | MindShield HFA | LIME (Surrogate Explainer) |
| :--- | :---: | :---: |
| **Input Perturbation** | **NO** | YES |
| **Local Surrogate Model** | **NO** | YES (trains sparse linear models) |
| **Model-Agnostic** | **NO** (hardcoded logic) | YES |
| **Computational cost** | **Negligible** (<0.1ms) | Higher (requires multiple inference runs) |
| **Inference dependency** | **Independent** | Dependent on model outputs |
| **Output Type** | Categorical Indicators | Numerical feature attribution coefficients |
| **Implementation Complexity** | **Low** | High |
| **Current Project State** | **IMPLEMENTED** | **NOT IMPLEMENTED** |

HFA acts as a fast, deterministic explainer suitable for resource-constrained mobile APIs, establishing the data structures for a transition to true local surrogate modeling in later phases.

---

## 8.11 Advantages of HFA

* **Minimal Latency:** Rule checks run in under 0.1ms on the CPU, preventing inference delays.
* **Deterministic Explanations:** The explanations are predictable, ensuring that identical text patterns yield consistent security indicators.
* **Low Computational Overhead:** Does not require multiple model iterations or gradient computations.

---

## 8.12 Limitations of HFA

* **Decoupled Explanations:** HFA cannot explain *why* DistilBERT made a classification choice; it only describes the indicators found in the text.
* **Static Rule Dependency:** If a smishing message uses obfuscated characters or novel phrasing not covered by the keyword dictionaries, HFA will fail to flag the indicator.
* **Substring Highlight Mismatch:** If the backend flags an indicator category but the frontend substring search does not find a match, no words will be highlighted in the message body.

---

## 8.13 Future Explainability (XAI) Architecture (Future Work)

To implement true token-level model attribution in **FYP2**, the system will require:
1. **Model-Agnostic Surrogate Explainer:** Implementing the perturbation step on the server (generating $N$ variations of the input SMS, querying DistilBERT, and using ridge regression to calculate token-level feature coefficients).
2. **Server-Side Token Spans:** The API will return exact token indices and highlight weights:
   ```json
   "highlights": [ {"start": 12, "end": 15, "weight": 0.85} ]
   ```
3. **In-Context Highlighting:** The frontend will highlight these character ranges directly, ensuring that the visual interface reflects the model's actual self-attention decisions.

---

## 8.14 Privacy Considerations

Because SMS text is sent to the backend for analysis, the explainability layer is designed with strict privacy boundaries:
* **No Server-Side Retention:** Payloads are analyzed in memory; the message body is **never saved** to disk or database logs on the server.
* **Local Contact Security:** The contact display name lookup is performed strictly on-device, preventing contact data from leaking to the server.

---

## 8.15 Chapter Summary

This chapter has detailed the implementation of MindShield's explainability layer, highlighting the distinction between DistilBERT classification and Heuristic Feature Attribution (HFA). While the prototype uses a rule-based HFA engine to generate deterministic indicators, this architecture sets up the API contracts and UI designs for full LIME integration in future phases.

The API schemas, request-response mappings, and server orchestration services are detailed in **Chapter 9 — Backend/API Architecture & Implementation**.
