# MindShield — Security, Permissions & GDPR Viva Guide

> **Module**: Android Security Model, Runtime Permissions & Regulatory Compliance  
> **Focus**: `READ_SMS`, `RECEIVE_SMS`, GDPR (Art 6/13/17/25), Google Play SMS Policy, Threat Model  
> **Parent Guide**: [`MASTER_VIVA_GUIDE.md`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/docs/thesis-preparation/MASTER_VIVA_GUIDE.md)  

---

## Section A — Conceptual Understanding

### Q1: How does Android's permission model protect users, and how does MindShield comply?
**Model Answer:**  
Android implements a layered permission model. Permissions are declared in `AndroidManifest.xml` at build time. Since Android 6.0 (API 23), "dangerous" permissions (accessing personal data like SMS) require runtime user consent via system dialogs. MindShield requests `READ_SMS` and `RECEIVE_SMS` at runtime via `permission_handler`. To build user trust, the `PermissionsScreen` displays explicit rationale cards *before* triggering OS dialogs, explaining exactly why each permission is needed.

- **Permission State Handling**:

| Status | UX Handling |
|---|---|
| `granted` | Proceed with SMS scan |
| `denied` | Render rationale card + retry button |
| `permanentlyDenied` | Render "Open App Settings" CTA (`openAppSettings()`) |

---

### Q2: How does MindShield comply with Google Play's SMS & Call Log Policy?
**Model Answer:**  
Google Play restricts `READ_SMS` and `RECEIVE_SMS` to apps whose core capability strictly requires them. MindShield qualifies under the **Security / Anti-Fraud App** exemption category. Compliance requires:
1. Clear declaration of intent in the Play Store listing.
2. Completing Google's Permissions Declaration Form.
3. Strict data minimization — processing messages in-memory or on-device SQLite, never uploading raw inbox databases to remote servers.

---

## Section B — Design Decision Justification

### Q3: How does MindShield implement Privacy by Design under GDPR Article 25?
**Model Answer:**  
GDPR Article 25 mandates data protection by design and default. MindShield implements this through:
- **On-Device Storage**: Full message text and scan history are stored locally in `mindshield.db` (SQLite).
- **Data Minimization (Art 5)**: Only the individual message selected for AI classification is transmitted to the backend API; no contact lists or unrelated phone metadata are collected.
- **Right to Information (Art 13)**: Rationale cards explain processing scope before consent.
- **Right to Erasure (Art 17)**: Users can clear history and delete quarantined spam items at any time.

---

## Section C — Implementation & Technical Depth

### Q4: Explain the difference between `READ_SMS` and `RECEIVE_SMS` in MindShield.
**Model Answer:**  
- `READ_SMS`: Grants access to the Android SMS ContentProvider (`content://sms`), enabling MindShield to query existing inbox messages for retrospective historical scans.
- `RECEIVE_SMS`: Grants the right to register a manifest `BroadcastReceiver` for `SMS_RECEIVED`, enabling native Kotlin `SmsReceiver` to intercept new incoming messages in real time.

---

## Section D — Limitations, Risks & Future Work

### Q5: How is the AI API Key secured, and what is the production security roadmap?
**Model Answer:**  
In the v1.0 prototype, API key constants are compiled into Dart code. For production deployment, client-side static keys risk reverse-engineering via APK decompilation (`jadx`). The production roadmap replaces static keys with an OAuth2 / JWT authentication service where mobile apps authenticate users, and backend microservices attach hidden API keys server-side when communicating with AI model providers.

---
*MindShield Security & Privacy Viva Guide · Final Year Project 2026*
