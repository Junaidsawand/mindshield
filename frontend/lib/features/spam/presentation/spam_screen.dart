// lib/features/spam/presentation/spam_screen.dart

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../../../core/router/app_router.dart';
import '../../inbox/domain/conversation.dart';
import '../../inbox/domain/sms_message.dart';
import '../domain/spam_message.dart';
import 'spam_provider.dart';
import 'widgets/spam_filter_bar.dart';
import 'widgets/spam_conversation_tile.dart';
import 'widgets/spam_section_header.dart';
import 'widgets/spam_action_sheet.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SpamScreen
// ─────────────────────────────────────────────────────────────────────────────

/// Spam Folder screen – shows all quarantined SMS messages grouped by risk
/// level (Critical → High → Medium).
///
/// Architecture
/// ────────────
/// * [SpamProvider] is scoped locally via [ChangeNotifierProvider].
/// * Data flows through [SqfliteSpamRepository].
/// * Navigation to [AnalysisScreen] passes a compatible [SmsMessage] via
///   [GoRouter.extra].
///
/// User Actions
/// ────────────
/// * Tap tile    → Navigate to full Analysis screen.
/// * Long-press  → [SpamActionSheet] with Restore / Block / Delete options.
/// * Tap ⋮ menu  → Same actions as above, in-tile.
/// * Pull-to-refresh → Reload from repository.
/// * Sort button → [SpamSortOrder] bottom sheet.
class SpamScreen extends StatelessWidget {
  const SpamScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<SpamProvider>(
      create: (_) => SpamProvider(),
      child: const _SpamView(),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SpamView
// ─────────────────────────────────────────────────────────────────────────────

class _SpamView extends StatelessWidget {
  const _SpamView();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<SpamProvider>();

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: RefreshIndicator(
        onRefresh: provider.loadMessages,
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            // ── Large collapsing app bar ───────────────────────────────────
            _SpamSliverAppBar(
              totalCount: provider.totalCount,
              criticalCount: provider.criticalCount,
              sortOrder: provider.sortOrder,
              onSortTap: () => _showSortSheet(context, provider),
            ),

            // ── Filter chips ──────────────────────────────────────────────
            SliverPersistentHeader(
              pinned: true,
              delegate: _FilterBarDelegate(
                child: ColoredBox(
                  color: Theme.of(context).colorScheme.surface,
                  child: SizedBox(
                    height: 61,
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const SizedBox(height: 8),
                        SpamFilterBar(
                          activeFilter: provider.activeFilter,
                          countFor: provider.countFor,
                          onFilterSelected: provider.setFilter,
                        ),
                        const SizedBox(height: 8),
                        Divider(
                          height: 1,
                          thickness: 1,
                          color: Theme.of(context)
                              .colorScheme
                              .outlineVariant
                              .withValues(alpha: 0.4),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            // ── Body: loading / error / empty / grouped list ───────────────
            if (provider.isLoading)
              const SliverFillRemaining(
                hasScrollBody: false,
                child: _LoadingState(),
              )
            else if (provider.errorMessage != null)
              SliverFillRemaining(
                hasScrollBody: false,
                child: _ErrorState(
                  message: provider.errorMessage ?? 'Unknown error',
                  onRetry: provider.loadMessages,
                ),
              )
            else if (provider.filteredConversations.isEmpty)
              SliverFillRemaining(
                hasScrollBody: false,
                child: _EmptyState(filter: provider.activeFilter),
              )
            else
              _GroupedMessageList(grouped: provider.groupedConversations),
          ],
        ),
      ),
    );
  }

  // ── Sort bottom sheet ────────────────────────────────────────────────────

  void _showSortSheet(BuildContext context, SpamProvider provider) {
    showModalBottomSheet<void>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (sheetCtx) => _SortSheet(
        currentOrder: provider.sortOrder,
        onSelected: (order) {
          provider.setSortOrder(order);
          Navigator.pop(sheetCtx);
        },
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SpamSliverAppBar
// ─────────────────────────────────────────────────────────────────────────────

class _SpamSliverAppBar extends StatelessWidget {
  const _SpamSliverAppBar({
    required this.totalCount,
    required this.criticalCount,
    required this.sortOrder,
    required this.onSortTap,
  });

  final int totalCount;
  final int criticalCount;
  final SpamSortOrder sortOrder;
  final VoidCallback onSortTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    const criticalRed = Color(0xFFC62828);

    return SliverAppBar.large(
      pinned: true,
      floating: false,
      backgroundColor: cs.surface,
      surfaceTintColor: cs.surfaceTint,
      leading: IconButton(
        icon: const Icon(Icons.arrow_back_rounded),
        onPressed: () => context.canPop() ? context.pop() : null,
        tooltip: 'Back',
      ),
      title: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.folder_special_rounded, color: criticalRed, size: 22),
          const SizedBox(width: 8),
          const Text('Spam Folder'),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.sort_rounded),
          tooltip: 'Sort messages',
          onPressed: onSortTap,
        ),
        IconButton(
          icon: const Icon(Icons.search_rounded),
          tooltip: 'Search spam',
          onPressed: () {
            // Search – future implementation
          },
        ),
        const SizedBox(width: 4),
      ],
      flexibleSpace: FlexibleSpaceBar(
        background: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.end,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: [
                  _StatPill(
                    label: '$totalCount quarantined',
                    icon: Icons.folder_special_rounded,
                    color: criticalRed,
                  ),
                  if (criticalCount > 0)
                    _StatPill(
                      label: '$criticalCount critical',
                      icon: Icons.dangerous_rounded,
                      color: criticalRed,
                    ),
                  if (criticalCount == 0)
                    _StatPill(
                      label: 'AI Protected',
                      icon: Icons.shield_rounded,
                      color: const Color(0xFF2E7D32),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatPill extends StatelessWidget {
  const _StatPill({
    required this.label,
    required this.icon,
    required this.color,
  });

  final String label;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(100),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 6),
          Text(
            label,
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w600,
                ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _FilterBarDelegate
// ─────────────────────────────────────────────────────────────────────────────

class _FilterBarDelegate extends SliverPersistentHeaderDelegate {
  const _FilterBarDelegate({required this.child});

  final Widget child;

  @override
  double get minExtent => 61;
  @override
  double get maxExtent => 61;

  @override
  Widget build(
    BuildContext context,
    double shrinkOffset,
    bool overlapsContent,
  ) =>
      child;

  @override
  bool shouldRebuild(_FilterBarDelegate old) => old.child != child;
}

// ─────────────────────────────────────────────────────────────────────────────
// _GroupedMessageList
// ─────────────────────────────────────────────────────────────────────────────

class _GroupedMessageList extends StatelessWidget {
  const _GroupedMessageList({required this.grouped});

  final Map<SpamRiskLevel, List<Conversation<SpamMessage>>> grouped;

  @override
  Widget build(BuildContext context) {
    final items = <_ListItem>[];
    for (final entry in grouped.entries) {
      items.add(_ListItem.header(entry.key, entry.value.length));
      for (var i = 0; i < entry.value.length; i++) {
        items.add(_ListItem.tile(entry.value[i], i));
      }
    }

    return SliverPadding(
      padding: const EdgeInsets.only(bottom: 32),
      sliver: SliverList.builder(
        itemCount: items.length,
        itemBuilder: (context, index) {
          final item = items[index];
          if (item.isHeader) {
            return SpamSectionHeader(
              riskLevel: item.riskLevel ?? SpamRiskLevel.medium,
              count: item.headerCount ?? 0,
            );
          }
          final conv = item.conversation!;
          return _buildTile(
            context,
            conv,
            item.tileIndex ?? 0,
          );
        },
      ),
    );
  }

  Widget _buildTile(BuildContext context, Conversation<SpamMessage> conversation, int index) {
    return _AnimatedTile(
      key: ValueKey(conversation.sender),
      index: index,
      child: Column(
        children: [
          GestureDetector(
            onLongPress: () => _longPress(context, conversation),
            child: SpamConversationTile(
              conversation: conversation,
              onTap: () => _onTap(context, conversation),
              onRestore: () => _restore(context, conversation),
              onDelete: () => _confirmAndDelete(context, conversation),
              onBlock: () => _block(context, conversation.latestMessage.id),
            ),
          ),
          Divider(
            indent: 76,
            endIndent: 16,
            height: 1,
            thickness: 0.8,
            color: Theme.of(context)
                .colorScheme
                .outlineVariant
                .withValues(alpha: 0.35),
          ),
        ],
      ),
    );
  }

  void _onTap(BuildContext context, Conversation<SpamMessage> conversation) {
    context.push(
      AppRoutes.conversation,
      extra: {
        'sender': conversation.sender,
        'isSpam': true,
      },
    );
  }

  void _navigateToAnalysis(BuildContext context, SpamMessage spam) {
    final sms = SmsMessage(
      id: spam.id,
      sender: spam.sender,
      body: spam.body,
      timestamp: spam.timestamp,
      aiStatus: _mapRiskToStatus(spam.riskLevel),
      isRead: true,
      confidenceScore: spam.aiConfidence,
      detectedThreats: spam.detectedThreats,
    );
    context.push(AppRoutes.analysis, extra: sms);
  }

  AiStatus _mapRiskToStatus(SpamRiskLevel level) {
    switch (level) {
      case SpamRiskLevel.critical:
      case SpamRiskLevel.high:
        return AiStatus.scam;
      case SpamRiskLevel.medium:
        return AiStatus.suspicious;
    }
  }

  void _longPress(BuildContext context, Conversation<SpamMessage> conversation) {
    SpamActionSheet.show(
      context: context,
      message: conversation.latestMessage,
      onRestore: () => _restore(context, conversation),
      onBlock: () => _block(context, conversation.latestMessage.id),
      onViewAnalysis: () => _navigateToAnalysis(context, conversation.latestMessage),
      onDelete: () => _confirmConversationDelete(context, conversation),
    );
  }

  void _restore(BuildContext context, Conversation<SpamMessage> conversation) {
    context.read<SpamProvider>().restoreConversationToInbox(conversation.sender);
    _showSnackBar(context, 'Conversation restored to Inbox', Icons.restore_rounded,
        const Color(0xFF2E7D32));
  }

  void _block(BuildContext context, String id) {
    context.read<SpamProvider>().blockSender(id);
    _showSnackBar(context, 'Sender blocked', Icons.block_rounded,
        const Color(0xFFE65100));
  }

  void _delete(BuildContext context, Conversation<SpamMessage> conversation) {
    context.read<SpamProvider>().deleteConversation(conversation.sender);
    _showSnackBar(context, 'Conversation deleted permanently',
        Icons.delete_forever_rounded, Theme.of(context).colorScheme.error);
  }

  void _confirmConversationDelete(BuildContext context, Conversation<SpamMessage> conversation) {
    showDialog<void>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        icon: const Icon(Icons.delete_forever_rounded, size: 32),
        iconColor: Theme.of(dialogCtx).colorScheme.error,
        title: const Text('Delete permanently?'),
        content: Text(
          'All messages in the conversation from "${conversation.sender}" '
          'will be removed permanently.',
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
              _delete(context, conversation);
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _confirmAndDelete(BuildContext context, Conversation<SpamMessage> conversation) {
    _confirmConversationDelete(context, conversation);
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
// _ListItem – union type for headers and tiles
// ─────────────────────────────────────────────────────────────────────────────

class _ListItem {
  _ListItem.header(SpamRiskLevel level, int count)
      : isHeader = true,
        riskLevel = level,
        headerCount = count,
        conversation = null,
        tileIndex = null;

  _ListItem.tile(Conversation<SpamMessage> conv, int index)
      : isHeader = false,
        riskLevel = null,
        headerCount = null,
        conversation = conv,
        tileIndex = index;

  final bool isHeader;
  final SpamRiskLevel? riskLevel;
  final int? headerCount;
  final Conversation<SpamMessage>? conversation;
  final int? tileIndex;
}

// ─────────────────────────────────────────────────────────────────────────────
// _AnimatedTile – staggered entrance animation
// ─────────────────────────────────────────────────────────────────────────────

class _AnimatedTile extends StatefulWidget {
  const _AnimatedTile({
    super.key,
    required this.index,
    required this.child,
  });

  final int index;
  final Widget child;

  @override
  State<_AnimatedTile> createState() => _AnimatedTileState();
}

class _AnimatedTileState extends State<_AnimatedTile>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _fade;
  late final Animation<Offset> _slide;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 350),
    );
    _fade = CurvedAnimation(parent: _ctrl, curve: Curves.easeOut);
    _slide = Tween<Offset>(
      begin: const Offset(0, 0.06),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));

    Future.delayed(
      Duration(milliseconds: 40 * (widget.index.clamp(0, 10))),
      () {
        if (mounted) _ctrl.forward();
      },
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fade,
      child: SlideTransition(position: _slide, child: widget.child),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SortSheet
// ─────────────────────────────────────────────────────────────────────────────

class _SortSheet extends StatelessWidget {
  const _SortSheet({
    required this.currentOrder,
    required this.onSelected,
  });

  final SpamSortOrder currentOrder;
  final ValueChanged<SpamSortOrder> onSelected;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Handle
            Center(
              child: Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(
                  color: cs.outlineVariant,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(bottom: 12, left: 4),
              child: Text(
                'Sort Messages',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
            ...SpamSortOrder.values.map((order) {
              final isSelected = order == currentOrder;
              return ListTile(
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                leading: Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: isSelected
                        ? cs.primaryContainer
                        : cs.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    _orderIcon(order),
                    size: 20,
                    color: isSelected ? cs.primary : cs.onSurface,
                  ),
                ),
                title: Text(
                  order.label,
                  style: TextStyle(
                    fontWeight:
                        isSelected ? FontWeight.w600 : FontWeight.normal,
                    color: isSelected ? cs.primary : null,
                  ),
                ),
                trailing: isSelected
                    ? Icon(Icons.check_circle_rounded, color: cs.primary)
                    : null,
                onTap: () => onSelected(order),
              );
            }),
          ],
        ),
      ),
    );
  }

  IconData _orderIcon(SpamSortOrder order) {
    switch (order) {
      case SpamSortOrder.newestFirst:
        return Icons.schedule_rounded;
      case SpamSortOrder.highestConfidence:
        return Icons.bar_chart_rounded;
      case SpamSortOrder.senderAZ:
        return Icons.sort_by_alpha_rounded;
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// States: Loading / Error / Empty
// ─────────────────────────────────────────────────────────────────────────────

class _LoadingState extends StatelessWidget {
  const _LoadingState();

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircularProgressIndicator(color: cs.primary),
          const SizedBox(height: 20),
          Text(
            'Scanning spam folder…',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.6),
                ),
          ),
        ],
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 56, color: cs.error),
            const SizedBox(height: 16),
            Text(
              'Something went wrong',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.55),
                  ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.filter});

  final SpamFilter filter;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final (icon, title, subtitle) = _content(filter);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFFC62828).withValues(alpha: 0.08),
              ),
              child: Icon(icon, size: 38, color: const Color(0xFFC62828)),
            ),
            const SizedBox(height: 20),
            Text(
              title,
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.55),
                  ),
            ),
          ],
        ),
      ),
    );
  }

  (IconData, String, String) _content(SpamFilter f) {
    switch (f) {
      case SpamFilter.all:
        return (
          Icons.folder_special_rounded,
          'Spam folder is empty',
          'MindShield has not quarantined any messages yet.',
        );
      case SpamFilter.critical:
        return (
          Icons.dangerous_rounded,
          'No critical threats',
          'No messages with critical risk have been quarantined.',
        );
      case SpamFilter.high:
        return (
          Icons.warning_rounded,
          'No high-risk messages',
          'No high-risk messages are currently quarantined.',
        );
      case SpamFilter.medium:
        return (
          Icons.info_outline_rounded,
          'No medium-risk messages',
          'No medium-risk messages are currently quarantined.',
        );
    }
  }
}
