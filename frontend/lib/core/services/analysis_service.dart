import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../constants/app_constants.dart';
import '../database/database_helper.dart';
import '../network/dio_client.dart';

/// Production AnalysisService for MindShield Flutter application.
///
/// Sends incoming SMS messages to the FastAPI backend (`POST /api/v1/analyze`)
/// running fine-tuned DistilBERT inference. Parses the response JSON and
/// persists full classification metadata into SQLite.
class AnalysisService {
  static final AnalysisService instance = AnalysisService._();

  final Dio _dio;

  AnalysisService._([Dio? dio]) : _dio = dio ?? DioClient.instance.dio;

  /// Factory constructor for testing with custom/mock [Dio] client.
  factory AnalysisService.withDio(Dio dio) => AnalysisService._(dio);

  /// Sends message to the FastAPI backend for real AI inference,
  /// parses backend response, and updates SQLite database.
  Future<void> analyzeMessage({
    required String id,
    required String sender,
    required String body,
  }) async {
    debugPrint('AnalysisService: Initiating backend AI analysis for $id from $sender...');

    final payload = {
      'message': body,
      'sender': sender,
      'metadata': {
        'app_version': AppConstants.appVersion,
        'locale': 'en-US',
        'network': 'mobile',
      },
    };

    Map<String, dynamic>? responseData;
    int attempts = 0;
    const maxRetries = 2;

    while (attempts <= maxRetries) {
      try {
        attempts++;
        final response = await _dio.post(
          AppConstants.analyzeEndpoint,
          data: payload,
        );

        if (response.statusCode == 200 && response.data != null) {
          final resMap = response.data is String
              ? jsonDecode(response.data as String) as Map<String, dynamic>
              : response.data as Map<String, dynamic>;

          if (resMap['success'] == true && resMap['data'] != null) {
            responseData = resMap['data'] as Map<String, dynamic>;
            break;
          }
        }
      } on DioException catch (e) {
        debugPrint('AnalysisService: DioException on attempt $attempts/$maxRetries for $id: ${e.message}');
        if (attempts > maxRetries || e.type == DioExceptionType.cancel) {
          rethrow;
        }
        await Future.delayed(Duration(milliseconds: 300 * attempts));
      } catch (e) {
        debugPrint('AnalysisService: Unexpected error on attempt $attempts/$maxRetries: $e');
        if (attempts > maxRetries) rethrow;
        await Future.delayed(Duration(milliseconds: 300 * attempts));
      }
    }

    if (responseData == null) {
      throw Exception('Failed to receive valid analysis response from backend after $maxRetries retries.');
    }

    // ── Parse backend JSON response ──────────────────────────────────────────
    final threatLevel = (responseData['threat_level'] as String? ?? 'safe').toLowerCase();
    final label = (responseData['label'] as String? ?? 'safe').toLowerCase();
    final confidence = (responseData['confidence'] as num? ?? 0.0).toDouble();

    final rawIndicators = responseData['indicators'] as List<dynamic>? ?? [];
    final List<String> activeThreats = [];
    bool hasCritical = false;

    for (final ind in rawIndicators) {
      if (ind is Map<String, dynamic> && ind['present'] == true) {
        final name = ind['name'] as String? ?? '';
        if (name.isNotEmpty) {
          activeThreats.add(name);
        }
        if (ind['weight'] == 'critical') {
          hasCritical = true;
        }
      }
    }

    // ── Map Backend Verdict -> SQLite schema ─────────────────────────────────
    String aiStatus;
    int isSpam;
    String? spamRiskLevel;
    String? spamAttackType;
    String? spamStatus;
    int? quarantinedAt;

    if (threatLevel == 'dangerous') {
      aiStatus = 'scam';
      isSpam = 1;
      spamStatus = 'quarantined';
      quarantinedAt = DateTime.now().millisecondsSinceEpoch;
      spamRiskLevel = hasCritical ? 'critical' : 'high';
      spamAttackType = _mapLabelToAttackType(label, activeThreats);
    } else if (threatLevel == 'suspicious') {
      aiStatus = 'suspicious';
      isSpam = 1;
      spamStatus = 'quarantined';
      quarantinedAt = DateTime.now().millisecondsSinceEpoch;
      spamRiskLevel = 'medium';
      spamAttackType = _mapLabelToAttackType(label, activeThreats);
    } else {
      aiStatus = 'safe';
      isSpam = 0;
      spamStatus = null;
      quarantinedAt = null;
      spamRiskLevel = null;
      spamAttackType = null;
    }

    final updateValues = <String, dynamic>{
      'ai_status': aiStatus,
      'is_spam': isSpam,
      'confidence_score': confidence,
      'detected_threats': jsonEncode(activeThreats),
      'spam_risk_level': spamRiskLevel,
      'spam_attack_type': spamAttackType,
      'spam_status': spamStatus,
      'quarantined_at': quarantinedAt,
    };

    await DatabaseHelper.instance.updateMessage(id, updateValues);
    debugPrint(
      'AnalysisService: Backend analysis complete for $id. '
      'Verdict: $aiStatus (threatLevel: $threatLevel, conf: ${confidence.toStringAsFixed(2)}, backend: ${responseData['model_version']})',
    );
  }

  String _mapLabelToAttackType(String label, List<String> activeThreats) {
    if (label == 'phishing') return 'phishing';
    if (activeThreats.contains('prize_language') || activeThreats.contains('prize_scam')) {
      return 'prizeScam';
    }
    if (activeThreats.contains('financial_keywords')) {
      return 'investmentFraud';
    }
    if (activeThreats.contains('credential_request')) {
      return 'phishing';
    }
    return 'socialEngineering';
  }
}
