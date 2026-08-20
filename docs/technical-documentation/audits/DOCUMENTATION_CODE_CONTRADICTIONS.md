# Documentation and Code Contradictions

This document lists all historical, architectural, and metric discrepancies found between existing project proposals/readmes and the actual codebase implementation of MindShield.

| Existing Claim | Actual Evidence in Code | The Problem | Correct Statement |
| :--- | :--- | :--- | :--- |
| **"MindShield implements a LIME explainer model on the backend."** | No LIME library imports or local surrogate perturbation training in [`model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py). | Overclaims implementation detail. The code uses static keyword regex checks. | **"MindShield implements a Heuristic Feature Attribution framework as a conceptual precursor to LIME."** |
| **"MindShield uses multi-class classification to categorize SMS attacks."** | [`config.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/distilbert/config.py) specifies `num_labels = 2`. The ML outputs are strictly binary. | Describes rule-based post-processing as machine learning. | **"MindShield fine-tunes a binary DistilBERT classifier; attack types are resolved via keyword matching."** |
| **"The system provides on-device machine learning for privacy."** | Flutter calls HTTP API endpoints to FastAPI (`/analyze`); ML models are loaded in python. | Implies on-device models (TFLite/ONNX on mobile). | **"MindShield uses local storage for SMS logs but delegates ML inference to a remote backend server."** |
| **"LIME dynamically highlights specific keywords based on model weights."** | `lime_highlight_card.dart` uses local substring matches against static lists. | Highlighting is decoupled from the ML model's weights. | **"The frontend highlights flagged indicators locally using substring matching."** |
| **"MindShield has a 100% spam detection accuracy."** | Metrics files show `distilbert-uci-v1` spam recall is 88.4% on PakScam validation. | Generalizes perfect training metrics to absolute performance. | **"The model achieves high in-domain recall but is subject to domain generalization limits."** |
