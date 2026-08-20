# Chapter 11 — Security, Privacy & Threat Analysis

This chapter provides a security audit, threat model, and data privacy analysis of the MindShield platform. It differentiates between the security *of* the application itself (transport encryption, access limits, sanitization) and the security *capabilities* of the platform (ML smishing detection).

---

## 11.1 Security of the System vs. Detection Capability

In security engineering, it is critical to distinguish between two separate scopes:
* **Scope A: Security of the System:** The controls that protect the MindShield application, SQLite databases, and API channels from exploitation, tampering, and unauthorized access.
* **Scope B: Security Detection Capability:** The performance of the machine learning classifier and HFA modules in identifying external threats (such as phishing links or lottery scams) within the incoming SMS stream.

This chapter focuses on **Scope A**, identifying potential vulnerabilities in the prototype implementation and establishing a roadmap for security hardening.

---

## 11.2 Protected Assets

MindShield interacts with and persists sensitive user information:

### Table 11.1 — Protected Assets

| Asset Name | Asset Type | Storage Location | Sensitivity | Threat Target |
| :--- | :--- | :--- | :---: | :--- |
| **SMS Payload** | Text | SQLite (`sms_messages`) & Memory | High | Contains OTPs, banking receipts, and personal data. |
| **Sender Identifiers** | Metadata | SQLite (`sms_messages`) & Contacts | Medium | Phone numbers and alphanumeric brand codes. |
| **Risk Verdict Logs** | Metadata | SQLite (`sms_messages`) | Low | Classification records and timestamps. |
| **Model Weights** | Binary | Backend Disk / GPU memory | High | Intellectual property; risk of unauthorized extraction. |
| **API Endpoints** | Interface | Backend Routing Service | Medium | Vulnerable to Denial-of-Service and unauthorized queries. |

---

## 11.3 Threat Actors & Surface Map

MindShield operates in environments with diverse threat profiles:

### Table 11.2 — Threat Actors

| Threat Actor | Motivation | Typical Vector |
| :--- | :--- | :--- |
| **External Smisher** | Financial fraud, credential theft | Sends malicious text payloads containing banking templates and shortened URLs. |
| **Network Eavesdropper**| Eavesdropping, PII collection | Intercepts HTTP request traffic between the client and backend. |
| **Malicious Co-located App**| Local data access | Attempts to bypass Android filesystem sandbox bounds to read SQLite files. |
| **Model Adversary** | Classifier evasion | Obfuscates text (e.g. using spelling variations) to bypass detection filters. |

---

## 11.4 System Attack Surface Analysis

The system’s attack surface maps to the data ingestion boundaries:

```
[External SMS Sender] 
         │ (SMS Broadcast PDU)
         ▼ (Trust Boundary: OS Interception)
[SmsReceiver.kt]
         │ (Local Broadcast Intent)
         ▼
[MainActivity.kt] ──► [MethodChannel] ──► [SmsBackgroundService (Dart)]
                                                    │
                                                    ▼ (Local Query)
                                          [SQLite: mindshield.db]
                                                    │
                                                    ▼ (Trust Boundary: HTTP Network)
                                          [Dio HTTP Request Payload]
                                                    │
                                                    ▼
                                          [FastAPI Web Router]
                                                    │
                                                    ▼ (Pydantic Schema Validation)
                                          [Inference + HFA Service]
```

### Table 11.3 — Attack Surface Boundaries

| Interface Boundary | Ingested Input | Primary Security Threat | Implemented Controls | Residual Risk |
| :--- | :--- | :--- | :--- | :--- |
| **OS Interception** | SMS PDU | Malformed payload crashing receiver | Try-catch handler in Kotlin | Minimal |
| **Local Database** | SQL updates | SQL Injection | Fully parameterized query statements | Root access extraction |
| **Network Transit** | JSON payload | Man-in-the-Middle (MITM) | Plain HTTP defaults | Text payload eavesdropping |
| **API Routing** | HTTP REST | API abuse / Denial of Service | CORS origin mappings | Unauthenticated access |
| **ML Inference** | Text string | Evasion via Unicode tricks | NFKC sanitization | Classifier bypass |

---

## 11.5 SMS Ingestion & Receiver Security

