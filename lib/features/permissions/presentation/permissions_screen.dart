import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:provider/provider.dart';
import '../../../core/router/app_router.dart';
import 'permissions_provider.dart';

// ─────────────────────────────────────────────────────────────────────────────
// PermissionsScreen
// ─────────────────────────────────────────────────────────────────────────────

/// Full-screen onboarding surface that requests SMS-related runtime permissions.
///
/// The screen is driven entirely by [PermissionsProvider].  It:
///
/// * Calls [PermissionsProvider.checkStatuses] on first build via [initState]
///   so it reflects any permissions previously granted in an earlier session.
/// * Registers as a [WidgetsBindingObserver] to detect when the user returns
///   from the OS App Settings page, at which point statuses are re-queried.
/// * Listens to [PermissionsProvider.allGranted] via a post-frame callback and
///   navigates to [AppRoutes.dashboard] as soon as all required permissions
///   are granted.
///
/// Layout anatomy
/// ──────────────
/// ```
/// Scaffold
/// └── CustomScrollView
///     ├── SliverAppBar (collapsing hero)
///     │   └── FlexibleSpaceBar (shield gradient + title)
///     └── SliverList
///         ├── _IntroText          — subtitle & description
///         ├── _PermissionCard × N — one per PermissionItem
///         └── _ActionButtons      — Grant / Open Settings CTAs
/// ```
class PermissionsScreen extends StatefulWidget {
  const PermissionsScreen({super.key});

  @override
  State<PermissionsScreen> createState() => _PermissionsScreenState();
}

class _PermissionsScreenState extends State<PermissionsScreen>
    with WidgetsBindingObserver {
  // Flag: have we already navigated away? Prevents double-navigation in edge cases.
  bool _navigated = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    // Query current statuses without triggering the OS dialog.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PermissionsProvider>().checkStatuses();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  // Re-query statuses whenever the user returns from the OS Settings page.
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      context.read<PermissionsProvider>().checkStatuses();
    }
  }

  void _maybeNavigate(PermissionsProvider provider) {
    if (!_navigated && provider.allGranted && mounted) {
      _navigated = true;
      // Navigate AFTER the current build frame to avoid modifying the tree mid-build.
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) context.goNamed('dashboard');
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PermissionsProvider>();
    // React to allGranted change.
    _maybeNavigate(provider);

    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // ── Collapsing hero header ──────────────────────────────────────
          SliverAppBar(
            expandedHeight: 240,
            pinned: true,
            backgroundColor: colorScheme.primary,
            flexibleSpace: FlexibleSpaceBar(
              collapseMode: CollapseMode.parallax,
              background: _HeroBackground(colorScheme: colorScheme),
              titlePadding: const EdgeInsetsDirectional.only(
                start: 20,
                bottom: 16,
              ),
              title: Text(
                'App Permissions',
                style: textTheme.titleLarge?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                ),
              ),
            ),
          ),

          // ── Body content ────────────────────────────────────────────────
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                const SizedBox(height: 24),

                // Intro text block.
                _IntroText(textTheme: textTheme),

                const SizedBox(height: 24),

                // One card per permission.
                ...PermissionsProvider.permissionItems.map(
                  (item) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _PermissionCard(
                      item: item,
                      status: provider.statusOf(item),
                      colorScheme: colorScheme,
                      textTheme: textTheme,
                    ),
                  ),
                ),

                const SizedBox(height: 8),

                // Error message (if any).
                if (provider.errorMessage != null)
                  _ErrorBanner(message: provider.errorMessage!),

                const SizedBox(height: 16),

                // CTA buttons.
                _ActionButtons(provider: provider),

                const SizedBox(height: 40),
              ]),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _HeroBackground
// ─────────────────────────────────────────────────────────────────────────────

