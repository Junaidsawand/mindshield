// lib/features/spam/presentation/widgets/spam_filter_bar.dart

import 'package:flutter/material.dart';
import '../spam_provider.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SpamFilterBar
// ─────────────────────────────────────────────────────────────────────────────

/// Horizontally scrollable row of [FilterChip]s for the Spam Folder.
///
/// Displays a count badge on each chip and highlights the active filter with
/// the theme's primary colour.
class SpamFilterBar extends StatelessWidget {
  const SpamFilterBar({
    super.key,
    required this.activeFilter,
    required this.countFor,
    required this.onFilterSelected,
  });

  final SpamFilter activeFilter;
  final int Function(SpamFilter) countFor;
  final ValueChanged<SpamFilter> onFilterSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: SpamFilter.values.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final filter = SpamFilter.values[index];
          final isActive = filter == activeFilter;
          final count = countFor(filter);
          return _SpamFilterChip(
            filter: filter,
            count: count,
            isActive: isActive,
            onTap: () => onFilterSelected(filter),
          );
        },
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SpamFilterChip
// ─────────────────────────────────────────────────────────────────────────────

class _SpamFilterChip extends StatelessWidget {
  const _SpamFilterChip({
    required this.filter,
    required this.count,
    required this.isActive,
    required this.onTap,
  });

  final SpamFilter filter;
  final int count;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final chipColor = _chipColor(filter, cs);

    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      curve: Curves.easeOut,
      decoration: BoxDecoration(
        color: isActive ? chipColor.withValues(alpha: 0.15) : Colors.transparent,
        borderRadius: BorderRadius.circular(100),
        border: Border.all(
          color: isActive
              ? chipColor
              : cs.outlineVariant.withValues(alpha: 0.6),
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
                style: Theme.of(context).textTheme.labelMedium!.copyWith(
                      color: isActive
                          ? chipColor
                          : cs.onSurface.withValues(alpha: 0.65),
                      fontWeight:
                          isActive ? FontWeight.w700 : FontWeight.w500,
                    ),
              ),
              const SizedBox(width: 6),
              // Count badge
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                decoration: BoxDecoration(
                  color: isActive
                      ? chipColor.withValues(alpha: 0.2)
                      : cs.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(100),
                ),
                child: Text(
                  '$count',
                  style: Theme.of(context).textTheme.labelSmall!.copyWith(
                        color: isActive
                            ? chipColor
                            : cs.onSurface.withValues(alpha: 0.5),
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _chipColor(SpamFilter f, ColorScheme cs) {
    switch (f) {
      case SpamFilter.all:
        return cs.primary;
      case SpamFilter.critical:
        return const Color(0xFFC62828);
      case SpamFilter.high:
        return const Color(0xFFE65100);
      case SpamFilter.medium:
        return const Color(0xFFF57F17);
    }
  }
}
