# MindShield Spam Folder Module
**Technical Documentation & Architecture Report**

## 1. Introduction
The MindShield Spam Folder Module provides a secure quarantine environment for SMS messages flagged as malicious or suspicious by the AI engine. This module isolates potential threats from the primary Inbox, categorizing them by severity to help users safely review, restore, block, or permanently delete deceptive communications. This document outlines the module's architecture, design patterns, and UI/UX decisions.

## 2. Architecture & Folder Structure
MindShield employs a Feature-First Clean Architecture. The Spam Folder is entirely self-contained within `lib/features/spam/`, decoupled from the core Inbox, but capable of mapping its data to the shared `AnalysisScreen` when detailed AI threat breakdowns are requested.

```text
lib/features/spam/
├── domain/
│   └── spam_message.dart         # Core domain entity and enums (Risk, Attack Type)
├── data/
│   └── dummy_spam_repository.dart # Data source (currently populated with thesis seed data)
└── presentation/
    ├── spam_screen.dart          # Main UI entry point (Slivers, RefreshIndicator)
    ├── spam_provider.dart        # State management (Provider / ChangeNotifier)
    └── widgets/                  # Reusable local UI components
        ├── spam_filter_bar.dart
        ├── spam_section_header.dart
        ├── spam_message_tile.dart
        ├── spam_action_sheet.dart
        ├── risk_level_badge.dart
        └── confidence_indicator.dart
```

## 3. Domain Layer
The `SpamMessage` domain entity is a plain Dart class, completely agnostic to the UI or database layers. It introduces specific metadata essential for a threat quarantine system:
*   `riskLevel` (`critical`, `high`, `medium`): Used for UI grouping and color-coding.
*   `attackType`: Categorizes the threat (e.g., `phishing`, `smishing`, `cryptoScam`).
*   `status` (`quarantined`, `reviewed`, `blocked`): Tracks the lifecycle of the message.
*   `aiConfidence`: A double (0.0 to 1.0) representing the model's certainty.

## 4. State Management
We use the `provider` package. The `SpamProvider` class manages all state for the Spam Folder.
*   **Encapsulation**: `SpamProvider` holds the raw list of messages, the current active filter (`SpamFilter`), and the current sort order (`SpamSortOrder`).
*   **Computed Getters**: It exposes `groupedMessages` (grouping messages by `SpamRiskLevel` in descending order of severity) and `filteredMessages`.
*   **Asynchronous Actions**: Provides methods like `restoreToInbox`, `deleteMessage`, and `blockSender` that update the local repository and immediately notify listeners to rebuild the UI.

## 5. UI / Presentation Layer
The UI strictly adheres to Google's Material 3 guidelines, emphasizing a clean, responsive, and accessible experience.

### 5.1 Main Screen (`spam_screen.dart`)
*   **CustomScrollView & Slivers**: We use slivers for a highly fluid scrolling experience.
*   **SliverAppBar.large**: Collapses on scroll. It dynamically displays the total quarantined count and the count of critical threats.
*   **Sticky Filters**: A `SliverPersistentHeader` is used for the `SpamFilterBar` so that the filter chips remain pinned to the top of the screen even when the user scrolls down the list.

### 5.2 Animations & Feedback
*   **Staggered List Animation**: Tiles fade and slide up sequentially (`_AnimatedTile`) when the screen loads, providing a premium, polished feel.
*   **Micro-interactions**: Filter chips animate their color and border transitions when selected.
*   **Snackbars**: Immediate visual confirmation is given when an action (Restore, Block, Delete) is performed.

### 5.3 Contextual Actions
*   **SpamMessageTile**: Displays rich information including a sender avatar with a risk-colored ring, the AI confidence bar, and multiple badges (`RiskLevelBadge`, `AttackTypeBadge`). It includes an overflow menu (`⋮`).
*   **SpamActionSheet**: Long-pressing a tile triggers a customizable bottom sheet offering the same actions, improving reachability on large devices. A destructive action (Delete) requires a secondary dialog confirmation to prevent accidental data loss.

## 6. Security & UX Considerations
*   **De-risked Previews**: The Spam Folder intentionally does not auto-render links or images, preventing accidental execution of malicious payloads.
*   **Color Psychology**: Critical threats use deep reds (`#C62828`), high threats use oranges, and medium threats use amber. This creates an immediate, subconscious understanding of the threat level.
*   **Integration with Analysis Engine**: The Spam Folder seamlessly bridges a `SpamMessage` back to the shared `SmsMessage` format when the user navigates to the `AnalysisScreen`, allowing code reuse for the deep-dive AI explanation view.

## 7. Future Integration Roadmap
*   **SQFlite Integration**: The `DummySpamRepository` will be swapped for a real SQLite database repository once the local database architecture is finalized.
*   **Search**: A search delegate will be added to the AppBar to filter the quarantined messages by sender or keyword.

---
*Generated for the MindShield Project Documentation.*
