import '../domain/analysis_result.dart';
import '../../inbox/domain/sms_message.dart';

// ─────────────────────────────────────────────────────────────────────────────
// DummyAnalysisRepository
// ─────────────────────────────────────────────────────────────────────────────

/// Provides rich dummy [AnalysisResult] objects for UI development.
///
/// When the real AI backend is wired up, replace this with an
/// [ApiAnalysisRepository] that calls the Dio client. The [AnalysisProvider]
/// only depends on [getAnalysis], so the swap is a one-line change.
class DummyAnalysisRepository {
  DummyAnalysisRepository._();

  static final DummyAnalysisRepository instance = DummyAnalysisRepository._();

  /// Returns an [AnalysisResult] for the given [message], simulating a short
  /// AI inference delay. Returns a fallback safe result if no entry exists.
  Future<AnalysisResult> getAnalysis(SmsMessage message) async {
    // Simulate AI inference latency.
    await Future.delayed(const Duration(milliseconds: 1200));
    return _results[message.id] ?? _buildFallback(message);
  }

  // ── Private helpers ────────────────────────────────────────────────────────

  AnalysisResult _buildFallback(SmsMessage msg) => AnalysisResult(
        messageId: msg.id,
        threatScore: 5,
        confidencePercent: 91,
        attackType: AttackType.benign,
        psychologicalTactics: [],
        suspiciousKeywords: [],
        aiExplanation:
            'MindShield\'s NLP pipeline analysed this message and found no statistically '
            'significant patterns associated with phishing, social engineering, or malicious '
            'URLs. The message exhibits natural conversational language and known-safe sender '
            'characteristics.',
        senderInfo: SenderInfo(
          displayName: msg.sender,
          phoneNumber: msg.sender,
          countryCode: 'ZA',
          countryName: 'South Africa',
          firstSeenDate: DateTime(2024, 1, 10),
          reportCount: 0,
          isKnownScammer: false,
          carrierName: 'Vodacom',
          lineType: 'Mobile',
        ),
        recommendations: [
          'No action required – this message appears legitimate.',
          'Always verify unexpected requests through official channels.',
          'MindShield continues monitoring your inbox in the background.',
        ],
        analysisTimestamp: DateTime.now().toUtc(),
        modelVersion: 'MindShield-NLP v2.3.1',
        processingTimeMs: 318,
      );

  // ── Dummy data keyed by message ID ────────────────────────────────────────

