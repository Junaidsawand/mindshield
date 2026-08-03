// lib/features/spam/presentation/widgets/spam_message_tile.dart

import 'package:flutter/material.dart';
import '../../domain/spam_message.dart';
import 'risk_level_badge.dart';
import 'confidence_indicator.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SpamMessageTile
// ─────────────────────────────────────────────────────────────────────────────

/// Material 3 list tile that represents a single quarantined spam message.
///
/// Displays:
/// * Sender avatar with risk-coloured ring
/// * Sender name + formatted timestamp
/// * Message body preview (2 lines)
/// * [RiskLevelBadge] + [AttackTypeBadge] + [SpamStatusChip]
/// * [ConfidenceIndicator] bar
///
/// Tapping the tile calls [onViewAnalysis].
/// The trailing "⋮" menu exposes [onRestore], [onDelete], [onBlock] actions.
class SpamMessageTile extends StatelessWidget {
  const SpamMessageTile({
    super.key,
    required this.message,
    required this.onViewAnalysis,
    required this.onRestore,
    required this.onDelete,
    required this.onBlock,
  });

  final SpamMessage message;
  final VoidCallback onViewAnalysis;
  final VoidCallback onRestore;
  final VoidCallback onDelete;
  final VoidCallback onBlock;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final ringColor = _ringColor(message.riskLevel);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onViewAnalysis,
        borderRadius: BorderRadius.circular(16),
        splashColor: ringColor.withValues(alpha: 0.08),
        highlightColor: ringColor.withValues(alpha: 0.04),
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Row 1: Avatar + Header + Menu ────────────────────────────
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Avatar
                  _SpamAvatar(sender: message.sender, ringColor: ringColor),
                  const SizedBox(width: 12),

                  // Sender + timestamp + preview
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Sender name + timestamp
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                message.sender,
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: theme.textTheme.titleSmall!.copyWith(
                                  fontWeight: FontWeight.w700,
                                  color: cs.onSurface,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _formatTimestamp(message.timestamp),
                              style: theme.textTheme.labelSmall!.copyWith(
                                color: cs.onSurface.withValues(alpha: 0.45),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),

                        // Message preview
                        Text(
                          message.body,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.bodySmall!.copyWith(
                            color: cs.onSurface.withValues(alpha: 0.7),
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Overflow menu
                  _TileMenu(
                    message: message,
                    onViewAnalysis: onViewAnalysis,
                    onRestore: onRestore,
                    onDelete: onDelete,
                    onBlock: onBlock,
                  ),
                ],
              ),

              const SizedBox(height: 10),

              // ── Row 2: Badges ─────────────────────────────────────────────
              Padding(
                padding: const EdgeInsets.only(left: 62),
                child: Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: [
                    RiskLevelBadge(riskLevel: message.riskLevel),
                    AttackTypeBadge(attackType: message.attackType),
                    SpamStatusChip(status: message.status),
                  ],
                ),
              ),

              const SizedBox(height: 10),

              // ── Row 3: Confidence bar ─────────────────────────────────────
              Padding(
                padding: const EdgeInsets.only(left: 62, right: 8),
                child: ConfidenceIndicator(confidence: message.aiConfidence),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  Color _ringColor(SpamRiskLevel level) {
    switch (level) {
      case SpamRiskLevel.critical:
        return const Color(0xFFC62828);
      case SpamRiskLevel.high:
        return const Color(0xFFE65100);
      case SpamRiskLevel.medium:
        return const Color(0xFFF57F17);
    }
  }

  String _formatTimestamp(DateTime ts) {
    final now = DateTime.now();
    final diff = now.difference(ts);
    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays == 1) return 'Yesterday';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${ts.day}/${ts.month}/${ts.year.toString().substring(2)}';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SpamAvatar
// ─────────────────────────────────────────────────────────────────────────────

class _SpamAvatar extends StatelessWidget {
  const _SpamAvatar({
    required this.sender,
    required this.ringColor,
  });

  final String sender;
  final Color ringColor;

  @override
  Widget build(BuildContext context) {
    final hue = (sender.codeUnits.fold(0, (a, b) => a + b) % 30) * 12.0;
    final avatarColor = HSLColor.fromAHSL(1.0, hue, 0.55, 0.48).toColor();

    return Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: avatarColor.withValues(alpha: 0.12),
        border: Border.all(color: ringColor, width: 2.5),
      ),
      child: Center(
        child: Text(
          _initials(sender),
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: avatarColor,
          ),
        ),
      ),
    );
  }

  String _initials(String s) {
    final parts = s.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      final a = _firstAlpha(parts[0]);
      final b = _firstAlpha(parts[1]);
      if (a.isNotEmpty && b.isNotEmpty) return '$a$b'.toUpperCase();
    }
    return _firstAlpha(parts[0]).toUpperCase();
  }

  String _firstAlpha(String s) {
    for (final c in s.split('')) {
      if (RegExp(r'[A-Za-z0-9]').hasMatch(c)) return c;
    }
    return s.isEmpty ? '?' : String.fromCharCode(s.runes.first);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _TileMenu – overflow menu (⋮)
// ─────────────────────────────────────────────────────────────────────────────

class _TileMenu extends StatelessWidget {
  const _TileMenu({
    required this.message,
    required this.onViewAnalysis,
    required this.onRestore,
    required this.onDelete,
    required this.onBlock,
  });

  final SpamMessage message;
  final VoidCallback onViewAnalysis;
  final VoidCallback onRestore;
  final VoidCallback onDelete;
  final VoidCallback onBlock;

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<_MenuAction>(
      icon: Icon(
        Icons.more_vert_rounded,
        size: 20,
        color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
      ),
      tooltip: 'Message options',
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      onSelected: (action) {
        switch (action) {
          case _MenuAction.viewAnalysis:
            onViewAnalysis();
          case _MenuAction.restore:
            onRestore();
          case _MenuAction.block:
            onBlock();
          case _MenuAction.delete:
            onDelete();
        }
      },
      itemBuilder: (_) => [
        const PopupMenuItem(
          value: _MenuAction.viewAnalysis,
          child: _MenuRow(
            icon: Icons.analytics_rounded,
            label: 'View full analysis',
            color: null,
          ),
        ),
        const PopupMenuItem(
          value: _MenuAction.restore,
          child: _MenuRow(
            icon: Icons.restore_rounded,
            label: 'Restore to Inbox',
            color: Color(0xFF1565C0),
          ),
        ),
        if (true) // always shown
          const PopupMenuItem(
            value: _MenuAction.block,
            child: _MenuRow(
              icon: Icons.block_rounded,
              label: 'Block sender',
              color: Color(0xFFE65100),
            ),
          ),
        const PopupMenuDivider(),
        const PopupMenuItem(
          value: _MenuAction.delete,
          child: _MenuRow(
            icon: Icons.delete_forever_rounded,
            label: 'Delete permanently',
            color: Color(0xFFC62828),
          ),
        ),
      ],
    );
  }
}

class _MenuRow extends StatelessWidget {
  const _MenuRow({
    required this.icon,
    required this.label,
    required this.color,
  });

  final IconData icon;
  final String label;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final effectiveColor =
        color ?? Theme.of(context).colorScheme.onSurface;
    return Row(
      children: [
        Icon(icon, size: 18, color: effectiveColor),
        const SizedBox(width: 12),
        Text(
          label,
          style: TextStyle(
            color: effectiveColor,
            fontWeight: FontWeight.w500,
            fontSize: 14,
          ),
        ),
      ],
    );
  }
}

enum _MenuAction { viewAnalysis, restore, block, delete }
