# MindShield — Literature Review & Existing-System Analysis

> **Document ID**: `docs/LITERATURE_REVIEW.md`  
> **Phase**: FYP-I Academic Foundation  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Introduction

The rapid expansion of mobile telecommunications in developing nations has made Short Message Service (SMS) a primary channel for communication, financial transactions, and service notifications. However, this ubiquity has also turned SMS into a major vector for social engineering, financial fraud, and credential harvesting—commonly referred to as SMS phishing or "smishing". In Pakistan, the Pakistan Telecommunication Authority (PTA) has highlighted a major rise in unsolicited and fraudulent communication, with scammers targeting users via lottery scams (e.g. fake Benazir Income Support Programme [BISP] or Ehsaas grants), bank account blockage alerts, and unauthorized value-added service (VAS) subscriptions [9]. 

Traditional security systems rely on static keyword filtering or blacklists, which fail to adapt to spelling modifications, bilingual contexts, and local language variations. This literature review establishes the academic and technical foundations of the MindShield platform. It examines the state-of-the-art in SMS spam filtering, Natural Language Processing (NLP) pipelines, machine learning architectures (ranging from classical baselines to modern pre-trained transformers), Explainable AI (XAI) frameworks, and mobile cybersecurity architectures, highlighting the specific engineering and research gaps that MindShield addresses.

---

## 2. SMS Spam and Smishing Detection

### 2.1 The Evolution of SMS Threat Vector
SMS spam originally consisted of unsolicited bulk marketing messages, which were primarily annoying rather than malicious. In contrast, modern **smishing** is highly adversarial, utilizing advanced social engineering techniques to deceive users into transferring funds, sharing one-time passwords (OTPs), or visiting credential-harvesting websites.

Smishing differs from email phishing in several critical ways:
* **Trust Factor**: Users generally trust SMS more than email, as phone numbers are perceived as personal identifiers.
* **Payload Constraints**: SMS messages are limited to 160 characters (GSM-7 encoding), forcing attackers to write concise, high-impact messages and utilize shortened URLs (e.g., `bit.ly`, `tinyurl.com`).
* **Visual Context**: SMS clients lack visual security indicators (like email sender badges, SSL lock icons, or domain indicators), making spoofed sender IDs statistically indistinguishable from legitimate ones.

### 2.2 Domain Shifts and Transliterated Urdu
A major challenge in localized SMS security is the linguistic domain shift. In Pakistan, the majority of SMS communication is written in **Roman Urdu**—transliterated Urdu written using the Latin alphabet (e.g., `"Mubarak ho! Aap ka BISP Rs. 25,000 grant approve ho gaya hai"`). Roman Urdu lacks standardized grammar, spelling, or vocabulary conventions, making it highly challenging for global text classification models pre-trained exclusively on standard English corpora.

---

## 3. NLP-Based Cybersecurity

### 3.1 Preprocessing and Text Normalization
In security applications, raw text must be converted into a structured representation without discarding critical threat indicators. The preprocessing pipeline involves:
1. **Normalization**: Standardization of capitalization, removal of non-standard punctuation, and stripping of duplicate whitespace.
2. **Entity Anonymization**: Identifying and replacing specific variables (like phone numbers, credit card numbers, or transaction IDs) with generic tags (e.g., `[PHONE]`, `[NUMBER]`) to prevent overfitting on arbitrary values.
3. **URL Handling**: Scammers use URL shorteners to mask malicious destinations. While some pipelines scrub URLs entirely to prevent vocabulary explosion, doing so discards a critical feature. Normalization must preserve link markers (`http`, `https`, `bit.ly`) as distinct tokens.

### 3.2 Subword Tokenization vs. Traditional Tokenization
Traditional tokenization splits text on whitespace and punctuation. This fails on out-of-vocabulary (OOV) terms, spelling variations, or code-switched text. To address this, modern NLP pipelines use subword tokenization algorithms, such as **WordPiece**:
* **Mechanism**: WordPiece segments words into subword units (tokens) based on character-level likelihoods. If a word is unknown, it is broken down into constituent subwords (e.g., `"Mubarak"` might be tokenized as `["mub", "##arak"]`).
* **SLA Advantage**: This approach ensures a fixed-size vocabulary ($30,522$ tokens in English DistilBERT) and guarantees that the model will never encounter an OOV token during real-time inference, preserving representation integrity.

