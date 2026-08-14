# MindShield — Component & Module Map

> **Document ID**: `docs/design/COMPONENT_DIAGRAM.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. Core Component Map

The software architecture of MindShield enforces a strict separation of concerns, decoupling UI components, local SQLite caching, FastAPI routers, and PyTorch classification weights.

```mermaid
graph TD
    %% Frontend Subsystems
    subgraph Frontend Subsystem (Flutter Client)
        subgraph Presentation Module
            A1[Screens: Inbox, Analysis, Settings, Spam, History] -->|Reactive Bindings| A2[ChangeNotifier Providers]
        end
        
        subgraph Domain Module
            B1[Entities: SmsMessage, Conversation, AnalysisResult]
            B2[Repository Interfaces]
        end
        
        subgraph Data Module
            C1[Sqflite Repositories] -->|Implement| B2
            C2[ApiAnalysisRepository] -->|Implement| B2
            C3[DatabaseHelper]
            C4[Dio Client / HTTP]
        end
        
        subgraph Native Bindings
            D1[Kotlin SMSBroadcastReceiver]
            D2[Method Channel Bindings]
        end
        
        A2 -->|Observe| B1
        C1 -->|Persist / Query| C3
        C2 -->|Call REST API| C4
        D2 -->|Write messages| C3
    end

    %% Backend Subsystems
    subgraph Backend Subsystem (FastAPI Server)
        subgraph API Controller Module
            E1[main.py / lifespan]
            E2[FastAPI Routers: analysis.py, health.py]
            E3[Pydantic schemas: common.py, analysis.py]
        end
        
        subgraph Services Module
            F1[InferenceService]
            F2[Validators: validators.py]
        end
        
        subgraph ML Pipeline Module
            G1[BaseModelLoader]
            G2[HuggingFaceModelLoader]
            G3[WordPiece Tokenizer]
            G4[Active Model: distilbert-pakscam-v1]
        end
    end

    %% Cross-Subsystem Connections
    C4 -->|REST Calls| E2
    E2 -->|Validate input| F2
    E2 -->|Delegate prediction| F1
    F1 -->|Process text| G2
    G2 -->|Compile vocabulary| G3
    G2 -->|Inference pass| G4
    
    classDef client fill:#2a7f5c,stroke:#fff,stroke-width:1px,color:#fff;
    classDef server fill:#2a5c7f,stroke:#fff,stroke-width:1px,color:#fff;
    classDef weights fill:#7f5c2a,stroke:#fff,stroke-width:1px,color:#fff;

    class A1,A2,B1,B2,C1,C2,C3,C4,D1,D2 client;
    class E1,E2,E3,F1,F2,G1,G2,G3 server;
    class G4 weights;
```

---

## 2. Component Interface Definitions

### 2.1 Mobile Presentation Module
* **State Managers (Providers)**: ChangeNotifier logic driving reactive data flows (e.g. updating inbox list when SQLite triggers update notifications).
* **UI Widgets**: Material 3 visual cards displaying threat gauges, visual explanation highlights, settings configuration, history log cards, and dashboard metrics.

### 2.2 Data & Storage Module
* **SQLite Repositories**: Encapsulates CRUD transactions targeting database helper helper paths.
* **Dio Client**: Encapsulates network operations, HTTP interceptors, timeouts, and automatic retry handlers.

### 2.3 FastAPI Controller Module
* **API Routers**: Translates REST requests into domain service invocations.
* **Pydantic Schemas**: Validates input types and serialization formats.

### 2.4 ML pipeline Module
* **HuggingFaceModelLoader**: Handles tokenizer compilation, PyTorch sequence encoding, device mapping (CPU/GPU), and logits evaluation.
* **Active Model Weights**: Serves the fine-tuned classification parameters (`distilbert-pakscam-v1`).
