import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'history_provider.dart';
import 'widgets/history_card.dart';
import '../../inbox/domain/sms_message.dart';

/// History screen – a chronological log of all past AI scan results,
/// filterable by threat type, searchable, and sortable.
class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => HistoryProvider(),
      child: const _HistoryScreenContent(),
    );
  }
}

class _HistoryScreenContent extends StatelessWidget {
  const _HistoryScreenContent();

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<HistoryProvider>();
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Scaffold(
      backgroundColor: cs.surface,
      appBar: AppBar(
        title: const Text('Analysis History'),
        actions: [
          IconButton(
            icon: Icon(
              provider.isSortAscending ? Icons.arrow_upward : Icons.arrow_downward,
            ),
            tooltip: 'Toggle Sort Order',
            onPressed: () => provider.toggleSort(),
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(116),
          child: Column(
            children: [
              // Search Bar
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: SearchBar(
                  hintText: 'Search senders or messages...',
                  leading: const Icon(Icons.search_rounded),
                  elevation: WidgetStateProperty.all(0),
                  backgroundColor: WidgetStateProperty.all(
                    cs.surfaceContainerHighest.withValues(alpha: 0.5),
                  ),
                  onChanged: (query) => provider.setSearchQuery(query),
                ),
              ),
              // Filter Chips
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                child: Row(
                  children: [
                    _buildFilterChip(context, provider, null, 'All'),
                    const SizedBox(width: 8),
                    _buildFilterChip(context, provider, AiStatus.safe, 'Safe', Colors.green),
                    const SizedBox(width: 8),
                    _buildFilterChip(context, provider, AiStatus.suspicious, 'Suspicious', Colors.orange),
                    const SizedBox(width: 8),
                    _buildFilterChip(context, provider, AiStatus.scam, 'Scam', Colors.red),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? Center(child: Text(provider.errorMessage!, style: TextStyle(color: cs.error)))
              : provider.filteredMessages.isEmpty
                  ? _buildEmptyState(context)
                  : ListView.builder(
                      padding: const EdgeInsets.all(16.0),
                      itemCount: provider.filteredMessages.length,
                      itemBuilder: (context, index) {
                        return HistoryCard(message: provider.filteredMessages[index]);
                      },
                    ),
    );
  }

  Widget _buildFilterChip(
    BuildContext context,
    HistoryProvider provider,
    AiStatus? status,
    String label, [
    Color? baseColor,
  ]) {
    final isSelected = provider.filterStatus == status;
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    
    final activeColor = baseColor ?? cs.primary;

    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) => provider.setFilter(status),
      showCheckmark: false,
      selectedColor: activeColor.withValues(alpha: 0.2),
      labelStyle: TextStyle(
        color: isSelected ? activeColor : cs.onSurface,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
      side: BorderSide(
        color: isSelected ? activeColor : cs.outlineVariant,
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.history_rounded, size: 64, color: cs.onSurface.withValues(alpha: 0.3)),
          const SizedBox(height: 16),
          Text(
            'No history found',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                  color: cs.onSurface.withValues(alpha: 0.6),
                ),
          ),
        ],
      ),
    );
  }
}
