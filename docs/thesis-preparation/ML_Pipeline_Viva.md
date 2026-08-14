# MindShield — ML Pipeline & Viva Defense Technical Reference

> **Document ID**: `docs/thesis-preparation/ML_Pipeline_Viva.md`  
> **Target Audience**: Viva Defense Examiners & Thesis Reviewers  
> **Key Focus**: Rigorous, Examiner-Proof Q&A Knowledge Base for Thesis Defense  

---

## 1. Thesis Defense Core Structure

For every major machine learning technique, we structure our defense using five parameters:
1. **What is it?** (Academic definition)
2. **Why did we use it?** (Rationale for selection in MindShield)
3. **How does it work?** (Mathematical/algorithmic formulation)
4. **What evidence do we have?** (Experimental results supporting/rejecting it)
5. **What is its limitation?** (Compromises or boundaries introduced)

---

## 2. Frequently Asked Viva Questions & Defensible Answers

### Q1: Why did you choose DistilBERT instead of traditional Machine Learning (e.g. TF-IDF + Logistic Regression)?
* **What is it?**: DistilBERT is a lightweight transformer model pre-trained on large English corpora. Traditional ML (TF-IDF + LR) relies on Bag-of-Words vectors representing frequency counts.
* **Why did we use it?**: Smishing attacks rely on linguistic context, urgency manipulation, and subtle spelling mutations. Traditional ML models fail when words are slightly modified or when spam keywords are used in legitimate contexts.
* **How does it work?**: DistilBERT utilizes multi-head self-attention mechanisms to construct dynamic, contextual embeddings of words based on their surroundings:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$

* **Evidence**: The Logistic Regression baseline achieved $94\%$ validation accuracy but failed completely when faced with local Pakistani transactions and shortened links. DistilBERT reached **$96.00\%$** UCI F1 and successfully caught $100\%$ of Pakistani spam in the v3 candidate.
* **Limitation**: DistilBERT requires significant memory (255 MB weights) and CPU execution time ($\approx 57\text{ms}$) compared to Logistic Regression ($< 1\text{ms}$, $< 1\text{MB}$).

---

### Q2: Why didn't you choose a larger transformer model like BERT or a generative model like GPT?
* **Defense**: 
  * **BERT (110M params / 440MB)**: MindShield is designed for real-time mobile security alerts. Decoupling to a FastAPI server helps, but the server must still run inference on CPU to control cloud hosting costs. BERT increases inference latency to $> 100\text{ms}$ on CPU, adding excessive thread blockage. DistilBERT compresses BERT by $40\%$ while maintaining $97\%$ of its performance.
  * **Generative GPT (LLMs)**: Large Language Models are highly expensive, require complex APIs, add latency of $> 1\text{s}$, and are prone to hallucinations. Smishing detection is a classification task (discriminative, not generative), which does not require generation. DistilBERT is the optimal, resource-efficient boundary for our production deployment requirements.

---

### Q3: What is "Catastrophic Forgetting" and how did you prevent it during local domain adaptation?
* **What is it?**: Catastrophic forgetting is the phenomenon where a neural network fine-tuned on a new target domain ($\mathcal{P}_{\text{local}}$) overwrites the weights associated with the source domain ($\mathcal{P}_{\text{source}}$), losing its original capabilities.
* **Why did we use it?**: MindShield must protect against local Pakistani smishing without losing the ability to detect standard English spam.
* **How does it work?**: We implemented **Mix-C oversampling**. Instead of fine-tuning only on our small Pakistani corpus, we duplicated the Pakistani templates 3 times ($3\times$ oversampling) and combined them with the full, original UCI training corpus. The combined dataset contained $88.8\%$ UCI samples and $11.2\%$ Pakistani samples.
* **Evidence**: Fine-tuning strictly on Pakistani data (v2 candidate) dropped UCI test F1 to **$94.21\%$**. Integrating Mix-C in the v3 candidate successfully restored UCI F1 back to **$95.08\%$** (passing the $\ge 95.0\%$ gate).
* **Limitation**: Mix-C increases training epoch size (from 4,118 to 4,637 samples), which increases training time slightly.

---

