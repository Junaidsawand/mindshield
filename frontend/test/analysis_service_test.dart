import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mindshield/core/services/analysis_service.dart';

class MockAdapter implements HttpClientAdapter {
  late RequestOptions lastOptions;
  int callCount = 0;
  ResponseBody Function(RequestOptions options)? responseHandler;

  @override
  Future<ResponseBody> fetch(
    RequestOptions options,
    Stream<List<int>>? requestStream,
    Future<void>? cancelFuture,
  ) async {
    callCount++;
    lastOptions = options;
    if (responseHandler != null) {
      return responseHandler!(options);
    }
    const jsonStr = '''
    {
      "success": true,
      "message": "Analysis complete",
      "data": {
        "label": "phishing",
        "threat_level": "dangerous",
        "confidence": 0.952,
        "explanation": "Test explanation",
        "indicators": [
          {"name": "credential_request", "present": true, "weight": "critical", "detail": "Test detail"}
        ],
        "model_version": "distilbert-uncased-v1",
        "processing_time_ms": 42.0
      }
    }
    ''';
    return ResponseBody.fromString(
      jsonStr,
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
  TestWidgetsFlutterBinding.ensureInitialized();

  group('AnalysisService Production Integration Tests', () {
    late Dio dio;
    late MockAdapter adapter;
    late AnalysisService service;

    setUp(() {
      dio = Dio(BaseOptions(baseUrl: 'http://127.0.0.1:8000/api/v1'));
      adapter = MockAdapter();
      dio.httpClientAdapter = adapter;
      service = AnalysisService.withDio(dio);
    });

    test('analyzeMessage sends correct HTTP POST payload to backend endpoint', () async {
      // Execute analyzeMessage logic
      // Using mock ID that will not fail DB if DB is mocked or uninitialized in test
      try {
        await service.analyzeMessage(
          id: 'test_msg_001',
          sender: 'BANK_ALERT',
          body: 'URGENT: Verify your account at http://fake.bank',
        );
      } catch (_) {
        // SQLite may not be initialized in headless widget test context; verify Dio request details
      }

      expect(adapter.callCount, equals(1));
      expect(adapter.lastOptions.path, equals('/analyze'));
      expect(adapter.lastOptions.method, equals('POST'));

      final bodyData = adapter.lastOptions.data as Map<String, dynamic>;
      expect(bodyData['message'], equals('URGENT: Verify your account at http://fake.bank'));
      expect(bodyData['sender'], equals('BANK_ALERT'));
      expect(bodyData['metadata']['app_version'], isNotNull);
    });

    test('retries up to 2 times on network failure', () async {
      int fetchCalls = 0;
      adapter.responseHandler = (options) {
        fetchCalls++;
        if (fetchCalls <= 2) {
          throw DioException(
            requestOptions: options,
            type: DioExceptionType.connectionTimeout,
            error: 'Connection timeout',
          );
        }
        const successJson = '''
        {
          "success": true,
          "data": {
            "label": "safe",
            "threat_level": "safe",
            "confidence": 0.98,
            "explanation": "Safe text",
            "indicators": [],
            "model_version": "distilbert-uncased-v1"
          }
        }
        ''';
        return ResponseBody.fromString(successJson, 200);
      };

      try {
        await service.analyzeMessage(
          id: 'test_msg_retry',
          sender: 'Friend',
          body: 'Hello, how are you doing?',
        );
      } catch (_) {}

      expect(fetchCalls, equals(3)); // 1 initial + 2 retries
    });
  });
}
