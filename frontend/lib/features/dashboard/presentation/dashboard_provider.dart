import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../../../core/database/database_helper.dart';
import '../../../core/services/sms_background_service.dart';
import '../../inbox/domain/sms_message.dart';

class DashboardProvider extends ChangeNotifier {
  final DatabaseHelper _db;

  DashboardProvider([DatabaseHelper? dbHelper]) : _db = dbHelper ?? DatabaseHelper.instance {
    loadDashboardData();
    SmsBackgroundService.instance.addListener(loadDashboardData);
  }

  @override
  void dispose() {
    SmsBackgroundService.instance.removeListener(loadDashboardData);
    super.dispose();
  }

  // ── Internal State ────────────────────────────────────────────────────────
  int _totalSms = 0;
  int _analyzedSms = 0;
  int _safeSms = 0;
  int _suspiciousSms = 0;
  int _spamSms = 0;
  List<SmsMessage> _recentAnalyzed = [];
  bool _isLoading = false;
  String? _errorMessage;

  // ── Public Getters ────────────────────────────────────────────────────────
  int get totalSms => _totalSms;
  int get analyzedSms => _analyzedSms;
  int get safeSms => _safeSms;
  int get suspiciousSms => _suspiciousSms;
  int get spamSms => _spamSms;
  List<SmsMessage> get recentAnalyzed => _recentAnalyzed;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  // ── Public API ────────────────────────────────────────────────────────────
  Future<void> loadDashboardData() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final db = _db;
      _totalSms = await db.getTotalSmsCount();
      _analyzedSms = await db.getAnalyzedSmsCount();
      _safeSms = await db.getSafeSmsCount();
      _suspiciousSms = await db.getSuspiciousSmsCount();
      _spamSms = await db.getSpamSmsCount();

      final recentRows = await db.queryRecentAnalyzedMessages(limit: 5);
      _recentAnalyzed = recentRows.map(_mapToSmsMessage).toList();
    } catch (e, st) {
      _errorMessage = 'Failed to load dashboard data: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ── Private Helpers ───────────────────────────────────────────────────────
  SmsMessage _mapToSmsMessage(Map<String, dynamic> row) {
    final rawThreats = row['detected_threats'] as String? ?? '[]';
    List<String> threats = [];
    try {
      threats = List<String>.from(jsonDecode(rawThreats));
    } catch (e) {
      debugPrint('DashboardProvider: Error decoding threats string: $e');
    }

    return SmsMessage(
      id: row['id'] as String,
      sender: row['sender'] as String,
      body: row['body'] as String,
      timestamp: DateTime.fromMillisecondsSinceEpoch(row['timestamp'] as int),
      aiStatus: _parseAiStatus(row['ai_status'] as String),
      isRead: (row['is_read'] as int) == 1,
      confidenceScore: row['confidence_score'] as double?,
      detectedThreats: threats,
    );
  }

  AiStatus _parseAiStatus(String val) {
    switch (val) {
      case 'pending':
        return AiStatus.pending;
      case 'safe':
        return AiStatus.safe;
      case 'suspicious':
        return AiStatus.suspicious;
      case 'scam':
        return AiStatus.scam;
      default:
        return AiStatus.safe;
    }
  }
}