### Q4: Why did your best-performing research model (distilbert-pakscam-v3) fail to get promoted to production?
* **Defense**: MindShield enforces a strict safety-critical deployment standard. Even though `v3` achieved a massive reduction in false positives (reducing Pakistani HAM FPR to $3.45\%$ from v1's $93.1\%$) and caught $100\%$ of Pakistani spam, it failed two critical promotion gates:
  1. **FPR Gate (Fails)**: FPR was $3.45\%$, violating the $\le 2.0\%$ threshold (representing exactly 3 false alarms in 87 legitimate samples).
  2. **Regression Gate (Fails)**: Passed 13 out of 14 regression benchmarks, failing on `zong_engage_prize_lang`.
* *Critical Script for the Examiners*:
  *"In a production mobile security application, a false alarm that blocks a legitimate bank transaction receipt or carrier service message is highly disruptive. Since `distilbert-pakscam-v3` failed the strict $2.0\%$ FPR gate and failed a regression case, we kept the production model safely at `distilbert-pakscam-v1` (which has a near-zero FPR of $0.22\%$ on standard UCI spam) and quarantined v3 as a research candidate for further iteration. We do not promote models that fail safety gates."*

---

### Q5: Explain the failure of the `zong_engage_prize_lang` regression benchmark.
* **What is it?**: A benchmark message check using a legitimate carrier promo: `"Jeetne ke liye tayyar ho jao!... Zong Engage... 6PKR/Day..."`.
* **Why did it fail?**: During v3 training, we added Roman Urdu lottery phishing templates (such as Ehsaas and BISP scams) to prevent false negatives. These templates use urgent Urdu phrases like `"jeeto"` (win) and `"bade inaam"` (big prizes) along with URLs. The model over-generalized this combination.
* **How does it work?**: The self-attention layers focused heavily on the Roman Urdu tokens `["jeeto", "bade", "inaa", "##m"]` and link headers, driving the final sigmoid probability $P(\text{phishing}) = 0.9929$.
* **Evidence**: Pytest output:
  `FAILED tests/test_ml_regression_v3.py::test_v3_ham_regression[...-zong_engage_prize_lang] - AssertionError: Expected 'safe' but got 'phishing'`
* **Limitation**: Correcting this requires further iteration—specifically collecting and adding benign carrier promos containing identical Urdu win-phrases to the training set and running a fresh, isolated training experiment.

---

### Q6: What are "Hard Negatives" and why are they important?
* **What is it?**: Legitimate messages (HAM) that share surface-level vocabulary and structures commonly found in spam (e.g., links, prices, urgency, capital letters).
* **Why did we use it?**: In the baseline UCI training set, almost 100% of shortened URLs (`bit.ly`) occur in spam. This causes the model to learn a "shortcut": **if a message contains a URL, classify it as spam**.
* **How does it work?**: We added legitimate customer service survey links (`https://bit.ly/ubl-help`) and billing updates pointing to official pages, labeled strictly as HAM. This forced the self-attention heads to look past the presence of the link and evaluate the surrounding context.
* **Evidence**: In `v2`, UBL customer service containing a `bit.ly` link failed regression (phishing with $91.51\%$ confidence). In `v3`, after adding shortened link HAM, this benchmark successfully **PASSED** (classified as safe with $99.71\%$ confidence).
* **Limitation**: Hand-crafting high-quality hard negatives is time-consuming and requires strict validation to prevent label noise.

---

### Q7: Why did you use "Template-Family splitting" instead of standard random splits?
* **What is it?**: A dataset partitioning method where similar templates (derived from the same source structure) are grouped together and allocated as a unit to either the training set or the testing set.
* **Why did we use it?**: Under standard random splitting, one version of a Zong promo template might end up in the training set and another slightly different version (e.g. price changed from Rs 50 to Rs 80) in the test set. The model would achieve near 100% test accuracy by simple rote-memorization rather than learning generalizeable context.
* **How does it work?**: A template family identifier is assigned to every template (e.g., `readycash_alerts`). The split algorithm hashes the families and maps them to splits:

$$\mathcal{F}_{\text{train}} \cap \mathcal{F}_{\text{test}} = \emptyset$$

* **Evidence**: Our evaluation script verified `[Leakage Check] PASSED` showing 118 train families and 30 test families with zero overlap.
* **Limitation**: Requires manual curation to tag template families in the dataset metadata.

---

### Q8: Is your dataset synthetic or real-world collected?
* **Defense**: We maintain strict academic integrity. The PakScam dataset is primarily **template-derived synthetic data** (140 base templates + 65 augmentations), labeled with `is_synthetic = True`. However, we integrated **15 real-world user-observed seeds** (labeled `is_synthetic = False`), representing actual smishing lures and transaction notices observed in the wild. We do not claim this is a large-scale real-world corpus. It serves as a benchmark and proof-of-concept for domain adaptation within the scope of this Final Year Project.

---

### Q9: Why can't Accuracy alone evaluate the performance of this system?
* **Defense**: Accuracy represents the ratio of correct predictions to total samples:

$$\text{Accuracy} = \frac{\text{TP} + \text{TN}}{\text{TP} + \text{TN} + \text{FP} + \text{FN}}$$

Under severe class imbalance (where HAM is $90\%$ of the data), a model that predicts `"safe"` for all inputs achieves $90\%$ accuracy while catching $0\%$ of threats. In cybersecurity, we must track **Recall** (to ensure threats are caught) and **False Positive Rate** (to ensure user alerts are not flooded with false alarms). Accuracy masks these critical trade-offs.

---

### Q10: How does the LIME highlight card work on the Flutter client if LIME is not executed in real-time?
* **Defense**: Running the formal LIME perturbation algorithm (generating 500 mutated strings and running inference on each) on a CPU backend takes **1.5s - 2.5s**, violating our real-time API SLA. 
  * Therefore, we implement **static indicator mapping**: the backend `AnalysisService` identifies warning indicators (e.g., `url_detected`, `urgency_language`) using regular expressions and returns them in the API response.
  * The Flutter client's `ApiAnalysisRepository` maps these indicators to local keyword weights. The `LimeHighlightCard` widget receives these weights and draws opacity highlights directly over the matching terms, bypassing LIME's execution latency while delivering the same explanatory visual output.
