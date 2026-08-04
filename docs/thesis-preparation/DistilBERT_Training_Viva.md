# MindShield FYP Viva Defense Preparation Guide
## Phase 3.4: DistilBERT Transformer Fine-Tuning Pipeline

> **Document Focus**: Academic Q&A Preparation for BS Computer Science FYP Panel Defense  
> **Target Audience**: External Examiners & Academic Evaluation Committee  

---

### Q1: Why did you choose DistilBERT over standard BERT-base or RoBERTa?
**Answer**:  
DistilBERT was selected due to its optimal balance between classification performance and computational efficiency for real-time mobile/API cybersecurity applications:
1. **Model Parameter Reduction**: DistilBERT contains 66 million parameters (40% fewer than BERT-base's 110M parameters).
2. **Speed & Latency**: Executes inference 60% faster than BERT-base while retaining 97% of BERT's language understanding capability on GLUE benchmarks.
3. **Low Resource Footprint**: Memory requirements during inference are under 260 MB, enabling smooth deployment on single-instance API servers.

---

### Q2: Why is light non-destructive preprocessing necessary for DistilBERT fine-tuning?
**Answer**:  
Transformers rely on WordPiece subword tokenization and positional embeddings to learn bidirectional context. Aggressive classical preprocessing (stemming, stopword removal, or lowercasing entity placeholders) destroys positional context and subword morphology. Preserving exact character structure (capitalization, emojis, phone numbers, URLs) allows DistilBERT's multi-head self-attention mechanisms to attend to critical threat patterns.

---

### Q3: How did DistilBERT perform compared to the best classical baseline from Phase 3.3?
**Answer**:  
DistilBERT outperformed the best classical model (`linear_svm_count`) across every key metric:
- **Test Accuracy**: `98.83%` vs `98.25%` (**+0.58%**)
- **Test F1-Score**: `95.16%` vs `92.56%` (**+2.60%**)
- **Test Recall**: `92.19%` vs `87.50%` (**+4.69%**)
- **ROC-AUC**: `0.9961` vs `0.9908` (**+0.53%**)

The +4.69% gain in Recall is especially vital for cybersecurity because it directly reduces False Negatives (missed phishing attacks).

---

### Q4: What optimization hyper-parameters were used during fine-tuning?
**Answer**:  
- **Optimizer**: AdamW ($\beta_1=0.9$, $\beta_2=0.999$, $\epsilon=10^{-8}$, $\text{weight\_decay}=0.01$).
- **Learning Rate**: $2 \times 10^{-5}$ with linear learning rate warmup over the first 10% of total training steps (`warmup_ratio=0.1`).
- **Batch Size**: 16 text sequences per step.
- **Epochs & Early Stopping**: 3 epochs with patience of 2 epochs monitoring validation F1-score.

---

### Q5: How did you implement Early Stopping during training?
**Answer**:  
At the end of every epoch, the trainer evaluates validation loss and validation F1-score on `val.csv`. If validation F1 does not improve over `patience=2` consecutive epochs, training terminates early and weights from the epoch with the highest validation F1 score are restored.

---

### Q6: How does mixed precision (FP16) training benefit transformer fine-tuning?
**Answer**:  
Mixed Precision training utilizes 16-bit floating point arithmetic (`torch.cuda.amp.autocast`) for forward and backward passes while maintaining 32-bit master weights. This cuts GPU memory consumption in half and accelerates tensor core execution speed up to $2\times$ without loss of precision.

---

### Q7: What artifacts are saved when DistilBERT completes training?
**Answer**:  
The trainer serializes the complete Hugging Face model suite under `backend/data/models/distilbert/`:
1. `model.safetensors` (or `pytorch_model.bin`) — trained weights.
2. `config.json` — architecture configuration.
3. `tokenizer.json` / `vocab.txt` — subword tokenizer files.
4. `label_mapping.json` — `{0: "ham", 1: "spam"}`.
5. `training_history.json` & `metrics.json` — full epoch loss history and evaluation metrics.

---

### Q8: How does your pipeline maintain dataset-agnostic reusability for the future PakScam dataset?
**Answer**:  
The `DistilBERTPipeline` ingests standardized pandas DataFrames containing `text` and `label` columns. All tokenization, PyTorch DataLoader construction, and evaluation logic are configuration-driven, enabling the exact same code to fine-tune DistilBERT on PakScam without modification.
