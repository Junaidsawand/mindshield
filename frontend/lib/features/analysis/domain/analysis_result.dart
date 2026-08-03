// ─────────────────────────────────────────────────────────────────────────────
// AttackType enum
// ─────────────────────────────────────────────────────────────────────────────

/// Categorises the primary attack vector identified by the AI model.
enum AttackType {
  phishing,
  smishing,
  vishing,
  prizeScam,
  investmentFraud,
  deliveryScam,
  governmentImpersonation,
  cryptoScam,
  piiHarvesting,
  malwareDistribution,
  benign,
}

/// Extension providing display helpers for [AttackType].
extension AttackTypeX on AttackType {
  String get label {
    switch (this) {
      case AttackType.phishing:
        return 'Phishing';
      case AttackType.smishing:
        return 'SMiShing';
      case AttackType.vishing:
        return 'Vishing';
      case AttackType.prizeScam:
        return 'Prize Scam';
      case AttackType.investmentFraud:
        return 'Investment Fraud';
      case AttackType.deliveryScam:
        return 'Delivery Scam';
      case AttackType.governmentImpersonation:
        return 'Gov. Impersonation';
      case AttackType.cryptoScam:
        return 'Crypto Scam';
      case AttackType.piiHarvesting:
        return 'PII Harvesting';
      case AttackType.malwareDistribution:
        return 'Malware Distribution';
      case AttackType.benign:
        return 'Benign';
    }
  }

