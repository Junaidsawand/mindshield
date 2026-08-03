import 'package:flutter/foundation.dart';
import '../data/dummy_analysis_repository.dart';
import '../domain/analysis_result.dart';
import '../../inbox/domain/sms_message.dart';
import '../../spam/data/sqflite_spam_repository.dart';
import '../../../core/services/sms_background_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// AnalysisActionState
// ─────────────────────────────────────────────────────────────────────────────

/// Tracks which action button (if any) is currently processing.
enum AnalysisActionState {
  idle,
  movingToSpam,
  markingSafe,
  blockingSender,
  reporting,
}

// ─────────────────────────────────────────────────────────────────────────────
// AnalysisProvider
// ─────────────────────────────────────────────────────────────────────────────

/// Manages all state for the AI Threat Analysis screen.
class AnalysisProvider extends ChangeNotifier {
  AnalysisProvider();

  // ── Dependencies ──────────────────────────────────────────────────────────

  final _repo = DummyAnalysisRepository.instance;

  // ── Internal state ────────────────────────────────────────────────────────

  AnalysisResult? _analysisResult;
  bool _isLoading = false;
  String? _errorMessage;
  AnalysisActionState _actionState = AnalysisActionState.idle;
  SmsMessage? _currentMessage;

  // ── Public getters ────────────────────────────────────────────────────────

  AnalysisResult? get analysisResult => _analysisResult;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  AnalysisActionState get actionState => _actionState;
  SmsMessage? get currentMessage => _currentMessage;

  /// Whether any action button is processing.
  bool get isActionBusy => _actionState != AnalysisActionState.idle;

  // ── Public API ────────────────────────────────────────────────────────────

  /// Loads the [AnalysisResult] for [message]. Safe to call multiple times;
  /// skips re-fetch if the same message is already loaded.
  Future<void> loadAnalysis(SmsMessage message) async {
    if (_currentMessage?.id == message.id && _analysisResult != null) return;
    _currentMessage = message;
    _setLoading(true);
    _errorMessage = null;
    _analysisResult = null;
    try {
      _analysisResult = await _repo.getAnalysis(message);
    } catch (e, st) {
      _errorMessage = 'Analysis failed: $e';
      debugPrintStack(stackTrace: st);
    } finally {
      _setLoading(false);
    }
  }

  /// Marks the current message as spam and notifies listeners.
  Future<void> moveToSpam() async {
    if (_currentMessage == null) return;
    await _performAction(AnalysisActionState.movingToSpam, () async {
      await SqfliteSpamRepository.instance.moveToSpam(_currentMessage!.id);
      SmsBackgroundService.instance.notifyListeners();
    });
  }

  /// Marks the current message as safe and notifies listeners.
  Future<void> markSafe() async {
    if (_currentMessage == null) return;
    await _performAction(AnalysisActionState.markingSafe, () async {
      await SqfliteSpamRepository.instance.restoreToInbox(_currentMessage!.id);
      SmsBackgroundService.instance.notifyListeners();
    });
  }

  /// Blocks the sender of the current message.
  Future<void> blockSender() async {
    if (_currentMessage == null) return;
    await _performAction(AnalysisActionState.blockingSender, () async {
      await SqfliteSpamRepository.instance.blockSender(_currentMessage!.id);
      SmsBackgroundService.instance.notifyListeners();
    });
  }

  /// Reports the current message to the MindShield threat database.
  Future<void> report() async {
    await _performAction(AnalysisActionState.reporting, () async {
      // Future: call ThreatReportingRepository.submit(_currentMessage!.id)
      await Future.delayed(const Duration(milliseconds: 900));
      debugPrint('[AnalysisProvider] report: ${_currentMessage?.id}');
    });
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  Future<void> _performAction(
    AnalysisActionState state,
    Future<void> Function() action,
  ) async {
    if (isActionBusy) return;
    _actionState = state;
    notifyListeners();
    try {
      await action();
    } catch (e) {
      debugPrint('[AnalysisProvider] action error: $e');
    } finally {
      _actionState = AnalysisActionState.idle;
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }
}
