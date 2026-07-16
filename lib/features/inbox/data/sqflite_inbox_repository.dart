import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../domain/sms_message.dart';
import '../../../core/database/database_helper.dart';

class SqfliteInboxRepository {
  SqfliteInboxRepository._();

  static final SqfliteInboxRepository instance = SqfliteInboxRepository._();

  /// Fetches all messages from the SQLite database.
  Future<List<SmsMessage>> fetchMessages() async {
    try {
      final rows = await DatabaseHelper.instance.queryAllMessages();
      return rows.map(_mapToSmsMessage).toList();
    } catch (e, st) {
      debugPrint('SqfliteInboxRepository: Error fetching messages: $e');
      debugPrintStack(stackTrace: st);
      rethrow;
    }
  }

  /// Marks a message as read in SQLite and returns the updated entity.
  Future<SmsMessage> markAsRead(String id) async {
    try {
      await DatabaseHelper.instance.updateMessage(id, {'is_read': 1});
      final rows = await DatabaseHelper.instance.queryAllMessages();
      final updatedRow = rows.firstWhere((r) => r['id'] == id);
      return _mapToSmsMessage(updatedRow);
    } catch (e) {
      debugPrint('SqfliteInboxRepository: Error marking message as read: $e');
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
      debugPrint('SqfliteInboxRepository: Error decoding threats string: $e');
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
