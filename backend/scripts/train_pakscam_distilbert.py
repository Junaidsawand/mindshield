# ==============================================================================
# MindShield Backend — DistilBERT Multi-Domain Fine-Tuning & Evaluation Script
# Phase 3.4 / 3.5: Training distilbert-pakscam-v1 on Combined UCI + PakScam Data
# ==============================================================================

import json
from pathlib import Path
import shutil
import pandas as pd

from app.distilbert.config import DistilBERTConfig
from app.distilbert.trainer import DistilBERTTrainer
from app.core.model_loader import HuggingFaceModelLoader


def main():
    """Run multi-domain fine-tuning and evaluation for distilbert-pakscam-v1."""
    print("=" * 80)
    print("  MINDSHIELD AI CYBERSECURITY — PAKSCAM DISTILBERT FINE-TUNING  ")
    print("=" * 80)

    backend_dir = Path(__file__).resolve().parents[1]
    processed_dir = backend_dir / "data/processed"

    train_csv = processed_dir / "train.csv"
    val_csv = processed_dir / "val.csv"
    test_csv = processed_dir / "test.csv"
    pakscam_csv = processed_dir / "pakscam_dataset.csv"

    if not pakscam_csv.exists():
        from app.data.pakscam_generator import PakScamDatasetGenerator
        PakScamDatasetGenerator(output_dir=str(processed_dir)).generate_dataset()

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)
    test_df = pd.read_csv(test_csv)
    pakscam_df = pd.read_csv(pakscam_csv)

    print(
        f"[Ingestion] UCI Train: {len(train_df)} | UCI Val: {len(val_df)} | "
        f"UCI Test: {len(test_df)}"
    )
    print(f"[Ingestion] PakScam Synthetic Dataset: {len(pakscam_df)} records")

    # Split PakScam 80/20 for training augmentation
    shuffled_pakscam = pakscam_df.sample(
        frac=1.0, random_state=42
    ).reset_index(drop=True)
    pak_train_cut = int(0.8 * len(shuffled_pakscam))
    pak_train = shuffled_pakscam.iloc[:pak_train_cut]
    pak_val = shuffled_pakscam.iloc[pak_train_cut:]

    combined_train_df = pd.concat(
        [train_df, pak_train[["text", "label"]]], ignore_index=True
    )
    combined_val_df = pd.concat(
        [val_df, pak_val[["text", "label"]]], ignore_index=True
    )

    print(
        f"[Combined Data] Total Train: {len(combined_train_df)} | "
        f"Total Val: {len(combined_val_df)}"
    )

    # Initialize Trainer with shared Transformer Config
    config = DistilBERTConfig(
        models_output_dir=Path("data/models/distilbert"),
        epochs=1,
        learning_rate=2e-5,
        batch_size=32,
    )
    trainer = DistilBERTTrainer(config)

    metrics, history = trainer.train_and_evaluate(
        combined_train_df, combined_val_df, test_df
    )

    # Save to distilbert_pakscam_v1 backup
    backup_dir = backend_dir / "data/models/distilbert_pakscam_v1"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for item in (backend_dir / "data/models/distilbert").glob("*"):
        if item.is_file():
            shutil.copy(item, backup_dir / item.name)

    print(f"[Archive] Saved model artifacts to {backup_dir}")

    # Comprehensive Multi-Subset Evaluation
    print("\n" + "=" * 80)
    print("  EVALUATING DISTILBERT-PAKSCAM-V1 ACROSS SUBSETS  ")
    print("=" * 80)

    loader = HuggingFaceModelLoader(
        model_path="data/models/distilbert_pakscam_v1"
    )
    loader.load()

    def evaluate_subset(name: str, df: pd.DataFrame) -> dict:
        correct = 0
        tp = fp = tn = fn = 0
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

        res = {
            "subset": name,
            "total_samples": total,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn
        }
        print(
            f"[{name}] Acc: {acc:.4f} | Prec: {prec:.4f} | Rec: {rec:.4f} | "
            f"F1: {f1:.4f} | FP: {fp} | FN: {fn}"
        )
        return res

    subset_results = {}
    subset_results["UCI_In_Domain_Test"] = evaluate_subset(
        "UCI In-Domain Test", test_df
    )
    subset_results["PakScam_All_Synthetic"] = evaluate_subset(
        "PakScam All Synthetic", pakscam_df
    )

    for category in pakscam_df["subset_category"].unique():
        cat_df = pakscam_df[pakscam_df["subset_category"] == category]
        subset_results[category] = evaluate_subset(
            f"PakScam — {category}", cat_df
        )

    eval_out_path = (
        backend_dir / "data/metadata/pakscam_v1_evaluation_subsets.json"
    )
    with open(eval_out_path, "w", encoding="utf-8") as f:
        json.dump(subset_results, f, indent=2)

    # Diagnostic Benchmark Test Messages
    print("\n" + "=" * 80)
    print("  DIAGNOSTIC REGRESSION BENCHMARK MESSAGES (pakscam-v1)  ")
    print("=" * 80)
    diag_msgs = [
        (
            "Legitimate UBL Transaction",
            "PKR 1,000 received from AZHAR ALI* in your UBL A/C *5034 on "
            "08-AUG-2026 14:45 via IBFT. Tx ID 6959318669. For info: 111825888."
        ),
        (
            "Obvious Prize Scam",
            "Congratulations! You have won PKR 100,000. Click "
            "http://example.com to claim your prize immediately."
        ),
        (
            "Fake Bank Phishing",
            "Your UBL account has been suspended. Verify your account "
            "immediately by clicking http://example.com/login"
        )
    ]

    for label_title, text in diag_msgs:
        pred = loader.predict(text)
        print(
            f"[{label_title}] -> label: {pred.label} | threat: "
            f"{pred.threat_level} | conf: {pred.confidence:.4f} | "
            f"logits: {pred.logits}"
        )

    print("=" * 80)
    print("[OK] PakScam DistilBERT Fine-Tuning Complete.")


if __name__ == "__main__":
    main()
