import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'main_scaffold.dart';
import '../../features/splash/presentation/splash_screen.dart';
import '../../features/permissions/presentation/permissions_screen.dart';
import '../../features/dashboard/presentation/dashboard_screen.dart';
import '../../features/inbox/presentation/inbox_screen.dart';
import '../../features/inbox/domain/sms_message.dart';
import '../../features/spam/presentation/spam_screen.dart';
import '../../features/analysis/presentation/analysis_screen.dart';
import '../../features/history/presentation/history_screen.dart';
import '../../features/settings/presentation/settings_screen.dart';

/// All named route paths used throughout the app.
abstract class AppRoutes {
  static const String splash = '/';
  static const String permissions = '/permissions';
  static const String dashboard = '/dashboard';
  static const String inbox = '/inbox';
  static const String spam = '/spam';
  static const String analysis = '/analysis';
  static const String history = '/history';
  static const String settings = '/settings';
}

final GlobalKey<NavigatorState> _rootNavigatorKey =
    GlobalKey<NavigatorState>(debugLabel: 'root');

/// Application-level [GoRouter] configuration.
final GoRouter appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: AppRoutes.splash,
  debugLogDiagnostics: true,
  routes: [
    GoRoute(
      path: AppRoutes.splash,
      name: 'splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: AppRoutes.permissions,
      name: 'permissions',
      builder: (context, state) => const PermissionsScreen(),
    ),
    GoRoute(
      parentNavigatorKey: _rootNavigatorKey,
      path: AppRoutes.analysis,
      name: 'analysis',
      builder: (context, state) {
        final message = state.extra as SmsMessage?;
        return AnalysisScreen(message: message);
      },
    ),
    // Bottom Navigation with StatefulShellRoute
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) {
        return MainScaffold(navigationShell: navigationShell);
      },
      branches: [
        // Tab 1: Dashboard
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: AppRoutes.dashboard,
              name: 'dashboard',
              builder: (context, state) => const DashboardScreen(),
            ),
          ],
        ),
        // Tab 2: Inbox
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: AppRoutes.inbox,
              name: 'inbox',
              builder: (context, state) => const InboxScreen(),
            ),
          ],
        ),
        // Tab 3: Spam
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: AppRoutes.spam,
              name: 'spam',
              builder: (context, state) => const SpamScreen(),
            ),
          ],
        ),
        // Tab 4: History
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: AppRoutes.history,
              name: 'history',
              builder: (context, state) => const HistoryScreen(),
            ),
          ],
        ),
        // Tab 5: Settings
        StatefulShellBranch(
          routes: [
            GoRoute(
              path: AppRoutes.settings,
              name: 'settings',
              builder: (context, state) => const SettingsScreen(),
            ),
          ],
        ),
      ],
    ),
  ],
);
