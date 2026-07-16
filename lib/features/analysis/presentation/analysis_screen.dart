import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../inbox/domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// AnalysisScreen
// ─────────────────────────────────────────────────────────────────────────────

/// Analysis screen – shows the AI analysis detail for a single SMS message:
/// sender info, full message body, confidence score, detected threat
/// categories, risk level, and actionable recommendations.
///
/// Accepts a [SmsMessage] via [GoRouterState.extra]. If [message] is null
/// (e.g. navigated directly without context) a fallback empty-state is shown.
///
/// Will later be powered by an [AnalysisProvider] that calls the Dio AI
/// backend for real-time analysis results.
class AnalysisScreen extends StatelessWidget {
  const AnalysisScreen({super.key, this.message});

  final SmsMessage? message;

  @override
  Widget build(BuildContext context) {
    if (message == null) return const _NoMessageState();
    return _AnalysisView(message: message!);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _AnalysisView
// ─────────────────────────────────────────────────────────────────────────────

class _AnalysisView extends StatelessWidget {
  const _AnalysisView({required this.message});

  final SmsMessage message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final cfg = _StatusConfig.of(message.aiStatus);

    return Scaffold(
      backgroundColor: cs.surface,
      body: CustomScrollView(
        slivers: [
          // ── Coloured hero app bar ─────────────────────────────────────────
          SliverAppBar.large(
            pinned: true,
            backgroundColor: cfg.heroBackground,
            surfaceTintColor: Colors.transparent,
            foregroundColor: cfg.heroForeground,
            leading: IconButton(
              icon: Icon(Icons.arrow_back_rounded, color: cfg.heroForeground),
              onPressed: () => context.pop(),
              tooltip: 'Back to Inbox',
            ),
            title: Text(
              'Analysis Report',
              style: TextStyle(color: cfg.heroForeground),
            ),
            flexibleSpace: FlexibleSpaceBar(
              background: _HeroContent(message: message, cfg: cfg),
            ),
          ),

          // ── Content cards ─────────────────────────────────────────────────
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Verdict card
                _VerdictCard(message: message, cfg: cfg),
                const SizedBox(height: 16),

                // Confidence score
                if (message.confidenceScore != null) ...[
                  _ConfidenceCard(score: message.confidenceScore!),
                  const SizedBox(height: 16),
                ],

                // Detected threats
                if (message.detectedThreats.isNotEmpty) ...[
                  _ThreatsCard(threats: message.detectedThreats),
                  const SizedBox(height: 16),
                ],

                // Full message body
                _MessageBodyCard(message: message),
                const SizedBox(height: 16),

                // Recommendations
                _RecommendationsCard(status: message.aiStatus),
                const SizedBox(height: 16),

                // Disclaimer
                _DisclaimerNote(),
              ]),
            ),
          ),
        ],
      ),

      // ── Bottom action bar ─────────────────────────────────────────────────
      bottomNavigationBar: _ActionBar(message: message, cfg: cfg),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _HeroContent
// ─────────────────────────────────────────────────────────────────────────────

class _HeroContent extends StatelessWidget {
  const _HeroContent({required this.message, required this.cfg});

