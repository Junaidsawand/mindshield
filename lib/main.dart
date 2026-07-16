import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'core/router/app_router.dart';
import 'features/permissions/presentation/permissions_provider.dart';
// InboxProvider is scoped to InboxScreen and created locally there.

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MindShieldApp());
}

/// Root widget of the MindShield application.
///
/// [MultiProvider] is placed here at the top of the widget tree so that all
/// feature-specific providers can be registered in one place as modules are
/// built out.  GoRouter is wired up via [MaterialApp.router].
class MindShieldApp extends StatelessWidget {
  const MindShieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // ── Permissions module ─────────────────────────────────────────────
        ChangeNotifierProvider<PermissionsProvider>(
          create: (_) => PermissionsProvider(),
        ),
        // Future feature providers will be registered here.
        // Example:
        // ChangeNotifierProvider(create: (_) => DashboardProvider()),
      ],
      child: const _AppView(),
    );
  }
}

class _AppView extends StatelessWidget {
  const _AppView();

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'MindShield',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      routerConfig: appRouter,
    );
  }
}
