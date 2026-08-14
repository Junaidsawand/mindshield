# MindShield — Machine Learning System Documentation

This document serves as the master machine learning technical reference for the MindShield Final Year Project (FYP-I / FYP-II) and Thesis. It provides an end-to-end academic and practical guide to the smishing (SMS phishing) detection engine, from mathematical first principles to production deployment architectures.

---

## 1. Machine Learning & Statistical Fundamentals

### 1.1 Supervised Learning
Supervised learning is a paradigm in machine learning where an algorithm is trained on a labeled dataset $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^N$, where $\mathbf{x}_i \in \mathcal{X}$ is a feature vector (or raw text representation) and $y_i \in \mathcal{Y}$ is the corresponding ground-truth label. The goal is to learn a mapping function $f: \mathcal{X} \rightarrow \mathcal{Y}$ that minimizes an empirical loss function $\mathcal{L}(y, f(\mathbf{x}))$ over the training distribution, allowing the model to generalize and make accurate predictions on unseen data $\mathbf{x}_{\text{test}}$.

* **In MindShield**: The dataset $\mathcal{D}$ contains SMS messages mapped to binary labels (0 for benign "safe" message, 1 for malicious "phishing/spam" message).

### 1.2 Binary Text Classification
Binary text classification is a supervised learning subfield where the label space is restricted to two discrete classes: $\mathcal{Y} = \{0, 1\}$. In natural language processing, the input $\mathbf{x}_i$ is a sequence of characters or tokens representing human language, requiring transformation into numerical vectors before classification.

$$P(y=1 | \mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x} + b)$$

Where $\sigma(z) = \frac{1}{1 + e^{-z}}$ is the logistic sigmoid function, mapping raw model outputs (logits) to a probability distribution in the range $[0.0, 1.0]$.

### 1.3 HAM vs. SPAM/PHISHING Formulation
In MindShield, the classification target is defined as:
* **HAM (Class 0 / `safe`)**: Legitimate communications, such as personal chats, service updates, carrier notifications, and banking transactions.
* **SPAM/PHISHING (Class 1 / `phishing`)**: Social engineering attempts, credential-harvesting lures, fake lotteries, advance-fee fraud, and spoofed bank security alerts.

### 1.4 Train/Validation/Test Split
To evaluate generalization capability and prevent overfitting, the dataset is partitioned:
1. **Training Set ($80\%$)**: Used by the optimizer to adjust model parameters (weights $\mathbf{w}$ and biases $b$).
2. **Validation Set ($10\%$)**: Independent dataset used during training to monitor loss, evaluate convergence, and trigger early stopping (hyperparameter tuning).
3. **Test Set ($10\%$)**: Strictly held-out dataset, used only after training is completed to report final performance metrics.

### 1.5 Class Imbalance
Class imbalance occurs when one class significantly outnumbers the other in the training set. In standard SMS datasets (like the UCI SMS Spam corpus), HAM messages outnumber SPAM by nearly $6:1$.
* **The Danger**: Models trained on highly imbalanced data can optimize for accuracy by simply predicting the majority class (e.g., classifying everything as HAM), resulting in high accuracy but zero recall on the critical minority class (SPAM).
* **In MindShield**: Addressed through targeted minority class augmentation and cost-sensitive evaluation (monitoring F1-score rather than simple accuracy).

### 1.6 Overfitting and Underfitting
* **Overfitting**: Occurs when a model memorizes high-frequency noise and specific patterns in the training set instead of learning generalizable features. The training loss decreases to near zero, but the validation loss rises significantly.
* **Underfitting**: Occurs when the model is too simple to capture the underlying structure of the data (e.g., using a linear model for highly non-linear text semantics), resulting in poor performance on both training and validation sets.

### 1.7 Generalization & The Domain Shift Problem
Generalization is a model's ability to perform accurately on new, unseen examples from the same underlying distribution. **Domain Shift** occurs when the model is deployed on a target data distribution $\mathcal{P}_{\text{target}}$ that differs from the training distribution $\mathcal{P}_{\text{source}}$:

