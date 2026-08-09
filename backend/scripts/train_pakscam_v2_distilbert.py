# ==============================================================================
# MindShield Backend — DistilBERT PakScam v2 Fine-Tuning Script
# Phase 3.6: Pakistani Domain Generalization Training
# ==============================================================================
"""Train distilbert-pakscam-v2 on UCI + Pakistani localized data.

Key changes from v1:
- max_length=128 (matching inference, fixing v1 mismatch of 64)
- 3 epochs with early stopping (patience=2)
- ~140 Pakistani samples (vs 58 in v1)
- Template-family-aware train/test splitting
"""

import json
import shutil
from pathlib import Path

import pandas as pd

from app.distilbert.config import DistilBERTConfig
from app.distilbert.trainer import DistilBERTTrainer
from app.core.model_loader import HuggingFaceModelLoader


def split_pakscam_by_family(
    pak_df: pd.DataFrame,
    train_ratio: float = 0.80,
    seed: int = 42,
) -> tuple:
    """Split PakScam data by template family to prevent leakage.

    All samples from the same template_family go to the same split.
    Returns (train_df, test_df).
    """
    families = pak_df["template_family"].unique().tolist()

    # Deterministic shuffle of families
    import random
    rng = random.Random(seed)
    rng.shuffle(families)

    # Assign families to train/test
    n_train = max(1, int(len(families) * train_ratio))
    train_families = set(families[:n_train])
    test_families = set(families[n_train:])

    train_mask = pak_df["template_family"].isin(train_families)
    test_mask = pak_df["template_family"].isin(test_families)

    return pak_df[train_mask].copy(), pak_df[test_mask].copy()


def evaluate_model_on_df(
    loader: HuggingFaceModelLoader,
    df: pd.DataFrame,
    label_col: str = "label",
) -> dict:
    """Evaluate a model on a DataFrame with ham/spam labels."""
    tp = fp = tn = fn = 0
    for _, row in df.iterrows():
        pred = loader.predict(str(row["text"]))
        pred_spam = pred.label == "phishing"
        true_spam = str(row[label_col]) in ("spam", "1")

        if pred_spam and true_spam:
            tp += 1
        elif pred_spam and not true_spam:
            fp += 1
        elif not pred_spam and not true_spam:
            tn += 1
        elif not pred_spam and true_spam:
            fn += 1

    total = tp + fp + tn + fn
    acc = (tp + tn) / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * prec * rec / (prec + rec) if (prec + rec) > 0
        else 0.0
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


