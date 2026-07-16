import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import '../database/database_helper.dart';
import 'analysis_service.dart';

class SmsBackgroundService {
  static final SmsBackgroundService instance = SmsBackgroundService._();
  SmsBackgroundService._() {
    _channel.setMethodCallHandler(_handleMethodCall);
  }

  static const _channel = MethodChannel('com.mindshield/sms_receiver');
  
  final List<VoidCallback> _listeners = [];

  /// Add a listener to get notified when database updates occur (e.g., after SMS is received/analyzed).
  void addListener(VoidCallback listener) {
    if (!_listeners.contains(listener)) {
      _listeners.add(listener);
    }
  }

  /// Remove a registered listener.
  void removeListener(VoidCallback listener) {
    _listeners.remove(listener);
  }

  /// Iterates and notifies all listeners to refresh their local states.
  void notifyListeners() {
    for (final listener in _listeners) {
      try {
        listener();
      } catch (e) {
        debugPrint('SmsBackgroundService: Error calling listener: $e');
      }
    }
  }

  /// Method channel call handler for background Android events.
  Future<void> _handleMethodCall(MethodCall call) async {
    switch (call.method) {
      case 'onSmsReceived':
        final Map<dynamic, dynamic>? args = call.arguments as Map<dynamic, dynamic>?;
        if (args == null) return;

        final String id = args['id'] as String? ?? '';
        final String sender = args['sender'] as String? ?? '';
        final String body = args['body'] as String? ?? '';

        debugPrint('SmsBackgroundService: Intercepted incoming SMS ($id) from $sender. Triggering analysis...');

        // Notify UI immediately so that the "Analyzing..." state is shown
        notifyListeners();

        // Run analysis in background (Centralized Dart analysis flow)
        _runAnalysisAndRefresh(id: id, sender: sender, body: body);
        break;
      default:
        debugPrint('SmsBackgroundService: Unknown method ${call.method}');
    }
  }

  /// Run analysis asynchronously and notify when done
  Future<void> _runAnalysisAndRefresh({
    required String id,
    required String sender,
    required String body,
  }) async {
    try {
      await AnalysisService.instance.analyzeMessage(id: id, sender: sender, body: body);
    } catch (e, st) {
      debugPrint('SmsBackgroundService: Analysis failed for $id: $e');
      debugPrintStack(stackTrace: st);
    } finally {
      // Re-notify UI so it changes from "Analyzing..." to the final verdict
      notifyListeners();
    }
  }

  /// Scans the database for any 'pending' messages (e.g. received when the app was closed)
  /// and runs them through the AnalysisService.
  Future<void> syncPendingMessages() async {
    debugPrint('SmsBackgroundService: Syncing pending messages from database...');
    try {
      final pendingRows = await DatabaseHelper.instance.queryPendingMessages();
      if (pendingRows.isEmpty) {
        debugPrint('SmsBackgroundService: No pending messages found.');
        return;
      }

      debugPrint('SmsBackgroundService: Found ${pendingRows.length} pending messages to analyze.');
      for (final row in pendingRows) {
        final String id = row['id'] as String;
        final String sender = row['sender'] as String;
        final String body = row['body'] as String;

        // Perform analysis
        await AnalysisService.instance.analyzeMessage(id: id, sender: sender, body: body);
      }
      debugPrint('SmsBackgroundService: Sync completed.');
      notifyListeners();
    } catch (e, st) {
      debugPrint('SmsBackgroundService: Sync error: $e');
      debugPrintStack(stackTrace: st);
    }
  }
}
