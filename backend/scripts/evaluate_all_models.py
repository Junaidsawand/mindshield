# ==============================================================================
# MindShield Backend — Master Multi-Model Comparative Evaluation Engine
# Phase 3.5: Side-by-Side Comparison of distilbert-uci-v1, uci-v2, and pakscam-v1
# ==============================================================================

import json
from pathlib import Path
import pandas as pd
from app.core.model_loader import HuggingFaceModelLoader


def evaluate_loader_on_df(loader: HuggingFaceModelLoader, df: pd.DataFrame) -> dict:
    """Evaluate a loaded model on a pandas DataFrame test subset."""
    correct = tp = fp = tn = fn = 0
    for _, row in df.iterrows():
        pred = loader.predict(row["text"])
        pred_label = 1 if pred.label == "phishing" else 0
        true_label = int(row["label"])
        if pred_label == true_label:
            correct += 1
        if pred_label == 1 and true_label == 1:
            tp += 1
        elif pred_label == 1 and true_label == 0:
            fp += 1
        elif pred_label == 0 and true_label == 0:
            tn += 1
        elif pred_label == 0 and true_label == 1:
            fn += 1

    total = len(df)
    acc = correct / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

    return {
        "samples": total,
        "acc": round(acc, 4),
        "prec": round(prec, 4),
        "rec": round(rec, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def main():
    """Run master side-by-side evaluation across all model checkpoints."""
    print("=" * 100)
    print("  MINDSHIELD AI CYBERSECURITY — MASTER COMPARATIVE EVALUATION  ")
    print("=" * 100)

    backend_dir = Path(__file__).resolve().parents[1]
    processed_dir = backend_dir / "data/processed"
    test_df = pd.read_csv(processed_dir / "test.csv")
    pakscam_df = pd.read_csv(processed_dir / "pakscam_dataset.csv")

    models = {
        "distilbert-uci-v1": backend_dir / "data/models/distilbert_uci_v1",
        "distilbert-uci-v2": backend_dir / "data/models/distilbert_uci_v2",
        "distilbert-pakscam-v1": backend_dir / "data/models/distilbert_pakscam_v1",
    }

    subsets = {
        "UCI In-Domain Test": test_df,
        "PakScam All Synthetic": pakscam_df,
    }

    for cat in pakscam_df["subset_category"].unique():
        subsets[f"PakScam — {cat}"] = pakscam_df[
            pakscam_df["subset_category"] == cat
        ]

    results = {}

    for model_name, path in models.items():
        if not path.exists():
            print(f"[Warning] Model path missing: {path}")
            continue
        print(f"\nEvaluating Model: {model_name}...")
        loader = HuggingFaceModelLoader(model_path=str(path))
        loader.load()

        model_res = {}
        for s_name, s_df in subsets.items():
            model_res[s_name] = evaluate_loader_on_df(loader, s_df)
        results[model_name] = model_res

    # Print Side-by-Side Comparison Table
    header = (
        f"{'EVALUATION SUBSET':<32} | {'distilbert-uci-v1':<25} | "
        f"{'distilbert-uci-v2':<25} | {'distilbert-pakscam-v1':<25}"
    )
    print("\n" + "=" * 120)
    print(header)
    print("=" * 120)

    for s_name in subsets.keys():
        r1 = results.get("distilbert-uci-v1", {}).get(s_name, {})
        r2 = results.get("distilbert-uci-v2", {}).get(s_name, {})
        r3 = results.get("distilbert-pakscam-v1", {}).get(s_name, {})

        str1 = (
            f"F1:{r1.get('f1', 0):.4f} (FP:{r1.get('fp', 0)}/FN:{r1.get('fn', 0)})"
            if r1 else "N/A"
        )
        str2 = (
            f"F1:{r2.get('f1', 0):.4f} (FP:{r2.get('fp', 0)}/FN:{r2.get('fn', 0)})"
            if r2 else "N/A"
        )
        str3 = (
            f"F1:{r3.get('f1', 0):.4f} (FP:{r3.get('fp', 0)}/FN:{r3.get('fn', 0)})"
            if r3 else "N/A"
        )

        print(f"{s_name:<32} | {str1:<25} | {str2:<25} | {str3:<25}")

    print("=" * 120)

    # Diagnostic Benchmark Test Messages
    print("\n" + "=" * 100)
    print("  DIAGNOSTIC REGRESSION BENCHMARK MESSAGES ACROSS ALL MODELS  ")
    print("=" * 100)
    diag_msgs = [
        (
            "TEST 1: Legitimate UBL Receipt",
            "PKR 1,000 received from AZHAR ALI* in your UBL A/C *5034 on "
            "08-AUG-2026 14:45 via IBFT. Tx ID 6959318669. For info: 111825888."
        ),
        (
            "TEST 2: Obvious Prize Scam",
            "Congratulations! You have won PKR 100,000. Click "
            "http://example.com to claim your prize immediately."
        ),
        (
            "TEST 3: Fake Bank Phishing",
            "Your UBL account has been suspended. Verify your account "
            "immediately by clicking http://example.com/login"
        )
    ]

    for title, text in diag_msgs:
        print(f"\n[{title}]")
        for model_name, path in models.items():
            if not path.exists():
                continue
            loader = HuggingFaceModelLoader(model_path=str(path))
            loader.load()
            pred = loader.predict(text)
            print(
                f"  {model_name:<22} -> label={pred.label:<8} "
                f"threat={pred.threat_level:<10} conf={pred.confidence:.4f} "
                f"logits={pred.logits}"
            )

    out_file = backend_dir / "data/metadata/master_model_comparison.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 100)
    print(f"[OK] Master comparative evaluation saved to {out_file}")


if __name__ == "__main__":
    main()
