# ONNX Model Export and Validation Report

This report documents the export of the champion fine-tuned SMS threat analysis model to ONNX format and verifies the mathematical equivalence of the exported model compared to the original PyTorch model.

---

## 1. Export Overview
* **Champion Model Used:** `distilbert_pakscam_v3` (Fine-tuned DistilBERT on localized Pakistani SMS datasets).
* **Export Strategy:** Conversion of PyTorch model parameters and network topology into ONNX format via `torch.onnx.export` with dynamic axes to support variable batch sizes and input sequence lengths on mobile devices.
* **Target Environment:** Android CPU/GPU execution via the `onnxruntime_flutter` package.
* **Quantization Status:** Float32 (Unquantized). Quantization is deferred to native runtime compilation checks or next-phase optimizations.

---

## 2. Reproducibility & Export Execution
The export process is fully reproducible from the repository using the script [`export_to_onnx.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/export_to_onnx.py).

### Command to Reproduce Export:
```bash
# Run from the backend/ directory with Python UTF-8 mode active
python -X utf8 scripts/export_to_onnx.py
```

### Export Pipeline Operations:
1. **Model Instantiation:** Loads PyTorch weights and configuration from [`distilbert_pakscam_v3`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/models/distilbert_pakscam_v3) using Hugging Face `AutoModelForSequenceClassification` and set to evaluation mode (`model.eval()`).
2. **Graph Tracing:** Constructs dummy tensor inputs (`input_ids` and `attention_mask`) from a sample text to trace the neural network forward pass graph.
3. **ONNX Graph Generation:** Calls `torch.onnx.export` to serialize the PyTorch structure. The export utilizes dynamic axes mapping:
   - `input_ids`: dynamic dimensions `[batch_size, sequence_length]`
   - `attention_mask`: dynamic dimensions `[batch_size, sequence_length]`
   - `logits`: dynamic dimension `[batch_size]`
4. **Opset Level:** Target opset version set to `14` (supported natively by Android CPU backends).
5. **Asset Preservation:** Tokenizer rules and vocabulary are saved to the deployment target folder using `tokenizer.save_pretrained()`, and supplementary mapping configurations ([`label_mapping.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/models/distilbert_pakscam_v3/label_mapping.json) and [`config.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/models/distilbert_pakscam_v3/config.json)) are copied directly.

---

## 3. Exported Deployment Artifacts
The exported artifacts are stored in a deployment directory separate from the original training directory:
`backend/data/models/distilbert_pakscam_v3_onnx/`

### Artifact Inventory:
* **`model.onnx` (0.7861 MB):** The compiled ONNX network graph.
* **`model.onnx.data` (255.4199 MB):** The separate external weights data binary (automatically split during PyTorch Dynamo-based tracing).
* **`tokenizer.json` (0.6787 MB):** The full subword WordPiece tokenizer schema.
* **`tokenizer_config.json` (0.0005 MB):** Preprocessing parameters (lower case matching, max lengths).
* **`config.json` (0.0007 MB):** Transformer model layer, vocabulary, and token dimension settings.
* **`label_mapping.json` (0.0001 MB):** Index to text label mappings (`0: ham`, `1: spam`).

---

## 4. PyTorch vs. ONNX Inference Equivalence Verification
To confirm that model behaviors are identical after conversion, a side-by-side comparative analysis was executed.

### Validation Script:
The verification is executed using [`validate_onnx.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/scripts/validate_onnx.py):
```bash
# Run from the backend/ directory
python -X utf8 scripts/validate_onnx.py
```

### Evaluation Dataset Composition:
* **Regression Subset:** 14 highly sensitive localized regression cases covering Pakistani banking receipts, ATM transactions, telecom subscriptions, BISP scams, OTP harvesting, and Roman Urdu.
* **In-Domain Subset:** 50 randomly sampled SMS texts from the UCI test dataset ([`test.csv`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/processed/test.csv)).
* **Total Comparative Samples:** 64 instances.

