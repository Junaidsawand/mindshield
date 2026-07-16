import 'package:flutter/material.dart';

/// Spam screen – lists all SMS messages that the AI has flagged as spam
/// or phishing, allowing the user to review and take action.
///
/// Will later be driven by a [SpamProvider] that filters the local
/// SQFLite database by spam classification labels.
class SpamScreen extends StatelessWidget {
  const SpamScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Spam')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.block, size: 64),
            SizedBox(height: 16),
            Text(
              'Spam Screen',
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
