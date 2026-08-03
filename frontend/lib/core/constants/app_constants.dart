/// Global application constants used across features.
///
/// Centralising these values avoids magic strings and makes
/// refactoring easier in later modules.
class AppConstants {
  AppConstants._();

  // ── App metadata ────────────────────────────────────────────────────────────
  static const String appName = 'MindShield';
  static const String appVersion = '1.0.0';

  // ── Shared-preference keys ──────────────────────────────────────────────────
  static const String prefKeyOnboardingDone = 'onboarding_done';
  static const String prefKeyPermissionsGranted = 'permissions_granted';
  static const String prefKeyThemeMode = 'theme_mode';

  // ── Database ────────────────────────────────────────────────────────────────
  static const String dbName = 'mindshield.db';
  static const int dbVersion = 1;

  // ── Network ─────────────────────────────────────────────────────────────────
  /// Base URL for the MindShield AI backend (placeholder – update before use).
  static const String apiBaseUrl = 'https://api.mindshield.local/v1';
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // ── SMS analysis ────────────────────────────────────────────────────────────
  /// Confidence threshold above which an SMS is considered spam.
  static const double spamThreshold = 0.70;
}
