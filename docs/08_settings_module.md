# Settings Module Documentation

## 1. Introduction
The Settings module in MindShield provides a centralized interface for users to configure application behavior, security preferences, and aesthetic settings. Built with a Feature-First architecture, it maintains strict separation between presentation and state management, utilizing `Provider` and `SharedPreferences` for efficient, reactive updates across the application.

## 2. Architecture & Design
The module adheres to the existing Feature-First structure:
- **Presentation Layer (`settings_screen.dart`)**: A responsive, Material 3 compliant UI that displays configuration options categorized into Protection, Preferences, Privacy & Data, and About sections.
- **State Management (`settings_provider.dart`)**: A `ChangeNotifier` that interfaces with `SharedPreferences` to load, cache, and persist user preferences. It exposes an API that the UI consumes to trigger state changes dynamically.

## 3. Key Components
### 3.1 SettingsProvider
The `SettingsProvider` acts as the single source of truth for app settings.
- **Persistent Storage Abstraction**: Uses `SharedPreferences` directly but abstracts it from the UI. This ensures the provider interface remains stable even if the persistence layer changes in the future.
- **Reactive State**: Changes to settings like `ThemeMode` invoke `notifyListeners()`, causing the root `MaterialApp` to rebuild with the new theme instantly.

### 3.2 SettingsScreen
A `StatelessWidget` that uses a `Consumer<SettingsProvider>` to read and manipulate settings.
- **Material 3 UI**: Uses `Card` components with low elevation and `surfaceContainerHighest` colors for grouping related settings.
- **Interactive Elements**: Features `SwitchListTile`, `DropdownButton`, and `SegmentedButton` to handle boolean toggles, enums, and lists respectively.

## 4. Integration
### 4.1 Global Theming
The `main.dart` initialization process has been updated to initialize `SharedPreferences` asynchronously before `runApp()`. The `SettingsProvider` is registered at the top of the widget tree in a `MultiProvider`. 
The `MaterialApp` widget is then wrapped in a `Builder` (or its equivalent component extraction) that watches `SettingsProvider`, allowing `themeMode` changes to propagate to the entire application instantly.

### 4.2 Bottom Navigation
The module integrates seamlessly with the existing `GoRouter` Stateful Shell navigation. It occupies its own isolated navigation branch, ensuring its state is preserved when users switch tabs.

## 5. Technical Challenges & Considerations
- **Synchronous vs Asynchronous Loading**: `SharedPreferences` initialization is inherently asynchronous. To prevent UI flickers, the instance is awaited in `main()` before the widget tree starts building, ensuring synchronous access to cached values throughout the app's lifecycle.
- **Dummy Data to Persistence**: By building the `SharedPreferences` abstraction immediately, the app requires zero structural changes to transition from default fallback values to fully persisted configurations.

## 6. Future Enhancements
- **Data Export & Privacy Rules**: Implementing the actual logic for GDPR-compliant data export and managing blocked senders lists via SQLite integration.
- **Cloud Sync**: Expanding the `SettingsProvider` to synchronize preferences across multiple devices using Firebase or a custom backend.
