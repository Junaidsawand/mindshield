# ==============================================================================
# MindShield Backend — Pakistani SMS Localized Dataset Generator v2
# Phase 3.6: Domain Generalization with Provenance Tracking
# ==============================================================================
"""Generate pakscam_localized_v2.csv with full provenance schema.

Dataset includes:
- 15 user-observed legitimate Pakistani SMS (is_synthetic=False)
- Re-imported PakScam v1 samples with updated schema (is_synthetic=True)
- New synthetic samples for coverage gaps (is_synthetic=True)

Every row contains: id, text, label, category, language,
source_type, is_synthetic, origin, notes
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List

import pandas as pd


class PakScamV2DatasetGenerator:
    """Generate localized Pakistani SMS dataset with provenance."""

    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._id_counter = 0
        self._seen_hashes = set()
        self._template_families: Dict[str, List[int]] = {}

    def _next_id(self) -> str:
        self._id_counter += 1
        return f"pak_v2_{self._id_counter:04d}"

    def _text_hash(self, text: str) -> str:
        normalized = " ".join(text.lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def _add_record(
        self,
        records: list,
        text: str,
        label: str,
        category: str,
        language: str,
        source_type: str,
        is_synthetic: bool,
        origin: str,
        notes: str = "",
        template_family: str = "",
    ) -> bool:
        """Add record with deduplication check. Returns True if added."""
        h = self._text_hash(text)
        if h in self._seen_hashes:
            return False
        self._seen_hashes.add(h)

        rid = self._next_id()
        records.append({
            "id": rid,
            "text": text,
            "label": label,
            "category": category,
            "language": language,
            "source_type": source_type,
            "is_synthetic": is_synthetic,
            "origin": origin,
            "notes": notes,
            "template_family": template_family,
        })

        if template_family:
            self._template_families.setdefault(
                template_family, []
            ).append(self._id_counter)
        return True

    def _add_user_observed(self, records: list) -> int:
        """Add 15 user-observed SMS. Returns count added."""
        count = 0
        observed = [
            {
                "text": (
                    "PKR 5,030 received from ILAM UL DIN* in your UBL "
                    "A/C *5034 on 04-AUG-2026 19:53 via IBFT. Tx ID "
                    "6940522193. For info: 111825888."
                ),
                "label": "ham",
                "category": "banking_transaction",
                "language": "en",
                "notes": "UBL IBFT credit. Hard-negative: PKR, "
                         "masked A/C, Tx ID, all-caps, numbers.",
                "family": "ubl_ibft_credit",
            },
            {
                "text": (
                    "JUNAID AHMED A/C *5034 is debited with PKR 5,000"
                    " on 04/08/26 at 20:13 from ATM. For info: "
                    "111825888."
                ),
                "label": "ham",
                "category": "banking_transaction",
                "language": "en",
                "notes": "UBL ATM debit alert. Hard-negative: PKR, "
                         "masked A/C, ATM, debit language.",
                "family": "ubl_atm_debit",
            },
            {
                "text": (
                    "Dear UBL Customer,\nYou may log your complaints "
                    "via our Contact Center, Email, Website, Mobile "
                    "App, Social Media, Branches or visit: "
                    "https://bit.ly/2WceaFA"
                ),
                "label": "ham",
                "category": "banking_customer_service",
                "language": "en",
                "notes": "UBL complaint portal. Hard-negative: "
                         "shortened bit.ly URL.",
                "family": "ubl_customer_service",
            },
            {
                "text": (
                    "Daily Supreme sy 2GB Data, 1000 ZONG mins, 100 "
                    "SMS rozana sirf Rs.81 ky recharge me. Activation "
                    "kliye 310 mila kr Call Center Services sey menu "
                    "3 muntakhib kren"
                ),
                "label": "ham",
                "category": "telecom_promotion",
                "language": "roman_urdu",
                "notes": "Zong daily bundle. Roman Urdu promotion.",
                "family": "zong_bundle_promo",
            },
            {
                "text": (
                    "Monthly Pro Max Basic 200GB Data aur bohat kuch "
                    "30 din kly sirf Rs2600 k recharge me. Activation "
                    "klye 310 mila kr Call Center Services sy menu 8 "
                    "muntakhib krn"
                ),
                "label": "ham",
                "category": "telecom_promotion",
                "language": "roman_urdu",
                "notes": "Zong monthly package. Same template "
                         "family as msg #4 and #6.",
                "family": "zong_bundle_promo",
            },
            {
                "text": (
                    "Monthly Digital Max Basic 100GB Data aur bohat "
                    "kuch 30 din kly Sirf Rs2500 recharge me. "
                    "Activation klye 310 mila kr Call Center "
                    "Services..."
                ),
                "label": "ham",
                "category": "telecom_promotion",
                "language": "roman_urdu",
                "notes": "Zong monthly package. Same template "
                         "family as msg #4 and #5.",
                "family": "zong_bundle_promo",
            },
            {
                "text": (
                    "50% OFF Only 4 You! Make the most of Z Hour sale "
                    "from 5PM-9PM & get 50% OFF on WhatsApp Plus "
                    "Bundle in My Zong App. Tap now: bit.ly/3rY7XHq"
                ),
                "label": "ham",
                "category": "telecom_promotion",
                "language": "en",
                "notes": "EXTREME hard-negative: 50% OFF, urgency, "
                         "exclamations, shortened URL, Only 4 You!",
                "family": "zong_flash_sale",
            },
            {
                "text": (
                    "Thanks for subscribing to Gaming Royale at Rs "
                    "11.95/Day (Auto Renewal). Play live Games on "
                    "http://z.gamingroyale.club. To Unsub click "
                    "http://z.gamingroyale.club/u"
                ),
                "label": "ham",
                "category": "telecom_subscription",
                "language": "en",
                "notes": "VAS subscription confirmation. "
                         "Hard-negative: URLs, auto-renewal, pricing.",
                "family": "gaming_royale_vas",
            },
            {
                "text": (
                    "Dear Customer, You have successfully "
                    "unsubscribed from Gaming Royale service. To "
                    "subscribe again visit "
                    "http://z.gamingroyale.club. Thank you"
                ),
                "label": "ham",
                "category": "telecom_unsubscription",
                "language": "en",
                "notes": "VAS unsubscription confirmation.",
                "family": "gaming_royale_vas",
            },
            {
                "text": (
                    "You have unlocked ONE Day FREE Trial of Gaming "
                    "Royale and will be charged Rs 11.95/Day (Auto "
                    "renewal) tomorrow. To Unsub click "
                    "http://z.gamingroyale.club/u"
                ),
                "label": "ham",
                "category": "telecom_subscription",
                "language": "en",
                "notes": "EXTREME hard-negative: FREE, auto-renewal, "
                         "URL, pricing, .club TLD.",
                "family": "gaming_royale_vas",
            },
            {
                "text": (
                    "Your ReadCash is Overdue! Save on the next "
                    "weekly fee of Rs 160 (applied in 2 days) by "
                    "repaying your ReadyCash Rs 3151.18 now by "
                    "dialing *786*4*2#."
                ),
                "label": "ham",
                "category": "loan_notification",
                "language": "en",
                "notes": "EXTREME hard-negative: Overdue!, urgency, "
                         "financial amounts, USSD code.",
                "family": "readycash_repayment",
            },
            {
                "text": (
                    "1 DAY LEFT! Your ReadyCash loan is due "
                    "tomorrow! Make sure to Dial *786*4*2# to repay "
                    "your Rs 3151.18 on time and to be able to "
                    "borrow again!"
                ),
                "label": "ham",
                "category": "loan_notification",
                "language": "en",
                "notes": "EXTREME hard-negative: 1 DAY LEFT!, double "
                         "exclamation, urgency, financial amounts.",
                "family": "readycash_repayment",
            },
            {
                "text": (
                    "Apki ReadyCash loan ki limit ab Rs. 55000 hai. "
                    "Mazeed maloomat ya loan hasil karne ke liye "
                    "*786*4# ya JazzCash app ka istemaal karein"
                ),
                "label": "ham",
                "category": "loan_notification",
                "language": "roman_urdu",
                "notes": "Roman Urdu loan limit notification. "
                         "Hard-negative: Rs, loan, USSD code.",
                "family": "readycash_limit",
            },
            {
                "text": (
                    "Aap ne ReadyCash ki total ada hone wali raqam "
                    "Rs 3311.18 ka Rs 60 ada kar diya hai. Baqia "
                    "raqam ki miyaad 2026-08-10 23:59:59 hai. "
                    "7864*2# dial kr k baki raqam jald se jald ada "
                    "karen. TID: 718371921242"
                ),
                "label": "ham",
                "category": "payment_notification",
                "language": "roman_urdu",
                "notes": "Roman Urdu partial repayment confirmation. "
                         "Hard-negative: deadline, TID, Rs amounts.",
                "family": "readycash_repayment",
            },
            {
                "text": (
                    "Jeetne ke liye tayyar ho jao! aur jeeto bade "
                    "inaam, Zong Engage ke taraf se khaas "
                    "http://games.zongengage.com.pk 6PKR/Day, Reply "
                    "1 ke saath on 4263\u200bor\u200bdial\u200b*4263#"
                ),
                "label": "ham",
                "category": "telecom_promotion",
                "language": "roman_urdu",
                "notes": "EXTREME hard-negative: prize language "
                         "(jeetne, inaam), URL, subscription. "
                         "Official Zong Engage domain.",
                "family": "zong_engage_gaming",
            },
        ]

        for msg in observed:
            added = self._add_record(
                records,
                text=msg["text"],
                label=msg["label"],
                category=msg["category"],
                language=msg["language"],
                source_type="user_observed",
                is_synthetic=False,
                origin="user_provided_observation",
                notes=msg["notes"],
                template_family=msg["family"],
            )
            if added:
                count += 1
        return count

    def _add_pakscam_v1_reimport(self, records: list) -> int:
        """Re-import PakScam v1 samples with v2 schema. Returns count."""
        count = 0

        # Map v1 subset_categories to v2 categories
        category_map = {
            "banking_ham": "banking_transaction",
            "hard_negative_ham": "banking_notification",
            "phishing_spam": "bank_phishing",
            "prize_spam": "fake_prize",
            "roman_urdu_ham": "telecom_service_notification",
            "roman_urdu_spam": "roman_urdu_phishing",
        }
        label_map = {0: "ham", 1: "spam"}

        v1_path = self.output_dir / "pakscam_dataset.csv"
        if not v1_path.exists():
            print("[PakScam v2] Warning: v1 dataset not found, skipping.")
            return 0

        v1_df = pd.read_csv(v1_path)
        for _, row in v1_df.iterrows():
            v1_cat = str(row.get("subset_category", ""))
            v2_cat = category_map.get(v1_cat, v1_cat)
            label = label_map.get(int(row["label"]), "ham")
            lang = str(row.get("language", "en"))

            added = self._add_record(
                records,
                text=str(row["text"]),
                label=label,
                category=v2_cat,
                language=lang,
                source_type="synthetic",
                is_synthetic=True,
                origin="pakscam_v1_reimport",
                notes=f"Re-imported from pakscam_v1 ({v1_cat}).",
                template_family=f"v1_{v1_cat}",
            )
            if added:
                count += 1
        return count

    def _add_synthetic_banking_ham(self, records: list) -> int:
        """Generate synthetic legitimate banking messages."""
        count = 0
        samples = [
            (
                "HBL Alert: PKR 12,500 credited to A/C *7892 via "
                "Raast on 05-AUG-2026. Ref: RAST44810293. "
                "Balance: PKR 67,300.",
                "banking_transaction", "en",
                "hbl_raast_credit",
            ),
            (
                "Askari Bank: Your A/C *3301 debited PKR 8,000 "
                "via ATM at Askari Tower Rawalpindi. "
                "Balance: PKR 34,500. Help: 051-111-515-515.",
                "banking_transaction", "en",
                "askari_atm_debit",
            ),
            (
                "SCB Pakistan: Card *4418 charged PKR 6,200 at "
                "Hyperstar DHA Lahore. Remaining limit: "
                "PKR 93,800. Query? Call 111-111-722.",
                "banking_transaction", "en",
                "scb_card_pos",
            ),
            (
                "Faysal Bank: Salary PKR 75,000 credited to "
                "A/C *2209 on 01-AUG-2026. Balance: PKR 82,100.",
                "banking_transaction", "en",
                "faysal_salary_credit",
            ),
            (
                "MCB: Fund transfer of PKR 20,000 to A/C *5501 "
                "successful. Ref: MCB77210934. Helpline: "
                "111-000-622.",
                "banking_transaction", "en",
                "mcb_fund_transfer",
            ),
            (
                "Bank Alfalah: Your OTP for online purchase of "
                "PKR 4,999 at Daraz.pk is 738201. Valid 5 mins. "
                "Never share this code.",
                "otp_security", "en",
                "alfalah_otp",
            ),
            (
                "UBL: Your internet banking password has been "
                "changed successfully. If you did not make this "
                "change, call 111-825-888 immediately.",
                "banking_customer_service", "en",
                "ubl_password_change",
            ),
            (
                "Dear Customer, your SBP Raast ID has been "
                "registered with HBL A/C *7892. For queries "
                "call 111-111-425.",
                "banking_notification", "en",
                "hbl_raast_register",
            ),
            (
                "Meezan Bank: Profit of PKR 1,250 has been "
                "credited to your Islamic Savings A/C *6010. "
                "Current balance: PKR 310,000.",
                "banking_transaction", "en",
                "meezan_profit_credit",
            ),
            (
                "Allied Bank: Your cheque #001492 of PKR 35,000 "
                "has been cleared in A/C *8801. Balance: "
                "PKR 142,500.",
                "banking_transaction", "en",
                "abl_cheque_clear",
            ),
        ]

        for text, cat, lang, fam in samples:
            added = self._add_record(
                records, text=text, label="ham",
                category=cat, language=lang,
                source_type="synthetic", is_synthetic=True,
                origin="generated_from_template_family",
                notes="Synthetic banking HAM.",
                template_family=fam,
            )
            if added:
                count += 1
        return count

    def _add_synthetic_telecom_ham(self, records: list) -> int:
        """Generate synthetic legitimate telecom messages."""
        count = 0
        samples = [
            (
                "Jazz: Your Weekly Internet Xtreme bundle of "
                "5GB is now active for 7 days. Dial *114# to "
                "check balance.",
                "telecom_promotion", "en",
                "jazz_weekly_bundle",
            ),
            (
                "Telenor: Congratulations! Your 4G SIM upgrade "
                "is complete. Enjoy faster speeds. Dial *345# "
                "for details.",
                "telecom_service_notification", "en",
                "telenor_sim_upgrade",
            ),
            (
                "Ufone: Your Super Card Rs 600 is activated. "
                "Enjoy 6GB data, 600 mins, 600 SMS for 30 days.",
                "telecom_promotion", "en",
                "ufone_super_card",
            ),
            (
                "Jazz: Rs 50 deducted for Daily Social bundle. "
                "Unlimited WhatsApp, Facebook, Instagram for "
                "24 hours. Dial *114*2# for status.",
                "telecom_subscription", "en",
                "jazz_social_bundle",
            ),
            (
                "Zong: Your International Roaming is now active "
                "for UAE. Standard roaming charges apply. "
                "Dial *310# for rates.",
                "telecom_service_notification", "en",
                "zong_roaming",
            ),
            (
                "Telenor: You have successfully subscribed to "
                "Telenor Health. Rs 3/day. To unsub send UNSUB "
                "to 7441.",
                "telecom_subscription", "en",
                "telenor_health_sub",
            ),
            (
                "Jazz: Aap ka Super Duper Card Rs 499 activate "
                "ho gaya hai. 5GB data, 500 mins, 500 SMS, "
                "30 din ke liye.",
                "telecom_promotion", "roman_urdu",
                "jazz_super_duper_ru",
            ),
            (
                "Ufone: Aap ne Mini Budget Package subscribe "
                "kiya hai. Rs 13/day. Unsub ke liye UNSUB "
                "bhejein 3457 par.",
                "telecom_subscription", "roman_urdu",
                "ufone_mini_budget_ru",
            ),
        ]

        for text, cat, lang, fam in samples:
            added = self._add_record(
                records, text=text, label="ham",
                category=cat, language=lang,
                source_type="synthetic", is_synthetic=True,
                origin="generated_from_template_family",
                notes="Synthetic telecom HAM.",
                template_family=fam,
            )
            if added:
                count += 1
        return count

    def _add_synthetic_financial_ham(self, records: list) -> int:
        """Generate synthetic legitimate financial/loan messages."""
        count = 0
        samples = [
            (
                "JazzCash: You have received Rs 2,500 from "
                "AHMED ALI (03001234567). Balance: Rs 8,430. "
                "Trans ID: 981273910.",
                "payment_notification", "en",
                "jazzcash_p2p_receive",
            ),
            (
                "Easypaisa: Rs 1,500 bill payment to SSGC "
                "successful. Fee: Rs 0. Balance: Rs 6,200. "
                "Trans ID: EP88192.",
                "payment_notification", "en",
                "easypaisa_bill_pay",
            ),
            (
                "JazzCash: Your ReadyCash loan of Rs 5,000 "
                "has been disbursed. Total payable: Rs 5,350. "
                "Due date: 15-AUG-2026.",
                "loan_notification", "en",
                "readycash_disbursement",
            ),
            (
                "Easypaisa: Your Easyloan of Rs 3,000 is "
                "approved. Amount will be credited shortly. "
                "Repay by 20-AUG-2026.",
                "loan_notification", "en",
                "easyloan_approval",
            ),
            (
                "SadaPay: PKR 1,200 paid to Spotify Premium. "
                "Card balance: PKR 8,500.",
                "payment_notification", "en",
                "sadapay_payment",
            ),
            (
                "NayaPay: Rs 500 cashback credited to wallet "
                "for electricity bill payment. Enjoy!",
                "payment_notification", "en",
                "nayapay_cashback",
            ),
            (
                "K-Electric: Your bill for A/C 040001293819 "
                "of Rs 8,450 is due on 12-AUG-2026. Pay via "
                "bank app or JazzCash.",
                "payment_notification", "en",
                "kelectric_bill_due",
            ),
            (
                "PTCL: Your broadband bill of Rs 3,200 for "
                "August 2026 is generated. Last date: "
                "20-AUG-2026. Pay online or dial 1218.",
                "payment_notification", "en",
                "ptcl_bill",
            ),
        ]

        for text, cat, lang, fam in samples:
            added = self._add_record(
                records, text=text, label="ham",
                category=cat, language=lang,
                source_type="synthetic", is_synthetic=True,
                origin="generated_from_template_family",
                notes="Synthetic financial/loan HAM.",
                template_family=fam,
            )
            if added:
                count += 1
        return count

    def _add_synthetic_hard_negative_ham(self, records: list) -> int:
        """Generate hard-negative HAM: legitimate but suspicious-looking."""
        count = 0
        samples = [
            (
                "URGENT: Your HBL credit card payment of "
                "PKR 15,000 is due in 2 days. Avoid late fee "
                "by paying now via HBL Mobile app.",
                "banking_notification", "en",
                "hbl_urgent_payment",
                "Hard-negative: URGENT, due in 2 days, financial.",
            ),
            (
                "Last chance! Activate Zong Super Weekly Max "
                "before midnight. 12GB + 1000 mins for only "
                "Rs 220. Dial *6464#",
                "telecom_promotion", "en",
                "zong_last_chance",
                "Hard-negative: Last chance!, urgency, pricing.",
            ),
            (
                "Congratulations! Your UBL Visa Debit Card "
                "*5034 has been successfully renewed. Collect "
                "from your branch or call 111-825-888.",
                "banking_notification", "en",
                "ubl_card_renewal",
                "Hard-negative: Congratulations!, card renewal.",
            ),
            (
                "Alert: 3 failed login attempts on your HBL "
                "Mobile app. If this was not you, call "
                "111-111-425 immediately.",
                "banking_customer_service", "en",
                "hbl_login_alert",
                "Hard-negative: Alert, failed attempts, urgency.",
            ),
            (
                "Win exciting prizes with Telenor Spin the "
                "Wheel! Play daily in My Telenor App. "
                "No charges apply. T&C on telenor.com.pk",
                "telecom_promotion", "en",
                "telenor_spin_wheel",
                "Hard-negative: Win prizes, exclamation, URL.",
            ),
            (
                "FREE! Get 1GB bonus data on your next recharge "
                "of Rs 100 or more. Offer valid till "
                "10-AUG-2026. T&C apply.",
                "telecom_promotion", "en",
                "free_data_promo",
                "Hard-negative: FREE!, bonus, urgency deadline.",
            ),
            (
                "Easypaisa: IMPORTANT! Update your CNIC before "
                "31-AUG-2026 to continue using your account. "
                "Visit nearest retailer or call 3737.",
                "payment_notification", "en",
                "easypaisa_cnic_update",
                "Hard-negative: IMPORTANT!, update CNIC, deadline.",
            ),
            (
                "JazzCash: Aap ka account verify karne ke liye "
                "apne nearest JazzCash agent se milein ya "
                "helpline 051-111-124-444 par call karein.",
                "payment_notification", "roman_urdu",
                "jazzcash_verify_legit",
                "Hard-negative: verify account, Roman Urdu.",
            ),
            (
                "SBP Raast: Your Raast ID 03001234567 is now "
                "linked to Allied Bank A/C *8801. For support "
                "call your bank directly.",
                "banking_notification", "en",
                "sbp_raast_link",
                "Hard-negative: Raast ID, bank account, official.",
            ),
            (
                "Zong 4G: You have won 500MB FREE data in Zong "
                "Cricket Mania! Use it within 24 hours. "
                "Check balance *102#",
                "telecom_promotion", "en",
                "zong_cricket_reward",
                "Hard-negative: won, FREE, 24 hours, cricket.",
            ),
        ]

        for text, cat, lang, fam, note in samples:
            added = self._add_record(
                records, text=text, label="ham",
                category=cat, language=lang,
                source_type="synthetic", is_synthetic=True,
                origin="generated_from_template_family",
                notes=note,
                template_family=fam,
            )
            if added:
                count += 1
        return count

    def _add_synthetic_roman_urdu_ham(self, records: list) -> int:
        """Generate synthetic Roman Urdu legitimate messages."""
        count = 0
        samples = [
            (
                "Aap ka Easypaisa account Rs 3,500 se credit "
                "ho gaya hai. Balance: Rs 12,800. Trans ID: "
                "EP99281.",
                "payment_notification", "roman_urdu",
                "easypaisa_credit_ru",
            ),
            (
                "Zong: Aap ka Monthly Internet bundle khatam "
                "hone wala hai. Renewal ke liye Rs 500 recharge "
                "karein ya *6464# dial karein.",
                "telecom_service_notification", "roman_urdu",
                "zong_renewal_ru",
            ),
            (
                "Telenor: Aap ki complaint #88102 resolve ho "
                "gayi hai. Feedback ke liye 345 par SMS karein "
                "ya 111-345-100 call karein.",
                "telecom_service_notification", "roman_urdu",
                "telenor_complaint_ru",
            ),
            (
                "HBL: Aap ke account *7892 mein PKR 25,000 "
                "IBFT se credit ho gaye hain. Maujuda balance: "
                "PKR 92,300.",
                "banking_transaction", "roman_urdu",
                "hbl_ibft_credit_ru",
            ),
            (
                "Meezan Bank: Aap ka Roshan Digital Account "
                "successfully kholiya gaya hai. Account number: "
                "*6010. App download karein.",
                "banking_customer_service", "roman_urdu",
                "meezan_rda_ru",
            ),
        ]

        for text, cat, lang, fam in samples:
            added = self._add_record(
                records, text=text, label="ham",
                category=cat, language=lang,
                source_type="synthetic", is_synthetic=True,
                origin="generated_from_template_family",
                notes="Synthetic Roman Urdu HAM.",
                template_family=fam,
            )
            if added:
                count += 1
        return count

    def _add_synthetic_spam(self, records: list) -> int:
        """Generate synthetic Pakistani SPAM messages."""
        count = 0
        spam_samples = [
            # bank_phishing
            (
                "HBL Alert: Your account will be blocked in "
                "24 hours due to pending verification. Update "
                "now: http://hbl-secure-login.xyz",
                "bank_phishing", "en", "fake_hbl_block",
            ),
            (
                "Meezan Bank Security: Suspicious transaction "
                "detected on A/C *9012. Verify PIN immediately "
                "at http://meezan-verify.top",
                "bank_phishing", "en", "fake_meezan_verify",
            ),
            (
                "SBP Notice: Your bank accounts require "
                "mandatory KYC update before 15-AUG-2026. "
                "Submit documents: http://sbp-kyc-update.com",
                "bank_phishing", "en", "fake_sbp_kyc",
            ),
            (
                "UBL Security: Unrecognized login from "
                "unknown device. Secure your account now: "
                "http://ubl-account-secure.site",
                "bank_phishing", "en", "fake_ubl_login",
            ),
            # fake_transaction
            (
                "You have received PKR 50,000 from overseas. "
                "Claim transfer by verifying identity at "
                "http://pkr-transfer-claim.com",
                "fake_transaction", "en", "fake_overseas_transfer",
            ),
            (
                "JazzCash: Rs 25,000 credited to your wallet "
                "by mistake. Reverse immediately by sending "
                "OTP to 0300-1112233.",
                "fake_transaction", "en", "fake_jazzcash_reverse",
            ),
            (
                "Easypaisa: PKR 10,000 pending in your "
                "account. Share your PIN with our agent at "
                "0321-9876543 to release funds.",
                "fake_transaction", "en", "fake_easypaisa_pending",
            ),
            # fake_account_alert
            (
                "Your JazzCash wallet will be permanently "
                "blocked within 12 hours. Submit CNIC photo "
                "at http://jazzcash-verify.info",
                "fake_account_alert", "en", "fake_jazzcash_block",
            ),
            (
                "Easypaisa Notice: Account frozen due to "
                "irregular activity. Unfreeze: "
                "http://easypaisa-unfreeze.site/login",
                "fake_account_alert", "en", "fake_easypaisa_freeze",
            ),
            # credential_phishing
            (
                "Dear Customer, share your 6-digit OTP code "
                "with our support team to stop unauthorized "
                "transaction of PKR 45,000.",
                "credential_phishing", "en", "fake_otp_request",
            ),
            (
                "Bank Alfalah: Enter your ATM PIN and card "
                "number at http://alfalah-card-check.net to "
                "verify your account status.",
                "credential_phishing", "en", "fake_alfalah_pin",
            ),
            (
                "UBL Digital: Your mobile banking password "
                "has expired. Reset now by clicking "
                "http://ubl-reset-password.org",
                "credential_phishing", "en", "fake_ubl_password",
            ),
            # fake_prize
            (
                "Mubarak ho! Aap ka mobile number lucky draw "
                "mein select hua hai. PKR 500,000 cash prize "
                "ke liye call karein: 0312-9876543",
                "fake_prize", "roman_urdu", "fake_lucky_draw_ru",
            ),
            (
                "Congratulations! You won PKR 200,000 in PTA "
                "National Lottery. Claim before 48 hours: "
                "http://pta-lottery-claim.site",
                "fake_prize", "en", "fake_pta_lottery",
            ),
            (
                "Earn Rs 5,000 daily by working from home! "
                "No investment needed. WhatsApp us: "
                "0345-1122334",
                "fake_prize", "en", "fake_work_from_home",
            ),
            # fake_subscription
            (
                "You are subscribed to Premium VIP Club "
                "Rs 50/day. If you did not subscribe, send "
                "your CNIC to 0300-9988776 to cancel.",
                "fake_subscription", "en", "fake_vip_club",
            ),
            (
                "Alert! Rs 500 will be charged daily for "
                "your new Premium service. Cancel by sharing "
                "account details at 0321-4433221.",
                "fake_subscription", "en", "fake_premium_charge",
            ),
            # fake_loan
            (
                "URGENT: Get PKR 500,000 instant loan with "
                "zero documentation! Apply now: "
                "http://quick-loan-pakistan.com/apply",
                "fake_loan", "en", "fake_instant_loan",
            ),
            (
                "Ehsaas Emergency Cash: Rs 25,000 approved "
                "for your CNIC. Collect from agent or verify "
                "at http://ehsaas-cash.xyz",
                "fake_loan", "en", "fake_ehsaas_cash",
            ),
            # malicious_url
            (
                "Pakistan Post: Your parcel delivery failed. "
                "Reschedule at http://pak-post-delivery.top "
                "within 24 hours or it will be returned.",
                "malicious_url", "en", "fake_pakistan_post",
            ),
            (
                "FBR Tax Notice: Outstanding tax of Rs 45,000. "
                "Pay immediately to avoid penalty: "
                "http://fbr-tax-payment.site",
                "malicious_url", "en", "fake_fbr_tax",
            ),
            # roman_urdu_phishing
            (
                "Aap ka JazzCash account 24 ghante mein band "
                "ho jaye ga. Verification ke liye apna PIN "
                "bhejein 0300-1112233 par.",
                "roman_urdu_phishing", "roman_urdu",
                "fake_jazzcash_ru",
            ),
            (
                "Easypaisa Alert: Aap ka wallet suspend hone "
                "wala hai. CNIC aur PIN update karein: "
                "http://easypaisa-login.info",
                "roman_urdu_phishing", "roman_urdu",
                "fake_easypaisa_ru",
            ),
            (
                "BISP ki taraf se 25,000 rupay approved hain. "
                "Abhi claim karein 0312-9876543 par call "
                "kar ke.",
                "roman_urdu_phishing", "roman_urdu",
                "fake_bisp_ru",
            ),
            (
                "Bohot Mubarak! Aap ki SIM par PKR 100,000 ka "
                "inaam nikla hai. Claim ke liye link kholain: "
                "http://inaam-win.xyz",
                "roman_urdu_phishing", "roman_urdu",
                "fake_sim_prize_ru",
            ),
            # code_switched_phishing
            (
                "Dear customer, aap ka bank account block ho "
                "gaya hai due to suspicious activity. Unblock "
                "karein: http://bank-unblock.site",
                "code_switched_phishing", "roman_urdu",
                "fake_codeswitched_block",
            ),
            (
                "Urgent notice: Aap ki ATM card expire ho gayi "
                "hai. New card ke liye apna PIN aur CNIC "
                "share karein 0345-6677889 par.",
                "code_switched_phishing", "roman_urdu",
                "fake_codeswitched_atm",
            ),
        ]

        for text, cat, lang, fam in spam_samples:
            added = self._add_record(
                records, text=text, label="spam",
                category=cat, language=lang,
                source_type="synthetic", is_synthetic=True,
                origin="generated_from_template_family",
                notes="Synthetic Pakistani SPAM.",
                template_family=fam,
            )
            if added:
                count += 1
        return count

    def generate_dataset(self) -> pd.DataFrame:
        """Generate the complete pakscam_localized_v2 dataset."""
        records: list = []

        print("[PakScam v2] Adding user-observed SMS...")
        n_observed = self._add_user_observed(records)
        print(f"  -> {n_observed} user-observed samples added.")

        print("[PakScam v2] Re-importing PakScam v1...")
        n_v1 = self._add_pakscam_v1_reimport(records)
        print(f"  -> {n_v1} PakScam v1 samples re-imported.")

        print("[PakScam v2] Generating synthetic banking HAM...")
        n_bank = self._add_synthetic_banking_ham(records)
        print(f"  -> {n_bank} synthetic banking HAM added.")

        print("[PakScam v2] Generating synthetic telecom HAM...")
        n_telecom = self._add_synthetic_telecom_ham(records)
        print(f"  -> {n_telecom} synthetic telecom HAM added.")

        print("[PakScam v2] Generating synthetic financial HAM...")
        n_fin = self._add_synthetic_financial_ham(records)
        print(f"  -> {n_fin} synthetic financial/loan HAM added.")

        print("[PakScam v2] Generating hard-negative HAM...")
        n_hard = self._add_synthetic_hard_negative_ham(records)
        print(f"  -> {n_hard} hard-negative HAM added.")

        print("[PakScam v2] Generating synthetic Roman Urdu HAM...")
        n_ru = self._add_synthetic_roman_urdu_ham(records)
        print(f"  -> {n_ru} synthetic Roman Urdu HAM added.")

        print("[PakScam v2] Generating synthetic SPAM...")
        n_spam = self._add_synthetic_spam(records)
        print(f"  -> {n_spam} synthetic SPAM added.")

        df = pd.DataFrame(records)

        # Summary stats
        total = len(df)
        ham_count = len(df[df["label"] == "ham"])
        spam_count = len(df[df["label"] == "spam"])
        observed_count = len(
            df[df["source_type"] == "user_observed"]
        )
        synthetic_count = len(df[df["is_synthetic"]])
        v1_count = len(
            df[df["origin"] == "pakscam_v1_reimport"]
        )
        new_synthetic = synthetic_count - v1_count

        print(f"\n{'='*60}")
        print("  PAKSCAM LOCALIZED v2 DATASET SUMMARY")
        print(f"{'='*60}")
        print(f"  Total samples:       {total}")
        print(f"  HAM samples:         {ham_count}")
        print(f"  SPAM samples:        {spam_count}")
        print(f"  User-observed:       {observed_count}")
        print(f"  PakScam v1 reimport: {v1_count}")
        print(f"  New synthetic:       {new_synthetic}")
        print(f"  Template families:   "
              f"{len(self._template_families)}")
        print(f"  Unique text hashes:  {len(self._seen_hashes)}")

        # Category breakdown
        print("\n  Category distribution:")
        for cat in sorted(df["category"].unique()):
            cat_df = df[df["category"] == cat]
            print(
                f"    {cat:<35} "
                f"ham={len(cat_df[cat_df['label'] == 'ham']):>3} "
                f"spam={len(cat_df[cat_df['label'] == 'spam']):>3}"
            )

        # Save CSV
        csv_path = self.output_dir / "pakscam_localized_v2.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"\n  Dataset saved to: {csv_path}")

        # Save metadata JSON
        metadata = {
            "dataset_version": "pakscam_localized_v2",
            "total_samples": total,
            "ham_count": ham_count,
            "spam_count": spam_count,
            "user_observed_count": observed_count,
            "pakscam_v1_reimport_count": v1_count,
            "new_synthetic_count": new_synthetic,
            "template_families": len(self._template_families),
            "unique_hashes": len(self._seen_hashes),
            "dataset_hash": hashlib.sha256(
                df.to_csv(index=False).encode("utf-8")
            ).hexdigest(),
            "categories": {
                cat: {
                    "ham": int(
                        len(cat_df[cat_df["label"] == "ham"])
                    ),
                    "spam": int(
                        len(cat_df[cat_df["label"] == "spam"])
                    ),
                }
                for cat, cat_df in df.groupby("category")
            },
            "template_family_assignments": {
                k: v for k, v in self._template_families.items()
            },
            "provenance_note": (
                "The Pakistani corpus contains both observed "
                "user-provided SMS examples and "
                "synthetic/template-derived examples. Synthetic "
                "examples are explicitly identified and are not "
                "presented as independently collected real-world "
                "data."
            ),
        }

        meta_path = (
            self.output_dir / "pakscam_localized_v2_metadata.json"
        )
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  Metadata saved to: {meta_path}")

        return df


if __name__ == "__main__":
    generator = PakScamV2DatasetGenerator()
    generator.generate_dataset()