### Comparative Metrics Summary:
* **Class Equivalence Pass Rate:** **100.00%** (All 64 test samples predict exactly identical classes across PyTorch and ONNX).
* **Class Mismatches:** **0 / 64**
* **Mean Logit Max-Difference:** **\(1.08825 \times 10^{-6}\)**
* **Max Logit Max-Difference:** **\(2.86102 \times 10^{-6}\)**
* **Mean Probability Difference:** **\(2.98405 \times 10^{-8}\)**
* **Max Probability Difference:** **\(5.36442 \times 10^{-7}\)**

The minuscule differences in logits are well within the floating-point tolerance limit of **\(10^{-4}\)** and arise purely from single-precision float representation and minor operator reordering during backend compilation.

---

## 5. Side-by-Side Representative Test Cases
Below are the exact comparison logs for representative SMS examples:

### Case 1: Legitimate UBL IBFT Transaction (Source: `regression:ubl_ibft_receipt`)
* **SMS Text:** `PKR 5,030 received from ILAM UL DIN* in your UBL A/C *5034 on 04-AUG-2026 19:53 via IBFT. Tx ID 6940522193. For info: 111825888.`
* **PyTorch Output:** Label: `ham` | Confidence: `99.19%` | Logits: `[2.3010587, -2.5098838]`
* **ONNX Output:** Label: `ham` | Confidence: `99.19%` | Logits: `[2.3010583, -2.5098838]`
* **Equivalence:** `TRUE` (Logit Difference: \(4.77 \times 10^{-7}\))

### Case 2: UBL ATM Debit Alert (Source: `regression:ubl_atm_debit`)
* **SMS Text:** `JUNAID AHMED A/C *5034 is debited with PKR 5,000 on 04/08/26 at 20:13 from ATM. For info: 111825888.`
* **PyTorch Output:** Label: `ham` | Confidence: `98.62%` | Logits: `[2.0410020, -2.2295599]`
* **ONNX Output:** Label: `ham` | Confidence: `98.62%` | Logits: `[2.0410015, -2.2295596]`
* **Equivalence:** `TRUE` (Logit Difference: \(4.77 \times 10^{-7}\))

### Case 3: Urgency / Suspicious URL Phishing (Source: `regression:ubl_customer_service_bitly`)
* **SMS Text:** `Dear UBL Customer, You may log your complaints via our Contact Center, Email, Website, Mobile App, Social Media, Branches or visit: https://bit.ly/2WceaFA`
* **PyTorch Output:** Label: `spam` | Confidence: `72.72%` | Logits: `[-0.5078933, 0.4723955]`
* **ONNX Output:** Label: `spam` | Confidence: `72.72%` | Logits: `[-0.5078922, 0.4723941]`
* **Equivalence:** `TRUE` (Logit Difference: \(1.34 \times 10^{-6}\))

### Case 4: Overdue ReadyCash Loan (Source: `regression:readycash_overdue`)
* **SMS Text:** `Your ReadCash is Overdue! Save on the next weekly fee of Rs 160 (applied in 2 days) by repaying your ReadyCash Rs 3151.18 now by dialing *786*4*2#.`
* **PyTorch Output:** Label: `ham` | Confidence: `98.92%` | Logits: `[2.2855901, -2.2346749]`
* **ONNX Output:** Label: `ham` | Confidence: `98.92%` | Logits: `[2.2855896, -2.2346735]`
* **Equivalence:** `TRUE` (Logit Difference: \(1.43 \times 10^{-6}\))

### Case 5: Roman Urdu BISP Scam (Source: `regression:bisp_roman_urdu_scam`)
* **SMS Text:** `BISP ki taraf se 25,000 rupay approved hain. Abhi claim karein 0312-9876543 par call kar ke.`
* **PyTorch Output:** Label: `spam` | Confidence: `99.20%` | Logits: `[-2.3023033, 2.5204217]`
* **ONNX Output:** Label: `spam` | Confidence: `99.20%` | Logits: `[-2.3023028, 2.5204207]`
* **Equivalence:** `TRUE` (Logit Difference: \(9.54 \times 10^{-7}\))

---

## 6. Conclusion
The model export validation test has completed with a **100% success rate**. The mathematical outputs of the ONNX Runtime model align perfectly with the original PyTorch model, resulting in identical verdicts across all local and general SMS patterns. The model is successfully compiled to ONNX format and is ready for the on-device mobile integration phase.
