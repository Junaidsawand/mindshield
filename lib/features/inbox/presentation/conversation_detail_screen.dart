import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../domain/sms_message.dart';
import 'conversation_provider.dart';
import '../../../core/router/app_router.dart';
import '../../spam/data/sqflite_spam_repository.dart';
import '../../../core/services/sms_background_service.dart';
import '../../../core/services/contacts_service.dart';

class ConversationDetailScreen extends StatelessWidget {
  final String sender;
  final bool isSpam;

  const ConversationDetailScreen({
    super.key,
    required this.sender,
    required this.isSpam,
  });

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<ConversationProvider>(
      create: (_) => ConversationProvider(sender: sender, isSpam: isSpam),
      child: const _ConversationDetailView(),
    );
  }
}

class _ConversationDetailView extends StatefulWidget {
  const _ConversationDetailView();

  @override
  State<_ConversationDetailView> createState() => _ConversationDetailViewState();
}

class _ConversationDetailViewState extends State<_ConversationDetailView> {
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ConversationProvider>();
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    // Trigger scrolling when messages load or change
    if (!provider.isLoading && provider.messages.isNotEmpty) {
      _scrollToBottom();
    }

    // Determine aggregate thread status (highest risk)
    final threadStatus = _getThreadStatus(provider.messages);
    final statusConfig = _StatusConfig.of(threadStatus);

