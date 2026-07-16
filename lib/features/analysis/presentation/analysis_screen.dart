import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../inbox/domain/sms_message.dart';
import 'analysis_provider.dart';
import 'widgets/threat_score_gauge.dart';
import 'widgets/confidence_bar.dart';
import 'widgets/attack_type_card.dart';
import 'widgets/lime_highlight_card.dart';
import 'widgets/ai_explanation_card.dart';
import 'widgets/sender_info_card.dart';
import 'widgets/recommendations_card.dart';
import 'widgets/action_buttons_bar.dart';

// ─────────────────────────────────────────────────────────────────────────────
// AnalysisScreen
// ─────────────────────────────────────────────────────────────────────────────

/// AI Threat Analysis Screen.
///
/// Accepts a [SmsMessage] via [GoRouterState.extra]. Scopes an
/// [AnalysisProvider] locally so the analysis lifecycle is tied to this screen.
///
/// Layout
/// ──────
/// ┌─ SliverAppBar (coloured hero) ──────────────────────┐
/// │  Verdict badge  │  Threat Gauge  │  Confidence bar   │
/// ├─ Content cards (lazy SliverList) ───────────────────┤
/// │  1. Attack Type & Psychological Tactics             │
/// │  2. LIME Highlighted Message Body                   │
/// │  3. AI Explanation                                  │
/// │  4. Sender Information                              │
/// │  5. Recommended Actions                             │
/// │  6. Disclaimer                                      │
/// └─ Bottom Action Bar ──────────────────────────────────┘
class AnalysisScreen extends StatelessWidget {
  const AnalysisScreen({super.key, this.message});

  final SmsMessage? message;

