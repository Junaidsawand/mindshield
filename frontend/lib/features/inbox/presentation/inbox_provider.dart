import 'package:flutter/foundation.dart';
import '../data/sqflite_inbox_repository.dart';
import '../../spam/data/sqflite_spam_repository.dart';
import '../domain/sms_message.dart';
import '../domain/conversation.dart';
import '../../../core/services/sms_background_service.dart';

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
class InboxProvider extends ChangeNotifier {
  InboxProvider() {
    loadMessages();
    SmsBackgroundService.instance.addListener(loadMessages);
  }

  @override
  void dispose() {
    SmsBackgroundService.instance.removeListener(loadMessages);
    super.dispose();
  }

  // ── Dependencies ──────────────────────────────────────────────────────────

  final _repo = SqfliteInboxRepository.instance;

  // ── Internal state ────────────────────────────────────────────────────────

  List<Conversation<SmsMessage>> _conversations = [];
  InboxFilter _activeFilter = InboxFilter.all;
  bool _isLoading = false;
  String? _errorMessage;

  // ── Public getters ────────────────────────────────────────────────────────

  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  InboxFilter get activeFilter => _activeFilter;

  /// All conversations.
  List<Conversation<SmsMessage>> get allConversations => _conversations;

  /// Latest message from each conversation, sorted newest-first.
  List<SmsMessage> get allMessages => _conversations.map((c) => c.latestMessage).toList();

  /// Conversations filtered by [_activeFilter], newest-first.
  List<Conversation<SmsMessage>> get filteredConversations {
    if (_activeFilter == InboxFilter.all) return _conversations;
    final target = _filterToStatus(_activeFilter);
    return _conversations.where((c) => c.aiStatus == target).toList();
  }

  /// Latest message from each conversation filtered by [_activeFilter], newest-first.
  List<SmsMessage> get filteredMessages {
    if (_activeFilter == InboxFilter.all) {
      return _conversations.map((c) => c.latestMessage).toList();
    }
    final target = _filterToStatus(_activeFilter);
    return _conversations
        .where((c) => c.aiStatus == target)
        .map((c) => c.latestMessage)
        .toList();
  }

  /// Count of unread messages for the badge on the bottom navigation.
  int get unreadCount => _conversations.fold(0, (sum, c) => sum + c.messages.where((m) => !m.isRead).length);

  /// Count of conversation threads per status – used to display counts on filter chips.
  int countFor(InboxFilter filter) {
    if (filter == InboxFilter.all) return _conversations.length;
    final target = _filterToStatus(filter);
    return _conversations.where((c) => c.aiStatus == target).length;
  }

  // ── Public API ────────────────────────────────────────────────────────────

  /// Fetches messages from the repository, groups them into conversations, and notifies listeners.
  Future<void> loadMessages() async {
    _setLoading(true);
    _errorMessage = null;
    try {
      final fetched = await _repo.fetchMessages();
      _conversations = groupIntoConversations<SmsMessage>(
        messages: fetched,
        getSender: (m) => m.sender,
        getTimestamp: (m) => m.timestamp,
      );
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
      for (var i = 0; i < _conversations.length; i++) {
        final thread = _conversations[i].messages;
        final idx = thread.indexWhere((m) => m.id == id);
        if (idx != -1) {
          thread[idx] = updated;
          notifyListeners();
          break;
        }
      }
    } catch (e) {
      debugPrint('InboxProvider.markAsRead error: $e');
    }
  }

  /// Marks all messages in a conversation as read.
  Future<void> markConversationAsRead(String senderName) async {
    try {
      final normalizedTarget = normalizeSender(senderName);
      final idx = _conversations.indexWhere((c) => normalizeSender(c.sender) == normalizedTarget);
      if (idx != -1) {
        final conversation = _conversations[idx];
        bool updatedAny = false;
        for (var i = 0; i < conversation.messages.length; i++) {
          final msg = conversation.messages[i];
          if (!msg.isRead) {
            final updatedMsg = await _repo.markAsRead(msg.id);
            conversation.messages[i] = updatedMsg;
            updatedAny = true;
          }
        }
        if (updatedAny) {
          notifyListeners();
          // Notify background service so other screens/badges can update
          SmsBackgroundService.instance.notifyListeners();
        }
      }
    } catch (e) {
      debugPrint('InboxProvider.markConversationAsRead error: $e');
    }
  }

  /// Moves all messages in a conversation thread to the spam folder.
  Future<void> moveConversationToSpam(String senderName) async {
    try {
      await SqfliteSpamRepository.instance.moveConversationToSpam(senderName);
      _conversations.removeWhere((c) => normalizeSender(c.sender) == normalizeSender(senderName));
      notifyListeners();
      SmsBackgroundService.instance.notifyListeners();
    } catch (e) {
      debugPrint('InboxProvider.moveConversationToSpam error: $e');
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