  static final Map<String, AnalysisResult> _results = {
    // ── msg_001: Mum – Safe ─────────────────────────────────────────────────
    'msg_001': AnalysisResult(
      messageId: 'msg_001',
      threatScore: 2,
      confidencePercent: 97,
      attackType: AttackType.benign,
      psychologicalTactics: [],
      suspiciousKeywords: [],
      aiExplanation:
          'The message was authored in natural, informal English consistent with personal '
          'family communication. Sentiment analysis reveals positive emotional tone with no '
          'imperative commands, suspicious URLs, or requests for sensitive information. '
          'Sender is identified as a known contact in the device address book. '
          'Bi-LSTM and TF-IDF feature vectors both score below threat threshold (0.03 / 1.0).',
      senderInfo: SenderInfo(
        displayName: 'Mum 👩',
        phoneNumber: '+27 83 200 1234',
        countryCode: 'ZA',
        countryName: 'South Africa',
        firstSeenDate: DateTime(2020, 6, 14),
        reportCount: 0,
        isKnownScammer: false,
        carrierName: 'MTN South Africa',
        lineType: 'Mobile',
      ),
      recommendations: [
        'No action required – this message appears completely safe.',
        'Enjoy your dinner! 🍝',
        'MindShield continues protecting your inbox in the background.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 287,
    ),

    // ── msg_002: Bank suspension – Scam ────────────────────────────────────
    'msg_002': AnalysisResult(
      messageId: 'msg_002',
      threatScore: 99,
      confidencePercent: 99,
      attackType: AttackType.phishing,
      psychologicalTactics: [
        PsychologicalTactic.urgency,
        PsychologicalTactic.fearInduction,
        PsychologicalTactic.authority,
      ],
      suspiciousKeywords: [
        SuspiciousKeyword(
          word: 'URGENT',
          weight: 0.94,
          reason: 'High-urgency trigger word – top LIME feature contributor.',
        ),
        SuspiciousKeyword(
          word: 'suspended',
          weight: 0.88,
          reason: 'Account-status manipulation to induce panic.',
        ),
        SuspiciousKeyword(
          word: 'http://secure-bank-verify.xyz',
          weight: 0.99,
          reason: 'Malicious URL: .xyz TLD, non-bank domain, known phishing host.',
        ),
        SuspiciousKeyword(
          word: 'immediately',
          weight: 0.79,
          reason: 'Urgency amplifier reducing victim deliberation time.',
        ),
        SuspiciousKeyword(
          word: 'restore access',
          weight: 0.83,
          reason: 'Social engineering phrase common in credential harvesting.',
        ),
      ],
      aiExplanation:
          'This message exhibits a classic multi-vector SMiShing pattern. The NLP model '
          'detected three concurrent psychological manipulation tactics: urgency induction '
          'via "URGENT" and "immediately", fear amplification through false account suspension '
          'claims, and authority spoofing by impersonating a banking institution. '
          'The embedded URL (secure-bank-verify.xyz) resolves to a known phishing host '
          'in the MindShield threat intelligence database, registered only 3 days ago '
          'with anonymous WHOIS data. LIME explainability weights confirm the URL and '
          'urgency triggers as the top contributing features (combined weight: 0.92). '
          'Bi-LSTM threat score: 0.99 / 1.0.',
      senderInfo: SenderInfo(
        displayName: 'Unknown Sender',
        phoneNumber: '+1 (888) 220-5530',
        countryCode: 'US',
        countryName: 'United States',
        firstSeenDate: DateTime(2026, 7, 10),
        reportCount: 847,
        isKnownScammer: true,
        carrierName: 'VoIP Provider',
        lineType: 'VoIP',
      ),
      recommendations: [
        'Do NOT click any links in this message under any circumstances.',
        'Your real bank will NEVER ask you to restore access via an SMS link.',
        'Call your bank directly using the number on the back of your card.',
        'Block this number immediately to prevent further contact.',
        'Report the message to the South African Banking Risk Information Centre (SABRIC).',
        'Check your accounts for unauthorised transactions at the official bank website.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 512,
    ),

    // ── msg_003: FNB Alerts – Safe ──────────────────────────────────────────
    'msg_003': AnalysisResult(
      messageId: 'msg_003',
      threatScore: 4,
      confidencePercent: 95,
      attackType: AttackType.benign,
      psychologicalTactics: [],
      suspiciousKeywords: [],
      aiExplanation:
          'The sender "FNB Alerts" matches a verified banking short-code in the '
          'MindShield allowlist. Transaction notification format conforms to the '
          'standard FNB debit alert template. The message includes correct account '
          'masking (last 4 digits only), a legitimate helpline number (0800 111 005), '
          'and no embedded links. TF-IDF feature vector shows no threat indicators; '
          'Bi-LSTM score: 0.04 / 1.0.',
      senderInfo: SenderInfo(
        displayName: 'FNB Alerts',
        phoneNumber: 'FNB Alerts',
        countryCode: 'ZA',
        countryName: 'South Africa',
        firstSeenDate: DateTime(2019, 3, 1),
        reportCount: 0,
        isKnownScammer: false,
        carrierName: 'First National Bank',
        lineType: 'Short Code',
      ),
      recommendations: [
        'This is a legitimate FNB transaction notification.',
        'If you do not recognise the debit, call 0800 111 005 immediately.',
        'Verify transactions regularly through the FNB app or internet banking.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 298,
    ),

    // ── msg_004: Shoprite prize scam ────────────────────────────────────────
    'msg_004': AnalysisResult(
      messageId: 'msg_004',
      threatScore: 98,
      confidencePercent: 98,
      attackType: AttackType.prizeScam,
      psychologicalTactics: [
        PsychologicalTactic.greed,
        PsychologicalTactic.scarcity,
        PsychologicalTactic.isolation,
      ],
      suspiciousKeywords: [
        SuspiciousKeyword(
          word: 'won a R50,000',
          weight: 0.97,
          reason: 'Unrealistic prize claim – top LIME feature.',
        ),
        SuspiciousKeyword(
          word: 'ID number',
          weight: 0.95,
          reason: 'Direct PII harvesting request for national identity number.',
        ),
        SuspiciousKeyword(
          word: 'banking details',
          weight: 0.99,
          reason: 'Request for financial credentials – highest-weight keyword.',
        ),
        SuspiciousKeyword(
          word: 'claims@shoprite-promo.net',
          weight: 0.91,
          reason: 'Non-official email domain spoofing Shoprite brand.',
        ),
      ],
      aiExplanation:
          'This message is a textbook prize scam (also known as "advance-fee fraud" '
          'or "419 scam"). The model identified three manipulation tactics operating '
          'simultaneously: greed appeal via the inflated prize amount (R50,000), '
          'scarcity pressure implying the victim must act to claim, and overt PII '
          'harvesting requesting the victim\'s national ID number and banking details. '
          'The email domain "shoprite-promo.net" is not affiliated with Shoprite Holdings '
          'Ltd – the real corporate domain is shoprite.co.za. '
          'Named entity recognition (NER) confirms "Shoprite" is used as a brand spoof. '
          'LIME combined weight: 0.96 / 1.0.',
      senderInfo: SenderInfo(
        displayName: 'Unknown Sender',
        phoneNumber: '+27 82 555 0193',
        countryCode: 'ZA',
        countryName: 'South Africa',
        firstSeenDate: DateTime(2026, 6, 28),
        reportCount: 1203,
        isKnownScammer: true,
        carrierName: 'Cell C',
        lineType: 'Mobile',
      ),
      recommendations: [
        'Do NOT share your ID number, banking details, or OTP with anyone via SMS.',
        'Shoprite does NOT run competitions via unsolicited SMS messages.',
        'Block and report this number to the SAPS Cybercrime Unit.',
        'Report the email address to ISPA (Internet Service Providers\' Association of SA).',
        'Warn family members who may receive similar messages from this number.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 498,
    ),

    // ── msg_006: Investment fraud – Suspicious ──────────────────────────────
    'msg_006': AnalysisResult(
      messageId: 'msg_006',
      threatScore: 74,
      confidencePercent: 82,
      attackType: AttackType.investmentFraud,
      psychologicalTactics: [
        PsychologicalTactic.greed,
        PsychologicalTactic.trustBuilding,
        PsychologicalTactic.curiosity,
      ],
      suspiciousKeywords: [
        SuspiciousKeyword(
          word: 'double your investment',
          weight: 0.92,
          reason: 'Unrealistic ROI promise – primary Ponzi scheme indicator.',
        ),
        SuspiciousKeyword(
          word: 'in 30 days',
          weight: 0.85,
          reason: 'Impossibly short investment window to create urgency.',
        ),
        SuspiciousKeyword(
          word: 'financial advisor',
          weight: 0.61,
          reason: 'Unverified authority claim to establish credibility.',
        ),
        SuspiciousKeyword(
          word: 'Reply "YES"',
          weight: 0.77,
          reason: 'Engagement hook – common social engineering entry point.',
        ),
      ],
      aiExplanation:
          'The model assigns a "suspicious" classification with 82% confidence. The message '
          'contains investment fraud indicators but lacks the explicit URL, PII request, or '
          'confirmed threat-intel match needed for a "scam" verdict. '
          'Key signals: unsolicited contact from an unknown international number (+44 UK), '
          'an unverifiable "financial advisor" claim, and an impossible 30-day 100% return '
          'promise – the hallmarks of advance-fee investment fraud. '
          'The model is 18% uncertain because the message does not contain a direct '
          'payment request or harvesting link in this first contact, suggesting a '
          'multi-stage grooming approach.',
      senderInfo: SenderInfo(
        displayName: 'Unknown Sender',
        phoneNumber: '+44 7923 102938',
        countryCode: 'GB',
        countryName: 'United Kingdom',
        firstSeenDate: DateTime(2026, 7, 1),
        reportCount: 34,
        isKnownScammer: false,
        carrierName: 'UK VoIP',
        lineType: 'VoIP',
      ),
      recommendations: [
        'Do NOT reply to this message or engage with the sender.',
        'Legitimate financial advisors do not solicit clients via unsolicited SMS.',
        'Any investment promising 100% returns in 30 days is almost certainly a scam.',
        'Report to the Financial Sector Conduct Authority (FSCA) if you have engaged.',
        'Block this number to prevent follow-up messages.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 437,
    ),

    // ── msg_008: SARS impersonation – Scam ──────────────────────────────────
    'msg_008': AnalysisResult(
      messageId: 'msg_008',
      threatScore: 97,
      confidencePercent: 97,
      attackType: AttackType.governmentImpersonation,
      psychologicalTactics: [
        PsychologicalTactic.authority,
        PsychologicalTactic.scarcity,
        PsychologicalTactic.greed,
        PsychologicalTactic.fearInduction,
      ],
      suspiciousKeywords: [
        SuspiciousKeyword(
          word: 'SARS',
          weight: 0.89,
          reason: 'Government brand impersonation to establish false authority.',
        ),
        SuspiciousKeyword(
          word: 'tax refund',
          weight: 0.91,
          reason: 'Financial lure exploiting greed and SARS legitimacy.',
        ),
        SuspiciousKeyword(
          word: 'http://sars-refund.co',
          weight: 0.98,
          reason: 'Malicious URL mimicking SARS.gov.za; not a government domain.',
        ),
        SuspiciousKeyword(
          word: 'within 24 hours',
          weight: 0.86,
          reason: 'Artificial deadline creating scarcity pressure.',
        ),
        SuspiciousKeyword(
          word: 'Provide your bank details',
          weight: 0.97,
          reason: 'Explicit financial credential harvesting instruction.',
        ),
      ],
      aiExplanation:
          'This is a high-confidence government impersonation scam. The real South African '
          'Revenue Service (SARS) only communicates refunds through the official eFiling portal '
          '(sars.gov.za) and never requests banking details via SMS. '
          'The URL "sars-refund.co" is a lookalike domain designed to impersonate the official '
          '.gov.za domain and was registered anonymously 11 days ago. '
          'The model detected four simultaneous psychological tactics: authority (SARS brand), '
          'greed (R3,892 refund), scarcity (24-hour deadline), and fear (implied penalty for '
          'non-compliance). LIME top features: URL (0.98), credential request (0.97). '
          'Bi-LSTM confidence: 0.97 / 1.0.',
      senderInfo: SenderInfo(
        displayName: 'SARS eFiling (FAKE)',
        phoneNumber: 'SARS eFilng',
        countryCode: 'ZA',
        countryName: 'South Africa',
        firstSeenDate: DateTime(2026, 7, 5),
        reportCount: 2841,
        isKnownScammer: true,
        carrierName: 'Unknown Short Code',
        lineType: 'Short Code (Spoofed)',
      ),
      recommendations: [
        'Do NOT click the link or provide any banking details.',
        'SARS never requests banking details via SMS – this is 100% a scam.',
        'Check your actual SARS refund status at www.sars.gov.za (eFiling portal only).',
        'Report the scam directly to SARS at phishing@sars.gov.za.',
        'File a complaint with the SAPS Cybercrime Unit at cybercrime.saps.gov.za.',
        'Forward the SMS to 082 135 for Vodacom spam reporting (or your carrier\'s equivalent).',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 541,
    ),

    // ── msg_010: Delivery scam – Suspicious ─────────────────────────────────
    'msg_010': AnalysisResult(
      messageId: 'msg_010',
      threatScore: 68,
      confidencePercent: 78,
      attackType: AttackType.deliveryScam,
      psychologicalTactics: [
        PsychologicalTactic.urgency,
        PsychologicalTactic.scarcity,
        PsychologicalTactic.authority,
      ],
      suspiciousKeywords: [
        SuspiciousKeyword(
          word: 'on hold',
          weight: 0.79,
          reason: 'Status-blocking tactic to trigger anxiety and action.',
        ),
        SuspiciousKeyword(
          word: 'unpaid customs duty',
          weight: 0.88,
          reason: 'Fabricated bureaucratic hurdle requiring payment.',
        ),
        SuspiciousKeyword(
          word: 'track-my-parcel.delivery',
          weight: 0.93,
          reason: 'Non-standard TLD (.delivery) suspicious domain.',
        ),
        SuspiciousKeyword(
          word: 'R49.99',
          weight: 0.74,
          reason: 'Specific low amount to seem plausible and reduce victim hesitation.',
        ),
      ],
      aiExplanation:
          'The model classifies this as suspicious (78% confidence) with delivery scam '
          'characteristics. The pattern – parcel held due to unpaid duty, low payment amount, '
          'suspicious URL – matches known South African "parcel fee" phishing campaigns. '
          'Confidence falls short of "scam" (>85%) because the model cannot confirm the URL '
          'is actively malicious in the current threat feed, and the message does not '
          'directly request sensitive credentials in this version. '
          'Exercise extreme caution – this pattern frequently escalates to credential theft '
          'on the payment page.',
      senderInfo: SenderInfo(
        displayName: 'Unknown Sender',
        phoneNumber: '+1 (202) 555-0147',
        countryCode: 'US',
        countryName: 'United States',
        firstSeenDate: DateTime(2026, 7, 12),
        reportCount: 156,
        isKnownScammer: false,
        carrierName: 'US VoIP',
        lineType: 'VoIP',
      ),
      recommendations: [
        'Do NOT click the link or make any payment.',
        'Contact the courier directly using the tracking number from your purchase confirmation.',
        'SAPO (South African Post Office) and DHL never request customs fees via SMS links.',
        'If you are expecting a parcel, track it at the courier\'s official website only.',
        'Report this number to the SAPS Cybercrime Unit if you paid any money.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 389,
    ),

    // ── msg_012: Crypto scam ─────────────────────────────────────────────────
    'msg_012': AnalysisResult(
      messageId: 'msg_012',
      threatScore: 99,
      confidencePercent: 99,
      attackType: AttackType.cryptoScam,
      psychologicalTactics: [
        PsychologicalTactic.urgency,
        PsychologicalTactic.fearInduction,
        PsychologicalTactic.authority,
        PsychologicalTactic.scarcity,
      ],
      suspiciousKeywords: [
        SuspiciousKeyword(
          word: 'compromised',
          weight: 0.93,
          reason: 'Security breach claim to induce panic and bypass critical thinking.',
        ),
        SuspiciousKeyword(
          word: 'NOW',
          weight: 0.88,
          reason: 'Extreme urgency trigger – capitalised for maximum psychological impact.',
        ),
        SuspiciousKeyword(
          word: '0800-CRYPTO',
          weight: 0.82,
          reason: 'Fake helpline number directing victim to fraudsters.',
        ),
        SuspiciousKeyword(
          word: 'http://crypto-secure-wallet.ru',
          weight: 0.99,
          reason: '.ru TLD, non-crypto domain, confirmed malicious in threat feed.',
        ),
        SuspiciousKeyword(
          word: 'immediately',
          weight: 0.76,
          reason: 'Secondary urgency amplifier.',
        ),
      ],
      aiExplanation:
          'Maximum-confidence crypto scam detected. The message employs four psychological '
          'tactics simultaneously: urgency ("NOW", "immediately"), fear ("compromised"), '
          'false authority ("security team"), and scarcity (implied time pressure). '
          'The URL crypto-secure-wallet.ru uses a Russian TLD and is flagged in the '
          'MindShield threat intelligence feed as an active credential-harvesting page '
          'targeting cryptocurrency wallet seed phrases and private keys. '
          'The phone number 0800-CRYPTO does not correspond to any legitimate '
          'cryptocurrency exchange operating in South Africa. '
          'Bi-LSTM threat score: 0.99 / 1.0. This message should be treated as a '
          'confirmed, active threat.',
      senderInfo: SenderInfo(
        displayName: 'Unknown Sender',
        phoneNumber: '+27 60 123 4567',
        countryCode: 'ZA',
        countryName: 'South Africa',
        firstSeenDate: DateTime(2026, 7, 9),
        reportCount: 3102,
        isKnownScammer: true,
        carrierName: 'Telkom Mobile',
        lineType: 'Mobile',
      ),
      recommendations: [
        'Do NOT click the link or call the number provided in this message.',
        'No legitimate crypto exchange contacts users about wallet security via SMS.',
        'If you have a crypto wallet concern, go directly to the exchange app or website.',
        'If you already clicked the link, immediately revoke any connected wallet sessions.',
        'Report to the Financial Sector Conduct Authority (FSCA) and SAPS Cybercrime.',
        'Consider running a malware scan if you visited the URL on your device.',
      ],
      analysisTimestamp: DateTime.now().toUtc(),
      modelVersion: 'MindShield-NLP v2.3.1',
      processingTimeMs: 523,
    ),
  };
}
