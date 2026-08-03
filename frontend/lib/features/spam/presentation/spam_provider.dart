// lib/features/spam/presentation/spam_provider.dart

import 'package:flutter/foundation.dart';
import '../data/sqflite_spam_repository.dart';
import '../domain/spam_message.dart';
import '../../inbox/domain/conversation.dart';
import '../../../core/services/sms_background_service.dart';

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
class SpamProvider extends ChangeNotifier {
  SpamProvider() {
    loadMessages();
    SmsBackgroundService.instance.addListener(loadMessages);
  }

  @override
  void dispose() {
    SmsBackgroundService.instance.removeListener(loadMessages);
    super.dispose();
  }

  // ── Dependencies ──────────────────────────────────────────────────────────

  final _repo = SqfliteSpamRepository.instance;

  // ── Internal state ────────────────────────────────────────────────────────

  List<Conversation<SpamMessage>> _conversations = [];
  SpamFilter _activeFilter = SpamFilter.all;
  SpamSortOrder _sortOrder = SpamSortOrder.newestFirst;
  bool _isLoading = false;
  String? _errorMessage;

  // ── Public getters ────────────────────────────────────────────────────────

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  SpamFilter get activeFilter => _activeFilter;
  SpamSortOrder get sortOrder => _sortOrder;

  /// All conversations.
  List<Conversation<SpamMessage>> get allConversations => _conversations;

  /// All latest messages currently in memory (unfiltered).
  List<SpamMessage> get allMessages => _conversations.map((c) => c.latestMessage).toList();

  /// Total count of quarantined messages across all risk levels.
  int get totalCount => _conversations.fold(0, (sum, c) => sum + c.messages.length);

  /// Count of conversation threads per [SpamFilter] tab.
  int countFor(SpamFilter filter) {
    if (filter == SpamFilter.all) return _conversations.length;
    final level = _filterToLevel(filter);
    return _conversations.where((c) => c.riskLevel == level).length;
  }

  /// Count of critical-risk messages across all conversations.
  int get criticalCount =>
      _conversations.fold(0, (sum, c) => sum + c.messages.where((m) => m.riskLevel == SpamRiskLevel.critical).length);

  /// Conversations matching the active filter and sort order.
  List<Conversation<SpamMessage>> get filteredConversations {
    List<Conversation<SpamMessage>> result;
    if (_activeFilter == SpamFilter.all) {
      result = List.from(_conversations);
    } else {
      final level = _filterToLevel(_activeFilter);
      result = _conversations.where((c) => c.riskLevel == level).toList();
    }
    _applySortConversations(result);
    return result;
  }

  /// Conversations grouped by [SpamRiskLevel] in severity order.
  Map<SpamRiskLevel, List<Conversation<SpamMessage>>> get groupedConversations {
    final filtered = filteredConversations;
    final map = <SpamRiskLevel, List<Conversation<SpamMessage>>>{};
    for (final level in SpamRiskLevel.values) {
      final group = filtered.where((c) => c.riskLevel == level).toList();
      if (group.isNotEmpty) map[level] = group;
    }
    return map;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /// Fetches messages from the repository, groups them, and notifies listeners.
  Future<void> loadMessages() async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final fetched = await _repo.fetchSpamMessages();
      _conversations = groupIntoConversations<SpamMessage>(
        messages: fetched,
        getSender: (m) => m.sender,
        getTimestamp: (m) => m.timestamp,
      );
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
      _removeMessageFromThreads(id);
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.restoreToInbox error: $e');
    }
  }

  /// Restores all messages in a conversation thread to the inbox.
  Future<void> restoreConversationToInbox(String senderName) async {
    try {
      await _repo.restoreConversation(senderName);
      _conversations.removeWhere((c) => normalizeSender(c.sender) == normalizeSender(senderName));
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.restoreConversationToInbox error: $e');
    }
  }

  /// Permanently deletes all messages in a conversation thread.
  Future<void> deleteConversation(String senderName) async {
    try {
      await _repo.deleteConversation(senderName);
      _conversations.removeWhere((c) => normalizeSender(c.sender) == normalizeSender(senderName));
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.deleteConversation error: $e');
    }
  }

  /// Permanently deletes a message from the spam folder.
  Future<void> deleteMessage(String id) async {
    try {
      await _repo.deleteMessage(id);
      _removeMessageFromThreads(id);
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.deleteMessage error: $e');
    }
  }

  /// Blocks the sender and updates the message status in place.
  Future<void> blockSender(String id) async {
    try {
      final updated = await _repo.blockSender(id);
      _updateMessageInThreads(id, updated);
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.blockSender error: $e');
    }
  }

  /// Marks the message as reviewed.
  Future<void> markReviewed(String id) async {
    try {
      final updated = await _repo.markReviewed(id);
      _updateMessageInThreads(id, updated);
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('SpamProvider.markReviewed error: $e');
    }
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  void _removeMessageFromThreads(String id) {
    for (var i = 0; i < _conversations.length; i++) {
      final thread = _conversations[i].messages;
      final idx = thread.indexWhere((m) => m.id == id);
      if (idx != -1) {
        thread.removeAt(idx);
        if (thread.isEmpty) {
          _conversations.removeAt(i);
        }
        break;
      }
    }
  }

  void _updateMessageInThreads(String id, SpamMessage updated) {
    for (var i = 0; i < _conversations.length; i++) {
      final thread = _conversations[i].messages;
      final idx = thread.indexWhere((m) => m.id == id);
      if (idx != -1) {
        thread[idx] = updated;
        break;
      }
    }
  }

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

  void _applySortConversations(List<Conversation<SpamMessage>> list) {
    switch (_sortOrder) {
      case SpamSortOrder.newestFirst:
        list.sort((a, b) => b.latestTimestamp.compareTo(a.latestTimestamp));
      case SpamSortOrder.highestConfidence:
        list.sort((a, b) => b.aiConfidence.compareTo(a.aiConfidence));
      case SpamSortOrder.senderAZ:
        list.sort((a, b) => a.sender.compareTo(b.sender));
    }
  }
}