$$\mathcal{P}_{\text{source}}(\text{SMS}) \neq \mathcal{P}_{\text{target}}(\text{SMS})$$

* **In MindShield**: The base model was trained on the UCI SMS Spam corpus (primarily UK/US English from 2011). When evaluated on Pakistani SMS (containing currency notations, local banking transaction phrasing, carrier notifications in English/Roman Urdu, and shortened URLs), the model suffered a massive generalization failure, misclassifying legitimate local notifications as spam.

### 1.8 Performance Evaluation Metrics

#### Confusion Matrix
A tabular layout of classification outcomes:
* **True Positive (TP)**: Phishing SMS correctly classified as `phishing`.
* **True Negative (TN)**: Benign SMS correctly classified as `safe`.
* **False Positive (FP) [False Alarm]**: Benign SMS incorrectly classified as `phishing`.
* **False Negative (FN) [Missed Threat]**: Phishing SMS incorrectly classified as `safe`.

$$\begin{array}{c|cc}
& \text{Predicted: Safe (0)} & \text{Predicted: Phishing (1)} \\
\hline
\text{Actual: Safe (0)} & \text{TN} & \text{FP} \\
\text{Actual: Phishing (1)} & \text{FN} & \text{TP}
\end{array}$$

#### Precision
The proportion of predicted phishing cases that were actually phishing. Critical for minimizing false alarms.

$$\text{Precision} = \frac{\text{TP}}{\text{TP} + \text{FP}}$$

#### Recall (True Positive Rate / Sensitivity)
The proportion of actual phishing threats that were successfully caught by the model. Critical for ensuring user safety.

$$\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$$

#### F1-Score
The harmonic mean of precision and recall, providing a single metric that balances both under class imbalance.

$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}} = \frac{2\text{TP}}{2\text{TP} + \text{FP} + \text{FN}}$$

#### False Positive Rate (FPR)
The proportion of benign messages incorrectly flagged as phishing. In MindShield, we demand $\text{FPR} \le 2\%$.

$$\text{FPR} = \frac{\text{FP}}{\text{FP} + \text{TN}}$$

#### `[Theory/Background]` ROC-AUC & PR-AUC
* **ROC-AUC (Receiver Operating Characteristic - Area Under Curve)**: Plots True Positive Rate (Recall) vs. False Positive Rate across all classification thresholds. AUC measures the probability that the model ranks a random positive sample higher than a random negative sample.
* **PR-AUC (Precision-Recall Area Under Curve)**: Plots Precision vs. Recall across thresholds. More informative than ROC-AUC when evaluating highly imbalanced datasets because it focuses heavily on the minority class (positives).
* *Note*: MindShield's automated pipelines utilize F1-score, Recall, and FPR directly; ROC-AUC is not explicitly tracked inside the validation loop.

### 1.9 Confidence and Decision Thresholds
The raw output of the classification head is a probability score $p \in [0.0, 1.0]$. The standard decision boundary is:

$$\hat{y} = \begin{cases} 
1 & \text{if } p \ge \theta \\
0 & \text{if } p < \theta 
\end{cases}$$

Where $\theta$ is the decision threshold. 
* **Argmax Classification**: Under standard multiclass setup, the class with the highest probability is selected. For binary classification, argmax is mathematically equivalent to setting $\theta = 0.50$.
* **Cost-Sensitive Thresholds**: In production, False Positives (blocking a legal banking receipt) are much more damaging than False Negatives. Thus, a conservative threshold $\theta = 0.85$ can be applied to classify messages as dangerous/phishing only under high model certainty, mapping intermediate scores ($0.60 \le p < 0.85$) to a "suspicious" warnings tier.

---

## 2. Natural Language Processing (NLP) Preprocessing Pipeline

Before feeding text into machine learning models, raw strings must undergo structured preprocessing. In MindShield, this is orchestrated by the `NLPPreprocessingPipeline` in `backend/app/nlp/pipeline.py`.

```
Raw Text ──► Normalization ──► Lowercasing ──► Tokenization ──► Padding/Truncation ──► Input Tensors
```

