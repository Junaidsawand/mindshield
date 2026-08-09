# ==============================================================================
# MindShield Backend — ML Regression Test Suite v2
# Phase 3.6: 14 Critical Benchmark Messages for Pakistani Generalization
# ==============================================================================
"""Automated regression tests using the real model.

No hardcoded inference rules. No threshold manipulation.
Tests call HuggingFaceModelLoader.predict() directly.
"""

import pytest
from app.core.model_loader import HuggingFaceModelLoader


@pytest.fixture(scope="module")
def pakscam_v2_loader():
    """Fixture providing distilbert-pakscam-v2 model loader."""
    from pathlib import Path
    path = Path("data/models/distilbert_pakscam_v2")
    if not path.exists():
        pytest.skip("distilbert-pakscam-v2 not trained yet")
    loader = HuggingFaceModelLoader(model_path=str(path))
    loader.load()
    return loader


# ------------------------------------------------------------------
# HAM Regression Tests — Must classify as safe
# ------------------------------------------------------------------


class TestPakistaniHAMRegression:
    """Legitimate Pakistani SMS must be classified as safe."""

    def test_ubl_ibft_receipt(self, pakscam_v2_loader):
        """User-observed #1: UBL IBFT credit receipt."""
        text = (
            "PKR 5,030 received from ILAM UL DIN* in your "
            "UBL A/C *5034 on 04-AUG-2026 19:53 via IBFT. "
            "Tx ID 6940522193. For info: 111825888."
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"UBL IBFT receipt misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_ubl_atm_debit(self, pakscam_v2_loader):
        """User-observed #2: UBL ATM debit notification."""
        text = (
            "JUNAID AHMED A/C *5034 is debited with PKR "
            "5,000 on 04/08/26 at 20:13 from ATM. "
            "For info: 111825888."
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"UBL ATM debit misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_ubl_customer_service_bitly(
        self, pakscam_v2_loader
    ):
        """User-observed #3: UBL complaint portal with bit.ly."""
        text = (
            "Dear UBL Customer,\nYou may log your complaints "
            "via our Contact Center, Email, Website, Mobile "
            "App, Social Media, Branches or visit: "
            "https://bit.ly/2WceaFA"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"UBL customer service misclassified as "
            f"{pred.label} (conf={pred.confidence:.4f})"
        )

    def test_zong_50_percent_off(self, pakscam_v2_loader):
        """User-observed #7: Zong 50% OFF flash sale."""
        text = (
            "50% OFF Only 4 You! Make the most of Z Hour "
            "sale from 5PM-9PM & get 50% OFF on WhatsApp "
            "Plus Bundle in My Zong App. Tap now: "
            "bit.ly/3rY7XHq"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"Zong promo misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_gaming_royale_subscription(
        self, pakscam_v2_loader
    ):
        """User-observed #8: Gaming Royale VAS subscription."""
        text = (
            "Thanks for subscribing to Gaming Royale at Rs "
            "11.95/Day (Auto Renewal). Play live Games on "
            "http://z.gamingroyale.club. To Unsub click "
            "http://z.gamingroyale.club/u"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"Gaming Royale sub misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_gaming_royale_free_trial(
        self, pakscam_v2_loader
    ):
        """User-observed #10: Gaming Royale FREE trial."""
        text = (
            "You have unlocked ONE Day FREE Trial of Gaming "
            "Royale and will be charged Rs 11.95/Day (Auto "
            "renewal) tomorrow. To Unsub click "
            "http://z.gamingroyale.club/u"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"Gaming Royale trial misclassified as "
            f"{pred.label} (conf={pred.confidence:.4f})"
        )

    def test_readycash_overdue(self, pakscam_v2_loader):
        """User-observed #11: ReadyCash overdue repayment."""
        text = (
            "Your ReadCash is Overdue! Save on the next "
            "weekly fee of Rs 160 (applied in 2 days) by "
            "repaying your ReadyCash Rs 3151.18 now by "
            "dialing *786*4*2#."
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"ReadyCash overdue misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_readycash_1_day_left(self, pakscam_v2_loader):
        """User-observed #12: ReadyCash 1 DAY LEFT urgency."""
        text = (
            "1 DAY LEFT! Your ReadyCash loan is due "
            "tomorrow! Make sure to Dial *786*4*2# to repay "
            "your Rs 3151.18 on time and to be able to "
            "borrow again!"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"ReadyCash 1 DAY LEFT misclassified as "
            f"{pred.label} (conf={pred.confidence:.4f})"
        )

    def test_zong_engage_prize_language(
        self, pakscam_v2_loader
    ):
        """User-observed #15: Zong Engage with prize language."""
        text = (
            "Jeetne ke liye tayyar ho jao! aur jeeto bade "
            "inaam, Zong Engage ke taraf se khaas "
            "http://games.zongengage.com.pk 6PKR/Day, Reply "
            "1 ke saath on 4263\u200bor\u200bdial\u200b*4263#"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "safe", (
            f"Zong Engage misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )


# ------------------------------------------------------------------
# SPAM Regression Tests — Must classify as phishing
# ------------------------------------------------------------------


class TestPakistaniSPAMRegression:
    """Pakistani phishing/scam SMS must be classified as phishing."""

    def test_obvious_prize_phishing(self, pakscam_v2_loader):
        """Obvious prize phishing with URL."""
        text = (
            "Congratulations! You have won PKR 100,000. "
            "Click http://example.com to claim your prize "
            "immediately."
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "phishing", (
            f"Prize phishing misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_fake_bank_verification(self, pakscam_v2_loader):
        """Fake bank biometric verification."""
        text = (
            "HBL Alert: Your account will be blocked in "
            "24 hours due to pending verification. Update "
            "now: http://hbl-secure-login.xyz"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "phishing", (
            f"Fake bank verification misclassified as "
            f"{pred.label} (conf={pred.confidence:.4f})"
        )

    def test_fake_account_suspension(self, pakscam_v2_loader):
        """Fake account suspension with malicious URL."""
        text = (
            "Your UBL account has been suspended. Verify "
            "your account immediately by clicking "
            "http://example.com/login"
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "phishing", (
            f"Fake suspension misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_malicious_url_phishing(self, pakscam_v2_loader):
        """Credential phishing with malicious URL."""
        text = (
            "Dear Customer, share your 6-digit OTP code "
            "with our support team to stop unauthorized "
            "transaction of PKR 45,000."
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "phishing", (
            f"OTP phishing misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )

    def test_roman_urdu_prize_scam(self, pakscam_v2_loader):
        """Roman Urdu BISP prize scam."""
        text = (
            "BISP ki taraf se 25,000 rupay approved hain. "
            "Abhi claim karein 0312-9876543 par call "
            "kar ke."
        )
        pred = pakscam_v2_loader.predict(text)
        assert pred.label == "phishing", (
            f"BISP scam misclassified as {pred.label} "
            f"(conf={pred.confidence:.4f})"
        )
