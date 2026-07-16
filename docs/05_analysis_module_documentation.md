# MindShield – AI Threat Analysis Module
### Technical Documentation · v1.0 · July 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Data Layer](#3-data-layer)
4. [Domain Layer](#4-domain-layer)
5. [Presentation Layer](#5-presentation-layer)
   - [AnalysisProvider](#51-analysisprovider)
   - [AnalysisScreen](#52-analysisscreen)
   - [Reusable Widgets](#53-reusable-widgets)
6. [LIME Explainability Integration](#6-lime-explainability-integration)
7. [State Management Flow](#7-state-management-flow)
8. [Animation Architecture](#8-animation-architecture)
9. [UI/UX Design Decisions](#9-uiux-design-decisions)
10. [Dummy Data Strategy](#10-dummy-data-strategy)
11. [Extension Points](#11-extension-points)
12. [API Contract (Future Backend)](#12-api-contract-future-backend)
13. [Test Coverage Strategy](#13-test-coverage-strategy)
14. [File & Folder Reference](#14-file--folder-reference)

---

## 1. Overview

The **Analysis Module** is the core intelligence-display layer of MindShield. It receives a selected `SmsMessage` from the Inbox module and presents a comprehensive AI threat analysis report to the user.

### Key Features

| Feature | Description |
|---|---|
| **Threat Score Gauge** | Animated radial arc (0–100) with colour gradient |
| **Confidence Bar** | Linear bar showing AI model certainty (%) |
| **Attack Classification** | Categorised attack type with description |
| **Psychological Tactics** | Detected NLP manipulation strategies as chips |
| **LIME Highlights** | Suspicious keywords highlighted by feature importance |
| **AI Explanation** | Natural-language reasoning from the NLP pipeline |
| **Sender Intelligence** | Country, carrier, line type, report count, scammer flag |
| **Recommendations** | Numbered, context-aware action guidance |
| **Action Buttons** | Move to Spam · Mark Safe · Block Sender · Report |

### Design Principles

- **Production-quality UI** using Material 3, custom painters, and multi-step animations.
- **Clean Architecture** with strict separation of data / domain / presentation.
- **Provider state management** — no global singletons leaking into the UI layer.
- **Dummy-first development** — all data is realistic but hard-coded, ready for API swap.
- **LIME-ready placeholder** — keyword highlighting matches the expected LIME output format.

---

## 2. Architecture

The Analysis module follows the **Feature-First Clean Architecture** established in the MindShield project:

```
lib/features/analysis/
├── data/
│   └── dummy_analysis_repository.dart   # Implements analysis retrieval (dummy)
├── domain/
│   └── analysis_result.dart             # Pure Dart entities & enums (no Flutter deps)
└── presentation/
    ├── analysis_provider.dart            # ChangeNotifier: state + actions
    ├── analysis_screen.dart              # Root screen widget
    └── widgets/
        ├── threat_score_gauge.dart       # CustomPainter radial gauge
        ├── confidence_bar.dart           # Animated LinearProgressIndicator
        ├── attack_type_card.dart         # Attack type + tactic chips
        ├── lime_highlight_card.dart      # RichText keyword highlighter
        ├── ai_explanation_card.dart      # Faded explanation text card
        ├── sender_info_card.dart         # Sender metadata display
        ├── recommendations_card.dart     # Staggered numbered list
        └── action_buttons_bar.dart       # 4-button action bar
```

### Dependency Rule

> **Presentation** → **Domain** ← **Data**

- The `domain/` layer has **zero** Flutter or external library imports.
- `data/` implements retrieval logic and maps to domain entities.
- `presentation/` reads domain entities via the provider — never touches `data/` directly.

---

## 3. Data Layer

### `DummyAnalysisRepository`

**Location:** `lib/features/analysis/data/dummy_analysis_repository.dart`

**Pattern:** Singleton (`DummyAnalysisRepository.instance`) — will be replaced by dependency injection when the real API is ready.

**Responsibilities:**
- Maintains a static `Map<String, AnalysisResult>` keyed by `messageId`.
- Simulates AI inference latency with `Future.delayed(1200ms)`.
- Returns a sensible fallback `AnalysisResult` for messages without an entry.

**Swap strategy (production):**
```dart
// AnalysisProvider (current)
final _repo = DummyAnalysisRepository.instance;

// AnalysisProvider (production — one-line swap)
final _repo = ApiAnalysisRepository(client: DioClient.instance);
```

---

## 4. Domain Layer

### `AnalysisResult`

**Location:** `lib/features/analysis/domain/analysis_result.dart`

The primary domain entity returned by every analysis request:

| Field | Type | Description |
|---|---|---|
| `messageId` | `String` | Links result to its `SmsMessage` |
| `threatScore` | `int` (0–100) | Overall threat severity |
| `confidencePercent` | `int` (0–100) | Model certainty in classification |
| `attackType` | `AttackType` | Primary attack vector enum |
| `psychologicalTactics` | `List<PsychologicalTactic>` | NLP-detected manipulation tactics |
| `suspiciousKeywords` | `List<SuspiciousKeyword>` | LIME feature-weighted keywords |
| `aiExplanation` | `String` | Natural-language reasoning text |
| `senderInfo` | `SenderInfo` | Enriched sender metadata |
| `recommendations` | `List<String>` | Ordered action recommendations |
| `analysisTimestamp` | `DateTime` | UTC analysis completion time |
| `modelVersion` | `String` | e.g. `"MindShield-NLP v2.3.1"` |
| `processingTimeMs` | `int` | Inference pipeline duration |

### `AttackType` Enum (11 values)

```dart
enum AttackType {
  phishing, smishing, vishing, prizeScam, investmentFraud,
  deliveryScam, governmentImpersonation, cryptoScam,
  piiHarvesting, malwareDistribution, benign,
}
```

Each value provides `.label` and `.description` via extension.

### `PsychologicalTactic` Enum (10 values)

```dart
enum PsychologicalTactic {
  urgency, fearInduction, authority, scarcity, socialProof,
  reciprocity, curiosity, greed, trustBuilding, isolation,
}
```

Each value provides `.label` (display name) and `.icon` (emoji) via extension.

### `SuspiciousKeyword`

```dart
class SuspiciousKeyword {
  final String word;     // Exact phrase from message body
  final double weight;   // LIME importance: 0.0–1.0
  final String reason;   // Human-readable explanation
}
```

### `SenderInfo`

```dart
class SenderInfo {
  final String displayName;    // Contact name or "Unknown Sender"
  final String phoneNumber;    // Raw number string
  final String countryCode;    // ISO 3166-1 alpha-2 (e.g. "ZA")
  final String countryName;
  final DateTime firstSeenDate; // First threat report date
  final int reportCount;        // Crowd-sourced report total
  final bool isKnownScammer;
  final String? carrierName;
  final String? lineType;       // "Mobile" | "VoIP" | "Short Code"
}
```

---

## 5. Presentation Layer

### 5.1 AnalysisProvider

**Location:** `lib/features/analysis/presentation/analysis_provider.dart`

**Extends:** `ChangeNotifier`

**Scope:** Created by `ChangeNotifierProvider` *inside* `AnalysisScreen`, not at the app root. This means the provider's lifetime is tied to the screen — it is disposed when the user navigates away.

#### State Fields

| Field | Type | Description |
|---|---|---|
| `_analysisResult` | `AnalysisResult?` | The loaded result (null while loading) |
| `_isLoading` | `bool` | True during API/repo fetch |
| `_errorMessage` | `String?` | Set on exception |
| `_actionState` | `AnalysisActionState` | Tracks which action button is processing |
| `_currentMessage` | `SmsMessage?` | Guards against redundant re-fetch |

#### `AnalysisActionState` Enum

```dart
enum AnalysisActionState {
  idle, movingToSpam, markingSafe, blockingSender, reporting,
}
```

#### Public API

| Method | Description |
|---|---|
| `loadAnalysis(SmsMessage)` | Fetches analysis; skips if same message already loaded |
| `moveToSpam()` | Sets `movingToSpam` state, awaits action, resets to `idle` |
| `markSafe()` | Sets `markingSafe` state, awaits action, resets to `idle` |
| `blockSender()` | Sets `blockingSender` state, awaits action, resets to `idle` |
| `report()` | Sets `reporting` state, awaits action, resets to `idle` |

### 5.2 AnalysisScreen

**Location:** `lib/features/analysis/presentation/analysis_screen.dart`

The root widget accepts `SmsMessage? message` from GoRouter's `extra` parameter. It:

1. If `message == null` → shows `_NoMessageState` with back button.
2. Creates a scoped `ChangeNotifierProvider<AnalysisProvider>` and calls `loadAnalysis`.
3. Renders a `CustomScrollView` with:
   - `SliverAppBar.large` (hero with gradient background, verdict label, sender info).
   - `SliverToBoxAdapter` for the gauge + confidence section.
   - `SliverList` for the 6 content cards.
4. Shows `_LoadingState` (pulsing icon + progress bar) while fetching.
5. Shows `_ErrorState` (retry button) on failure.

#### Screen States

```
AnalysisScreen
  ├── message == null → _NoMessageState
  └── message != null
        ├── isLoading = true → _LoadingState (animated)
        ├── errorMessage != null → _ErrorState (retry button)
        └── analysisResult != null → Full content
```

### 5.3 Reusable Widgets

#### `ThreatScoreGauge`
- **File:** `widgets/threat_score_gauge.dart`
- **Type:** `StatefulWidget` with `SingleTickerProviderStateMixin`
- **Technique:** `CustomPainter` draws a 240° arc with:
  - Background track arc
  - Gradient foreground arc (green → amber → orange → red)
  - Animated tip dot at the sweep position
  - 10 tick marks
  - "0" and "100" labels
- **Animation:** `CurvedAnimation(curve: Curves.easeOutCubic)` over 1400ms
- **Props:** `score` (int 0–100), `size` (double, default 200)

#### `ConfidenceBar`
- **File:** `widgets/confidence_bar.dart`
- **Type:** `StatefulWidget`
- **Technique:** Animated `LinearProgressIndicator` with count-up label
- **Colours:** Blue ≥90% / Green ≥70% / Amber <70%
- **Animation:** 1000ms `easeOutCubic`

#### `AttackTypeCard`
- **File:** `widgets/attack_type_card.dart`
- **Type:** `StatelessWidget`
- **Renders:** Colour-coded container with attack icon, label, description, then a `Wrap` of `_TacticChip` widgets for each psychological tactic.

#### `LimeHighlightCard` *(LIME Placeholder)*
- **File:** `widgets/lime_highlight_card.dart`
- **Type:** `StatelessWidget`
- **Technique:** `RichText` with `TextSpan` children. Suspicious keywords are matched case-insensitively in the message body and highlighted with:
  - Background colour opacity ∝ LIME weight (0.08–0.35 alpha)
  - Bold orange-red foreground
  - Dotted underline decoration
- Below the body, a ranked keyword list shows each word's LIME weight as a mini bar chart + description.
- **Production integration:** Replace the string-search matching with server-provided character offsets (`[start, end]` spans) from the LIME backend.

#### `AiExplanationCard`
- **File:** `widgets/ai_explanation_card.dart`
- **Type:** `StatefulWidget`
- **Animation:** 700ms `FadeTransition` with 600ms initial delay (so it appears after the gauge animates).
- **Design:** Gradient "MindShield AI" badge header + styled italic explanation block with gradient border.

#### `SenderInfoCard`
- **File:** `widgets/sender_info_card.dart`
- **Type:** `StatelessWidget`
- Renders: Country flag avatar (Unicode Regional Indicator conversion), known-scammer badge, info chips (country, carrier, line type, first seen), and a crowd-report count bar.

#### `RecommendationsCard`
- **File:** `widgets/recommendations_card.dart`
- **Type:** `StatefulWidget` with `SingleTickerProviderStateMixin`
- **Animation:** Staggered `SlideTransition` + `FadeTransition` per item. Items slide in from right sequentially with `Interval` curves.

#### `ActionButtonsBar`
- **File:** `widgets/action_buttons_bar.dart`
- **Type:** `StatelessWidget` (reads Provider via `context.watch`)
- **Layout:** Two rows of two buttons:
  - Row 1: Move to Spam (outlined, orange) + Mark Safe (filled, green)
  - Row 2: Block Sender (outlined, red) + Report (filled, red)
- Each button shows a `CircularProgressIndicator` while its action is processing.
- On completion, a `SnackBar` confirms the action.
- All buttons are disabled while any action is in progress (`isActionBusy`).

---

## 6. LIME Explainability Integration

LIME (Local Interpretable Model-Agnostic Explanations) is a post-hoc explainability technique that approximates a complex model's local behaviour with a simpler, interpretable surrogate.

### Current Implementation (Placeholder)

The `LimeHighlightCard` widget currently:
1. Receives pre-computed `List<SuspiciousKeyword>` from the repository.
2. Searches the message body for each keyword (case-insensitive).
3. Applies highlight intensity proportional to the `weight` field.

### Production LIME Pipeline

```
SMS Message Text
      ↓
[Tokenisation] → BERT/TF-IDF feature extraction
      ↓
[Bi-LSTM / SVM Classifier] → Classification + confidence
      ↓
[LIME Explainer]
  ├── Perturbs input (replaces words with [MASK])
  ├── Queries classifier on N perturbed samples
  ├── Fits linear surrogate model
  └── Returns feature weights per token
      ↓
[Backend API] → { word, start_char, end_char, weight, reason }
      ↓
[LimeHighlightCard] → RichText highlighting
```

### Required API Response Schema

```json
{
  "lime_keywords": [
    {
      "word": "URGENT",
      "start_char": 0,
      "end_char": 6,
      "weight": 0.94,
      "reason": "High-urgency trigger word – top LIME feature contributor."
    }
  ]
}
```

### UI Mapping

| LIME Weight | Background Alpha | Visual Effect |
|---|---|---|
| 0.8 – 1.0 | 0.28 – 0.35 | Strong highlight (deep orange) |
| 0.5 – 0.79 | 0.18 – 0.27 | Moderate highlight |
| 0.0 – 0.49 | 0.08 – 0.17 | Subtle highlight |

---

## 7. State Management Flow

```
GoRouter navigates to /analysis with SmsMessage as extra
          ↓
AnalysisScreen.build()
  ├── Creates ChangeNotifierProvider<AnalysisProvider>
  └── Calls provider.loadAnalysis(message) in create:
          ↓
AnalysisProvider.loadAnalysis()
  ├── Sets _isLoading = true → notifyListeners()
  ├── _AnalysisView renders _LoadingState
  ├── Awaits DummyAnalysisRepository.getAnalysis() (1.2s delay)
  ├── Sets _analysisResult = result → _isLoading = false → notifyListeners()
  └── _AnalysisView renders full content
          ↓
User taps "Report" button
  ├── ActionButtonsBar calls provider.report()
  ├── Sets _actionState = reporting → notifyListeners()
  ├── Button shows CircularProgressIndicator
  ├── Awaits _repo.submit() (0.9s delay)
  ├── Sets _actionState = idle → notifyListeners()
  └── SnackBar "Reported to MindShield threat database"
```

---

## 8. Animation Architecture

| Widget | Controller Duration | Curve | Effect |
|---|---|---|---|
| `ThreatScoreGauge` | 1400ms | `easeOutCubic` | Arc sweep + score count-up |
| `ConfidenceBar` | 1000ms | `easeOutCubic` | Bar fill + percentage count-up |
| `AiExplanationCard` | 700ms (+ 600ms delay) | `easeIn` | FadeTransition |
| `RecommendationsCard` | 400ms + N×120ms | `easeOut` (staggered intervals) | SlideTransition + FadeTransition per item |
| `_LoadingState` | 1000ms (repeat) | `easeInOut` | Pulsing ScaleTransition |

**Why `easeOutCubic` for gauges?** It mimics the physical deceleration of a real analogue needle, making the UI feel premium and grounded.

**Why staggered recommendations?** Staggering each item by 120ms creates a reading rhythm that naturally guides the eye through the list, improving comprehension.

---

## 9. UI/UX Design Decisions

### Colour System

| Status | Hero Background | Meaning |
|---|---|---|
| `safe` | `#2E7D32` (dark green) | Clear — no action required |
| `suspicious` | `#E65100` (deep orange) | Caution — review before acting |
| `scam` | `#C62828` (dark red) | Danger — confirmed threat |

### Gauge Design Rationale

The radial gauge was chosen over a simple percentage number because:
- It communicates severity **spatially** (more sweep = more danger).
- The gradient (green→red) aligns with universal traffic-light mental models.
- The animated sweep gives the screen a premium, app-like feel on first open.

### LIME Highlight Colour Choice

Orange-red highlights (`#BF360C`) were chosen because:
- They are clearly distinct from normal text without causing panic for low-weight words.
- The opacity-based intensity lets users quickly identify the highest-risk terms.
- The dotted underline signals "flagged" without being visually aggressive.

### Action Button Layout

Two rows of two buttons allow all four actions to be reachable without scrolling, while maintaining adequate touch-target size (≥48dp height). The fill/outlined distinction creates a clear visual hierarchy between primary (filled) and secondary (outlined) actions.

---

## 10. Dummy Data Strategy

Dummy data covers **8 out of 12** inbox messages with full `AnalysisResult` objects:

| Message ID | Status | Attack Type | Tactics |
|---|---|---|---|
| `msg_001` | Safe | Benign | — |
| `msg_002` | Scam | Phishing | Urgency, Fear, Authority |
| `msg_003` | Safe | Benign | — |
| `msg_004` | Scam | Prize Scam | Greed, Scarcity, Isolation |
| `msg_006` | Suspicious | Investment Fraud | Greed, Trust Building, Curiosity |
| `msg_008` | Scam | Gov. Impersonation | Authority, Scarcity, Greed, Fear |
| `msg_010` | Suspicious | Delivery Scam | Urgency, Scarcity, Authority |
| `msg_012` | Scam | Crypto Scam | Urgency, Fear, Authority, Scarcity |

Messages without an explicit entry receive a sensible fallback (`benign`, 5/100 threat score).

All LIME keyword weights, psychological tactic selections, and AI explanations were authored to be **academically accurate** — they reflect real-world NLP threat detection literature.

---

## 11. Extension Points

### Adding a New Attack Type

1. Add value to `AttackType` enum in `domain/analysis_result.dart`.
2. Add `label`, `description` to `AttackTypeX` extension.
3. Add an icon mapping in `AttackTypeCard._attackIcon()`.
4. Add `color` mapping in `AttackTypeCard._attackColor()` if needed.

### Connecting the Real API

1. Create `lib/features/analysis/data/api_analysis_repository.dart`.
2. Implement `getAnalysis(SmsMessage) → Future<AnalysisResult>` calling `DioClient`.
3. In `AnalysisProvider`, replace:
   ```dart
   final _repo = DummyAnalysisRepository.instance;
   ```
   with:
   ```dart
   final _repo = ApiAnalysisRepository(client: DioClient.instance);
   ```

### Using Real LIME Output

Replace `LimeHighlightCard`'s string-search approach with character-offset spans:
```dart
// Current: string search
final idx = lower.indexOf(kw.word.toLowerCase(), offset);

// Future: server-provided offsets
final idx = kw.startChar;  // from API response
final end = kw.endChar;
```

---

## 12. API Contract (Future Backend)

**Endpoint:** `POST /api/v1/analyse`

**Request:**
```json
{
  "message_id": "msg_002",
  "body": "URGENT: Your bank account has been suspended...",
  "sender": "+1 (888) 220-5530",
  "timestamp": "2026-07-16T07:38:00Z"
}
```

**Response:**
```json
{
  "message_id": "msg_002",
  "threat_score": 99,
  "confidence_percent": 99,
  "attack_type": "phishing",
  "psychological_tactics": ["urgency", "fear_induction", "authority"],
  "lime_keywords": [
    { "word": "URGENT", "start_char": 0, "end_char": 6, "weight": 0.94, "reason": "..." }
  ],
  "ai_explanation": "...",
  "sender_info": {
    "display_name": "Unknown Sender",
    "phone_number": "+1 (888) 220-5530",
    "country_code": "US",
    "country_name": "United States",
    "first_seen_date": "2026-07-10",
    "report_count": 847,
    "is_known_scammer": true,
    "carrier_name": "VoIP Provider",
    "line_type": "VoIP"
  },
  "recommendations": ["Do NOT click...", "..."],
  "analysis_timestamp": "2026-07-16T08:00:00Z",
  "model_version": "MindShield-NLP v2.3.1",
  "processing_time_ms": 512
}
```

---

## 13. Test Coverage Strategy

### Unit Tests (to be added in `test/features/analysis/`)

| Test | Target |
|---|---|
| `analysis_result_test.dart` | `AnalysisResult` copy, equality |
| `dummy_analysis_repository_test.dart` | Correct result per message ID, fallback for unknown |
| `analysis_provider_test.dart` | State transitions: loading → result / error; action states |

**Example Provider test:**
```dart
test('loadAnalysis sets isLoading then sets result', () async {
  final provider = AnalysisProvider();
  final msg = SmsMessage(id: 'msg_002', ...);
  
  final future = provider.loadAnalysis(msg);
  expect(provider.isLoading, isTrue);
  
  await future;
  expect(provider.isLoading, isFalse);
  expect(provider.analysisResult, isNotNull);
  expect(provider.analysisResult!.threatScore, equals(99));
});
```

### Widget Tests

| Test | Target |
|---|---|
| `threat_score_gauge_test.dart` | Renders correct score label; animation starts |
| `action_buttons_bar_test.dart` | Buttons disabled during action; SnackBar shown |
| `lime_highlight_card_test.dart` | Keywords highlighted; empty state shown correctly |

### Integration Test

- Navigate from Inbox → tap a scam message → verify Analysis screen renders gauge, keywords, and action buttons within 3 seconds.

---

## 14. File & Folder Reference

```
lib/features/analysis/
├── data/
│   └── dummy_analysis_repository.dart     ~250 lines  Repository with 8 full results
├── domain/
│   └── analysis_result.dart               ~220 lines  All entities & enums
└── presentation/
    ├── analysis_provider.dart             ~130 lines  ChangeNotifier + 4 actions
    ├── analysis_screen.dart               ~480 lines  Root screen + all sub-widgets
    └── widgets/
        ├── threat_score_gauge.dart        ~195 lines  CustomPainter gauge
        ├── confidence_bar.dart            ~100 lines  Animated linear bar
        ├── attack_type_card.dart          ~155 lines  Attack type + tactic chips
        ├── lime_highlight_card.dart       ~290 lines  RichText keyword highlight
        ├── ai_explanation_card.dart       ~110 lines  Faded explanation block
        ├── sender_info_card.dart          ~215 lines  Sender metadata
        ├── recommendations_card.dart      ~110 lines  Staggered list
        └── action_buttons_bar.dart        ~165 lines  4-button action bar

Total: ~2,225 lines of production Dart code
```

---

*Documentation generated for MindShield v1.0 — AI-powered SMS cybersecurity application.*
*Author: MindShield Development Team · July 2026*
