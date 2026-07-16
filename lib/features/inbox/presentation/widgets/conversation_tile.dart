import 'package:flutter/material.dart';
import '../../domain/sms_message.dart';
import '../../domain/conversation.dart';
import 'ai_status_badge.dart';
import '../../../../core/services/contacts_service.dart';

class ConversationTile extends StatelessWidget {
  final Conversation<SmsMessage> conversation;
  final VoidCallback onTap;

  const ConversationTile({
    super.key,
    required this.conversation,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final isUnread = conversation.isUnread;
    final latestMsg = conversation.latestMessage;
    final threadStatus = conversation.aiStatus;

    // Count of unread messages in this thread
    final unreadMsgsCount = conversation.messages.where((m) => !m.isRead).length;

    final displayName = ContactsService.instance.getDisplayName(conversation.sender);

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
              // Avatar
              _SenderAvatar(
                sender: displayName,
                status: threadStatus,
              ),
              const SizedBox(width: 14),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Row 1: sender + timestamp + unread dot
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            displayName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.titleSmall!.copyWith(
                              fontWeight: isUnread ? FontWeight.w700 : FontWeight.w500,
                              color: isUnread ? cs.onSurface : cs.onSurface.withValues(alpha: 0.75),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          _formatTimestamp(conversation.latestTimestamp),
                          style: theme.textTheme.labelSmall!.copyWith(
                            color: isUnread ? cs.primary : cs.onSurface.withValues(alpha: 0.45),
                            fontWeight: isUnread ? FontWeight.w600 : FontWeight.normal,
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
                      latestMsg.body,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodySmall!.copyWith(
                        color: isUnread ? cs.onSurface.withValues(alpha: 0.85) : cs.onSurface.withValues(alpha: 0.55),
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 8),

                    // Row 3: Badges
                    Row(
                      children: [
                        AiStatusBadge(status: threadStatus),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: cs.secondaryContainer.withValues(alpha: 0.7),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '${conversation.totalCount} ${conversation.totalCount == 1 ? "message" : "messages"}',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: cs.onSecondaryContainer,
                              fontWeight: FontWeight.w600,
                              fontSize: 10,
                            ),
                          ),
                        ),
                        if (unreadMsgsCount > 0) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: cs.primaryContainer,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Text(
                              '$unreadMsgsCount new',
                              style: theme.textTheme.labelSmall?.copyWith(
                                color: cs.onPrimaryContainer,
                                fontWeight: FontWeight.bold,
                                fontSize: 10,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

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

class _SenderAvatar extends StatelessWidget {
  final String sender;
  final AiStatus status;

  const _SenderAvatar({required this.sender, required this.status});

  @override
  Widget build(BuildContext context) {
    final hue = (sender.codeUnits.fold(0, (a, b) => a + b) % 30) * 12.0;
    final avatarColor = HSLColor.fromAHSL(1.0, hue, 0.55, 0.48).toColor();
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
    final runes = sender.runes.toList();
    if (runes.isEmpty) return '?';

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
    for (final c in s.split('')) {
      if (RegExp(r'[A-Za-z0-9]').hasMatch(c)) return c;
    }
    return String.fromCharCode(s.runes.first);
  }

  Color _ringColor(AiStatus status) {
    switch (status) {
      case AiStatus.pending:
        return const Color(0xFF42A5F5);
      case AiStatus.safe:
        return const Color(0xFF66BB6A);
      case AiStatus.suspicious:
        return const Color(0xFFFFA726);
      case AiStatus.scam:
        return const Color(0xFFEF5350);
    }
  }
}

class _UnreadDot extends StatelessWidget {
  final Color color;
  const _UnreadDot({required this.color});

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
