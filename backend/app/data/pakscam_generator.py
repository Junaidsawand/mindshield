# ==============================================================================
# MindShield Backend — Localized Pakistani SMS Dataset Generator (PakScam v1)
# ==============================================================================

from pathlib import Path
from typing import Dict, List
import pandas as pd


class PakScamDatasetGenerator:
    """Generates a synthetic localized Pakistani SMS dataset (`pakscam-v1`).

    Covers legitimate Pakistani banking transaction alerts, hard-negative HAM,
    financial phishing, prize scams, and Roman Urdu / code-switched SMS. All
    samples are explicitly tagged with `is_synthetic=True`.
    """

    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dataset(self) -> pd.DataFrame:
        """Generate comprehensive PakScam synthetic dataset."""
        records: List[Dict[str, any]] = []

        # ── 1. Legitimate Banking & Transactional HAM (Label 0) ──────────────
        legit_banking = [
            (
                "PKR 1,000 received from AZHAR ALI* in your UBL A/C *5034 on "
                "08-AUG-2026 14:45 via IBFT. Tx ID 6959318669. For info: 111825888."
            ),
            (
                "PKR 5,500.00 debited from A/C *4821 at HBL ATM Gulberg Lahore "
                "on 08-AUG-2026. Bal: PKR 42,100.00. Help: 111-111-425."
            ),
            (
                "Meezan Bank: Your A/C *9012 credited with PKR 15,000.00 via "
                "Raast ID. Ref: RAST92830192. Bal: PKR 89,250.00."
            ),
            (
                "JazzCash: You have received PKR 2,500 from MUHAMMAD USMAN "
                "(03001234567). Balance: PKR 8,430.00. Trans ID: 981273910."
            ),
            (
                "Easypaisa: Rs 1,200 transferred to K-Electric Bill Payment. "
                "Fee: Rs 0.00. New Balance: Rs 4,150. Trans ID: 8812903."
            ),
            (
                "Bank Alfalah: Your OTP for online purchase of PKR 3,499.00 at "
                "Daraz PK is 492019. Valid for 5 mins. Do not share."
            ),
            (
                "Faysal Bank: Salary credit of PKR 85,000.00 received in A/C "
                "*1102 on 01-AUG-2026. Current Balance: PKR 91,400.00."
            ),
            (
                "MCB Live: Fund Transfer of PKR 10,000 to Account *4401 "
                "successful. Ref No: MCB882910. Helpline 111-000-622."
            ),
            (
                "Allied Bank: PKR 500 loaded to Mobile Prepaid 03215550192. "
                "Transaction ID: ABL99201. Thank you for using ABL Direct."
            ),
            (
                "Dear Customer, your K-Electric bill for A/C 040001293819 of "
                "Rs 8,450 is due on 12-AUG-2026. Pay via bank app."
            ),
            (
                "Careem: Your ride with Ahmed is confirmed. Captain vehicle: "
                "Toyota Corolla LEA-19-201. Live tracking: careem.me/ride"
            ),
            (
                "Daraz PK: Your order #491290321 has been dispatched via TCS. "
                "Tracking ID: TCS99201. Expected delivery: Tomorrow."
            ),
            (
                "SadaPay: PKR 750 paid to Netflix International. Remaining "
                "card balance: PKR 12,300.00."
            ),
            (
                "NayaPay: Rs 300 cash back credited to your wallet for mobile "
                "load transaction. Enjoy seamless payments!"
            ),
            (
                "Zong 4G: Your 12GB Super Weekly Max bundle has been activated "
                "successfully. Dial *102# to check remaining resources."
            ),
        ]

        for text in legit_banking:
            records.append({
                "text": text,
                "label": 0,
                "is_synthetic": True,
                "language": "en",
                "subset_category": "banking_ham",
            })

        # ── 2. Hard-Negative Legitimate HAM (Label 0) ────────────────────────
        hard_negatives = [
            (
                "UBL ALERT: A/C *5034 debited PKR 25,000 via IBFT to TARIQ "
                "MEHMOOD. Tx ID 1092830192. Call 111825888 if not done by you."
            ),
            (
                "HBL Notification: Transaction of PKR 50,000 via Raast ID "
                "03009876543 successful. Fee: PKR 0. Balance: PKR 140,000."
            ),
            (
                "Meezan Bank: A/C *9012 OTP is 881920 for Fund Transfer of PKR "
                "45,000. NEVER share your OTP with anyone, including bank staff."
            ),
            (
                "JazzCash Alert: Rs 15,000 transferred to ZONG Microfinance "
                "Bank A/C *0012. Fee: Rs 15.00. Trans ID 77281902."
            ),
            (
                "Easypaisa: Rs 30,000 received from Telenor Bank A/C *9910. "
                "New balance: Rs 48,200. Helpline 3737."
            ),
            (
                "Bank Alfalah Card Alert: POS Transaction of PKR 18,900 at "
                "Hyperstar Lahore on 08-AUG-2026. Remaining limit: PKR 120,000."
            ),
            (
                "Standard Chartered: Your credit card *1192 charged PKR "
                "12,450.00 at Emirates Airline. Query? Call 111-111-722."
            ),
            (
                "Pak Railways: Ticket #PR99210 confirmed for Karakoram Express. "
                "Coach AC Standard, Seat 14. Dep: 16:00 09-AUG-2026."
            ),
        ]

        for text in hard_negatives:
            records.append({
                "text": text,
                "label": 0,
                "is_synthetic": True,
                "language": "en",
                "subset_category": "hard_negative_ham",
            })

        # ── 3. Malicious Financial Phishing & Urgency SPAM (Label 1) ──────────
        phishing_spam = [
            (
                "Your UBL account has been suspended. Verify your account "
                "immediately by clicking http://example.com/login"
            ),
            (
                "HBL Urgent Alert: Your mobile banking account is blocked due to "
                "pending biometric verification. Unblock now: http://hbl-verify.xyz"
            ),
            (
                "Meezan Bank Notice: Suspicious activity detected on A/C *9012. "
                "Confirm your PIN immediately at http://meezan-security.top/verify"
            ),
            (
                "JazzCash Security: Your wallet will be blocked within 24 hours. "
                "Submit CNIC at http://jazzcash-update.info to avoid suspension."
            ),
            (
                "Easypaisa Alert: Account frozen due to invalid registration. "
                "Verify identity at http://easypaisa-help.site/login now."
            ),
            (
                "State Bank of Pakistan: Your account requires mandatory KYC update. "
                "Failure will result in freeze: http://sbp-kyc.com/update"
            ),
            (
                "Bank Alfalah: Security alert! Unrecognized login attempt from IP. "
                "Secure your account now: http://alfalah-secure.org"
            ),
            (
                "Faysal Bank: Your debit card *1102 has been temporarily locked. "
                "Restore access immediately: http://faysal-card-verify.net"
            ),
            (
                "URGENT: Your ATM card has been blocked. Call security department "
                "immediately at 0300-1234567 or visit http://bank-card-unlock.site"
            ),
            (
                "Share your 6-digit OTP code with our customer support officer "
                "immediately to stop unauthorized transaction of PKR 50,000."
            ),
        ]

        for text in phishing_spam:
            records.append({
                "text": text,
                "label": 1,
                "is_synthetic": True,
                "language": "en",
                "subset_category": "phishing_spam",
            })

        # ── 4. Pakistani Prize & Loan Fraud SPAM (Label 1) ──────────────────
        prize_loan_spam = [
            (
                "Congratulations! You have won PKR 100,000. Click "
                "http://example.com to claim your prize immediately."
            ),
            (
                "Benazir Income Support Programme (BISP): PKR 25,000 grant approved. "
                "Contact 0312-9876543 to receive your cash immediately."
            ),
            (
                "Jeeto Pakistan Offer: Mubarak ho! Aap ka 5 tola sona aur PKR "
                "500,000 inaam nikla hai. Claim karne ke liye call 0301-8877665."
            ),
            (
                "Ehsaas Emergency Cash: Rs 14,000 status approved. Collect cash "
                "from nearest center or verify online at http://ehsaas-grant.xyz"
            ),
            (
                "Instant Emergency Loan: Get up to PKR 200,000 loan approved in 5 "
                "minutes without documentation. Apply: http://quick-cash-loan.pk"
            ),
            (
                "Mubarak! You are selected for Gold Lucky Draw 2026. Claim your "
                "Honda 125 bike by registering at http://gold-draw.site/claim"
            ),
            (
                "Earn PKR 5,000 daily from home by typing simple SMS messages. "
                "No investment required! WhatsApp us at 0345-1122334."
            ),
            (
                "Earle Gold Lottery: Rs 1,000,000 cash prize won! Send Rs 2,000 "
                "fee via JazzCash to 0302-7711223 to receive prize."
            ),
        ]

        for text in prize_loan_spam:
            records.append({
                "text": text,
                "label": 1,
                "is_synthetic": True,
                "language": "en",
                "subset_category": "prize_spam",
            })

        # ── 5. Roman Urdu Legitimate HAM (Label 0) ───────────────────────────
        roman_urdu_ham = [
            (
                "Aap ka JazzCash account Rs 500 se credit ho gaya hai. Maujuda "
                "balance Rs 1,850 hai."
            ),
            "Salam bhai, ghar aate waqt doodh aur dahi lete aana. Shukriya.",
            (
                "Easypaisa bill payment kamyab ho chuki hai. Rs 2,300 K-Electric "
                "ko bhej diye gaye hain."
            ),
            (
                "Aap ka Daraz parcel raaste mein hai. Delivery rider aap se "
                "jald rabta karega."
            ),
            (
                "UBL Digital: Aap ka Raast ID successfully register ho gaya hai. "
                "Balance check karne ke liye app login karein."
            ),
            "Meeting kal subah 10 baje office mein hogi. Apni presentation tayar.",
            (
                "Zong 4G: Aap ka remaining data 4.5 GB hai. Check karne ke liye "
                "*102# dial karein."
            ),
            (
                "Dear Customer, aap ki complaint #99201 resolve kar di gayi hai. "
                "Feedback ke liye 111-111-222 par call karein."
            ),
        ]

        for text in roman_urdu_ham:
            records.append({
                "text": text,
                "label": 0,
                "is_synthetic": True,
                "language": "roman_urdu",
                "subset_category": "roman_urdu_ham",
            })

        # ── 6. Roman Urdu Threat & Phishing SPAM (Label 1) ───────────────────
        roman_urdu_spam = [
            (
                "Mubarak ho! Aap ko BISP ki taraf se 25,000 rupay cash inaam "
                "mila hai. Abhi 0312-9876543 par call karke wasool karein."
            ),
            (
                "Aap ka JazzCash account 24 ghante mein band kar diya jaye ga. "
                "Verification ke liye http://jazzcash-verify.site par login."
            ),
            (
                "Easypaisa Alert: Aap ka account suspend hone wala hai. Abhi apna "
                "PIN aur CNIC update karein http://easypaisa-login.info par."
            ),
            (
                "Meezan Bank Urgent: Aap ke account par mashkook activity mili hai. "
                "Verify karein: http://meezan-help.org aksar block na ho."
            ),
            (
                "Ghar baithay mahana 50,000 rupay kamayein. Sirf mobile par kaam "
                "karein. WhatsApp par rabta karein 0300-9988776."
            ),
            (
                "Ehsaas Kafalat Program: Aap ke 14,000 rupay aa gaye hain. Wasool "
                "karne ke liye call karein: 0321-4433221."
            ),
            (
                "Bohot Mubarak! Aap ki SIM par PKR 100,000 ka inaam nikla hai. "
                "Claim karne ke liye link kholain http://inaam-win.xyz"
            ),
            (
                "Urgent Notice: HBL account block ho gaya hai. Account unlock "
                "karne ke liye OTP code 0345-9988112 par SMS karein."
            ),
        ]

        for text in roman_urdu_spam:
            records.append({
                "text": text,
                "label": 1,
                "is_synthetic": True,
                "language": "roman_urdu",
                "subset_category": "roman_urdu_spam",
            })

        df = pd.DataFrame(records)
        output_file = self.output_dir / "pakscam_dataset.csv"
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"[PakScam Generator] Exported {len(df)} samples to {output_file}")
        return df


if __name__ == "__main__":
    generator = PakScamDatasetGenerator()
    generator.generate_dataset()
