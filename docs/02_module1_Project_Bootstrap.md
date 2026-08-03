# MindShield — Module 1: Project Bootstrap
## Complete Technical & Academic Documentation

> **Project:** MindShield — AI-Powered SMS Cybersecurity Application
> **Module:** 1 of N — Project Bootstrap & Architectural Foundation
> **Platform:** Android (Flutter 3.29.3 / Dart 3.7.2)
> **Author:** \[Your Name\]
> **Date:** July 2026

---

## Table of Contents

1. [Module Purpose & Scope](#1-module-purpose--scope)
2. [System Architecture](#2-system-architecture)
3. [Folder Structure](#3-folder-structure)
4. [Technology Stack & Dependency Analysis](#4-technology-stack--dependency-analysis)
5. [Data Flow & Lifecycle](#5-data-flow--lifecycle)
6. [Implementation Details](#6-implementation-details)
7. [Design Decisions & Rationale](#7-design-decisions--rationale)
8. [Engineering Challenges & Resolutions](#8-engineering-challenges--resolutions)
9. [Verification & Testing](#9-verification--testing)
10. [Thesis-Ready Academic Content](#10-thesis-ready-academic-content)
11. [References](#11-references)

---

## 1. Module Purpose & Scope

### 1.1 What This Module Does

Module 1 establishes the **complete engineering foundation** of the MindShield application. It produces no user-facing intelligence yet — its sole responsibility is to ensure every subsequent feature module has a stable, consistent, and well-structured platform to build upon.

Specifically, this module:

- Scaffolds the Flutter project with a production-grade Android target
- Defines and enforces the **Feature-First Clean Architecture** directory contract
- Installs and resolves all third-party dependencies the full application will require
- Configures a **Material Design 3** visual system (light and dark themes)
- Registers all eight application screens as **named routes** in a declarative router
- Creates **placeholder screens** for every feature so the navigation graph compiles and can be exercised immediately
- Provides a **singleton network client** stub ready to accept interceptors
- Validates the entire setup via static analysis and a successful debug APK compilation

### 1.2 What This Module Intentionally Defers

The following are deliberately *not* implemented in Module 1:

| Deferred Concern | Rationale |
|---|---|
| SMS reading / parsing | Requires permission grants; handled in Module 2 |
| AI inference calls | Requires a working backend; handled in Module 4 |
| Local database schema | Defined when first entity is known; Module 3 |
| Authentication / user accounts | Removed from scope — not required for an SMS security tool |
| Cybersecurity education content | Deferred as non-core feature |

### 1.3 Module Boundaries

```
┌─────────────────────────────────────────────────────┐
│                   Module 1 Boundary                 │
│                                                     │
│  flutter create → pubspec.yaml → core/ → features/  │
│  placeholder screens → GoRouter → Material 3 theme  │
│                                                     │
│  OUTPUT: Compilable, routable, themeable skeleton   │
└─────────────────────────────────────────────────────┘
         │
         ▼
   Module 2: Permissions
   Module 3: Inbox + DB
   Module 4: AI Analysis
   Module 5: Dashboard / Spam / History
   Module 6: Settings
```

---

## 2. System Architecture

### 2.1 Architectural Pattern: Feature-First Clean Architecture

MindShield adopts **Feature-First Clean Architecture**, a hybrid pattern that combines:

- **Vertical slicing** (organise by feature, not layer) for discoverability and independent development
- **Horizontal layering** within each feature (data → domain → presentation) for testability and separation of concerns
- **Provider** for reactive state management at the presentation layer

This is distinct from the traditional "layer-first" approach where all repositories live in one folder, all models in another, etc.

#### 2.1.1 Traditional Layer-First (Rejected)

```
lib/
├── data/          ← ALL data sources mixed together
├── domain/        ← ALL entities mixed together
└── presentation/  ← ALL screens mixed together
```

**Problem:** As features grow, each folder becomes a dumping ground. Adding or removing a feature requires hunting across three unrelated directories.

#### 2.1.2 Feature-First Clean Architecture (Adopted)

```
lib/
├── core/                    ← Cross-cutting concerns only
└── features/
    └── inbox/
        ├── data/            ← InboxDataSource, SmsModel, InboxRepository
        ├── domain/          ← SmsEntity, InboxRepositoryInterface
        └── presentation/    ← InboxScreen, InboxProvider
```

**Benefit:** The entire `inbox/` feature can be developed, tested, and even deleted as a self-contained unit. Other features are unaffected.

### 2.2 Layer Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  Widgets, Screens, Providers (ChangeNotifier)               │
│  Reads from domain. Emits UI events. No raw data access.    │
├─────────────────────────────────────────────────────────────┤
│                     DOMAIN LAYER                            │
│  Entities (pure Dart), Repository Interfaces (abstract)     │
│  Has zero Flutter imports. Fully unit-testable in isolation. │
├─────────────────────────────────────────────────────────────┤
│                      DATA LAYER                             │
│  Repository Implementations, Data Sources, DTOs/Models      │
│  Talks to SQLite, SMS platform API, HTTP backend.            │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Dependency Rule

The dependency rule (from Clean Architecture, R. Martin) states that **source code dependencies must point only inward**:

```
Presentation  →  Domain  ←  Data
```

- Presentation depends on Domain (uses entities and interfaces)
- Data depends on Domain (implements interfaces)
- Domain depends on **nothing** (no Flutter SDK, no Dio, no SQLite)

This means the domain layer can be tested with pure Dart, without a device or emulator.

### 2.4 State Management Architecture

```
User Action
    │
    ▼
Widget (StatelessWidget)
    │  context.read<Provider>().method()
    ▼
ChangeNotifier (Provider)
    │  calls domain use case / repository
    ▼
Repository Interface (domain)
    │  implemented by
    ▼
Repository Impl (data)
    │  reads/writes
    ▼
Data Source (SQLite / SMS API / HTTP)
    │
    ▼  notifyListeners()
Provider ──────────────────────► Widget rebuilds
```

### 2.5 Navigation Architecture

GoRouter uses a **URL-centric, declarative** model:

```
AppRouter (GoRouter)
    │
    ├── /                  → SplashScreen
    ├── /permissions       → PermissionsScreen
    ├── /dashboard         → DashboardScreen
    ├── /inbox             → InboxScreen
    ├── /spam              → SpamScreen
    ├── /analysis          → AnalysisScreen
    ├── /history           → HistoryScreen
    └── /settings          → SettingsScreen
```

A **redirect callback** (added in Module 2) will gate the `/dashboard` route behind a permissions check, routing users to `/permissions` if SMS access has not been granted.

---

## 3. Folder Structure

### 3.1 Complete Annotated Tree

```
mindshield/
│
├── android/                          ← Android host project
│   ├── app/
│   │   └── build.gradle.kts         ← NDK version pinned to 26.3.11579264
│   └── build.gradle.kts             ← Root Gradle (repositories, clean task)
│
├── assets/
│   ├── icons/                        ← SVG icon assets (populated in UI modules)
│   └── images/                       ← Brand images (populated in UI modules)
│
├── lib/
│   │
│   ├── core/                         ← Shared, feature-agnostic infrastructure
│   │   ├── constants/
│   │   │   └── app_constants.dart    ← All magic values in one place
│   │   ├── network/
│   │   │   └── dio_client.dart       ← Singleton Dio HTTP client stub
│   │   ├── router/
│   │   │   └── app_router.dart       ← GoRouter config + AppRoutes constants
│   │   └── theme/
│   │       └── app_theme.dart        ← Material 3 light + dark ThemeData
│   │
│   ├── features/                     ← One subfolder per vertical feature slice
│   │   ├── analysis/
│   │   │   └── presentation/
│   │   │       └── analysis_screen.dart
│   │   ├── dashboard/
│   │   │   └── presentation/
│   │   │       └── dashboard_screen.dart
│   │   ├── history/
│   │   │   └── presentation/
│   │   │       └── history_screen.dart
│   │   ├── inbox/
│   │   │   └── presentation/
│   │   │       └── inbox_screen.dart
│   │   ├── permissions/
│   │   │   └── presentation/
│   │   │       └── permissions_screen.dart
│   │   ├── settings/
│   │   │   └── presentation/
│   │   │       └── settings_screen.dart
│   │   ├── spam/
│   │   │   └── presentation/
│   │   │       └── spam_screen.dart
│   │   └── splash/
│   │       └── presentation/
│   │           └── splash_screen.dart
│   │
│   └── main.dart                     ← App entry point: MultiProvider + MaterialApp.router
│
├── test/
│   └── widget_test.dart              ← Smoke test: MindShieldApp mounts without error
│
└── pubspec.yaml                      ← Project metadata + all dependencies
```

### 3.2 Future Feature Expansion Contract

Every feature added after Module 1 **must** follow this internal structure:

```
features/<feature_name>/
├── data/
│   ├── datasources/
│   │   └── <name>_local_data_source.dart
│   ├── models/
│   │   └── <name>_model.dart          ← DTO with toJson/fromJson
│   └── repositories/
│       └── <name>_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── <name>_entity.dart         ← Pure Dart, no Flutter/Dio
│   └── repositories/
│       └── <name>_repository.dart     ← Abstract interface
└── presentation/
    ├── <name>_screen.dart
    └── providers/
        └── <name>_provider.dart       ← ChangeNotifier
```

---

## 4. Technology Stack & Dependency Analysis

### 4.1 Core Framework

| Technology | Version | Purpose |
|---|---|---|
| Flutter | 3.29.3 | UI framework and build toolchain |
| Dart | 3.7.2 | Programming language |
| Android SDK | 35 (compileSdk) | Android platform target |
| Android NDK | 26.3.11579264 | Native code compilation for plugins |

### 4.2 Third-Party Dependencies

#### State Management: `provider ^6.1.2`

**Provider** is a Flutter-first wrapper around `InheritedWidget`. It implements the **Observer pattern**: `ChangeNotifier` subclasses hold state and call `notifyListeners()` when it changes; widgets subscribed via `Consumer<T>` or `context.watch<T>()` rebuild automatically.

Chosen over alternatives because:
- **vs. Riverpod**: Provider is simpler for FYP scale; no code-gen required
- **vs. BLoC**: BLoC adds event/stream boilerplate; Provider is more readable for examiners
- **vs. GetX**: GetX mixes routing, DI, and state into one package — violates separation of concerns

#### Navigation: `go_router ^14.6.2`

**GoRouter** is the Flutter team's official router, built on the `Router` API (Navigator 2.0). It supports:
- URL-based navigation (deep links work out of the box)
- `redirect` callbacks for auth/permission gating
- Named routes to avoid hardcoded path strings
- `GoRouterState.extra` for passing objects between routes

Chosen over `Navigator.push()` because imperative navigation does not scale past 3–4 screens without becoming unmaintainable.

#### Networking: `dio ^5.7.0`

**Dio** is a Dart HTTP client that supports interceptors, request cancellation, multipart uploads, and response transformers. The `DioClient` singleton pattern ensures one HTTP client instance is shared across the application, avoiding connection pool fragmentation.

#### Local Storage — Key-Value: `shared_preferences ^2.3.3`

Wraps `SharedPreferences` (Android) and `NSUserDefaults` (iOS). Used for small, non-relational data: onboarding flags, theme mode preference, spam confidence threshold.

#### Local Storage — Relational: `sqflite ^2.4.1`

SQLite wrapper for Flutter. Used to persist SMS messages, analysis results, and scan history as structured, queryable relational data. Chosen over Hive/Isar because:
- SQL is a transferable skill the examiner will recognise
- Relational queries (filter by date, threat type, confidence) are natural in SQL

#### SMS Access: `flutter_sms_inbox ^1.0.4`

Reads the device's SMS inbox via Android's `ContentProvider` interface (URI: `content://sms/inbox`). Replaced the discontinued `telephony` package which was incompatible with Android Gradle Plugin 8.x due to a missing `namespace` declaration.

#### SVG Rendering: `flutter_svg ^2.0.10+1`

Renders `.svg` files as Flutter widgets. Required because icon assets in Material Design 3 are commonly distributed as SVGs; PNG alternatives at every density bucket would increase APK size.

### 4.3 Dependency Compatibility Matrix

```
Flutter 3.29.3
    ├── Dart SDK ≥3.7.0
    ├── Android Gradle Plugin 8.x
    │       └── Requires namespace in plugin build.gradle ✓
    ├── NDK 26.3.11579264 (installed) / 27.0.12077973 (advisory)
    └── All pub.dev packages resolved without version conflicts ✓
```

---

## 5. Data Flow & Lifecycle

### 5.1 Application Boot Sequence

```
main()
  │
  ├─ WidgetsFlutterBinding.ensureInitialized()
  │        Initialises Flutter engine bindings before any
  │        platform channel calls (required for async main).
  │
  └─ runApp(MindShieldApp())
           │
           └─ MultiProvider (empty in Module 1; populated per module)
                    │
                    └─ MaterialApp.router
                             │
                             ├─ theme: AppTheme.light
                             ├─ darkTheme: AppTheme.dark
                             ├─ themeMode: ThemeMode.system
                             └─ routerConfig: appRouter
                                      │
                                      └─ initialLocation: '/'
                                               │
                                               └─ SplashScreen
```

### 5.2 Navigation Flow (Current: Module 1)

```
App Launch
    │
    ▼
SplashScreen (/)
    │
    │  [In Module 2, redirect logic reads SharedPreferences]
    │
    ├──► PermissionsScreen (/permissions)   if SMS not granted
    │
    └──► DashboardScreen (/dashboard)       if SMS granted
              │
              ├──► InboxScreen (/inbox)
              ├──► SpamScreen (/spam)
              ├──► HistoryScreen (/history)
              └──► SettingsScreen (/settings)
                        │
                        └──► AnalysisScreen (/analysis)  [from Inbox/Spam items]
```

### 5.3 Theme Resolution Flow

```
Device OS setting (Light / Dark / Auto)
    │
    ▼
MaterialApp.router(themeMode: ThemeMode.system)
    │
    ├── Brightness.light → AppTheme.light
    │       ColorScheme.fromSeed(seed: #1E88E5, brightness: light)
    │
    └── Brightness.dark  → AppTheme.dark
            ColorScheme.fromSeed(seed: #1E88E5, brightness: dark)
```

Material 3's `ColorScheme.fromSeed()` generates a complete 30-colour tonal palette from a single seed colour, ensuring all UI components (buttons, cards, app bars, chips) are harmoniously coloured without manual specification.

### 5.4 Provider Data Flow (Future Modules)

```
ChangeNotifierProvider<InboxProvider>
    │
    ├── Exposed via context.watch<InboxProvider>()
    ├── State: List<SmsEntity>, LoadingState enum
    ├── On mount: calls repository.fetchAll()
    │       │
    │       └── InboxRepositoryImpl.fetchAll()
    │               │
    │               └── SmsLocalDataSource.queryDb() → SQFLite
    │
    └── On new SMS: telephony callback → repository.insert() → notifyListeners()
```

---

## 6. Implementation Details

### 6.1 `main.dart` — Entry Point

```dart
void main() {
  WidgetsFlutterBinding.ensureInitialized(); // (1)
  runApp(const MindShieldApp());
}
```

**(1) `WidgetsFlutterBinding.ensureInitialized()`**

This call is **mandatory** before any `async` operation that uses platform channels occurs before `runApp()`. Without it, the Flutter engine may not be ready to receive plugin calls (e.g., reading SharedPreferences in `main()` to decide initial route). Even though Module 1 makes no such calls, it is established here as a safety guard for future modules.

**`MultiProvider` placement:**

The `MultiProvider` is placed at the root of the widget tree — above `MaterialApp.router` — so that all `BuildContext`s in the application have access to the full provider tree. Placing it below `MaterialApp` would prevent screens from accessing providers during navigation.

### 6.2 `app_theme.dart` — Material 3 Design System

```dart
ColorScheme.fromSeed(
  seedColor: Color(0xFF1E88E5), // electric blue
  brightness: Brightness.light,
  error: Color(0xFFD32F2F),
)
```

**Why `ColorScheme.fromSeed()`?**

Material 3 (M3) replaces the manual primary/secondary colour system of M2 with a **tonal palette** derived algorithmically from a single seed colour using the HCT colour space (Hue, Chroma, Tone). This produces:

- Primary, secondary, tertiary colour roles
- Container variants for each role (e.g., `primaryContainer`)
- Surface, background, and error role colours
- On-colour variants (text on primary, text on surface, etc.)

A single seed colour thus generates a complete, accessible, and harmonious colour system that automatically adapts to light and dark modes.

**Why electric blue (`#1E88E5`) as the seed?**

Blue is psychologically associated with trust, security, and technology — all aligned with a cybersecurity application's brand values (Elliot & Maier, 2014).

### 6.3 `app_router.dart` — GoRouter Configuration

```dart
abstract class AppRoutes {
  static const String splash = '/';
  static const String permissions = '/permissions';
  // ...
}
```

**Why an `AppRoutes` abstract class?**

Path strings are defined **once** and referenced by name throughout the codebase. If a route path changes (e.g., `/inbox` → `/messages`), only one line changes. This eliminates the entire class of bugs caused by hardcoded string duplication.

**`debugLogDiagnostics: true`**

During development, GoRouter prints every route resolution, redirect evaluation, and navigation event to the debug console. This is invaluable for diagnosing incorrect redirect logic and will be set to `false` in the release build.

### 6.4 `app_constants.dart` — Configuration Hub

```dart
static const double spamThreshold = 0.70;
```

The 70% confidence threshold defines the boundary above which an SMS is labelled as spam. This value is centralised here so it can be:
1. Modified without searching the codebase
2. Overridden by the Settings module (persisted in SharedPreferences)
3. Referenced consistently across the analysis and spam filtering logic

### 6.5 `dio_client.dart` — Singleton Network Client

```dart
class DioClient {
  DioClient._();  // private constructor prevents external instantiation
  static final DioClient _instance = DioClient._();
  static DioClient get instance => _instance;

  late final Dio dio = Dio(BaseOptions(...));
}
```

**Singleton pattern rationale:**

A single `Dio` instance shares one connection pool across all HTTP requests. Multiple instances would open redundant connections to the same server, wasting memory and sockets. The `late final` keyword ensures the `Dio` object is created lazily (on first access) and never replaced.

**Interceptor hooks (future modules):**

```
DioClient.instance.dio.interceptors.addAll([
  AuthInterceptor(),    // attach JWT headers
  LogInterceptor(),     // log request/response in debug mode
  RetryInterceptor(),   // exponential back-off on 5xx
]);
```

---

## 7. Design Decisions & Rationale

### 7.1 Why Flutter (not React Native, not native Android)?

| Criterion | Flutter | React Native | Native Android |
|---|---|---|---|
| Single codebase | ✅ Dart | ✅ JS/TS | ❌ Java/Kotlin only |
| UI rendering | Own engine (Skia/Impeller) | Native bridge | Native |
| SMS plugin maturity | ✅ | ⚠️ Limited | ✅ Full |
| FYP development speed | Fast | Fast | Slow |
| Type safety | ✅ Strong (Dart) | ⚠️ TypeScript optional | ✅ |
| Material 3 support | ✅ Official | ⚠️ Third-party | ✅ Official |

Flutter's own rendering engine eliminates the native bridge that React Native depends on for every widget draw call, producing smoother 60/120fps animations and eliminating an entire class of bridge-related bugs.

### 7.2 Why Provider (not BLoC, not Riverpod)?

**BLoC** (Business Logic Component) uses Streams and Events. For a data-driven app with simple CRUD-style state, BLoC introduces unnecessary ceremony:

```dart
// BLoC: emit an event to fetch messages
context.read<InboxBloc>().add(FetchMessagesEvent());

// Provider: call a method directly
context.read<InboxProvider>().fetchMessages();
```

**Riverpod** is architecturally superior to Provider but requires understanding of `ref`, `Provider`, `AsyncNotifier`, and code generation for its full potential. For an FYP where the examiner may not be familiar with Riverpod-specific concepts, Provider's simplicity is an advantage.

### 7.3 Why GoRouter (not Navigator 1.0 push/pop)?

`Navigator.push()` (Navigator 1.0) is **imperative**: each screen is responsible for deciding what to push next. This creates tight coupling and makes adding a global redirect (e.g., "if permissions not granted, always go to permissions screen") require touching every screen.

GoRouter is **declarative**: the routing logic lives in one place (`app_router.dart`), routes are testable in isolation, and deep links work without additional configuration.

### 7.4 Why `telephony` was rejected in favour of `flutter_sms_inbox`

The `telephony` package (version 0.2.0, last updated 2021) was designed for Android Gradle Plugin (AGP) 4.x. AGP 8.x (used by Flutter 3.29.3) **requires** that every Android library declare a `namespace` in its `build.gradle` file. The `telephony` package does not — making it incompatible with the current toolchain.

`flutter_sms_inbox` provides equivalent SMS inbox reading functionality and is actively maintained, correctly declaring its AGP namespace.

### 7.5 Why Feature-First over Layer-First?

Consider the impact of adding a new "Reports" feature:

| Operation | Layer-First | Feature-First |
|---|---|---|
| Files to create | Spread across `data/`, `domain/`, `presentation/` | All in `features/reports/` |
| Files touched by deletion | 3+ directories | 1 directory |
| Risk of breaking other features | Higher (shared folders) | Lower (isolated folder) |
| IDE navigation | Requires mental mapping | `features/reports/` is self-contained |

---

## 8. Engineering Challenges & Resolutions

### Challenge 1: NDK Version Incompatibility

**Problem:** Plugins (`shared_preferences_android`, `sqflite_android`, `flutter_sms_inbox`) declared a dependency on NDK `27.0.12077973` in their Gradle configurations. The project's `app/build.gradle.kts` was using `flutter.ndkVersion`, which resolved to `26.3.11579264`.

**Attempted Fix 1:** Pin `ndkVersion = "27.0.12077973"` in `app/build.gradle.kts`.
**Result:** Build failed — NDK 27 folder existed on disk but contained only a `.installer` marker file, indicating a previously failed/interrupted SDK Manager download.

**Attempted Fix 2:** Override NDK version for all subprojects using `afterEvaluate` in root `build.gradle.kts`.
**Result:** Build failed — `afterEvaluate` cannot be called inside a `subprojects` block when `evaluationDependsOn(":app")` is present; the project is already evaluated at that point.

**Final Resolution:**
- Keep `ndkVersion = "26.3.11579264"` (fully installed NDK) in `app/build.gradle.kts`
- Remove the `afterEvaluate` hook entirely
- Verify that the NDK mismatch message is a **warning** (printed to `stderr`), not a build error — the APK compiles and links correctly with NDK 26

**Lesson learned:** The PowerShell `2>&1` redirect causes `NativeCommandError` when *any* text appears on stderr, even for successful processes. Verification must check `$LASTEXITCODE` rather than relying on PowerShell's exception model.

### Challenge 2: `telephony` Plugin Namespace Error

**Problem:** Android Gradle Plugin 8.x requires a `namespace` declaration in every library's `build.gradle`. The `telephony` 0.2.0 plugin predates this requirement and does not include it, causing configuration failure:

```
Could not create an instance of type LibraryVariantBuilderImpl.
> Namespace not specified.
```

**Resolution:** Replace `telephony: ^0.2.0` with `flutter_sms_inbox: ^1.0.4`. Both packages provide read access to the device SMS inbox, but `flutter_sms_inbox` is AGP 8.x-compatible.

### Challenge 3: Stale Widget Test After Class Rename

**Problem:** `flutter create` generates `test/widget_test.dart` referencing `MyApp`. Replacing `main.dart`'s content with `MindShieldApp` caused `flutter analyze` to report:

```
error - The name 'MyApp' isn't a class - test/widget_test.dart:16:35
```

**Resolution:** Rewrote `widget_test.dart` to import `MindShieldApp`, pump the widget tree, and assert the splash screen renders the text `'MindShield'`.

### Challenge 4: `const` Lint on Empty List Literal

**Problem:** `providers: const []` in `MultiProvider` triggered an info-level lint:

```
'const' modifier can't be applied to a mutable list
```

**Resolution:** Changed to `providers: []` (non-const). The `const` keyword on a list literal that will later be populated with non-const values is semantically incorrect.

---

## 9. Verification & Testing

### 9.1 Static Analysis

```bash
flutter analyze
# Output: No issues found. (ran in 6.5s)
```

`flutter analyze` runs the Dart analyser across the entire project, checking for:
- Type errors
- Unused imports
- Unreachable code
- Lint violations defined in `analysis_options.yaml` (using `flutter_lints` ruleset)

### 9.2 Smoke Test

```dart
// test/widget_test.dart
testWidgets('MindShieldApp smoke test', (WidgetTester tester) async {
  await tester.pumpWidget(const MindShieldApp());
  expect(find.text('MindShield'), findsOneWidget);
});
```

This test verifies that:
1. The widget tree mounts without throwing
2. The splash screen renders its title text

### 9.3 Build Verification

```bash
flutter build apk --debug
# Output: ✓ Built build\app\outputs\flutter-apk\app-debug.apk
# Exit code: 0
```

A successful debug APK build confirms:
- All Dart code compiles
- All plugin native code compiles (Kotlin/Java)
- Gradle dependency graph resolves
- NDK toolchain links correctly
- Asset bundles are packaged

### 9.4 Verification Matrix

| Test Type | Tool | Result |
|---|---|---|
| Static analysis | `flutter analyze` | ✅ No issues |
| Widget smoke test | `flutter test` | ✅ Pass |
| Debug compilation | `flutter build apk --debug` | ✅ Exit code 0 |
| Dependency resolution | `flutter pub get` | ✅ 36 packages |

---

---

## 10. Thesis-Ready Academic Content

### 10.1 Abstract (Module 1 Contribution)

> The development of a production-grade mobile application requires a foundational engineering phase that, while producing no directly user-observable output, determines the long-term maintainability, scalability, and testability of the entire system. This section documents the architectural bootstrapping of MindShield, an AI-powered Short Message Service (SMS) cybersecurity application developed for the Android platform using the Flutter framework. The bootstrap phase established a Feature-First Clean Architecture directory contract, configured a Material Design 3 visual design system, integrated a declarative navigation framework, and resolved a series of Android build toolchain compatibility issues arising from the use of a contemporary Gradle plugin version. The resulting project skeleton passes static analysis with zero violations and produces a valid Android Package Kit (APK) artefact, providing a verified foundation for subsequent feature development.

---

### 10.2 Introduction

The proliferation of SMS-based phishing attacks — commonly referred to as "smishing" — has created a pressing need for intelligent, on-device threat detection systems accessible to general users (Mishra & Soni, 2019). MindShield addresses this problem by applying machine learning classification to incoming SMS messages, categorising them as legitimate, suspicious, or spam with an associated confidence score.

Prior to implementing any detection capability, a robust software engineering foundation must be established. This is not merely a practical necessity but an architectural decision that constrains and enables all subsequent engineering choices. The selection of an architectural pattern, state management library, navigation framework, and data persistence strategy collectively determine whether the application will remain maintainable as it scales from a single-feature prototype to a multi-module production system.

This chapter documents the design and implementation of Module 1: the project bootstrap. It examines the rationale behind each architectural decision, catalogues the engineering challenges encountered during environment configuration, and demonstrates the verification methodology used to confirm the module's correctness.

---

### 10.3 Architectural Design

#### 10.3.1 Feature-First Clean Architecture

The architecture adopted for MindShield is a variant of the Clean Architecture framework proposed by Martin (2017), adapted for the vertical-slicing concerns of a feature-rich mobile application. The central principle of Clean Architecture — that the dependency graph must point inward, from low-level implementation details toward high-level business policies — is preserved. However, rather than organising files by technical layer across the entire application, MindShield organises files by feature first, then by layer within each feature.

This pattern is consistent with the emerging practice of "screaming architecture" (Martin, 2012), wherein the top-level directory structure communicates the application's domain — its features and capabilities — rather than its technical implementation details. An examiner reviewing `lib/features/inbox/domain/entities/sms_entity.dart` immediately understands the context of that file (the inbox feature's domain model of an SMS message) without requiring any additional documentation.

The three internal layers within each feature follow Clean Architecture's dependency rule:

**(i) Domain Layer.** Contains pure Dart entity classes and abstract repository interfaces. This layer has no dependencies on Flutter, Dart I/O, SQLite, or any third-party package. It encodes the application's business rules in the most portable, testable form possible. The domain layer of MindShield will define the `SmsEntity`, `SpamAnalysisEntity`, and `ScanHistoryEntity` classes, along with abstract interfaces such as `InboxRepository` and `AnalysisRepository`.

**(ii) Data Layer.** Contains concrete implementations of the domain's abstract interfaces, data transfer objects (DTOs), and the data source classes that communicate with SQLite, the Android SMS ContentProvider, and the remote AI inference endpoint. This layer depends on the domain layer (it implements its interfaces) but is itself unknown to the domain layer, satisfying the dependency inversion principle.

**(iii) Presentation Layer.** Contains Flutter widgets, screen classes, and `ChangeNotifier` subclasses (Providers). The presentation layer reads application state from Providers and dispatches actions (method calls) back to them. It has no direct knowledge of data sources — all state transitions are mediated through the domain layer.

#### 10.3.2 State Management

The Provider package (version 6.1.2) was selected as the state management solution for MindShield. Provider implements the Observer pattern through Flutter's `InheritedWidget` mechanism: a `ChangeNotifier` subclass holds application state and broadcasts change notifications via `notifyListeners()`, triggering widget subtrees registered with `Consumer<T>` or `context.watch<T>()` to rebuild.

This choice was made after evaluating three principal alternatives. The BLoC (Business Logic Component) pattern, proposed by Soares (2018), uses asynchronous `Stream`s and explicit `Event` classes to communicate state changes. While BLoC provides clear audit trails of state transitions, its verbosity introduces substantial boilerplate for the CRUD-dominated data flows present in MindShield (fetch messages, insert analysis result, update spam flag). The Riverpod library (Rousselet, 2021) offers a compile-safe, testable extension of Provider's model but requires familiarity with its `ProviderScope`, `Ref`, and `AsyncNotifier` primitives that may reduce accessibility for academic assessment. Provider's explicit method-call model — `context.read<InboxProvider>().fetchMessages()` — was judged most legible for the intended audience.

#### 10.3.3 Navigation

GoRouter (version 14.6.2), the navigation solution officially recommended by the Flutter team, was adopted for its declarative routing model. In contrast to Navigator 1.0's imperative `push`/`pop` API, GoRouter defines all application routes in a single configuration object. Navigation state is expressed as a URL path, enabling deep-link support without additional configuration and facilitating the implementation of cross-cutting navigation concerns — such as permission gating — as `redirect` callbacks applied uniformly to all routes.

The separation of routing logic from screen logic is consistent with the Single Responsibility Principle: screens are responsible for their own UI; the router is responsible for navigation policy. This becomes particularly significant in Module 2, where the permission check redirect must intercept navigation to any protected route.

---

### 10.4 Implementation

The Flutter project was initialised using the `flutter create` command with the `--org com.mindshield` and `--platforms android` flags, producing the Android-specific project scaffolding including the Gradle build system, `AndroidManifest.xml`, and required directory structure.

The Material Design 3 theme was configured through Flutter's `ColorScheme.fromSeed()` API, which derives a complete thirty-colour tonal palette from a single seed colour (`#1E88E5`, electric blue) using the HCT (Hue, Chroma, Tone) colour space. Both light and dark `ThemeData` instances share the same seed colour, ensuring visual consistency across system theme modes. The theme is applied at the root of the widget tree via `MaterialApp.router`, making it available to all descendant widgets through the `Theme.of(context)` accessor.

Eight named routes were registered in the GoRouter configuration, corresponding to the eight primary screens of the application: Splash, Permissions, Dashboard, Inbox, Spam, Analysis, History, and Settings. Each route maps to a placeholder `StatelessWidget` containing a descriptive doc-comment outlining the widget's intended future functionality. This approach allows the navigation graph to be compiled and exercised in its entirety before any individual screen is implemented, reducing integration risk in later development phases.

---

### 10.5 Challenges and Resolutions

The bootstrapping phase encountered three engineering challenges that required systematic diagnosis and resolution, each offering insight into the complexity of managing cross-platform build toolchains.

**Build Toolchain Compatibility.** The Android Gradle Plugin version 8.x, required by Flutter 3.29.3, mandates that all Android library modules declare a `namespace` property in their `build.gradle` configuration. The `telephony` plugin (version 0.2.0), selected for its SMS access capabilities, was published in 2021 under AGP 4.x conventions and does not include this declaration. This produced a configuration-phase build failure. Resolution required identifying and substituting an AGP 8.x-compatible alternative (`flutter_sms_inbox` 1.0.4) with equivalent SMS inbox reading functionality.

**NDK Version Management.** Three plugin subprojects (`shared_preferences_android`, `sqflite_android`, `flutter_sms_inbox`) declared a compilation dependency on Android NDK version 27.0.12077973. The local development environment had NDK 26.3.11579264 fully installed; NDK 27 was present in the SDK directory only as an `.installer` marker from a previously failed download, lacking the actual toolchain binaries. Specifying NDK 27 in the build configuration caused a `InstallFailedException` as Gradle attempted auto-installation. The resolution was to pin the `ndkVersion` to the installed NDK 26. Investigation confirmed that the mismatch produces an advisory warning — not a build error — because NDK versions within a major release are ABI-compatible.

**PowerShell Standard Error Conflation.** Verification of build success was complicated by PowerShell's error handling model: the `2>&1` redirect operator causes PowerShell to raise a `NativeCommandError` when any text appears on the `stderr` stream, regardless of the process's actual exit code. Flutter's Gradle integration prints the NDK advisory and the x86 deprecation notice to `stderr`, causing PowerShell to report exit code 1 even when the APK was successfully produced. Correct verification required checking `$LASTEXITCODE` independently of PowerShell's exception mechanism, which confirmed exit code 0 and a valid APK artefact.

---

### 10.6 Verification

The correctness of the bootstrap module was verified through three complementary mechanisms. Static analysis using `flutter analyze` confirmed zero violations across all source files. A widget smoke test using `flutter test` validated that the application's root widget mounts without runtime exceptions and that the splash screen renders its title text. Debug APK compilation using `flutter build apk --debug` verified that all Dart source code, Kotlin plugin bindings, and NDK-compiled native libraries link correctly into a deployable Android package. All three checks were executed in sequence and passed, providing high confidence in the module's correctness as a foundation for subsequent development.

---

### 10.7 Conclusion

This chapter has presented the design, implementation, and verification of the MindShield project's architectural bootstrap. The Feature-First Clean Architecture structure establishes a scalable, testable codebase organisation that will accommodate the addition of AI inference, database persistence, and real-time SMS monitoring in subsequent modules without architectural refactoring. The resolution of three build toolchain challenges provides a stable and well-understood Android build environment. The resulting artefact — a compilable, routable, and correctly themed Flutter application skeleton — constitutes the necessary and sufficient foundation for the feature development phases documented in subsequent chapters.

---

## 11. References

- Flutter Team. (2024). *Flutter documentation: Go Router*. Google. https://pub.dev/packages/go_router
- Flutter Team. (2024). *Material Design 3 in Flutter*. Google. https://m3.material.io/develop/flutter
- Martin, R. C. (2012). *The screaming architecture*. Clean Coder Blog. https://blog.cleancoder.com/uncle-bob/2011/09/30/Screaming-Architecture.html
- Martin, R. C. (2017). *Clean architecture: A craftsman's guide to software structure and design*. Prentice Hall.
- Mishra, S., & Soni, D. (2019). SMS phishing and mitigation approaches. *2019 Twelfth International Conference on Contemporary Computing (IC3)*, 1–5. IEEE.
- Natebosch. (2022). *flutter_sms_inbox*. pub.dev. https://pub.dev/packages/flutter_sms_inbox
- Rousselet, R. (2021). *Riverpod: A reactive caching and data-binding framework*. pub.dev. https://pub.dev/packages/riverpod
- Soares, F. (2018). *BLoC — Business logic component*. Medium / Flutter Community. https://medium.com/flutter-community/bloc-0-0-7-its-time-to-learn-it-ef7eafbe3c57
- Remi Rousselet. (2021). *Provider package*. pub.dev. https://pub.dev/packages/provider
- Elliot, A. J., & Maier, M. A. (2014). Color psychology: Effects of perceiving color on psychological functioning in humans. *Annual Review of Psychology*, 65, 95–120.

---

*Document prepared for MindShield Final Year Project — Module 1: Project Bootstrap*
*Flutter 3.29.3 | Dart 3.7.2 | Android NDK 26.3.11579264 | AGP 8.x*
