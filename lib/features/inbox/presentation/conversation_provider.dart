import 'package:flutter/foundation.dart';
import '../data/sqflite_inbox_repository.dart';
import '../../spam/data/sqflite_spam_repository.dart';
import '../../spam/domain/spam_message.dart';
import '../domain/sms_message.dart';
import '../domain/conversation.dart';
import '../../../core/services/sms_background_service.dart';

/// Manages state for the conversation thread screen.
class ConversationProvider extends ChangeNotifier {
  final String sender;
  final bool isSpam;

  ConversationProvider({required this.sender, required this.isSpam}) {
    loadMessages();
    SmsBackgroundService.instance.addListener(loadMessages);
  }

  @override
  void dispose() {
    SmsBackgroundService.instance.removeListener(loadMessages);
    super.dispose();
  }

  List<SmsMessage> _messages = [];
  bool _isLoading = false;
  String? _errorMessage;
  bool _isBlocked = false;

  List<SmsMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isBlocked => _isBlocked;

  /// Fetches messages matching this conversation's sender, ordered chronologically.
  Future<void> loadMessages() async {
    _isLoading = true;
    _errorMessage = null;
    // We notify listeners here to trigger the initial loading shimmer.
    // However, when called from SmsBackgroundService listener we also refresh state.
    notifyListeners();

    try {
      final normalizedTarget = normalizeSender(sender);
      final spamMsgs = await SqfliteSpamRepository.instance.fetchSpamMessages();
      _isBlocked = spamMsgs.any((m) => normalizeSender(m.sender) == normalizedTarget && m.status == SpamStatus.blocked);

      if (isSpam) {
        final filtered = spamMsgs.where((m) => normalizeSender(m.sender) == normalizedTarget).toList();
        
        _messages = filtered.map((spam) => SmsMessage(
          id: spam.id,
          sender: spam.sender,
          body: spam.body,
          timestamp: spam.timestamp,
          aiStatus: _bridgeRiskToStatus(spam.riskLevel),
          isRead: true,
          confidenceScore: spam.aiConfidence,
          detectedThreats: spam.detectedThreats,
        )).toList();
      } else {
        final inboxMsgs = await SqfliteInboxRepository.instance.fetchMessages();
        _messages = inboxMsgs.where((m) => normalizeSender(m.sender) == normalizedTarget).toList();
      }

      // Sort chronologically: oldest first
      _messages.sort((a, b) => a.timestamp.compareTo(b.timestamp));
    } catch (e, st) {
      _errorMessage = 'Failed to load conversation: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  AiStatus _bridgeRiskToStatus(SpamRiskLevel level) {
    switch (level) {
      case SpamRiskLevel.critical:
      case SpamRiskLevel.high:
        return AiStatus.scam;
      case SpamRiskLevel.medium:
        return AiStatus.suspicious;
    }
  }
}
