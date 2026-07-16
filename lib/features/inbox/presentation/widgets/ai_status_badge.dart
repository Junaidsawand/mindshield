import 'package:flutter/material.dart';
import '../../domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// AiStatusBadge
// ─────────────────────────────────────────────────────────────────────────────

/// Compact chip that displays an [AiStatus] label with a colour-coded
/// background and icon. Designed to fit inside a message list tile.
class AiStatusBadge extends StatelessWidget {
  const AiStatusBadge({
    super.key,
    required this.status,
    this.compact = false,
  });

  /// The AI classification to display.
  final AiStatus status;

  /// When [compact] is true the icon is omitted, useful in very tight spaces.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final config = _config(context, status);
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 8 : 10,
        vertical: compact ? 3 : 5,
      ),
      decoration: BoxDecoration(
        color: config.background,
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: config.border, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (!compact) ...[
            Icon(config.icon, size: 12, color: config.foreground),
            const SizedBox(width: 4),
          ],
          Text(
            status.label,
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: config.foreground,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.3,
                ),
          ),
        ],
      ),
    );
  }

  static _BadgeConfig _config(BuildContext context, AiStatus status) {
    switch (status) {
      case AiStatus.safe:
        return _BadgeConfig(
          background: const Color(0xFFE8F5E9),
          border: const Color(0xFFA5D6A7),
          foreground: const Color(0xFF2E7D32),
          icon: Icons.verified_rounded,
        );
      case AiStatus.suspicious:
        return _BadgeConfig(
          background: const Color(0xFFFFF8E1),
          border: const Color(0xFFFFE082),
          foreground: const Color(0xFFE65100),
          icon: Icons.warning_amber_rounded,
        );
      case AiStatus.scam:
        return _BadgeConfig(
          background: const Color(0xFFFFEBEE),
          border: const Color(0xFFEF9A9A),
          foreground: const Color(0xFFC62828),
          icon: Icons.dangerous_rounded,
        );
    }
  }
}

class _BadgeConfig {
  const _BadgeConfig({
    required this.background,
    required this.border,
    required this.foreground,
    required this.icon,
  });
  final Color background;
  final Color border;
  final Color foreground;
  final IconData icon;
}
