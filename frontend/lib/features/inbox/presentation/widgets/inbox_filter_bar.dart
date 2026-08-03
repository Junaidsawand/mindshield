import 'package:flutter/material.dart';
import '../inbox_provider.dart';


// ─────────────────────────────────────────────────────────────────────────────
// InboxFilterBar
// ─────────────────────────────────────────────────────────────────────────────

/// Horizontally-scrollable filter chip bar for the Inbox screen.
///
/// Displays a chip for each [InboxFilter] value, with message counts.
/// The active chip uses the [ColorScheme.primary] colour.
class InboxFilterBar extends StatelessWidget {
  const InboxFilterBar({
    super.key,
    required this.activeFilter,
    required this.countFor,
    required this.onFilterSelected,
  });

  final InboxFilter activeFilter;
  final int Function(InboxFilter) countFor;
  final ValueChanged<InboxFilter> onFilterSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: InboxFilter.values.map((filter) {
          final isActive = filter == activeFilter;
          final count = countFor(filter);
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: _FilterChip(
              filter: filter,
              count: count,
              isActive: isActive,
              onTap: () => onFilterSelected(filter),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.filter,
    required this.count,
    required this.isActive,
    required this.onTap,
  });

  final InboxFilter filter;
  final int count;
  final bool isActive;
  final VoidCallback onTap;

  Color _activeColor(InboxFilter f) {
    switch (f) {
      case InboxFilter.safe:
        return const Color(0xFF2E7D32);
      case InboxFilter.suspicious:
        return const Color(0xFFE65100);
      case InboxFilter.scam:
        return const Color(0xFFC62828);
      case InboxFilter.all:
        return const Color(0xFF1565C0);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final color = isActive ? _activeColor(filter) : cs.onSurface;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      curve: Curves.easeInOut,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(100),
        color: isActive ? color.withValues(alpha: 0.12) : cs.surfaceContainerLow,
        border: Border.all(
          color: isActive ? color : cs.outline.withValues(alpha: 0.4),
          width: isActive ? 1.5 : 1,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(100),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                filter.label,
                style: theme.textTheme.labelMedium!.copyWith(
                  color: isActive ? color : cs.onSurface.withValues(alpha: 0.6),
                  fontWeight:
                      isActive ? FontWeight.w700 : FontWeight.w500,
                ),
              ),
              if (count > 0) ...[
                const SizedBox(width: 6),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: isActive ? color : cs.onSurface.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(100),
                  ),
                  child: Text(
                    '$count',
                    style: theme.textTheme.labelSmall!.copyWith(
                      color:
                          isActive ? Colors.white : cs.onSurface.withValues(alpha: 0.6),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