  String get description {
    switch (this) {
      case AttackType.phishing:
        return 'Deceptive attempt to steal sensitive credentials via fake links or spoofed identities.';
      case AttackType.smishing:
        return 'SMS-based phishing using fraudulent links, impersonation, or social pressure.';
      case AttackType.vishing:
        return 'Voice/call-based phishing requesting personal or financial information.';
      case AttackType.prizeScam:
        return 'Fraudulent claim of a prize requiring personal details or upfront payment.';
      case AttackType.investmentFraud:
        return 'Unsolicited high-return investment offer with characteristics of a Ponzi or pyramid scheme.';
      case AttackType.deliveryScam:
        return 'Fake parcel/delivery notification designed to extract payment or credentials.';
      case AttackType.governmentImpersonation:
        return 'Impersonation of SARS, Home Affairs, or other government entities to steal information.';
      case AttackType.cryptoScam:
        return 'Fraudulent cryptocurrency scheme or fake wallet security alert.';
      case AttackType.piiHarvesting:
        return 'Attempt to collect personally identifiable information (ID, bank details, OTP).';
      case AttackType.malwareDistribution:
        return 'Message containing a link that likely distributes malicious software.';
      case AttackType.benign:
        return 'No threat characteristics identified. Message appears legitimate.';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PsychologicalTactic enum
// ─────────────────────────────────────────────────────────────────────────────

/// Psychological manipulation tactics identified by the NLP model.
enum PsychologicalTactic {
  urgency,
  fearInduction,
  authority,
  scarcity,
  socialProof,
  reciprocity,
  curiosity,
  greed,
  trustBuilding,
  isolation,
}

/// Extension providing display helpers for [PsychologicalTactic].
extension PsychologicalTacticX on PsychologicalTactic {
  String get label {
    switch (this) {
      case PsychologicalTactic.urgency:
        return 'Urgency';
      case PsychologicalTactic.fearInduction:
        return 'Fear Induction';
      case PsychologicalTactic.authority:
        return 'Authority Appeal';
      case PsychologicalTactic.scarcity:
        return 'Scarcity';
      case PsychologicalTactic.socialProof:
        return 'Social Proof';
      case PsychologicalTactic.reciprocity:
        return 'Reciprocity';
      case PsychologicalTactic.curiosity:
        return 'Curiosity Bait';
      case PsychologicalTactic.greed:
        return 'Greed Appeal';
      case PsychologicalTactic.trustBuilding:
        return 'Trust Building';
      case PsychologicalTactic.isolation:
        return 'Isolation Tactic';
    }
  }

  String get icon {
    switch (this) {
      case PsychologicalTactic.urgency:
        return '⏰';
      case PsychologicalTactic.fearInduction:
        return '😨';
      case PsychologicalTactic.authority:
        return '🏛️';
      case PsychologicalTactic.scarcity:
        return '⚡';
      case PsychologicalTactic.socialProof:
        return '👥';
      case PsychologicalTactic.reciprocity:
        return '🎁';
      case PsychologicalTactic.curiosity:
        return '❓';
      case PsychologicalTactic.greed:
        return '💰';
      case PsychologicalTactic.trustBuilding:
        return '🤝';
      case PsychologicalTactic.isolation:
        return '🔒';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SenderInfo
// ─────────────────────────────────────────────────────────────────────────────

/// Enriched sender metadata retrieved from the analysis backend.
class SenderInfo {
  const SenderInfo({
    required this.displayName,
    required this.phoneNumber,
    required this.countryCode,
    required this.countryName,
    required this.firstSeenDate,
    required this.reportCount,
    required this.isKnownScammer,
    this.carrierName,
    this.lineType,
  });

  /// Human-readable name (contact name or "Unknown Sender").
  final String displayName;

  /// Raw phone number string.
  final String phoneNumber;

  /// ISO 3166-1 alpha-2 country code (e.g. "ZA", "US").
  final String countryCode;

  /// Full country name.
  final String countryName;

  /// Date this number was first seen reporting threats in the MindShield network.
  final DateTime firstSeenDate;

  /// Number of times this sender has been reported in the crowd-sourced database.
  final int reportCount;

  /// Whether the number appears in known scammer databases.
  final bool isKnownScammer;

  /// Carrier / network operator name (if resolvable).
  final String? carrierName;

  /// Line type: e.g. "Mobile", "VoIP", "Landline".
  final String? lineType;
}

// ─────────────────────────────────────────────────────────────────────────────
// SuspiciousKeyword
// ─────────────────────────────────────────────────────────────────────────────

/// Represents a single highlighted keyword and its LIME importance weight.
class SuspiciousKeyword {
  const SuspiciousKeyword({
    required this.word,
    required this.weight,
    required this.reason,
  });

  /// The exact word or phrase as it appears in the message body.
  final String word;

  /// LIME feature importance weight (0.0 – 1.0). Higher = stronger contributor.
  final double weight;

  /// Short human-readable reason this word was flagged.
  final String reason;
}

// ─────────────────────────────────────────────────────────────────────────────
// AnalysisResult
// ─────────────────────────────────────────────────────────────────────────────

/// Full AI analysis result for a single [SmsMessage].
///
/// This is a pure Dart domain entity with no framework dependencies.
/// The data layer maps dummy (or real API) responses into this class.
class AnalysisResult {
  const AnalysisResult({
    required this.messageId,
    required this.threatScore,
    required this.confidencePercent,
    required this.attackType,
    required this.psychologicalTactics,
    required this.suspiciousKeywords,
    required this.aiExplanation,
    required this.senderInfo,
    required this.recommendations,
    required this.analysisTimestamp,
    required this.modelVersion,
    required this.processingTimeMs,
  });

  /// ID of the [SmsMessage] this result belongs to.
  final String messageId;

  /// Threat score 0–100 (0 = completely safe, 100 = confirmed threat).
  final int threatScore;

  /// Model confidence in the classification (0–100 %).
  final int confidencePercent;

  /// Primary attack vector classification.
  final AttackType attackType;

  /// List of detected psychological manipulation tactics.
  final List<PsychologicalTactic> psychologicalTactics;

  /// LIME-highlighted suspicious keywords within the message body.
  final List<SuspiciousKeyword> suspiciousKeywords;

  /// Natural-language AI explanation of the analysis reasoning.
  final String aiExplanation;

  /// Enriched sender metadata.
  final SenderInfo senderInfo;

  /// Ordered list of actionable recommendation strings.
  final List<String> recommendations;

  /// UTC timestamp when the analysis was computed.
  final DateTime analysisTimestamp;

  /// Model version identifier (e.g. "MindShield-NLP v2.3.1").
  final String modelVersion;

  /// Time taken by the inference pipeline in milliseconds.
  final int processingTimeMs;
}
