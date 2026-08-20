# Chapter 10 — Mobile Application Architecture & Implementation

This chapter describes the frontend architecture, system integration bridge, and feature-level implementation of MindShield's mobile application. It details the Kotlin native interception layer, the MethodChannel bridge, and the feature-based Flutter app layout.

---

## 10.1 Chapter Introduction & Technology Stack

MindShield uses a cross-platform presentation layer written in Flutter (Dart), integrated with native Android components in Kotlin to support low-level SMS broadcast interception:

### Table 10.1 — Mobile Technology Stack

| Technology Component | Implemented Version | Purpose in MindShield | Source Code References |
| :--- | :---: | :--- | :--- |
| **Flutter SDK** | `>=3.7.0 <4.0.0` | Cross-platform UI layout framework | [`pubspec.yaml`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/pubspec.yaml) |
| **Kotlin / Android SDK**| `1.9.0` | OS-level SMS interception and native contacts query | `MainActivity.kt`, `SmsReceiver.kt` |
| **`sqflite`** | `^2.4.1` | Local SQLite database persistence | [`database_helper.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/database/database_helper.dart) |
| **`provider`** | `^6.1.2` | State management and ChangeNotifier rebuilds | `dashboard_provider.dart`, `inbox_provider.dart` |
| **`go_router`** | `^14.6.2` | Shell tab routing and screen arguments | [`app_router.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/router/app_router.dart) |
| **`dio`** | `^5.7.0` | HTTP request serialization and retry loops | [`dio_client.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/network/dio_client.dart) |

---

## 10.2 Android Native SMS Interception

Background SMS interception is implemented at the OS level using an Android `BroadcastReceiver`:

* **Action:** Listens for `android.provider.Telephony.SMS_RECEIVED`.
* **PDU Extraction:** The receiver extracts SMS protocol data units (PDUs) using the `Telephony.Sms.Intents.getMessagesFromIntent(intent)` helper to construct the sender address and combine multipart text payloads.
* **Local SQLite Write:** `SmsReceiver` opens `mindshield.db` in Kotlin, inserting records into `sms_messages` with `ai_status = "pending"`. This prevents data loss if the Flutter application is suspended or closed.
* **Bridge Signaling:** After the database write, `SmsReceiver` broadcasts a local intent `com.mindshield.SMS_RECEIVED` containing the message UUID.

```
[Android OS Broadcast] ──► SmsReceiver.onReceive()
                                 │
                                 ▼ (Extract address & body)
                       insertPendingSms()
                                 │
                                 ▼ (Write direct to local SQLite)
                       [SQLite: sms_messages (status=pending)]
                                 │
                                 ▼ (Send local broadcast)
                       Intent("com.mindshield.SMS_RECEIVED")
```

**Implementation Evidence:**
* **Source File:** [`SmsReceiver.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/SmsReceiver.kt) (lines 12-91)
* **Manifest Config:** [`AndroidManifest.xml`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/AndroidManifest.xml) (lines 40-47)

---

## 10.3 MainActivity Bridge & MethodChannels

`MainActivity` acts as the native entry point and communication bridge, exposing two platform channels to the Flutter engine:

### 1. Inbound SMS Channel (`com.mindshield/sms_receiver`)
Registers `smsReceiver` to listen for the local intent `com.mindshield.SMS_RECEIVED`. When a local intent is caught, it transmits the message payload to Dart via:
```kotlin
methodChannel?.invokeMethod("onSmsReceived", data)
```

### 2. Contacts Channel (`com.mindshield/contacts`)
Exposes the `fetchContacts` method. It queries the device contact store using `ContactsContract.CommonDataKinds.Phone.CONTENT_URI`, mapping phone numbers to display names to identify known senders:
```kotlin
MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CONTACTS_CHANNEL)
    .setMethodCallHandler { call, result ->
        if (call.method == "fetchContacts") {
            val contacts = getAllContacts()
            result.success(contacts)
        }
    }
```

**Implementation Evidence:**
* **Source File:** [`MainActivity.kt`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/android/app/src/main/kotlin/com/mindshield/mindshield/MainActivity.kt) (lines 35-80)

---

## 10.4 Background SMS Service

In Dart, the native channel callbacks are handled by `SmsBackgroundService`:

* **Initialization:** Instantiated as a singleton composition root during Flutter app startup.
* **Verification Pipeline:**
  1. Catches the `"onSmsReceived"` platform method invocation.
  2. Notifies active providers to display the `"Analyzing..."` UI state.
  3. Triggers `AnalysisService.instance.analyzeMessage` to query the FastAPI backend.
  4. Updates the database record with the classification results and triggers a UI refresh.

