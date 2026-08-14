# MindShield — Design Decisions Log

> **Document ID**: `docs/design/DESIGN_DECISIONS.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Key Architectural Decisions

The following records document the major technical design choices made during the development of the MindShield platform.

### 1.1 Choice of Frontend: Flutter SDK
* **Decision**: Selected **Flutter (Dart)** as the core mobile client framework.
* **Alternatives Considered**: React Native, Kotlin Multiplatform (KMP), native Java/Kotlin.
* **Reason Selected**: Single-source cross-platform compiling. Flutter's custom canvas rendering offers smooth M3 layout structures, while platform Method Channels permit simple bindings to background Kotlin broadcast receivers.
* **Trade-off**: Native binaries are slightly larger than native Java applications ($\approx 15\text{ MB}$ base APK).
* **Status**: **IMPLEMENTED**

### 1.2 Choice of Native Bridge: Kotlin Broadcast Receiver
* **Decision**: Configured custom Kotlin telephony intent catchers in `android/app/src/main/kotlin`.
* **Alternatives Considered**: Third-party Flutter pub packages (e.g. `telephony`).
* **Reason Selected**: Modern Android background execution constraints (API 26+) restrict automatic background starts. Native Kotlin receiver implementations guarantee low-memory, zero-thread blockages, and ensure background durability.
* **Trade-off**: Requires writing native platform code, reducing compiler parity.
* **Status**: **IMPLEMENTED**

### 1.3 Choice of Backend: FastAPI (Python)
* **Decision**: Selected **FastAPI** as the central REST routing web host.
* **Alternatives Considered**: Flask, Django, Node.js (Express).
* **Reason Selected**: Built-in support for Pydantic schema validation, asynchronous lifecycle context managers (Uvicorn), automatic Swagger/OpenAPI documentation generation, and extremely low execution overhead ($< 3\text{ ms}$).
* **Trade-off**: Requires setting up Python execution environments (compared to Node.js hosting).
* **Status**: **IMPLEMENTED**

### 1.4 Choice of Local Storage: SQLite (sqflite)
* **Decision**: Selected **SQLite** as the primary client database helper.
* **Alternatives Considered**: Hive, SharedPreferences (for message cache).
* **Reason Selected**: SQLite allows transactional safety, structured schemas, relational grouping filters, and fast indices, keeping message load queries under $15\text{ ms}$.
* **Trade-off**: Requires schema management and migrations.
* **Status**: **IMPLEMENTED**

### 1.5 Choice of Model Architecture: DistilBERT
* **Decision**: Selected **DistilBERT-Base-Uncased** for fine-tuning.
* **Alternatives Considered**: BERT-Base, LSTM, RoBERTa.
* **Reason Selected**: DistilBERT reduces parameters by $40\%$ and speeds up inference by $60\%$ compared to BERT, while retaining $97\%$ of its classification capabilities, enabling fast CPU host inference ($< 60\text{ ms}$).
* **Trade-off**: Slightly reduced accuracy limits (approximately $1.5\%$ lower F1 than BERT-Base).
* **Status**: **IMPLEMENTED**

### 1.6 Choice of Explainability Pipeline: Heuristic Highlight Engine
* **Decision**: Implemented static, regex-based keyword validation matching (`validators.py`) instead of running dynamic perturbations at runtime.
* **Alternatives Considered**: True LIME surrogate model fitting.
* **Reason Selected**: Running true LIME requires generating $1000+$ text perturbations and executing them through the transformer model for *each* classification, taking upwards of $30\text{ seconds}$ on CPU. Mobile smishing prevention requires sub-second alerts. Heuristic checks execute in $< 1\text{ ms}$ and correspond directly to the model's key targets.
* **Trade-off**: Highlight cards do not represent mathematically calculated model weights, only approximated heuristic indications.
* **Status**: **IMPLEMENTED**

---

## 2. Scope Exclusions (Deferred to FYP-II / Planned)
* **XLM-RoBERTa (Multilingual)**: Deferring to FYP-II to support bilingual Urdu/English routing.
* **On-Device ONNX Compiling**: Deferring local model loading to FYP-II to allow offline, local predictions.
* **Secure HTTPS**: Local prototype runs HTTP. Cloud security certificates are planned.
