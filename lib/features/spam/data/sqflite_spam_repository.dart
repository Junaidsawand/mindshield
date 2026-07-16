import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../domain/spam_message.dart';
import '../../../core/database/database_helper.dart';

class SqfliteSpamRepository {
  SqfliteSpamRepository._();

  static final SqfliteSpamRepository instance = SqfliteSpamRepository._();

  /// Fetches all quarantined spam messages.
  Future<List<SpamMessage>> fetchSpamMessages() async {
    try {
      final rows = await DatabaseHelper.instance.querySpamMessages();
      return rows.map(_mapToSpamMessage).toList();
    } catch (e, st) {
      debugPrint('SqfliteSpamRepository: Error fetching spam messages: $e');
      debugPrintStack(stackTrace: st);
      rethrow;
    }
  }

  /// Permanently deletes a message from the database.
  Future<void> deleteMessage(String id) async {
    try {
      await DatabaseHelper.instance.deleteMessage(id);
      debugPrint('SqfliteSpamRepository: Deleted spam message $id from SQLite.');
    } catch (e) {
      debugPrint('SqfliteSpamRepository: Error deleting message: $e');
      rethrow;
    }
  }

  /// Restores a message to the inbox by marking it as safe and not spam.
  Future<void> restoreToInbox(String id) async {
    try {
      await DatabaseHelper.instance.updateMessage(id, {
        'is_spam': 0,
        'ai_status': 'safe',
        'spam_risk_level': null,
        'spam_attack_type': null,
        'spam_status': null,
        'quarantined_at': null,
      });
      debugPrint('SqfliteSpamRepository: Restored message $id to inbox.');
    } catch (e) {
      debugPrint('SqfliteSpamRepository: Error restoring message to inbox: $e');
      rethrow;
    }
  }

  /// Blocks the sender of the message and updates its status.
  Future<SpamMessage> blockSender(String id) async {
    try {
      await DatabaseHelper.instance.updateMessage(id, {'spam_status': 'blocked'});
      final rows = await DatabaseHelper.instance.querySpamMessages();
      final updatedRow = rows.firstWhere((r) => r['id'] == id);
      return _mapToSpamMessage(updatedRow);
    } catch (e) {
      debugPrint('SqfliteSpamRepository: Error blocking sender for $id: $e');
      rethrow;
    }
  }

  /// Marks a message as reviewed.
  Future<SpamMessage> markReviewed(String id) async {
    try {
      await DatabaseHelper.instance.updateMessage(id, {'spam_status': 'reviewed'});
      final rows = await DatabaseHelper.instance.querySpamMessages();
      final updatedRow = rows.firstWhere((r) => r['id'] == id);
      return _mapToSpamMessage(updatedRow);
    } catch (e) {
      debugPrint('SqfliteSpamRepository: Error marking reviewed for $id: $e');
      rethrow;
    }
  }

  /// Maps an SQLite database row into a domain SpamMessage.
  SpamMessage _mapToSpamMessage(Map<String, dynamic> row) {
    final rawThreats = row['detected_threats'] as String? ?? '[]';
    List<String> threats = [];
    try {
      threats = List<String>.from(jsonDecode(rawThreats));
    } catch (e) {
      debugPrint('SqfliteSpamRepository: Error decoding threats string: $e');
    }

    final quarantinedAtVal = row['quarantined_at'] as int?;

    return SpamMessage(
      id: row['id'] as String,
      sender: row['sender'] as String,
      body: row['body'] as String,
      timestamp: DateTime.fromMillisecondsSinceEpoch(row['timestamp'] as int),
      riskLevel: _parseRiskLevel(row['spam_risk_level'] as String? ?? 'medium'),
      attackType: _parseAttackType(row['spam_attack_type'] as String? ?? 'socialEngineering'),
      aiConfidence: row['confidence_score'] as double? ?? 0.5,
      status: _parseSpamStatus(row['spam_status'] as String? ?? 'quarantined'),
      detectedThreats: threats,
      quarantinedAt: quarantinedAtVal != null ? DateTime.fromMillisecondsSinceEpoch(quarantinedAtVal) : null,
    );
  }

  SpamRiskLevel _parseRiskLevel(String val) {
    switch (val) {
      case 'critical':
        return SpamRiskLevel.critical;
      case 'high':
        return SpamRiskLevel.high;
      case 'medium':
        return SpamRiskLevel.medium;
      default:
        return SpamRiskLevel.medium;
    }
  }

  AttackType _parseAttackType(String val) {
    switch (val) {
      case 'phishing': return AttackType.phishing;
      case 'smishing': return AttackType.smishing;
      case 'vishing': return AttackType.vishing;
      case 'prizeScam': return AttackType.prizeScam;
      case 'investmentFraud': return AttackType.investmentFraud;
      case 'deliveryScam': return AttackType.deliveryScam;
      case 'govImpersonation': return AttackType.govImpersonation;
      case 'cryptoScam': return AttackType.cryptoScam;
      case 'malwareLink': return AttackType.malwareLink;
      case 'socialEngineering': return AttackType.socialEngineering;
      default: return AttackType.socialEngineering;
    }
  }

  SpamStatus _parseSpamStatus(String val) {
    switch (val) {
      case 'quarantined':
        return SpamStatus.quarantined;
      case 'reviewed':
        return SpamStatus.reviewed;
      case 'blocked':
        return SpamStatus.blocked;
      default:
        return SpamStatus.quarantined;
    }
  }
}
