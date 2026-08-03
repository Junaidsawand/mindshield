# MindShield — Thesis Defense Checklist & Anticipation Guide

> **Module**: Viva Voce & Thesis Defense Readiness  
> **Focus**: Final Defense Preparation, Equipment Checklist, Weak-Point Anticipation, Demo Recovery  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## 1. Hardware & Physical Setup Checklist

- [ ] **Android Test Device**: Fully charged (100%), developer options active, screen timeout set to 10 minutes.
- [ ] **USB Connection Cable**: Original data-capable USB cable (tested with `adb devices`).
- [ ] **Presenter Laptop**: Fully charged, power adapter connected, Wi-Fi hotspot configured.
- [ ] **Display Adapters**: HDMI / USB-C display adapters verified with projector.
- [ ] **Printed Materials**: 3 bound copies of Thesis Document, 3 copies of Executive Summary.

---

## 2. Software & Live Environment Checklist

- [ ] **Local Wi-Fi Network**: Laptop host and Android device connected to same local subnet.
- [ ] **FastAPI Backend Server**: Running via `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- [ ] **Health Endpoint Verified**: `curl http://localhost:8000/health` returns `HTTP 200 OK`.
- [ ] **FastAPI Interactive Docs**: Browser tab open to `http://localhost:8000/docs`.
- [ ] **Android App Installed**: Debug APK built (`flutter build apk --debug`) and launched on phone.
- [ ] **SQLite Database Pre-seeded**: Inbox and History tables populated with 10+ test SMS messages.
- [ ] **Flutter DevTools**: Open in browser to demonstrate 60fps performance overlay if requested.

---

## 3. Weak-Point Anticipation & Defense Strategies

### Weak-Point 1: "Your backend currently uses a placeholder model instead of BERT."
- **Defense Response**:  
  *"That is correct. In Phase 2.1, our engineering goal was to design and verify the system architecture, REST API contracts, validation pipelines, and frontend state management. By applying the Dependency Inversion Principle, `AnalysisService` interacts with an abstract `BaseModelLoader` interface. We verified this architecture with 71 automated tests and 94% code coverage. Plugging in `BertModelLoader` in Phase 2.2 requires changing zero lines of UI, service, or API code."*

### Weak-Point 2: "iOS does not support background SMS reading."
- **Defense Response**:  
  *"Yes, iOS security policies strictly prohibit third-party applications from reading the SMS inbox. MindShield is architected primarily for Android, which holds the largest market share in regions most affected by smishing. For iOS, we provide a cross-platform manual SMS paste fallback, ensuring the core AI classification and explainability engine remains fully accessible."*

### Weak-Point 3: "Stored API keys in client code can be reverse-engineered."
- **Defense Response**:  
  *"In our v1.0 prototype, compiling API key constants in `api_constants.dart` enabled offline development and testing. As documented in our Security Architecture section, production deployment will replace static client keys with an OAuth2 / JWT authentication proxy service where mobile apps authenticate users and backend microservices attach hidden API keys server-side."*

---

## 4. Live Demo Fallback & Emergency Contingency

| Potential Failure | Root Cause | Emergency Recovery Action |
|---|---|---|
| **App cannot connect to backend** | IP address mismatch or firewall | Switch Flutter `api_constants.dart` base URL to `10.0.2.2` (emulator) or run app on Android Emulator. |
| **No SMS received during live test** | Carrier network delay | Manually insert test message via ADB command: `adb shell am broadcast -a android.provider.Telephony.SMS_RECEIVED`. |
| **Projector disconnects** | Cable / resolution error | Use pre-recorded 2-minute MP4 screen recording of the app stored on desktop. |
| **Backend server crashes** | Unhandled exception | Restart Uvicorn via terminal command `uvicorn app.main:app --reload` (takes 2 seconds). |

---

## 5. Post-Defense Administrative Tasks

- [ ] Record examiner feedback and requested thesis revisions.
- [ ] Obtain signature sheet from thesis committee chairman.
- [ ] Tag git repository commit: `git tag -a v1.0-thesis-defense -m "Thesis Defense Release"`.
- [ ] Push final documentation and thesis preparation files to GitHub repository.

---
*MindShield Thesis Defense Checklist & Anticipation Guide · Final Year Project 2026*
