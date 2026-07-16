// lib/features/spam/presentation/widgets/spam_section_header.dart

import 'package:flutter/material.dart';
import '../../domain/spam_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SpamSectionHeader
// ─────────────────────────────────────────────────────────────────────────────

/// Sticky section header that separates quarantined messages by [SpamRiskLevel].
///
/// Displays:
/// * Colour-coded left border accent
/// * Risk level label + icon
/// * Short descriptive subtitle
/// * Message count badge
class SpamSectionHeader extends StatelessWidget {
  const SpamSectionHeader({
    super.key,
    required this.riskLevel,
    required this.count,
  });

  final SpamRiskLevel riskLevel;
  final int count;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final cfg = _config(riskLevel);

    return Container(
      color: cs.surface,
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Accent bar ────────────────────────────────────────────────
            Container(
              width: 4,
              height: 42,
              margin: const EdgeInsets.only(right: 12),
              decoration: BoxDecoration(
                color: cfg.color,
                borderRadius: BorderRadius.circular(4),
              ),
            ),

            // ── Labels ───────────────────────────────────────────────────
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(cfg.icon, size: 16, color: cfg.color),
                      const SizedBox(width: 6),
                      Text(
                        riskLevel.label,
                        style: theme.textTheme.titleSmall!.copyWith(
                          color: cfg.color,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 0.2,
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Count badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 7,
                          vertical: 1,
                        ),
                        decoration: BoxDecoration(
                          color: cfg.color.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(100),
                        ),
                        child: Text(
                          '$count',
                          style: theme.textTheme.labelSmall!.copyWith(
                            color: cfg.color,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    riskLevel.subtitle,
                    style: theme.textTheme.bodySmall!.copyWith(
                      color: cs.onSurface.withValues(alpha: 0.55),
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  _SectionConfig _config(SpamRiskLevel level) {
    switch (level) {
      case SpamRiskLevel.critical:
        return const _SectionConfig(
          color: Color(0xFFC62828),
          icon: Icons.dangerous_rounded,
        );
      case SpamRiskLevel.high:
        return const _SectionConfig(
          color: Color(0xFFE65100),
          icon: Icons.warning_rounded,
        );
      case SpamRiskLevel.medium:
        return const _SectionConfig(
          color: Color(0xFFF57F17),
          icon: Icons.info_outline_rounded,
        );
    }
  }
}

class _SectionConfig {
  const _SectionConfig({required this.color, required this.icon});
  final Color color;
  final IconData icon;
}
