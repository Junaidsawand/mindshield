// lib/features/spam/presentation/widgets/confidence_indicator.dart

import 'package:flutter/material.dart';

// ─────────────────────────────────────────────────────────────────────────────
// ConfidenceIndicator
// ─────────────────────────────────────────────────────────────────────────────

/// Compact horizontal progress bar with a percentage label that visualises
/// the AI model's confidence score for a quarantined message.
///
/// The bar colour transitions from amber (low confidence) to red (high
/// confidence) to reinforce the severity semantics.
class ConfidenceIndicator extends StatelessWidget {
  const ConfidenceIndicator({
    super.key,
    required this.confidence,
  });

  /// AI confidence score in range 0.0–1.0.
  final double confidence;

  @override
  Widget build(BuildContext context) {
    final pct = (confidence * 100).round();
    final barColor = _barColor(confidence);

    return Row(
      children: [
        // Label
        Text(
          'AI Confidence',
          style: Theme.of(context).textTheme.labelSmall!.copyWith(
                color:
                    Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                fontSize: 10,
              ),
        ),
        const SizedBox(width: 8),
        // Progress bar
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: confidence,
              minHeight: 6,
              backgroundColor: barColor.withValues(alpha: 0.12),
              valueColor: AlwaysStoppedAnimation<Color>(barColor),
            ),
          ),
        ),
        const SizedBox(width: 6),
        // Percentage
        Text(
          '$pct%',
          style: Theme.of(context).textTheme.labelSmall!.copyWith(
                color: barColor,
                fontWeight: FontWeight.w700,
                fontSize: 11,
              ),
        ),
      ],
    );
  }

  Color _barColor(double value) {
    if (value >= 0.9) return const Color(0xFFC62828); // critical red
    if (value >= 0.7) return const Color(0xFFE65100); // high orange
    return const Color(0xFFF57F17); // medium amber
  }
}
