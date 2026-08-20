# MindShield Chapter 2 Literature Reference Gaps & Recommendations

This document outlines the recommended academic reference expansions for **Chapter 2 (Literature Review)** to strengthen the system architecture and domain justification before final defense.

---

## Recommended Reference Expansions

The following references are highly recommended to justify specific engineering decisions (Clean Architecture, FastAPI logic tier) and domain-specific challenges (Roman Urdu spelling variations) that lack direct academic citations in the template.

### 1. Architectural Justification (Mobile Clean Presentation-Domain-Data)
* **Citation**: Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.
* **Why it matters**: Justifies the Presentation-Domain-Data layering implemented in the Flutter mobile client (`features/inbox/presentation`, `features/analysis/data`, etc.), which decouples state management from HTTP and database adapters.
* **Status**: Recommended for supervisor confirmation.

### 2. High-Performance REST API Tier (FastAPI Logic Layer)
* **Citation**: Ramirez, S. (2024). *FastAPI Documentation and Framework Design*. FastAPI.
* **Why it matters**: Justifies the choice of FastAPI for hosting the DistilBERT inference logic, highlighting asynchronous request routing and low serialization overhead on local loopback.
* **Status**: Recommended for supervisor confirmation.

### 3. Linguistic Domain Justification (Roman Urdu Spelling Variations)
* **Citation**: Sharaf, A. M. (2005). *Roman Urdu: A Study in Spelling Variation*. Language in India, 5(4).
* **Why it matters**: Explains phonetic transcription variability in South Asian SMS text (e.g., "aap", "ap", "aapp" for the Urdu word "you"), justifying the need for deep subword tokenization and custom localized oversampling.
* **Status**: Recommended for supervisor confirmation.
