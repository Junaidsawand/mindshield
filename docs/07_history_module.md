# MindShield: History Module Documentation

## 1. Introduction and Purpose
The History module serves as a critical component of the MindShield application, providing users with a comprehensive, chronological ledger of all SMS messages that have undergone AI threat analysis. The primary purpose of this module is to foster user trust and transparency by allowing users to retrospectively review the AI's verdicts (Safe, Suspicious, or Scam), inspect the confidence scores, and access the granular analysis rationale for each message. By offering robust filtering, searching, and sorting capabilities, the History module empowers users to efficiently retrieve specific historical threats, facilitating post-incident review and continuous learning about social engineering attack vectors.

## 2. System Architecture
The History module is designed adhering strictly to the Feature-First architectural paradigm, ensuring high cohesion and low coupling.
- **Domain Layer**: The module reuses the existing `SmsMessage` entity defined in the Inbox module. By treating an archived history item and an unread inbox item as fundamentally the same domain entity, we prevent model duplication and maintain a Single Source of Truth.
- **Data Layer**: Data access is abstracted behind the `DummyHistoryRepository`, which currently serves curated dummy data to simulate a populated local database. This abstracts the data source, allowing a seamless future transition to a local SQLite-backed repository (`SqfliteHistoryRepository`).
- **State Management**: The presentation logic is decoupled from the UI using the Provider pattern (`ChangeNotifier`). The `HistoryProvider` encapsulates all business logic related to data fetching, in-memory filtering, keyword searching, and temporal sorting.
- **Presentation Layer**: Built entirely using Flutter's Material 3 design system, the UI comprises a `HistoryScreen` for layout and navigation, and a reusable `HistoryCard` for rendering individual threat summaries.

## 3. Directory and Folder Structure
The History module is encapsulated within the `lib/features/history/` directory:

```text
lib/features/history/
├── data/
│   └── dummy_history_repository.dart    # Simulates historical AI analysis data
├── presentation/
│   ├── history_provider.dart            # Manages state, filtering, searching, and sorting
│   ├── history_screen.dart              # Main Material 3 UI screen
│   └── widgets/
│       └── history_card.dart            # Summary card for an analyzed SMS
```

## 4. Data Flow
1. **Initialization**: Upon navigating to the `HistoryScreen`, a localized `HistoryProvider` is instantiated via `ChangeNotifierProvider`.
2. **Data Fetching**: The provider automatically invokes `loadHistory()`, communicating asynchronously with the `DummyHistoryRepository` to retrieve a list of `SmsMessage` objects.
3. **State Mutation**: The repository returns the data, and the provider updates its internal `_allMessages` state, notifying listeners to rebuild the UI from a loading state to a populated list.
4. **User Interaction (Filtering/Sorting)**: When a user interacts with the UI (e.g., typing in the search bar or toggling a filter chip), the provider's corresponding setters (`setSearchQuery`, `setFilter`) are called.
5. **Dynamic Computation**: The `filteredMessages` getter dynamically computes the visible subset of messages based on the current state criteria and returns the sorted, filtered list to the UI.
6. **Navigation**: Tapping a `HistoryCard` invokes `GoRouter` (`context.push`), passing the tapped `SmsMessage` object to the `AnalysisScreen`, which then lazily loads the complete LIME-based `AnalysisResult`.

## 5. Implementation Details
- **Material 3 UI**: The `HistoryScreen` implements a persistent `AppBar` that houses a Material 3 `SearchBar` and a horizontally scrollable row of `FilterChip` widgets. 
- **Dynamic Filtering Engine**: The `HistoryProvider` utilizes a combined functional approach in its `filteredMessages` getter. It first applies an `AiStatus` filter (if selected), then performs a case-insensitive sub-string match against both the sender's name and the message body, and finally applies a temporal `sort()` operation.
- **Lazy Detailed Loading**: The `HistoryCard` only displays summary metadata (sender, date, verdict, confidence, primary threat). It does not hold the heavy `AnalysisResult` object, ensuring the `ListView.builder` remains performant even with thousands of history records.

## 6. Design Decisions
- **Reuse of `SmsMessage` Domain Entity**: Instead of creating a unique `HistoryItem` model, we reused `SmsMessage`. This decision was made because the attributes required for the history list view are identical to those needed in the inbox. It significantly reduces boilerplate mapping code and ensures architectural consistency.
- **In-Memory Filtering vs Database Queries**: Currently, filtering and sorting are handled in-memory by the `HistoryProvider` on the `_allMessages` list. This decision prioritizes immediate UI responsiveness during the prototyping phase. In a production environment with millions of rows, this logic will be pushed down to the SQLite repository via SQL `WHERE` and `ORDER BY` clauses to ensure scalability.
- **Decoupled Data Repository**: We created `DummyHistoryRepository` instead of reusing `DummyInboxRepository` to fetch data. While the data model is identical, the semantic origin of the data differs (archived vs unread). Decoupling them allows independent future implementation (e.g., querying a `history_table` vs an `inbox_table`).

