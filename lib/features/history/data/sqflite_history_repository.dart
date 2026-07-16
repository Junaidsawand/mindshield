import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../../inbox/domain/sms_message.dart';
import '../../../core/database/database_helper.dart';

class SqfliteHistoryRepository {
  SqfliteHistoryRepository._();

  static final SqfliteHistoryRepository instance = SqfliteHistoryRepository._();

  /// Fetches all analyzed messages from the SQLite database.
  Future<List<SmsMessage>> fetchHistory() async {
    try {
      final rows = await DatabaseHelper.instance.queryAllMessages();
      // Filter out messages that are still pending analysis
      return rows
          .where((row) => row['ai_status'] != 'pending')
          .map(_mapToSmsMessage)
          .toList();
    } catch (e, st) {
      debugPrint('SqfliteHistoryRepository: Error fetching history: $e');
      debugPrintStack(stackTrace: st);
      rethrow;
    }
  }

  /// Map an SQLite row into the domain SmsMessage.
  SmsMessage _mapToSmsMessage(Map<String, dynamic> row) {
    final rawThreats = row['detected_threats'] as String? ?? '[]';
    List<String> threats = [];
    try {
      threats = List<String>.from(jsonDecode(rawThreats));
    } catch (e) {
      debugPrint('SqfliteHistoryRepository: Error decoding threats string: $e');
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
