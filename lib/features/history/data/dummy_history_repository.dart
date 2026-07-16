import '../../inbox/domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// DummyHistoryRepository
// ─────────────────────────────────────────────────────────────────────────────

/// Provides realistic dummy history data for UI development.
///
/// When the real SMS backend is ready, replace this class with a
/// [SqfliteHistoryRepository] that reads from the local database.
class DummyHistoryRepository {
  DummyHistoryRepository._();

  static final DummyHistoryRepository instance = DummyHistoryRepository._();

  /// Returns a list of previously analyzed [SmsMessage]s.
  Future<List<SmsMessage>> fetchHistory() async {
    // Simulate a brief network/DB delay for realistic UX.
    await Future.delayed(const Duration(milliseconds: 400));
    return _messages;
  }

  // ── Dummy data ─────────────────────────────────────────────────────────────

  static final List<SmsMessage> _messages = [
    SmsMessage(
      id: 'hist_001',
      sender: 'Mum 👩',
      body: 'Hi sweetheart! Are you coming home for dinner tonight? I made your favourite pasta 🍝',
      timestamp: DateTime.now().subtract(const Duration(days: 1, hours: 4)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.97,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'hist_002',
      sender: '+1 (888) 220-5530',
      body: 'URGENT: Your bank account has been suspended. Click here immediately to restore access: http://secure-bank-verify.xyz/restore?token=aB3kD9',
      timestamp: DateTime.now().subtract(const Duration(days: 1, hours: 18)),
      aiStatus: AiStatus.scam,
      isRead: true,
      confidenceScore: 0.99,
      detectedThreats: ['phishing', 'malicious_url', 'urgency_manipulation'],
    ),
    SmsMessage(
      id: 'hist_003',
      sender: 'FNB Alerts',
      body: 'Your account ending 4821 has been debited R1,250.00 on 15 Jul 2026. Available balance: R8,340.00. Not you? Call 0800 111 005.',
      timestamp: DateTime.now().subtract(const Duration(days: 2, hours: 1)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.95,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'hist_004',
      sender: '+27 82 555 0193',
      body: 'You have won a R50,000 Shoprite voucher! To claim your prize send your ID number and banking details to claims@shoprite-promo.net',
      timestamp: DateTime.now().subtract(const Duration(days: 3, hours: 2)),
      aiStatus: AiStatus.scam,
      isRead: true,
      confidenceScore: 0.98,
      detectedThreats: ['social_engineering', 'pii_harvesting', 'prize_scam'],
    ),
    SmsMessage(
      id: 'hist_005',
      sender: 'Uber',
      body: 'Your ride is arriving in 2 minutes. Driver: Sipho M, Toyota Corolla GK 43 XP. Track live: uber.com/live/abc123',
      timestamp: DateTime.now().subtract(const Duration(days: 3, hours: 5)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.96,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'hist_006',
      sender: '+44 7923 102938',
      body: 'Hi, I saw your profile. I am a financial advisor based in London. I can double your investment in 30 days. Reply "YES" to learn more.',
      timestamp: DateTime.now().subtract(const Duration(days: 4, hours: 7)),
      aiStatus: AiStatus.suspicious,
      isRead: true,
      confidenceScore: 0.82,
      detectedThreats: ['investment_fraud', 'unsolicited_contact'],
    ),
    SmsMessage(
      id: 'hist_007',
      sender: 'Netflix',
      body: 'Your Netflix password was recently changed. If this was not you, visit netflix.com/account to secure your account.',
      timestamp: DateTime.now().subtract(const Duration(days: 5, hours: 2)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.91,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'hist_008',
      sender: 'SARS eFilng',
      body: 'SARS: Your tax refund of R3,892.00 is ready. Provide your bank details at: http://sars-refund.co/claim?ref=TX9281 within 24 hours.',
      timestamp: DateTime.now().subtract(const Duration(days: 6, hours: 9)),
      aiStatus: AiStatus.scam,
      isRead: true,
      confidenceScore: 0.97,
      detectedThreats: ['government_impersonation', 'phishing', 'malicious_url'],
    ),
  ];
}
