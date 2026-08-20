import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite/sqflite.dart';
import 'package:mindshield/features/dashboard/presentation/dashboard_provider.dart';
import 'package:mindshield/core/database/database_helper.dart';
import 'package:mindshield/features/inbox/domain/sms_message.dart';

// ── Mock Database for Migration tests ───────────────────────────────────────
class MockDatabase implements Database {
  String? lastDeleteTable;
  String? lastDeleteWhere;
  List<dynamic>? lastDeleteWhereArgs;
  int mockDeleteResult = 0;

  @override
  Future<int> delete(String table, {String? where, List<Object?>? whereArgs}) async {
    lastDeleteTable = table;
    lastDeleteWhere = where;
    lastDeleteWhereArgs = whereArgs;
    return mockDeleteResult;
  }

  @override
  noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

// ── Mock DatabaseHelper for Provider tests ──────────────────────────────────
class MockDatabaseHelper implements DatabaseHelper {
  int totalSmsCount = 0;
  int analyzedSmsCount = 0;
  int safeSmsCount = 0;
  int suspiciousSmsCount = 0;
  int spamSmsCount = 0;
  List<Map<String, dynamic>> recentMessages = [];

  @override
  Future<int> getTotalSmsCount() async => totalSmsCount;

  @override
  Future<int> getAnalyzedSmsCount() async => analyzedSmsCount;

  @override
  Future<int> getSafeSmsCount() async => safeSmsCount;

  @override
  Future<int> getSuspiciousSmsCount() async => suspiciousSmsCount;

  @override
  Future<int> getSpamSmsCount() async => spamSmsCount;

  @override
  Future<List<Map<String, dynamic>>> queryRecentAnalyzedMessages({int limit = 5}) async => recentMessages;

  @override
  noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('DashboardProvider Tests', () {
    late MockDatabaseHelper mockDb;

    setUp(() {
      mockDb = MockDatabaseHelper();
    });

    test('1. Zero SMS case', () async {
      mockDb.totalSmsCount = 0;
      mockDb.analyzedSmsCount = 0;
      mockDb.safeSmsCount = 0;
      mockDb.suspiciousSmsCount = 0;
      mockDb.spamSmsCount = 0;
      mockDb.recentMessages = [];

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.totalSms, equals(0));
      expect(provider.analyzedSms, equals(0));
      expect(provider.safeSms, equals(0));
      expect(provider.suspiciousSms, equals(0));
      expect(provider.spamSms, equals(0));
      expect(provider.recentAnalyzed, isEmpty);
    });

    test('2. Real SMS but zero analyzed', () async {
      mockDb.totalSmsCount = 100;
      mockDb.analyzedSmsCount = 0;
      mockDb.safeSmsCount = 0;
      mockDb.suspiciousSmsCount = 0;
      mockDb.spamSmsCount = 0;
      mockDb.recentMessages = [];

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.totalSms, equals(100));
      expect(provider.analyzedSms, equals(0));
      expect(provider.recentAnalyzed, isEmpty);
    });

    test('3. One analyzed safe message', () async {
      mockDb.totalSmsCount = 1;
      mockDb.analyzedSmsCount = 1;
      mockDb.safeSmsCount = 1;
      mockDb.suspiciousSmsCount = 0;
      mockDb.spamSmsCount = 0;
      mockDb.recentMessages = [
        {
          'id': 'sms_abc123',
          'sender': 'Mum',
          'body': 'Hello there',
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'ai_status': 'safe',
          'is_read': 1,
          'confidence_score': 0.99,
          'detected_threats': '[]',
        }
      ];

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.totalSms, equals(1));
      expect(provider.analyzedSms, equals(1));
      expect(provider.safeSms, equals(1));
      expect(provider.recentAnalyzed.first.sender, equals('Mum'));
      expect(provider.recentAnalyzed.first.aiStatus, equals(AiStatus.safe));
    });

