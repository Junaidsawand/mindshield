import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../analysis_provider.dart';
import '../../../../features/inbox/domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// ActionButtonsBar
// ─────────────────────────────────────────────────────────────────────────────

/// Bottom action bar with four action buttons:
/// • Move to Spam
/// • Mark Safe
/// • Block Sender
/// • Report
///
/// Buttons reflect the current [AnalysisActionState] with loading indicators.
/// Adapts layout depending on the message's [AiStatus].
class ActionButtonsBar extends StatelessWidget {
  const ActionButtonsBar({super.key, required this.aiStatus});

  final AiStatus aiStatus;

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<AnalysisProvider>();
    final cs = Theme.of(context).colorScheme;
    final isBusy = provider.isActionBusy;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 14),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // ── Primary row (Move to Spam / Mark Safe) ─────────────────────
            Row(
              children: [
                if (aiStatus != AiStatus.safe) ...[
                  Expanded(
                    child: _ActionButton(
                      id: 'btn_move_to_spam',
                      label: 'Move to Spam',
                      icon: Icons.move_to_inbox_rounded,
                      isLoading: provider.actionState ==
                          AnalysisActionState.movingToSpam,
                      isEnabled: !isBusy,
                      color: const Color(0xFFE65100),
                      outlined: true,
                      onTap: () async {
                        await provider.moveToSpam();
                        if (context.mounted) {
                          _showSnackBar(
                            context,
                            '📥 Message moved to Spam',
                            Icons.check_circle_rounded,
                          );
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 10),
                ],
                Expanded(
                  child: _ActionButton(
                    id: 'btn_mark_safe',
                    label: 'Mark Safe',
                    icon: Icons.verified_rounded,
                    isLoading:
                        provider.actionState == AnalysisActionState.markingSafe,
                    isEnabled: !isBusy,
                    color: const Color(0xFF2E7D32),
                    outlined: aiStatus == AiStatus.safe,
                    onTap: () async {
                      await provider.markSafe();
                      if (context.mounted) {
                        _showSnackBar(
                          context,
                          '✅ Message marked as safe',
                          Icons.verified_rounded,
                        );
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            // ── Secondary row (Block Sender / Report) ──────────────────────
            Row(
              children: [
                Expanded(
                  child: _ActionButton(
                    id: 'btn_block_sender',
                    label: 'Block Sender',
                    icon: Icons.block_rounded,
                    isLoading: provider.actionState ==
                        AnalysisActionState.blockingSender,
                    isEnabled: !isBusy,
                    color: cs.error,
                    outlined: true,
                    onTap: () async {
                      await provider.blockSender();
                      if (context.mounted) {
                        _showSnackBar(
                          context,
                          '🚫 Sender blocked',
                          Icons.block_rounded,
                        );
                      }
                    },
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: _ActionButton(
                    id: 'btn_report',
                    label: 'Report',
                    icon: Icons.flag_rounded,
                    isLoading:
                        provider.actionState == AnalysisActionState.reporting,
                    isEnabled: !isBusy,
                    color: cs.error,
                    outlined: false,
                    onTap: () async {
                      await provider.report();
                      if (context.mounted) {
                        _showSnackBar(
                          context,
                          '🚩 Reported to MindShield threat database',
                          Icons.flag_rounded,
                        );
                      }
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showSnackBar(BuildContext context, String message, IconData icon) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(icon, color: Colors.white, size: 18),
            const SizedBox(width: 10),
            Text(message),
          ],
        ),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ActionButton
// ─────────────────────────────────────────────────────────────────────────────

class _ActionButton extends StatelessWidget {
  const _ActionButton({
    required this.id,
    required this.label,
    required this.icon,
    required this.isLoading,
    required this.isEnabled,
    required this.color,
    required this.outlined,
    required this.onTap,
  });

  final String id;
  final String label;
  final IconData icon;
  final bool isLoading;
  final bool isEnabled;
  final Color color;
  final bool outlined;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final child = isLoading
        ? SizedBox(
            width: 18,
            height: 18,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: outlined ? color : Colors.white,
            ),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 16),
              const SizedBox(width: 6),
              Text(label),
            ],
          );

    if (outlined) {
      return OutlinedButton(
        key: Key(id),
        onPressed: isEnabled && !isLoading ? onTap : null,
        style: OutlinedButton.styleFrom(
          foregroundColor: color,
          side: BorderSide(
              color: isEnabled ? color.withValues(alpha: 0.6) : Colors.grey),
          padding: const EdgeInsets.symmetric(vertical: 13),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
        child: child,
      );
    }

    return FilledButton(
      key: Key(id),
      onPressed: isEnabled && !isLoading ? onTap : null,
      style: FilledButton.styleFrom(
        backgroundColor: color,
        padding: const EdgeInsets.symmetric(vertical: 13),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      child: child,
    );
  }
}