### 2.1 Text Normalization
Replaces variable text features with standardized representations to collapse the vocabulary space:
* **URL Normalization**: Raw URLs (e.g. `https://ubldigital.com/login`) are identified using regular expressions and replaced with token identifiers. In classical baselines, URLs are stripped or normalized to `<URL>`.
* **Phone/Number Normalization**: Phone numbers are converted to `<PHONE_NUMBER>`, and numeric sequences (such as OTP codes or transaction amounts) are collapsed to `<NUMBER>`.

### 2.2 Lowercasing
Converts all characters to lowercase to treat `"FREE"` and `"free"` as the same token. While beneficial for classical Bag-of-Words models, lowercasing is optional for transformers depending on whether a cased or uncased model is used (MindShield uses `distilbert-base-uncased`, so text lowercasing is aligned).

### 2.3 Tokenization
The process of splitting a continuous text string into discrete units (tokens).
* **Word-Level Tokenization**: Splits on whitespace. Failed by out-of-vocabulary (OOV) terms (e.g. `"smishing"` becomes an unknown token `<UNK>`).
* **Subword-Level Tokenization (WordPiece)**: Used by DistilBERT. It segment words into subword units based on character frequency statistics (e.g., `"annoyingly"` $\rightarrow$ `["annoy", "##ing", "##ly"]`). This allows the model to handle unseen words by breaking them down into familiar subword root components, eliminating the OOV problem.

### 2.4 Padding and Truncation
Deep learning batches require uniform input dimensions:
* **Padding**: Shorter sequences are appended with special padding tokens (`[PAD]`) up to the maximum sequence length. Attention masks are configured to assign `0` to these tokens so the transformer ignores them.
* **Truncation**: Sequences longer than the configured maximum length (`max_length = 128` in MindShield v2/v3) are sliced, discarding trailing tokens.

### 2.5 Training-Inference Alignment
* **The Concept**: The exact same preprocessing steps (normalization, vocabulary, truncation length) applied to the training dataset must be executed identically at the real-time inference pipeline.
* **MindShield Alignment Case**: In v1, training was configured with `max_length=64` while the FastAPI production runtime used `128`. This length mismatch caused misalignment in the positional embeddings of the transformer, leading to false negatives on raw URL prize scams. Aligning both to `128` in v2/v3 restored correct classification behavior.

### 2.6 Transliterated Roman Urdu and Code-Switched text Challenges
In Pakistan, users frequently write Urdu sentences using Latin script (Roman Urdu, e.g. `"Mubarak ho aap ka lottery ticket..."`) or mix English and Urdu words in the same message (code-switching).
* **Tokenization Splitting**: Standard English tokenizers (like WordPiece) fail to recognize Roman Urdu root words, splitting them into small character-level chunks (e.g. `"mubarak"` $\rightarrow$ `["mu", "##ba", "##ra", "##k"]`).
* **Semantic Dilution**: Because the underlying base model was pre-trained on English, character-level representation splits lose semantic richness unless specifically exposed to Roman Urdu samples during fine-tuning.

---

## 3. Classical Machine Learning Baselines

### 3.1 Rationale for Baselines
Before implementing complex, resource-heavy transformer architectures, baseline models are trained to establish a performance ceiling. If a lightweight classical model achieves high accuracy, it represents the most cost-effective solution for production deployment.

### 3.2 Term Frequency-Inverse Document Frequency (TF-IDF)
TF-IDF is a statistical vectorization technique that converts text documents into numerical vectors by weighing terms based on their local frequency and global rarity.

$$\text{TF}(t, d) = \frac{f_{t,d}}{\sum_{t' \in d} f_{t',d}}$$

$$\text{IDF}(t, \mathcal{D}) = \log \left( \frac{1 + N}{1 + |\{d \in \mathcal{D} : t \in d\}|} \right) + 1$$

$$\text{TF-IDF}(t, d, \mathcal{D}) = \text{TF}(t, d) \cdot \text{IDF}(t, \mathcal{D})$$

