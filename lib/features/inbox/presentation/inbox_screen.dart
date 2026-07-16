import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../../core/router/app_router.dart';
import '../domain/sms_message.dart';
import '../domain/conversation.dart';
import 'inbox_provider.dart';

import 'widgets/inbox_filter_bar.dart';
import 'widgets/conversation_tile.dart';

// ─────────────────────────────────────────────────────────────────────────────
// InboxScreen
// ─────────────────────────────────────────────────────────────────────────────

/// Main Inbox screen.
///
/// Displays all received SMS messages with their AI-assigned risk labels.
/// Driven by [InboxProvider] via [Provider.of].
///
/// Navigation
/// ──────────
/// Tapping a tile calls [InboxProvider.markAsRead] then navigates to
/// [AppRoutes.analysis], passing the full [SmsMessage] via [GoRouter.extra].
class InboxScreen extends StatelessWidget {
  const InboxScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider<InboxProvider>(
      create: (_) => InboxProvider(),
      child: const _InboxView(),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _InboxView – the actual stateful content
// ─────────────────────────────────────────────────────────────────────────────

class _InboxView extends StatelessWidget {
  const _InboxView();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<InboxProvider>();

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: RefreshIndicator(
        onRefresh: () => provider.loadMessages(),
        child: CustomScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          slivers: [
            // ── Large collapsing app bar ───────────────────────────────────
            _InboxSliverAppBar(unreadCount: provider.unreadCount),

            // ── Filter chips ──────────────────────────────────────────────
            SliverPersistentHeader(
              pinned: true,
              delegate: _FilterBarDelegate(
                child: ColoredBox(
                  color: Theme.of(context).colorScheme.surface,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SizedBox(height: 10),
                      InboxFilterBar(
                        activeFilter: provider.activeFilter,
                        countFor: provider.countFor,
                        onFilterSelected: provider.setFilter,
                      ),
                      const SizedBox(height: 10),
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

            // ── Body: loading / error / empty / list ──────────────────────
            if (provider.isLoading)
              const SliverFillRemaining(
                child: _LoadingState(),
              )
            else if (provider.errorMessage != null)
              SliverFillRemaining(
                child: _ErrorState(
                  message: provider.errorMessage!,
                  onRetry: provider.loadMessages,
                ),
              )
            else if (provider.filteredConversations.isEmpty)
              SliverFillRemaining(
                child: _EmptyState(filter: provider.activeFilter),
              )
            else
              _MessageList(conversations: provider.filteredConversations),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _InboxSliverAppBar
// ─────────────────────────────────────────────────────────────────────────────

class _InboxSliverAppBar extends StatelessWidget {
  const _InboxSliverAppBar({required this.unreadCount});

  final int unreadCount;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

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
          Icon(Icons.shield_rounded, color: cs.primary, size: 22),
          const SizedBox(width: 8),
          const Text('Inbox'),
        ],
      ),
      actions: [
        // Unread badge on search icon
        Stack(
          alignment: Alignment.topRight,
          children: [
            IconButton(
              icon: const Icon(Icons.search_rounded),
              tooltip: 'Search messages',
              onPressed: () {
                // Search – future implementation
              },
            ),
          ],
        ),
        IconButton(
          icon: const Icon(Icons.tune_rounded),
          tooltip: 'Sort & filter',
          onPressed: () {
            // Advanced filter sheet – future implementation
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
              // Stats row
              Row(
                children: [
                  _StatPill(
                    label: '$unreadCount unread',
                    icon: Icons.mark_email_unread_rounded,
                    color: cs.primary,
                  ),
                  const SizedBox(width: 8),
                  _StatPill(
                    label: 'AI Protected',
                    icon: Icons.security_rounded,
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
            style: Theme.of(context).textTheme.labelSmall!.copyWith(
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
// _FilterBarDelegate – keeps the filter bar pinned below the AppBar
// ─────────────────────────────────────────────────────────────────────────────

class _FilterBarDelegate extends SliverPersistentHeaderDelegate {
  const _FilterBarDelegate({required this.child});

  final Widget child;

  @override
  double get minExtent => 65;
  @override
  double get maxExtent => 65;

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
// _MessageList
// ─────────────────────────────────────────────────────────────────────────────

class _MessageList extends StatelessWidget {
  const _MessageList({required this.conversations});

  final List<Conversation<SmsMessage>> conversations;

  @override
  Widget build(BuildContext context) {
    return SliverPadding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      sliver: SliverList.separated(
        itemCount: conversations.length,
        separatorBuilder: (_, __) => Divider(
          indent: 80,
          endIndent: 16,
          height: 1,
          thickness: 0.8,
          color:
              Theme.of(context).colorScheme.outlineVariant.withValues(alpha: 0.35),
        ),
        itemBuilder: (context, index) {
          final conv = conversations[index];
          return _AnimatedTile(
            key: ValueKey(conv.sender),
            index: index,
            child: ConversationTile(
              conversation: conv,
              onTap: () => _onTap(context, conv),
            ),
          );
        },
      ),
    );
  }

  void _onTap(BuildContext context, Conversation<SmsMessage> conversation) {
    context.read<InboxProvider>().markConversationAsRead(conversation.sender);
    context.push(
      AppRoutes.conversation,
      extra: {
        'sender': conversation.sender,
        'isSpam': false,
      },
    );
  }
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

    // Stagger by index (capped at 10 items to avoid long delays).
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
            'Scanning your inbox…',
            style: Theme.of(context).textTheme.bodyMedium!.copyWith(
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
                  .titleMedium!
                  .copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall!.copyWith(
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

  final InboxFilter filter;

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
                color: cs.primaryContainer.withValues(alpha: 0.5),
              ),
              child: Icon(icon, size: 38, color: cs.primary),
            ),
            const SizedBox(height: 20),
            Text(
              title,
              style: Theme.of(context)
                  .textTheme
                  .titleMedium!
                  .copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              subtitle,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall!.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.55),
                  ),
            ),
          ],
        ),
      ),
    );
  }

  (IconData, String, String) _content(InboxFilter f) {
    switch (f) {
      case InboxFilter.all:
        return (
          Icons.inbox_rounded,
          'No messages yet',
          'Your SMS inbox is empty.',
        );
      case InboxFilter.safe:
        return (
          Icons.verified_rounded,
          'No safe messages',
          'None of your messages were classified as safe yet.',
        );
      case InboxFilter.suspicious:
        return (
          Icons.warning_amber_rounded,
          'No suspicious messages',
          'Great news – no suspicious messages found.',
        );
      case InboxFilter.scam:
        return (
          Icons.dangerous_rounded,
          'No scam messages',
          'MindShield hasn\'t detected any scams.',
        );
    }
  }
}