## 7. Development Challenges and Solutions
- **Challenge: UI Jitter During Search Filtering**
  - *Context*: Rapid typing in the search bar could trigger continuous rebuilds of the ListView, causing UI stutter.
  - *Solution*: Leveraged the efficient `ListView.builder` combined with the `ChangeNotifier` architecture. By keeping the `filteredMessages` computation isolated in a getter and only notifying listeners on explicit state changes, Flutter's render pipeline efficiently handles the diffing, resulting in smooth 60fps performance.
- **Challenge: Routing Payload Size**
  - *Context*: Passing large data structures between screens using routing arguments can sometimes lead to serialization issues or memory bloat.
  - *Solution*: By passing the lightweight `SmsMessage` domain model via `GoRouter.extra` to the `AnalysisScreen`, rather than the heavy `AnalysisResult`, we minimized the payload footprint. The `AnalysisScreen` remains responsible for independently loading its heavy data requirements.

## 8. Academic Thesis Content

### 8.1. Abstract integration (Draft Segment)
*The system implements a persistent History module that serves as an immutable ledger of all threat assessments conducted by the on-device NLP model. By leveraging a reactive state management paradigm, the module provides users with instantaneous, multidimensional filtering of historical SMS data. This component is instrumental in bridging the gap between automated AI classification and user comprehension, acting as an educational interface where users can scrutinize past attacks, review LIME-generated explanations, and cultivate a deeper intuition for identifying social engineering tactics.*

### 8.2. Methodology (Draft Segment)
*The architecture of the historical analysis ledger employs a decoupled Provider pattern to separate the graphical user interface from the underlying data manipulation logic. To optimize rendering performance within the mobile environment, the system adopts a Lazy Loading strategy for detailed threat metadata. The primary ledger interface constructs a lightweight representation of historical messages—encapsulating only the temporal data, sender heuristics, and the aggregate threat confidence score. High-dimensionality data, such as token-level feature importance weights and psychological tactic matrices, are deferred from memory allocation until explicit user navigation is initiated.*

## 9. Viva / Interview Questions and Answers

**Q: Explain the architectural pattern you used for the History module and why you chose it.**
**A:** We utilized a Feature-First architecture paired with the Provider pattern (`ChangeNotifier`). This approach was chosen to enforce strict separation of concerns. The `HistoryScreen` acts purely as a declarative UI layer, the `HistoryProvider` encapsulates the business rules for filtering and sorting, and the `DummyHistoryRepository` abstracts the data access. This makes the module highly testable and allows us to easily swap the dummy data source for a real SQLite database without altering the presentation logic.

**Q: You mentioned reusing the `SmsMessage` model. What are the potential drawbacks of this approach compared to creating a dedicated `HistoryItem` model?**
**A:** The primary risk is the violation of the Interface Segregation Principle if the two contexts eventually diverge significantly. If the History view suddenly requires unique fields that the Inbox view does not (e.g., 'user_dispute_status' or 'archived_date'), stuffing those into `SmsMessage` could bloat the class with nullable fields. However, within the current scope, an SMS is fundamentally the same entity regardless of where it is viewed, making reuse the most pragmatic and efficient choice to avoid unnecessary mapping overhead.

**Q: How does the History screen maintain performance if the user has 10,000 analyzed messages?**
**A:** Performance is maintained through two primary mechanisms:
1. **UI Layer:** We utilize `ListView.builder`, which lazily builds child widgets only when they scroll into the viewport, keeping the widget tree footprint small regardless of list size.
2. **Data Layer (Future):** While currently filtering in-memory for prototyping, the architecture is designed so that the `HistoryProvider` will eventually pass offset and limit parameters to the repository, utilizing SQLite `LIMIT` and `OFFSET` commands for true data-layer pagination.

**Q: How does the History module interact with the Analysis module?**
**A:** The interaction is loosely coupled via the application router (`GoRouter`). The History module does not depend on the `AnalysisProvider` or `AnalysisResult`. When a user taps a history card, the History module simply pushes the `/analysis` route and passes the tapped `SmsMessage` object as a payload argument. The Analysis module is then independently responsible for using that message to fetch and render the detailed AI explanation.
