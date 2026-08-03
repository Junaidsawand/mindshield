import 'package:flutter/foundation.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../constants/app_constants.dart';

class DatabaseHelper {
  static final DatabaseHelper instance = DatabaseHelper._init();
  static Database? _database;

  DatabaseHelper._init();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB(AppConstants.dbName);
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);
    debugPrint('Initializing SQLite database at: $path');

    return await openDatabase(
      path,
      version: AppConstants.dbVersion,
      onCreate: _createDB,
      onOpen: (db) async {
        // Seed if empty on open
        await _seedIfEmpty(db);
      },
    );
  }

  Future<void> _createDB(Database db, int version) async {
    debugPrint('Creating sms_messages table...');
    await db.execute('''
      CREATE TABLE sms_messages (
        id TEXT PRIMARY KEY,
        sender TEXT NOT NULL,
        body TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        ai_status TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        confidence_score REAL,
        detected_threats TEXT NOT NULL,
        is_spam INTEGER NOT NULL DEFAULT 0,
        spam_risk_level TEXT,
        spam_attack_type TEXT,
        spam_status TEXT,
        quarantined_at INTEGER
      )
    ''');
  }

  Future<void> _seedIfEmpty(Database db) async {
    final countResult = await db.rawQuery('SELECT COUNT(*) as count FROM sms_messages');
    final count = Sqflite.firstIntValue(countResult) ?? 0;
    if (count > 0) {
      debugPrint('Database already seeded. Message count: $count');
      return;
    }

    debugPrint('Seeding database with initial mock messages...');
    final now = DateTime.now();

    final seedMessages = [
      {
        'id': 'msg_001',
        'sender': 'Mum 👩',
        'body': 'Hi sweetheart! Are you coming home for dinner tonight? I made your favourite pasta 🍝',
        'timestamp': now.subtract(const Duration(minutes: 4)).millisecondsSinceEpoch,
        'ai_status': 'safe',
        'is_read': 0,
        'confidence_score': 0.97,
        'detected_threats': '[]',
        'is_spam': 0,
      },
      {
        'id': 'msg_002',
        'sender': '+1 (888) 220-5530',
        'body': 'URGENT: Your bank account has been suspended. Click here immediately to restore access: http://secure-bank-verify.xyz/restore?token=aB3kD9',
        'timestamp': now.subtract(const Duration(minutes: 18)).millisecondsSinceEpoch,
        'ai_status': 'scam',
        'is_read': 0,
        'confidence_score': 0.99,
        'detected_threats': '["phishing", "malicious_url", "urgency_manipulation"]',
        'is_spam': 1,
        'spam_risk_level': 'critical',
        'spam_attack_type': 'phishing',
        'spam_status': 'quarantined',
        'quarantined_at': now.subtract(const Duration(minutes: 17)).millisecondsSinceEpoch,
      },
      {
        'id': 'msg_003',
        'sender': 'FNB Alerts',
        'body': 'Your account ending 4821 has been debited R1,250.00 on 16 Jul 2026. Available balance: R8,340.00. Not you? Call 0800 111 005.',
        'timestamp': now.subtract(const Duration(hours: 1, minutes: 12)).millisecondsSinceEpoch,
        'ai_status': 'safe',
        'is_read': 1,
        'confidence_score': 0.95,
        'detected_threats': '[]',
        'is_spam': 0,
      },
      {
        'id': 'msg_004',
        'sender': '+27 82 555 0193',
        'body': 'You have won a R50,000 Shoprite voucher! To claim your prize send your ID number and banking details to claims@shoprite-promo.net',
        'timestamp': now.subtract(const Duration(hours: 2, minutes: 45)).millisecondsSinceEpoch,
        'ai_status': 'scam',
        'is_read': 0,
        'confidence_score': 0.98,
        'detected_threats': '["social_engineering", "pii_harvesting", "prize_scam"]',
        'is_spam': 1,
        'spam_risk_level': 'high',
        'spam_attack_type': 'prizeScam',
        'spam_status': 'quarantined',
        'quarantined_at': now.subtract(const Duration(hours: 2, minutes: 40)).millisecondsSinceEpoch,
      },
      {
        'id': 'msg_005',
        'sender': 'Uber',
        'body': 'Your ride is arriving in 2 minutes. Driver: Sipho M, Toyota Corolla GK 43 XP. Track live: uber.com/live/abc123',
        'timestamp': now.subtract(const Duration(hours: 3)).millisecondsSinceEpoch,
        'ai_status': 'safe',
        'is_read': 1,
        'confidence_score': 0.96,
        'detected_threats': '[]',
        'is_spam': 0,
      },
      {
        'id': 'msg_006',
        'sender': '+44 7923 102938',
        'body': 'Hi, I saw your profile. I am a financial advisor based in London. I can double your investment in 30 days. Reply "YES" to learn more.',
        'timestamp': now.subtract(const Duration(hours: 5, minutes: 30)).millisecondsSinceEpoch,
        'ai_status': 'suspicious',
        'is_read': 0,
        'confidence_score': 0.82,
        'detected_threats': '["investment_fraud", "unsolicited_contact"]',
        'is_spam': 1,
        'spam_risk_level': 'high',
        'spam_attack_type': 'investmentFraud',
        'spam_status': 'quarantined',
        'quarantined_at': now.subtract(const Duration(hours: 5, minutes: 25)).millisecondsSinceEpoch,
      },
      {
        'id': 'msg_007',
        'sender': 'Netflix',
        'body': 'Your Netflix password was recently changed. If this was not you, visit netflix.com/account to secure your account.',
        'timestamp': now.subtract(const Duration(hours: 7, minutes: 15)).millisecondsSinceEpoch,
        'ai_status': 'safe',
        'is_read': 1,
        'confidence_score': 0.91,
        'detected_threats': '[]',
        'is_spam': 0,
      },
      {
        'id': 'msg_008',
        'sender': 'SARS eFilng',
        'body': 'SARS: Your tax refund of R3,892.00 is ready. Provide your bank details at: http://sars-refund.co/claim?ref=TX9281 within 24 hours.',
        'timestamp': now.subtract(const Duration(hours: 9)).millisecondsSinceEpoch,
        'ai_status': 'scam',
        'is_read': 0,
        'confidence_score': 0.97,
        'detected_threats': '["government_impersonation", "phishing", "malicious_url"]',
        'is_spam': 1,
        'spam_risk_level': 'critical',
        'spam_attack_type': 'govImpersonation',
        'spam_status': 'quarantined',
        'quarantined_at': now.subtract(const Duration(hours: 8, minutes: 55)).millisecondsSinceEpoch,
      },
      {
        'id': 'msg_009',
        'sender': 'James 🤝',
        'body': 'Bro, meeting moved to 3pm. Don\'t forget to bring the project files. See you there 👍',
        'timestamp': now.subtract(const Duration(hours: 11)).millisecondsSinceEpoch,
        'ai_status': 'safe',
        'is_read': 1,
        'confidence_score': 0.99,
        'detected_threats': '[]',
        'is_spam': 0,
      },
      {
        'id': 'msg_010',
        'sender': '+1 (202) 555-0147',
        'body': 'Your parcel delivery has been put on hold due to unpaid customs duty. Pay R49.99 to release: track-my-parcel.delivery/pay',
        'timestamp': now.subtract(const Duration(hours: 14, minutes: 8)).millisecondsSinceEpoch,
        'ai_status': 'suspicious',
        'is_read': 0,
        'confidence_score': 0.78,
        'detected_threats': '["delivery_scam", "suspicious_url"]',
        'is_spam': 1,
        'spam_risk_level': 'high',
        'spam_attack_type': 'deliveryScam',
        'spam_status': 'quarantined',
        'quarantined_at': now.subtract(const Duration(hours: 14)).millisecondsSinceEpoch,
      },
      {
        'id': 'msg_011',
        'sender': 'Vodacom',
        'body': 'Good news! You have been gifted 2GB of free data valid for 7 days. Dial *135# to check your balance.',
        'timestamp': now.subtract(const Duration(days: 1, hours: 2)).millisecondsSinceEpoch,
        'ai_status': 'safe',
        'is_read': 1,
        'confidence_score': 0.93,
        'detected_threats': '[]',
        'is_spam': 0,
      },
      {
        'id': 'msg_012',
        'sender': '+27 60 123 4567',
        'body': 'Your crypto wallet has been compromised. Call our security team NOW at 0800-CRYPTO or visit http://crypto-secure-wallet.ru immediately.',
        'timestamp': now.subtract(const Duration(days: 1, hours: 6)).millisecondsSinceEpoch,
        'ai_status': 'scam',
        'is_read': 0,
        'confidence_score': 0.99,
        'detected_threats': '["crypto_scam", "malicious_url", "urgency_manipulation"]',
        'is_spam': 1,
        'spam_risk_level': 'critical',
        'spam_attack_type': 'cryptoScam',
        'spam_status': 'blocked',
        'quarantined_at': now.subtract(const Duration(days: 1, hours: 5)).millisecondsSinceEpoch,
      },
    ];

    final batch = db.batch();
    for (final msg in seedMessages) {
      batch.insert('sms_messages', msg);
    }
    await batch.commit(noResult: true);
    debugPrint('Database seeding completed successfully.');
  }

  // ── Helper CRUD database operations ───────────────────────────────────────

  Future<List<Map<String, dynamic>>> queryAllMessages() async {
    final db = await database;
    return await db.query('sms_messages', orderBy: 'timestamp DESC');
  }

  Future<List<Map<String, dynamic>>> queryInboxMessages() async {
    final db = await database;
    return await db.query(
      'sms_messages',
      where: 'is_spam = 0',
      orderBy: 'timestamp DESC',
    );
  }

  Future<Map<String, dynamic>?> queryMessageById(String id) async {
    final db = await database;
    final results = await db.query(
      'sms_messages',
      where: 'id = ?',
      whereArgs: [id],
    );
    return results.isNotEmpty ? results.first : null;
  }

  Future<List<Map<String, dynamic>>> querySpamMessages() async {
    final db = await database;
    return await db.query(
      'sms_messages',
      where: 'is_spam = 1',
      orderBy: 'timestamp DESC',
    );
  }

  Future<List<Map<String, dynamic>>> queryPendingMessages() async {
    final db = await database;
    return await db.query(
      'sms_messages',
      where: 'ai_status = ?',
      whereArgs: ['pending'],
    );
  }

  // ── Conversation-level SQL operations ────────────────────────────────────

  String _normalizeSender(String sender) {
    return sender.replaceAll(RegExp(r'[\s\-()]+'), '').toLowerCase();
  }

  Future<int> moveConversationToSpam(String sender, int quarantinedAt) async {
    final db = await database;
    return await db.rawUpdate('''
      UPDATE sms_messages
      SET is_spam = 1,
          spam_status = 'quarantined',
          quarantined_at = ?,
          ai_status = 'scam',
          spam_risk_level = 'high',
          spam_attack_type = 'socialEngineering'
      WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(sender, ' ', ''), '-', ''), '(', ''), ')', '')) = ?
    ''', [quarantinedAt, _normalizeSender(sender)]);
  }

  Future<int> restoreConversationToInbox(String sender) async {
    final db = await database;
    return await db.rawUpdate('''
      UPDATE sms_messages
      SET is_spam = 0,
          ai_status = 'safe',
          spam_status = NULL,
          quarantined_at = NULL,
          spam_risk_level = NULL,
          spam_attack_type = NULL
      WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(sender, ' ', ''), '-', ''), '(', ''), ')', '')) = ?
    ''', [_normalizeSender(sender)]);
  }

  Future<int> blockConversation(String sender) async {
    final db = await database;
    return await db.rawUpdate('''
      UPDATE sms_messages
      SET spam_status = 'blocked'
      WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(sender, ' ', ''), '-', ''), '(', ''), ')', '')) = ?
    ''', [_normalizeSender(sender)]);
  }

  Future<int> unblockConversation(String sender) async {
    final db = await database;
    return await db.rawUpdate('''
      UPDATE sms_messages
      SET spam_status = 'quarantined'
      WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(sender, ' ', ''), '-', ''), '(', ''), ')', '')) = ?
        AND is_spam = 1
    ''', [_normalizeSender(sender)]);
  }

  Future<int> deleteConversation(String sender) async {
    final db = await database;
    return await db.rawDelete('''
      DELETE FROM sms_messages
      WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(sender, ' ', ''), '-', ''), '(', ''), ')', '')) = ?
    ''', [_normalizeSender(sender)]);
  }

  Future<int> insertMessage(Map<String, dynamic> row) async {
    final db = await database;
    return await db.insert('sms_messages', row, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<int> updateMessage(String id, Map<String, dynamic> values) async {
    final db = await database;
    return await db.update(
      'sms_messages',
      values,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> deleteMessage(String id) async {
    final db = await database;
    return await db.delete(
      'sms_messages',
      where: 'id = ?',
      whereArgs: [id],
    );
  }
}
