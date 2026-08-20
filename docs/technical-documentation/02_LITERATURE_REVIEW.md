# Chapter 2 — Literature Review & Technical Background

This chapter provides a comprehensive review of the scientific literature and technical background underpinning the MindShield platform. It contextualizes the SMS smishing threat, reviews classical and deep-learning natural language processing (NLP) architectures, and surveys state-of-the-art developments in domain shift, Explainable AI (XAI), and mobile application security. Finally, it identifies the primary research gaps that motivate the MindShield project.

---

## 2.1 Introduction to the Literature Review

Securing the Short Message Service (SMS) protocol on user endpoints requires an intersection of multiple disciplines: data engineering, statistical machine learning, deep neural network architectures, model interpretability, and mobile operating system integrations. 

This literature review is structured to trace the evolution of SMS threat filtering:
1. Identifying the core characteristics of mobile messaging threats (smishing) and the limitations of traditional rules-based defenses.
2. Reviewing the progression of NLP classifiers from classical machine learning baselines (Naive Bayes, Support Vector Machines) to contextual deep learning models (RNNs, LSTMs, Transformers, and DistilBERT).
3. Analyzing the localized challenges of low-resource transliterated languages (Roman Urdu) and the phenomenon of domain shift and shortcut learning.
4. Examining the current state of Explainable AI (XAI) frameworks (LIME, SHAP) and their compatibility with mobile systems.

---

## 2.2 SMS Spam, Smishing and Mobile Messaging Threats

SMS spam has historically been defined as unsolicited bulk messaging, typically containing marketing promotions. However, modern mobile threat landscapes have transitioned from simple commercial spam toward targeted malicious smishing (SMS phishing) operations (Almeida et al., 2011). 

Smishing represents a critical security threat because it utilizes **social engineering** techniques (psychological triggers like urgency, greed, or fear) to induce the user to perform dangerous actions:
* **Credential Harvesting:** Text messages containing links to cloned login portals designed to capture user passwords, PINs, or Multi-Factor Authentication (MFA) tokens.
* **Financial Fraud:** Scam messages urging users to execute mobile wallet transactions or contact fraudulent helplines to resolve fake account suspensions.

### Limitations of Traditional Filtering
Traditional endpoint filtering relies on **static blacklists** of sender phone numbers or simple regex keyword matching (e.g., blocking messages containing "lottery" or "block"). Attackers easily bypass these controls by:
1. Obfuscating characters (using lookalike Unicode symbols).
2. Constantly rotating sender phone numbers or abusing alphanumeric Sender ID spoofing.
3. Using link shorteners (such as `bit.ly` or `tinyurl`) to hide the final redirect destination.

Consequently, modern systems require content-aware classification engines capable of modeling the semantic context of messages.

---

## 2.3 Machine Learning for SMS Classification

Prior to the dominance of deep neural networks, classical machine learning algorithms paired with feature-engineering techniques formed the standard for text classification:

* **Feature Representation:** Raw text is transformed into numerical vectors using techniques like **Count Vectorization** (representing term frequency counts) or **TF-IDF (Term Frequency-Inverse Document Frequency)**, which weights terms based on their document-wide importance:
  $$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{|D|}{1 + |\{d \in D : t \in d\}|}\right)$$
* **Classifiers:** Popular models include Naive Bayes (leveraging conditional probabilities), Logistic Regression, and **Support Vector Machines (SVM)**. An SVM constructs an optimal hyperplane that maximizes the geometric margin between the benign and malicious classes:
  $$\min_{\mathbf{w}, b} \frac{1}{2} \|\mathbf{w}\|^2 + C \sum_{i=1}^{n} \xi_i$$
  subject to $y_i (\mathbf{w}^T \mathbf{x}_i + b) \ge 1 - \xi_i$ for $i \in \{1, \dots, n\}$.

