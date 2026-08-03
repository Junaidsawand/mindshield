/// Represents the AI-assigned risk level for an SMS message.
enum AiStatus {
  /// Message is recently received and awaiting analysis.
  pending,

  /// No threat detected.
  safe,

  /// Potentially deceptive content – user should review carefully.
  suspicious,

  /// Confirmed scam / phishing / spam pattern.
  scam,
}

/// Extension providing display helpers for [AiStatus].
extension AiStatusX on AiStatus {
  /// Short label shown in the badge chip.
  String get label {
    switch (this) {
      case AiStatus.pending:
        return 'Analyzing...';
      case AiStatus.safe:
        return 'Safe';
      case AiStatus.suspicious:
        return 'Suspicious';
      case AiStatus.scam:
        return 'Scam';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SmsMessage entity
// ─────────────────────────────────────────────────────────────────────────────

/// Domain entity representing a single SMS message with its AI analysis result.
///
/// This is a plain Dart class (no framework dependencies). The data layer maps
/// raw SMS data into this entity; the presentation layer renders it.
class SmsMessage {
  const SmsMessage({
    required this.id,
    required this.sender,
    required this.body,
    required this.timestamp,
    required this.aiStatus,
    this.isRead = false,
    this.confidenceScore,
    this.detectedThreats = const [],
  });

  /// Unique identifier (thread ID from Android / sequential dummy id).
  final String id;

  /// Display name or phone number of the sender.
  final String sender;

  /// Full message body.
  final String body;

  /// When the message was received.
  final DateTime timestamp;

  /// AI-assigned classification.
  final AiStatus aiStatus;

  /// Whether the user has opened / read the message.
  final bool isRead;

  /// Optional: 0.0–1.0 confidence from the AI model.
  final double? confidenceScore;

  /// Optional: list of detected threat categories (e.g. ['phishing', 'url']).
  final List<String> detectedThreats;

  /// Returns a copy of this entity with the given fields overridden.
  SmsMessage copyWith({
    String? id,
    String? sender,
    String? body,
    DateTime? timestamp,
    AiStatus? aiStatus,
    bool? isRead,
    double? confidenceScore,
    List<String>? detectedThreats,
  }) {
    return SmsMessage(
      id: id ?? this.id,
      sender: sender ?? this.sender,
      body: body ?? this.body,
      timestamp: timestamp ?? this.timestamp,
      aiStatus: aiStatus ?? this.aiStatus,
      isRead: isRead ?? this.isRead,
      confidenceScore: confidenceScore ?? this.confidenceScore,
      detectedThreats: detectedThreats ?? this.detectedThreats,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SmsMessage && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;
}
