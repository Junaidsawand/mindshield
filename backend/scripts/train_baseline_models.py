# ==============================================================================
# MindShield Backend — Baseline Models CLI Training Runner
# Phase 3.3: CLI Execution for 5-Fold CV, Model Fitting & Comparison Export
# ==============================================================================

from app.baselines.pipeline import BaselineMLPipeline


def main():
    """Run Phase 3.3 Classical Machine Learning Baseline Pipeline."""
    print("=" * 80)
    print("  MINDSHIELD AI CYBERSECURITY — PHASE 3.3 CLASSICAL ML BASELINES  ")
    print("=" * 80)

    pipeline = BaselineMLPipeline()
    metadata = pipeline.run_pipeline()

    best = metadata["best_classical_model"]
    print("\n" + "=" * 80)
    print("  CLASSICAL ML BASELINE PERFORMANCE COMPARISON AUDIT SUMMARY  ")
    print("=" * 80)
    print(
        f"{'Experiment':<28} | {'Accuracy':<8} | {'Precision':<9} | "
        f"{'Recall':<8} | {'F1-Score':<8} | {'ROC-AUC':<8}"
    )
    print("-" * 80)

    for exp in metadata["experiments"]:
        name = exp["experiment_key"]
        m = exp["metrics"]
        print(
            f"{name:<28} | {m['accuracy']:<8.4f} | {m['precision']:<9.4f} | "
            f"{m['recall']:<8.4f} | {m['f1_score']:<8.4f} | {m['roc_auc']:<8.4f}"
        )

    print("-" * 80)
    print(f"[BEST] SELECTED BEST CLASSICAL MODEL: {best['selected_best_model']}")
    f1 = best['metrics']['f1_score']
    auc = best['metrics']['roc_auc']
    print(f"  F1-Score: {f1:.4f} | ROC-AUC: {auc:.4f}")
    print("=" * 80)
    print("[OK] Phase 3.3 Classical ML Baseline Pipeline finished successfully.")


if __name__ == "__main__":
    main()
