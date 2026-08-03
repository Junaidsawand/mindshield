import 'dart:convert';
import 'package:flutter/foundation.dart';
import '../database/database_helper.dart';

class AnalysisService {
  static final AnalysisService instance = AnalysisService._();
  AnalysisService._();

  /// Analyzes a pending message, determines threat level, and updates SQLite.
  Future<void> analyzeMessage({
    required String id,
    required String sender,
    required String body,
  }) async {
    debugPrint('AnalysisService: Analyzing message $id from $sender...');

    // Simulate AI inference delay (~500ms)
    await Future.delayed(const Duration(milliseconds: 500));

    final lowerBody = body.toLowerCase();
    
    // Default values for benign/safe message
    String aiStatus = 'safe';
    int isSpam = 0;
    double confidenceScore = 0.95;
    List<String> detectedThreats = [];
    String? spamRiskLevel;
    String? spamAttackType;
    String? spamStatus;

    if (lowerBody.contains('urgent') ||
        lowerBody.contains('suspended') ||
        lowerBody.contains('verify') ||
        lowerBody.contains('secure') ||
        lowerBody.contains('bank') ||
        lowerBody.contains('http://') ||
        lowerBody.contains('https://')) {
      // Phishing / Smishing
      aiStatus = 'scam';
      isSpam = 1;
      confidenceScore = 0.95;
      detectedThreats = ['phishing', 'malicious_url', 'urgency_manipulation'];
      spamRiskLevel = 'critical';
      spamAttackType = 'phishing';
      spamStatus = 'quarantined';
    } else if (lowerBody.contains('won') ||
        lowerBody.contains('voucher') ||
        lowerBody.contains('prize') ||
        lowerBody.contains('cash') ||
        lowerBody.contains('claim')) {
      // Prize Scam
      aiStatus = 'scam';
      isSpam = 1;
      confidenceScore = 0.98;
      detectedThreats = ['prize_scam', 'social_engineering'];
      spamRiskLevel = 'high';
      spamAttackType = 'prizeScam';
      spamStatus = 'quarantined';
    } else if (lowerBody.contains('investment') ||
        lowerBody.contains('advisor') ||
        lowerBody.contains('double your') ||
        lowerBody.contains('earn') ||
        lowerBody.contains('work from home')) {
      // Investment / Job Fraud
      aiStatus = 'suspicious';
      isSpam = 1;
      confidenceScore = 0.75;
      detectedThreats = ['investment_fraud', 'unsolicited_contact'];
      spamRiskLevel = 'medium';
      spamAttackType = 'investmentFraud';
      spamStatus = 'quarantined';
    }

    final updateValues = {
      'ai_status': aiStatus,
      'is_spam': isSpam,
      'confidence_score': confidenceScore,
      'detected_threats': jsonEncode(detectedThreats),
      'spam_risk_level': spamRiskLevel,
      'spam_attack_type': spamAttackType,
      'spam_status': spamStatus,
      'quarantined_at': isSpam == 1 ? DateTime.now().millisecondsSinceEpoch : null,
    };

    await DatabaseHelper.instance.updateMessage(id, updateValues);
    debugPrint('AnalysisService: Completed analysis for $id. Verdict: $aiStatus');
  }
}
