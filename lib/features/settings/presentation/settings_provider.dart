import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsProvider extends ChangeNotifier {
  final SharedPreferences _prefs;

  SettingsProvider(this._prefs) {
    _loadSettings();
  }

  // Default values
  bool _aiProtectionEnabled = true;
  bool _smsMonitoringEnabled = true;
  bool _notificationsEnabled = true;
  ThemeMode _themeMode = ThemeMode.system;
  String _scanSensitivity = 'Medium';

  // Getters
  bool get aiProtectionEnabled => _aiProtectionEnabled;
  bool get smsMonitoringEnabled => _smsMonitoringEnabled;
  bool get notificationsEnabled => _notificationsEnabled;
  ThemeMode get themeMode => _themeMode;
  String get scanSensitivity => _scanSensitivity;

  // Load settings from SharedPreferences
  void _loadSettings() {
    _aiProtectionEnabled = _prefs.getBool('aiProtection') ?? true;
    _smsMonitoringEnabled = _prefs.getBool('smsMonitoring') ?? true;
    _notificationsEnabled = _prefs.getBool('notifications') ?? true;
    
    final themeString = _prefs.getString('themeMode') ?? 'system';
    _themeMode = ThemeMode.values.firstWhere(
      (e) => e.toString() == 'ThemeMode.$themeString',
      orElse: () => ThemeMode.system,
    );

    _scanSensitivity = _prefs.getString('scanSensitivity') ?? 'Medium';
    notifyListeners();
  }

  // Setters
  Future<void> toggleAiProtection(bool value) async {
    _aiProtectionEnabled = value;
    await _prefs.setBool('aiProtection', value);
    notifyListeners();
  }

  Future<void> toggleSmsMonitoring(bool value) async {
    _smsMonitoringEnabled = value;
    await _prefs.setBool('smsMonitoring', value);
    notifyListeners();
  }

  Future<void> toggleNotifications(bool value) async {
    _notificationsEnabled = value;
    await _prefs.setBool('notifications', value);
    notifyListeners();
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    _themeMode = mode;
    await _prefs.setString('themeMode', mode.name);
    notifyListeners();
  }

  Future<void> setScanSensitivity(String sensitivity) async {
    _scanSensitivity = sensitivity;
    await _prefs.setString('scanSensitivity', sensitivity);
    notifyListeners();
  }
}