class _HeroBackground extends StatelessWidget {
  const _HeroBackground({required this.colorScheme});
  final ColorScheme colorScheme;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            colorScheme.primary,
            colorScheme.tertiary,
          ],
        ),
      ),
      child: SafeArea(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SizedBox(height: 16),
            // Glassmorphic circle behind the shield icon.
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: Colors.white.withAlpha(38), // ~15 % opacity
                border: Border.all(
                  color: Colors.white.withAlpha(77), // ~30 % opacity
                  width: 1.5,
                ),
              ),
              child: const Icon(
                Icons.security_rounded,
                size: 52,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'MindShield',
              style: const TextStyle(
                fontSize: 13,
                color: Colors.white70,
                letterSpacing: 3,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _IntroText
// ─────────────────────────────────────────────────────────────────────────────

class _IntroText extends StatelessWidget {
  const _IntroText({required this.textTheme});
  final TextTheme textTheme;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Grant access to protect you',
          style: textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'MindShield needs the following permissions to scan your messages '
          'for phishing attempts and scam patterns. Your data never leaves '
          'your device without your explicit consent.',
          style: textTheme.bodyMedium?.copyWith(
            height: 1.55,
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _PermissionCard
// ─────────────────────────────────────────────────────────────────────────────

/// Material 3 card showing one permission's icon, title, rationale, and status.
class _PermissionCard extends StatelessWidget {
  const _PermissionCard({
    required this.item,
    required this.status,
    required this.colorScheme,
    required this.textTheme,
  });

  final PermissionItem item;
  final PermissionStatus status;
  final ColorScheme colorScheme;
  final TextTheme textTheme;

  // Map icon string → IconData.
  static const _iconMap = {
    'message': Icons.message_rounded,
    'inbox': Icons.move_to_inbox_rounded,
    'phone_in_talk': Icons.phone_in_talk_rounded,
    'contacts': Icons.contacts_rounded,
  };

  @override
  Widget build(BuildContext context) {
    final iconData = _iconMap[item.icon] ?? Icons.lock_outline_rounded;
    final chipConfig = _resolveChip(status, colorScheme);

    return Card(
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon container.
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: item.required
                    ? colorScheme.primaryContainer
                    : colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                iconData,
                color: item.required
                    ? colorScheme.onPrimaryContainer
                    : colorScheme.onSurfaceVariant,
                size: 26,
              ),
            ),
            const SizedBox(width: 14),

            // Text + chip column.
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          item.title,
                          style: textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Optional badge.
                      if (!item.required)
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 7,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            'Optional',
                            style: textTheme.labelSmall?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    item.rationale,
                    style: textTheme.bodySmall?.copyWith(height: 1.5),
                  ),
                  const SizedBox(height: 10),

                  // Status chip.
                  _StatusChip(config: chipConfig, textTheme: textTheme),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Resolve chip label + colours based on [PermissionStatus].
  _ChipConfig _resolveChip(PermissionStatus s, ColorScheme cs) {
    if (s.isGranted) {
      return _ChipConfig(
        label: 'Granted',
        icon: Icons.check_circle_outline_rounded,
        backgroundColor: const Color(0xFF1B5E20).withAlpha(25),
        foregroundColor: const Color(0xFF2E7D32),
      );
    }
    if (s.isPermanentlyDenied) {
      return _ChipConfig(
        label: 'Permanently Denied',
        icon: Icons.block_rounded,
        backgroundColor: cs.errorContainer,
        foregroundColor: cs.onErrorContainer,
      );
    }
    if (s.isDenied) {
      return _ChipConfig(
        label: 'Not Granted',
        icon: Icons.radio_button_unchecked_rounded,
        backgroundColor: const Color(0xFFE65100).withAlpha(20),
        foregroundColor: const Color(0xFFBF360C),
      );
    }
    // Restricted / limited / provisional → neutral.
    return _ChipConfig(
      label: 'Restricted',
      icon: Icons.info_outline_rounded,
      backgroundColor: cs.surfaceContainerHighest,
      foregroundColor: cs.onSurfaceVariant,
    );
  }
}

/// Simple value class carrying chip presentation data.
class _ChipConfig {
  const _ChipConfig({
    required this.label,
    required this.icon,
    required this.backgroundColor,
    required this.foregroundColor,
  });
  final String label;
  final IconData icon;
  final Color backgroundColor;
  final Color foregroundColor;
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.config, required this.textTheme});
  final _ChipConfig config;
  final TextTheme textTheme;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: config.backgroundColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(config.icon, size: 14, color: config.foregroundColor),
          const SizedBox(width: 4),
          Text(
            config.label,
            style: textTheme.labelSmall?.copyWith(
              color: config.foregroundColor,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ErrorBanner
// ─────────────────────────────────────────────────────────────────────────────

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});
  final String message;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: cs.errorContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: cs.onErrorContainer),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: cs.onErrorContainer,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ActionButtons
// ─────────────────────────────────────────────────────────────────────────────

/// Renders the primary CTA (Grant Permissions) and, when needed,
/// a secondary CTA (Open Settings) for permanently denied permissions.
class _ActionButtons extends StatelessWidget {
  const _ActionButtons({required this.provider});
  final PermissionsProvider provider;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // ── Primary: Grant / Loading ───────────────────────────────────────
        FilledButton.icon(
          onPressed: provider.isLoading || provider.allGranted
              ? null
              : () => provider.requestAll(),
          icon: provider.isLoading
              ? SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: cs.onPrimary,
                  ),
                )
              : Icon(
                  provider.allGranted
                      ? Icons.check_circle_rounded
                      : Icons.lock_open_rounded,
                ),
          label: Text(
            provider.isLoading
                ? 'Requesting…'
                : provider.allGranted
                    ? 'All Permissions Granted'
                    : 'Grant Permissions',
          ),
          style: FilledButton.styleFrom(
            minimumSize: const Size.fromHeight(52),
          ),
        ),

        // ── Secondary: Open Settings (only if permanentlyDenied) ──────────
        if (provider.hasPermanentlyDenied) ...[
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () => provider.openSettings(),
            icon: const Icon(Icons.settings_rounded),
            label: const Text('Open App Settings'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size.fromHeight(52),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'One or more permissions were permanently denied. '
            'Tap "Open App Settings" and enable them manually.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: cs.error,
                  height: 1.5,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ],
    );
  }
}