Where $f_{t,d}$ is the raw count of term $t$ in document $d$, $N$ is the total number of documents in corpus $\mathcal{D}$, and the vector is normalized using L2 norm.
* **Limitation**: TF-IDF ignores word order, context, syntax, and polysemy (e.g., `"bank"` as a financial institution vs. `"river bank"` get identical weights).

### 3.3 Logistic Regression
Logistic Regression is a linear classification model that estimates the probability of a binary outcome.

$$z = \mathbf{w}^T \mathbf{x} + b$$

$$\hat{y} = \sigma(z) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}}$$

The parameters $\mathbf{w}$ (weight vector) and $b$ (bias) are optimized using the binary cross-entropy loss function:

$$\mathcal{L}(\mathbf{w}, b) = -\frac{1}{N} \sum_{i=1}^N \left[ y_i \log(\hat{y}_i) + (1 - y_i) \log(1 - \hat{y}_i) \right] + \lambda ||\mathbf{w}||_2^2$$

Where $\lambda ||\mathbf{w}||_2^2$ is the L2 regularization penalty (Ridge regularization) to prevent overfitting.
* **In MindShield**: Configured in `app/baselines/trainer.py`, TF-IDF combined with Logistic Regression served as the baseline model, achieving over $94\%$ validation accuracy but failing entirely on complex context switches or unseen local banking patterns.

### 3.4 Classical vs. Transformer Trade-offs
| Feature | Classical ML (TF-IDF + LR) | Transformer (DistilBERT) |
|---|---|---|
| **Semantic Extraction** | Bag-of-Words (ignores context) | Self-Attention (fully contextual) |
| **Inference Time** | $< 1\text{ms}$ on CPU | $\approx 40\text{ms} - 60\text{ms}$ on CPU |
| **Model Size** | $< 1\text{MB}$ | **255 MB** weights |
| **Out-of-Vocabulary** | Fails on unseen words | Handles OOV via subword units |
| **Generalization** | Poor on Roman Urdu code-switches | High when fine-tuned |

---

## 4. Deep Learning & DistilBERT Architecture

### 4.1 Transformer Architecture Rationale
Transformers discard recurrence (RNNs/LSTMs) in favor of **Self-Attention** layers, allowing parallel sequence processing and capturing long-range dependencies regardless of word distance in a sentence.

### 4.2 Self-Attention Mechanics
Self-attention computes dynamic weight assignments between every word in a sequence:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

Where:
* $Q = X W^Q$ (Queries: what the word is looking for)
* $K = X W^K$ (Keys: what representation the word offers)
* $V = X W^V$ (Values: the actual semantic payload)
* $\sqrt{d_k}$ is the scaling factor (dimension of query/key vectors) to prevent vanishing gradients during softmax.

This allows the word `"bank"` in `"deposit money into my bank"` to pay high attention to `"money"` and `"deposit"`, resolving context dynamically.

### 4.3 Contextual Embeddings
Unlike static word vectors (e.g. Word2Vec) where `"bank"` has a fixed vector, transformers output contextualized token representations. The final hidden state vector for a token is computed as a weighted sum of the representations of all other tokens in the sentence, capturing syntactic and semantic structure.

### 4.4 Knowledge Distillation
Knowledge distillation is a compression technique where a compact student model is trained to replicate the behavior (soft target probabilities) of a larger teacher model.

$$\mathcal{L}_{\text{KD}} = (1 - \alpha) \mathcal{L}_{\text{CE}}(y, \sigma(z_s)) + \alpha T^2 \mathcal{L}_{\text{KL}}(\sigma(z_t / T), \sigma(z_s / T))$$

Where $z_s$ and $z_t$ are student and teacher logits, $\mathcal{L}_{\text{CE}}$ is cross-entropy, $\mathcal{L}_{\text{KL}}$ is Kullback-Leibler divergence, $T$ is temperature, and $\alpha$ is a balancing coefficient.
* **DistilBERT**: A student model derived from BERT. It has **6 layers** instead of BERT's 12 layers, retaining **97% of BERT's capabilities** while being **40% smaller** (66 million parameters, 255MB weights) and **60% faster** during inference.

