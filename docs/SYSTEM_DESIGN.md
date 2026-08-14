# MindShield — Master System Design Document

> **Document ID**: `docs/SYSTEM_DESIGN.md`  
> **Phase**: FYP-I System Design  
> **Status**: Completed  
> **Date**: 2026-08-14  
> **Author**: Junaid Ahmed | Final Year Project | University of Sindh  

---

## 1. Purpose
This document serves as the master entry point and design blueprint for the MindShield system architecture. It outlines the structural design, interfaces, workflows, and database layers of the platform, linking directly to detailed sub-diagrams and specification files.

---

## 2. System Scope
The MindShield platform provides incoming SMS protection for mobile devices in Pakistan. The scope of this system design documents the:
* **Mobile Client**: Features thread layouts, warning gauges, highlights, history logs, settings, and quarantined spam.
* **Android Native Bindings**: Background interception daemons and contacts providers.
* **Local SQLite Store**: Offline database persisting message parameters.
* **FastAPI Backend Services**: REST routes providing text validations and model pipeline interfaces.
* **AI Model weights**: PyTorch transformer classification (`distilbert-pakscam-v1`) and tokenization engines.

---

## 3. Design Objectives
* **Sub-60ms Latency SLA**: Keeping model CPU inference execution under 60ms.
* **User Transparency**: Translating threat indicators into direct visual highlighted text.
* **Offline-First Resilience**: Grouping and caching messages locally in SQLite to survive disconnection states.
* **Extensibility**: Ensuring the transformer loaders can swap weights without affecting services.

---

## 4. System Boundary
The system boundary separates the local mobile client (handling SMS interception and UI rendering), the central FastAPI backend server (performing validation and pre-processing), and the PyTorch ML classification engine.

---

## 5. Architectural Index & Sitemap

To review the specific diagrams and sub-modules of the system design, navigate to the following documents:

1. **System Architecture Blueprint**: [`design/SYSTEM_ARCHITECTURE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SYSTEM_ARCHITECTURE.md)  
   *High-level presentation, state management, repository, backend server, and ML loader layout.*
2. **UML Use Case Diagram**: [`design/USE_CASE_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/USE_CASE_DIAGRAM.md)  
   *10-use-case UML diagram mapping actors, triggers, flows, and explanations.*
3. **Context Diagram (DFD Level 0)**: [`design/DFD_LEVEL_0.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DFD_LEVEL_0.md)  
   *System boundaries, inputs, processes, and outputs.*
4. **Data Flow Diagram (DFD Level 1)**: [`design/DFD_LEVEL_1.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DFD_LEVEL_1.md)  
   *Decomposition of major processes and local/central data stores.*
5. **Entity Relationship Diagram (ERD)**: [`design/ERD.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/ERD.md)  
   *Audited SQLite schema for the single-table `sms_messages` structure.*
6. **Sequence Workflow Diagram**: [`design/SEQUENCE_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/SEQUENCE_DIAGRAM.md)  
   *Step-by-step chronology from SMS incoming trigger to final visual highlights.*
7. **Component / Module Map**: [`design/COMPONENT_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/COMPONENT_DIAGRAM.md)  
   *Clean Architecture layers on the client and controller/service layers on the backend.*
8. **Deployment Architecture Node Map**: [`design/DEPLOYMENT_DIAGRAM.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DEPLOYMENT_DIAGRAM.md)  
   *Hardware nodes, software target API constraints, and future deployment roadmaps.*
9. **API Data Flow Contract**: [`design/API_DATA_FLOW.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/API_DATA_FLOW.md)  
   *REST requests, responses, HTTP statuses, and validation schemas.*
10. **Design Traceability Matrix**: [`design/DESIGN_TRACEABILITY.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DESIGN_TRACEABILITY.md)  
    *Requirements-to-design elements mapping.*
11. **Design Decisions Log**: [`design/DESIGN_DECISIONS.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DESIGN_DECISIONS.md)  
    *Technology selections (FastAPI, Flutter, SQLite, DistilBERT) and trade-off rationales.*
12. **FYP-I / FYP-II Boundary Document**: [`design/FYP1_VS_FYP2_BOUNDARY.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/FYP1_VS_FYP2_BOUNDARY.md)  
    *Strict scope separation of proof-of-concept features from planned research.*
13. **Design Audit & Discrepancies Report**: [`design/DESIGN_AUDIT.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/design/DESIGN_AUDIT.md)  
    *A requirements engineering audit checking implementation status and database alignment.*

---

## 6. Summary
This master document outlines the system architecture of the MindShield platform. The design is structured to serve as the technical blueprint for the FYP-I presentation, thesis compilation, and subsequent FYP-II development phases.
