# MindShield — System Sequence Workflow

> **Document ID**: `docs/design/SEQUENCE_DIAGRAM.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. End-to-End SMS Interception & Threat Analysis Workflow

This sequence diagram details the chronological execution path across the mobile client, native method channels, SQLite persistence, FastAPI backend, and PyTorch inference pipeline.

```mermaid
sequenceDiagram
    autonumber
    actor User as Mobile User
    actor OS as Android OS
    participant native as Kotlin SMSBroadcastReceiver
    participant channel as Dart sms_background_service
    participant db as DatabaseHelper (SQLite)
    participant UI as Flutter presentation (UI)
    participant repo as ApiAnalysisRepository (Dio)
    participant api as FastAPI router (main.py)
    participant validator as Validators Module
    participant service as InferenceService
    participant ml as HuggingFaceModelLoader (PyTorch)

    %% SMS Interception Phase
    OS->>native: BroadCast SMS received Intent
    activate native
    native->>channel: Invoke native platform Method Channel
    deactivate native
    activate channel
    channel->>db: insertMessage(row) into sms_messages
    activate db
    db-->>channel: Return row ID / confirmation
    deactivate db
    channel-->>OS: Acknowledge intent completion
    deactivate channel

    %% UI Presentation Phase
    User->>UI: Launch Application / navigate to Inbox
    activate UI
    UI->>db: queryInboxMessages()
    activate db
    db-->>UI: Return cached thread records list
    deactivate db
    UI-->>User: Render Material 3 conversation thread list

    %% Threat Analysis Phase
    User->>UI: Click on thread & select "Analyze Thread"
    UI->>repo: getAnalysis(smsMessage)
    deactivate UI
    activate repo
    repo->>api: POST /api/v1/analyze (HTTP request payload)
    activate api
    api->>validator: is_valid_message(message)
    activate validator
    validator-->>api: Return validation confirmation
    deactivate validator

    api->>service: predict(message_text)
    activate service
    service->>ml: predict(clean_text)
    activate ml
    ml->>ml: Preprocess text (NFKC) & tokenise (WordPiece)
    ml->>ml: Run PyTorch forward pass (distilbert-pakscam-v1)
    ml-->>service: Return ModelPrediction (label, class, confidence)
    deactivate ml
    
    service->>validator: extract_heuristic_features(text)
    activate validator
    validator-->>service: Return indicators checklist
    deactivate validator
    
    service-->>api: Return consolidated verdict details DTO
    deactivate service
    api-->>repo: Return APIResponse[AnalysisResult] JSON
    deactivate api
    repo->>db: updateMessage(id, analysis_details)
    activate db
    db-->>repo: Acknowledge cache write
    deactivate db
    repo-->>UI: Return mapped AnalysisResult entity
    deactivate repo
    activate UI
    UI->>UI: Render threat gauge & highlights (LimeHighlightCard)
    UI-->>User: Render visual threat explainability overlay
    deactivate UI
```

---

## 2. Step-by-Step Execution Narrative

### Phase A: Background Message Acquisition (Steps 1–6)
* The Android OS triggers a receiver intent when an SMS arrives.
* The Kotlin wrapper intercepts the intent payload and sends it via platform channels to the background Dart task.
* The background service writes the raw text and sender info to `sms_messages` in SQLite, creating a new thread or adding to an existing one.

### Phase B: UI Navigation & View Assembly (Steps 7–10)
* The user opens the app, prompting the inbox list view.
* The client queries SQLite for safe/inbox messages and displays the grouped list.

### Phase C: Deep-Learning Inference & Highlight Visualisation (Steps 11–24)
* The user opens a thread and triggers analysis.
* The Dio client posts the raw text and sender metadata over HTTP to the backend server.
* The FastAPI server parses the request using Pydantic and executes basic validations.
* The validator outputs validation confirmations, forwarding the payload to the active inference manager.
* The PyTorch model tokenizer processes the text and runs forward inference on the production model (`distilbert-pakscam-v1`).
* Heuristic indicators are evaluated to identify matches (such as shortened URLs).
* The combined results are wrapped in a standard JSON response envelope and returned.
* The client caches these metrics locally in SQLite, maps the JSON payload to domain entities, and renders the visual explanation overlays using `LimeHighlightCard`.