  final SmsMessage message;
  final _StatusConfig cfg;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status icon + label
          Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: cfg.heroForeground.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(cfg.icon, color: cfg.heroForeground, size: 26),
              ),
              const SizedBox(width: 14),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    cfg.verdictLabel,
                    style: theme.textTheme.headlineSmall!.copyWith(
                      color: cfg.heroForeground,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  Text(
                    cfg.verdictSubtitle,
                    style: theme.textTheme.bodySmall!.copyWith(
                      color: cfg.heroForeground.withValues(alpha: 0.75),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Sender info
          Row(
            children: [
              Icon(
                Icons.person_rounded,
                size: 14,
                color: cfg.heroForeground.withValues(alpha: 0.75),
              ),
              const SizedBox(width: 6),
              Expanded(
                child: Text(
                  'From: ${message.sender}',
                  style: theme.textTheme.bodySmall!.copyWith(
                    color: cfg.heroForeground.withValues(alpha: 0.75),
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 12),
              Icon(
                Icons.schedule_rounded,
                size: 14,
                color: cfg.heroForeground.withValues(alpha: 0.75),
              ),
              const SizedBox(width: 6),
              Text(
                _formatFull(message.timestamp),
                style: theme.textTheme.bodySmall!.copyWith(
                  color: cfg.heroForeground.withValues(alpha: 0.75),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatFull(DateTime ts) {
    final months = [
      'Jan','Feb','Mar','Apr','May','Jun',
      'Jul','Aug','Sep','Oct','Nov','Dec',
    ];
    final h = ts.hour.toString().padLeft(2, '0');
    final m = ts.minute.toString().padLeft(2, '0');
    return '${ts.day} ${months[ts.month - 1]} · $h:$m';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _VerdictCard
// ─────────────────────────────────────────────────────────────────────────────

class _VerdictCard extends StatelessWidget {
  const _VerdictCard({required this.message, required this.cfg});

  final SmsMessage message;
  final _StatusConfig cfg;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionTitle(label: 'AI Verdict', icon: Icons.auto_awesome_rounded),
            const SizedBox(height: 14),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: cfg.heroBackground.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: cfg.heroBackground.withValues(alpha: 0.25),
                ),
              ),
              child: Row(
                children: [
                  Icon(cfg.icon, color: cfg.heroBackground, size: 32),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          cfg.verdictLabel,
                          style: theme.textTheme.titleMedium!.copyWith(
                            fontWeight: FontWeight.w700,
                            color: cfg.heroBackground,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          cfg.verdictDescription,
                          style: theme.textTheme.bodySmall!.copyWith(
                            color: theme.colorScheme.onSurface.withValues(alpha: 0.65),
                            height: 1.4,
                          ),
                        ),
                      ],
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
}

// ─────────────────────────────────────────────────────────────────────────────
// _ConfidenceCard
// ─────────────────────────────────────────────────────────────────────────────

class _ConfidenceCard extends StatefulWidget {
  const _ConfidenceCard({required this.score});

  final double score;

  @override
  State<_ConfidenceCard> createState() => _ConfidenceCardState();
}

class _ConfidenceCardState extends State<_ConfidenceCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    );
    _anim = CurvedAnimation(parent: _ctrl, curve: Curves.easeOutCubic);
    _ctrl.forward();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final pct = (widget.score * 100).round();

    final barColor = widget.score >= 0.9
        ? const Color(0xFFC62828)
        : widget.score >= 0.75
            ? const Color(0xFFE65100)
            : const Color(0xFF2E7D32);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionTitle(
              label: 'AI Confidence',
              icon: Icons.bar_chart_rounded,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: AnimatedBuilder(
                    animation: _anim,
                    builder: (context, _) => Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(100),
                          child: LinearProgressIndicator(
                            value: _anim.value * widget.score,
                            minHeight: 12,
                            backgroundColor: cs.outlineVariant.withValues(alpha: 0.25),
                            valueColor:
                                AlwaysStoppedAnimation<Color>(barColor),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'Model is ${(_anim.value * pct).round()}% confident in this classification',
                          style: theme.textTheme.bodySmall!.copyWith(
                            color: cs.onSurface.withValues(alpha: 0.55),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Text(
                  '$pct%',
                  style: theme.textTheme.headlineMedium!.copyWith(
                    fontWeight: FontWeight.w800,
                    color: barColor,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ThreatsCard
// ─────────────────────────────────────────────────────────────────────────────

class _ThreatsCard extends StatelessWidget {
  const _ThreatsCard({required this.threats});

  final List<String> threats;

  String _humanize(String tag) =>
      tag.replaceAll('_', ' ').split(' ').map((w) {
        if (w.isEmpty) return w;
        return w[0].toUpperCase() + w.substring(1);
      }).join(' ');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionTitle(
              label: 'Detected Threats',
              icon: Icons.bug_report_rounded,
            ),
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: threats.map((t) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 7,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFEBEE),
                    borderRadius: BorderRadius.circular(100),
                    border: Border.all(color: const Color(0xFFEF9A9A)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.warning_amber_rounded,
                        size: 13,
                        color: Color(0xFFC62828),
                      ),
                      const SizedBox(width: 5),
                      Text(
                        _humanize(t),
                        style: theme.textTheme.labelSmall!.copyWith(
                          color: const Color(0xFFC62828),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _MessageBodyCard
// ─────────────────────────────────────────────────────────────────────────────

class _MessageBodyCard extends StatelessWidget {
  const _MessageBodyCard({required this.message});

  final SmsMessage message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionTitle(label: 'Message Content', icon: Icons.sms_rounded),
            const SizedBox(height: 14),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: cs.surfaceContainerLow,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: cs.outlineVariant.withValues(alpha: 0.4),
                ),
              ),
              child: Text(
                message.body,
                style: theme.textTheme.bodyMedium!.copyWith(
                  height: 1.6,
                  color: cs.onSurface.withValues(alpha: 0.85),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _RecommendationsCard
// ─────────────────────────────────────────────────────────────────────────────

class _RecommendationsCard extends StatelessWidget {
  const _RecommendationsCard({required this.status});

  final AiStatus status;

  @override
  Widget build(BuildContext context) {
    final tips = _tips(status);
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionTitle(
              label: 'Recommendations',
              icon: Icons.tips_and_updates_rounded,
            ),
            const SizedBox(height: 14),
            ...tips.map(
              (tip) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.check_circle_rounded,
                      size: 18,
                      color: Color(0xFF1565C0),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        tip,
                        style: theme.textTheme.bodySmall!.copyWith(
                          height: 1.5,
                          color: theme.colorScheme.onSurface.withValues(alpha: 0.8),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<String> _tips(AiStatus s) {
    switch (s) {
      case AiStatus.safe:
        return [
          'This message appears safe. No immediate action required.',
          'Always verify links even from known contacts before tapping.',
          'MindShield continuously monitors new messages in the background.',
        ];
      case AiStatus.suspicious:
        return [
          'Do NOT tap any links or call numbers in this message.',
          'Verify the sender\'s identity through an official channel.',
          'Do not share personal information, passwords, or OTPs.',
          'Report the message to your network provider if unsolicited.',
        ];
      case AiStatus.scam:
        return [
          'Do NOT respond to this message or click any links.',
          'Block this number immediately using your phone\'s settings.',
          'Report the scam to the South African Police Service (SAPS) or your bank.',
          'Never share OTPs, ID numbers, or banking details via SMS.',
          'Warn friends and family who may receive similar messages.',
        ];
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _DisclaimerNote
// ─────────────────────────────────────────────────────────────────────────────

class _DisclaimerNote extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cs.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.info_outline_rounded,
              size: 16, color: cs.onSurface.withValues(alpha: 0.45)),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'AI analysis is indicative and not infallible. Always exercise personal judgement when interacting with unexpected messages.',
              style: Theme.of(context).textTheme.bodySmall!.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.45),
                    height: 1.5,
                  ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ActionBar
// ─────────────────────────────────────────────────────────────────────────────

class _ActionBar extends StatelessWidget {
  const _ActionBar({required this.message, required this.cfg});

  final SmsMessage message;
  final _StatusConfig cfg;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
        child: Row(
          children: [
            if (message.aiStatus != AiStatus.safe) ...[
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    // Block sender – future implementation
                  },
                  icon: const Icon(Icons.block_rounded, size: 18),
                  label: const Text('Block Sender'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: cs.error,
                    side: BorderSide(color: cs.error.withValues(alpha: 0.5)),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
              const SizedBox(width: 12),
            ],
            Expanded(
              child: FilledButton.icon(
                onPressed: () {
                  // Report – future implementation
                },
                icon: const Icon(Icons.flag_rounded, size: 18),
                label: Text(
                  message.aiStatus == AiStatus.safe
                      ? 'Mark as Spam'
                      : 'Report Scam',
                ),
                style: FilledButton.styleFrom(
                  backgroundColor: message.aiStatus == AiStatus.safe
                      ? cs.primary
                      : const Color(0xFFC62828),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _SectionTitle
// ─────────────────────────────────────────────────────────────────────────────

class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.label, required this.icon});

  final String label;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    return Row(
      children: [
        Icon(icon, size: 18, color: cs.primary),
        const SizedBox(width: 8),
        Text(
          label,
          style: theme.textTheme.titleSmall!.copyWith(
            fontWeight: FontWeight.w700,
            color: cs.onSurface,
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _NoMessageState
// ─────────────────────────────────────────────────────────────────────────────

class _NoMessageState extends StatelessWidget {
  const _NoMessageState();

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analysis'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.analytics_outlined, size: 64, color: cs.primary),
            const SizedBox(height: 16),
            Text(
              'No message selected',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium!
                  .copyWith(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            Text(
              'Navigate from the Inbox to analyse a message.',
              style: Theme.of(context).textTheme.bodySmall!.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.55),
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _StatusConfig – centralises colour/icon/copy per AiStatus
// ─────────────────────────────────────────────────────────────────────────────

class _StatusConfig {
  const _StatusConfig({
    required this.heroBackground,
    required this.heroForeground,
    required this.icon,
    required this.verdictLabel,
    required this.verdictSubtitle,
    required this.verdictDescription,
  });

  final Color heroBackground;
  final Color heroForeground;
  final IconData icon;
  final String verdictLabel;
  final String verdictSubtitle;
  final String verdictDescription;

  factory _StatusConfig.of(AiStatus status) {
    switch (status) {
      case AiStatus.safe:
        return const _StatusConfig(
          heroBackground: Color(0xFF2E7D32),
          heroForeground: Colors.white,
          icon: Icons.verified_rounded,
          verdictLabel: 'Safe Message',
          verdictSubtitle: 'No threats detected',
          verdictDescription:
              'Our AI model analysed this message and found no indicators of phishing, scam, or malicious content.',
        );
      case AiStatus.suspicious:
        return const _StatusConfig(
          heroBackground: Color(0xFFE65100),
          heroForeground: Colors.white,
          icon: Icons.warning_amber_rounded,
          verdictLabel: 'Suspicious Message',
          verdictSubtitle: 'Review carefully before acting',
          verdictDescription:
              'This message contains patterns that may indicate deceptive or manipulative intent. Proceed with caution.',
        );
      case AiStatus.scam:
        return const _StatusConfig(
          heroBackground: Color(0xFFC62828),
          heroForeground: Colors.white,
          icon: Icons.dangerous_rounded,
          verdictLabel: 'Scam Detected',
          verdictSubtitle: 'High-risk — do not interact',
          verdictDescription:
              'MindShield has identified this message as a confirmed scam or phishing attempt. Do not click links or share information.',
        );
    }
  }
}
