# MindShield FYP Viva Defense Preparation Guide
## Phase 3.3: Classical Machine Learning Baseline Models

> **Document Focus**: Academic Q&A Preparation for BS Computer Science FYP Panel Defense  
> **Target Audience**: External Examiners & Academic Evaluation Committee  

---

### Q1: Why did you implement classical machine learning baselines before fine-tuning DistilBERT?
**Answer**:  
Establishing baseline performance using classical machine learning models (Multinomial Naive Bayes, Logistic Regression, Linear SVM, Random Forest) is a foundational principle of scientific rigor in machine learning research. Baselines provide:
1. Empirical lower bounds for accuracy, precision, recall, and F1-score.
2. Computational benchmarks for inference latency and model size.
3. Verification that deep transformer fine-tuning in Phase 3.4 produces statistically significant performance gains justifying higher compute costs.

---

### Q2: Which classical model achieved the highest performance on the test corpus, and why?
**Answer**:  
`Linear SVM` paired with `CountVectorizer` (`linear_svm_count`) achieved the highest overall performance:
- **Test Accuracy**: `98.25%`
- **Precision**: `98.25%`
- **Recall**: `87.50%`
- **F1-Score**: `92.56%`
- **ROC-AUC**: `0.9908`

Linear Support Vector Machines excel in high-dimensional text classification because SMS word occurrence matrices are sparse and linearly separable in high-dimensional n-gram feature spaces.

---

### Q3: Why did CountVectorizer outperform TF-IDF Vectorizer for Linear SVM and Naive Bayes in your experiments?
**Answer**:  
SMS messages are concise (typically 1 to 2 sentences). In short text payloads, term repetition within a single message is rare, rendering term frequency weighting nearly binary. CountVectorizer preserving raw n-gram occurrence counts provided sharper boundary margins for SVM hyperplanes and Naive Bayes conditional probability estimates compared to sublinearly scaled TF-IDF weights.

---

### Q4: Why did you use 5-Fold Stratified Cross-Validation instead of standard K-Fold CV?
**Answer**:  
The UCI SMS Spam Collection is highly class-imbalanced (~87.5% ham vs ~12.5% spam). Standard K-Fold CV risks creating folds with fluctuating spam ratios. **Stratified K-Fold CV** guarantees that every fold preserves the exact 87.5:12.5 class ratio, providing unbiased estimates of model mean performance ($\mu$) and variance ($\sigma$).

---

### Q5: What features were identified as strongest spam indicators across models?
**Answer**:  
Feature importance analysis extracted key threat tokens across models:
- **Random Forest Gini Importance**: `claim`, `prize`, `txt`, `urgent`, `call`.
- **Logistic Regression Coefficients**: `0800`, `claim`, `prize`, `free`, `http`.
- **Naive Bayes Log-Likelihood Ratios**: `0800`, `claim`, `urgent`, `nokia`, `award`.

---

### Q6: How is probability estimation handled for Linear Support Vector Machines?
**Answer**:  
Standard `LinearSVC` outputs uncalibrated decision boundary margins (distance to hyperplane) rather than probabilities. To compute ROC-AUC and PR-AUC metrics, we wrapped `LinearSVC` inside `CalibratedClassifierCV` using Platt scaling (sigmoid calibration) to generate valid probability distributions ($P(y=1|x)$).

---

### Q7: What additional metrics did you evaluate beyond Accuracy and F1-Score?
**Answer**:  
We evaluated 11 comprehensive metrics: Accuracy, Precision, Recall, F1-Score, Macro F1, Weighted F1, ROC-AUC, PR-AUC (`average_precision_score`), Matthews Correlation Coefficient (MCC), Cohen's Kappa, Training Time (s), Prediction Time (s), and Model Size (MB).

---

### Q8: What are MCC and Cohen's Kappa, and why are they important for imbalanced SMS data?
**Answer**:  
- **Matthews Correlation Coefficient (MCC)** evaluates all four confusion matrix quadrants (TP, TN, FP, FN), ranging from -1 to +1. `linear_svm_count` achieved an MCC of **0.9184**, proving high reliability.
- **Cohen's Kappa** measures inter-rater agreement adjusted for chance classifier agreement. `linear_svm_count` achieved a Kappa of **0.9160**.

---

### Q9: How is the best classical model serialized and exported?
**Answer**:  
The trainer automatically identifies the top-performing model and copies its serialized joblib artifacts (`model.joblib`, `vectorizer.joblib`, `pipeline.json`, `metadata.json`) to `backend/data/models/best_classical_model/`.

---

### Q10: How does your baseline architecture ensure dataset-agnostic reusability for PakScam?
**Answer**:  
The `BaselineMLPipeline` depends entirely on abstract DataFrames containing `text` and `label` columns. It contains zero hardcoded vocabulary rules or UCI-specific assumptions, allowing the exact same pipeline to train baseline classifiers on the future PakScam dataset without code changes.