### 4.5 Classification Head
For sequence classification, the representation of the special start token `[CLS]` (which aggregates information from the entire sequence via self-attention) is extracted from the last layer. It is fed into a linear layer followed by a dropout regularization layer and projected onto the binary label dimension (2 output classes).

$$z = \text{Linear}(\text{Dropout}(\mathbf{h}_{[\text{CLS}]}))$$

### 4.6 Fine-Tuning vs. Training from Scratch
* **Training from Scratch**: Requires massive datasets (millions of documents) and high compute resources to learn base language grammar, vocabulary, and syntax.
* **Fine-Tuning**: Initializes the model with pre-trained parameters (which already understand English grammar) and continues training on a specific target task (spam detection) using a small, labeled dataset. This adapts the pre-trained weights to domain terminology with low learning rates (e.g., $2\times 10^{-5}$) within few epochs (3–4).

### 4.7 Early Stopping and Validation Tuning
During fine-tuning, validation metrics are monitored at the end of each epoch. If the validation F1-score stops improving (or validation loss starts rising) for a predefined number of epochs (`patience = 3` in v3), training is aborted, and the best-performing checkpoint weights are saved. This prevents the model from overfitting to the training samples.

---

## 5. Domain Generalization & Anti-Shortcut Learning

### 5.1 The Root-Cause of v1 Domain Failure
When trained primarily on the UCI corpus, the model optimized for shortcuts (spurious correlations):
1. **The URL Bias**: In the UCI dataset, 100% of shortened URLs (`bit.ly`, `tinyurl`) exist only in SPAM messages. The model learned that any message containing a URL is phishing/spam, regardless of context.
2. **Transaction Term Overlap**: Benign transaction notifications use financial words (`PKR`, `A/C`, `debit`, `Rs`) that overlap heavily with fake bank security alerts.
3. **Generalization Mismatch**: Positional embeddings truncated text at `64` tokens during training, but inference operated at `128`, diluting long-range attention signals.

### 5.2 Anti-Shortcut Strategy: Hard Negatives
To break these spurious correlations, we introduce **Hard Negatives**—samples designed to teach the model that specific tokens (like URLs and financial terms) do not determine spam status on their own:
* **Legitimate URL-Bearing Messages**: Benign customer service links (`https://bit.ly/ubl-help`) and telecom discount promos (`bit.ly/3rY7XHq`). If the context is promotional or helpful, the model must classify it as `safe`, forcing it to look past the presence of the link.
* **Urgent Benign Alerts**: Overdue loan alerts ("Your ReadyCash is Overdue! Repay via *786#") containing urgency keywords and financial values, categorized strictly as HAM.

### 5.3 Preventing Data Leakage via Template-Family Splitting
Standard random train/test splitting fails when a dataset contains multiple variants of identical message templates (e.g. Zong promos with different package prices).
* **The Leakage**: If one template variant is in the training set and another is in the test set, the model will achieve 100% test accuracy by simple memorization.
* **The Solution**: We group messages sharing structural patterns into **Template Families** (e.g., `zong_flash_sale`). The split logic ensures that entire families are kept strictly together—assigned either $100\%$ to the training set or $100\%$ to the testing set. This guarantees the model is evaluated on its ability to generalize to unseen template structures.

### 5.4 Mitigating Catastrophic Forgetting via Mix-C Oversampling
When fine-tuning a model on a small local dataset (140 Pakistani samples), the model parameters adapt heavily to the new features, overriding the weights learned during baseline training. This is called **Catastrophic Forgetting** (e.g., the model learns Pakistani HAM but forgets how to detect standard UCI spam).
* **Oversampling (Mix-C)**: The Pakistani training subset is duplicated 3 times ($3\times$ oversampling) and combined with the full UCI training set. This balances the distribution, ensuring the model sees enough Pakistani samples in each batch to adapt its weights, while keeping the majority of training inputs from the UCI set ($88.8\%$) to preserve baseline classification boundaries.

---

## 6. Machine Learning Model Evolution & Comparative Audit

