import 'package:flutter/material.dart';

/// Dashboard screen – the main hub showing threat summary, quick stats,
/// and navigation shortcuts to Inbox, Spam, and History.
///
/// Will later be powered by a [DashboardProvider] that aggregates
/// scan counts, recent detections, and threat level.
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Dashboard')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.dashboard, size: 64),
            SizedBox(height: 16),
            Text(
              'Dashboard Screen',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 8),
            Text('— Placeholder —', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
