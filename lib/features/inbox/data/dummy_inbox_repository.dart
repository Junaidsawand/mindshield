import '../domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// DummyInboxRepository
// ─────────────────────────────────────────────────────────────────────────────

/// Provides realistic dummy SMS data for UI development.
///
/// When the real SMS backend is ready, replace this class with a
/// [SqfliteInboxRepository] that reads from the local database. The
/// [InboxProvider] only depends on the public [fetchMessages] API, so the
/// swap is a one-line change in [main.dart].
class DummyInboxRepository {
  DummyInboxRepository._();

  static final DummyInboxRepository instance = DummyInboxRepository._();

  /// Returns a curated list of dummy [SmsMessage]s simulating a realistic
  /// Android SMS inbox with a mix of safe, suspicious, and scam messages.
  Future<List<SmsMessage>> fetchMessages() async {
    // Simulate a brief network/DB delay for realistic UX.
    await Future.delayed(const Duration(milliseconds: 600));
    return _messages;
  }

  /// Marks a message as read in the in-memory list and returns the updated
  /// entity. In the real implementation this would UPDATE the SQLite row.
  Future<SmsMessage> markAsRead(String id) async {
    final idx = _messages.indexWhere((m) => m.id == id);
    if (idx == -1) throw ArgumentError('Message not found: $id');
    _messages[idx] = _messages[idx].copyWith(isRead: true);
    return _messages[idx];
  }

  // ── Dummy data ─────────────────────────────────────────────────────────────

  static final List<SmsMessage> _messages = [
    SmsMessage(
      id: 'msg_001',
      sender: 'Mum 👩',
      body:
          'Hi sweetheart! Are you coming home for dinner tonight? I made your favourite pasta 🍝',
      timestamp: DateTime.now().subtract(const Duration(minutes: 4)),
      aiStatus: AiStatus.safe,
      isRead: false,
      confidenceScore: 0.97,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'msg_002',
      sender: '+1 (888) 220-5530',
      body:
          'URGENT: Your bank account has been suspended. Click here immediately to restore access: http://secure-bank-verify.xyz/restore?token=aB3kD9',
      timestamp: DateTime.now().subtract(const Duration(minutes: 18)),
      aiStatus: AiStatus.scam,
      isRead: false,
      confidenceScore: 0.99,
      detectedThreats: ['phishing', 'malicious_url', 'urgency_manipulation'],
    ),
    SmsMessage(
      id: 'msg_003',
      sender: 'FNB Alerts',
      body:
          'Your account ending 4821 has been debited R1,250.00 on 16 Jul 2026. Available balance: R8,340.00. Not you? Call 0800 111 005.',
      timestamp: DateTime.now().subtract(const Duration(hours: 1, minutes: 12)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.95,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'msg_004',
      sender: '+27 82 555 0193',
      body:
          'You have won a R50,000 Shoprite voucher! To claim your prize send your ID number and banking details to claims@shoprite-promo.net',
      timestamp: DateTime.now().subtract(const Duration(hours: 2, minutes: 45)),
      aiStatus: AiStatus.scam,
      isRead: false,
      confidenceScore: 0.98,
      detectedThreats: ['social_engineering', 'pii_harvesting', 'prize_scam'],
    ),
    SmsMessage(
      id: 'msg_005',
      sender: 'Uber',
      body:
          'Your ride is arriving in 2 minutes. Driver: Sipho M, Toyota Corolla GK 43 XP. Track live: uber.com/live/abc123',
      timestamp: DateTime.now().subtract(const Duration(hours: 3)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.96,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'msg_006',
      sender: '+44 7923 102938',
      body:
          'Hi, I saw your profile. I am a financial advisor based in London. I can double your investment in 30 days. Reply "YES" to learn more.',
      timestamp: DateTime.now().subtract(const Duration(hours: 5, minutes: 30)),
      aiStatus: AiStatus.suspicious,
      isRead: false,
      confidenceScore: 0.82,
      detectedThreats: ['investment_fraud', 'unsolicited_contact'],
    ),
    SmsMessage(
      id: 'msg_007',
      sender: 'Netflix',
      body:
          'Your Netflix password was recently changed. If this was not you, visit netflix.com/account to secure your account.',
      timestamp:
          DateTime.now().subtract(const Duration(hours: 7, minutes: 15)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.91,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'msg_008',
      sender: 'SARS eFilng',
      body:
          'SARS: Your tax refund of R3,892.00 is ready. Provide your bank details at: http://sars-refund.co/claim?ref=TX9281 within 24 hours.',
      timestamp: DateTime.now().subtract(const Duration(hours: 9)),
      aiStatus: AiStatus.scam,
      isRead: false,
      confidenceScore: 0.97,
      detectedThreats: ['government_impersonation', 'phishing', 'malicious_url'],
    ),
    SmsMessage(
      id: 'msg_009',
      sender: 'James 🤝',
      body:
          'Bro, meeting moved to 3pm. Don\'t forget to bring the project files. See you there 👍',
      timestamp: DateTime.now().subtract(const Duration(hours: 11)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.99,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'msg_010',
      sender: '+1 (202) 555-0147',
      body:
          'Your parcel delivery has been put on hold due to unpaid customs duty. Pay R49.99 to release: track-my-parcel.delivery/pay',
      timestamp: DateTime.now().subtract(const Duration(hours: 14, minutes: 8)),
      aiStatus: AiStatus.suspicious,
      isRead: false,
      confidenceScore: 0.78,
      detectedThreats: ['delivery_scam', 'suspicious_url'],
    ),
    SmsMessage(
      id: 'msg_011',
      sender: 'Vodacom',
      body:
          'Good news! You have been gifted 2GB of free data valid for 7 days. Dial *135# to check your balance.',
      timestamp: DateTime.now().subtract(const Duration(days: 1, hours: 2)),
      aiStatus: AiStatus.safe,
      isRead: true,
      confidenceScore: 0.93,
      detectedThreats: [],
    ),
    SmsMessage(
      id: 'msg_012',
      sender: '+27 60 123 4567',
      body:
          'Your crypto wallet has been compromised. Call our security team NOW at 0800-CRYPTO or visit http://crypto-secure-wallet.ru immediately.',
      timestamp: DateTime.now().subtract(const Duration(days: 1, hours: 6)),
      aiStatus: AiStatus.scam,
      isRead: false,
      confidenceScore: 0.99,
      detectedThreats: ['crypto_scam', 'malicious_url', 'urgency_manipulation'],
    ),
  ];
}
