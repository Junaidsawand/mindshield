// lib/features/spam/data/dummy_spam_repository.dart

import '../domain/spam_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// DummySpamRepository
// ─────────────────────────────────────────────────────────────────────────────

/// Provides realistic dummy quarantined-spam data for UI development and
/// thesis demonstration.
///
/// When the real backend is ready, replace this class with a
/// [SqfliteSpamRepository] that reads from the local database.
/// [SpamProvider] only depends on the public API, so the swap is a one-line
/// change in [main.dart].
class DummySpamRepository {
  DummySpamRepository._();

  static final DummySpamRepository instance = DummySpamRepository._();

  // ── In-memory data store ─────────────────────────────────────────────────

  // Mutable list so operations (restore / delete / block) can be applied
  // in-memory during the session.
  final List<SpamMessage> _messages = _seed();

  // ── Public API ───────────────────────────────────────────────────────────

  /// Fetches all quarantined spam messages, newest-quarantined first.
  Future<List<SpamMessage>> fetchSpamMessages() async {
    await Future.delayed(const Duration(milliseconds: 550));
    return List.unmodifiable(_messages);
  }

  /// Permanently removes a message from the spam folder (simulated delete).
  Future<void> deleteMessage(String id) async {
    await Future.delayed(const Duration(milliseconds: 200));
    _messages.removeWhere((m) => m.id == id);
  }

  /// Restores a message to the inbox by removing it from the spam folder.
  Future<void> restoreToInbox(String id) async {
    await Future.delayed(const Duration(milliseconds: 200));
    _messages.removeWhere((m) => m.id == id);
  }

  /// Marks the sender of this message as blocked and updates the status.
  Future<SpamMessage> blockSender(String id) async {
    await Future.delayed(const Duration(milliseconds: 200));
    final idx = _messages.indexWhere((m) => m.id == id);
    if (idx == -1) throw ArgumentError('SpamMessage not found: $id');
    _messages[idx] = _messages[idx].copyWith(status: SpamStatus.blocked);
    return _messages[idx];
  }

  /// Marks a message as reviewed.
  Future<SpamMessage> markReviewed(String id) async {
    final idx = _messages.indexWhere((m) => m.id == id);
    if (idx == -1) throw ArgumentError('SpamMessage not found: $id');
    _messages[idx] = _messages[idx].copyWith(status: SpamStatus.reviewed);
    return _messages[idx];
  }

  // ── Seed data ────────────────────────────────────────────────────────────

