import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'settings_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        centerTitle: true,
      ),
      body: Consumer<SettingsProvider>(
        builder: (context, provider, child) {
          return ListView(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 24.0),
            children: [
              _buildSectionHeader(context, 'Protection'),
              _buildProtectionCard(context, provider),
              const SizedBox(height: 24),
              _buildSectionHeader(context, 'Preferences'),
              _buildPreferencesCard(context, provider),
              const SizedBox(height: 24),
              _buildSectionHeader(context, 'Privacy & Data'),
              _buildPrivacyCard(context),
              const SizedBox(height: 24),
              _buildSectionHeader(context, 'About'),
              _buildAboutCard(context),
              const SizedBox(height: 32),
            ],
          );
        },
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0, left: 8.0),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
              color: Theme.of(context).colorScheme.primary,
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }

  Widget _buildProtectionCard(BuildContext context, SettingsProvider provider) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          SwitchListTile(
            title: const Text('AI Protection'),
            subtitle: const Text('Enable AI-based threat analysis'),
            value: provider.aiProtectionEnabled,
            onChanged: (value) => provider.toggleAiProtection(value),
            secondary: const Icon(Icons.security),
          ),
          const Divider(height: 1, indent: 56),
          SwitchListTile(
            title: const Text('SMS Monitoring'),
            subtitle: const Text('Automatically scan incoming messages'),
            value: provider.smsMonitoringEnabled,
            onChanged: (value) => provider.toggleSmsMonitoring(value),
            secondary: const Icon(Icons.sms_outlined),
          ),
          const Divider(height: 1, indent: 56),
          ListTile(
            title: const Text('Scan Sensitivity'),
            subtitle: const Text('Adjust how aggressively to block messages'),
            leading: const Icon(Icons.tune),
            trailing: DropdownButton<String>(
              value: provider.scanSensitivity,
              underline: const SizedBox(),
              items: ['Low', 'Medium', 'High'].map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              onChanged: (newValue) {
                if (newValue != null) {
                  provider.setScanSensitivity(newValue);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPreferencesCard(BuildContext context, SettingsProvider provider) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          SwitchListTile(
            title: const Text('Notifications'),
            subtitle: const Text('Alerts for threats and reports'),
            value: provider.notificationsEnabled,
            onChanged: (value) => provider.toggleNotifications(value),
            secondary: const Icon(Icons.notifications_none),
          ),
          const Divider(height: 1, indent: 56),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            child: Row(
              children: [
                const Icon(Icons.palette_outlined),
                const SizedBox(width: 16),
                const Expanded(child: Text('Theme')),
                SegmentedButton<ThemeMode>(
                  showSelectedIcon: false,
                  segments: const [
                    ButtonSegment<ThemeMode>(
                      value: ThemeMode.system,
                      label: Text('System'),
                    ),
                    ButtonSegment<ThemeMode>(
                      value: ThemeMode.light,
                      label: Text('Light'),
                    ),
                    ButtonSegment<ThemeMode>(
                      value: ThemeMode.dark,
                      label: Text('Dark'),
                    ),
                  ],
                  selected: {provider.themeMode},
                  onSelectionChanged: (Set<ThemeMode> newSelection) {
                    provider.setThemeMode(newSelection.first);
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPrivacyCard(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.block),
            title: const Text('Blocked Senders'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Blocked Senders coming soon')),
              );
            },
          ),
          const Divider(height: 1, indent: 56),
          ListTile(
            leading: const Icon(Icons.privacy_tip_outlined),
            title: const Text('Privacy & Permissions'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Privacy & Permissions coming soon')),
              );
            },
          ),
          const Divider(height: 1, indent: 56),
          ListTile(
            leading: const Icon(Icons.download_outlined),
            title: const Text('Export Data'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Data Export coming soon')),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAboutCard(BuildContext context) {
    return Card(
      elevation: 0,
      color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('About MindShield'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'MindShield',
                applicationVersion: '1.0.0+1',
                applicationLegalese: '© 2026 MindShield',
              );
            },
          ),
          const Divider(height: 1, indent: 56),
          const ListTile(
            leading: Icon(Icons.code),
            title: Text('App Version'),
            trailing: Text('1.0.0+1', style: TextStyle(color: Colors.grey)),
          ),
        ],
      ),
    );
  }
}
