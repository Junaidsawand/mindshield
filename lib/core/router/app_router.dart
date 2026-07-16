import 'package:go_router/go_router.dart';
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

/// Application-level [GoRouter] configuration.
///
/// Redirect logic (e.g. skip splash once onboarding is done) will be
/// implemented in a later module once SharedPreferences is wired up.
final GoRouter appRouter = GoRouter(
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
      path: AppRoutes.dashboard,
      name: 'dashboard',
      builder: (context, state) => const DashboardScreen(),
    ),
    GoRoute(
      path: AppRoutes.inbox,
      name: 'inbox',
      builder: (context, state) => const InboxScreen(),
    ),
    GoRoute(
      path: AppRoutes.spam,
      name: 'spam',
      builder: (context, state) => const SpamScreen(),
    ),
    GoRoute(
      path: AppRoutes.analysis,
      name: 'analysis',
      builder: (context, state) {
        final message = state.extra as SmsMessage?;
        return AnalysisScreen(message: message);
      },
    ),
    GoRoute(
      path: AppRoutes.history,
      name: 'history',
      builder: (context, state) => const HistoryScreen(),
    ),
    GoRoute(
      path: AppRoutes.settings,
      name: 'settings',
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);