  static List<SpamMessage> _seed() {
    final now = DateTime.now();
    return [
      // ── CRITICAL ─────────────────────────────────────────────────────────
      SpamMessage(
        id: 'spam_001',
        sender: '+1 (888) 220-5530',
        body:
            'URGENT: Your bank account has been suspended. Click here immediately to restore access: http://secure-bank-verify.xyz/restore?token=aB3kD9',
        timestamp: now.subtract(const Duration(minutes: 18)),
        riskLevel: SpamRiskLevel.critical,
        attackType: AttackType.phishing,
        aiConfidence: 0.99,
        status: SpamStatus.quarantined,
        detectedThreats: ['phishing', 'malicious_url', 'urgency_manipulation'],
        quarantinedAt: now.subtract(const Duration(minutes: 17)),
      ),
      SpamMessage(
        id: 'spam_002',
        sender: 'SARS eFilng',
        body:
            'SARS: Your tax refund of R3,892.00 is ready. Provide your bank details at: http://sars-refund.co/claim?ref=TX9281 within 24 hours.',
        timestamp: now.subtract(const Duration(hours: 9)),
        riskLevel: SpamRiskLevel.critical,
        attackType: AttackType.govImpersonation,
        aiConfidence: 0.97,
        status: SpamStatus.quarantined,
        detectedThreats: [
          'government_impersonation',
          'phishing',
          'malicious_url',
        ],
        quarantinedAt: now.subtract(const Duration(hours: 8, minutes: 55)),
      ),
      SpamMessage(
        id: 'spam_003',
        sender: '+27 60 123 4567',
        body:
            'Your crypto wallet has been compromised. Call our security team NOW at 0800-CRYPTO or visit http://crypto-secure-wallet.ru immediately.',
        timestamp: now.subtract(const Duration(days: 1, hours: 6)),
        riskLevel: SpamRiskLevel.critical,
        attackType: AttackType.cryptoScam,
        aiConfidence: 0.99,
        status: SpamStatus.blocked,
        detectedThreats: [
          'crypto_scam',
          'malicious_url',
          'urgency_manipulation',
        ],
        quarantinedAt: now.subtract(const Duration(days: 1, hours: 5)),
      ),
      SpamMessage(
        id: 'spam_004',
        sender: 'ABSA Security',
        body:
            'Alert: Unusual login detected on your ABSA account. Verify your identity immediately at: http://absa-verify-now.info/login or your account will be frozen.',
        timestamp: now.subtract(const Duration(days: 2, hours: 3)),
        riskLevel: SpamRiskLevel.critical,
        attackType: AttackType.smishing,
        aiConfidence: 0.98,
        status: SpamStatus.reviewed,
        detectedThreats: [
          'bank_impersonation',
          'malicious_url',
          'account_freeze_threat',
        ],
        quarantinedAt: now.subtract(const Duration(days: 2, hours: 2)),
      ),
      SpamMessage(
        id: 'spam_005',
        sender: 'MTN Rewards',
        body:
            'Congratulations! Your MTN number has won R100,000. To claim, visit: bit.ly/mtn-prize-claim and enter your OTP. Expires in 24hrs!',
        timestamp: now.subtract(const Duration(days: 3, hours: 1)),
        riskLevel: SpamRiskLevel.critical,
        attackType: AttackType.prizeScam,
        aiConfidence: 0.96,
        status: SpamStatus.quarantined,
        detectedThreats: ['prize_scam', 'shortened_url', 'otp_harvesting'],
        quarantinedAt: now.subtract(const Duration(days: 3)),
      ),

      // ── HIGH RISK ─────────────────────────────────────────────────────────
      SpamMessage(
        id: 'spam_006',
        sender: '+27 82 555 0193',
        body:
            'You have won a R50,000 Shoprite voucher! To claim your prize send your ID number and banking details to claims@shoprite-promo.net',
        timestamp: now.subtract(const Duration(hours: 2, minutes: 45)),
        riskLevel: SpamRiskLevel.high,
        attackType: AttackType.prizeScam,
        aiConfidence: 0.88,
        status: SpamStatus.quarantined,
        detectedThreats: ['social_engineering', 'pii_harvesting', 'prize_scam'],
        quarantinedAt: now.subtract(const Duration(hours: 2, minutes: 40)),
      ),
      SpamMessage(
        id: 'spam_007',
        sender: '+44 7923 102938',
        body:
            'Hi, I saw your profile. I am a financial advisor based in London. I can double your investment in 30 days guaranteed. Reply YES to learn more.',
        timestamp: now.subtract(const Duration(hours: 5, minutes: 30)),
        riskLevel: SpamRiskLevel.high,
        attackType: AttackType.investmentFraud,
        aiConfidence: 0.82,
        status: SpamStatus.quarantined,
        detectedThreats: ['investment_fraud', 'unsolicited_contact'],
        quarantinedAt: now.subtract(const Duration(hours: 5, minutes: 25)),
      ),
      SpamMessage(
        id: 'spam_008',
        sender: 'DHL Express',
        body:
            'Package #ZA849302 on hold. Customs clearance fee R79.99 outstanding. Pay now: dhl-za-customs.net/pay or package returned.',
        timestamp: now.subtract(const Duration(days: 1, hours: 10)),
        riskLevel: SpamRiskLevel.high,
        attackType: AttackType.deliveryScam,
        aiConfidence: 0.85,
        status: SpamStatus.reviewed,
        detectedThreats: ['delivery_scam', 'fake_domain', 'urgency_manipulation'],
        quarantinedAt: now.subtract(const Duration(days: 1, hours: 9)),
      ),
      SpamMessage(
        id: 'spam_009',
        sender: '+1 (202) 555-0147',
        body:
            'Your parcel delivery has been put on hold due to unpaid customs duty. Pay R49.99 to release: track-my-parcel.delivery/pay',
        timestamp: now.subtract(const Duration(hours: 14, minutes: 8)),
        riskLevel: SpamRiskLevel.high,
        attackType: AttackType.deliveryScam,
        aiConfidence: 0.78,
        status: SpamStatus.quarantined,
        detectedThreats: ['delivery_scam', 'suspicious_url'],
        quarantinedAt: now.subtract(const Duration(hours: 14)),
      ),
      SpamMessage(
        id: 'spam_010',
        sender: 'Telkom Loyalty',
        body:
            'As a valued Telkom customer you qualify for a FREE upgrade. Click to claim your reward: telkom-loyalty-upgrade.com/claim',
        timestamp: now.subtract(const Duration(days: 2, hours: 15)),
        riskLevel: SpamRiskLevel.high,
        attackType: AttackType.socialEngineering,
        aiConfidence: 0.81,
        status: SpamStatus.blocked,
        detectedThreats: ['brand_impersonation', 'suspicious_url'],
        quarantinedAt: now.subtract(const Duration(days: 2, hours: 14)),
      ),

      // ── MEDIUM RISK ───────────────────────────────────────────────────────
      SpamMessage(
        id: 'spam_011',
        sender: '+27 73 400 9123',
        body:
            'Work from home and earn R5,000/week. No experience needed. Join our team: wa.me/27734009123',
        timestamp: now.subtract(const Duration(days: 1, hours: 2)),
        riskLevel: SpamRiskLevel.medium,
        attackType: AttackType.socialEngineering,
        aiConfidence: 0.65,
        status: SpamStatus.quarantined,
        detectedThreats: ['job_scam', 'whatsapp_redirect'],
        quarantinedAt: now.subtract(const Duration(days: 1, hours: 1)),
      ),
      SpamMessage(
        id: 'spam_012',
        sender: 'HealthAlert ZA',
        body:
            'Medical breakthrough: Lose 10kg in 7 days with this one weird trick. Click here: slim-now.co.za/special-offer',
        timestamp: now.subtract(const Duration(days: 3, hours: 5)),
        riskLevel: SpamRiskLevel.medium,
        attackType: AttackType.malwareLink,
        aiConfidence: 0.61,
        status: SpamStatus.quarantined,
        detectedThreats: ['health_scam', 'suspicious_url'],
        quarantinedAt: now.subtract(const Duration(days: 3, hours: 4)),
      ),
      SpamMessage(
        id: 'spam_013',
        sender: '+27 11 568 2211',
        body:
            'You have been pre-approved for a personal loan of R250,000. No credit checks. Call 011-568-2211 now. Limited offer!',
        timestamp: now.subtract(const Duration(days: 4, hours: 8)),
        riskLevel: SpamRiskLevel.medium,
        attackType: AttackType.socialEngineering,
        aiConfidence: 0.58,
        status: SpamStatus.reviewed,
        detectedThreats: ['loan_scam', 'no_credit_check_fraud'],
        quarantinedAt: now.subtract(const Duration(days: 4, hours: 7)),
      ),
    ];
  }
}