def main():
    """Train distilbert-pakscam-v2 and evaluate."""
    print("=" * 70)
    print("  MINDSHIELD — DISTILBERT-PAKSCAM-V2 FINE-TUNING")
    print("=" * 70)

    backend = Path(__file__).resolve().parents[1]
    processed = backend / "data/processed"

    # Load UCI splits
    train_df = pd.read_csv(processed / "train.csv")
    val_df = pd.read_csv(processed / "val.csv")
    test_df = pd.read_csv(processed / "test.csv")

    # Load PakScam v2
    pak_path = processed / "pakscam_localized_v2.csv"
    if not pak_path.exists():
        from app.data.pakscam_v2_generator import (
            PakScamV2DatasetGenerator,
        )
        PakScamV2DatasetGenerator(
            output_dir=str(processed)
        ).generate_dataset()
    pak_df = pd.read_csv(pak_path)

    # Map labels: ham=0, spam=1 for training
    label_map = {"ham": 0, "spam": 1}
    pak_df["label_int"] = pak_df["label"].map(label_map)

    print(f"[Data] UCI Train: {len(train_df)}")
    print(f"[Data] UCI Val:   {len(val_df)}")
    print(f"[Data] UCI Test:  {len(test_df)}")
    print(f"[Data] PakScam v2: {len(pak_df)} "
          f"(HAM={len(pak_df[pak_df['label'] == 'ham'])}, "
          f"SPAM={len(pak_df[pak_df['label'] == 'spam'])})")

    # Split PakScam by template family
    pak_train, pak_test = split_pakscam_by_family(
        pak_df, train_ratio=0.80, seed=42,
    )
    print(
        f"[Split] PakScam Train: {len(pak_train)} "
        f"(families: "
        f"{pak_train['template_family'].nunique()})"
    )
    print(
        f"[Split] PakScam Test:  {len(pak_test)} "
        f"(families: "
        f"{pak_test['template_family'].nunique()})"
    )

    # Verify no family leakage
    train_fams = set(pak_train["template_family"].unique())
    test_fams = set(pak_test["template_family"].unique())
    overlap = train_fams & test_fams
    if overlap:
        raise ValueError(
            f"Template family leakage detected: {overlap}"
        )
    print("[Leakage Check] PASSED — zero family overlap.")

    # Combine UCI + PakScam for training
    pak_train_slim = pak_train[["text", "label_int"]].rename(
        columns={"label_int": "label"}
    )
    combined_train = pd.concat(
        [train_df, pak_train_slim], ignore_index=True
    )
    # Use PakScam test portion as additional validation
    pak_val_slim = pak_test[["text", "label_int"]].rename(
        columns={"label_int": "label"}
    )
    combined_val = pd.concat(
        [val_df, pak_val_slim], ignore_index=True
    )

    print(
        f"[Combined] Train: {len(combined_train)} | "
        f"Val: {len(combined_val)}"
    )

    # Configure trainer with max_length=128 (fixing v1 mismatch)
    config = DistilBERTConfig(
        models_output_dir=Path("data/models/distilbert"),
        epochs=3,
        learning_rate=2e-5,
        batch_size=32,
        max_length=128,
        patience=2,
    )

    print(f"\n[Config] epochs={config.epochs}, "
          f"max_length={config.max_length}, "
          f"lr={config.learning_rate}, "
          f"batch_size={config.batch_size}, "
          f"patience={config.patience}")

    trainer = DistilBERTTrainer(config)
    metrics, history = trainer.train_and_evaluate(
        combined_train, combined_val, test_df,
    )

    # Archive to distilbert_pakscam_v2
    v2_dir = backend / "data/models/distilbert_pakscam_v2"
    v2_dir.mkdir(parents=True, exist_ok=True)
    src_dir = backend / "data/models/distilbert"
    for item in src_dir.glob("*"):
        if item.is_file():
            shutil.copy(item, v2_dir / item.name)

    # Save training config
    config_record = {
        "model_version": "distilbert-pakscam-v2",
        "base_model": "distilbert-base-uncased",
        "epochs": config.epochs,
        "max_length": config.max_length,
        "learning_rate": config.learning_rate,
        "batch_size": config.batch_size,
        "seed": config.seed,
        "patience": config.patience,
        "uci_train_samples": len(train_df),
        "pakscam_train_samples": len(pak_train),
        "combined_train_samples": len(combined_train),
        "combined_val_samples": len(combined_val),
        "uci_test_samples": len(test_df),
        "pakscam_test_samples": len(pak_test),
        "dataset_version": "pakscam_localized_v2",
        "preprocessing": "create_transformer_config()",
    }
    with open(
        v2_dir / "training_config.json", "w", encoding="utf-8"
    ) as f:
        json.dump(config_record, f, indent=2)

    print(f"\n[Archive] Model saved to {v2_dir}")
    print("[Archive] Training config saved.")

    # Quick diagnostic on the 3 original benchmark messages
    print("\n" + "=" * 70)
    print("  DIAGNOSTIC BENCHMARK MESSAGES (pakscam-v2)")
    print("=" * 70)
    loader = HuggingFaceModelLoader(
        model_path=str(v2_dir),
    )
    loader.load()

    diagnostics = [
        (
            "UBL IBFT Receipt (user-observed #1)",
            "PKR 5,030 received from ILAM UL DIN* in your "
            "UBL A/C *5034 on 04-AUG-2026 19:53 via IBFT. "
            "Tx ID 6940522193. For info: 111825888.",
        ),
        (
            "Zong 50% OFF (user-observed #7)",
            "50% OFF Only 4 You! Make the most of Z Hour sale "
            "from 5PM-9PM & get 50% OFF on WhatsApp Plus "
            "Bundle in My Zong App. Tap now: bit.ly/3rY7XHq",
        ),
        (
            "ReadyCash Overdue (user-observed #11)",
            "Your ReadCash is Overdue! Save on the next "
            "weekly fee of Rs 160 (applied in 2 days) by "
            "repaying your ReadyCash Rs 3151.18 now by "
            "dialing *786*4*2#.",
        ),
        (
            "Obvious Prize Phishing",
            "Congratulations! You have won PKR 100,000. Click "
            "http://example.com to claim your prize.",
        ),
        (
            "Fake Bank Verification",
            "Your UBL account has been suspended. Verify your "
            "account immediately by clicking "
            "http://example.com/login",
        ),
    ]

    for title, text in diagnostics:
        pred = loader.predict(text)
        print(
            f"  [{title}]\n"
            f"    label={pred.label:<10} "
            f"threat={pred.threat_level:<10} "
            f"conf={pred.confidence:.4f}"
        )

    print("\n" + "=" * 70)
    print("  TRAINING COMPLETE — distilbert-pakscam-v2")
    print("=" * 70)


if __name__ == "__main__":
    main()
