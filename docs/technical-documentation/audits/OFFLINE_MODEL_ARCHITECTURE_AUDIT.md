# Offline Model Deployment and Architecture Audit

This audit evaluates the feasibility, model performance, technical requirements, and architectural impact of migrating the MindShield SMS threat analysis pipeline from a server-side FastAPI deployment to a fully offline, on-device Android execution model.

---

## 1. Verified Model Benchmarks & Comparison
Below is the comparative performance data extracted directly from the repository's evaluation records:
* [`v3_evaluation_results.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/v3_evaluation_results.json)
* [`pakscam_v2_model_comparison.json`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/data/metadata/pakscam_v2_model_comparison.json)

### Comparative Performance Table

| Metric / Benchmark | distilbert-uci-v1 | distilbert-uci-v2 | distilbert-pakscam-v1 | distilbert-pakscam-v2 | distilbert-pakscam-v3 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **In-Domain F1-Score (UCI Test)** | 88.89% | 95.16% | 96.00% | 94.21% | 95.08% |
| **In-Domain Precision (UCI Test)** | 98.11% | 98.33% | 98.36% | 100.0% | 100.0% |
| **In-Domain Recall (UCI Test)** | 81.25% | 92.19% | 93.75% | 89.06% | 90.62% |
| **Pak Scams Spam Recall / F1** | 79.25% | 98.11% | 98.11% | 86.79% | 100.0% |
| **Pak Scams ALL HAM (FPR)** | **82.76% (FAIL)** | **94.25% (FAIL)** | **93.10% (FAIL)** | 9.20% | **3.45% (BEST)** |
| **Pak Banking HAM (FPR)** | 95.12% | 100.0% | 100.0% | 2.44% | 2.44% |
| **Pak Telecom HAM (FPR)** | 70.00% | 83.33% | 80.00% | 20.00% | 3.33% |
| **Roman Urdu HAM (FPR)** | 40.91% | 77.27% | 72.73% | 0.00% | 13.64% |
| **Roman Urdu SPAM (Recall)** | 40.00% | 93.33% | 93.33% | 53.33% | 100.0% |
| **Regression Pass Rate** | N/A | N/A | 35.71% (5/14) | 78.57% (11/14) | **92.86% (13/14)** |
| **Mean Inference Latency (ms)** | ~34.29 ms | ~30.41 ms | 41.95 ms | 60.80 ms | 57.62 ms |

---

## 2. Model Selection Rationale
### Champion Candidate: `distilbert_pakscam_v3`

Based on repository evidence, `distilbert_pakscam_v3` is the strongest validated candidate for deployment. The model must be selected due to the following facts:
1. **Critical False Positive Reduction:** Deep learning models trained solely on Western data (`uci-v1`, `uci-v2`) or early local fine-tunes (`pakscam-v1`) completely fail to generalize to localized Pakistani legitimate messages. They exhibit disastrous False Positive Rates (FPR) on harmless texts, flagging **82.76% to 94.25% of Pakistani HAM** as dangerous. In contrast, `distilbert_pakscam_v3` leverages specialized local datasets and oversampling (Mix-C Pak 3x) to suppress the overall FPR to **3.45%** (only 3 False Positives out of 87 unique samples).
2. **Superior Local Smishing Detection:** It achieves **100% recall (F1: 1.0)** on Pakistani Spam and **100% recall** on Roman Urdu Spam, outperforming `pakscam_v2` which catches only 86.79% and 53.33% respectively.
3. **Regression Stability:** It passes **92.86% (13 out of 14)** of diagnostic regression cases. It successfully classifies complex Pakistani banking receipts, ATM alerts, subscription notifications, and Roman Urdu scams. The sole failure is `zong_engage_prize_lang` (a borderline promotional message containing "win prize" triggers and a URL).
4. **Latency Verification:** It clocks a mean CPU prediction latency of **57.62 ms**, satisfying the maximum latency promotion gate requirement of **<= 60.0 ms** (unlike `pakscam_v2` which fails at 60.80 ms).

---

## 3. Tokenizer & Configuration Compatibility with ONNX Export
1. **Tokenizer Format:** The models use standard Hugging Face tokenizers configured under the `BertTokenizer` class (WordPiece algorithm). The presence of `tokenizer.json` and `tokenizer_config.json` files containing complete vocabularies, lowercase conversions (`do_lower_case: true`), and special control characters (`[CLS]`, `[SEP]`, `[PAD]`, `[UNK]`) ensures full compatibility with on-device ONNX runtime tokenization libraries.
2. **Model Graph Structure:** The model configurations (`config.json`) follow the standard `DistilBertForSequenceClassification` architecture with 6 layers, 12 attention heads, and a vocabulary size of 30,522. The model outputs a simple 2-dimensional tensor of logits corresponding to the classification labels (`0: ham, 1: spam`). This topology is natively supported by `torch.onnx.export` and Hugging Face Optimum.

---

## 4. Required Deployment Files
To run the target local inference on Android via ONNX Runtime, the following assets are required:
1. **`model_quantized.onnx`:** The optimized and quantized 8-bit integer (INT8) representation of the model graph, converted from `model.safetensors`.
2. **`vocab.txt`:** The raw vocabulary file containing all 30,522 tokens (derived from `tokenizer.json`) to map string words/subwords to tensor inputs on the device.
3. **`label_mapping.json`:** The JSON mapping dict (`0: ham, 1: spam`) to translate the integer indices of the output logits to labels.
4. **Local Feature Heuristics:** The regex/keyword checks for indicator extraction (porting `validators.py` to Dart).

---

## 5. Weights File Presence & Verification
* **Fact Check:** No Transformer model is missing its weights.
* **Weights Location:** In all five versions (`distilbert_pakscam_v1`, `distilbert_pakscam_v2`, `distilbert_pakscam_v3`, `distilbert_uci_v1`, `distilbert_uci_v2`), the fine-tuned model weights reside in the Hugging Face standard **`model.safetensors`** binary format directly within their respective subdirectories inside `backend/data/models/`.
* **Classical Baselines:** The `best_classical_model` folder uses joblib binaries (`model.joblib` and `vectorizer.joblib`) instead of Safetensors, as it is a classical SVM model.

---

## 6. Current FastAPI Inference Flow
The current server-side SMS threat analysis flow is structured as follows:
```
[Flutter App Client]
        │  (HTTP POST /api/v1/analyze)
        ▼
[FastAPI Router: app/routers/v1/analysis.py]
        │  (Extracts request_id; routes request)
        ▼
[AnalysisService: app/services/analysis_service.py]
        │  1. is_valid_message(message) -> validates string length & contents
        │  2. sanitise_message(message) -> Normalises spaces & NFKC Unicode
        │  3. compute_message_features(message) -> Computes 9 rule-based indicators
        │  4. Delegates classification execution
        ▼
[InferenceService: app/services/inference_service.py]
        │  (latency tracking; handles fallback recovery if primary loader errors)
        ▼
[HuggingFaceModelLoader: app/core/model_loader.py]
        │  1. Normalises text using NLPPreprocessingPipeline
        │  2. Tokenizes text using AutoTokenizer (max_length=128, padding, truncation)
        │  3. Runs PyTorch model forward pass on CPU/GPU
        │  4. Calculates probabilities via Softmax over output logits
        │  5. Constructs ModelPrediction DTO (label, confidence, explanation)
        ▼
[AnalysisService]
        │  (Builds list of ThreatIndicator schemas using computed features + weights)
        ▼
[FastAPI Router]
        │  (Wraps result inside APIResponse envelope)
        ▼
[Flutter App Client]
```

---

## 7. Current Flutter Analysis Flow
In the current architecture, Flutter delegates all machine learning work to the FastAPI backend. It contains two parallel paths:

### A. Foreground (Manual UI Check / Detail View)
1. **Trigger:** The user opens the SMS Threat Analysis screen, which instantiates `AnalysisProvider` ([`analysis_provider.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/analysis_provider.dart)).
2. **Data Call:** The provider invokes `ApiAnalysisRepository.getAnalysis()` ([`api_analysis_repository.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/data/api_analysis_repository.dart)).
3. **HTTP Request:** The repository formats the payload with metadata (app version, locale) and executes a POST request via `Dio` to `AppConstants.analyzeEndpoint`.
4. **Parsing & Domain Mapping:** The JSON response is decoded and mapped into a domain-level `AnalysisResult` object. The backend's string-based indicators are parsed into UI-compatible lists of `SuspiciousKeyword` (with static weights) and `PsychologicalTactic` items.
5. **State Notification:** The provider updates its state and calls `notifyListeners()`, causing the UI widgets to refresh and highlight detected keywords.

### B. Background (SMS Interception / Notification)
1. **Trigger:** The Android BroadcastReceiver intercepts an incoming SMS. The background isolate triggers `AnalysisService.analyzeMessage()` ([`analysis_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/analysis_service.dart)).
2. **Network with Retry:** It attempts a POST request via `Dio` to the backend. In case of timeout or connection errors, it retries up to **2 times** with exponential backoff.
3. **Verdict Mapping:** Upon receiving the analysis result, it parses the threat level and indicators to determine the local security status.
4. **SQLite Persistence:** It updates the local SQLite database using `DatabaseHelper` (e.g. setting `ai_status`, `is_spam = 1`, `spam_status = 'quarantined'`).
5. **UI Trigger:** Calls `SmsBackgroundService.instance.notifyListeners()`, instructing active foreground screens (like `DashboardProvider`) to reload their metrics.

