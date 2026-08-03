import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Splash screen – shown on cold start while boot checks run.
///
/// Displays the MindShield brand mark for [_kSplashDuration] then navigates
/// to the Permissions screen.  Future iterations will check
/// [AppConstants.prefKeyPermissionsGranted] via SharedPreferences and skip
/// straight to the Dashboard if all permissions were previously granted.
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  static const Duration _kSplashDuration = Duration(seconds: 2);

  late final AnimationController _controller;
  late final Animation<double> _fadeIn;

  @override
  void initState() {
    super.initState();

    // Fade-in the logo over 800 ms.
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeIn = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
    _controller.forward();

    // Navigate to Permissions after the splash duration.
    Future.delayed(_kSplashDuration, () {
      if (mounted) context.goNamed('permissions');
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Scaffold(
      backgroundColor: colorScheme.primary,
      body: FadeTransition(
        opacity: _fadeIn,
        child: const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.shield, size: 96, color: Colors.white),
              SizedBox(height: 16),
              Text(
                'MindShield',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 2,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'AI SMS Security',
                style: TextStyle(fontSize: 16, color: Colors.white70),
              ),
              SizedBox(height: 48),
              CircularProgressIndicator(color: Colors.white),
            ],
          ),
        ),
      ),
    );
  }
}
