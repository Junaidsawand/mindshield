import 'dart:math' as math;
import 'package:flutter/material.dart';

// ─────────────────────────────────────────────────────────────────────────────
// ThreatScoreGauge
// ─────────────────────────────────────────────────────────────────────────────

/// Animated radial arc gauge displaying the AI threat score (0–100).
///
/// Uses a custom painter to draw a segmented arc with animated fill.
/// The needle sweeps from 0° to the target score over 1200 ms using
/// [Curves.easeOutBack] for a satisfying spring effect.
class ThreatScoreGauge extends StatefulWidget {
  const ThreatScoreGauge({
    super.key,
    required this.score,
    this.size = 200.0,
  });

  /// Threat score in the range 0–100.
  final int score;

  /// Diameter of the gauge widget.
  final double size;

  @override
  State<ThreatScoreGauge> createState() => _ThreatScoreGaugeState();
}

class _ThreatScoreGaugeState extends State<ThreatScoreGauge>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );
    _anim = CurvedAnimation(parent: _ctrl, curve: Curves.easeOutCubic);
    _ctrl.forward();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Color _scoreColor(int score) {
    if (score >= 80) return const Color(0xFFC62828);
    if (score >= 50) return const Color(0xFFE65100);
    if (score >= 20) return const Color(0xFFF9A825);
    return const Color(0xFF2E7D32);
  }

  String _scoreLabel(int score) {
    if (score >= 80) return 'HIGH RISK';
    if (score >= 50) return 'MEDIUM RISK';
    if (score >= 20) return 'LOW RISK';
    return 'SAFE';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = _scoreColor(widget.score);
    final label = _scoreLabel(widget.score);

    return SizedBox(
      width: widget.size,
      height: widget.size * 0.85,
      child: AnimatedBuilder(
        animation: _anim,
        builder: (context, _) {
          final animated = (_anim.value * widget.score).round();
          return CustomPaint(
            painter: _GaugePainter(
              score: _anim.value * widget.score / 100,
              color: color,
              bgColor: theme.colorScheme.outlineVariant.withValues(alpha: 0.2),
            ),
            child: Center(
              child: Padding(
                padding: EdgeInsets.only(top: widget.size * 0.12),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '$animated',
                      style: theme.textTheme.displaySmall!.copyWith(
                        fontWeight: FontWeight.w900,
                        color: color,
                        height: 1.0,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(100),
                      ),
                      child: Text(
                        label,
                        style: theme.textTheme.labelSmall!.copyWith(
                          color: color,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 1.2,
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Threat Score',
                      style: theme.textTheme.bodySmall!.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// _GaugePainter
// ─────────────────────────────────────────────────────────────────────────────

class _GaugePainter extends CustomPainter {
  _GaugePainter({
    required this.score,
    required this.color,
    required this.bgColor,
  });

  /// Normalised score (0.0–1.0).
  final double score;
  final Color color;
  final Color bgColor;

  static const double _startAngle = 150 * math.pi / 180;
  static const double _sweepTotal = 240 * math.pi / 180;
  static const double _strokeWidth = 16.0;
  static const double _tickCount = 10;

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height * 0.56);
    final radius = (math.min(size.width, size.height) / 2) - _strokeWidth / 2 - 4;

    final bgPaint = Paint()
      ..color = bgColor
      ..strokeWidth = _strokeWidth
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    // Background arc
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      _startAngle,
      _sweepTotal,
      false,
      bgPaint,
    );

    if (score > 0) {
      // Gradient foreground arc
      final rect = Rect.fromCircle(center: center, radius: radius);
      final gradient = SweepGradient(
        center: Alignment.center,
        startAngle: _startAngle,
        endAngle: _startAngle + _sweepTotal,
        colors: [
          const Color(0xFF2E7D32),
          const Color(0xFFF9A825),
          const Color(0xFFE65100),
          const Color(0xFFC62828),
        ],
        stops: const [0.0, 0.35, 0.65, 1.0],
      );

      final fgPaint = Paint()
        ..shader = gradient.createShader(rect)
        ..strokeWidth = _strokeWidth
        ..strokeCap = StrokeCap.round
        ..style = PaintingStyle.stroke;

      canvas.drawArc(
        rect,
        _startAngle,
        _sweepTotal * score,
        false,
        fgPaint,
      );

      // Needle / indicator dot at the tip
      final tipAngle = _startAngle + _sweepTotal * score;
      final tipX = center.dx + radius * math.cos(tipAngle);
      final tipY = center.dy + radius * math.sin(tipAngle);
      final dotPaint = Paint()..color = color;
      canvas.drawCircle(Offset(tipX, tipY), _strokeWidth / 2 + 2, dotPaint);
      canvas.drawCircle(
        Offset(tipX, tipY),
        _strokeWidth / 2,
        Paint()..color = Colors.white,
      );
    }

    // Tick marks
    final tickPaint = Paint()
      ..color = bgColor.withValues(alpha: 0.6)
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    for (int i = 0; i <= _tickCount; i++) {
      final angle = _startAngle + _sweepTotal * (i / _tickCount);
      final outer = radius + _strokeWidth / 2 + 6;
      final inner = radius - _strokeWidth / 2 - 4;
      canvas.drawLine(
        Offset(center.dx + inner * math.cos(angle),
            center.dy + inner * math.sin(angle)),
        Offset(center.dx + outer * math.cos(angle),
            center.dy + outer * math.sin(angle)),
        tickPaint,
      );
    }

    // Labels: 0 and 100
    _drawLabel(canvas, center, radius + _strokeWidth + 16, _startAngle, '0', size);
    _drawLabel(
      canvas,
      center,
      radius + _strokeWidth + 16,
      _startAngle + _sweepTotal,
      '100',
      size,
    );
  }

  void _drawLabel(
    Canvas canvas,
    Offset center,
    double r,
    double angle,
    String text,
    Size size,
  ) {
    final tp = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: bgColor.withValues(alpha: 1.0),
          fontSize: 10,
          fontWeight: FontWeight.w600,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(
      canvas,
      Offset(
        center.dx + r * math.cos(angle) - tp.width / 2,
        center.dy + r * math.sin(angle) - tp.height / 2,
      ),
    );
  }

  @override
  bool shouldRepaint(_GaugePainter old) =>
      old.score != score || old.color != color;
}
