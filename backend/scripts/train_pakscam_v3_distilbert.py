# ==============================================================================
# MindShield Backend - DistilBERT PakScam v3 Fine-Tuning Script
# Phase 3.8: Mix-C + Roman Urdu Patch
# ==============================================================================
import json
import re
import shutil
import time
from pathlib import Path

import pandas as pd

from app.distilbert.config import DistilBERTConfig
from app.distilbert.trainer import DistilBERTTrainer
from app.core.model_loader import HuggingFaceModelLoader


# 65 augmentation samples: 55 HAM + 10 SPAM
# G1=bit.ly banking HAM(15), G2=bit.ly telecom HAM(5), G3=bit.ly service HAM(5)
# G4=flash-sale HAM(8), G5=VAS subscription HAM(7), G6=Roman Urdu HAM patch(15)
# G7=Roman Urdu + bit.ly SPAM(5), G8=social engineering SPAM(5)
V3_AUGMENTATIONS = [
    # G1 bit.ly banking HAM (15) - inverts URL-spam signal ratio
    ("UBL Customer Support. Visit our official portal: https://bit.ly/ubl-help", "ham", "banking_customer_service", "ubl_bitly_support"),
    ("HBL: Download our official Mobile Banking app: bit.ly/hbl-app", "ham", "banking_customer_service", "hbl_bitly_app"),
    ("Meezan Bank: Access digital banking at bit.ly/meezan-portal. Call 111-331-331.", "ham", "banking_customer_service", "meezan_bitly_portal"),
    ("JazzCash: Install our latest app update: bit.ly/jazzcash-update", "ham", "banking_customer_service", "jazzcash_bitly_update"),
    ("Easypaisa: Give feedback at bit.ly/ep-survey. Your opinion matters!", "ham", "banking_customer_service", "easypaisa_bitly_survey"),
    ("Allied Bank: Rate your branch visit at bit.ly/abl-feedback. Help us improve.", "ham", "banking_customer_service", "abl_bitly_feedback"),
    ("Bank Alfalah: View your e-statement at bit.ly/alfalah-stmt. Updated monthly.", "ham", "banking_customer_service", "alfalah_bitly_stmt"),
    ("Faysal Bank: Join loyalty rewards program: bit.ly/faysal-rewards", "ham", "banking_customer_service", "faysal_bitly_rewards"),
    ("Standard Chartered Pakistan: Book appointment online: bit.ly/scb-appt", "ham", "banking_customer_service", "scb_bitly_appt"),
    ("Askari Bank: Download ASKARI Mobile app: bit.ly/askari-app. Safe and convenient.", "ham", "banking_customer_service", "askari_bitly_app"),
    ("SadaPay: Check our fee schedule at bit.ly/sadapay-info. Transparent banking.", "ham", "banking_customer_service", "sadapay_bitly_info"),
    ("NayaPay: Read privacy policy update at bit.ly/nayapay-policy", "ham", "banking_customer_service", "nayapay_bitly_policy"),
    ("Habib Metro Bank: Apply for personal loan online: bit.ly/hm-loan", "ham", "banking_customer_service", "habibmetro_bitly_loan"),
    ("MCB: Activate your debit card for online shopping at bit.ly/mcb-activate", "ham", "banking_customer_service", "mcb_bitly_activate"),
    ("UBL: Submit feedback on recent branch service: https://bit.ly/ubl-feedback-form", "ham", "banking_customer_service", "ubl_bitly_feedback"),
    # G2 bit.ly telecom HAM (5)
    ("Zong 4G: Download My Zong App: bit.ly/myzong-app. Exclusive in-app offers!", "ham", "telecom_service_notification", "zong_bitly_app"),
    ("Jazz: Download My Jazz app: bit.ly/myjazz-app. 24/7 self-service available.", "ham", "telecom_service_notification", "jazz_bitly_app"),
    ("Telenor: Download My Telenor app: bit.ly/mytelenor-app. Works on all devices.", "ham", "telecom_service_notification", "telenor_bitly_app"),
    ("Ufone: Get U-Wallet app: bit.ly/ufone-uwallet. Limited-time Rs 50 signup bonus!", "ham", "telecom_service_notification", "ufone_bitly_app"),
    ("Zong: Join Zong Community: bit.ly/zong-community. Win prizes every week. Free!", "ham", "telecom_promotion", "zong_bitly_community"),
    # G3 bit.ly service HAM (5)
    ("PTCL: Pay broadband bill at bit.ly/ptcl-pay. Quick secure. 24/7 available.", "ham", "payment_notification", "ptcl_bitly_pay"),
    ("K-Electric: Pay electricity bill via bit.ly/ke-pay. Avoid late fees.", "ham", "payment_notification", "kelectric_bitly_pay"),
    ("SSGC: Check gas bill and pay online at bit.ly/ssgc-bill. No queues.", "ham", "payment_notification", "ssgc_bitly_bill"),
    ("Pakistan Post: Track parcel at bit.ly/pakpost-track. Enter tracking number.", "ham", "payment_notification", "pakpost_bitly_track"),
    ("FBR: File income tax return at bit.ly/fbr-iris. Deadline 30-SEP-2026.", "ham", "payment_notification", "fbr_bitly_iris"),
    # G4 flash-sale promo HAM (8) - covers zong_flash_sale family gap
    ("MEGA SALE! Get 30% OFF on all Jazz bundles this Friday only! Activate via *111# or My Jazz app. Offer expires midnight.", "ham", "telecom_promotion", "jazz_flash_sale_30"),
    ("Zong Ramazan Special: 40% OFF on all monthly data bundles! Subscribe via My Zong App or dial *6464#. Hurry, limited time!", "ham", "telecom_promotion", "zong_ramazan_sale"),
    ("Telenor Super Deal TONIGHT ONLY! Get double data on any bundle. Dial *345# or visit MyTelenor app. Valid till 11:59PM.", "ham", "telecom_promotion", "telenor_super_deal"),
    ("Ufone FLASH SALE: 50% OFF on Super Card Rs 600! Get it NOW via *123# before midnight. Only for prepaid customers.", "ham", "telecom_promotion", "ufone_flash_50_off"),
    ("Jazz Independence Day Offer: FREE 1GB for ALL customers! Dial *114*7# to activate. Valid 14-AUG only.", "ham", "telecom_promotion", "jazz_independence_free"),
    ("Zong: Exclusive for YOU - WhatsApp bundle at 60% discount! Valid today 8PM-12AM. My Zong App NOW: bit.ly/zong-deal", "ham", "telecom_promotion", "zong_exclusive_whatsapp"),
    ("Telenor: Book Telenor Health consultation for Rs 50 only. Valid this weekend. Book: bit.ly/tnr-health", "ham", "telecom_promotion", "telenor_health_discount"),
    ("Ufone BIGGEST SALE of the year! 70% OFF on Ufone SIM packages. Activate: bit.ly/ufone-sale or *123#", "ham", "telecom_promotion", "ufone_biggest_sale"),
    # G5 VAS subscription HAM (7) - covers gaming_royale_vas variants
    ("You are now subscribed to Telenor TV Rs 15/day (Auto Renewal). Watch: http://telenortv.pk. Unsub: STOP to 5454.", "ham", "telecom_subscription", "telenor_tv_vas"),
    ("Thanks for subscribing to Cricket Live Score Rs 3/day (Auto Renewal). Check: http://cricket.ufone.com. Unsub: STOP to 3737.", "ham", "telecom_subscription", "ufone_cricket_vas"),
    ("You have subscribed to Jazz News Service Rs 2/day. Breaking news: http://news.jazz.com.pk. Unsub: STOP to 1234.", "ham", "telecom_subscription", "jazz_news_vas"),
    ("Zong Daily Horoscope activated Rs 2/day (Auto-renew). View: http://horoscope.zong.com.pk. Unsub: STOP to 4040.", "ham", "telecom_subscription", "zong_horoscope_vas"),
    ("Subscribed to Quran-e-Pak Rs 1/day. Listen: http://quran.jazz.com.pk. Auto-renew. Cancel: STOP to 9900.", "ham", "telecom_subscription", "jazz_quran_vas"),
    ("Thanks for subscribing to Ufone Cooking Tips Rs 2/day (Auto Renewal). Recipes: http://cook.ufone.com. Unsub: UNSUB to 2222.", "ham", "telecom_subscription", "ufone_cooking_vas"),
    ("You are subscribed to Zong Weather Updates Rs 2/day. Forecasts: http://weather.zong.com.pk. Unsub: UNSUB to 5050.", "ham", "telecom_subscription", "zong_weather_vas"),
    # G6 Roman Urdu HAM patch (15) - closes 4 proxy FP categories
    ("HBL: Aap ke account *7892 mein PKR 15,000 Raast se credit ho gaye. Balance: PKR 67,300. Madad: 111-111-425", "ham", "banking_transaction", "hbl_credit_ru_patch1"),
    ("JazzCash: Aap ke wallet mein Rs 3,000 AHMED KHAN ki taraf se transfer ho gaye. Naya balance: Rs 8,750.", "ham", "banking_transaction", "jazzcash_transfer_ru_patch"),
    ("Easypaisa: Rs 2,500 K-Electric bill ke liye gaye. Baqia balance: Rs 5,100. Trans ID: EP99281.", "ham", "banking_transaction", "easypaisa_bill_ru_patch"),
    ("Meezan Bank: Aap ki A/C *6010 mein PKR 50,000 IBFT se credit ho gaye. Balance: PKR 310,000.", "ham", "banking_transaction", "meezan_ibft_ru_patch"),
    ("UBL: Aap ki A/C *5034 se PKR 10,000 UBL Omni ke zariye gaye. Trans ID: 9910293. Madad: 111-825-888.", "ham", "banking_transaction", "ubl_omni_ru_patch"),
    ("Zong 4G: Sirf Rs 81 recharge kar ke rozana 2GB data, 1000 mins, 100 SMS hasil karein. *6464# dial.", "ham", "telecom_promotion", "zong_bundle_ru_patch1"),
    ("Jazz: Rs 499 mein Super Duper Card - 5GB data, 500 mins, 500 SMS 30 din. *111# dial karein.", "ham", "telecom_promotion", "jazz_super_duper_ru_patch"),
    ("Ufone: Rs 300 ka Mini Budget - 3GB data + 300 mins 30 din ke liye. *123# se activate.", "ham", "telecom_promotion", "ufone_budget_ru_patch"),
    ("Telenor: Rs 200 mein 2GB weekly bundle. My Telenor app ya *345# se activate karein.", "ham", "telecom_promotion", "telenor_weekly_ru_patch"),
    ("Zong: Aap ka Monthly bundle Rs 500 mein renew ho gaya. 30 din 10GB data. *102# check.", "ham", "telecom_service_notification", "zong_renewal_ru_patch"),
    ("Daraz: Aap ka order #4912903 TCS ke zariye dispatch ho gaya. Tracking: TCS99201. Kal delivery.", "ham", "telecom_service_notification", "daraz_delivery_ru_patch"),
    ("Careem: Aap ki ride confirm ho gayi. Driver: Ahmed Khan, Corolla LEA-19-201. ETA: 5 mins.", "ham", "telecom_service_notification", "careem_ride_ru_patch"),
    ("Zong: Aap ka remaining data 1.5 GB hai. Renewal: *6464# dial karein ya My Zong App.", "ham", "telecom_service_notification", "zong_data_check_ru_patch"),
    ("Jazz: Aap ki shikayat #88102 resolve ho gayi. Feedback ke liye *117# dial karein.", "ham", "telecom_service_notification", "jazz_complaint_ru_patch"),
    ("Telenor: Aap ka SIM 4G mein upgrade ho gaya. Faster speeds. Details: *345# dial.", "ham", "telecom_service_notification", "telenor_4g_upgrade_ru_patch"),
    # G7 Hard SPAM - Roman Urdu + bit.ly (5)
    ("Mubarak ho! BISP grant approved. CNIC verify: bit.ly/bisp-claim999. 48 ghante expire!", "spam", "roman_urdu_phishing", "fake_bisp_bitly_ru"),
    ("JazzCash: Rs 5,000 pending. Verify karein: bit.ly/jc-verify99. Abhi!", "spam", "roman_urdu_phishing", "fake_jazzcash_bitly_ru"),
    ("URGENT: Aap ka Easypaisa suspend ho raha. Restore: bit.ly/ep-restore99. 2 ghante!", "spam", "roman_urdu_phishing", "fake_easypaisa_bitly_ru"),
    ("HBL lottery mein lucky nikla! PKR 50,000 claim: bit.ly/hbl-lucky. Sirf aaj!", "spam", "roman_urdu_phishing", "fake_hbl_lottery_bitly"),
    ("Ehsaas cash Rs 25,000 approved. Claim: bit.ly/ehsaas-cash99. Jaldi karein!", "spam", "roman_urdu_phishing", "fake_ehsaas_bitly_ru"),
    # G8 Hard SPAM - social engineering no URL (5)
    ("URGENT: Your UBL card *5034 will be blocked in 2 hours. Call security: 0300-9988001 NOW.", "spam", "bank_phishing", "fake_ubl_call_social"),
    ("HBL Security: Unrecognized OTP request. Share OTP with agent 0321-1122334 to cancel.", "spam", "credential_phishing", "fake_hbl_otp_social"),
    ("Dear Customer, your Easypaisa wallet is under review. Share mPIN with officer 0312-5544321.", "spam", "credential_phishing", "fake_ep_mpin_social"),
    ("Meezan Bank: PKR 200,000 wire transfer pending. Cancel: call fraud line 0345-9988556 NOW.", "spam", "bank_phishing", "fake_meezan_wire_social"),
    ("State Bank: Mandatory CNIC verification required by 15-AUG-2026. Call: 0300-1122993.", "spam", "credential_phishing", "fake_sbp_cnic_social"),
]


