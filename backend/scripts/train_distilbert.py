# ==============================================================================
# MindShield Backend — DistilBERT CLI Training Runner
# Phase 3.4: CLI Execution for DistilBERT Fine-Tuning & Model Comparison
# ==============================================================================

from app.distilbert.pipeline import DistilBERTPipeline


def main():
    """Run Phase 3.4 DistilBERT Fine-Tuning Pipeline."""
    print("=" * 80)
    print("  MINDSHIELD AI CYBERSECURITY — PHASE 3.4 DISTILBERT FINE-TUNING  ")
    print("=" * 80)

    pipeline = DistilBERTPipeline()
    results = pipeline.run_pipeline()

    distil_metrics = results["distilbert_metrics"]["metrics"]
    comp = results["comparison"]

    print("\n" + "=" * 80)
    print("  DISTILBERT FINE-TUNING EVALUATION SUMMARY  ")
    print("=" * 80)
    print(f"  Test Accuracy  : {distil_metrics['accuracy']:.4f}")
    print(f"  Test Precision : {distil_metrics['precision']:.4f}")
    print(f"  Test Recall    : {distil_metrics['recall']:.4f}")
    print(f"  Test F1-Score  : {distil_metrics['f1_score']:.4f}")
    print(f"  Test ROC-AUC   : {distil_metrics['roc_auc']:.4f}")
    print(f"  Test PR-AUC    : {distil_metrics['pr_auc']:.4f}")
    print(f"  MCC Score      : {distil_metrics['mcc']:.4f}")
    print(f"  Cohen's Kappa  : {distil_metrics['cohen_kappa']:.4f}")

    print("\n" + "=" * 80)
    print("  CLASSICAL VS TRANSFORMER COMPARATIVE BENCHMARK  ")
    print("=" * 80)
    c_name = comp["classical_model"]["name"]
    c_f1 = comp["classical_model"]["metrics"].get("f1_score", 0.0)
    d_f1 = comp["distilbert_model"]["metrics"]["f1_score"]
    gain = comp["delta"]["f1_score_gain"]

    print(f"  Best Classical Model ({c_name}) F1 : {c_f1:.4f}")
    print(f"  DistilBERT Fine-Tuned Model F1         : {d_f1:.4f}")
    print(f"  F1 Score Gain                          : {gain:+.4f}")
    print(f"  [WINNER] WINNING MODEL ARCHITECTURE     : {comp['winner']}")
    print("=" * 80)
    print(
        "[OK] Phase 3.4 DistilBERT Fine-Tuning Pipeline finished successfully."
    )


if __name__ == "__main__":
    main()