  @override
  Widget build(BuildContext context) {
    if (message == null) return const _NoMessageState();
    return ChangeNotifierProvider<AnalysisProvider>(
      create: (_) => AnalysisProvider()..loadAnalysis(message!),
      child: _AnalysisView(message: message!),
    );
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
    final provider = context.watch<AnalysisProvider>();
    final cfg = _StatusConfig.of(message.aiStatus);

    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: CustomScrollView(
        physics: const ClampingScrollPhysics(),
        slivers: [
          // ── Hero app bar ─────────────────────────────────────────────────
          _HeroAppBar(message: message, cfg: cfg),

          // ── Loading shimmer / content ────────────────────────────────────
          if (provider.isLoading)
            const SliverFillRemaining(child: _LoadingState())
          else if (provider.errorMessage != null)
            SliverFillRemaining(
              child: _ErrorState(error: provider.errorMessage!),
            )
          else if (provider.analysisResult != null) ...[
            // ── Gauge + Confidence ─────────────────────────────────────────
            SliverToBoxAdapter(
              child: _GaugeSection(
                cfg: cfg,
                threatScore: provider.analysisResult!.threatScore,
                confidencePercent: provider.analysisResult!.confidencePercent,
                modelVersion: provider.analysisResult!.modelVersion,
                processingMs: provider.analysisResult!.processingTimeMs,
              ),
            ),

            // ── Content cards ──────────────────────────────────────────────
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // 1. Attack Type & Tactics
                  _AnalysisCard(
                    title: 'Attack Classification',
                    icon: Icons.crisis_alert_rounded,
                    child: AttackTypeCard(
                      attackType: provider.analysisResult!.attackType,
                      tactics: provider.analysisResult!.psychologicalTactics,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // 2. LIME Highlighted Message Body
                  _AnalysisCard(
                    title: 'Message Body (LIME Analysis)',
                    icon: Icons.text_snippet_rounded,
                    child: LimeHighlightCard(
                      messageBody: message.body,
                      keywords: provider.analysisResult!.suspiciousKeywords,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // 3. AI Explanation
                  _AnalysisCard(
                    title: 'AI Reasoning',
                    icon: Icons.auto_awesome_rounded,
                    child: AiExplanationCard(
                      explanation: provider.analysisResult!.aiExplanation,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // 4. Sender Information
                  _AnalysisCard(
                    title: 'Sender Intelligence',
                    icon: Icons.person_search_rounded,
                    child: SenderInfoCard(
                      senderInfo: provider.analysisResult!.senderInfo,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // 5. Recommendations
                  _AnalysisCard(
                    title: 'Recommended Actions',
                    icon: Icons.tips_and_updates_rounded,
                    child: RecommendationsCard(
                      recommendations: provider.analysisResult!.recommendations,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // 6. Disclaimer
                  _DisclaimerNote(
                    modelVersion: provider.analysisResult!.modelVersion,
                    processingMs: provider.analysisResult!.processingTimeMs,
                    timestamp: provider.analysisResult!.analysisTimestamp,
                  ),
                ]),
              ),
            ),
          ],
        ],
      ),

      // ── Bottom action bar ─────────────────────────────────────────────────
      bottomNavigationBar: provider.analysisResult != null
          ? ActionButtonsBar(aiStatus: message.aiStatus)
          : null,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _HeroAppBar
// ─────────────────────────────────────────────────────────────────────────────

class _HeroAppBar extends StatelessWidget {
  const _HeroAppBar({required this.message, required this.cfg});

  final SmsMessage message;
  final _StatusConfig cfg;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return SliverAppBar.large(
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
        style: TextStyle(
          color: cfg.heroForeground,
          fontWeight: FontWeight.w700,
        ),
      ),
      actions: [
        IconButton(
          icon: Icon(Icons.share_rounded, color: cfg.heroForeground),
          tooltip: 'Share report',
          onPressed: () {
            // Future: share analysis as PDF
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Share report coming soon')),
            );
          },
        ),
      ],
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                cfg.heroBackground.withValues(alpha: 0.95),
                cfg.heroBackground,
              ],
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 60, 20, 16),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Status row
                  Row(
                    children: [
                      Container(
                        width: 46,
                        height: 46,
                        decoration: BoxDecoration(
                          color: cfg.heroForeground.withValues(alpha: 0.15),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(cfg.icon,
                            color: cfg.heroForeground, size: 24),
                      ),
                      const SizedBox(width: 12),
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
                              color:
                                  cfg.heroForeground.withValues(alpha: 0.75),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  // Sender & time row
                  Row(
                    children: [
                      Icon(Icons.person_rounded,
                          size: 13,
                          color: cfg.heroForeground.withValues(alpha: 0.7)),
                      const SizedBox(width: 5),
                      Expanded(
                        child: Text(
                          'From: ${message.sender}',
                          style: theme.textTheme.bodySmall!.copyWith(
                            color: cfg.heroForeground.withValues(alpha: 0.75),
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Icon(Icons.schedule_rounded,
                          size: 13,
                          color: cfg.heroForeground.withValues(alpha: 0.7)),
                      const SizedBox(width: 5),
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
            ),
          ),
        ),
      ),
    );
  }

  String _formatFull(DateTime ts) {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    final h = ts.hour.toString().padLeft(2, '0');
    final m = ts.minute.toString().padLeft(2, '0');
    return '${ts.day} ${months[ts.month - 1]} · $h:$m';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _GaugeSection
// ─────────────────────────────────────────────────────────────────────────────

/// Section containing the threat score gauge and confidence bar.
class _GaugeSection extends StatelessWidget {
  const _GaugeSection({
    required this.cfg,
    required this.threatScore,
    required this.confidencePercent,
    required this.modelVersion,
    required this.processingMs,
  });

  final _StatusConfig cfg;
  final int threatScore;
  final int confidencePercent;
  final String modelVersion;
  final int processingMs;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: cs.shadow.withValues(alpha: 0.07),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.2)),
      ),
      child: Column(
        children: [
          // Gauge
          ThreatScoreGauge(score: threatScore, size: 210),
          const SizedBox(height: 20),
          const Divider(height: 1),
          const SizedBox(height: 20),
          // Confidence bar
          ConfidenceBar(confidencePercent: confidencePercent),
          const SizedBox(height: 14),
          // Model metadata
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _MetaChip(
                icon: Icons.memory_rounded,
                label: modelVersion,
              ),
              _MetaChip(
                icon: Icons.timer_rounded,
                label: '${processingMs}ms',
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetaChip extends StatelessWidget {
  const _MetaChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 12, color: cs.onSurface.withValues(alpha: 0.4)),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall!.copyWith(
                color: cs.onSurface.withValues(alpha: 0.45),
              ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _AnalysisCard  – reusable section card wrapper
// ─────────────────────────────────────────────────────────────────────────────

/// Reusable card wrapper used for every content section.
/// Provides a consistent section header (icon + title) and card styling.
class _AnalysisCard extends StatelessWidget {
  const _AnalysisCard({
    required this.title,
    required this.icon,
    required this.child,
  });

  final String title;
  final IconData icon;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: cs.outlineVariant.withValues(alpha: 0.25)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Section header
            Row(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: cs.primaryContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, size: 17, color: cs.onPrimaryContainer),
                ),
                const SizedBox(width: 10),
                Text(
                  title,
                  style: theme.textTheme.titleSmall!.copyWith(
                    fontWeight: FontWeight.w700,
                    color: cs.onSurface,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            const Divider(height: 1),
            const SizedBox(height: 16),
            child,
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _DisclaimerNote
// ─────────────────────────────────────────────────────────────────────────────

class _DisclaimerNote extends StatelessWidget {
  const _DisclaimerNote({
    required this.modelVersion,
    required this.processingMs,
    required this.timestamp,
  });

  final String modelVersion;
  final int processingMs;
  final DateTime timestamp;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final theme = Theme.of(context);
    final tsStr =
        '${timestamp.toLocal().toString().substring(0, 16)} UTC';

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cs.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.info_outline_rounded,
                  size: 16, color: cs.onSurface.withValues(alpha: 0.45)),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  'AI analysis is indicative and not infallible. Always exercise personal judgement when interacting with unexpected messages. '
                  'Results are based on pattern recognition and may produce false positives or negatives.',
                  style: theme.textTheme.bodySmall!.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.5),
                    height: 1.5,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 12,
            children: [
              _DisclaimerMeta(label: 'Model: $modelVersion'),
              _DisclaimerMeta(label: 'Inference: ${processingMs}ms'),
              _DisclaimerMeta(label: 'Analysed: $tsStr'),
            ],
          ),
        ],
      ),
    );
  }
}

class _DisclaimerMeta extends StatelessWidget {
  const _DisclaimerMeta({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: Theme.of(context).textTheme.labelSmall!.copyWith(
            color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.35),
            fontFamily: 'monospace',
          ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _LoadingState
// ─────────────────────────────────────────────────────────────────────────────

class _LoadingState extends StatefulWidget {
  const _LoadingState();

  @override
  State<_LoadingState> createState() => _LoadingStateState();
}

class _LoadingStateState extends State<_LoadingState>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _pulse;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    )..repeat(reverse: true);
    _pulse = CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          ScaleTransition(
            scale: Tween<double>(begin: 0.9, end: 1.1).animate(_pulse),
            child: Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: cs.primaryContainer,
              ),
              child: Icon(
                Icons.analytics_rounded,
                size: 40,
                color: cs.primary,
              ),
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Analysing Message…',
            style: Theme.of(context).textTheme.titleMedium!.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Running NLP threat detection pipeline',
            style: Theme.of(context).textTheme.bodySmall!.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.5),
                ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: 180,
            child: LinearProgressIndicator(
              borderRadius: BorderRadius.circular(100),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _ErrorState
// ─────────────────────────────────────────────────────────────────────────────

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error});

  final String error;

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
              'Analysis Failed',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium!
                  .copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            Text(
              error,
              style: Theme.of(context).textTheme.bodySmall!.copyWith(
                    color: cs.onSurface.withValues(alpha: 0.6),
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: () {
                final provider = context.read<AnalysisProvider>();
                if (provider.currentMessage != null) {
                  provider.loadAnalysis(provider.currentMessage!);
                }
              },
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
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
  });

  final Color heroBackground;
  final Color heroForeground;
  final IconData icon;
  final String verdictLabel;
  final String verdictSubtitle;

  factory _StatusConfig.of(AiStatus status) {
    switch (status) {
      case AiStatus.safe:
        return const _StatusConfig(
          heroBackground: Color(0xFF2E7D32),
          heroForeground: Colors.white,
          icon: Icons.verified_rounded,
          verdictLabel: 'Safe Message',
          verdictSubtitle: 'No threats detected',
        );
      case AiStatus.suspicious:
        return const _StatusConfig(
          heroBackground: Color(0xFFE65100),
          heroForeground: Colors.white,
          icon: Icons.warning_amber_rounded,
          verdictLabel: 'Suspicious Message',
          verdictSubtitle: 'Review carefully before acting',
        );
      case AiStatus.scam:
        return const _StatusConfig(
          heroBackground: Color(0xFFC62828),
          heroForeground: Colors.white,
          icon: Icons.dangerous_rounded,
          verdictLabel: 'Confirmed Scam',
          verdictSubtitle: 'Do not interact with this message',
        );
    }
  }
}
