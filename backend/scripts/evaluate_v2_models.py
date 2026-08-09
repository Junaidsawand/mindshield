# ==============================================================================
# MindShield Backend — Multi-Model Comparative Evaluation v2
# Phase 3.6: 4-Model Side-by-Side Evaluation with FPR Tracking
# ==============================================================================
"""Evaluate distilbert-uci-v1, uci-v2, pakscam-v1, pakscam-v2.

Reports accuracy, precision, recall, F1, FP, FN, FPR across
8 evaluation subsets (A-H) per the master prompt.
"""

import json
from pathlib import Path

import pandas as pd
from app.core.model_loader import HuggingFaceModelLoader


def evaluate_on_df(
    loader: HuggingFaceModelLoader,
    df: pd.DataFrame,
    label_col: str = "label",
) -> dict:
    """Evaluate a loaded model on a DataFrame."""
    tp = fp = tn = fn = 0
    for _, row in df.iterrows():
        pred = loader.predict(str(row["text"]))
        pred_spam = pred.label == "phishing"

        raw_label = str(row[label_col])
        true_spam = raw_label in ("spam", "1")

        if pred_spam and true_spam:
            tp += 1
        elif pred_spam and not true_spam:
            fp += 1
        elif not pred_spam and not true_spam:
            tn += 1
        else:
            fn += 1

    total = tp + fp + tn + fn
    acc = (tp + tn) / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * prec * rec / (prec + rec)
        if (prec + rec) > 0 else 0.0
    )
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        "samples": total,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "fpr": round(fpr, 4),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


def print_comparison_table(
    results: dict,
    subset_names: list,
    model_names: list,
):
    """Print formatted comparison table."""
    col_w = 28
    name_w = 34

    header = f"{'SUBSET':<{name_w}}"
    for m in model_names:
        header += f" | {m:<{col_w}}"
    print(header)
    print("=" * len(header))

    for s_name in subset_names:
        row = f"{s_name:<{name_w}}"
        for m_name in model_names:
            r = results.get(m_name, {}).get(s_name, {})
            if r:
                cell = (
                    f"F1:{r['f1']:.3f} FPR:{r['fpr']:.3f} "
                    f"FP:{r['fp']}/FN:{r['fn']}"
                )
            else:
                cell = "N/A"
            row += f" | {cell:<{col_w}}"
        print(row)


