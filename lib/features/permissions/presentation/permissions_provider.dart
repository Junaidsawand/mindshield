import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants/app_constants.dart';

// ─────────────────────────────────────────────────────────────────────────────
// PermissionItem — lightweight data class describing one permission entry.
// ─────────────────────────────────────────────────────────────────────────────

/// Metadata bundle for a single Android permission shown in the UI.
class PermissionItem {
  const PermissionItem({
    required this.permission,
    required this.title,
    required this.rationale,
    required this.icon,
    this.required = true,
  });

  /// The [Permission] constant from `permission_handler`.
  ///
  /// * [Permission.sms]   → READ_SMS + RECEIVE_SMS (Android)
  /// * [Permission.phone] → READ_PHONE_STATE (Android; optional)
  final Permission permission;

  /// Human-readable name shown in the card title.
  final String title;

  /// One-sentence explanation shown beneath the title.
  final String rationale;

  /// Icon key resolved in the UI layer via [_PermissionCard._iconMap].
  final String icon;

  /// When [required] is [false] the permission is displayed informally and does
  /// NOT block navigation.  [PermissionsProvider.allGranted] only evaluates
  /// items where [required] is [true].
  final bool required;
}

// ─────────────────────────────────────────────────────────────────────────────
// PermissionsProvider
// ─────────────────────────────────────────────────────────────────────────────

/// Manages runtime permission state for the Permissions module.
///
/// Responsibilities
/// ─────────────────
/// * Owns the canonical list of [PermissionItem]s the app needs.
/// * Tracks the current [PermissionStatus] for each permission.
/// * Exposes [requestAll] to trigger the OS permission dialog sequence.
/// * Computes [allGranted] as a single boolean the UI can act on.
/// * Persists the "all granted" flag to [SharedPreferences] under
///   [AppConstants.prefKeyPermissionsGranted] so later modules (e.g. Splash)
///   can skip the Permissions screen on repeat launches.
///
/// State transitions
/// ──────────────────
/// ```
/// initial (PermissionStatus.denied)
///   ──► [requestAll] ──► granted           → navigate to Dashboard
///                    ──► denied            → show retry button
///                    ──► permanentlyDenied → show "Open Settings" button
/// ```
class PermissionsProvider extends ChangeNotifier {
  PermissionsProvider() {
    _initStatuses();
  }

  // ── Permission catalogue ──────────────────────────────────────────────────

  /// Ordered list of permissions shown on the Permissions screen.
  ///
  /// Not `const` because [Permission.phone] is a [PermissionWithService]
  /// subtype whose constructor is not a compile-time constant expression.
  ///
  /// Only items with [PermissionItem.required] == true are evaluated by
  /// [allGranted].  Optional items are displayed for transparency.
  static final List<PermissionItem> permissionItems = [
    const PermissionItem(
      permission: Permission.sms,
      title: 'Read & Receive SMS',
      rationale:
          'MindShield reads your incoming messages to detect phishing links, '
          'scam patterns, and malicious content using on-device AI analysis. '
          'It also monitors new messages in real time so you receive instant '
          'alerts before you open a suspicious message.',
      icon: 'message',
      required: true,
    ),
    PermissionItem(
      permission: Permission.phone,
      title: 'Phone State',
      rationale:
          'Used in future versions to correlate suspicious calls with known '
          'scam numbers. Not required to use MindShield today.',
      icon: 'phone_in_talk',
      required: false, // informational — does NOT block navigation
    ),
  ];

  // ── Internal state ────────────────────────────────────────────────────────

  /// Current status for every permission in [permissionItems].
  Map<Permission, PermissionStatus> _statuses = {};

  /// True while an async operation ([checkStatuses] or [requestAll]) is running.
  bool _isLoading = false;

  /// Non-null when [requestAll] or [checkStatuses] throws an unexpected error.
  String? _errorMessage;

