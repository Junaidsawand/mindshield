import 'package:flutter/foundation.dart';
import '../data/dummy_inbox_repository.dart';
import '../domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// InboxFilter enum
// ─────────────────────────────────────────────────────────────────────────────

/// Filter tabs available on the Inbox screen.
enum InboxFilter { all, safe, suspicious, scam }

/// Extension providing display helpers for [InboxFilter].
extension InboxFilterX on InboxFilter {
  String get label {
    switch (this) {
      case InboxFilter.all:
        return 'All';
      case InboxFilter.safe:
        return 'Safe';
      case InboxFilter.suspicious:
        return 'Suspicious';
      case InboxFilter.scam:
        return 'Scam';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// InboxProvider
// ─────────────────────────────────────────────────────────────────────────────

/// Manages the state of the Inbox feature.
///
/// Responsibilities
/// ─────────────────
/// * Loads messages from [DummyInboxRepository] (later: SqfliteInboxRepository).
/// * Holds the active [InboxFilter] and exposes [filteredMessages].
/// * Tracks [isLoading] and [errorMessage] for UI error/loading states.
/// * Exposes [markAsRead] to update the read flag on a message.
///
/// Register in [main.dart] via:
/// ```dart
/// ChangeNotifierProvider<InboxProvider>(create: (_) => InboxProvider()),
/// ```
class InboxProvider extends ChangeNotifier {
  InboxProvider() {
    loadMessages();
  }

  // ── Dependencies ──────────────────────────────────────────────────────────

  final _repo = DummyInboxRepository.instance;

  // ── Internal state ────────────────────────────────────────────────────────

  List<SmsMessage> _messages = [];
  InboxFilter _activeFilter = InboxFilter.all;
  bool _isLoading = false;
  String? _errorMessage;

  // ── Public getters ────────────────────────────────────────────────────────

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  InboxFilter get activeFilter => _activeFilter;

  /// All messages, sorted newest-first.
  List<SmsMessage> get allMessages => _messages;

  /// Messages filtered by [_activeFilter], newest-first.
  List<SmsMessage> get filteredMessages {
    if (_activeFilter == InboxFilter.all) return _messages;
    final target = _filterToStatus(_activeFilter);
    return _messages.where((m) => m.aiStatus == target).toList();
  }

  /// Count of unread messages for the badge on the bottom navigation.
  int get unreadCount => _messages.where((m) => !m.isRead).length;

  /// Count per status – used to display counts on filter chips.
  int countFor(InboxFilter filter) {
    if (filter == InboxFilter.all) return _messages.length;
    final target = _filterToStatus(filter);
    return _messages.where((m) => m.aiStatus == target).length;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /// Fetches messages from the repository and notifies listeners.
  Future<void> loadMessages() async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final fetched = await _repo.fetchMessages();
      // Sort: newest first.
      fetched.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      _messages = fetched;
    } catch (e, st) {
      _errorMessage = 'Failed to load messages: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _setLoading(false);
    }
  }

  /// Changes the active filter tab and triggers a rebuild.
  void setFilter(InboxFilter filter) {
    if (_activeFilter == filter) return;
    _activeFilter = filter;
    notifyListeners();
  }

  /// Marks the given message as read in the repository and in-memory list.
  Future<void> markAsRead(String id) async {
    try {
      final updated = await _repo.markAsRead(id);
      final idx = _messages.indexWhere((m) => m.id == id);
      if (idx != -1) {
        _messages[idx] = updated;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('InboxProvider.markAsRead error: $e');
    }
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  AiStatus _filterToStatus(InboxFilter filter) {
    switch (filter) {
      case InboxFilter.safe:
        return AiStatus.safe;
      case InboxFilter.suspicious:
        return AiStatus.suspicious;
      case InboxFilter.scam:
        return AiStatus.scam;
      default:
        return AiStatus.safe;
    }
  }
}