def main():
    """Run 4-model comparative evaluation."""
    print("=" * 80)
    print("  MINDSHIELD — 4-MODEL COMPARATIVE EVALUATION (v2)")
    print("=" * 80)

    backend = Path(__file__).resolve().parents[1]
    processed = backend / "data/processed"

    # Load evaluation data
    uci_test = pd.read_csv(processed / "test.csv")
    pak_df = pd.read_csv(
        processed / "pakscam_localized_v2.csv"
    )

    # Build evaluation subsets (A-H)
    subsets = {}

    # A. UCI In-Domain Test
    subsets["A. UCI In-Domain Test"] = uci_test

    # B. Pakistani Banking HAM
    banking_cats = {
        "banking_transaction",
        "banking_notification",
        "banking_customer_service",
    }
    b_mask = (
        (pak_df["category"].isin(banking_cats))
        & (pak_df["label"] == "ham")
    )
    subsets["B. Pak Banking HAM"] = pak_df[b_mask]

    # C. Pakistani Telecom/Promo HAM
    telecom_cats = {
        "telecom_promotion",
        "telecom_subscription",
        "telecom_unsubscription",
        "telecom_service_notification",
    }
    c_mask = (
        (pak_df["category"].isin(telecom_cats))
        & (pak_df["label"] == "ham")
    )
    subsets["C. Pak Telecom HAM"] = pak_df[c_mask]

    # D. Pakistani Financial/Loan HAM
    fin_cats = {
        "loan_notification",
        "payment_notification",
        "otp_security",
    }
    d_mask = (
        (pak_df["category"].isin(fin_cats))
        & (pak_df["label"] == "ham")
    )
    subsets["D. Pak Financial HAM"] = pak_df[d_mask]

    # E. Pakistani Hard-Negative HAM (all HAM samples)
    e_mask = pak_df["label"] == "ham"
    subsets["E. Pak ALL HAM (FPR)"] = pak_df[e_mask]

    # F. Pakistani SPAM
    f_mask = pak_df["label"] == "spam"
    subsets["F. Pak ALL SPAM"] = pak_df[f_mask]

    # G. Roman Urdu HAM
    g_mask = (
        (pak_df["language"] == "roman_urdu")
        & (pak_df["label"] == "ham")
    )
    subsets["G. Roman Urdu HAM"] = pak_df[g_mask]

    # H. Roman Urdu SPAM
    h_mask = (
        (pak_df["language"] == "roman_urdu")
        & (pak_df["label"] == "spam")
    )
    subsets["H. Roman Urdu SPAM"] = pak_df[h_mask]

    # Print subset sizes
    print("\nEvaluation Subsets:")
    for name, df in subsets.items():
        print(f"  {name}: {len(df)} samples")

    # Load models
    model_configs = {
        "uci-v1": backend / "data/models/distilbert_uci_v1",
        "uci-v2": backend / "data/models/distilbert_uci_v2",
        "pak-v1": (
            backend / "data/models/distilbert_pakscam_v1"
        ),
        "pak-v2": (
            backend / "data/models/distilbert_pakscam_v2"
        ),
    }

    results = {}
    for m_name, m_path in model_configs.items():
        if not m_path.exists():
            print(f"\n[SKIP] {m_name}: path not found {m_path}")
            continue
        print(f"\n[Evaluating] {m_name} from {m_path}...")
        loader = HuggingFaceModelLoader(
            model_path=str(m_path)
        )
        loader.load()

        model_results = {}
        for s_name, s_df in subsets.items():
            if len(s_df) == 0:
                continue
            r = evaluate_on_df(loader, s_df)
            model_results[s_name] = r
            print(
                f"  {s_name}: F1={r['f1']:.4f} "
                f"FPR={r['fpr']:.4f} "
                f"FP={r['fp']} FN={r['fn']}"
            )
        results[m_name] = model_results

    # Print comparison table
    print("\n" + "=" * 80)
    print("  SIDE-BY-SIDE COMPARISON TABLE")
    print("=" * 80)
    print_comparison_table(
        results,
        list(subsets.keys()),
        list(model_configs.keys()),
    )

    # Diagnostic messages
    print("\n" + "=" * 80)
    print("  DIAGNOSTIC REGRESSION BENCHMARKS")
    print("=" * 80)

    diag_msgs = [
        ("UBL IBFT (user #1)",
         "PKR 5,030 received from ILAM UL DIN* in your UBL "
         "A/C *5034 on 04-AUG-2026 19:53 via IBFT. Tx ID "
         "6940522193. For info: 111825888.",
         "HAM"),
        ("UBL ATM (user #2)",
         "JUNAID AHMED A/C *5034 is debited with PKR 5,000 "
         "on 04/08/26 at 20:13 from ATM. For info: 111825888.",
         "HAM"),
        ("Zong 50% OFF (user #7)",
         "50% OFF Only 4 You! Make the most of Z Hour sale "
         "from 5PM-9PM & get 50% OFF on WhatsApp Plus Bundle "
         "in My Zong App. Tap now: bit.ly/3rY7XHq",
         "HAM"),
        ("ReadyCash Overdue (user #11)",
         "Your ReadCash is Overdue! Save on the next weekly "
         "fee of Rs 160 (applied in 2 days) by repaying your "
         "ReadyCash Rs 3151.18 now by dialing *786*4*2#.",
         "HAM"),
        ("Prize Phishing",
         "Congratulations! You have won PKR 100,000. Click "
         "http://example.com to claim your prize immediately.",
         "SPAM"),
        ("Fake Bank Suspension",
         "Your UBL account has been suspended. Verify your "
         "account immediately by clicking "
         "http://example.com/login",
         "SPAM"),
    ]

    for m_name, m_path in model_configs.items():
        if not m_path.exists():
            continue
        print(f"\n  Model: {m_name}")
        loader = HuggingFaceModelLoader(
            model_path=str(m_path)
        )
        loader.load()
        for title, text, expected in diag_msgs:
            pred = loader.predict(text)
            status = (
                "PASS" if (
                    (expected == "HAM" and
                     pred.label == "safe")
                    or (expected == "SPAM" and
                        pred.label == "phishing")
                ) else "FAIL"
            )
            print(
                f"    [{status}] {title}: "
                f"label={pred.label} "
                f"conf={pred.confidence:.4f} "
                f"(expected {expected})"
            )

    # Save results
    out_path = (
        backend / "data/metadata"
        / "pakscam_v2_model_comparison.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[Saved] {out_path}")


if __name__ == "__main__":
    main()
