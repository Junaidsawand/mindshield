import 'package:flutter/material.dart';
import '../../domain/analysis_result.dart';

// ─────────────────────────────────────────────────────────────────────────────
// LimeHighlightCard
// ─────────────────────────────────────────────────────────────────────────────

/// Displays the full message body with suspicious keywords highlighted using
/// colour intensity proportional to their LIME importance weight.
///
/// This is a placeholder for the real LIME (Local Interpretable Model-Agnostic
/// Explanations) integration. In production, keyword spans would be computed
/// server-side and returned with character offsets.
class LimeHighlightCard extends StatelessWidget {
  const LimeHighlightCard({
    super.key,
    required this.messageBody,
    required this.keywords,
  });

  final String messageBody;
  final List<SuspiciousKeyword> keywords;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Legend ───────────────────────────────────────────────────────────
        if (keywords.isNotEmpty) ...[
          _LimeLegend(),
          const SizedBox(height: 10),
        ],

        // ── Highlighted text ─────────────────────────────────────────────────
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: cs.surfaceContainerLow,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.4)),
          ),
          child: _buildHighlightedText(context),
        ),

        // ── Keyword list ─────────────────────────────────────────────────────
        if (keywords.isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(
            'LIME Feature Importance',
            style: theme.textTheme.labelMedium!.copyWith(
              color: cs.onSurface.withValues(alpha: 0.6),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          ...keywords.map((kw) => _KeywordRow(keyword: kw)),
        ],

        if (keywords.isEmpty) ...[
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.check_circle_outline_rounded,
                  size: 15, color: const Color(0xFF2E7D32)),
              const SizedBox(width: 6),
              Text(
                'No suspicious keywords identified.',
                style: theme.textTheme.bodySmall!.copyWith(
                  color: const Color(0xFF2E7D32),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  Widget _buildHighlightedText(BuildContext context) {
    if (keywords.isEmpty) {
      return Text(
        messageBody,
        style: Theme.of(context).textTheme.bodyMedium!.copyWith(height: 1.6),
      );
    }

    final spans = <TextSpan>[];
    int offset = 0;

    // Sort keywords by their position in the text (case-insensitive search).
    final sorted = List<SuspiciousKeyword>.from(keywords)
      ..sort((a, b) {
        final ia = messageBody.toLowerCase().indexOf(a.word.toLowerCase());
        final ib = messageBody.toLowerCase().indexOf(b.word.toLowerCase());
        return ia.compareTo(ib);
      });

    final lower = messageBody.toLowerCase();

    for (final kw in sorted) {
      final idx = lower.indexOf(kw.word.toLowerCase(), offset);
      if (idx == -1) continue;

      // Text before the keyword
      if (idx > offset) {
        spans.add(TextSpan(
          text: messageBody.substring(offset, idx),
          style: TextStyle(
            color:
                Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.85),
            height: 1.6,
          ),
        ));
      }

      // Highlighted keyword
      final intensity = (kw.weight * 0.35).clamp(0.08, 0.35);
      spans.add(TextSpan(
        text: messageBody.substring(idx, idx + kw.word.length),
        style: TextStyle(
          backgroundColor:
              const Color(0xFFFF6F00).withValues(alpha: intensity),
          color: const Color(0xFFBF360C),
          fontWeight: FontWeight.w700,
          height: 1.6,
          decoration: TextDecoration.underline,
          decorationColor: const Color(0xFFBF360C).withValues(alpha: 0.5),
          decorationStyle: TextDecorationStyle.dotted,
        ),
      ));

      offset = idx + kw.word.length;
    }

    // Remaining text after last keyword
    if (offset < messageBody.length) {
      spans.add(TextSpan(
        text: messageBody.substring(offset),
        style: TextStyle(
          color:
              Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.85),
          height: 1.6,
        ),
      ));
    }

    return RichText(
      text: TextSpan(
        children: spans,
        style: Theme.of(context).textTheme.bodyMedium,
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _LimeLegend
// ─────────────────────────────────────────────────────────────────────────────

class _LimeLegend extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: const Color(0xFFFF6F00).withValues(alpha: 0.25),
            borderRadius: BorderRadius.circular(3),
            border: Border.all(
              color: const Color(0xFFBF360C).withValues(alpha: 0.4),
            ),
          ),
        ),
        const SizedBox(width: 6),
        Text(
          'Highlighted = suspicious keyword (LIME weight)',
          style: theme.textTheme.labelSmall!.copyWith(
            color: theme.colorScheme.onSurface.withValues(alpha: 0.55),
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _KeywordRow
// ─────────────────────────────────────────────────────────────────────────────

class _KeywordRow extends StatelessWidget {
  const _KeywordRow({required this.keyword});

  final SuspiciousKeyword keyword;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final pct = (keyword.weight * 100).round();

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Weight indicator bar
          Column(
            children: [
              const SizedBox(height: 2),
              Container(
                width: 4,
                height: 36,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  color: const Color(0xFFFF6F00).withValues(alpha: 0.15),
                ),
                alignment: Alignment.bottomCenter,
                child: FractionallySizedBox(
                  heightFactor: keyword.weight,
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(4),
                      color: const Color(0xFFE65100),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        '"${keyword.word}"',
                        style: theme.textTheme.labelMedium!.copyWith(
                          color: const Color(0xFFBF360C),
                          fontWeight: FontWeight.w700,
                          fontStyle: FontStyle.italic,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 7, vertical: 2),
                      decoration: BoxDecoration(
                        color:
                            const Color(0xFFE65100).withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: Text(
                        '$pct%',
                        style: theme.textTheme.labelSmall!.copyWith(
                          color: const Color(0xFFE65100),
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  keyword.reason,
                  style: theme.textTheme.bodySmall!.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.6),
                    height: 1.4,
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
