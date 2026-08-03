import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class NativeActionsService {
  NativeActionsService._();

  static const _channel = MethodChannel('com.mindshield/actions');

  /// Launches the default SMS application with the given phone number prefilled.
  static Future<void> launchSms(String number) async {
    try {
      await _channel.invokeMethod('launchSms', {'number': number});
    } catch (e) {
      debugPrint('NativeActionsService: Error launching SMS: $e');
    }
  }

  /// Launches the system dialer with the given phone number.
  static Future<void> launchDialer(String number) async {
    try {
      await _channel.invokeMethod('launchDialer', {'number': number});
    } catch (e) {
      debugPrint('NativeActionsService: Error launching dialer: $e');
    }
  }

  /// Opens the native Android share sheet with the given text.
  static Future<void> shareText(String text) async {
    try {
      await _channel.invokeMethod('shareText', {'text': text});
    } catch (e) {
      debugPrint('NativeActionsService: Error sharing text: $e');
    }
  }
}
