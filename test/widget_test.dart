// Basic smoke test: verifies that MindShieldApp mounts without throwing.
//
// Full widget and integration tests will be added per-feature module.

import 'package:flutter_test/flutter_test.dart';
import 'package:mindshield/main.dart';

void main() {
  testWidgets('MindShieldApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MindShieldApp());
    // The splash screen should render without errors.
    expect(find.text('MindShield'), findsOneWidget);
  });
}