---

## 4. Traditional Machine Learning Approaches

Early machine learning classifiers represented text using Bag-of-Words (BoW) matrices or Term Frequency-Inverse Document Frequency (TF-IDF) scores, feeding them into shallow classifiers.

### 4.1 Term Frequency-Inverse Document Frequency (TF-IDF)
TF-IDF measures a term's relevance within a specific document relative to a corpus:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{|D|}{|\{d \in D : t \in d\}|}\right)$$

Where $\text{TF}(t, d)$ is the term frequency in document $d$, and the logarithmic term represents the inverse document frequency across corpus $D$. While effective for detecting frequent keywords, TF-IDF ignores word order, grammar, and semantic relationships, making it vulnerable to synonym substitutions by adversaries.

### 4.2 Classifiers
* **Naive Bayes**: Based on Bayes' theorem, assuming strict feature independence:

$$P(C_k \mid x) = \frac{P(C_k) \prod_{i=1}^{n} P(x_i \mid C_k)}{P(x)}$$

While fast and requiring minimal data, it fails when threat indicators depend on word combinations rather than individual keywords.
* **Logistic Regression**: A linear model mapping features to probabilities using the sigmoid function:

$$\sigma(z) = \frac{1}{1 + e^{-z}}$$

It is highly efficient and serves as a strong baseline, but it cannot capture complex, non-linear relationships or contextual subtleties.
* **Support Vector Machines (SVM)**: Projects vectors into high-dimensional space to find the optimal separating hyperplane:

$$\min_{w, b} \frac{1}{2} \|w\|^2 \quad \text{s.t.} \quad y_i (w \cdot x_i + b) \ge 1$$

While accurate, it scales poorly to large vocabularies and lacks real-time efficiency on complex text streams.

---

## 5. Deep Learning and Transformer-Based Approaches

### 5.1 Recurrent Neural Networks (RNN) and LSTM
To capture sequence information, researchers adopted Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) networks. LSTMs mitigate the vanishing gradient problem using gating mechanisms:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$$

While LSTMs capture sequential dependencies, they process tokens sequentially, preventing parallelization during training and introducing latency bottlenecks during CPU inference.

### 5.2 The Transformer Revolution
Vaswani et al. (2017) introduced the Transformer architecture, replacing recurrence with self-attention. This allows the model to process all tokens in parallel and dynamically weigh relationships between words regardless of distance:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

Where $Q$ (Query), $K$ (Key), and $V$ (Value) represent projection matrices derived from input embeddings, and $d_k$ is the scaling factor of key dimensions. This attention mechanism allows the model to capture deep semantic context, which is critical for identifying subtle manipulation and fraud strategies.

---

## 6. BERT and DistilBERT for Text Classification

### 6.1 BERT (Bidirectional Encoder Representations from Transformers)
BERT [2] utilizes a bi-directional transformer encoder to learn representations from both left and right context simultaneously. This is highly effective for text classification but computationally expensive, requiring 110 million parameters (approx. 440MB weights), which makes it challenging to deploy on resource-constrained servers or mobile environments.

### 6.2 DistilBERT (Knowledge Distillation)
Sanh et al. (2019) introduced **DistilBERT** [3], a compressed transformer model trained via knowledge distillation:
* **Mechanism**: A larger "teacher" model (BERT) transfers its learned probability distributions to a smaller "student" model (DistilBERT). The student optimizes a triple loss function combining distillation loss, masked language modeling loss, and cosine distance loss:

$$\mathcal{L}_{\text{total}} = \alpha \mathcal{L}_{\text{distil}} + \beta \mathcal{L}_{\text{mlm}} + \gamma \mathcal{L}_{\text{cosine}}$$

* **Result**: DistilBERT reduces parameters by $40\%$ (66M parameters, approx. 255MB weights) and increases speed by $60\%$, while retaining $97\%$ of BERT's performance, making it ideal for real-time mobile API backends.

---

## 7. Explainable AI (XAI) and LIME

### 7.1 The Black-Box Problem in Security
Deep learning models provide high classification accuracy but lack transparency. If a system flags a bank notification as phishing with 99% confidence, the user cannot verify *why* this decision was made. In security, this transparency is critical to build user trust and prevent false alarms from causing panic.

