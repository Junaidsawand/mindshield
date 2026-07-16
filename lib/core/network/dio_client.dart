import 'package:dio/dio.dart';
import '../constants/app_constants.dart';

/// Singleton Dio HTTP client pre-configured for the MindShield backend.
///
/// Interceptors for auth headers, logging, and error normalisation
/// will be added in the networking module.
class DioClient {
  DioClient._();

  static final DioClient _instance = DioClient._();
  static DioClient get instance => _instance;

  late final Dio dio = Dio(
    BaseOptions(
      baseUrl: AppConstants.apiBaseUrl,
      connectTimeout: AppConstants.connectTimeout,
      receiveTimeout: AppConstants.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );
}
