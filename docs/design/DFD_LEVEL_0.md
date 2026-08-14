# MindShield — Data Flow Diagram (DFD Level 0)

> **Document ID**: `docs/design/DFD_LEVEL_0.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  

---

## 1. DFD Level 0 (Context Diagram)

The Context Diagram defines the boundary of the MindShield application, modeling all data exchanges between the core system and external entities.

```mermaid
graph LR
    User([Mobile User])
    OS([Android Operating System])
    MS[("MindShield System (1.0)")]

    %% User Input/Output Flows
    User -->|1. Onboarding & Permissions grant| MS
    User -->|2. Analysis trigger / Thread view request| MS
    User -->|3. Configuration changes / Server IP| MS
    User -->|4. Manage spam / restore / delete command| MS

    MS -->|1. Render inbox conversation threads| User
    MS -->|2. Render threat score, gauge & highlights| User
    MS -->|3. Render history list & stats charts| User
    MS -->|4. Active API operational status badges| User

    %% Android System Flows
    OS -->|1. Incoming SMS Intent payload| MS
    OS -->|2. Contacts list database records| MS
    
    MS -->|1. Native SMS block / Dial intent trigger| OS
```

---

## 2. Interface Flow Specifications

### 2.1 Inputs
1. **SMS Intent Payload**: Incoming raw text stream (body, sender address, timestamp) routed from the Android broadcast receiver.
2. **Onboarding / Permission Grant**: Android OS security allowances (`READ_SMS`, `RECEIVE_SMS`) approved by the user.
3. **Trigger Commands**: Manual selections prompting API analysis, spam management, settings changes, or navigation.

### 2.2 Processes
* **MindShield System**: Encapsulates on-device SQLite caching, background method channel handlers, REST requests compilation, text validation routines, and the DistilBERT inference pipeline.

### 2.3 Outputs
1. **Inbox Visualisation**: Grouped conversation lists.
2. **Threat Assessment**: Scores, safety categories (safe, suspicious, dangerous), and heuristic term warnings.
3. **System Logs & Dashboard metrics**: Cached logging views and aggregated charts.
4. **Android Intent Triggers**: Opens native dialer and SMS client parameters.
