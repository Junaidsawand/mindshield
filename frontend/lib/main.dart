import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/theme/app_theme.dart';
import 'core/router/app_router.dart';
import 'features/permissions/presentation/permissions_provider.dart';
import 'features/settings/presentation/settings_provider.dart';
import 'core/services/sms_background_service.dart';

import 'core/services/contacts_service.dart';
import 'features/dashboard/presentation/dashboard_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  
  // Start analysis sync for any pending SMS messages in background
  SmsBackgroundService.instance.syncPendingMessages();

  // Pre-fetch contacts if permission is already granted
  ContactsService.instance.fetchContacts();
  
  runApp(MindShieldApp(prefs: prefs));
}

/// Root widget of the MindShield application.
///
/// [MultiProvider] is placed here at the top of the widget tree so that all
/// feature-specific providers can be registered in one place as modules are
/// built out.  GoRouter is wired up via [MaterialApp.router].
class MindShieldApp extends StatelessWidget {
  final SharedPreferences prefs;

  const MindShieldApp({super.key, required this.prefs});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // ── Permissions module ─────────────────────────────────────────────
        ChangeNotifierProvider<PermissionsProvider>(
          create: (_) => PermissionsProvider(),
        ),
        // ── Settings module ─────────────────────────────────────────────
        ChangeNotifierProvider<SettingsProvider>(
          create: (_) => SettingsProvider(prefs),
        ),
        // ── Dashboard module ─────────────────────────────────────────────
        ChangeNotifierProvider<DashboardProvider>(
          create: (_) => DashboardProvider(),
        ),
      ],
      child: const _AppView(),
    );
  }
}

class _AppView extends StatelessWidget {
  const _AppView();

  @override
  Widget build(BuildContext context) {
    final settingsProvider = context.watch<SettingsProvider>();
    
    return MaterialApp.router(
      title: 'MindShield',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: settingsProvider.themeMode,
      routerConfig: appRouter,
    );
  }
}
