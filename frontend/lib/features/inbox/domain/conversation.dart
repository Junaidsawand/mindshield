import 'sms_message.dart';
import '../../spam/domain/spam_message.dart';

/// Represents a group of messages from the same sender.
class Conversation<T> {
  final String sender;
  final List<T> messages;

  const Conversation({
    required this.sender,
    required this.messages,
  });

  /// The latest message in the conversation.
  /// Expects the list [messages] to be sorted in chronological order (oldest first).
  T get latestMessage => messages.last;

  /// The total number of messages in this conversation.
  int get totalCount => messages.length;
}

/// Extension methods for Inbox Conversation threads.
extension SmsConversationX on Conversation<SmsMessage> {
  DateTime get latestTimestamp => latestMessage.timestamp;

  /// Determines the conversation status based on the highest risk message.
  /// Risk order: scam > suspicious > pending > safe.
  AiStatus get aiStatus {
    if (messages.any((m) => m.aiStatus == AiStatus.scam)) {
      return AiStatus.scam;
    }
    if (messages.any((m) => m.aiStatus == AiStatus.suspicious)) {
      return AiStatus.suspicious;
    }
    if (messages.any((m) => m.aiStatus == AiStatus.pending)) {
      return AiStatus.pending;
    }
    return AiStatus.safe;
  }

  /// Whether the conversation contains any unread messages.
  bool get isUnread => messages.any((m) => !m.isRead);
}

/// Extension methods for Spam Conversation threads.
extension SpamConversationX on Conversation<SpamMessage> {
  DateTime get latestTimestamp => latestMessage.timestamp;

  /// Determined by the highest risk level.
  SpamRiskLevel get riskLevel {
    if (messages.any((m) => m.riskLevel == SpamRiskLevel.critical)) {
      return SpamRiskLevel.critical;
    }
    if (messages.any((m) => m.riskLevel == SpamRiskLevel.high)) {
      return SpamRiskLevel.high;
    }
    return SpamRiskLevel.medium;
  }

  SpamStatus get status => latestMessage.status;
  double get aiConfidence => latestMessage.aiConfidence;
  AttackType get attackType => latestMessage.attackType;
  List<String> get detectedThreats => latestMessage.detectedThreats;
}

/// Helper method to normalize a sender's phone number or name for grouping.
String normalizeSender(String sender) {
  // Strip whitespace, parentheses, hyphens, etc.
  final cleaned = sender.replaceAll(RegExp(r'[\s\-()]+'), '');
  return cleaned.toLowerCase();
}

/// Groups a list of messages into conversation threads.
List<Conversation<T>> groupIntoConversations<T>({
  required List<T> messages,
  required String Function(T) getSender,
  required DateTime Function(T) getTimestamp,
}) {
  if (messages.isEmpty) return [];

  final groups = <String, List<T>>{};
  for (final msg in messages) {
    final sender = getSender(msg);
    final key = normalizeSender(sender);
    groups.putIfAbsent(key, () => []).add(msg);
  }

  final list = <Conversation<T>>[];
  for (final entry in groups.entries) {
    final threadMsgs = entry.value;
    
    // Sort chronologically (oldest first, so that latest message is at the end)
    threadMsgs.sort((a, b) => getTimestamp(a).compareTo(getTimestamp(b)));

    // Extract the original sender display name from the latest message in the thread
    final latestMsg = threadMsgs.last;
    final senderName = getSender(latestMsg);

    list.add(Conversation<T>(
      sender: senderName,
      messages: threadMsgs,
    ));
  }

  // Sort conversations by their latest message's timestamp descending (newest first)
  list.sort((a, b) => getTimestamp(b.latestMessage).compareTo(getTimestamp(a.latestMessage)));

  return list;
}
