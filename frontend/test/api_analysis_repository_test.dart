import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mindshield/features/analysis/data/api_analysis_repository.dart';
import 'package:mindshield/features/analysis/domain/analysis_result.dart';
import 'package:mindshield/features/inbox/domain/sms_message.dart';

class MockAdapter implements HttpClientAdapter {
  late RequestOptions lastOptions;
  String responseJson;

  MockAdapter(this.responseJson);

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    lastOptions = options;
    return ResponseBody.fromString(
      responseJson,
      200,
      headers: {
        Headers.contentTypeHeader: [Headers.jsonContentType]
      },
    );
  }

  @override
  void close({bool force = false}) {}
}

void main() {
  group('ApiAnalysisRepository Tests', () {
    test('getAnalysis maps dangerous backend response to domain AnalysisResult entity', () async {
      const jsonResponse = '''
      {
        "success": true,
        "message": "Analysis complete",
        "data": {
          "label": "phishing",
          "threat_level": "dangerous",
          "confidence": 0.965,
          "explanation": "Fine-tuned DistilBERT model detected phishing attempt.",
          "indicators": [
            {
              "name": "credential_request",
              "present": true,
              "weight": "critical",
              "detail": "Requests sensitive password or OTP"
            },
            {
              "name": "url_detected",
              "present": true,
              "weight": "high",
              "detail": "Suspicious URL link"
            }
          ],
          "model_version": "distilbert-uncased-v1",
          "processing_time_ms": 38.5,
          "predicted_at": "2026-08-04T19:00:00Z"
        }
      }
      ''';

      final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000/api/v1'));
      final adapter = MockAdapter(jsonResponse);
      dio.httpClientAdapter = adapter;

      final repo = ApiAnalysisRepository.withDio(dio);
      final sms = SmsMessage(
        id: 'msg_002',
        sender: '+18882205530',
        body: 'URGENT: Verify account at http://fake.bank',
        timestamp: DateTime.now(),
        aiStatus: AiStatus.pending,
      );

      final result = await repo.getAnalysis(sms);

      expect(result.messageId, equals('msg_002'));
      expect(result.threatScore, greaterThanOrEqualTo(85));
      expect(result.confidencePercent, equals(97));
      expect(result.attackType, equals(AttackType.phishing));
      expect(result.modelVersion, equals('distilbert-uncased-v1'));
      expect(result.processingTimeMs, equals(39));
      expect(result.suspiciousKeywords.length, equals(2));
      expect(result.recommendations.length, greaterThan(0));
    });

    test('getAnalysis maps safe backend response to benign AnalysisResult entity', () async {
      const jsonResponse = '''
      {
        "success": true,
        "message": "Analysis complete",
        "data": {
          "label": "safe",
          "threat_level": "safe",
          "confidence": 0.982,
          "explanation": "Fine-tuned DistilBERT model classified text as benign.",
          "indicators": [
            {
              "name": "url_detected",
              "present": false,
              "weight": "high",
              "detail": null
            }
          ],
          "model_version": "distilbert-uncased-v1",
          "processing_time_ms": 24.1
        }
      }
      ''';

      final dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000/api/v1'));
      final adapter = MockAdapter(jsonResponse);
      dio.httpClientAdapter = adapter;

      final repo = ApiAnalysisRepository.withDio(dio);
      final sms = SmsMessage(
        id: 'msg_001',
        sender: 'Mum',
        body: 'Hi honey, see you at dinner!',
        timestamp: DateTime.now(),
        aiStatus: AiStatus.safe,
      );

      final result = await repo.getAnalysis(sms);

      expect(result.messageId, equals('msg_001'));
      expect(result.threatScore, lessThanOrEqualTo(15));
      expect(result.attackType, equals(AttackType.benign));
      expect(result.suspiciousKeywords, isEmpty);
    });
  });
}
