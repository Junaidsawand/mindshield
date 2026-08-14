"""
Phase 3.8 — Promotion Gate Evaluation Suite
Evaluates distilbert-pakscam-v1, v2, and v3 side-by-side.
Reports every metric needed for the 5 promotion gates.
Run from: backend/
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    f1_score,
    precision_recall_fscore_support,
)

from app.core.model_loader import HuggingFaceModelLoader

# ── Promotion gate thresholds ─────────────────────────────────────────────────
GATE_HAM_FPR    = 0.02     # <= 2%
GATE_SPAM_F1    = 0.95     # >= 95%
GATE_UCI_F1     = 0.95     # >= 95%
GATE_LATENCY_MS = 60.0     # <= 60ms mean

REGRESSION_CASES = [
    # (text, expected_label "safe"|"phishing", test_id)
    ("PKR 5,030 received from ILAM UL DIN* in your UBL A/C *5034 on 04-AUG-2026 19:53 via IBFT. Tx ID 6940522193. For info: 111825888.", "safe", "ubl_ibft_receipt"),
    ("JUNAID AHMED A/C *5034 is debited with PKR 5,000 on 04/08/26 at 20:13 from ATM. For info: 111825888.", "safe", "ubl_atm_debit"),
    ("Dear UBL Customer,\nYou may log your complaints via our Contact Center, Email, Website, Mobile App, Social Media, Branches or visit: https://bit.ly/2WceaFA", "safe", "ubl_customer_service_bitly"),
    ("50% OFF Only 4 You! Make the most of Z Hour sale from 5PM-9PM & get 50% OFF on WhatsApp Plus Bundle in My Zong App. Tap now: bit.ly/3rY7XHq", "safe", "zong_50_percent_off"),
    ("Thanks for subscribing to Gaming Royale at Rs 11.95/Day (Auto Renewal). Play live Games on http://z.gamingroyale.club. To Unsub click http://z.gamingroyale.club/u", "safe", "gaming_royale_subscription"),
    ("You have unlocked ONE Day FREE Trial of Gaming Royale and will be charged Rs 11.95/Day (Auto renewal) tomorrow. To Unsub click http://z.gamingroyale.club/u", "safe", "gaming_royale_free_trial"),
    ("Your ReadCash is Overdue! Save on the next weekly fee of Rs 160 (applied in 2 days) by repaying your ReadyCash Rs 3151.18 now by dialing *786*4*2#.", "safe", "readycash_overdue"),
    ("1 DAY LEFT! Your ReadyCash loan is due tomorrow! Make sure to Dial *786*4*2# to repay your Rs 3151.18 on time and to be able to borrow again!", "safe", "readycash_1_day_left"),
    ("Jeetne ke liye tayyar ho jao! aur jeeto bade inaam, Zong Engage ke taraf se khaas http://games.zongengage.com.pk 6PKR/Day, Reply 1 ke saath on 4263", "safe", "zong_engage_prize_lang"),
    # SPAM regression
    ("Congratulations! You have won PKR 100,000. Click http://example.com to claim your prize immediately.", "phishing", "prize_phishing"),
    ("HBL Alert: Your account will be blocked in 24 hours due to pending verification. Update now: http://hbl-secure-login.xyz", "phishing", "fake_bank_verification"),
    ("Your UBL account has been suspended. Verify your account immediately by clicking http://example.com/login", "phishing", "fake_account_suspension"),
    ("Dear Customer, share your 6-digit OTP code with our support team to stop unauthorized transaction of PKR 45,000.", "phishing", "otp_phishing"),
    ("BISP ki taraf se 25,000 rupay approved hain. Abhi claim karein 0312-9876543 par call kar ke.", "phishing", "bisp_roman_urdu_scam"),
]


def load_model(path: Path, version_name: str) -> HuggingFaceModelLoader | None:
    if not path.exists():
        print(f"  [SKIP] {version_name}: model not found at {path}")
        return None
    loader = HuggingFaceModelLoader(
        model_path=str(path),
        model_version=version_name,
    )
    loader.load()
    return loader


def evaluate_on_df(loader: HuggingFaceModelLoader, df: pd.DataFrame, label_col: str = "label") -> dict:
    y_true, y_pred, y_conf = [], [], []
    for _, row in df.iterrows():
        pred = loader.predict(str(row["text"]))
        pred_int = 1 if pred.label == "phishing" else 0
        true_str = str(row[label_col])
        true_int = 1 if true_str in ("spam", "1") else 0
        y_true.append(true_int)
        y_pred.append(pred_int)
        y_conf.append(float(pred.confidence))

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_conf = np.array(y_conf)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (cm[0, 0], 0, 0, cm[0, 0])
    total  = len(y_true)
    prec   = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1     = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    fpr    = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    return {
        "samples": int(total),
        "tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
        "precision": round(prec, 4),
        "recall":    round(rec, 4),
        "f1":        round(f1, 4),
        "fpr":       round(fpr, 4),
        "conf_mean": round(float(y_conf.mean()), 4),
        "conf_min":  round(float(y_conf.min()), 4),
        "conf_max":  round(float(y_conf.max()), 4),
        "conf_p25":  round(float(np.percentile(y_conf, 25)), 4),
        "conf_p75":  round(float(np.percentile(y_conf, 75)), 4),
    }


def measure_latency(loader: HuggingFaceModelLoader, n_samples: int = 30) -> dict:
    test_msgs = [
        "PKR 5,030 received from ILAM UL DIN in your UBL A/C on 04-AUG-2026.",
        "50% OFF Only 4 You! Tap now: bit.ly/3rY7XHq",
        "Congratulations! You have won PKR 100,000. Click http://example.com",
        "Your account has been suspended. Verify at http://hbl-secure-login.xyz",
        "JazzCash: Aap ke wallet mein Rs 3,000 credit ho gaye hain.",
        "BISP ki taraf se 25,000 rupay approved hain. Claim karein.",
    ] * (n_samples // 6 + 1)
    test_msgs = test_msgs[:n_samples]

    latencies = []
    for msg in test_msgs:
        t0 = time.perf_counter()
        loader.predict(msg)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    return {
        "n":       n_samples,
        "mean_ms": round(float(np.mean(latencies)), 2),
        "p50_ms":  round(float(np.percentile(latencies, 50)), 2),
        "p95_ms":  round(float(np.percentile(latencies, 95)), 2),
        "max_ms":  round(float(np.max(latencies)), 2),
    }


def run_regression(loader: HuggingFaceModelLoader) -> dict:
    passed, failed = [], []
    for text, expected, tid in REGRESSION_CASES:
        pred = loader.predict(text)
        got  = pred.label
        if got == expected:
            passed.append(tid)
        else:
            failed.append({"id": tid, "expected": expected, "got": got, "conf": pred.confidence})
    return {
        "total":  len(REGRESSION_CASES),
        "passed": len(passed),
        "failed": len(failed),
        "pass_rate": len(passed) / len(REGRESSION_CASES),
        "failures": failed,
    }


def gate_str(passed: bool) -> str:
    return "PASS" if passed else "FAIL"


def main():
    print("=" * 80)
    print("  MINDSHIELD - PHASE 3.8 PROMOTION GATE EVALUATION")
    print("  v1 vs v2 vs v3 - Full Comparative Suite")
    print("=" * 80)

    backend = Path(__file__).resolve().parents[1]
    proc    = backend / "data/processed"

    # Load datasets
    test_df = pd.read_csv(proc / "test.csv")
    pak_df  = pd.read_csv(proc / "pakscam_localized_v2.csv")
    pak_ham  = pak_df[pak_df["label"] == "ham"].copy().reset_index(drop=True)
    pak_spam = pak_df[pak_df["label"] == "spam"].copy().reset_index(drop=True)

    print(f"\n[Datasets] UCI test={len(test_df)} | Pak HAM={len(pak_ham)} | Pak SPAM={len(pak_spam)}")

    # Subcategory evaluation sets
    pak_banking_ham  = pak_ham[pak_ham["category"].str.contains("banking")]
    pak_telecom_ham  = pak_ham[pak_ham["category"].str.contains("telecom")]
    pak_ru_ham       = pak_ham[pak_ham["language"] == "roman_urdu"]
    pak_financial_ham = pak_ham[pak_ham["category"].isin(["loan_notification", "payment_notification"])]

    models = {
        "distilbert-pakscam-v1": backend / "data/models/distilbert_pakscam_v1",
        "distilbert-pakscam-v2": backend / "data/models/distilbert_pakscam_v2",
        "distilbert-pakscam-v3": backend / "data/models/distilbert_pakscam_v3",
    }

    all_results = {}

    for model_name, model_path in models.items():
        print(f"\n{'=' * 80}")
        print(f"  Evaluating: {model_name}")
        print(f"{'=' * 80}")

        loader = load_model(model_path, model_name)
        if loader is None:
            continue

        print("  [A] UCI test set...", flush=True)
        uci_res = evaluate_on_df(loader, test_df)

        print("  [B] Pak ALL HAM...", flush=True)
        pak_ham_res = evaluate_on_df(loader, pak_ham.assign(label_tmp=0).rename(
            columns={"label": "_lbl_orig"}), label_col="_lbl_orig")

        # Hack: evaluate HAM-only df as FPR (spam predicted on ham = FP)
        ham_preds, ham_conf = [], []
        for _, row in pak_ham.iterrows():
            pred = loader.predict(str(row["text"]))
            ham_preds.append(1 if pred.label == "phishing" else 0)
            ham_conf.append(pred.confidence)
        pak_ham_fp  = sum(ham_preds)
        pak_ham_fpr = pak_ham_fp / len(pak_ham)
        pak_ham_conf = {
            "fp_count": pak_ham_fp,
            "fpr": round(pak_ham_fpr, 4),
            "conf_mean": round(float(np.mean(ham_conf)), 4),
        }

        # Per-category HAM FPR
        cat_results = {}
        for cat_label, cat_df in [
            ("banking_ham", pak_banking_ham),
            ("telecom_ham", pak_telecom_ham),
            ("roman_urdu_ham", pak_ru_ham),
            ("financial_ham", pak_financial_ham),
        ]:
            if len(cat_df) == 0:
                continue
            fp_cnt = sum(1 for _, r in cat_df.iterrows()
                         if loader.predict(str(r["text"])).label == "phishing")
            cat_results[cat_label] = {
                "n": len(cat_df),
                "fp": fp_cnt,
                "fpr": round(fp_cnt / len(cat_df), 4),
            }

        print("  [C] Pak SPAM...", flush=True)
        spam_preds, spam_conf = [], []
        for _, row in pak_spam.iterrows():
            pred = loader.predict(str(row["text"]))
            spam_preds.append(1 if pred.label == "phishing" else 0)
            spam_conf.append(pred.confidence)
        pak_spam_tp  = sum(spam_preds)
        pak_spam_fn  = len(pak_spam) - pak_spam_tp
        pak_spam_recall = pak_spam_tp / len(pak_spam)
        # Compute F1: precision = TP/(TP+FP), recall = TP/(TP+FN)
        # FP here = 0 (we already know all are spam, so any safe pred is FN)
        pak_spam_f1   = pak_spam_recall  # precision=1.0 since all test items are spam
        pak_spam_res  = {
            "n": len(pak_spam),
            "tp": pak_spam_tp,
            "fn": pak_spam_fn,
            "recall": round(pak_spam_recall, 4),
            "f1": round(pak_spam_f1, 4),
            "conf_mean": round(float(np.mean(spam_conf)), 4),
        }

        print("  [D] Regression tests...", flush=True)
        reg_res = run_regression(loader)

        print("  [E] Latency measurement...", flush=True)
        lat_res = measure_latency(loader, n_samples=30)

        # ── Gate evaluation ───────────────────────────────────────────────────
        gate_fpr    = pak_ham_fpr <= GATE_HAM_FPR
        gate_spam   = pak_spam_res["f1"] >= GATE_SPAM_F1
        gate_uci    = uci_res["f1"] >= GATE_UCI_F1
        gate_reg    = reg_res["failed"] == 0
        gate_lat    = lat_res["mean_ms"] <= GATE_LATENCY_MS
        all_gates   = all([gate_fpr, gate_spam, gate_uci, gate_reg, gate_lat])

        all_results[model_name] = {
            "uci": uci_res,
            "pak_ham_summary": pak_ham_conf,
            "pak_ham_categories": cat_results,
            "pak_spam": pak_spam_res,
            "regression": reg_res,
            "latency": lat_res,
            "gates": {
                "fpr_gate":    {"value": pak_ham_fpr, "threshold": GATE_HAM_FPR, "pass": gate_fpr},
                "spam_f1_gate": {"value": pak_spam_res["f1"], "threshold": GATE_SPAM_F1, "pass": gate_spam},
                "uci_f1_gate": {"value": uci_res["f1"], "threshold": GATE_UCI_F1, "pass": gate_uci},
                "reg_gate":    {"passed": reg_res["passed"], "total": reg_res["total"], "pass": gate_reg},
                "lat_gate":    {"value": lat_res["mean_ms"], "threshold": GATE_LATENCY_MS, "pass": gate_lat},
            },
            "promote": all_gates,
        }

        print(f"\n  == GATE RESULTS for {model_name} ==")
        print(f"  Gate 1  Pak HAM FPR:     {pak_ham_fpr:.1%} (threshold: <= {GATE_HAM_FPR:.0%})  [{gate_str(gate_fpr)}]")
        print(f"  Gate 2  Pak SPAM F1:     {pak_spam_res['f1']:.4f} (threshold: >= {GATE_SPAM_F1})  [{gate_str(gate_spam)}]")
        print(f"  Gate 3  UCI test F1:     {uci_res['f1']:.4f} (threshold: >= {GATE_UCI_F1})  [{gate_str(gate_uci)}]")
        print(f"  Gate 4  Regression:      {reg_res['passed']}/{reg_res['total']} pass  [{gate_str(gate_reg)}]")
        print(f"  Gate 5  Latency mean:    {lat_res['mean_ms']:.1f}ms (threshold: <= {GATE_LATENCY_MS}ms)  [{gate_str(gate_lat)}]")
        print(f"  --> OVERALL: {'PROMOTE' if all_gates else 'DO NOT PROMOTE'}")

        if reg_res["failures"]:
            print(f"\n  Regression failures ({len(reg_res['failures'])}):")
            for fail in reg_res["failures"]:
                print(f"    [{fail['id']}] expected={fail['expected']} got={fail['got']} conf={fail['conf']:.4f}")

    # ── Comparative summary table ─────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("  COMPARATIVE SUMMARY TABLE")
    print("=" * 80)
    header = (f"  {'Metric':<30} | {'v1':^18} | {'v2':^18} | {'v3':^18}")
    print(header)
    print("-" * 80)

    def val(model_key, *path):
        r = all_results.get(model_key, {})
        for k in path:
            r = r.get(k, {}) if isinstance(r, dict) else {}
        return r if not isinstance(r, dict) else "N/A"

    rows = [
        ("UCI test F1", "uci", "f1"),
        ("UCI Precision", "uci", "precision"),
        ("UCI Recall", "uci", "recall"),
        ("UCI TN/FP/FN/TP", None, None),
        ("Pak HAM FPR", "pak_ham_summary", "fpr"),
        ("Pak HAM FP count / 87", "pak_ham_summary", "fp_count"),
        ("Pak SPAM Recall/F1", "pak_spam", "f1"),
        ("Pak SPAM TP / 53", "pak_spam", "tp"),
        ("Regression pass rate", None, None),
        ("Latency mean (ms)", "latency", "mean_ms"),
        ("Latency p95 (ms)", "latency", "p95_ms"),
    ]

    for label, k1, k2 in rows:
        v_list = []
        for mn in ["distilbert-pakscam-v1", "distilbert-pakscam-v2", "distilbert-pakscam-v3"]:
            r = all_results.get(mn)
            if r is None:
                v_list.append("N/A")
            elif label == "UCI TN/FP/FN/TP":
                u = r.get("uci", {})
                v_list.append(f"{u.get('tn','?')}/{u.get('fp','?')}/{u.get('fn','?')}/{u.get('tp','?')}")
            elif label == "Regression pass rate":
                rr = r.get("regression", {})
                v_list.append(f"{rr.get('passed','?')}/{rr.get('total','?')}")
            else:
                v_list.append(str(r.get(k1, {}).get(k2, "N/A") if k1 else "N/A"))
        print(f"  {label:<30} | {v_list[0]:^18} | {v_list[1]:^18} | {v_list[2]:^18}")

    print("=" * 80)
    print("\n  PROMOTION GATE SUMMARY")
    print("-" * 80)
    print(f"  {'Model':<30} | {'FPR Gate':^10} | {'SPAM Gate':^10} | {'UCI Gate':^10} | {'Reg Gate':^10} | {'Lat Gate':^10} | {'VERDICT':^12}")
    print("-" * 80)
    for mn in ["distilbert-pakscam-v1", "distilbert-pakscam-v2", "distilbert-pakscam-v3"]:
        r = all_results.get(mn)
        if not r:
            continue
        g = r["gates"]
        verdict = "PROMOTE" if r["promote"] else "DO NOT PROMOTE"
        print(
            f"  {mn:<30} | {gate_str(g['fpr_gate']['pass']):^10} | "
            f"{gate_str(g['spam_f1_gate']['pass']):^10} | "
            f"{gate_str(g['uci_f1_gate']['pass']):^10} | "
            f"{gate_str(g['reg_gate']['pass']):^10} | "
            f"{gate_str(g['lat_gate']['pass']):^10} | "
            f"{verdict:^12}"
        )
    print("=" * 80)

    # Save results
    out = backend / "data/metadata/v3_evaluation_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n[Saved] Full results: {out}")


if __name__ == "__main__":
    main()
