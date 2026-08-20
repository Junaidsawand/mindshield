import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../../core/constants/app_constants.dart';
import '../../../core/network/dio_client.dart';
import '../../inbox/domain/sms_message.dart';
import '../domain/analysis_result.dart';

/// Production repository fetching real AI threat analysis from the FastAPI backend.
class ApiAnalysisRepository {
  static final ApiAnalysisRepository instance = ApiAnalysisRepository._();

  final Dio _dio;

  ApiAnalysisRepository._([Dio? dio]) : _dio = dio ?? DioClient.instance.dio;

  /// Factory constructor for testing with custom/mock [Dio] client.
  factory ApiAnalysisRepository.withDio(Dio dio) => ApiAnalysisRepository._(dio);

  /// Performs backend HTTP POST inference for [message] and maps
  /// the JSON response into a domain [AnalysisResult] entity.
  Future<AnalysisResult> getAnalysis(SmsMessage message) async {
    debugPrint('ApiAnalysisRepository: Requesting analysis for message ${message.id}...');

    final payload = {
      'message': message.body,
      'sender': message.sender,
      'metadata': {
        'app_version': AppConstants.appVersion,
        'locale': 'en-US',
        'network': 'mobile',
      },
    };

    final response = await _dio.post(
      AppConstants.analyzeEndpoint,
      data: payload,
    );

    if (response.statusCode != 200 || response.data == null) {
      throw Exception('Backend API returned HTTP ${response.statusCode}');
    }

    final resMap = response.data is String
        ? jsonDecode(response.data as String) as Map<String, dynamic>
        : response.data as Map<String, dynamic>;

    if (resMap['success'] != true || resMap['data'] == null) {
      final err = resMap['error']?['message'] ?? 'Unknown API error';
      throw Exception('Analysis request failed: $err');
    }

    final data = resMap['data'] as Map<String, dynamic>;
    return _mapJsonToDomain(message, data);
  }

  AnalysisResult _mapJsonToDomain(SmsMessage message, Map<String, dynamic> data) {
    final threatLevel = (data['threat_level'] as String? ?? 'safe').toLowerCase();
    final label = (data['label'] as String? ?? 'safe').toLowerCase();
    final confidence = (data['confidence'] as num? ?? 0.0).toDouble();
    final explanation = data['explanation'] as String? ?? 'Backend model classification completed.';
    final modelVersion = data['model_version'] as String? ?? 'distilbert-uncased-v1';
    final processingMs = (data['processing_time_ms'] as num? ?? 45.0).round();

    final rawIndicators = data['indicators'] as List<dynamic>? ?? [];
    final List<SuspiciousKeyword> keywords = [];
    final List<PsychologicalTactic> tactics = [];

    for (final ind in rawIndicators) {
      if (ind is Map<String, dynamic> && ind['present'] == true) {
        final name = ind['name'] as String? ?? '';
        final detail = ind['detail'] as String? ?? name;
        final weightStr = ind['weight'] as String? ?? 'medium';
        final weightVal = _weightStringToDouble(weightStr);

        keywords.add(SuspiciousKeyword(
          word: name.replaceAll('_', ' ').toUpperCase(),
          weight: weightVal,
          reason: detail,
        ));

        final tactic = _mapIndicatorToTactic(name);
        if (tactic != null && !tactics.contains(tactic)) {
          tactics.add(tactic);
        }
      }
    }

    int threatScore;
    int confidencePercent = (confidence * 100).round().clamp(0, 100);
    AttackType attackType;
    List<String> recommendations;

    if (threatLevel == 'dangerous') {
      threatScore = (confidence * 100).round().clamp(85, 100);
      attackType = _parseAttackType(label, keywords);
      recommendations = const [
        'Do not click any links in this message.',
        'Never enter passwords, PINs, or OTP codes on linked pages.',
        'Quarantine or block this sender immediately.',
      ];
    } else if (threatLevel == 'suspicious') {
      threatScore = (confidence * 80).round().clamp(60, 84);
      attackType = _parseAttackType(label, keywords);
      recommendations = const [
        'Exercise caution before opening links or replying.',
        'Verify the sender identity through official channels.',
      ];
    } else {
      threatScore = (100 - (confidence * 100)).round().clamp(0, 15);
      attackType = AttackType.benign;
      recommendations = const [
        'No suspicious signals detected.',
        'Message appears safe to interact with.',
      ];
    }

    final countryMap = _CountryParser.parse(message.sender);
    final String? countryCode = countryMap?['code'];
    final String? countryName = countryMap?['name'];

    final senderInfo = SenderInfo(
      displayName: message.sender,
      phoneNumber: message.sender,
      countryCode: countryCode,
      countryName: countryName,
      firstSeenDate: null,
      reportCount: null,
      isKnownScammer: threatLevel == 'dangerous',
      carrierName: null,
      lineType: null,
    );

    return AnalysisResult(
      messageId: message.id,
      threatScore: threatScore,
      confidencePercent: confidencePercent,
      attackType: attackType,
      psychologicalTactics: tactics,
      suspiciousKeywords: keywords,
      aiExplanation: explanation,
      senderInfo: senderInfo,
      recommendations: recommendations,
      analysisTimestamp: DateTime.now(),
      modelVersion: modelVersion,
      processingTimeMs: processingMs,
    );
  }