### Strengths and Weaknesses of Classical NLP
Classical machine learning pipelines are highly efficient, requiring minimal memory and execution overhead. On standardized, keyword-heavy datasets, classical models (specifically Linear SVMs) frequently match or outperform deep learning models on local accuracy (Almeida et al., 2011). 

However, they suffer from a major weakness: **lack of semantic context**. Because bag-of-words models treat terms as independent dimensions, they cannot model word order or negations, rendering them vulnerable to adversarial keyword swapping.

---

## 2.4 Deep Learning for Text Classification

To overcome the lack of word-order context in bag-of-words models, researchers introduced deep learning neural architectures:

* **Recurrent Neural Networks (RNNs):** Model text as sequential inputs. However, standard RNNs suffer from the vanishing gradient problem when processing long sequences, preventing them from learning long-term dependencies.
* **Long Short-Term Memory (LSTM) & Gated Recurrent Units (GRU):** Introduce gating mechanisms (input, forget, and output gates) to regulate information flow. LSTMs maintain a cell state to propagate context across long sequences, making them highly effective for text classification (Hochreiter & Schmidhuber, 1997).
* **Convolutional Neural Networks (CNNs) for Text:** Use 1D convolutional filters over word embedding dimensions to extract local n-gram features (Kim, 2014).

While LSTMs and CNNs capture sequential relationships, they process text sequentially, preventing parallel computation and limiting their ability to learn bidirectional contextual representations.

---

## 2.5 Transformer Architecture

The introduction of the **Transformer architecture** by Vaswani et al. (2017) replaced recurrence and convolutions with the **Self-Attention mechanism**.

```
Input Tokens ──► [Input & Position Embeddings] ──► [Multi-Head Self-Attention] 
                                                         │
                                                         ▼
                                               [Feed Forward Layer] ──► Output Representation
```

### 1. Self-Attention Mechanics
Self-attention calculates representation vectors for each token by attending to every other token in the sequence. For input matrices representing Queries ($Q$), Keys ($K$), and Values ($V$), the Scaled Dot-Product Attention is computed as:

