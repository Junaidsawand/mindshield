import 'package:flutter/material.dart';
import '../../domain/analysis_result.dart';
import '../../../../core/services/contacts_service.dart';

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
    final displayName = ContactsService.instance.getDisplayName(senderInfo.phoneNumber);
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
                child: _buildAvatarChild(displayName, accentColor),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    displayName,
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
        if (senderInfo.reportCount != null && senderInfo.reportCount! > 0) ...[
          const SizedBox(height: 14),
          _ReportCountRow(reportCount: senderInfo.reportCount!),
        ],
      ],
    );
  }

  Widget _buildAvatarChild(String displayName, Color statusColor) {
    final code = senderInfo.countryCode;
    if (code != null && code.isNotEmpty) {
      return Text(
        _countryFlag(code),
        style: const TextStyle(fontSize: 24),
      );
    }

    final initials = _initials(displayName);
    final hue = (displayName.codeUnits.fold(0, (a, b) => a + b) % 30) * 12.0;
    final avatarColor = HSLColor.fromAHSL(1.0, hue, 0.55, 0.48).toColor();

    if (initials == '?') {
      return Icon(
        Icons.person_rounded,
        color: avatarColor,
        size: 24,
      );
    }

    return Text(
      initials,
      style: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.w700,
        color: avatarColor,
      ),
    );
  }

  String _initials(String name) {
    if (name.isEmpty) return '?';
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      final a = _firstChar(parts[0]);
      final b = _firstChar(parts[1]);
      if (a.isNotEmpty && b.isNotEmpty) return '$a$b'.toUpperCase();
    }
    final single = _firstChar(parts[0]);
    return single.isNotEmpty ? single.toUpperCase() : '?';
  }

  String _firstChar(String s) {
    if (s.isEmpty) return '';
    for (final c in s.split('')) {
      if (RegExp(r'[A-Za-z0-9]').hasMatch(c)) return c;
    }
    return '';
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
    final showCountry = senderInfo.countryName != null && senderInfo.countryCode != null;
    final showCarrier = senderInfo.carrierName != null;
    final showLineType = senderInfo.lineType != null;
    final showFirstSeen = senderInfo.firstSeenDate != null;

    if (!showCountry && !showCarrier && !showLineType && !showFirstSeen) {
      return const SizedBox.shrink();
    }

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        if (showCountry)
          _InfoChip(
            icon: Icons.public_rounded,
            label: 'Country (from number): ${senderInfo.countryName} (${senderInfo.countryCode})',
          ),
        if (showCarrier)
          _InfoChip(
            icon: Icons.signal_cellular_alt_rounded,
            label: senderInfo.carrierName!,
          ),
        if (showLineType)
          _InfoChip(
            icon: Icons.phone_rounded,
            label: senderInfo.lineType!,
          ),
        if (showFirstSeen)
          _InfoChip(
            icon: Icons.history_rounded,
            label: 'First seen: ${formatDate(senderInfo.firstSeenDate!)}',
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