  // ── Public getters ────────────────────────────────────────────────────────

  Map<Permission, PermissionStatus> get statuses =>
      Map.unmodifiable(_statuses);

  bool get isLoading => _isLoading;

  String? get errorMessage => _errorMessage;

  /// Returns the stored status for [item], defaulting to [PermissionStatus.denied]
  /// if the status has not been queried yet.
  PermissionStatus statusOf(PermissionItem item) =>
      _statuses[item.permission] ?? PermissionStatus.denied;

  /// [true] when every **required** permission has been granted.
  bool get allGranted {
    for (final item in permissionItems) {
      if (!item.required) continue;
      final status = _statuses[item.permission];
      if (status == null || !status.isGranted) return false;
    }
    return true;
  }

  /// [true] when at least one required permission is permanently denied,
  /// meaning the OS will no longer show its dialog and the user must visit
  /// the app settings page to change the grant.
  bool get hasPermanentlyDenied {
    for (final item in permissionItems) {
      if (!item.required) continue;
      if (_statuses[item.permission]?.isPermanentlyDenied ?? false) return true;
    }
    return false;
  }

  // ── Initialisation ────────────────────────────────────────────────────────

  /// Populate [_statuses] with the initial `denied` default without hitting
  /// the OS. Called from the constructor so the UI has a sensible initial
  /// state before [checkStatuses] completes.
  void _initStatuses() {
    _statuses = {
      for (final item in permissionItems)
        item.permission: PermissionStatus.denied,
    };
  }

  // ── Public async API ──────────────────────────────────────────────────────

  /// Queries the OS for current permission statuses without triggering the
  /// system dialog.  Safe to call from [State.initState] via a post-frame
  /// callback.
  Future<void> checkStatuses() async {
    _setLoading(true);
    try {
      final updated = <Permission, PermissionStatus>{};
      for (final item in permissionItems) {
        updated[item.permission] = await item.permission.status;
      }
      _statuses = updated;
      _errorMessage = null;
      if (allGranted) await _persistGrantedFlag();
    } catch (e, st) {
      _errorMessage = 'Failed to query permissions: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _setLoading(false);
    }
  }

  /// Presents the OS permission dialog for every permission that is not yet
  /// granted, then re-queries statuses and persists the outcome.
  ///
  /// Permissions that are already granted are skipped. Permanently denied
  /// permissions are also skipped (the user must use [openSettings] instead).
  Future<void> requestAll() async {
    _setLoading(true);
    _errorMessage = null;
    try {
      // Collect permissions that still need to be requested.
      final toRequest = <Permission>[];
      for (final item in permissionItems) {
        final current = _statuses[item.permission] ?? PermissionStatus.denied;
        if (!current.isGranted && !current.isPermanentlyDenied) {
          toRequest.add(item.permission);
        }
      }

      if (toRequest.isNotEmpty) {
        // [List<Permission>.request()] returns Map<Permission, PermissionStatus>.
        final results = await toRequest.request();
        _statuses = {..._statuses, ...results};
      }

      if (allGranted) await _persistGrantedFlag();
    } catch (e, st) {
      _errorMessage = 'Failed to request permissions: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _setLoading(false);
    }
  }

  /// Launches the platform App Settings page so the user can manually flip
  /// a permanently denied permission back to granted.
  ///
  /// After returning from settings [checkStatuses] will be called automatically
  /// via [WidgetsBindingObserver.didChangeAppLifecycleState] in the screen.
  Future<void> openSettings() async {
    await openAppSettings();
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  /// Writes [AppConstants.prefKeyPermissionsGranted] = true to SharedPreferences
  /// so future launches can bypass the Permissions screen.
  Future<void> _persistGrantedFlag() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(AppConstants.prefKeyPermissionsGranted, true);
    } catch (_) {
      // Non-fatal — the flag is a convenience cache; the app can re-request
      // permissions if prefs are unavailable.
    }
  }
}
