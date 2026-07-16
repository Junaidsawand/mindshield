import 'package:flutter/material.dart';
import '../../domain/analysis_result.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SenderInfoCard
// ─────────────────────────────────────────────────────────────────────────────

/// Displays enriched sender metadata: phone number, country, carrier, line
/// type, first-seen date, report count, and known-scammer badge.
class SenderInfoCard extends StatelessWidget {
  const SenderInfoCard({super.key, required this.senderInfo});

  final SenderInfo senderInfo;

  String _formatDate(DateTime d) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    return '${d.day} ${months[d.month - 1]} ${d.year}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final isScammer = senderInfo.isKnownScammer;
    final accentColor =
        isScammer ? const Color(0xFFC62828) : const Color(0xFF2E7D32);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Sender header ─────────────────────────────────────────────────
        Row(
          children: [
            // Avatar
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: accentColor.withValues(alpha: 0.1),
                shape: BoxShape.circle,
                border: Border.all(
                  color: accentColor.withValues(alpha: 0.3),
                  width: 2,
                ),
              ),
              child: Center(
                child: Text(
                  _countryFlag(senderInfo.countryCode),
                  style: const TextStyle(fontSize: 24),
                ),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    senderInfo.displayName,
                    style: theme.textTheme.titleSmall!.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    senderInfo.phoneNumber,
                    style: theme.textTheme.bodySmall!.copyWith(
                      color: cs.onSurface.withValues(alpha: 0.55),
                      fontFamily: 'monospace',
                    ),
                  ),
                ],
              ),
            ),
            // Known scammer / safe badge
            _StatusBadge(isScammer: isScammer),
          ],
        ),

        const SizedBox(height: 16),

        // ── Info grid ─────────────────────────────────────────────────────
        _InfoGrid(senderInfo: senderInfo, formatDate: _formatDate),

        // ── Report count bar ──────────────────────────────────────────────
        if (senderInfo.reportCount > 0) ...[
          const SizedBox(height: 14),
          _ReportCountRow(reportCount: senderInfo.reportCount),
        ],
      ],
    );
  }

  String _countryFlag(String code) {
    if (code.length != 2) return '🌐';
    final base = 0x1F1E6 - 0x41;
    return String.fromCharCodes(
      code.toUpperCase().codeUnits.map((c) => base + c),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _StatusBadge
// ─────────────────────────────────────────────────────────────────────────────

class _StatusBadge extends StatelessWidget {
  const _StatusBadge({required this.isScammer});

  final bool isScammer;

  @override
  Widget build(BuildContext context) {
    final color =
        isScammer ? const Color(0xFFC62828) : const Color(0xFF2E7D32);
    final label = isScammer ? 'Known Threat' : 'Clean Record';
    final icon = isScammer ? Icons.gpp_bad_rounded : Icons.gpp_good_rounded;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: color,
                  fontWeight: FontWeight.w700,
                ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _InfoGrid
// ─────────────────────────────────────────────────────────────────────────────

class _InfoGrid extends StatelessWidget {
  const _InfoGrid({required this.senderInfo, required this.formatDate});

  final SenderInfo senderInfo;
  final String Function(DateTime) formatDate;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        _InfoChip(
          icon: Icons.public_rounded,
          label: '${senderInfo.countryName} (${senderInfo.countryCode})',
        ),
        if (senderInfo.carrierName != null)
          _InfoChip(
            icon: Icons.signal_cellular_alt_rounded,
            label: senderInfo.carrierName!,
          ),
        if (senderInfo.lineType != null)
          _InfoChip(
            icon: Icons.phone_rounded,
            label: senderInfo.lineType!,
          ),
        _InfoChip(
          icon: Icons.history_rounded,
          label: 'First seen: ${formatDate(senderInfo.firstSeenDate)}',
        ),
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  const _InfoChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHigh,
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: cs.onSurface.withValues(alpha: 0.55)),
          const SizedBox(width: 5),
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.75),
                  fontWeight: FontWeight.w500,
                ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ReportCountRow
// ─────────────────────────────────────────────────────────────────────────────

class _ReportCountRow extends StatelessWidget {
  const _ReportCountRow({required this.reportCount});

  final int reportCount;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final severity = reportCount > 1000
        ? const Color(0xFFC62828)
        : reportCount > 100
            ? const Color(0xFFE65100)
            : const Color(0xFFF9A825);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: severity.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: severity.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          Icon(Icons.people_rounded, size: 18, color: severity),
          const SizedBox(width: 10),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: theme.textTheme.bodySmall!.copyWith(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.75),
                ),
                children: [
                  TextSpan(
                    text: '$reportCount users ',
                    style: TextStyle(
                      color: severity,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const TextSpan(
                    text: 'have reported this number in the MindShield threat network.',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
