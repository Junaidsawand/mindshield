import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../domain/sms_message.dart';
import 'conversation_provider.dart';
import '../../spam/data/sqflite_spam_repository.dart';
import '../../../core/router/app_router.dart';
import '../../../core/services/contacts_service.dart';
import '../../../core/services/native_actions_service.dart';
import '../../../core/services/sms_background_service.dart';

class ConversationDetailsScreen extends StatelessWidget {
  final String sender;
  final bool isSpam;

  const ConversationDetailsScreen({
    super.key,
    required this.sender,
    required this.isSpam,
  });

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<ConversationProvider>(
      create: (_) => ConversationProvider(sender: sender, isSpam: isSpam),
      child: const _ConversationDetailsView(),
    );
  }
}

class _ConversationDetailsView extends StatelessWidget {
  const _ConversationDetailsView();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ConversationProvider>();
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    final displayName = ContactsService.instance.getDisplayName(provider.sender);
    final isBlocked = provider.isBlocked;

    // Calculations
    final messages = provider.messages;
    final totalMsg = messages.length;
    final safeCount = messages.where((m) => m.aiStatus == AiStatus.safe).length;
    final suspiciousCount = messages.where((m) => m.aiStatus == AiStatus.suspicious).length;
    final scamCount = messages.where((m) => m.aiStatus == AiStatus.scam).length;
    final pendingCount = messages.where((m) => m.aiStatus == AiStatus.pending).length;

    // AI Confidence Average
    final confidences = messages.map((m) => m.confidenceScore).whereType<double>().toList();
    final avgConfidence = confidences.isEmpty
        ? 0.0
        : confidences.reduce((a, b) => a + b) / confidences.length;

    // Links Counter
    int totalLinks = 0;
    final urlRegex = RegExp(
      r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
      caseSensitive: false,
    );
    for (final msg in messages) {
      totalLinks += urlRegex.allMatches(msg.body).length;
    }

    // Threats / Suspicious keywords count
    final distinctThreats = messages
        .expand((m) => m.detectedThreats)
        .map((t) => t.trim())
        .where((t) => t.isNotEmpty)
        .toSet()
        .toList();

    // First and Latest Dates
    final firstDate = messages.isEmpty ? null : messages.first.timestamp;
    final latestDate = messages.isEmpty ? null : messages.last.timestamp;

    // Highest Risk status
    final threadStatus = _getThreadStatus(messages);

    return Scaffold(
      backgroundColor: cs.surface,
      appBar: AppBar(
        backgroundColor: cs.surface,
        surfaceTintColor: cs.surface,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => context.pop(),
          tooltip: 'Back',
        ),
        title: const Text('Conversation Info'),
      ),
      body: provider.isLoading && messages.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? _ErrorState(
                  message: provider.errorMessage!,
                  onRetry: provider.loadMessages,
                )
              : SafeArea(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 600),
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            // 1. Header Card
                            _HeaderCard(
                              displayName: displayName,
                              phoneNumber: provider.sender,
                              messageCount: totalMsg,
                              threadStatus: threadStatus,
                            ),
                            const SizedBox(height: 16),

                            // 2. Quick Actions Panel
                            _QuickActionsPanel(
                              sender: provider.sender,
                              isSpam: provider.isSpam,
                              latestMessageId: messages.isNotEmpty ? messages.last.id : '',
                              isBlocked: isBlocked,
                              onBlockedChanged: (value) async {
                                if (value) {
                                  await SqfliteSpamRepository.instance.blockConversation(provider.sender);
                                } else {
                                  await SqfliteSpamRepository.instance.unblockConversation(provider.sender);
                                }
                                SmsBackgroundService.instance.notifyListeners();
                              },
                              onDeleteCompleted: () {
                                // Pop back twice since the conversation thread has been deleted
                                // 1. Pop Details screen
                                context.pop();
                                // 2. Pop Detail screen (chat thread) if possible
                                if (context.canPop()) {
                                  context.pop();
                                }
                              },
                              onSpamMovedCompleted: () {
                                // Pop back twice since the conversation folder has changed
                                context.pop();
                                if (context.canPop()) {
                                  context.pop();
                                }
                              },
                            ),
                            const SizedBox(height: 16),

                            // 3. Security Summary Card
                            _SecuritySummaryCard(
                              total: totalMsg,
                              safe: safeCount,
                              suspicious: suspiciousCount,
                              scam: scamCount,
                              pending: pendingCount,
                            ),
                            const SizedBox(height: 16),

                            // 4. Conversation Audit Details Card
                            _ConversationAuditCard(
                              firstDate: firstDate,
                              latestDate: latestDate,
                              highestRisk: threadStatus,
                              avgConfidence: avgConfidence,
                              totalLinks: totalLinks,
                              threats: distinctThreats,
                              isBlocked: isBlocked,
                            ),
                            const SizedBox(height: 16),