MindShield's ML engine evolved through three model iterations to isolate research improvements from the production build:

```
[UCI Baseline] 
      │ (Identified Preprocessing/Truncation Discrepancy)
      ▼
[distilbert-pakscam-v1] (Active Production)
      │ (Domain Generalization Failure: 93.1% FPR on Pakistani HAM)
      ▼
[distilbert-pakscam-v2] (Research Candidate - Fails 3/14 Regressions)
      │ (Mix-C & Roman Urdu Patch Integration)
      ▼
[distilbert-pakscam-v3] (Research Candidate - Fails 1/14 Regression)
```

### 6.1 distilbert-uci-v1 / uci-v2 (Baselines)
* **uci-v1**: Fine-tuned strictly on the UCI SMS Spam corpus using aggressive text preprocessing (Porter stemming, URL stripping). When audited, we found this preprocessing was absent in production, causing high false-negative rates on raw URL texts.
* **uci-v2**: Retrained on raw, un-preprocessed UCI strings with unified `max_length = 128`, restoring baseline performance.

### 6.2 distilbert-pakscam-v1 (Production)
* **Dataset**: UCI SMS dataset augmented with 58 Pakistani templates (mostly spam).
* **Observed Behavior**: High generalization failure. It misclassifies **93.1%** of legitimate local Pakistani banking receipts, telecom promos, and Urdu updates as phishing.
* **Failure Mode**: URL-bias shortcut learning and lack of exposure to localized HAM.
* **Status**: Maintained in production (`backend/data/models/distilbert/`) as a baseline comparison model.

### 6.3 distilbert-pakscam-v2 (Research Candidate)
* **Dataset**: Expanded to ~140 Pakistani samples (incorporating bank receipts and Roman Urdu text).
* **Observed Behavior**: Massive drop in false alarms (overall Pak HAM FPR dropped from 93.1% to **9.2%**; banking FP count dropped to 1).
* **Failure Mode**: Failed 3 critical regression benchmarks (`zong_50_percent_off`, `ubl_customer_service_bitly`, `gaming_royale_subscription`) due to the presence of `bit.ly` shortened links and subscription terms.
* **Status**: Archived in `backend/data/models/distilbert_pakscam_v2/`.

### 6.4 distilbert-pakscam-v3 (Research Candidate)
* **Dataset**: Localized v2 base augmented with 65 anti-shortcut samples (55 HAM, 10 SPAM), including bit.ly-bearing banking/telecom HAM and a Roman Urdu HAM patch.
* **Observed Behavior**: Resolved all `bit.ly` banking and telecom false alarms.
* **Failure Mode**: Failed a single regression test (`zong_engage_prize_lang`).
* **Status**: Archived in `backend/data/models/distilbert_pakscam_v3/`.

---

## 7. Phase 3.8 / v3 Evaluation & Gate Decision

### 7.1 The Objective Promotion Gates
To prevent regression or security vulnerabilities, a model candidate must satisfy all five gates to be promoted:
1. **Pakistani HAM FPR**: $\le 2.0\%$ (allowing $\le 1$ false alarm in 87 samples).
2. **Pakistani SPAM Recall / F1**: $\ge 95.0\%$.
3. **UCI Test F1-Score**: $\ge 95.0\%$.
4. **Hard-Negative Regression Tests**: **100% pass rate** on all 14 regression benchmarks.
5. **CPU Inference Latency**: Mean backend pipeline duration $\le 60\text{ ms}$ (network latency excluded).

### 7.2 Gate Check Results for v3
* **Gate 1 (Pak HAM FPR)**: **3.45% (3/87 FP) [FAIL]**
* **Gate 2 (Pak SPAM Recall)**: **100.0% (53/53 TP) [PASS]**
* **Gate 3 (UCI test F1)**: **95.08% [PASS]**
* **Gate 4 (Regression Pass)**: **13/14 [FAIL]**
* **Gate 5 (Latency Mean)**: **57.62 ms [PASS]**

