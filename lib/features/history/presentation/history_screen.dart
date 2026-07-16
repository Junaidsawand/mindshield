import 'package:flutter/material.dart';

/// History screen – a chronological log of all past AI scan results,
/// filterable by date range, threat type, and confidence level.
///
/// Will later be driven by a [HistoryProvider] querying SQFLite
/// with pagination support.
class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('History')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.history, size: 64),
            SizedBox(height: 16),
            Text(
              'History Screen',
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