### 7.2 LIME (Local Interpretable Model-agnostic Explanations)
Ribeiro et al. (2016) proposed **LIME** [4], which explains a model's prediction locally by perturbing the input text (deleting words) and observing how the predictions change:

$$\xi(x) = \arg\min_{g \in G} \mathcal{L}(f, g, \pi_x) + \Omega(g)$$

Where $f$ is the black-box model, $g$ is the simple, interpretable model (like linear regression), $\pi_x$ defines proximity to the input, and $\Omega(g)$ represents complexity.
* **Limitation in Production**: Generating 500 perturbed strings and running model inference on each introduces a 1.5s - 2.5s latency, violating real-time API SLAs.
* **MindShield Heuristic Visualization**: True LIME runs a ridge regression on perturbed subsets, introducing a latency overhead of 1.5s - 2.5s. To satisfy the 60ms CPU latency SLA, MindShield replaces runtime perturbations with a static, rule-based keyword mapping that extracts indicators (e.g. urgency words, shortened links) on the backend and passes their weights to the Flutter client's `LimeHighlightCard` widget, visualising the indicators without active local surrogate modeling.

---

## 8. Mobile-Based Cybersecurity Systems

Developing client-side security applications requires balancing OS permissions, user privacy, and system latency:

```
[Android OS Broadcasts] ──> [Kotlin SMS Listener] ──> [Method Channel] ──> [Flutter App Services] ──> [FastAPI Server]
```

1. **Android Permissions**: Intercepting incoming SMS requires elevated system permissions (`READ_SMS`, `RECEIVE_SMS`). Modern Android releases enforce strict sandboxing, requiring runtime authorization and restricting background execution.
2. **Architectural Trade-offs**:
   * **On-Device Inference**: Storing a 250MB model locally on standard mobile processors drains battery, increases app size, and blocks memory.
   * **Cloud Inference**: Offloading text to an API enables light client packages and fast model updates, but it introduces network dependency and raises privacy concerns. Anonymizing PII before transmission is essential.

---

## 9. Existing Systems and Comparative Analysis

Existing smishing countermeasures generally fall into four categories:

1. **Static Filters (e.g. Android Default regex/keyword blockers)**: Fast and run offline, but easily bypassed by character mutations (e.g., Replacing `O` with `0`).
2. **Commercial Caller ID / Spam Blockers (e.g. Truecaller)**: Rely on crowdsourced reports and central blacklists. They fail on targeted, low-frequency smishing attempts and lack localized language understanding.
3. **Global Machine Learning Frameworks**: Achieve high accuracy on datasets like the UCI SMS Spam corpus, but struggle with domain shifts, transliterated Urdu, and local banking structures.
4. **Explainable Academic Prototypes**: Demonstrate LIME explainability in research environments but struggle with real-time execution constraints.

### 9.1 Comparative Matrix

| System / Approach | SMS Detection | ML/NLP Engine | Smishing Focus | Explainability | Mobile Integration | Network Overhead | Core Limitation |
|---|---|---|---|---|---|---|---|
| **UCI Spam Classifiers (Almeida, 2011)** [1] | Yes | Classic (SVM, Naive Bayes) | No (Spam only) | No | No (Offline evaluation) | None | Fails to generalize to non-English contexts |
| **Traditional Filters (SpamAssassin)** [10] | Yes | Rule-based & Regex | No | Partial (Rules list) | No | None | Easily bypassed by spelling mutations |
| **Caller ID platforms (Truecaller)** | Yes | Crowdsourcing & Blacklists | Partial | No | Yes (Android app) | High (Online query) | Fails on targeted smishing; privacy concerns |
| **Academic BERT systems** [2] | Yes | Heavy Transformer (BERT) | Yes | No | No (API prototype) | Medium | High CPU latency ($>100\text{ms}$) on server |
| **MindShield (FYP-I Proof of Concept)** | **Yes** | **Light Transformer (DistilBERT)** | **Yes** | **Yes (Decoupled UI Indicators)** | **Yes (Flutter / Kotlin App)** | **Low (REST API)** | **FastAPI connection required for inference** |

---

## 10. Research/Engineering Gap

While SMS spam detection is a mature research area, existing work exhibits three major gaps in the context of developing-country telecommunications:

