// Basic smoke test: verifies that MindShieldApp mounts without throwing.
//
// Full widget and integration tests will be added per-feature module.

import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mindshield/main.dart';

void main() {
  testWidgets('MindShieldApp smoke test', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    
    // Build our app and trigger a frame.
    await tester.pumpWidget(MindShieldApp(prefs: prefs));

    // The splash screen should render without errors.
    expect(find.text('MindShield'), findsOneWidget);
    await tester.pump(const Duration(seconds: 3));
    await tester.pumpAndSettle();
  });
}