### 7.3 Regression Failure Analysis (`zong_engage_prize_lang`)
* **Message**: `"Jeetne ke liye tayyar ho jao! aur jeeto bade inaam, Zong Engage ke taraf se khaas http://games.zongengage.com.pk 6PKR/Day, Reply 1 ke saath on 4263"`
* **Why it failed**: The text contains the Roman Urdu phrase `"jeeto bade inaam"` ("win big prizes") and a short link. During v3 training, we added Roman Urdu lottery spam training samples (such as fake lottery wins) which also use words like `"jeeto"` and `"bade inaam"`. The model generalized that Roman Urdu + win-phrases + link = phishing. Because this message is styled like a scam, the model classified it as spam with very high confidence.
* **Status**: Quarantined. `distilbert-pakscam-v1` remains in production.

---

## 8. Production Architecture & E2E Integration Lifecycle

The MindShield system separates the presentation layer, API controllers, and deep learning inference modules to maintain a stateless production runtime:

```
Flutter Client (Interception/UI)
       │ (HTTP POST /api/v1/analyze)
       ▼
FastAPI Request Controller (app/routers/v1/analysis.py)
       │ (JSON Validation & Heuristic Indicators)
       ▼
InferenceService (app/services/inference_service.py)
       │ (Latency Tracking & Loader Delegation)
       ▼
HuggingFaceModelLoader (app/core/model_loader.py)
       │ (Text Preprocessing & PyTorch Forward Pass)
       ▼
Inference Output (Class Probabilities & Logit Scoring)
```

### 8.1 Layer Responsibilities
1. **Flutter Client (`frontend/lib`)**: Native Android Kotlin receiver intercepts SMS. Dart `AnalysisService` dispatches HTTP payload via `Dio` and updates the SQLite database.
2. **FastAPI Router (`backend/app/routers/v1/analysis.py`)**: Validates input models via Pydantic v2 schemas and handles API envelope mapping.
3. **Backend `AnalysisService` (`backend/app/services/analysis_service.py`)**: Runs regular expressions to extract static warning indicators (e.g. `url_detected`, `financial_keywords`) and coordinates prediction output.
4. **`InferenceService` (`backend/app/services/inference_service.py`)**: Measures latency, coordinates primary loading, and automatically falls back to baseline/mock models upon weight load failures.
5. **`HuggingFaceModelLoader` (`backend/app/core/model_loader.py`)**: Loads pre-trained tokenizer and model parameters into CPU memory and computes forward passes.

### 8.2 Explainability & The LIME Highlight Design
* **`[Theory/Background]` LIME (Local Interpretable Model-Agnostic Explanations)**: LIME works by perturbing input text (randomly masking words), running inference on these perturbed instances, and training a simple interpretable linear model on these predictions. The weights of the linear model represent the classification contribution of each word.
* **In-Production Implementation**: Running LIME perturbations in real-time on CPU introduces an extra **1.5s - 2.5s** latency, violating real-time requirements. Thus, MindShield uses **heuristic indicators** on the backend: static keyword lists are matched during preprocessing, and their presence is returned in the `indicators` JSON array. The Flutter frontend maps these indicators to opacity levels to highlight suspicious terms inside the message body view, bypassing perturbation latencies.

---

## 9. Academic Evidence Reference Sitemap

The primary files implementing this ML system are:
* **Training script**: [`backend/scripts/train_pakscam_v3_distilbert.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/train_pakscam_v3_distilbert.py) (implements Mix-C and oversampling).
* **Evaluation runner**: [`backend/scripts/evaluate_v3_suite.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/evaluate_v3_suite.py) (implements evaluation metric splits and gates checks).
* **Regression tests**: [`backend/tests/test_ml_regression_v3.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/tests/test_ml_regression_v3.py) (implements v3 regression benchmarks).
* **FastAPI Endpoint**: [`backend/app/routers/v1/analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/routers/v1/analysis.py) (handles API entry).
* **Model Loader**: [`backend/app/core/model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py) (handles PyTorch serialization).
* **Authoritative metrics data**: [`backend/data/metadata/v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json) (houses the comparative benchmark log).
