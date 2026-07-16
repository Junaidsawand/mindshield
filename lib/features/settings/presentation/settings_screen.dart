import 'package:flutter/material.dart';

/// Settings screen – allows the user to configure app behaviour:
/// theme mode (light/dark/system), notification preferences,
/// spam threshold, and data-clearing options.
///
/// Will later be driven by a [SettingsProvider] backed by SharedPreferences.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.settings, size: 64),
            SizedBox(height: 16),
            Text(
              'Settings Screen',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 8),
            Text('— Placeholder —', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
