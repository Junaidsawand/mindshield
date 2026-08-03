// lib/features/spam/domain/spam_message.dart

// ─────────────────────────────────────────────────────────────────────────────
// SpamRiskLevel enum
// ─────────────────────────────────────────────────────────────────────────────

/// Severity tier assigned by the AI model, used to group and colour-code
/// messages inside the Spam Folder.
enum SpamRiskLevel {
  /// AI confidence 90–100 % – confirmed scam / phishing / malware link.
  critical,

  /// AI confidence 70–89 % – strong scam signals present.
  high,

  /// AI confidence 50–69 % – suspicious but not conclusively malicious.
  medium,
}

/// Extension providing display helpers for [SpamRiskLevel].
extension SpamRiskLevelX on SpamRiskLevel {
  /// Human-readable label shown in section headers and chips.
  String get label {
    switch (this) {
      case SpamRiskLevel.critical:
        return 'Critical';
      case SpamRiskLevel.high:
        return 'High Risk';
      case SpamRiskLevel.medium:
        return 'Medium Risk';
    }
  }

  /// Short subtitle shown below section header labels.
  String get subtitle {
    switch (this) {
      case SpamRiskLevel.critical:
        return 'Confirmed scam – do not interact';
      case SpamRiskLevel.high:
        return 'Strong scam indicators detected';
      case SpamRiskLevel.medium:
        return 'Suspicious – review carefully';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SpamStatus enum
// ─────────────────────────────────────────────────────────────────────────────

/// Lifecycle state of a quarantined message within the Spam Folder.
enum SpamStatus {
  /// Message is actively quarantined awaiting user action.
  quarantined,

  /// User has reviewed and confirmed this is spam.
  reviewed,

  /// User has blocked the sender.
  blocked,
}

/// Extension providing display helpers for [SpamStatus].
extension SpamStatusX on SpamStatus {
  /// Short label for the status chip.
  String get label {
    switch (this) {
      case SpamStatus.quarantined:
        return 'Quarantined';
      case SpamStatus.reviewed:
        return 'Reviewed';
      case SpamStatus.blocked:
        return 'Blocked';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// AttackType enum
// ─────────────────────────────────────────────────────────────────────────────

/// Broad category of attack technique identified by the AI model.
enum AttackType {
  phishing,
  smishing,
  vishing,
  prizeScam,
  investmentFraud,
  deliveryScam,
  govImpersonation,
  cryptoScam,
  malwareLink,
  socialEngineering,
}

/// Extension providing display helpers for [AttackType].
extension AttackTypeX on AttackType {
  /// Human-readable name used in the message card.
  String get label {
    switch (this) {
      case AttackType.phishing:
        return 'Phishing';
      case AttackType.smishing:
        return 'Smishing';
      case AttackType.vishing:
        return 'Vishing';
      case AttackType.prizeScam:
        return 'Prize Scam';
      case AttackType.investmentFraud:
        return 'Investment Fraud';
      case AttackType.deliveryScam:
        return 'Delivery Scam';
      case AttackType.govImpersonation:
        return 'Gov. Impersonation';
      case AttackType.cryptoScam:
        return 'Crypto Scam';
      case AttackType.malwareLink:
        return 'Malware Link';
      case AttackType.socialEngineering:
        return 'Social Engineering';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SpamMessage entity
// ─────────────────────────────────────────────────────────────────────────────

/// Domain entity representing a single SMS message that has been quarantined
/// in the Spam Folder after AI classification.
///
/// This is a plain Dart class with no framework dependencies.  The data layer
/// maps raw data into this entity; the presentation layer renders it.
class SpamMessage {
  const SpamMessage({
    required this.id,
    required this.sender,
    required this.body,
    required this.timestamp,
    required this.riskLevel,
    required this.attackType,
    required this.aiConfidence,
    required this.status,
    this.detectedThreats = const [],
    this.quarantinedAt,
  });

  /// Unique identifier (mirrors the inbox message ID).
  final String id;

  /// Sender display name or phone number.
  final String sender;

  /// Full SMS body text.
  final String body;

  /// When the original SMS was received.
  final DateTime timestamp;

  /// AI-assigned risk tier.
  final SpamRiskLevel riskLevel;

  /// Primary attack technique identified.
  final AttackType attackType;

  /// AI model confidence score in range 0.0–1.0.
  final double aiConfidence;

  /// Current lifecycle state within the spam folder.
  final SpamStatus status;

  /// List of granular threat tags surfaced by the AI (e.g. 'malicious_url').
  final List<String> detectedThreats;

  /// When the message was moved to the Spam Folder.
  final DateTime? quarantinedAt;

  /// Returns a copy of this entity with the specified fields overridden.
  SpamMessage copyWith({
    String? id,
    String? sender,
    String? body,
    DateTime? timestamp,
    SpamRiskLevel? riskLevel,
    AttackType? attackType,
    double? aiConfidence,
    SpamStatus? status,
    List<String>? detectedThreats,
    DateTime? quarantinedAt,
  }) {
    return SpamMessage(
      id: id ?? this.id,
      sender: sender ?? this.sender,
      body: body ?? this.body,
      timestamp: timestamp ?? this.timestamp,
      riskLevel: riskLevel ?? this.riskLevel,
      attackType: attackType ?? this.attackType,
      aiConfidence: aiConfidence ?? this.aiConfidence,
      status: status ?? this.status,
      detectedThreats: detectedThreats ?? this.detectedThreats,
      quarantinedAt: quarantinedAt ?? this.quarantinedAt,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SpamMessage &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}