def split_pakscam_by_family(pak_df, train_ratio=0.80, seed=42):
    import random
    families = pak_df["template_family"].unique().tolist()
    rng = random.Random(seed)
    rng.shuffle(families)
    n = max(1, int(len(families) * train_ratio))
    tr = set(families[:n])
    te = set(families[n:])
    return (
        pak_df[pak_df["template_family"].isin(tr)].copy(),
        pak_df[pak_df["template_family"].isin(te)].copy(),
    )


def main():
    print("=" * 70)
    print("  MINDSHIELD - DISTILBERT-PAKSCAM-V3 FINE-TUNING  (Phase 3.8)")
    print("=" * 70)

    backend = Path(__file__).resolve().parents[1]
    processed = backend / "data/processed"
    v3_dir = backend / "data/models/distilbert_pakscam_v3"
    v1_dir = backend / "data/models/distilbert_pakscam_v1"
    v2_dir = backend / "data/models/distilbert_pakscam_v2"
    staging = backend / "data/models/distilbert"

    assert v3_dir != v1_dir and v3_dir != v2_dir, "v3 must not overwrite v1 or v2"
    print(f"[Safety] Output: {v3_dir}")
    print(f"[Safety] v1 untouched: {v1_dir}")

    train_df = pd.read_csv(processed / "train.csv")
    val_df = pd.read_csv(processed / "val.csv")
    test_df = pd.read_csv(processed / "test.csv")
    pak_df = pd.read_csv(processed / "pakscam_localized_v2.csv")

    aug_df = pd.DataFrame(
        [{"text": t, "label": l, "category": c, "template_family": tf}
         for t, l, c, tf in V3_AUGMENTATIONS]
    )
    aug_df["is_synthetic"] = True
    aug_df["source_type"] = "v3_augmentation"

    pak_v3 = pd.concat([pak_df, aug_df], ignore_index=True)
    pak_v3["label_int"] = pak_v3["label"].map({"ham": 0, "spam": 1})

    aug_h = int(aug_df["label"].eq("ham").sum())
    aug_s = int(aug_df["label"].eq("spam").sum())
    print(f"[Data] UCI Train: {len(train_df)}")
    print(f"[Data] UCI Val:   {len(val_df)}")
    print(f"[Data] UCI Test:  {len(test_df)}")
    print(f"[Data] PakScam v2 base: {len(pak_df)}")
    print(f"[Data] v3 Augmentations: {len(aug_df)} (HAM={aug_h}, SPAM={aug_s})")
    print(f"[Data] PakScam v3 total: {len(pak_v3)} "
          f"(HAM={pak_v3['label'].eq('ham').sum()}, "
          f"SPAM={pak_v3['label'].eq('spam').sum()})")

    pak_train, pak_test = split_pakscam_by_family(pak_v3, 0.80, 42)
    print(f"[Split] Pak v3 Train: {len(pak_train)} "
          f"(families: {pak_train['template_family'].nunique()})")
    print(f"[Split] Pak v3 Test:  {len(pak_test)} "
          f"(families: {pak_test['template_family'].nunique()})")

    overlap = set(pak_train["template_family"]) & set(pak_test["template_family"])
    if overlap:
        raise ValueError(f"Template family leakage: {overlap}")
    print("[Leakage Check] PASSED")

    slim = pak_train[["text", "label_int"]].rename(columns={"label_int": "label"})
    combined_train = pd.concat([train_df, slim, slim, slim], ignore_index=True)
    val_slim = pak_test[["text", "label_int"]].rename(columns={"label_int": "label"})
    combined_val = pd.concat([val_df, val_slim], ignore_index=True)

    u = len(train_df)
    p = len(slim) * 3
    t = len(combined_train)
    print(f"[Mix-C] Combined Train: {t}")
    print(f"  UCI: {u} ({u / t:.1%})")
    print(f"  Pak: {p} ({p / t:.1%}) [{len(slim)} unique x3]")
    print(f"  Combined Val: {len(combined_val)}")

    url_pat = re.compile(r"http|bit\.ly|tinyurl", re.I)
    uh = sum(1 for x, l in zip(combined_train["text"], combined_train["label"])
             if url_pat.search(str(x)) and l == 0)
    us = sum(1 for x, l in zip(combined_train["text"], combined_train["label"])
             if url_pat.search(str(x)) and l == 1)
    rt = us / uh if uh > 0 else float("inf")
    print(f"[URL Signal] HAM={uh} ({uh / (uh + us):.1%}) "
          f"SPAM={us} ({us / (uh + us):.1%}) ratio={rt:.2f}:1")
    print("  OK: URL bias corrected" if rt <= 3.0 else "  WARNING: ratio still high")

    config = DistilBERTConfig(
        models_output_dir=staging,
        epochs=4,
        learning_rate=2e-5,
        batch_size=32,
        max_length=128,
        patience=3,
    )
    print(f"[Config] epochs={config.epochs} lr={config.learning_rate} "
          f"max_length={config.max_length} batch={config.batch_size} "
          f"patience={config.patience} device={config.device}")

    trainer = DistilBERTTrainer(config)
    ts = time.perf_counter()
    metrics, history = trainer.train_and_evaluate(
        combined_train, combined_val, test_df
    )
    tt = time.perf_counter() - ts

    v3_dir.mkdir(parents=True, exist_ok=True)
    for item in staging.glob("*"):
        if item.is_file():
            shutil.copy(item, v3_dir / item.name)

    cfg = {
        "model_version": "distilbert-pakscam-v3",
        "phase": "3.8",
        "base_model": "distilbert-base-uncased",
        "epochs": config.epochs,
        "max_length": config.max_length,
        "learning_rate": config.learning_rate,
        "batch_size": config.batch_size,
        "seed": config.seed,
        "patience": config.patience,
        "mix_strategy": "Mix-C Pak 3x oversampling",
        "uci_train_samples": len(train_df),
        "pakscam_v2_base": len(pak_df),
        "v3_aug_total": len(aug_df),
        "v3_aug_ham": aug_h,
        "v3_aug_spam": aug_s,
        "pak_train_unique": len(slim),
        "pak_train_3x": len(slim) * 3,
        "combined_train": len(combined_train),
        "combined_val": len(combined_val),
        "uci_test": len(test_df),
        "pak_test": len(pak_test),
        "url_ham": uh,
        "url_spam": us,
        "url_ratio": round(rt, 3),
        "production_modified": False,
        "total_sec": round(tt, 1),
    }
    with open(v3_dir / "training_config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print(f"[Archive] Saved to {v3_dir}  ({tt / 60:.1f} min)")

    print("\n" + "=" * 70)
    print("  POST-TRAINING DIAGNOSTIC")
    print("=" * 70)
    loader = HuggingFaceModelLoader(model_path=str(v3_dir))
    loader.load()
    diags = [
        ("UBL IBFT Receipt [HAM]",
         "PKR 5,030 received from ILAM UL DIN* in your UBL A/C *5034 on 04-AUG-2026 via IBFT. Tx ID 6940522193."),
        ("UBL bit.ly complaint [HAM]",
         "Dear UBL Customer, You may log your complaints via our Contact Center or visit: https://bit.ly/2WceaFA"),
        ("Zong 50pct OFF bit.ly [HAM]",
         "50% OFF Only 4 You! Make the most of Z Hour sale 5PM-9PM get 50% OFF WhatsApp Plus Bundle. Tap now: bit.ly/3rY7XHq"),
        ("Gaming Royale VAS [HAM]",
         "Thanks for subscribing to Gaming Royale at Rs 11.95/Day (Auto Renewal). Play on http://z.gamingroyale.club. Unsub: http://z.gamingroyale.club/u"),
        ("ReadyCash Overdue [HAM]",
         "Your ReadCash is Overdue! Save on the next weekly fee of Rs 160 by repaying Rs 3151.18 now by dialing *786*4*2#."),
        ("1 DAY LEFT ReadyCash [HAM]",
         "1 DAY LEFT! Your ReadyCash loan is due tomorrow! Dial *786*4*2# to repay Rs 3151.18 on time."),
        ("Zong Engage prize lang [HAM]",
         "Jeetne ke liye tayyar ho jao! aur jeeto bade inaam, Zong Engage ke taraf se khaas http://games.zongengage.com.pk 6PKR/Day"),
        ("Prize Phishing [SPAM]",
         "Congratulations! You have won PKR 100,000. Click http://example.com to claim your prize immediately."),
        ("Fake HBL Block [SPAM]",
         "HBL Alert: Your account will be blocked in 24 hours due to pending verification. Update now: http://hbl-secure-login.xyz"),
        ("Fake UBL Suspension [SPAM]",
         "Your UBL account has been suspended. Verify your account immediately by clicking http://example.com/login"),
        ("OTP Phishing [SPAM]",
         "Dear Customer, share your 6-digit OTP code with our support team to stop unauthorized transaction of PKR 45,000."),
        ("BISP RU Scam [SPAM]",
         "BISP ki taraf se 25,000 rupay approved hain. Abhi claim karein 0312-9876543 par call kar ke."),
    ]
    all_pass = True
    for title, text in diags:
        pred = loader.predict(text)
        exp = "safe" if "[HAM]" in title else "phishing"
        ok = "PASS" if pred.label == exp else "FAIL REGRESSION"
        if ok != "PASS":
            all_pass = False
        print(f"  [{ok}] {title}: label={pred.label} conf={pred.confidence:.4f}")

    print("\n" + "=" * 70)
    print("  TRAINING COMPLETE - distilbert-pakscam-v3")
    if all_pass:
        print("  All diagnostic checks PASSED")
    else:
        print("  WARNING: Some diagnostic checks FAILED - run full eval suite")
    print(f"  Next step: python scripts/evaluate_v3_suite.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
