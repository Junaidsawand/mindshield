# MindShield — Dataset & Evaluation Metrics Viva Guide

> **Module**: Dataset Methodology, Corpus Selection & Performance Metrics  
> **Focus**: SMS Spam Collection, Smishing Datasets, Class Imbalance, Precision/Recall/F1  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding

### Q1: What dataset was selected for model evaluation and why?
**Model Answer:**  
Primary benchmarking utilizes the **SMS Spam Collection Dataset** (Almeida et al., 2011), containing 5,574 real-world English SMS messages (4,827 legitimate, 747 spam/smishing). This dataset is universally accepted as the benchmark corpus in SMS classification literature. To address modern smishing tactics (such as cryptocurrency lures and mobile banking impersonation), the corpus was augmented with contemporary 2023–2025 smishing samples collected from public threat intelligence feeds (SABRIC, PhishTank).

---

### Q2: Why is Accuracy a poor metric for SMS spam classification?
**Model Answer:**  
The SMS Spam Collection dataset exhibits significant **class imbalance** (~87% ham, ~13% spam). A naive classifier that predicts every message as "legitimate" achieves 87% accuracy while failing to catch a single threat. Therefore, evaluation relies on Precision, Recall, F1-Score, and Confusion Matrices.

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

- **Domain Impact**: In cybersecurity, False Negatives (missing a scam) are significantly more dangerous than False Positives (flagging a safe message as suspicious).

---

## Section B — Design Decision Justification

### Q3: How do you handle class imbalance during model training?
**Model Answer:**  
Class imbalance is addressed through three techniques:
1. **SMOTE / Random Oversampling**: Synthetic minority oversampling balances class distributions in the training split.
2. **Weighted Cross-Entropy Loss**: Assigning a higher loss penalty to misclassified minority (scam) samples forces the gradient optimizer to prioritize threat detection.
3. **Stratified K-Fold Cross-Validation**: Ensures each validation fold maintains the original class distribution ratio.

---

## Section C — Implementation & Technical Depth

### Q4: Walk through the evaluation metric breakdown for MindShield's target pipeline.
**Model Answer:**  

| Metric | Target Benchmark | Academic Justification |
|---|---|---|
| **Precision** | $\ge 0.95$ | Minimizes false alarms on legitimate personal messages. |
| **Recall (Sensitivity)** | $\ge 0.97$ | Ensures critical smishing threats are captured. |
| **F1-Score** | $\ge 0.96$ | Harmonic mean providing a single robust performance score. |
| **Inference Latency** | $< 500\text{ ms}$ | Maintains responsive mobile UX. |

---

## Section D — Limitations, Risks & Future Work

### Q5: What are the main limitations of public SMS datasets for real-world deployment?
**Model Answer:**  
Public datasets suffer from **temporal degradation** (older message templates don't reflect modern AI-generated phishing scripts) and **geographic bias** (Almeida dataset features predominantly UK/US text structures). Future work requires continuous dataset curation via crowd-sourced user reports and federated learning to update threat signatures dynamically without violating user privacy.

---
*MindShield Dataset Viva Guide · Final Year Project 2026*