---

## 8. Current Persistence Architecture
Persistence is handled entirely on the mobile device using **SQLite** via the `sqflite` package, managed by `DatabaseHelper` ([`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart)).

* **Database Table:** `sms_messages`
* **Column Schema:**
  - `id`: TEXT PRIMARY KEY
  - `sender`: TEXT NOT NULL
  - `body`: TEXT NOT NULL
  - `timestamp`: INTEGER NOT NULL (Milliseconds epoch)
  - `ai_status`: TEXT NOT NULL (`'pending'`, `'safe'`, `'suspicious'`, `'scam'`)
  - `is_read`: INTEGER NOT NULL (0 or 1)
  - `confidence_score`: REAL (Float from backend model confidence)
  - `detected_threats`: TEXT NOT NULL (JSON-encoded array of active threat names, e.g. `["credential_request", "url_detected"]`)
  - `is_spam`: INTEGER NOT NULL DEFAULT 0
  - `spam_risk_level`: TEXT (`'low'`, `'medium'`, `'high'`, `'critical'`)
  - `spam_attack_type`: TEXT (`'phishing'`, `'prizeScam'`, `'investmentFraud'`, `'piiHarvesting'`, `'smishing'`, `'socialEngineering'`)
  - `spam_status`: TEXT (`'quarantined'`, `'blocked'`, `NULL`)
  - `quarantined_at`: INTEGER (Epoch timestamp, `NULL` if safe)

All data synchronization between the analysis results and the inbox dashboard is accomplished by querying the database metrics and updating UI state lists.

---

## 9. Current Explainable AI (XAI) Implementation
True mathematical Explainable AI (such as LIME or SHAP perturbation weights) is **not implemented** in the codebase. The system instead uses a **Heuristic Feature Attribution (HFA)** approach:
1. **Backend Indicator Evaluation:** The backend checks the SMS text for matches against keyword dictionaries and regex patterns inside [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py).
2. **Static Weighting:** Static weights are assigned to these features in a hardcoded mapping (`_INDICATOR_MAP`) in [`analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) (e.g. `credential_request` is mapped to `critical`, `url_detected` to `high`, `financial_keywords` to `medium`).
3. **Response Packaging:** The list of matching threat indicators (along with their static weights and details) is returned in the API response.
4. **UI Fallback Highlighting:** On the Flutter side inside `lime_highlight_card.dart`, the app runs local string search matches on the SMS body for the keywords associated with the flagged indicators and highlights them inline to simulate localized token weights.
5. **Formatted Explanations:** The explanation text returned by the model is a fixed template string outlining the confidence score or heuristic list.

---

## 10. Required Dependency Changes for Offline Inference
To support offline, local Android inference, the project configuration must undergo the following changes:

### A. Flutter (`frontend/pubspec.yaml`)
1. **`onnxruntime_flutter`:** Add the library to load and execute the ONNX runtime model graph on Android via native bindings.
2. **`bert_tokenizer`:** Add a tokenizer library or include a custom Dart implementation of the WordPiece tokenization logic.

### B. Python Export Environment (`backend/requirements.txt`)
1. **`onnx` & `onnxruntime`:** Necessary to export PyTorch weights to ONNX format.
2. **`optimum[onnxruntime]`:** Used to perform ONNX optimization and INT8 quantization.

### C. Android Build Configurations
1. **`android/app/build.gradle`:** Configure C++ toolchain configurations and architecture splits (ABI filters for `armeabi-v7a`, `arm64-v8a`, `x86`, `x86_64`) to include ONNX Runtime shared library `.so` packages.

---

## 11. Risks & Blockers for Mobile Execution
1. **Model Size and RAM Limits (OOM):** The unquantized `model.safetensors` files are **267.83 MB**. Allocating ~260MB in RAM for model execution on low-end or budget Android devices is highly likely to trigger Out-Of-Memory (OOM) app crashes by the OS.
2. **CPU Latency & Battery Drain:** Running standard FP32 Transformer forward passes on mobile CPUs without hardware acceleration will cause high latency (>100ms) and intense battery drain. INT8 quantization is an absolute necessity, but it may cause validation score degradations that must be audited.
3. **Lack of Repository Abstractions:** The Flutter frontend does not have an abstract `AnalysisRepository` class. `AnalysisProvider` directly references the concrete `ApiAnalysisRepository` class. To swap the data provider to a local ONNX model, the repository architecture must be refactored to introduce a clear interface.
4. **Porting Heuristics to Dart:** The rule-based indicators are computed in the Python FastAPI backend (`validators.py`). For offline operation, the regex rules and keyword dictionaries must be completely rewritten in Dart to preserve the XAI highlight features and tactic categorization.
5. **Background Isolate Bottleneck:** Background SMS interception runs in a separate Dart isolate. Loading the model weights into memory within the background thread while the main UI thread also needs it can result in duplicate memory allocation (2x model size in RAM).

---

## 12. Recommended Final Architecture
To enable a robust, high-performance offline smishing analysis on Android, the following final architecture is recommended:

```
                  ┌──────────────────────────────────────────────┐
                  │                 Flutter UI                   │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                     ┌──────────────────────────────────────┐
                     │     <<interface>> AnalysisRepo       │
                     └───────────────────┬──────────────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        ▼                                 ▼
         ┌──────────────────────────────┐  ┌──────────────────────────────┐
         │    LocalAnalysisRepository   │  │    ApiAnalysisRepository     │
         │   (Primary Offline Engine)   │  │  (Online Backup / Staging)   │
         └──────────────┬───────────────┘  └──────────────────────────────┘
                        │
       ┌────────────────┴────────────────┐
       ▼                                 ▼
┌──────────────┐                 ┌──────────────┐
│  Dart Isolate│                 │  SQLite DB   │
│  (Background)│                 │(DatabaseHelp)│
└──────┬───────┘                 └───────────┬──┘
       │                                     │
       │  1. Run LocalFeatureExtractor       │
       │  2. WordPiece Tokenizer             │
       │  3. ONNX Runtime Inference          │
       │  4. Predict Verdict                 │
       ▼                                     ▼
[Quantized INT8 ONNX Model (~67MB)] ◄────────┘
```

### Key Implementation Guidelines:
1. **Interface Segregation:** Refactor the frontend to define an abstract `AnalysisRepository` class. Inject `LocalAnalysisRepository` as the default provider, falling back to `ApiAnalysisRepository` only if native assets are corrupted or missing.
2. **Background Isolates:** Execute the tokenization and ONNX forward pass in a background Dart `Isolate` (worker thread). This keeps the main thread free, ensuring a smooth, stutter-free 60fps UI.
3. **INT8 Quantization:** Quantize the PyTorch model to an 8-bit integer ONNX model. This shrinks the binary size to **~67 MB** (75% reduction), drastically lowering memory usage and execution latency on mobile CPUs.
4. **Shared Database Helper:** Maintain the existing SQLite `sms_messages` table layout. Both foreground and background analysis repositories write to the same table, notifying listeners on completion.

---

## CHAMPION MODEL RECOMMENDATION

Based on empirical performance logs from the repository, **`distilbert_pakscam_v3`** is the officially recommended champion model for deployment.

### Validation Evidence (vs. Baselines):
* **PakScam Generalization:** `distilbert_pakscam_v3` exhibits an FPR of **3.45%** on localized Pakistani legitimate messages, whereas `distilbert_uci_v2` and `distilbert_pakscam_v1` fail with **94.25%** and **93.10%** FPR respectively. Swapping to this model prevents blocking legitimate personal and banking SMS.
* **Urdu & Localized Spam Catch-Rate:** It achieves **100% recall** on Pakistani Spam (including Roman Urdu Smishing), compared to `distilbert_pakscam_v2` which catches only **86.79%** of local spam and **53.33%** of Roman Urdu spam.
* **Latency Check:** Its mean execution latency is **57.62 ms** on CPU, which fits comfortably under the **60 ms** maximum response limit.