                            // 5. Threat Timeline
                            const Padding(
                              padding: EdgeInsets.symmetric(horizontal: 4, vertical: 8),
                              child: Text(
                                'Threat Timeline',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            if (messages.isEmpty)
                              const Card(
                                child: Padding(
                                  padding: EdgeInsets.all(16),
                                  child: Text('No timeline messages analyzed.'),
                                ),
                              )
                            else
                              Card(
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16),
                                  side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.4)),
                                ),
                                child: Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 8),
                                  child: ListView.separated(
                                    shrinkWrap: true,
                                    physics: const NeverScrollableScrollPhysics(),
                                    itemCount: messages.length,
                                    separatorBuilder: (_, __) => Divider(
                                      indent: 52,
                                      endIndent: 16,
                                      height: 1,
                                      color: cs.outlineVariant.withValues(alpha: 0.35),
                                    ),
                                    itemBuilder: (context, index) {
                                      final msg = messages[index];
                                      return _TimelineItem(
                                        message: msg,
                                        onTap: () {
                                          context.push(AppRoutes.analysis, extra: msg);
                                        },
                                      );
                                    },
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
    );
  }

  AiStatus _getThreadStatus(List<SmsMessage> messages) {
    if (messages.isEmpty) return AiStatus.safe;
    if (messages.any((m) => m.aiStatus == AiStatus.scam)) return AiStatus.scam;
    if (messages.any((m) => m.aiStatus == AiStatus.suspicious)) return AiStatus.suspicious;
    if (messages.any((m) => m.aiStatus == AiStatus.pending)) return AiStatus.pending;
    return AiStatus.safe;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Header Card Widget
// ─────────────────────────────────────────────────────────────────────────────

class _HeaderCard extends StatelessWidget {
  final String displayName;
  final String phoneNumber;
  final int messageCount;
  final AiStatus threadStatus;

  const _HeaderCard({
    required this.displayName,
    required this.phoneNumber,
    required this.messageCount,
    required this.threadStatus,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final ringColor = _ringColor(threadStatus);

    final hue = (phoneNumber.codeUnits.fold(0, (a, b) => a + b) % 30) * 12.0;
    final avatarColor = HSLColor.fromAHSL(1.0, hue, 0.55, 0.48).toColor();

    return Card(
      elevation: 0,
      color: cs.surfaceContainerLow,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Avatar
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: avatarColor.withValues(alpha: 0.15),
                border: Border.all(color: ringColor, width: 3),
              ),
              child: Center(
                child: Text(
                  _initials(displayName),
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w700,
                    color: avatarColor,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Contact Name
            Text(
              displayName,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: cs.onSurface,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),

            // Phone Number
            if (displayName != phoneNumber) ...[
              Text(
                phoneNumber,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.55),
                  fontFamily: 'monospace',
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),
            ],

            // Message Count Pill
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: cs.secondaryContainer,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '$messageCount ${messageCount == 1 ? "Message" : "Messages"}',
                style: theme.textTheme.labelMedium?.copyWith(
                  color: cs.onSecondaryContainer,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _initials(String name) {
    final parts = name.trim().split(RegExp(r'\s+'));
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
        return const Color(0xFF2E7D32);
      case AiStatus.suspicious:
        return const Color(0xFFFFA726);
      case AiStatus.scam:
        return const Color(0xFFEF5350);
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Quick Actions Panel Widget
// ─────────────────────────────────────────────────────────────────────────────

class _QuickActionsPanel extends StatelessWidget {
  final String sender;
  final bool isSpam;
  final String latestMessageId;
  final bool isBlocked;
  final ValueChanged<bool> onBlockedChanged;
  final VoidCallback onDeleteCompleted;
  final VoidCallback onSpamMovedCompleted;

  const _QuickActionsPanel({
    required this.sender,
    required this.isSpam,
    required this.latestMessageId,
    required this.isBlocked,
    required this.onBlockedChanged,
    required this.onDeleteCompleted,
    required this.onSpamMovedCompleted,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.4)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
        child: Wrap(
          alignment: WrapAlignment.spaceEvenly,
          spacing: 8,
          runSpacing: 16,
          children: [
            _ActionButton(
              icon: Icons.phone_rounded,
              label: 'Call',
              color: cs.primary,
              onTap: () => NativeActionsService.launchDialer(sender),
            ),
            _ActionButton(
              icon: Icons.chat_bubble_outline_rounded,
              label: 'Reply',
              color: cs.primary,
              onTap: () => NativeActionsService.launchSms(sender),
            ),
            _ActionButton(
              icon: Icons.share_rounded,
              label: 'Share',
              color: cs.primary,
              onTap: () {
                final display = ContactsService.instance.getDisplayName(sender);
                NativeActionsService.shareText('MindShield Conversation Report\nSender: $display ($sender)\nRisk Status: ${isSpam ? "Spam" : "Inbox"}');
              },
            ),
            _ActionButton(
              icon: isBlocked ? Icons.check_circle_outline_rounded : Icons.block_rounded,
              label: isBlocked ? 'Unblock' : 'Block',
              color: const Color(0xFFE65100),
              onTap: () {
                onBlockedChanged(!isBlocked);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    behavior: SnackBarBehavior.floating,
                    backgroundColor: isBlocked ? const Color(0xFF2E7D32) : const Color(0xFFE65100),
                    content: Text(isBlocked ? 'Sender unblocked' : 'Sender blocked'),
                    duration: const Duration(seconds: 2),
                  ),
                );
              },
            ),
            _ActionButton(
              icon: isSpam ? Icons.restore_rounded : Icons.folder_special_rounded,
              label: isSpam ? 'Restore' : 'Spam',
              color: isSpam ? const Color(0xFF2E7D32) : cs.error,
              onTap: () async {
                if (isSpam) {
                  await SqfliteSpamRepository.instance.restoreConversation(sender);
                  SmsBackgroundService.instance.notifyListeners();
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      behavior: SnackBarBehavior.floating,
                      backgroundColor: Color(0xFF2E7D32),
                      content: Text('Conversation restored to Inbox'),
                    ),
                  );
                  onSpamMovedCompleted();
                } else {
                  await SqfliteSpamRepository.instance.moveConversationToSpam(sender);
                  SmsBackgroundService.instance.notifyListeners();
                  if (!context.mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      behavior: SnackBarBehavior.floating,
                      backgroundColor: cs.error,
                      content: const Text('Conversation moved to Spam'),
                    ),
                  );
                  onSpamMovedCompleted();
                }
              },
            ),
            _ActionButton(
              icon: Icons.delete_forever_rounded,
              label: 'Delete',
              color: cs.error,
              onTap: () => _confirmDelete(context),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmDelete(BuildContext context) {
    final theme = Theme.of(context);
    final displayName = ContactsService.instance.getDisplayName(sender);

    showDialog<void>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        icon: const Icon(Icons.delete_forever_rounded, size: 32),
        iconColor: theme.colorScheme.error,
        title: const Text('Delete conversation?'),
        content: Text(
          'All messages in the conversation from "$displayName" '
          'will be removed permanently. This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogCtx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: theme.colorScheme.error,
            ),
            onPressed: () async {
              Navigator.pop(dialogCtx);
              await SqfliteSpamRepository.instance.deleteConversation(sender);
              SmsBackgroundService.instance.notifyListeners();
              onDeleteCompleted();
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton.filledTonal(
          style: IconButton.styleFrom(
            backgroundColor: color.withValues(alpha: 0.1),
            foregroundColor: color,
          ),
          onPressed: onTap,
          icon: Icon(icon),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: cs.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Security Summary Card Widget
// ─────────────────────────────────────────────────────────────────────────────

class _SecuritySummaryCard extends StatelessWidget {
  final int total;
  final int safe;
  final int suspicious;
  final int scam;
  final int pending;

  const _SecuritySummaryCard({
    required this.total,
    required this.safe,
    required this.suspicious,
    required this.scam,
    required this.pending,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Card(
      elevation: 0,
      color: cs.surfaceContainerHigh,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Security Summary',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              alignment: WrapAlignment.spaceAround,
              spacing: 8,
              runSpacing: 12,
              children: [
                _SummaryMetric(
                  count: total,
                  label: 'Total',
                  color: cs.onSurfaceVariant,
                ),
                _SummaryMetric(
                  count: safe,
                  label: 'Safe',
                  color: const Color(0xFF2E7D32),
                ),
                _SummaryMetric(
                  count: suspicious,
                  label: 'Suspicious',
                  color: const Color(0xFFFFA726),
                ),
                _SummaryMetric(
                  count: scam,
                  label: 'Scam',
                  color: const Color(0xFFEF5350),
                ),
                if (pending > 0)
                  _SummaryMetric(
                    count: pending,
                    label: 'Pending',
                    color: const Color(0xFF42A5F5),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _SummaryMetric extends StatelessWidget {
  final int count;
  final String label;
  final Color color;

  const _SummaryMetric({
    required this.count,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$count',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Conversation Audit Details Card Widget
// ─────────────────────────────────────────────────────────────────────────────

class _ConversationAuditCard extends StatelessWidget {
  final DateTime? firstDate;
  final DateTime? latestDate;
  final AiStatus highestRisk;
  final double avgConfidence;
  final int totalLinks;
  final List<String> threats;
  final bool isBlocked;

  const _ConversationAuditCard({
    required this.firstDate,
    required this.latestDate,
    required this.highestRisk,
    required this.avgConfidence,
    required this.totalLinks,
    required this.threats,
    required this.isBlocked,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.4)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Security Audit Info',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            _AuditRow(
              label: 'First Message Received',
              value: firstDate != null ? _formatFullDate(firstDate!) : 'N/A',
            ),
            _AuditRow(
              label: 'Latest Message Received',
              value: latestDate != null ? _formatFullDate(latestDate!) : 'N/A',
            ),
            _AuditRow(
              label: 'Highest Threat Level',
              value: highestRisk.label,
              valueColor: _statusColor(highestRisk),
            ),
            _AuditRow(
              label: 'Avg AI Confidence',
              value: '${(avgConfidence * 100).toStringAsFixed(0)}%',
            ),
            _AuditRow(
              label: 'Total Links Intercepted',
              value: '$totalLinks',
              valueColor: totalLinks > 0 ? const Color(0xFFFFA726) : null,
            ),
            _AuditRow(
              label: 'Threat Signatures Found',
              value: threats.isEmpty ? 'None' : threats.join(', '),
              valueColor: threats.isNotEmpty ? const Color(0xFFEF5350) : null,
            ),
            _AuditRow(
              label: 'Block List Status',
              value: isBlocked ? 'Blocked' : 'Active',
              valueColor: isBlocked ? const Color(0xFFEF5350) : const Color(0xFF2E7D32),
            ),
          ],
        ),
      ),
    );
  }

  String _formatFullDate(DateTime d) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    final hr = d.hour.toString().padLeft(2, '0');
    final min = d.minute.toString().padLeft(2, '0');
    return '${d.day} ${months[d.month - 1]} ${d.year}, $hr:$min';
  }

  Color _statusColor(AiStatus status) {
    switch (status) {
      case AiStatus.pending:
        return const Color(0xFF42A5F5);
      case AiStatus.safe:
        return const Color(0xFF2E7D32);
      case AiStatus.suspicious:
        return const Color(0xFFFFA726);
      case AiStatus.scam:
        return const Color(0xFFEF5350);
    }
  }
}

class _AuditRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;

  const _AuditRow({
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            flex: 4,
            child: Text(
              label,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: cs.onSurfaceVariant.withValues(alpha: 0.8),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            flex: 5,
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
                color: valueColor ?? cs.onSurface,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Timeline Item Widget
// ─────────────────────────────────────────────────────────────────────────────

class _TimelineItem extends StatelessWidget {
  final SmsMessage message;
  final VoidCallback onTap;

  const _TimelineItem({
    required this.message,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final config = _TimelineStatusConfig.of(message.aiStatus);

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Timeline dot and line representation
            Column(
              children: [
                Container(
                  width: 14,
                  height: 14,
                  margin: const EdgeInsets.only(top: 4),
                  decoration: BoxDecoration(
                    color: config.color,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: config.color.withValues(alpha: 0.3),
                        blurRadius: 4,
                        spreadRadius: 1,
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(width: 16),

            // Message content preview
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    alignment: WrapAlignment.spaceBetween,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    spacing: 8,
                    runSpacing: 4,
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: config.color.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: config.color.withValues(alpha: 0.25), width: 1),
                        ),
                        child: Text(
                          config.label,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: config.color,
                            fontWeight: FontWeight.bold,
                            fontSize: 9,
                          ),
                        ),
                      ),
                      Text(
                        _formatTime(message.timestamp),
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: cs.onSurface.withValues(alpha: 0.45),
                          fontSize: 10,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(
                    message.body,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: cs.onSurface,
                      height: 1.35,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatTime(DateTime ts) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    final hr = ts.hour.toString().padLeft(2, '0');
    final min = ts.minute.toString().padLeft(2, '0');
    return '${ts.day} ${months[ts.month - 1]} ${ts.year}, $hr:$min';
  }
}

class _TimelineStatusConfig {
  final Color color;
  final String label;

  const _TimelineStatusConfig({
    required this.color,
    required this.label,
  });

  static _TimelineStatusConfig of(AiStatus status) {
    switch (status) {
      case AiStatus.pending:
        return const _TimelineStatusConfig(
          color: Color(0xFF42A5F5),
          label: 'Analyzing',
        );
      case AiStatus.safe:
        return const _TimelineStatusConfig(
          color: Color(0xFF2E7D32),
          label: 'Safe',
        );
      case AiStatus.suspicious:
        return const _TimelineStatusConfig(
          color: Color(0xFFFFA726),
          label: 'Suspicious',
        );
      case AiStatus.scam:
        return const _TimelineStatusConfig(
          color: Color(0xFFEF5350),
          label: 'Scam',
        );
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Error State Helper Widget
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
              'Failed to load conversation statistics',
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
