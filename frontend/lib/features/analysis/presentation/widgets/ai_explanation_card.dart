import 'package:flutter/material.dart';

// ─────────────────────────────────────────────────────────────────────────────
// AiExplanationCard
// ─────────────────────────────────────────────────────────────────────────────

/// Displays the AI model's natural-language explanation of its analysis
/// reasoning with a typewriter-style fade-in animation.
class AiExplanationCard extends StatefulWidget {
  const AiExplanationCard({super.key, required this.explanation});

  final String explanation;

  @override
  State<AiExplanationCard> createState() => _AiExplanationCardState();
}

class _AiExplanationCardState extends State<AiExplanationCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 700),
    );
    _fadeAnim = CurvedAnimation(parent: _ctrl, curve: Curves.easeIn);
    // Brief delay so it appears after the gauge finishes.
    Future.delayed(const Duration(milliseconds: 600), () {
      if (mounted) _ctrl.forward();
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return FadeTransition(
      opacity: _fadeAnim,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── AI badge header ────────────────────────────────────────────────
          Row(
            children: [
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1565C0), Color(0xFF7B1FA2)],
                  ),
                  borderRadius: BorderRadius.circular(100),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.auto_awesome_rounded,
                        size: 13, color: Colors.white),
                    const SizedBox(width: 5),
                    Text(
                      'MindShield AI',
                      style: theme.textTheme.labelSmall!.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              Text(
                'Explanation',
                style: theme.textTheme.labelMedium!.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.5),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // ── Explanation text ───────────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF1565C0).withValues(alpha: 0.04),
                  const Color(0xFF7B1FA2).withValues(alpha: 0.04),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: const Color(0xFF1565C0).withValues(alpha: 0.15),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Quote icon
                const Icon(
                  Icons.format_quote_rounded,
                  size: 22,
                  color: Color(0xFF1565C0),
                ),
                const SizedBox(height: 6),
                Text(
                  widget.explanation,
                  style: theme.textTheme.bodyMedium!.copyWith(
                    height: 1.7,
                    color: cs.onSurface.withValues(alpha: 0.82),
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
