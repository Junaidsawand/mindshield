import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:permission_handler/permission_handler.dart';

class ContactsService {
  ContactsService._();

  static final ContactsService instance = ContactsService._();

  static const _channel = MethodChannel('com.mindshield/contacts');

  // Cache: normalized number -> display name
  final Map<String, String> _cache = {};

  /// Normalizes a phone number to match the database and native query format.
  String _normalize(String sender) {
    return sender.replaceAll(RegExp(r'[\s\-()]+'), '').toLowerCase();
  }

  /// Fetches all contacts from the Android Contacts Provider via MethodChannel.
  Future<void> fetchContacts() async {
    try {
      final status = await Permission.contacts.status;
      if (status.isGranted) {
        final result = await _channel.invokeMethod<Map<dynamic, dynamic>>('fetchContacts');
        if (result != null) {
          _cache.clear();
          result.forEach((key, value) {
            if (key is String && value is String) {
              _cache[key] = value;
            }
          });
        }
      }
    } on PlatformException catch (e) {
      // Graceful fallback: do nothing, display raw numbers
      debugPrint('ContactsService: PlatformException calling fetchContacts: $e');
    } catch (e) {
      debugPrint('ContactsService: Error fetching contacts: $e');
    }
  }

  /// Returns the contact name if cached; otherwise returns the original number/sender.
  String getDisplayName(String sender) {
    final normalized = _normalize(sender);
    return _cache[normalized] ?? sender;
  }
}
