# MindShield FYP Viva Defense Preparation Guide
## Phase 3.2: NLP Preprocessing & Feature Extraction Engine

> **Document Focus**: Academic Q&A Preparation for BS Computer Science FYP Panel Defense  
> **Target Audience**: External Examiners & Academic Evaluation Committee  

---

### Q1: Why did you decouple Classical NLP Preprocessing from Transformer Preprocessing?
**Answer**:  
Classical machine learning algorithms (e.g., Naive Bayes, Support Vector Machines) rely on bag-of-words or n-gram matrix representations. They suffer from high-dimensional sparsity and benefit from aggressive normalization (lowercasing, stopword removal, stemming/lemmatization, entity placeholders) to collapse vocabulary size.

Conversely, transformer architectures like DistilBERT use subword tokenization (WordPiece) and contextual self-attention mechanisms. Aggressive lowercasing or stemming destroys grammatical nuances, subword token prefixes, URLs, and emotional context (emojis). Therefore, our architecture explicitly separates Classical ML Feature Engineering from Light Transformer Preprocessing.

---

### Q2: What is the empirical vocabulary reduction achieved by Porter Stemming vs Lemmatization on the UCI corpus?
**Answer**:  
Empirical analysis across the 5,148-message cleaned UCI SMS corpus revealed:
- **Raw Vocabulary**: 8,063 unique terms.
- **Porter Stemmed Vocabulary**: 6,713 unique terms (**16.74% reduction**).
- **WordNet Lemmatized Vocabulary**: 7,090 unique terms (**12.07% reduction**).

Stemming achieves greater dimensional collapse by stripping suffixes algorithmically, whereas lemmatization preserves valid dictionary base forms (lemmas).

---

### Q3: How does your pipeline ensure future compatibility with the PakScam dataset?
**Answer**:  
The pipeline relies entirely on declarative, configuration-driven objects (`NLPPreprocessingConfig`). No dataset-specific regex rules or hardcoded text mappings are embedded inside the processing classes. The exact same normalizer, tokenizer, and vectorizers accept Roman Urdu/Pakistani SMS payloads (e.g., `0300...` numbers, BISP keywords) without structural code modifications.

---

### Q4: How are entity tokens like URLs and phone numbers handled in threat payloads?
**Answer**:  
Entity identifiers are critical threat indicators. In Classical ML mode, URLs are substituted with `[URL]`, emails with `[EMAIL]`, and phone numbers with `[PHONE]`. This preserves entity presence frequency across n-gram feature vectors while preventing high-cardinality noise from unique domain names or phone numbers.

---

### Q5: How do CountVectorizer and TF-IDF Vectorizer differ in feature extraction?
**Answer**:  
- **CountVectorizer** computes term frequency $tf(t, d)$, representing the raw occurrence count of term $t$ in document $d$.
- **TfidfVectorizer** weights term frequency by inverse document frequency:
  $$\text{TF-IDF}(t, d, D) = tf(t, d) \times \log\left(\frac{1 + |D|}{1 + df(t)}\right) + 1$$
  This penalizes ubiquitous terms that appear across many messages while amplifying distinct threat keywords (e.g., `claim`, `lottery`, `bisp`).

---

### Q6: What design pattern did you use to make the vectorizer extensible for future neural embeddings?
**Answer**:  
We implemented the **Strategy Pattern** combined with an **Abstract Base Class (`BaseVectorizer`)**. `NLPVectorizer` acts as a unified manager wrapping `CountVectorizerWrapper` and `TfidfVectorizerWrapper`. Future dense embedding models (Word2Vec, FastText, sentence-transformers) can be integrated by extending `BaseVectorizer` without modifying existing pipeline call sites.

---

### Q7: How is the NLP preprocessing pipeline serialized for production deployment?
**Answer**:  
The pipeline exports its complete declarative state as JSON (`nlp_pipeline_config.json`), while fitted vectorizers serialize as pickle artifacts using `.save()` and `.load()`. This guarantees exact feature alignment during real-time FastAPI inference.

---

### Q8: What processing throughput does your pipeline achieve?
**Answer**:  
On standard CPU hardware, the Python pipeline achieves a throughput of **~870 to 910 documents per second**, processing the full 5,148-message corpus in under 6 seconds.

---

### Q9: How are emojis handled in your text normalization engine?
**Answer**:  
Emojis are processed based on the configured `emoji_policy`:
- `"demojize"`: Converts Unicode emojis into text representations (e.g., `🎁` $\rightarrow$ `:wrapped_gift:`).
- `"remove"`: Strips Unicode emojis.
- `"preserve"`: Keeps emojis intact for transformer subword tokenizers.

---

### Q10: How do you verify the correctness of the NLP preprocessing pipeline?
**Answer**:  
Verification is enforced through 11 automated unit and integration tests (`tests/test_preprocessing_pipeline.py`) covering config presets, entity replacement, emoji handling, tokenization, stemming/lemmatization metrics, vectorizers, serialization, and batch execution. The test suite achieves 100% pass rate and $\ge 90\%$ code coverage.
