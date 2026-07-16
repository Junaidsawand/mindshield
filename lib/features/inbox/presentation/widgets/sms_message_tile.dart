import 'package:flutter/material.dart';
import '../../domain/sms_message.dart';
import 'ai_status_badge.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SmsMessageTile
// ─────────────────────────────────────────────────────────────────────────────

/// Material 3 list tile that represents a single SMS message in the inbox.
///
/// Displays:
/// * Sender avatar (initials or emoji)
/// * Sender name (bold if unread)
/// * Message preview (truncated to 2 lines)
/// * Formatted timestamp
/// * [AiStatusBadge]
/// * Unread indicator dot
///
/// Calls [onTap] when pressed (used by [InboxScreen] to navigate).
class SmsMessageTile extends StatelessWidget {
  const SmsMessageTile({
    super.key,
    required this.message,
    required this.onTap,
  });

  final SmsMessage message;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final isUnread = !message.isRead;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        splashColor: cs.primary.withValues(alpha: 0.08),
        highlightColor: cs.primary.withValues(alpha: 0.04),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Avatar ────────────────────────────────────────────────────
              _SenderAvatar(
                sender: message.sender,
                status: message.aiStatus,
              ),
              const SizedBox(width: 14),

              // ── Content ───────────────────────────────────────────────────
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Row 1: sender + timestamp + unread dot
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            message.sender,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.titleSmall!.copyWith(
                              fontWeight: isUnread
                                  ? FontWeight.w700
                                  : FontWeight.w500,
                              color: isUnread
                                  ? cs.onSurface
                                  : cs.onSurface.withValues(alpha: 0.75),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _formatTimestamp(message.timestamp),
                          style: theme.textTheme.labelSmall!.copyWith(
                            color: isUnread
                                ? cs.primary
                                : cs.onSurface.withValues(alpha: 0.45),
                            fontWeight: isUnread
                                ? FontWeight.w600
                                : FontWeight.normal,
                          ),
                        ),
                        if (isUnread) ...[
                          const SizedBox(width: 6),
                          _UnreadDot(color: cs.primary),
                        ],
                      ],
                    ),
                    const SizedBox(height: 4),

                    // Row 2: message preview
                    Text(
                      message.body,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall!.copyWith(
                        color: isUnread
                            ? cs.onSurface.withValues(alpha: 0.85)
                            : cs.onSurface.withValues(alpha: 0.55),
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 8),

                    // Row 3: AI status badge
                    AiStatusBadge(status: message.aiStatus),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  String _formatTimestamp(DateTime ts) {
    final now = DateTime.now();
    final diff = now.difference(ts);

    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays == 1) return 'Yesterday';
    return '${ts.day}/${ts.month}';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SenderAvatar
// ─────────────────────────────────────────────────────────────────────────────

class _SenderAvatar extends StatelessWidget {
  const _SenderAvatar({required this.sender, required this.status});

  final String sender;
  final AiStatus status;

  @override
  Widget build(BuildContext context) {
    // Derive a consistent avatar background from the sender string.
    final hue = (sender.codeUnits.fold(0, (a, b) => a + b) % 30) * 12.0;
    final avatarColor = HSLColor.fromAHSL(1.0, hue, 0.55, 0.48).toColor();

    // Status ring colour.
    final ringColor = _ringColor(status);

    return Stack(
      clipBehavior: Clip.none,
      children: [
        Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: avatarColor.withValues(alpha: 0.15),
            border: Border.all(color: ringColor, width: 2.5),
          ),
          child: Center(
            child: Text(
              _initials(sender),
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: avatarColor,
              ),
            ),
          ),
        ),
      ],
    );
  }

  String _initials(String sender) {
    // If the sender contains an emoji, return just the first grapheme cluster.
    final runes = sender.runes.toList();
    if (runes.isEmpty) return '?';

    // Try to get up to 2 initials from words.
    final parts = sender.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      final a = _firstChar(parts[0]);
      final b = _firstChar(parts[1]);
      if (a.isNotEmpty && b.isNotEmpty) return '$a$b'.toUpperCase();
    }
    return _firstChar(parts[0]).toUpperCase();
  }

  String _firstChar(String s) {
    if (s.isEmpty) return '';
    // Skip leading non-letter chars (emojis etc.) for initials.
    for (final c in s.split('')) {
      if (RegExp(r'[A-Za-z0-9]').hasMatch(c)) return c;
    }
    // Fallback: return first rune as string.
    return String.fromCharCode(s.runes.first);
  }

  Color _ringColor(AiStatus status) {
    switch (status) {
      case AiStatus.safe:
        return const Color(0xFF66BB6A);
      case AiStatus.suspicious:
        return const Color(0xFFFFA726);
      case AiStatus.scam:
        return const Color(0xFFEF5350);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _UnreadDot
// ─────────────────────────────────────────────────────────────────────────────

class _UnreadDot extends StatelessWidget {
  const _UnreadDot({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color,
        boxShadow: [
          BoxShadow(
            color: color.withValues(alpha: 0.45),
            blurRadius: 4,
            spreadRadius: 1,
          ),
        ],
      ),
    );
  }
}
