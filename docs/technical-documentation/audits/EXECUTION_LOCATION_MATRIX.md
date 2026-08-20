# Execution Location Matrix

MindShield operates on a hybrid architecture. This document maps out exactly where each process is executed to establish a clear boundary between local on-device capabilities and remote server operations.

| Operation / Process | Device (Android/Flutter) | Backend (FastAPI/PyTorch) | Evidence (Source Files) | Details / Invariants |
| :--- | :---: | :---: | :--- | :--- |
| **SMS Interception** | **YES** | **NO** | [`SmsReceiver.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/SmsReceiver.kt) | Runs in the background on the OS level via `BroadcastReceiver`. |
| **SQLite DB Storage** | **YES** | **NO** | [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart), `SmsReceiver.kt` | Directly modifies `mindshield.db` on local device storage. |
| **Contact Resolution** | **YES** | **NO** | [`MainActivity.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/MainActivity.kt) (lines 121-147) | Resolves names from the native contact store locally. |
| **Inference Orchestration** | **YES** | **NO** | [`analysis_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/analysis_service.dart) | Triggers HTTP API calls and updates local UI states. |
| **API Server Routing** | **NO** | **YES** | [`main.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/main.py), [`v1/analysis.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/routers/v1/analysis.py) | Thin router controller handling CORS and logging context. |
| **Heuristic Signal Extraction**| **NO** | **YES** | [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py) | Evaluates regexes and keywords for threat indicators on backend. |
| **DistilBERT Inference** | **NO** | **YES** | [`model_loader.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/core/model_loader.py) (lines 430-470) | PyTorch tensor prediction execution (running on CPU/GPU). |
| **Fallback Loading** | **NO** | **YES** | [`inference_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/inference_service.py) | Recovers from GPU model errors by swapping in `MockModelLoader`. |
| **LIME/XAI Attribution** | **NO** | **YES** | [`analysis_service.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/services/analysis_service.py) (lines 88-105) | Computes and packages feature weights into API payloads. |
| **Visual Highlighting** | **YES** | **NO** | [`lime_highlight_card.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/analysis/presentation/widgets/lime_highlight_card.dart) | Parses matched text to display highlights on screen. |
