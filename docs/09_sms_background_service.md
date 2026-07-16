# SMS Background Service & Database Module Documentation

## 1. Introduction
The **SMS Background Service & Database Module** is a core security component of the MindShield application. It is responsible for:
1. Intercepting incoming SMS messages at the OS level on Android (even when the application is closed or in the background).
2. Persisting raw SMS message details directly to a local SQLite database with a `pending` status.
3. Executing a centralized threat analysis pipeline on the Dart side (simulated with keyword rules for now, to be swapped with FastAPI + AI models later).
4. Updating the database with analysis findings (classification, confidence score, and specific threat tags).
5. Dynamically propagating changes to the UI via `Provider` to refresh screens (Inbox, Spam, and History) in real time.

---

## 2. Architecture & System Flow
The module is designed to keep native Android code thin, simple, and decoupled, placing all security analysis and business rules in the Dart layer. This prevents duplicate implementation of classification rules and simplifies the integration of future ML models.

```
Incoming SMS
     │
     ▼
[Android System] (Triggers BroadcastReceiver)
     │
     ▼
[SmsReceiver.kt] (Kotlin)
     │
     ├─► SQLite [mindshield.db] (Inserts as "pending")
     │
     ▼ (Local Intent)
[MainActivity.kt] (Kotlin)
     │
     ▼ (MethodChannel: com.mindshield/sms_receiver)
[SmsBackgroundService] (Dart)
     │
     ▼
[AnalysisService] (Dart) (Runs NLP rule matches & updates row)
     │
     ├─► SQLite [mindshield.db] (Updates status: safe/suspicious/scam)
     │
     ▼ (notifyListeners)
[InboxProvider / SpamProvider / HistoryProvider]
     │
     ▼ (UI Redraw)
[InboxScreen / SpamScreen / HistoryScreen]
```

### 2.1 Core Execution Steps
1. **SMS Reception**: When the device receives an SMS, the Android OS broadcasts `SMS_RECEIVED`. The manifest-registered `SmsReceiver` intercepts this message.
2. **Local Persistence**: `SmsReceiver` opens `mindshield.db` directly and inserts the message with `ai_status = "pending"`.
3. **App Communication**: If the app is active in the foreground, `SmsReceiver` sends a local broadcast caught by `MainActivity`, which invokes `onSmsReceived` over the `MethodChannel`.
4. **Analysis Pipeline**: On the Dart side, `SmsBackgroundService` receives the call and delegates to `AnalysisService.analyzeMessage()`. The message is processed, and its status is updated to `safe`, `suspicious`, or `scam` with appropriate risk levels, confidence scores, and threat tags.
5. **State Synchronization**: All three providers (`InboxProvider`, `HistoryProvider`, `SpamProvider`) listen to the background service and trigger database re-queries, updating the UI dynamically.
6. **Launch Synchronization (Offline Sync)**: On application launch (`main()`), `SmsBackgroundService.instance.syncPendingMessages()` runs asynchronously. It scans SQLite for any messages still marked as `pending` (which happens if messages were received while the application was closed/terminated) and runs the analysis, guaranteeing that no message goes unscanned.

---

## 3. Key Components & Implementation Details

### 3.1 SQLite Persistence (`DatabaseHelper`)
The database schema stores all fields required by both `SmsMessage` and `SpamMessage` in a unified `sms_messages` table:
- `id` (TEXT PRIMARY KEY): Unique identifier.
- `sender` / `body` (TEXT): Core message contents.
- `timestamp` (INTEGER): Milliseconds since epoch.
- `ai_status` (TEXT): Classification enum ('pending', 'safe', 'suspicious', 'scam').
- `is_read` (INTEGER): Read status (0/1).
- `confidence_score` (REAL): Confidence level from 0.0 to 1.0.
- `detected_threats` (TEXT): JSON array string of active threat tags (e.g. `["phishing", "malicious_url"]`).
- `is_spam` (INTEGER): Flag to route message to Spam folder.
- `spam_risk_level` / `spam_attack_type` / `spam_status` / `quarantined_at`: Quarantine details.

*Seeding Routine*: On first launch, the database creates the table and seeds it with mock messages from the UI validation phase, preventing an empty view and maintaining design continuity.

### 3.2 Native Interceptor (`SmsReceiver.kt`)
A manifest-registered broadcast receiver implementing the background interception:
- Reads the raw SMS PDU bytes using `Telephony.Sms.Intents.getMessagesFromIntent()`.
- Accesses `/data/data/com.mindshield.mindshield/databases/mindshield.db` natively via `SQLiteOpenHelper`.
- Secures itself against external invocation by requiring the `android.permission.BROADCAST_SMS` permission.

### 3.3 Platform-Channel Router (`MainActivity.kt`)
Registers a local BroadcastReceiver to catch internal intents sent by `SmsReceiver` and forwards the SMS payload to Flutter via a `MethodChannel` named `com.mindshield/sms_receiver`. It handles SDK compatibility up to Android 13+ (using `RECEIVER_EXPORTED` flags).

### 3.4 Dart Analysis Engine (`AnalysisService`)
Centralizes the threat analysis rules. Currently, it evaluates the message against key smishing, phishing, and scam patterns:
- **Phishing/Smishing**: Looks for links (`http://`, `https://`) or urgency terms (`urgent`, `suspended`, `verify`, `secure`, `bank`).
- **Prize Scams**: Checks for prize lures (`won`, `voucher`, `prize`, `cash`, `claim`).
- **Investment Scams**: Detects high-return financial hooks (`investment`, `advisor`, `double your`, `earn`, `work from home`).
- **Processing State**: Simulates inference delays (500ms) to model real-world inference and updates the database row.

---

## 4. Permissions & Configuration
To function, the Android application requires the following manifest configurations:
```xml
<!-- Manifest Permissions -->
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.RECEIVE_SMS" />

<!-- Background BroadcastReceiver Registration -->
<receiver
    android:name=".SmsReceiver"
    android:exported="true"
    android:permission="android.permission.BROADCAST_SMS">
    <intent-filter android:priority="999">
        <action android:name="android.provider.Telephony.SMS_RECEIVED" />
    </intent-filter>
</receiver>
```

---

## 5. Thesis & Documentation Value
- **Clean Architecture Principles**: Keeping the native Kotlin code extremely thin and routing analysis back to Dart demonstrates high decoupling.
- **SQLite Single-Source-of-Truth**: Running concurrent reads and writes from Kotlin and Dart processes on the same SQLite file ensures optimal local caching and offline capability.
- **Seamless AI Integration Path**: By separating the background interception code from the actual analysis method, replacing the dummy rules with a FastAPI network client (calling DistilBERT and LIME models) is a simple one-line modification. The Android native code is 100% stable.