$$\text{Attention}(Q, K, V) = \text{Softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

where $d_k$ is the scaling dimension of the keys.

### 2. Key Architectural Components
* **Multi-Head Attention:** Runs multiple attention layers (heads) in parallel, allowing the model to attend to information from different representation subspaces.
* **Positional Encoding:** Because transformers do not use recurrence, absolute or relative positional encodings are injected into the input embeddings to preserve token order.
* **Encoder-Only Stack:** Processes the entire sequence simultaneously in both directions, generating deeply contextualized token representations.

---

## 2.6 BERT (Bidirectional Encoder Representations from Transformers)

Devlin et al. (2018) introduced **BERT**, establishing the pre-training and fine-tuning paradigm for NLP:

* **Pre-training Pipeline:** BERT is trained bidirectionally on large unlabeled text corpora (e.g. Wikipedia) using two objectives:
  1. **Masked Language Modeling (MLM):** Randomly masking 15% of input tokens and training the model to predict them based on context.
  2. **Next Sentence Prediction (NSP):** Predicting whether a sentence logically follows another.
* **Fine-Tuning:** During fine-tuning, a task-specific linear layer (classification head) is appended to the contextual hidden state of the first special token (`[CLS]`). The entire architecture is then trained on labeled datasets, allowing the model to adapt to specific domains (like SMS classification) with minimal training data.

---

## 2.7 DistilBERT

Although transformers achieve state-of-the-art performance, their large parameter size (~110M parameters for BERT-base) creates high memory and latency overhead. Sanh et al. (2019) resolved this by introducing **DistilBERT**, a distilled version of BERT:

* **Knowledge Distillation:** A compression technique where a smaller student network (DistilBERT) is trained to reproduce the behavior and output probability distributions of a larger teacher network (BERT):
  $$\mathcal{L}_{\text{distil}} = \mathcal{L}_{\text{CE}}(y, \hat{y}_{\text{student}}) + t^2 \mathcal{L}_{\text{KL}}(P_t, P_s)$$
  where $\mathcal{L}_{\text{KL}}$ represents the Kullback-Leibler divergence between the teacher's soft targets $P_t$ and the student's predictions $P_s$ at temperature $t$.
* **Compression Profile:** DistilBERT reduces the number of transformer layers by 50% (6 layers instead of 12) and parameter counts by 40%, while retaining **97% of BERT's language understanding capability** and increasing inference speed by 60%.

---

## 2.8 Multilingual, Roman Urdu, and Code-Switched NLP

SMS threat filtering in localized South Asian environments is complicated by linguistic features:

* **Roman Urdu:** Urdu written using the Latin alphabet (transliterated phonetics). It lacks standard spelling dictionaries, resulting in multiple spelling variations for identical words (e.g., the word *inaam* can be spelled *inam*, *enaam*, or *enam*).
* **Code-Switching:** Alternating between English and Urdu within a single sentence (Rehman et al., 2020).
* **Low-Resource Classification:** Translating Roman Urdu back to Arabic-script Urdu before processing introduces high translation latency and error rates.

Traditional NLP models trained on standard English datasets cannot capture these localized code-switched patterns, requiring custom training datasets and vocabulary adaptations (Khan et al., 2022).

---

## 2.9 Domain Shift and Dataset Generalization

A machine learning model trained on a source distribution $\mathcal{P}_{\text{source}}$ can drop in performance when deployed on a target distribution $\mathcal{P}_{\text{target}}$ (Ben-David et al., 2010):

### 1. Shortcut Learning
Geirhos et al. (2020) define **shortcut learning** as a phenomenon where neural networks learn simple, decision-rule heuristics (e.g., classifying *any* message containing a shortened link or a currency tag as spam) that are highly accurate on the training dataset but fail when exposed to out-of-distribution data.

### 2. Hard Negatives
In local SMS traffic, legitimate transactional receipts (containing currency symbols, account numbers, and links) act as **hard negatives**. If the model relies on shortcut learning, it misclassifies these benign receipts as phishing, raising False Positive Rates. Generalization requires training pipelines that include localized hard negatives to force the model to learn contextual features.

---

## 2.10 Explainable AI (XAI) for Text Classification

As machine learning models are deployed in high-risk domains like cybersecurity, model transparency is critical (Ribeiro et al., 2016):

### 1. Local Surrogate Explanations (LIME)
LIME explains individual predictions by perturbing the input text (randomly masking words) and training a local, interpretable linear model around the prediction:
$$\xi(x) = \arg\max_{g \in G} \mathcal{L}(f, g, \pi_x) + \Omega(g)$$
where $\mathcal{L}$ measures the discrepancy between the primary model $f$ and surrogate model $g$, scaled by proximity measure $\pi_x$, while $\Omega(g)$ penalizes complexity.

### 2. SHAP (SHapley Additive exPlanations)
Lundberg & Lee (2017) compute feature attributions using Shapley values from cooperative game theory, calculating the average marginal contribution of a token across all possible feature subsets.

*MindShield's HFA pipeline is decoupled from these mathematical attributions, providing deterministic, rule-based indicator categories to optimize client-side mobile performance.*

---

## 2.11 Mobile Security and SMS Monitoring

Integrating threat classification models into mobile environments requires native operating system hooks:
* **Background Interception:** Android allows applications to register `BroadcastReceivers` for `SMS_RECEIVED` intents to capture incoming payloads before the system database commits them.
* **Sandbox Constraints:** Modern mobile operating systems restrict direct filesystem access, requiring inter-process communication (IPC) or platform-specific bridges (MethodChannels) to pass variables between native layers (Kotlin) and cross-platform views (Flutter).

---

## 2.12 Privacy-Preserving Mobile Security

SMS messages contain personally identifiable information (PII), such as OTP codes, bank balances, and names. 
* **Data Minimization:** Under privacy-by-design principles, security systems must minimize the collection of PII.
* **Transmission Risks:** Sending SMS content to remote servers for inference exposes data to transit eavesdropping. This requires in-memory transient processing (discarding payloads immediately after classification) and HTTPS transport security.

---

## 2.13 Existing SMS Security Systems

The following table summarizes existing SMS security research:

### Table 2.13 — Comparison of SMS Threat Detection Systems

| Study | Year | Dataset Size | Language Scope | Model Architecture | Threat Target | Explainability | Mobile Integration | Primary Limitation |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Almeida et al.** | 2011 | 5,574 (UCI) | English | SVM / Naive Bayes | Commercial Spam | None | None | No context modeling |
| **Rehman et al.** | 2020 | 1,500 | Roman Urdu | Random Forest | Spam | None | None | Rule dependent |
| **Khan et al.** | 2022 | 8,000 | Roman Urdu | LSTM / GRU | Spam | None | None | No real-time API |
| **MindShield (Ours)**| 2026 | 5,148 + 205 | Eng / Roman Urdu | DistilBERT + HFA | Phishing / Smishing | **HFA** | **Android / Flutter** | Remote server dependency |

---

## 2.14 Research Gap Analysis

1. **Local Domain-Shift Gap:** While literature covers English smishing and general Roman Urdu spam, it lacks evaluations of domain shift on localized Pakistani transactional alerts.
2. **Explainability-Latency Gap:** Existing XAI implementations (LIME/SHAP) add significant computational overhead, making them unsuitable for real-time mobile API constraints.
3. **Mobile-System Integration Gap:** Most studies evaluate models offline on static text corpora, without integrating the inference pipeline into native mobile BroadcastReceiver lifecycles.

---

## 2.15 Positioning of MindShield

MindShield bridges these research gaps by designing a hybrid system:

```
[Android Ingestion] ──► [SQLite Cache] ──► [FastAPI Tier] ──► [DistilBERT + HFA] ──► [Flutter UI]
   (Engineering)           (Storage)         (Communication)          (Research ML)         (Presentation)
```

The system combines background SMS interception, local database persistence, remote DistilBERT classification, and Heuristic Feature Attribution (HFA) to provide localized, explainable SMS threat filtering.

---

## 2.16 Chapter Summary

This chapter has reviewed the literature on SMS threats, machine learning models, domain generalization, and explainability frameworks. By identifying the limitations of base models under domain shift and the need for explainable mobile interfaces, this review establishes the foundations for the system methodology described in **Chapter 3 — Methodology**.

---

## 2.17 References

* Almeida, T. A., Hidalgo, J. M. G., & Yamakami, A. (2011). Contributions to a donating users' SMS spam collection. *Proceedings of the 11th ACM Symposium on Document Engineering*, 211-218.
* Ben-David, S., Blitzer, J., Crammer, K., Kulesza, A., Pereira, F., & Vaughan, J. W. (2010). A theory of learning from different domains. *Machine Learning*, 79(1-2), 151-175.
* Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. *arXiv preprint arXiv:1810.04805*.
* Geirhos, R., Jacobsen, J. H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence*, 2(11), 665-673.
* Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. *Neural Computation*, 9(8), 1735-1780.
* Khan, M. A., et al. (2022). Roman Urdu Spam SMS Detection Using Deep Learning Techniques. *IEEE Access*, 10, 56321-56334.
* Kim, Y. (2014). Convolutional neural networks for sentence classification. *Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, 1746-1751.
* Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 4765-4774.
* Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135-1144.
* Sanh, V., Debut, L., Chaumond, J., & Wolf, T. (2019). DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter. *arXiv preprint arXiv:1910.01108*.
* Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need. *Advances in Neural Information Processing Systems*, 5998-6008.