  double _weightStringToDouble(String weight) {
    switch (weight.toLowerCase()) {
      case 'critical':
        return 0.95;
      case 'high':
        return 0.80;
      case 'medium':
        return 0.60;
      case 'low':
        return 0.40;
      default:
        return 0.50;
    }
  }

  PsychologicalTactic? _mapIndicatorToTactic(String indicatorName) {
    switch (indicatorName.toLowerCase()) {
      case 'urgency_language':
        return PsychologicalTactic.urgency;
      case 'credential_request':
        return PsychologicalTactic.fearInduction;
      case 'url_detected':
        return PsychologicalTactic.curiosity;
      case 'financial_keywords':
        return PsychologicalTactic.greed;
      case 'prize_language':
        return PsychologicalTactic.greed;
      case 'excessive_caps':
        return PsychologicalTactic.urgency;
      default:
        return null;
    }
  }

  AttackType _parseAttackType(String label, List<SuspiciousKeyword> keywords) {
    if (label == 'phishing') return AttackType.phishing;
    final keywordNames = keywords.map((k) => k.word.toLowerCase()).toList();

    if (keywordNames.any((k) => k.contains('prize'))) return AttackType.prizeScam;
    if (keywordNames.any((k) => k.contains('financial'))) return AttackType.investmentFraud;
    if (keywordNames.any((k) => k.contains('credential'))) return AttackType.piiHarvesting;
    return AttackType.smishing;
  }
}

class _CountryParser {
  static const Map<String, String> _names = {
    '27': 'South Africa',
    '1': 'United States',
    '44': 'United Kingdom',
    '92': 'Pakistan',
    '91': 'India',
    '49': 'Germany',
    '33': 'France',
    '61': 'Australia',
    '81': 'Japan',
    '55': 'Brazil',
    '86': 'China',
    '7': 'Russia',
    '34': 'Spain',
    '39': 'Italy',
    '966': 'Saudi Arabia',
    '971': 'United Arab Emirates',
  };

  static const Map<String, String> _codes = {
    '27': 'ZA',
    '1': 'US',
    '44': 'GB',
    '92': 'PK',
    '91': 'IN',
    '49': 'DE',
    '33': 'FR',
    '61': 'AU',
    '81': 'JP',
    '55': 'BR',
    '86': 'CN',
    '7': 'RU',
    '34': 'ES',
    '39': 'IT',
    '966': 'SA',
    '971': 'AE',
  };

  static Map<String, String>? parse(String phoneNumber) {
    // Clean spaces, hyphens, and parens
    var clean = phoneNumber.replaceAll(RegExp(r'[\s\-()]+'), '');
    
    // Normalize 00 to +
    if (clean.startsWith('00')) {
      clean = '+${clean.substring(2)}';
    }
    
    if (!clean.startsWith('+')) {
      return null;
    }
    
    final digits = clean.substring(1);
    
    // Try matching prefixes of length 3, 2, then 1 digit
    for (int len = 3; len >= 1; len--) {
      if (digits.length >= len) {
        final prefix = digits.substring(0, len);
        if (_names.containsKey(prefix)) {
          return {
            'code': _codes[prefix]!,
            'name': _names[prefix]!,
          };
        }
      }
    }
    return null;
  }
}
