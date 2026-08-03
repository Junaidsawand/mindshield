import 'package:flutter/material.dart';
import '../../domain/analysis_result.dart';

// ─────────────────────────────────────────────────────────────────────────────
// AttackTypeCard
// ─────────────────────────────────────────────────────────────────────────────

/// Card displaying the primary attack type classification and a list of
/// detected psychological manipulation tactics as icon-chip pairs.
class AttackTypeCard extends StatelessWidget {
  const AttackTypeCard({
    super.key,
    required this.attackType,
    required this.tactics,
  });

  final AttackType attackType;
  final List<PsychologicalTactic> tactics;

  Color _attackColor(AttackType t) {
    if (t == AttackType.benign) return const Color(0xFF2E7D32);
    return const Color(0xFFC62828);
  }

  IconData _attackIcon(AttackType t) {
    switch (t) {
      case AttackType.phishing:
      case AttackType.smishing:
        return Icons.phishing_rounded;
      case AttackType.vishing:
        return Icons.call_rounded;
      case AttackType.prizeScam:
        return Icons.emoji_events_rounded;
      case AttackType.investmentFraud:
        return Icons.trending_up_rounded;
      case AttackType.deliveryScam:
        return Icons.local_shipping_rounded;
      case AttackType.governmentImpersonation:
        return Icons.account_balance_rounded;
      case AttackType.cryptoScam:
        return Icons.currency_bitcoin_rounded;
      case AttackType.piiHarvesting:
        return Icons.fingerprint_rounded;
      case AttackType.malwareDistribution:
        return Icons.bug_report_rounded;
      case AttackType.benign:
        return Icons.verified_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final color = _attackColor(attackType);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Attack type ──────────────────────────────────────────────────────
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.07),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.2)),
          ),
          child: Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(_attackIcon(attackType), color: color, size: 22),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      attackType.label,
                      style: theme.textTheme.titleSmall!.copyWith(
                        fontWeight: FontWeight.w700,
                        color: color,
                      ),
                    ),
                    const SizedBox(height: 3),
                    Text(
                      attackType.description,
                      style: theme.textTheme.bodySmall!.copyWith(
                        color: cs.onSurface.withValues(alpha: 0.65),
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),

        // ── Psychological tactics ─────────────────────────────────────────
        if (tactics.isNotEmpty) ...[
          const SizedBox(height: 14),
          Text(
            'Psychological Manipulation Tactics',
            style: theme.textTheme.labelMedium!.copyWith(
              color: cs.onSurface.withValues(alpha: 0.6),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: tactics.map((t) => _TacticChip(tactic: t)).toList(),
          ),
        ] else ...[
          const SizedBox(height: 10),
          Row(
            children: [
              Icon(Icons.check_circle_rounded,
                  size: 15, color: const Color(0xFF2E7D32)),
              const SizedBox(width: 6),
              Text(
                'No psychological manipulation tactics detected.',
                style: theme.textTheme.bodySmall!.copyWith(
                  color: const Color(0xFF2E7D32),
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _TacticChip
// ─────────────────────────────────────────────────────────────────────────────

class _TacticChip extends StatelessWidget {
  const _TacticChip({required this.tactic});

  final PsychologicalTactic tactic;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: const Color(0xFFFF6F00).withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(
          color: const Color(0xFFFF6F00).withValues(alpha: 0.25),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(tactic.icon, style: const TextStyle(fontSize: 12)),
          const SizedBox(width: 5),
          Text(
            tactic.label,
            style: theme.textTheme.labelSmall!.copyWith(
              color: const Color(0xFFE65100),
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
