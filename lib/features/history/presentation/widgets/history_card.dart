import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../inbox/domain/sms_message.dart';
import '../../../../core/router/app_router.dart';

/// A card displaying a brief summary of a previously analyzed SMS message.
class HistoryCard extends StatelessWidget {
  const HistoryCard({
    super.key,
    required this.message,
  });

  final SmsMessage message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    
    // Config based on AI Status
    final statusColor = _getStatusColor(message.aiStatus);
    final statusIcon = _getStatusIcon(message.aiStatus);

    return Card(
      elevation: 0,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.3)),
      ),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () {
          context.push(AppRoutes.analysis, extra: message);
        },
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: Sender & Timestamp
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      message.sender,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _formatDate(message.timestamp),
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: cs.onSurface.withValues(alpha: 0.6),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              
              // Body Preview
              Text(
                message.body,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.8),
                ),
              ),
              const SizedBox(height: 16),
              
              // Footer: Status Badge, Confidence, Attack Type
              Row(
                children: [
                  // Verdict Badge
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: statusColor.withValues(alpha: 0.3)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(statusIcon, size: 14, color: statusColor),
                        const SizedBox(width: 4),
                        Text(
                          message.aiStatus.label,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: statusColor,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  
                  // Confidence Score
                  if (message.confidenceScore != null)
                    Row(
                      children: [
                        Icon(Icons.analytics_rounded, size: 14, color: cs.onSurface.withValues(alpha: 0.5)),
                        const SizedBox(width: 4),
                        Text(
                          '${(message.confidenceScore! * 100).toInt()}% Conf.',
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: cs.onSurface.withValues(alpha: 0.6),
                          ),
                        ),
                      ],
                    ),
                  
                  const Spacer(),
                  
                  // Attack Type
                  if (message.detectedThreats.isNotEmpty)
                    Row(
                      children: [
                        Icon(Icons.bug_report_rounded, size: 14, color: cs.error),
                        const SizedBox(width: 4),
                        Text(
                          _formatThreatType(message.detectedThreats.first),
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: cs.error,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${dt.day}/${dt.month}/${dt.year}';
  }

  String _formatThreatType(String threat) {
    // Basic formatting: "malicious_url" -> "Malicious Url"
    final words = threat.split('_');
    final capitalized = words.map((w) {
      if (w.isEmpty) return '';
      return w[0].toUpperCase() + w.substring(1);
    });
    return capitalized.join(' ');
  }

  Color _getStatusColor(AiStatus status) {
    switch (status) {
      case AiStatus.safe:
        return const Color(0xFF2E7D32);
      case AiStatus.suspicious:
        return const Color(0xFFE65100);
      case AiStatus.scam:
        return const Color(0xFFC62828);
    }
  }

  IconData _getStatusIcon(AiStatus status) {
    switch (status) {
      case AiStatus.safe:
        return Icons.verified_rounded;
      case AiStatus.suspicious:
        return Icons.warning_amber_rounded;
      case AiStatus.scam:
        return Icons.dangerous_rounded;
    }
  }
}
