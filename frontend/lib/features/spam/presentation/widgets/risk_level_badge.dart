// lib/features/spam/presentation/widgets/risk_level_badge.dart

import 'package:flutter/material.dart';
import '../../domain/spam_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// RiskLevelBadge
// ─────────────────────────────────────────────────────────────────────────────

/// Compact pill chip that colour-codes a [SpamRiskLevel].
///
/// Used inside spam message tiles and section headers.
class RiskLevelBadge extends StatelessWidget {
  const RiskLevelBadge({
    super.key,
    required this.riskLevel,
    this.compact = false,
  });

  final SpamRiskLevel riskLevel;

  /// When true, omits the icon – useful in very tight spaces.
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final cfg = _config(riskLevel);
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 8 : 10,
        vertical: compact ? 3 : 5,
      ),
      decoration: BoxDecoration(
        color: cfg.background,
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: cfg.border, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (!compact) ...[
            Icon(cfg.icon, size: 12, color: cfg.foreground),
            const SizedBox(width: 4),
          ],
          Text(
            riskLevel.label,
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: cfg.foreground,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.3,
                ),
          ),
        ],
      ),
    );
  }

  static _BadgeConfig _config(SpamRiskLevel level) {
    switch (level) {
      case SpamRiskLevel.critical:
        return const _BadgeConfig(
          background: Color(0xFFFFEBEE),
          border: Color(0xFFEF9A9A),
          foreground: Color(0xFFC62828),
          icon: Icons.dangerous_rounded,
        );
      case SpamRiskLevel.high:
        return const _BadgeConfig(
          background: Color(0xFFFFF3E0),
          border: Color(0xFFFFCC02),
          foreground: Color(0xFFE65100),
          icon: Icons.warning_rounded,
        );
      case SpamRiskLevel.medium:
        return const _BadgeConfig(
          background: Color(0xFFFFF8E1),
          border: Color(0xFFFFE082),
          foreground: Color(0xFFF57F17),
          icon: Icons.info_rounded,
        );
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// AttackTypeBadge
// ─────────────────────────────────────────────────────────────────────────────

/// Small outlined chip for the attack type label.
class AttackTypeBadge extends StatelessWidget {
  const AttackTypeBadge({super.key, required this.attackType});

  final AttackType attackType;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: cs.secondaryContainer.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: cs.outline.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.security_rounded, size: 11, color: cs.secondary),
          const SizedBox(width: 4),
          Text(
            attackType.label,
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: cs.secondary,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.2,
                ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SpamStatusChip
// ─────────────────────────────────────────────────────────────────────────────

/// Tiny chip indicating the lifecycle status of a spam message.
class SpamStatusChip extends StatelessWidget {
  const SpamStatusChip({super.key, required this.status});

  final SpamStatus status;

  @override
  Widget build(BuildContext context) {
    final (color, icon) = _style(status);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 10, color: color),
          const SizedBox(width: 3),
          Text(
            status.label,
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                  fontSize: 10,
                ),
          ),
        ],
      ),
    );
  }

  (Color, IconData) _style(SpamStatus s) {
    switch (s) {
      case SpamStatus.quarantined:
        return (const Color(0xFF1565C0), Icons.lock_rounded);
      case SpamStatus.reviewed:
        return (const Color(0xFF2E7D32), Icons.check_circle_rounded);
      case SpamStatus.blocked:
        return (const Color(0xFFC62828), Icons.block_rounded);
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
