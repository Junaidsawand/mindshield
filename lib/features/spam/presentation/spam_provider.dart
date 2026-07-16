// lib/features/spam/presentation/spam_provider.dart

import 'package:flutter/foundation.dart';
import '../data/dummy_spam_repository.dart';
import '../domain/spam_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SpamFilter enum
// ─────────────────────────────────────────────────────────────────────────────

/// Filter tabs available on the Spam Folder screen.
enum SpamFilter { all, critical, high, medium }

/// Extension providing display helpers for [SpamFilter].
extension SpamFilterX on SpamFilter {
  String get label {
    switch (this) {
      case SpamFilter.all:
        return 'All';
      case SpamFilter.critical:
        return 'Critical';
      case SpamFilter.high:
        return 'High';
      case SpamFilter.medium:
        return 'Medium';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SpamSortOrder enum
// ─────────────────────────────────────────────────────────────────────────────

/// Available sort orders for the spam message list.
enum SpamSortOrder {
  /// Most recently quarantined first.
  newestFirst,

  /// Highest AI confidence first.
  highestConfidence,

  /// Alphabetical by sender.
  senderAZ,
}

/// Extension providing display helpers for [SpamSortOrder].
extension SpamSortOrderX on SpamSortOrder {
  String get label {
    switch (this) {
      case SpamSortOrder.newestFirst:
        return 'Newest first';
      case SpamSortOrder.highestConfidence:
        return 'Highest confidence';
      case SpamSortOrder.senderAZ:
        return 'Sender A–Z';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SpamProvider
// ─────────────────────────────────────────────────────────────────────────────

/// Manages state for the Spam Folder feature.
///
/// Responsibilities
/// ─────────────────
/// * Loads quarantined messages from [DummySpamRepository].
/// * Holds the active [SpamFilter] and [SpamSortOrder].
/// * Exposes [filteredMessages] and grouped views for the UI.
/// * Provides action methods: [restoreToInbox], [deleteMessage],
///   [blockSender], [markReviewed].
/// * Tracks [isLoading] and [errorMessage] for UI state feedback.
///
/// Scoped to [SpamScreen] via a local [ChangeNotifierProvider].
class SpamProvider extends ChangeNotifier {
  SpamProvider() {
    loadMessages();
  }

  // ── Dependencies ──────────────────────────────────────────────────────────

  final _repo = DummySpamRepository.instance;

  // ── Internal state ────────────────────────────────────────────────────────

  List<SpamMessage> _messages = [];
  SpamFilter _activeFilter = SpamFilter.all;
  SpamSortOrder _sortOrder = SpamSortOrder.newestFirst;
  bool _isLoading = false;
  String? _errorMessage;

  // ── Public getters ────────────────────────────────────────────────────────

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  SpamFilter get activeFilter => _activeFilter;
  SpamSortOrder get sortOrder => _sortOrder;

  /// All messages currently in memory (unfiltered).
  List<SpamMessage> get allMessages => _messages;

  /// Total count of quarantined messages across all risk levels.
  int get totalCount => _messages.length;

  /// Count of messages per [SpamFilter] tab.
  int countFor(SpamFilter filter) {
    if (filter == SpamFilter.all) return _messages.length;
    final level = _filterToLevel(filter);
    return _messages.where((m) => m.riskLevel == level).length;
  }

  /// Count of critical-risk messages – used by the app bar badge.
  int get criticalCount =>
      _messages.where((m) => m.riskLevel == SpamRiskLevel.critical).length;

  /// Messages matching the active filter and sort order.
  List<SpamMessage> get filteredMessages {
    List<SpamMessage> result;
    if (_activeFilter == SpamFilter.all) {
      result = List.of(_messages);
    } else {
      final level = _filterToLevel(_activeFilter);
      result = _messages.where((m) => m.riskLevel == level).toList();
    }
    _applySort(result);
    return result;
  }

  /// Messages grouped by [SpamRiskLevel] in severity order:
  /// Critical → High → Medium.
  /// Only includes groups that contain at least one message.
  Map<SpamRiskLevel, List<SpamMessage>> get groupedMessages {
    final filtered = filteredMessages;
    final map = <SpamRiskLevel, List<SpamMessage>>{};
    for (final level in SpamRiskLevel.values) {
      final group = filtered.where((m) => m.riskLevel == level).toList();
      if (group.isNotEmpty) map[level] = group;
    }
    return map;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /// Fetches messages from the repository and notifies listeners.
  Future<void> loadMessages() async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final fetched = await _repo.fetchSpamMessages();
      _messages = fetched.toList();
    } catch (e, st) {
      _errorMessage = 'Failed to load spam folder: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _setLoading(false);
    }
  }

  /// Changes the active filter tab.
  void setFilter(SpamFilter filter) {
    if (_activeFilter == filter) return;
    _activeFilter = filter;
    notifyListeners();
  }

  /// Changes the sort order.
  void setSortOrder(SpamSortOrder order) {
    if (_sortOrder == order) return;
    _sortOrder = order;
    notifyListeners();
  }

  /// Restores a message to the user's inbox (removes from spam).
  Future<void> restoreToInbox(String id) async {
    try {
      await _repo.restoreToInbox(id);
      _messages.removeWhere((m) => m.id == id);
      notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.restoreToInbox error: $e');
    }
  }

  /// Permanently deletes a message from the spam folder.
  Future<void> deleteMessage(String id) async {
    try {
      await _repo.deleteMessage(id);
      _messages.removeWhere((m) => m.id == id);
      notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.deleteMessage error: $e');
    }
  }

  /// Blocks the sender and updates the message status in place.
  Future<void> blockSender(String id) async {
    try {
      final updated = await _repo.blockSender(id);
      final idx = _messages.indexWhere((m) => m.id == id);
      if (idx != -1) {
        _messages[idx] = updated;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('SpamProvider.blockSender error: $e');
    }
  }

  /// Marks the message as reviewed.
  Future<void> markReviewed(String id) async {
    try {
      final updated = await _repo.markReviewed(id);
      final idx = _messages.indexWhere((m) => m.id == id);
      if (idx != -1) {
        _messages[idx] = updated;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('SpamProvider.markReviewed error: $e');
    }
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  SpamRiskLevel _filterToLevel(SpamFilter filter) {
    switch (filter) {
      case SpamFilter.critical:
        return SpamRiskLevel.critical;
      case SpamFilter.high:
        return SpamRiskLevel.high;
      case SpamFilter.medium:
        return SpamRiskLevel.medium;
      case SpamFilter.all:
        return SpamRiskLevel.critical; // fallback, never reached
    }
  }

  void _applySort(List<SpamMessage> list) {
    switch (_sortOrder) {
      case SpamSortOrder.newestFirst:
        list.sort((a, b) => b.timestamp.compareTo(a.timestamp));
      case SpamSortOrder.highestConfidence:
        list.sort((a, b) => b.aiConfidence.compareTo(a.aiConfidence));
      case SpamSortOrder.senderAZ:
        list.sort((a, b) => a.sender.compareTo(b.sender));
    }
  }
}