**Implementation Evidence:**
* **Source File:** [`sms_background_service.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/core/services/sms_background_service.dart) (lines 40-79)

---

## 10.5 Ingestion & In-App Lifecycle

An incoming SMS flows through the following pipeline:

```
[Incoming SMS Intent] ──► [SmsReceiver] ──► [Write pending to SQLite]
                                                  │
                                                  ▼ (local broadcast)
                                            [MainActivity]
                                                  │
                                                  ▼ (MethodChannel invocation)
                                            [SmsBackgroundService (Dart)]
                                                  │
                                                  ▼
                                            [ChangeNotifier Rebuilds UI]
                                                  │
                                                  ▼ (Dio HTTP call)
                                            [POST /api/v1/analyze]
                                                  │
                                                  ▼ (verdict payload)
                                            [SQLite: update details]
                                                  │
                                                  ▼
                                            [ChangeNotifier Rebuilds UI]
```

---

## 10.6 Local SQLite Database Architecture

The local database acts as the shared persistence layer between Kotlin and Dart:

* **File Name:** `mindshield.db`
* **Schema Version:** 2

### Table 10.5 — SQLite Schema: `sms_messages`

| Column | Data Type | Constraint | Default | Description |
| :--- | :--- | :---: | :---: | :--- |
| **`id`** | TEXT | PRIMARY KEY | — | Unique message UUID. |
| **`sender`** | TEXT | NOT NULL | — | Phone number or alphanumeric sender code. |
| **`body`** | TEXT | NOT NULL | — | SMS message text. |
| **`timestamp`** | INTEGER | NOT NULL | — | Epoch millisecond timestamp of receipt. |
| **`ai_status`** | TEXT | NOT NULL | — | Classification status (`pending`/`safe`/`suspicious`/`scam`). |
| **`is_read`** | INTEGER | NOT NULL | 0 | 0 = Unread, 1 = Read. |
| **`confidence_score`**| REAL | NULLABLE | — | Classification confidence in `[0.0, 1.0]`. |
| **`detected_threats`** | TEXT | NOT NULL | '[]' | JSON-encoded string list of detected HFA indicators. |
| **`is_spam`** | INTEGER | NOT NULL | 0 | Binary flag: 0 = Benign/Safe, 1 = Quarantine. |
| **`spam_risk_level`** | TEXT | NULLABLE | — | Severity rating (`safe`, `suspicious`, `dangerous`). |
| **`spam_attack_type`**| TEXT | NULLABLE | — | Categorized attack vector (e.g. `prizeScam`, `phishing`). |
| **`spam_status`** | TEXT | NULLABLE | — | Mitigation state (`quarantined`). |
| **`quarantined_at`** | INTEGER | NULLABLE | — | Epoch millisecond timestamp of quarantine. |

*There are no foreign-key relationships in the database schema.*

---

## 10.7 Message Status Lifecycle

### Table 10.6 — Message Status Lifecycle

| Status Code | Conditions | Trigger Event | Destination Screen |
| :--- | :--- | :--- | :--- |
| **`'pending'`** | `is_spam = 0` | Intercepted by `SmsReceiver`; awaiting API analysis. | Inbox (displays "Analyzing..." loader) |
| **`'safe'`** | `is_spam = 0` | Backend returns `threat_level = safe`. | Inbox (displays standard thread preview) |
| **`'suspicious'`**| `is_spam = 1` | Backend returns `threat_level = suspicious`. | Spam folder (quarantined) |
| **`'scam'`** | `is_spam = 1` | Backend returns `threat_level = dangerous`. | Spam folder (quarantined) |

**Implementation Evidence:**
* **State Mapping:** `analysis_service.dart` (lines 103-131)

---

## 10.8 Database Migrations (v1 $\rightarrow$ v2)

The database migration logic is executed inside `DatabaseHelper`:
* **Trigger:** Upgrading schema to version 2.
* **Migration Logic:** Identifies and deletes hardcoded seed messages (`msg_001` through `msg_012`) to ensure that the production application displays only genuine intercepted messages.

**Implementation Evidence:**
* **Source File:** `database_helper.dart` (lines 55-68)

---

## 10.9 State Management

State management is implemented using the **Provider** package with **ChangeNotifier**:

* **State Providers:** `InboxProvider` and `DashboardProvider` query `DatabaseHelper` instances.
* **State Updates:** Trigger `notifyListeners()` when data changes.
* **UI Rebuilds:** Widgets wrap content in `Consumer<InboxProvider>` and `Consumer<DashboardProvider>` builders, rebuilding when state notifications are received.

---

## 10.10 Feature Modules Inventory

### Table 10.4 — Flutter Feature Modules

| Feature Module | Presentation Widget | Provider Scope | Responsibility |
| :--- | :--- | :--- | :--- |
| **Dashboard** | `DashboardScreen` | `DashboardProvider` | Displays total metrics and recent spam indicators. |
| **Inbox** | `InboxScreen`, `ConversationDetailsScreen`| `InboxProvider` | Renders conversation threads and previews. |
| **Analysis** | `AnalysisScreen` | Uses domain model | Renders threat verdict speedometer and HFA highlights. |
| **Spam** | `SpamScreen` | `InboxProvider` | Renders quarantined spam messages. |
| **History** | `HistoryScreen` | `InboxProvider` | Displays historical analysis logs and indicators. |
| **Settings** | `SettingsScreen` | Directly manages state | Exposes server URL configurations. |

**Implementation Evidence:**
* **Source Folder:** [`frontend/lib/features/`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features)

---

## 10.11 Android Permissions

MindShield requests five permissions in the manifest:

### Table 10.2 — Android Permissions

| Permission Name | Required | MindShield Purpose | Denied Behavior |
| :--- | :---: | :--- | :--- |
| **`RECEIVE_SMS`** | **Required** | Permits OS-level SMS interception via `SmsReceiver`. | Background interception is disabled. |
| **`READ_SMS`** | **Required** | Allows the app to query existing inbox SMS. | The Inbox screen renders empty. |
| **`READ_CONTACTS`** | Optional | Resolves sender names from contacts. | Senders are displayed as raw numbers. |
| **`INTERNET`** | **Required** | Permits connection to the FastAPI backend. | Analysis calls fail with network timeout errors. |
| **`ACCESS_NETWORK_STATE`**| **Required** | Profiles network connectivity status. | Diagnostic cards display network failures. |

**Implementation Evidence:**
* **Permissions Screen:** [`frontend/lib/features/permissions/presentation/permissions_screen.dart`](file:///c:/Users/n%20tech/OneDrive/Desktop/mindshield/frontend/lib/features/permissions/presentation/permissions_screen.dart)

---

## 10.12 Navigation Layout

Navigation is managed using **GoRouter** with tab state persistence (`StatefulShellRoute`):

### Table 10.7 — Navigation Routes

| Route Constant | Shell Path | Target View Widget | Parent Navigator |
| :--- | :--- | :--- | :--- |
| **`AppRoutes.splash`** | `/` | `SplashScreen` | Root Navigator |
| **`AppRoutes.permissions`** | `/permissions` | `PermissionsScreen` | Root Navigator |
| **`AppRoutes.dashboard`** | `/dashboard` | `DashboardScreen` | Stateful Shell branch |
| **`AppRoutes.inbox`** | `/inbox` | `InboxScreen` | Stateful Shell branch |
| **`AppRoutes.spam`** | `/spam` | `SpamScreen` | Stateful Shell branch |
| **`AppRoutes.analysis`** | `/analysis` | `AnalysisScreen` (receives `SmsMessage` parameter) | Root Navigator |
| **`AppRoutes.conversationDetails`**| `/conversation/details`| `ConversationDetailsScreen` (receives sender arguments) | Root Navigator |

**Implementation Evidence:**
* **Router Config:** `app_router.dart` (lines 34-139)

---

## 10.13 Mobile Offline & Failure Handling

* **Background Sync:** If the app receives an SMS while the device is offline, `SmsReceiver.kt` still writes the record as `'pending'` to SQLite. When the app is opened, `SmsBackgroundService.syncPendingMessages()` runs to resolve all pending messages.
* **Network Failures:** Dio intercepts request timeouts, triggering retries. If all retries fail, the message state remains `'pending'` in the local database.
* **No local inference:** **The application does not perform ML inference locally.**

---

## 10.14 Implementation vs. Future Work

### 1. Implemented Features
* Native Kotlin background SMS interception and direct SQLite database writes.
* MethodChannel communication bridge for real-time app events.
* Contacts name resolution.
* Feature-based layout with Provider state management.

### 2. Not Implemented / Future Work
* **No Local Notifications:** The prototype **does not contain a notification package** (no `flutter_local_notifications` in `pubspec.yaml`). Incoming spam notifications are planned for **FYP2**.
* **Unencrypted Database:** SQLite files are saved as plain text (database encryption using SQLCipher is planned for **FYP2**).
* **On-Device Inference:** Local DistilBERT execution is not supported (planned for future optimization).

---

## 10.15 Chapter Summary

This chapter has detailed the mobile application architecture of MindShield. By combining native Android BroadcastReceivers with a Flutter MethodChannel bridge and a shared SQLite persistence layer, MindShield implements background message interception and local data sandboxing.

The validation testing, execution logs, and project results are detailed in **Chapter 11 — Verification, Validation & Testing**.

---

## Mobile Implementation Verification Summary

### Strongly Verified Features (Proven):
* Android `SmsReceiver.kt` handles the `SMS_RECEIVED` action and writes to SQLite (`mindshield.db`).
* MethodChannel `com.mindshield/sms_receiver` forwards events to `SmsBackgroundService`.
* Shared database queries and migrations (migrating v1 $\rightarrow$ v2 to delete seed data).
* Provider-based state management (`InboxProvider`, `DashboardProvider`).
* Routing layout using `GoRouter`.

### Contradictions Resolved:
* **No system notifications are implemented** in this prototype version (no notifications packages exist in dependencies).
* **No on-device ML model execution occurs** (inference is remote).
