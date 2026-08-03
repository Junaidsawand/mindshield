import 'package:flutter/material.dart';

// ─────────────────────────────────────────────────────────────────────────────
// ConfidenceBar
// ─────────────────────────────────────────────────────────────────────────────

/// Animated linear progress bar displaying the AI model's confidence
/// percentage. Animates from 0% to [confidencePercent] on first render.
class ConfidenceBar extends StatefulWidget {
  const ConfidenceBar({super.key, required this.confidencePercent});

  /// Confidence in the range 0–100.
  final int confidencePercent;

  @override
  State<ConfidenceBar> createState() => _ConfidenceBarState();
}

class _ConfidenceBarState extends State<ConfidenceBar>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );
    _anim = CurvedAnimation(parent: _ctrl, curve: Curves.easeOutCubic);
    _ctrl.forward();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Color _barColor(int pct) {
    if (pct >= 90) return const Color(0xFF1565C0);
    if (pct >= 70) return const Color(0xFF2E7D32);
    return const Color(0xFFF9A825);
  }

  String _confidenceLabel(int pct) {
    if (pct >= 90) return 'Very High';
    if (pct >= 75) return 'High';
    if (pct >= 60) return 'Moderate';
    return 'Low';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final color = _barColor(widget.confidencePercent);
    final label = _confidenceLabel(widget.confidencePercent);
    final fraction = widget.confidencePercent / 100;

    return AnimatedBuilder(
      animation: _anim,
      builder: (context, _) {
        final current = (_anim.value * widget.confidencePercent).round();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.psychology_rounded,
                      size: 16,
                      color: color,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Model Confidence',
                      style: theme.textTheme.labelMedium!.copyWith(
                        color: cs.onSurface.withValues(alpha: 0.7),
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Text(
                      label,
                      style: theme.textTheme.labelSmall!.copyWith(
                        color: color,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      '$current%',
                      style: theme.textTheme.titleMedium!.copyWith(
                        fontWeight: FontWeight.w800,
                        color: color,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            ClipRRect(
              borderRadius: BorderRadius.circular(100),
              child: LinearProgressIndicator(
                value: _anim.value * fraction,
                minHeight: 10,
                backgroundColor: cs.outlineVariant.withValues(alpha: 0.25),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'The AI model is $current% confident in this threat classification.',
              style: theme.textTheme.bodySmall!.copyWith(
                color: cs.onSurface.withValues(alpha: 0.5),
                height: 1.4,
              ),
            ),
          ],
        );
      },
    );
  }
}
