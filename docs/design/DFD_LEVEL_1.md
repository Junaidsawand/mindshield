# MindShield — Data Flow Diagram (DFD Level 1)

> **Document ID**: `docs/design/DFD_LEVEL_1.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. DFD Level 1 (Process Decomposition)

Decomposing the Context Diagram reveals the internal processing pipelines, REST interfaces, local data stores, and deep learning wrappers.

```mermaid
graph TD
    User([Mobile User])
    OS([Android Operating System])

    %% Data Stores
    D1[("D1: SQLite Database (sms_messages)")]
    D2[("D2: SharedPreferences (App settings)")]
    D3[("D3: Model Weights Folder")]

    %% Mobile Client Processes
    subgraph Client Application (Flutter Host)
        P1["1.0 Permission Handler"]
        P2["2.0 SMS Interceptor"]
        P3["3.0 Cache Manager"]
        P8["8.0 Presentation UI"]
        P9["9.0 Action Manager"]
        P10["10.0 Settings Manager"]
    end

    %% Backend Server Processes
    subgraph FastAPI API Server
        P4["4.0 Router Controller"]
        P5["5.0 Validator"]
    end

    %% ML Engine Processes
    subgraph PyTorch Inference Engine
        P6["6.0 Model Loader"]
        P7["7.0 Feature Extractor"]
    end

    %% Flow mappings
    User -->|Grant action| P1
    P1 -->|Register status| D2
    P1 -->|Check status| OS

    OS -->|Incoming SMS intent| P2
    P2 -->|Raw SMS payload| P3
    P3 -->|Write record| D1

    User -->|Open thread / details| P8
    P8 -->|Query conversations| P3
    P3 <-->|Read data| D1

    P8 -->|Trigger API check| P4
    P4 -->|Extract URL/financial metrics| P5
    P5 -->|Preprocessed DTO| P6
    
    P6 <-->|Weights lookup| D3
    P6 -->|Class probabilities| P4
    
    P4 -->|Indicators list| P7
    P7 -->|Generate explainability highlights| P8

    User -->|Modify server URL| P10
    P10 -->|Save settings| D2

    User -->|Block/Restore thread| P9
    P9 -->|Update record status| D1
    P9 -->|Method channel intent| OS
```

---

## 2. Process Descriptions and Flows

### Process 1.0 — Permission Handler
* **Function**: Checks and requests runtime allowances. Reads/writes status to `D2` (SharedPreferences).

### Process 2.0 — SMS Interceptor
* **Function**: Kotlin receiver capturing telephony SMS events and channeling details to Process 3.0.

### Process 3.0 — Cache Manager
* **Function**: Handles SQL transactions. Writes and queries entries in `D1` (`sms_messages` table).

### Process 4.0 — Router Controller
* **Function**: FastAPI endpoint handling REST requests. Parses input variables, calls validators, runs inference pipelines, and structures JSON envelopes.

### Process 5.0 — Validator
* **Function**: Stateless string cleaners checking message lengths and formatting rules.

### Process 6.0 — Model Loader
* **Function**: AutoModel sequence classification loader. Processes inputs through Tokenizer, loads weights from `D3` (Model folder), and outputs class probability tensors.

### Process 7.0 — Feature Extractor
* **Function**: Formulates explainability payloads by cross-referencing validator detections (e.g. `url_detected`, `urgency_language`) to return indicators list.

### Process 8.0 — Presentation UI
* **Function**: Renders lists, threat gauges, warning badges, highlights, settings configurations, and log records.

### Process 9.0 — Action Manager
* **Function**: Executes user-initiated management directives (Restore, Block, Delete). Modifies SQL flags in `D1` and redirects intents to the OS.

### Process 10.0 — Settings Manager
* **Function**: Configures API host variables. Persists values in `D2` and sets target endpoints.
