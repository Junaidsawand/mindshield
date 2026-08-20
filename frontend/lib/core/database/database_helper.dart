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
      onUpgrade: _upgradeDB,
      onOpen: (db) async {
        debugPrint('Database opened successfully.');
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

  Future<void> _upgradeDB(Database db, int oldVersion, int newVersion) async {
    debugPrint('Upgrading database from $oldVersion to $newVersion...');
    if (oldVersion < 2) {
      // Safely delete precisely only the old seeded dummy data (msg_001 to msg_012)
      final List<String> seedIds = List.generate(12, (index) => 'msg_${(index + 1).toString().padLeft(3, '0')}');
      
      final deleteCount = await db.delete(
        'sms_messages',
        where: 'id LIKE "msg_0%" AND id IN (${List.filled(seedIds.length, '?').join(', ')})',
        whereArgs: seedIds,
      );
      debugPrint('Database migration: Deleted $deleteCount seed mock messages during v1 -> v2 upgrade.');
    }
  }

  // ── Dashboard Metrics Helpers ──────────────────────────────────────────────

  Future<int> getTotalSmsCount() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(*) as count FROM sms_messages');
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<int> getAnalyzedSmsCount() async {
    final db = await database;
    final result = await db.rawQuery("SELECT COUNT(*) as count FROM sms_messages WHERE ai_status != 'pending'");
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<int> getSafeSmsCount() async {
    final db = await database;
    final result = await db.rawQuery("SELECT COUNT(*) as count FROM sms_messages WHERE ai_status = 'safe'");
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<int> getSuspiciousSmsCount() async {
    final db = await database;
    final result = await db.rawQuery("SELECT COUNT(*) as count FROM sms_messages WHERE ai_status = 'suspicious'");
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<int> getSpamSmsCount() async {
    final db = await database;
    final result = await db.rawQuery("SELECT COUNT(*) as count FROM sms_messages WHERE is_spam = 1");
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<List<Map<String, dynamic>>> queryRecentAnalyzedMessages({int limit = 5}) async {
    final db = await database;
    return await db.query(
      'sms_messages',
      where: "ai_status != 'pending'",
      orderBy: 'timestamp DESC',
      limit: limit,
    );
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

  @visibleForTesting
  Future<void> testUpgradeDB(Database db, int oldVersion, int newVersion) => _upgradeDB(db, oldVersion, newVersion);
}
