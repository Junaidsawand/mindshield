// lib/features/spam/presentation/widgets/spam_action_sheet.dart

import 'package:flutter/material.dart';
import '../../domain/spam_message.dart';
import 'risk_level_badge.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SpamActionSheet
// ─────────────────────────────────────────────────────────────────────────────

/// Bottom sheet that provides swipe-up contextual actions for a spam message.
///
/// Shown when the user long-presses a [SpamMessageTile].
/// Presents: Restore to Inbox, Block Sender, View Analysis, Delete.
class SpamActionSheet extends StatelessWidget {
  const SpamActionSheet({
    super.key,
    required this.message,
    required this.onRestore,
    required this.onBlock,
    required this.onViewAnalysis,
    required this.onDelete,
  });

  final SpamMessage message;
  final VoidCallback onRestore;
  final VoidCallback onBlock;
  final VoidCallback onViewAnalysis;
  final VoidCallback onDelete;

  /// Convenience method to show the sheet via [showModalBottomSheet].
  static Future<void> show({
    required BuildContext context,
    required SpamMessage message,
    required VoidCallback onRestore,
    required VoidCallback onBlock,
    required VoidCallback onViewAnalysis,
    required VoidCallback onDelete,
  }) {
    return showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (_) => SpamActionSheet(
        message: message,
        onRestore: onRestore,
        onBlock: onBlock,
        onViewAnalysis: onViewAnalysis,
        onDelete: onDelete,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Drag handle
            Container(
              width: 36,
              height: 4,
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: cs.outlineVariant,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // ── Message preview header ────────────────────────────────────
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: cs.surfaceContainerHighest.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          message.sender,
                          style: theme.textTheme.titleSmall!.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      RiskLevelBadge(riskLevel: message.riskLevel),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    message.body,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodySmall!.copyWith(
                      color: cs.onSurface.withValues(alpha: 0.65),
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ── Action buttons ────────────────────────────────────────────
            _ActionButton(
              icon: Icons.analytics_rounded,
              label: 'View Full Analysis',
              sublabel: 'See detailed AI threat breakdown',
              color: cs.primary,
              onTap: () {
                Navigator.pop(context);
                onViewAnalysis();
              },
            ),
            const SizedBox(height: 8),
            _ActionButton(
              icon: Icons.restore_rounded,
              label: 'Restore to Inbox',
              sublabel: 'Move this message back to your inbox',
              color: const Color(0xFF1565C0),
              onTap: () {
                Navigator.pop(context);
                onRestore();
              },
            ),
            const SizedBox(height: 8),
            _ActionButton(
              icon: Icons.block_rounded,
              label: 'Block Sender',
              sublabel: 'Prevent future messages from ${message.sender}',
              color: const Color(0xFFE65100),
              onTap: () {
                Navigator.pop(context);
                onBlock();
              },
            ),
            const SizedBox(height: 8),
            _ActionButton(
              icon: Icons.delete_forever_rounded,
              label: 'Delete Permanently',
              sublabel: 'This action cannot be undone',
              color: cs.error,
              onTap: () => _confirmDelete(context),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmDelete(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        icon: const Icon(Icons.delete_forever_rounded, size: 32),
        iconColor: Theme.of(dialogCtx).colorScheme.error,
        title: const Text('Delete permanently?'),
        content: Text(
          'This message from "${message.sender}" will be removed from your '
          'spam folder forever. This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogCtx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(dialogCtx).colorScheme.error,
            ),
            onPressed: () {
              Navigator.pop(dialogCtx); // close dialog
              Navigator.pop(context); // close bottom sheet
              onDelete();
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ActionButton
// ─────────────────────────────────────────────────────────────────────────────

class _ActionButton extends StatelessWidget {
  const _ActionButton({
    required this.icon,
    required this.label,
    required this.sublabel,
    required this.color,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final String sublabel;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Material(
      color: color.withValues(alpha: 0.06),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      label,
                      style: Theme.of(context).textTheme.bodyMedium!.copyWith(
                            fontWeight: FontWeight.w600,
                            color: color,
                          ),
                    ),
                    Text(
                      sublabel,
                      style: Theme.of(context).textTheme.bodySmall!.copyWith(
                            color: cs.onSurface.withValues(alpha: 0.5),
                            fontSize: 11,
                          ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right_rounded,
                color: color.withValues(alpha: 0.5),
                size: 18,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
