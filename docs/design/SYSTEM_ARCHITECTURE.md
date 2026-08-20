# MindShield — System Architecture

> **Document ID**: `docs/design/SYSTEM_ARCHITECTURE.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. High-Level Blueprint

The system architecture of MindShield implements a clean, decoupled layout dividing the local mobile client (built in Flutter and native Android/Kotlin bindings) and the centralized deep learning backend server (built in FastAPI and PyTorch).

```mermaid
graph TD
    subgraph "Mobile Device (Android API 21+)"
        A[Android Telephony Subsystem] -->|SMS Received Intent| B[Kotlin SMSBroadcastReceiver]
        B -->|Platform Method Channels| C[Flutter SMS Background Service]
        
        subgraph "Flutter Client App (Clean Architecture)"
            C -->|Write Message| D[(SQLite db: sms_messages)]
            
            subgraph "Presentation Layer (UI & Providers)"
                E1[Inbox Screen] --- EP[InboxProvider]
                E2[Spam Folder] --- SP[SpamProvider]
                E3[Analysis Details] --- AP[AnalysisProvider]
                E4[Dashboard / Stats] --- DP[DashboardProvider / State]
                E5[Settings Screen] --- STP[SettingsProvider]
            end
            
            subgraph "Data & Domain Layer"
                EP --- R1[SQLite Repositories]
                SP --- R1
                DP --- R1
                R1 --- D
                
                AP --- R2[ApiAnalysisRepository]
                STP -->|Configures Host IP| R2
            end
            
            R2 -->|Dio HTTP Client| F[HTTP Network Layer]
        end
    end

    subgraph "Backend Server (FastAPI Host)"
        F -->|POST /api/v1/analyze| G[FastAPI Router]
        G -->|Validation check| H[Validators Module]
        H -->|Cleaned message DTO| I[InferenceService]
        
        subgraph "ML Pipeline (PyTorch Sandbox)"
            I -->|Run predict| J[HuggingFaceModelLoader]
            J -->|Subword Tokenizer| K[WordPiece Vocab]
            J -->|Forward inference| L[Active Model: distilbert-pakscam-v1]
        end
        
        I -->|Heuristic highlight lookup| M[AnalysisService / Keyword checkers]
        J -->|Formulate envelope payload| G
        M -->|Formulate envelope payload| G
    end

    classDef implemented fill:#2a7f5c,stroke:#fff,stroke-width:1px,color:#fff;
    classDef planned fill:#7f2a2a,stroke:#fff,stroke-width:1px,color:#fff;
    classDef native fill:#2a5c7f,stroke:#fff,stroke-width:1px,color:#fff;

    class A,B,C native;
    class D,E1,E2,E3,E4,E5,EP,SP,AP,DP,STP,R1,R2,F,G,H,I,J,K,L,M implemented;
```

---

## 2. Layer Descriptions

### 2.1 Android / Kotlin Native Layer
* **Kotlin Broadcast Receiver**: Intercepts incoming SMS intents at OS level.
* **Method Channel Binder**: Directs raw SMS properties into the background Dart engine.

### 2.2 Flutter Client Layers
* **Presentation (UI)**: Material 3 visual cards displaying threat gauges, visual explanation highlights, settings configuration, history log cards, and dashboard metrics.
* **State Management (Providers)**: ChangeNotifier logic driving reactive data flows (e.g. updating inbox list when SQLite triggers update notifications).
* **Domain Layer**: Core models (`SmsMessage`, `Conversation`, `AnalysisResult`).
* **Data Layer**: Repositories converting API JSON schemas or SQLite row queries into clean domain models.

### 2.3 FastAPI Backend Layers
* **Router & Controller**: Parsers checking payload structures via Pydantic schemas.
* **Validation Sub-module**: Pure Python regex validators scrubbing inputs and verifying formatting constraints.
* **Inference Service**: Handles model lifetime status queries, execution profiling, and handles weight load failures by reverting to heuristics.

### 2.4 ML Model Layer
* **WordPiece Tokenizer**: Maps text to subword vocab keys, matching the training configuration of 128 tokens.
* **DistilBERT Classification Engine**: Primary model (**`distilbert-pakscam-v1`**) loaded in PyTorch, executing logits forward passes.

---

## 3. Strict Boundary Architecture Controls

To ensure design accuracy, the following architectural elements are **EXCLUDED** from the current system blueprint and marked strictly as **FYP-II/Planned**:
* **HTTPS Protocol**: Current prototype communicates over unencrypted local HTTP. HTTPS is restricted to the cloud production roadmap.
* **True Local Inference**: The model is hosted in the Python FastAPI backend, not locally on the device (ONNX/TFLite is planned).
* **Multilingual Classification (XLM-RoBERTa)**: Active weights are English/Transliterated DistilBERT (`v1`). Multi-model pipeline routing is planned.