    final displayName = ContactsService.instance.getDisplayName(provider.sender);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      appBar: AppBar(
        titleSpacing: 0,
        backgroundColor: cs.surface,
        surfaceTintColor: cs.surfaceTint,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => context.pop(),
          tooltip: 'Back',
        ),
        title: Row(
          children: [
            _SenderAvatar(
              sender: displayName,
              status: threadStatus,
              ringColor: statusConfig.color,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    displayName,
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: cs.onSurface,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    statusConfig.subtitle,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: statusConfig.color,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.info_outline_rounded),
            tooltip: 'Thread details',
            onPressed: () {
              // Information Dialog showing thread summary
              _showThreadInfoDialog(context, displayName, provider.messages);
            },
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          // Message List
          Expanded(
            child: provider.isLoading && provider.messages.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : provider.errorMessage != null
                    ? _ErrorState(
                        message: provider.errorMessage!,
                        onRetry: provider.loadMessages,
                      )
                    : provider.messages.isEmpty
                        ? const _EmptyState()
                        : ListView.builder(
                            controller: _scrollController,
                            padding: const EdgeInsets.all(16),
                            itemCount: provider.messages.length,
                            itemBuilder: (context, index) {
                              final msg = provider.messages[index];
                              return _ChatBubble(
                                message: msg,
                                onTap: () => _navigateToAnalysis(context, msg),
                              );
                            },
                          ),
          ),

          // Persistent Security Actions Panel at bottom
          if (provider.messages.isNotEmpty)
            _SecurityActionBar(
              isSpam: provider.isSpam,
              sender: provider.sender,
              latestMessageId: provider.messages.last.id,
              onActionCompleted: () {
                // Return to previous screen since the conversation has moved folders or has been deleted
                context.pop();
              },
            ),
        ],
      ),
    );
  }

  void _navigateToAnalysis(BuildContext context, SmsMessage message) {
    context.push(AppRoutes.analysis, extra: message);
  }

  AiStatus _getThreadStatus(List<SmsMessage> messages) {
    if (messages.isEmpty) return AiStatus.safe;
    if (messages.any((m) => m.aiStatus == AiStatus.scam)) return AiStatus.scam;
    if (messages.any((m) => m.aiStatus == AiStatus.suspicious)) return AiStatus.suspicious;
    if (messages.any((m) => m.aiStatus == AiStatus.pending)) return AiStatus.pending;
    return AiStatus.safe;
  }

  void _showThreadInfoDialog(BuildContext context, String sender, List<SmsMessage> messages) {
    final scamCount = messages.where((m) => m.aiStatus == AiStatus.scam).length;
    final suspiciousCount = messages.where((m) => m.aiStatus == AiStatus.suspicious).length;

    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Conversation Audit'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Sender: $sender', style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Text('Total Messages: ${messages.length}'),
            const SizedBox(height: 6),
            Text('Scam Detections: $scamCount', style: TextStyle(color: scamCount > 0 ? Colors.red : null)),
            const SizedBox(height: 6),
            Text('Suspicious Flags: $suspiciousCount', style: TextStyle(color: suspiciousCount > 0 ? Colors.orange : null)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ChatBubble Widget
// ─────────────────────────────────────────────────────────────────────────────

class _ChatBubble extends StatelessWidget {
  final SmsMessage message;
  final VoidCallback onTap;

  const _ChatBubble({
    required this.message,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final cfg = _StatusConfig.of(message.aiStatus);

    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12, right: 32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Bubble card
            Material(
              color: cfg.bubbleBackground(theme),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(16),
                topRight: Radius.circular(16),
                bottomRight: Radius.circular(16),
                bottomLeft: Radius.circular(4),
              ),
              child: InkWell(
                onTap: onTap,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                  bottomLeft: Radius.circular(4),
                ),
                splashColor: cfg.color.withValues(alpha: 0.15),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Message Text
                      Text(
                        message.body,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface,
                          height: 1.4,
                        ),
                      ),
                      const SizedBox(height: 8),

                      // AI Badge and time
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: cfg.color.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(color: cfg.color.withValues(alpha: 0.25), width: 1),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(cfg.icon, size: 12, color: cfg.color),
                                const SizedBox(width: 4),
                                Text(
                                  cfg.badgeText,
                                  style: theme.textTheme.labelSmall?.copyWith(
                                    color: cfg.color,
                                    fontWeight: FontWeight.w700,
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 16),
                          Text(
                            _formatTime(message.timestamp),
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: cs.onSurface.withValues(alpha: 0.4),
                              fontSize: 10,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 2),
            // Tap hint
            Padding(
              padding: const EdgeInsets.only(left: 4),
              child: Text(
                'Tap to view AI analysis',
                style: theme.textTheme.labelSmall?.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.35),
                  fontSize: 9,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime ts) {
    final hour = ts.hour.toString().padLeft(2, '0');
    final minute = ts.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SecurityActionBar Widget
// ─────────────────────────────────────────────────────────────────────────────

class _SecurityActionBar extends StatelessWidget {
  final bool isSpam;
  final String sender;
  final String latestMessageId;
  final VoidCallback onActionCompleted;

  const _SecurityActionBar({
    required this.isSpam,
    required this.sender,
    required this.latestMessageId,
    required this.onActionCompleted,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHigh,
        border: Border(
          top: BorderSide(
            color: cs.outlineVariant.withValues(alpha: 0.5),
            width: 1,
          ),
        ),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: isSpam
                  ? FilledButton.icon(
                      style: FilledButton.styleFrom(
                        backgroundColor: cs.primary,
                        foregroundColor: cs.onPrimary,
                      ),
                      onPressed: () => _restore(context),
                      icon: const Icon(Icons.restore_rounded, size: 18),
                      label: const Text('Restore to Inbox'),
                    )
                  : OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: cs.error),
                        foregroundColor: cs.error,
                      ),
                      onPressed: () => _moveToSpam(context),
                      icon: const Icon(Icons.folder_special_rounded, size: 18),
                      label: const Text('Move to Spam'),
                    ),
            ),
            const SizedBox(width: 12),
            IconButton.filledTonal(
              style: IconButton.styleFrom(
                backgroundColor: cs.errorContainer,
                foregroundColor: cs.onErrorContainer,
              ),
              onPressed: () => _confirmAndDelete(context),
              icon: const Icon(Icons.delete_forever_rounded),
              tooltip: 'Delete conversation',
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _moveToSpam(BuildContext context) async {
    final errorColor = Theme.of(context).colorScheme.error;
    try {
      await SqfliteSpamRepository.instance.moveConversationToSpam(sender);
      SmsBackgroundService.instance.notifyListeners();
      if (!context.mounted) return;
      _showSnackBar(context, 'Conversation moved to Spam', Icons.folder_special_rounded, errorColor);
      onActionCompleted();
    } catch (e) {
      debugPrint('Error moving thread to spam: $e');
    }
  }

  Future<void> _restore(BuildContext context) async {
    try {
      await SqfliteSpamRepository.instance.restoreConversation(sender);
      SmsBackgroundService.instance.notifyListeners();
      if (!context.mounted) return;
      _showSnackBar(context, 'Conversation restored to Inbox', Icons.restore_rounded, const Color(0xFF2E7D32));
      onActionCompleted();
    } catch (e) {
      debugPrint('Error restoring thread to inbox: $e');
    }
  }

  Future<void> _delete(BuildContext context) async {
    final errorColor = Theme.of(context).colorScheme.error;
    try {
      await SqfliteSpamRepository.instance.deleteConversation(sender);
      SmsBackgroundService.instance.notifyListeners();
      if (!context.mounted) return;
      _showSnackBar(context, 'Conversation deleted permanently', Icons.delete_forever_rounded, errorColor);
      onActionCompleted();
    } catch (e) {
      debugPrint('Error deleting conversation: $e');
    }
  }

  void _confirmAndDelete(BuildContext context) {
    final displayName = ContactsService.instance.getDisplayName(sender);
    showDialog<void>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        icon: const Icon(Icons.delete_forever_rounded, size: 32),
        iconColor: Theme.of(dialogCtx).colorScheme.error,
        title: const Text('Delete conversation?'),
        content: Text(
          'All messages from "$displayName" will be removed permanently.',
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
              Navigator.pop(dialogCtx);
              _delete(context);
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _showSnackBar(
      BuildContext context, String text, IconData icon, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        behavior: SnackBarBehavior.floating,
        backgroundColor: color,
        content: Row(
          children: [
            Icon(icon, color: Colors.white, size: 18),
            const SizedBox(width: 10),
            Text(text, style: const TextStyle(color: Colors.white)),
          ],
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SenderAvatar Widget
// ─────────────────────────────────────────────────────────────────────────────

class _SenderAvatar extends StatelessWidget {
  final String sender;
  final AiStatus status;
  final Color ringColor;

  const _SenderAvatar({
    required this.sender,
    required this.status,
    required this.ringColor,
  });

  @override
  Widget build(BuildContext context) {
    final hue = (sender.codeUnits.fold(0, (a, b) => a + b) % 30) * 12.0;
    final avatarColor = HSLColor.fromAHSL(1.0, hue, 0.55, 0.48).toColor();

    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: avatarColor.withValues(alpha: 0.15),
        border: Border.all(color: ringColor, width: 2),
      ),
      child: Center(
        child: Text(
          _initials(sender),
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: avatarColor,
          ),
        ),
      ),
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
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper Widgets
// ─────────────────────────────────────────────────────────────────────────────

class _ErrorState extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorState({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 48, color: cs.error),
            const SizedBox(height: 16),
            const Text(
              'Failed to load conversation history',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: onRetry,
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: Text('No messages in this conversation.'),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _StatusConfig Helper Model
// ─────────────────────────────────────────────────────────────────────────────

class _StatusConfig {
  final Color color;
  final String subtitle;
  final String badgeText;
  final IconData icon;

  const _StatusConfig({
    required this.color,
    required this.subtitle,
    required this.badgeText,
    required this.icon,
  });

  Color bubbleBackground(ThemeData theme) {
    return color.withValues(alpha: theme.brightness == Brightness.dark ? 0.15 : 0.08);
  }

  static _StatusConfig of(AiStatus status) {
    switch (status) {
      case AiStatus.pending:
        return const _StatusConfig(
          color: Color(0xFF42A5F5),
          subtitle: 'AI analyzing messages...',
          badgeText: 'Analyzing',
          icon: Icons.sync_rounded,
        );
      case AiStatus.safe:
        return const _StatusConfig(
          color: Color(0xFF2E7D32),
          subtitle: 'Secure connection',
          badgeText: 'Safe',
          icon: Icons.check_circle_rounded,
        );
      case AiStatus.suspicious:
        return const _StatusConfig(
          color: Color(0xFFFFA726),
          subtitle: 'Suspicious content flagged',
          badgeText: 'Suspicious',
          icon: Icons.warning_rounded,
        );
      case AiStatus.scam:
        return const _StatusConfig(
          color: Color(0xFFEF5350),
          subtitle: 'Malicious threat detected',
          badgeText: 'Scam',
          icon: Icons.dangerous_rounded,
        );
    }
  }
}