```
                    ┌──────────────────────────────┐
                    │     Global Spam Research     │
                    └──────────────┬───────────────┘
                                   │  Fails on Roman Urdu & Localized Fraud
                                   ▼
                    ┌──────────────────────────────┐
                    │      Linguistic Domain       │
                    │   (Bilingual / Code-Switch)  │
                    └──────────────┬───────────────┘
                                   │  Lacks Transparency & Context
                                   ▼
                    ┌──────────────────────────────┐
                    │      Explainability Gap      │
                    │    (User-facing Trust)       │
                    └──────────────┬───────────────┘
                                   │  No Real-Time E2E Implementation
                                   ▼
                    ┌──────────────────────────────┐
                    │     Architectural Gap        │
                    │    (Mobile-API Platform)     │
                    └──────────────────────────────┘
```

1. **Linguistic Gap (Roman Urdu & Code-Switching)**: Almost all public smishing datasets and models target pure English or Spanish text. There is a lack of structured research on bilingual (English + Roman Urdu) smishing patterns, which are highly prevalent in South Asia.
2. **Explainability Gap (User-facing Trust)**: Existing machine learning systems act as "black boxes", providing binary classifications without explanation. There is no standard framework to convey model decisions to low-literacy users in an intuitive, visual manner.
3. **Architectural Gap (E2E Integration)**: Much of the literature focuses on model evaluation on static datasets in Jupyter notebooks, without addressing E2E system integration challenges (such as Android background permission handling, SQLite persistence, and API latency constraints).

---

## 11. Relevance to MindShield

MindShield directly addresses these gaps:
1. **Targeting the Linguistic Gap**: Using the custom **PakScam-SMS** dataset (comprising 140 base templates, 65 augmentations, and 15 real-world user-observed seeds), MindShield fine-tunes DistilBERT to recognize Pakistani fraud patterns (BISP scams, fake OTP requests) in both English and Roman Urdu.
2. **Targeting the Explainability Gap**: MindShield translates backend classification indicators into direct visual opacity highlights on the client screen, explaining *why* a message is suspicious.
3. **Targeting the Architectural Gap**: By building a functional Flutter client integrated with a local SQLite database and a FastAPI backend model loader, MindShield demonstrates a viable runtime architecture for SMS protection.

---

## 12. Summary

The literature shows a clear progression from rule-based filters to contextual Transformer models like DistilBERT. While these architectures have improved classification performance, their integration into mobile applications is limited by bilingual domain shifts, latency constraints, and black-box behaviors. MindShield bridges this gap by combining a fine-tuned DistilBERT engine, a custom localized PakScam-SMS dataset, a decoupled user-facing explanation interface, and a functional Flutter-FastAPI architecture.

---

## 13. References

* **[1]** Almeida, T. A., Gómez Hidalgo, J. M., & Yamakami, A. (2011). Contributions to the study of SMS spam filtering: New collection and results. In *Proceedings of the 11th ACM Symposium on Document Engineering* (pp. 259–262). ACM.
* **[2]** Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. In *Proceedings of NAACL-HLT 2019* (pp. 4171–4186).
* **[3]** Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: Smaller, faster, cheaper and lighter. *arXiv preprint arXiv:1910.01108*.
* **[4]** Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). “Why should I trust you?”: Explaining the predictions of any classifier. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 1135–1144).
* **[5]** Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. In *Advances in Neural Information Processing Systems 30 (NeurIPS 2017)* (pp. 4765–4774).
* **[6]** Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. Harper Collins.
* **[7]** Sjarif, N. N. A., Azmi, N. F. M., Chuprat, S., & Udzir, N. I. (2019). SMS spam message detection using term frequency-inverse document frequency and random forest algorithm. *Procedia Computer Science*, 161, 509–515.
* **[8]** Wolf, T., et al. (2020). HuggingFace's Transformers: State-of-the-art natural language processing. In *Proceedings of the 2020 Conference on Empirical Methods in NLP: System Demonstrations* (pp. 38–45).
* **[9]** Pakistan Telecommunication Authority. (2024). *Annual Report 2023–24*. PTA, Islamabad. Retrieved from https://www.pta.gov.pk
* **[10]** Cormack, G. V. (2008). Email spam filtering: A systematic review. *Foundations and Trends in Information Retrieval*, 1(4), 335–455.
