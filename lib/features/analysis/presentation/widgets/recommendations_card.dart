import 'package:flutter/material.dart';

// ─────────────────────────────────────────────────────────────────────────────
// RecommendationsCard
// ─────────────────────────────────────────────────────────────────────────────

/// Numbered recommendations list rendered with staggered slide-in animations.
class RecommendationsCard extends StatefulWidget {
  const RecommendationsCard({super.key, required this.recommendations});

  final List<String> recommendations;

  @override
  State<RecommendationsCard> createState() => _RecommendationsCardState();
}

class _RecommendationsCardState extends State<RecommendationsCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  final List<Animation<Offset>> _slideAnims = [];
  final List<Animation<double>> _fadeAnims = [];

  @override
  void initState() {
    super.initState();
    final count = widget.recommendations.length;
    _ctrl = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 400 + count * 120),
    );

    for (int i = 0; i < count; i++) {
      final start = (i / (count + 1)).clamp(0.0, 1.0);
      final end = ((i + 1) / (count + 1)).clamp(0.0, 1.0);
      final interval = Interval(start, end, curve: Curves.easeOut);
      _slideAnims.add(
        Tween<Offset>(begin: const Offset(0.3, 0), end: Offset.zero)
            .animate(CurvedAnimation(parent: _ctrl, curve: interval)),
      );
      _fadeAnims.add(
        CurvedAnimation(parent: _ctrl, curve: interval),
      );
    }

    Future.delayed(const Duration(milliseconds: 300), () {
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

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: widget.recommendations.asMap().entries.map((entry) {
        final i = entry.key;
        final tip = entry.value;
        return SlideTransition(
          position: _slideAnims[i],
          child: FadeTransition(
            opacity: _fadeAnims[i],
            child: Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Numbered circle
                  Container(
                    width: 26,
                    height: 26,
                    decoration: BoxDecoration(
                      color: cs.primaryContainer,
                      shape: BoxShape.circle,
                    ),
                    child: Center(
                      child: Text(
                        '${i + 1}',
                        style: theme.textTheme.labelSmall!.copyWith(
                          color: cs.onPrimaryContainer,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        tip,
                        style: theme.textTheme.bodySmall!.copyWith(
                          height: 1.5,
                          color: cs.onSurface.withValues(alpha: 0.82),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
