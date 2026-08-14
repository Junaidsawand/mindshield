"""
Phase 3.8 — ML Regression Tests for distilbert-pakscam-v3
Runs against data/models/distilbert_pakscam_v3 (isolated).
All 14 original regression cases + 3 new v3-specific cases.
"""
import pytest
from pathlib import Path
from app.core.model_loader import HuggingFaceModelLoader

V3_MODEL_PATH = str(
    Path(__file__).resolve().parents[1] / "data/models/distilbert_pakscam_v3"
)


@pytest.fixture(scope="module")
def v3_loader():
    loader = HuggingFaceModelLoader(
        model_path=V3_MODEL_PATH,
        model_version="distilbert-pakscam-v3",
    )
    loader.load()
    return loader


# ── Original 14 regression cases (same as test_ml_regression.py) ─────────────
# 9 Pakistani HAM (must be classified as "safe")
@pytest.mark.parametrize("text,expected_label,test_id", [
    ("PKR 5,030 received from ILAM UL DIN* in your UBL A/C *5034 on 04-AUG-2026 19:53 via IBFT. Tx ID 6940522193. For info: 111825888.",
     "safe", "ubl_ibft_receipt"),
    ("JUNAID AHMED A/C *5034 is debited with PKR 5,000 on 04/08/26 at 20:13 from ATM. For info: 111825888.",
     "safe", "ubl_atm_debit"),
    ("Dear UBL Customer,\nYou may log your complaints via our Contact Center, Email, Website, Mobile App, Social Media, Branches or visit: https://bit.ly/2WceaFA",
     "safe", "ubl_customer_service_bitly"),
    ("50% OFF Only 4 You! Make the most of Z Hour sale from 5PM-9PM & get 50% OFF on WhatsApp Plus Bundle in My Zong App. Tap now: bit.ly/3rY7XHq",
     "safe", "zong_50_percent_off"),
    ("Thanks for subscribing to Gaming Royale at Rs 11.95/Day (Auto Renewal). Play live Games on http://z.gamingroyale.club. To Unsub click http://z.gamingroyale.club/u",
     "safe", "gaming_royale_subscription"),
    ("You have unlocked ONE Day FREE Trial of Gaming Royale and will be charged Rs 11.95/Day (Auto renewal) tomorrow. To Unsub click http://z.gamingroyale.club/u",
     "safe", "gaming_royale_free_trial"),
    ("Your ReadCash is Overdue! Save on the next weekly fee of Rs 160 (applied in 2 days) by repaying your ReadyCash Rs 3151.18 now by dialing *786*4*2#.",
     "safe", "readycash_overdue"),
    ("1 DAY LEFT! Your ReadyCash loan is due tomorrow! Make sure to Dial *786*4*2# to repay your Rs 3151.18 on time and to be able to borrow again!",
     "safe", "readycash_1_day_left"),
    ("Jeetne ke liye tayyar ho jao! aur jeeto bade inaam, Zong Engage ke taraf se khaas http://games.zongengage.com.pk 6PKR/Day, Reply 1 ke saath on 4263",
     "safe", "zong_engage_prize_lang"),
])
def test_v3_ham_regression(v3_loader, text, expected_label, test_id):
    pred = v3_loader.predict(text)
    assert pred.label == expected_label, (
        f"[{test_id}] Expected '{expected_label}' but got '{pred.label}' "
        f"(confidence={pred.confidence:.4f})"
    )


# 5 SPAM regression cases (must be classified as "phishing")
@pytest.mark.parametrize("text,expected_label,test_id", [
    ("Congratulations! You have won PKR 100,000. Click http://example.com to claim your prize immediately.",
     "phishing", "prize_phishing"),
    ("HBL Alert: Your account will be blocked in 24 hours due to pending verification. Update now: http://hbl-secure-login.xyz",
     "phishing", "fake_bank_verification"),
    ("Your UBL account has been suspended. Verify your account immediately by clicking http://example.com/login",
     "phishing", "fake_account_suspension"),
    ("Dear Customer, share your 6-digit OTP code with our support team to stop unauthorized transaction of PKR 45,000.",
     "phishing", "otp_phishing"),
    ("BISP ki taraf se 25,000 rupay approved hain. Abhi claim karein 0312-9876543 par call kar ke.",
     "phishing", "bisp_roman_urdu_scam"),
])
def test_v3_spam_regression(v3_loader, text, expected_label, test_id):
    pred = v3_loader.predict(text)
    assert pred.label == expected_label, (
        f"[{test_id}] Expected '{expected_label}' but got '{pred.label}' "
        f"(confidence={pred.confidence:.4f})"
    )


# ── 3 new v3-specific cases targeting the exact v2 failure families ───────────
@pytest.mark.parametrize("text,expected_label,test_id", [
    # The exact message from zong_flash_sale that v2 failed on
    ("50% OFF Only 4 You! Make the most of Z Hour sale from 5PM-9PM & get 50% OFF on WhatsApp Plus Bundle in My Zong App. Tap now: bit.ly/3rY7XHq",
     "safe", "v3_zong_flash_sale_regression"),
    # Variant of UBL customer service with bit.ly
    ("Dear UBL Customer, For complaints visit our portal: https://bit.ly/ubl-complaint-portal or call 111-825-888",
     "safe", "v3_ubl_bitly_variant"),
    # New Roman Urdu banking transaction (was proxy FP)
    ("HBL: Aap ke account *7892 mein PKR 25,000 IBFT se credit ho gaye hain. Maujuda balance: PKR 92,300.",
     "safe", "v3_hbl_ibft_roman_urdu"),
])
def test_v3_new_regression(v3_loader, text, expected_label, test_id):
    pred = v3_loader.predict(text)
    assert pred.label == expected_label, (
        f"[v3-specific][{test_id}] Expected '{expected_label}' but got "
        f"'{pred.label}' (confidence={pred.confidence:.4f})"
    )


# ── Promotion gate sanity check (informational, not blocking) ─────────────────
def test_v3_model_loads_successfully(v3_loader):
    pred = v3_loader.predict("Hello, this is a test message.")
    assert pred.label in ("safe", "phishing"), "Model did not return valid label"
    assert 0.0 <= pred.confidence <= 1.0, "Confidence out of range"
    assert pred.predicted_at is not None, "Execution timestamp should be set"