    test('4. One analyzed suspicious message', () async {
      mockDb.totalSmsCount = 1;
      mockDb.analyzedSmsCount = 1;
      mockDb.safeSmsCount = 0;
      mockDb.suspiciousSmsCount = 1;
      mockDb.spamSmsCount = 0;
      mockDb.recentMessages = [
        {
          'id': 'sms_abc456',
          'sender': 'Unknown',
          'body': 'Unusual login check link',
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'ai_status': 'suspicious',
          'is_read': 0,
          'confidence_score': 0.85,
          'detected_threats': '["suspicious_url"]',
        }
      ];

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.totalSms, equals(1));
      expect(provider.analyzedSms, equals(1));
      expect(provider.suspiciousSms, equals(1));
      expect(provider.recentAnalyzed.first.aiStatus, equals(AiStatus.suspicious));
    });

    test('5. One analyzed scam message', () async {
      mockDb.totalSmsCount = 1;
      mockDb.analyzedSmsCount = 1;
      mockDb.safeSmsCount = 0;
      mockDb.suspiciousSmsCount = 0;
      mockDb.spamSmsCount = 1;
      mockDb.recentMessages = [
        {
          'id': 'sms_abc789',
          'sender': 'BankScam',
          'body': 'Verify now fake bank link',
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'ai_status': 'scam',
          'is_read': 0,
          'confidence_score': 0.99,
          'detected_threats': '["phishing", "malicious_url"]',
        }
      ];

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.totalSms, equals(1));
      expect(provider.analyzedSms, equals(1));
      expect(provider.spamSms, equals(1));
      expect(provider.recentAnalyzed.first.aiStatus, equals(AiStatus.scam));
    });

    test('6. Mixed analyzed classifications', () async {
      mockDb.totalSmsCount = 50;
      mockDb.analyzedSmsCount = 20;
      mockDb.safeSmsCount = 15;
      mockDb.suspiciousSmsCount = 3;
      mockDb.spamSmsCount = 2;

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.totalSms, equals(50));
      expect(provider.analyzedSms, equals(20));
      expect(provider.safeSms, equals(15));
      expect(provider.suspiciousSms, equals(3));
      expect(provider.spamSms, equals(2));
    });

    test('7. Recent activity ordering', () async {
      final now = DateTime.now();
      mockDb.recentMessages = [
        {
          'id': 'sms_1',
          'sender': 'Sender 1',
          'body': 'First body',
          'timestamp': now.millisecondsSinceEpoch,
          'ai_status': 'safe',
          'is_read': 1,
          'detected_threats': '[]',
        },
        {
          'id': 'sms_2',
          'sender': 'Sender 2',
          'body': 'Second body',
          'timestamp': now.subtract(const Duration(minutes: 5)).millisecondsSinceEpoch,
          'ai_status': 'scam',
          'is_read': 0,
          'detected_threats': '[]',
        }
      ];

      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();

      expect(provider.recentAnalyzed.length, equals(2));
      expect(provider.recentAnalyzed[0].id, equals('sms_1'));
      expect(provider.recentAnalyzed[1].id, equals('sms_2'));
    });

    test('8. Dashboard refresh changes state', () async {
      final provider = DashboardProvider(mockDb);
      await provider.loadDashboardData();
      expect(provider.totalSms, equals(0));

      mockDb.totalSmsCount = 10;
      await provider.loadDashboardData();
      expect(provider.totalSms, equals(10));
    });
  });

  group('Database Migration Tests', () {
    test('9. Migration removes seed records & 10. preserves legitimate real SMS', () async {
      final mockDb = MockDatabase();
      mockDb.mockDeleteResult = 12;

      // Invoke the exposed testUpgradeDB method
      await DatabaseHelper.instance.testUpgradeDB(mockDb, 1, 2);

      expect(mockDb.lastDeleteTable, equals('sms_messages'));
      expect(mockDb.lastDeleteWhere, equals('id LIKE "msg_0%" AND id IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'));
      expect(mockDb.lastDeleteWhereArgs, isNotNull);
      expect(mockDb.lastDeleteWhereArgs!.length, equals(12));
      expect(mockDb.lastDeleteWhereArgs![0], equals('msg_001'));
      expect(mockDb.lastDeleteWhereArgs![11], equals('msg_012'));
    });
  });
}