* **Component:** [`SmsReceiver.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/SmsReceiver.kt)
* **Ingestion Security:** Native Android BroadcastReceivers are subject to broadcast spoofing. MindShield mitigates this in the manifest by requiring the `android.permission.BROADCAST_SMS` permission for the receiver:
  ```xml
  <receiver android:name=".SmsReceiver" android:permission="android.permission.BROADCAST_SMS">
  ```
  This ensures that only the Android Telephony framework can trigger the receiver, blocking local apps from sending fake SMS intents.
* **Malformed Input:** Kotlin uses a try-catch block wrapping the database write step, preventing unhandled PDU parsing errors from crashing the receiver process.

---

## 11.6 Input Validation & Sanitization

* **Component:** [`validators.py`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/backend/app/utils/validators.py) (lines 165-200)
* **Sanitization:** `sanitise_message(text)` applies **Unicode NFKC normalization** and collapses multiple whitespaces. This helps normalize lookalike characters (e.g. Cyrillic characters used to mimic Latin text) before the text reaches the tokenizer.
* **Size Enforcement:** Requests under 3 characters or over 2,000 characters are rejected at the schema level, preventing memory buffer overflows during model inference.

---

## 11.7 SQL Injection Vulnerability Analysis

* **Component:** [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart)
* **Audit Result:** The database helper **exclusively uses parameterized API bindings** (e.g. `db.query('sms_messages', where: 'id = ?', whereArgs: [id])`) for all CRUD operations. Dynamic string concatenation (such as embedding raw message text directly into query strings) is not used.
* **Conclusion:** The application is robust against SQL Injection attacks.

---

## 11.8 API Security & CORS Configurations

The FastAPI backend exposes endpoints to LAN environments:
* **CORS Settings:** Configured in `main.py` using `CORSMiddleware`. In development mode, allowed origins default to `["*"]` to simplify mobile emulator testing.
* **Rate Limiting:** **No rate limiting is implemented in the current prototype.** The backend is vulnerable to Denial-of-Service (DoS) and automated request flooding.
* **Authentication:** **No authentication is implemented in the prototype.** The `/api/v1/analyze` endpoint accepts requests from any client that can connect to the port.

---

## 11.9 Network Security (Prototype vs. Production)

* **Current State:** The client connects to the backend using plain **HTTP** (e.g., `http://10.250.110.244:8000/api/v1`).
* **Risk Profile:** Plaintext transmission exposes message payloads to Man-in-the-Middle (MITM) attacks. Eavesdroppers on the same local network can intercept sensitive data like transaction values or OTP codes in transit.
* **Recommendation:** HTTPS must be configured for all production deployments.

---

## 11.10 Local Database Security

* **Storage Path:** `/data/data/com.mindshield.mindshield/databases/mindshield.db`
* **Encryption Status:** **The local SQLite database is not encrypted.**
* **Risk Profile:** Because standard SQLite files are stored in plaintext, an attacker with root access or physical access to device backups can extract the database and read SMS logs.
* **Mitigation Context:** Android's default file sandbox isolates databases from non-root applications. However, database encryption (SQLCipher) is recommended for production builds.

---

## 11.11 Data Privacy Flow & Minimization

The diagram below traces the path of sensitive data:

```
[SMS Ingest] ──► [SQLite persistence] ──► [Dio HTTP Request] ──► [FastAPI Memory]
                        (Local)               (Plain HTTP text)        (Transient)
```

* **Data minimization is partially implemented:** The client resolves sender names locally using device contact APIs. Only raw phone numbers/shortcodes are sent to the backend, preventing user contact lists from leaking.
* **Data Retention:** The backend does not persist analyzed payloads to disk. Messages are processed in memory and discarded immediately after response serialization.

---

## 11.12 STRIDE Threat Analysis

### Table 11.4 — STRIDE Analysis

| STRIDE Category | Threat Description | Targeted Component | Current Control | Residual Risk |
| :--- | :--- | :--- | :--- | :--- |
| **Spoofing** | Adversary sends fake SMS intents to MainActivity. | Platform MethodChannel | Native broadcast permissions | Minimal |
| **Tampering** | Local filesystem attacker modifies SQLite logs. | `mindshield.db` file | Android app sandboxing | Root filesystem access |
| **Repudiation** | Client denies querying specific malicious URLs. | FastAPI routing logs | Basic console logger | No audit logs |
| **Information Disclosure** | Network eavesdropper reads OTPs in transit. | Network interface | None (Plain HTTP) | High (MITM risk) |
| **Denial of Service** | Botnet floods the analysis endpoint with queries. | FastAPI web server | None | Server overload |
| **Elevation of Privilege** | Local app reads Android manifest permissions. | OS permission store | User permission dialogs | Manifest exploits |

---

## 11.13 OWASP Top 10 Mappings

### 1. OWASP Mobile Top 10 Alignment
* **M2: Insecure Data Storage:** The unencrypted local SQLite database represents a risk on rooted devices.
* **M3: Insecure Communication:** Plain HTTP communication defaults expose payloads to eavesdropping.

### 2. OWASP API Security Top 10 Alignment
* **API2: Broken Authentication:** The `/api/v1/analyze` endpoint has no authentication keys or access checks.
* **API4: Unrestricted Resource Consumption:** The backend lacks rate-limiting mechanisms.

---

## 11.14 Security Controls Matrix

### Table 11.6 — Security Controls

| Security Control | Implemented? | Evidence (Source File) | Effectiveness | Future Improvement |
| :--- | :---: | :--- | :--- | :--- |
| **Input Validation** | **YES** | `validators.py` | High | Implement regex validation for phone numbers. |
| **Schema Validation**| **YES** | `analysis.py` (schemas) | High | Enforce stricter string limits. |
| **SQL Parameterization**| **YES** | `database_helper.dart` | High | None. |
| **Local Sandboxing** | **YES** | Android OS | High | Implement local database encryption. |
| **CORS Mappings** | **YES** | `main.py` | Medium | Restrict origins in production. |
| **Rate Limiting** | **NO** | codebase | None | Add ASGI rate-limiting middleware. |
| **API Authentication**| **NO** | codebase | None | Add API keys or JWT tokens. |
| **Transport Security**| **NO** | `app_constants.dart` | None | Configure HTTPS and enforce SSL pinning. |

---

## 11.15 Privacy Controls Matrix

### Table 11.7 — Privacy Controls

| Privacy Concern | Current Behavior | Risk | Recommendation |
| :--- | :--- | :--- | :--- |
| **SMS Collection** | Intercepts incoming SMS payloads. | PII exposure | Keep processing scoped to user confirmation. |
| **Local Storage** | Stores raw SMS body text in SQLite. | Filesystem exposure | Implement database encryption. |
| **Remote Transmission**| Transmits SMS text over the network. | Network interception | Enforce HTTPS transit. |
| **Retention** | Server processes payloads in memory. | None | Maintain in-memory processing invariants. |
| **User Deletion** | Users can delete local logs. | None | None. |

---

## 11.16 Android Permissions Security

### Table 11.8 — Android Permissions

| Permission Name | Mandatory? | Purpose in MindShield | Risk Rating | Least Privilege Review |
| :--- | :---: | :--- | :---: | :--- |
| **`RECEIVE_SMS`** | **YES** | Intercepts incoming SMS broadcasts. | High | Essential for background filtering. |
| **`READ_SMS`** | **YES** | Reads historical SMS inbox data. | High | Required for inbox list synchronization. |
| **`INTERNET`** | **YES** | Submits analysis requests to server. | Medium | Required for remote model inference. |
| **`READ_CONTACTS`** | **NO** | Resolves sender phone numbers to names. | Medium | Optional; sender names resolved locally. |

---

## 11.17 Security Recommendations

The following table lists security recommendations prioritized by criticality:

### Table 11.9 — Security Recommendations

| Priority | Targeted Component | Required Mitigation Action |
| :--- | :---: | :--- |
| **P0 (Critical)** | **Network Transport** | Enforce **HTTPS** across all endpoints. Block plain HTTP requests in the client configuration. |
| **P0 (Critical)** | **API Access** | Implement token-based authentication (e.g., API keys) to prevent unauthorized API calls. |
| **P1 (High)** | **API Availability** | Implement rate limiting (e.g. slowapi) on the server to prevent Denial-of-Service attacks. |
| **P1 (High)** | **Local Storage** | Encrypt `mindshield.db` using **SQLCipher** to protect data on rooted devices. |
| **P2 (Medium)**| **Inference Input** | Implement input sanitization to filter out malicious character tricks. |
| **P3 (Low)** | **Model Security** | Package models as signed artifacts to prevent model replacement attacks. |

---

## 11.18 Chapter Summary

This chapter has detailed the security, privacy, and threat models of the MindShield platform. While the local database implements parameterized queries and native Android permissions protect SMS interception broadcasts, the prototype lacks transport encryption and API authentication, which must be addressed before production deployment.

The automated verification tests and performance logs are detailed in **Chapter 12 — Verification, Validation & Testing**.

---

## Security Audit Verification Summary

### Strongly Verified Controls:
* Parameterized SQLite queries (`database_helper.dart`).
* Input length validations and digit checks (`validators.py`).
* Android BroadcastReceiver permission enforcement (`RECEIVE_SMS`).
* Contact resolution details kept on-device (`MainActivity.kt`).

### Missing Controls:
* **No Authentication:** Anyone can call the backend API endpoints.
* **No Rate Limiting:** The backend is vulnerable to request flooding.
* **No Transport Security:** Messages are sent over plain HTTP.
* **No Database Encryption:** The SQLite database is stored in plaintext.
* **No Model Verification:** The server does not verify model file integrity.
