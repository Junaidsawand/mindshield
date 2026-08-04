# ==============================================================================
# MindShield Backend — DistilBERT Evaluator & Comparative Benchmark Module
# Phase 3.4: DistilBERT Performance Evaluation & Classical vs Transformer
# ==============================================================================

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


class DistilBERTEvaluator:
    """Evaluation and comparison engine for DistilBERT fine-tuning."""

    def __init__(self, figures_dir: Optional[Path] = None):
        self.figures_dir = figures_dir or Path("data/figures")
        self.figures_dir.mkdir(parents=True, exist_ok=True)

        plt.style.use(
            "seaborn-v0_8-whitegrid"
            if "seaborn-v0_8-whitegrid" in plt.style.available
            else "default"
        )
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 10,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
        })

    def compute_all_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        train_time_sec: float,
        pred_time_sec: float,
        model_size_mb: float,
    ) -> Dict[str, Any]:
        """Compute complete 11 evaluation metrics for DistilBERT."""
        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        f1_macro = float(
            f1_score(y_true, y_pred, average="macro", zero_division=0)
        )
        f1_weighted = float(
            f1_score(y_true, y_pred, average="weighted", zero_division=0)
        )

        try:
            roc_auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            roc_auc = 0.5

        try:
            pr_auc = float(average_precision_score(y_true, y_prob))
        except Exception:
            pr_auc = 0.0

        mcc = float(matthews_corrcoef(y_true, y_pred))
        kappa = float(cohen_kappa_score(y_true, y_pred))
        cm = confusion_matrix(y_true, y_pred).tolist()
        report_dict = classification_report(
            y_true, y_pred, target_names=["ham", "spam"], output_dict=True
        )

        return {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "mcc": round(mcc, 4),
            "cohen_kappa": round(kappa, 4),
            "training_time_seconds": round(train_time_sec, 4),
            "prediction_time_seconds": round(pred_time_sec, 4),
            "model_size_mb": round(model_size_mb, 4),
            "confusion_matrix": cm,
            "classification_report": report_dict,
        }

    def generate_figures(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        history: Dict[str, List[float]],
    ) -> List[Path]:
        """Generate DistilBERT publication-grade 300 DPI figures."""
        output_paths = []

        # 1. Figure 11: Confusion Matrix
        fig, ax = plt.subplots(figsize=(6, 5))
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            ax=ax,
            xticklabels=["Ham", "Spam"],
            yticklabels=["Ham", "Spam"],
        )
        ax.set_title(
            "DistilBERT Fine-Tuned Confusion Matrix", fontweight="bold"
        )
        ax.set_ylabel("True Label")
        ax.set_xlabel("Predicted Label")
        plt.tight_layout()
        fig_11_path = self.figures_dir / "11_distilbert_confusion_matrix.png"
        plt.savefig(fig_11_path, dpi=300)
        plt.close()
        output_paths.append(fig_11_path)

        # 2. Figure 12: ROC Curve
        fig, ax = plt.subplots(figsize=(7, 6))
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        auc_score = roc_auc_score(y_true, y_prob)
        ax.plot(
            fpr,
            tpr,
            color="#d9381e",
            lw=2,
            label=f"DistilBERT (AUC = {auc_score:.4f})",
        )
        ax.plot(
            [0, 1],
            [0, 1],
            "k--",
            lw=1.5,
            label="Random Classifier (AUC=0.50)",
        )
        ax.set_title(
            "DistilBERT Receiver Operating Characteristic (ROC) Curve",
            fontweight="bold",
        )
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.legend(loc="lower right")
        plt.tight_layout()
        fig_12_path = self.figures_dir / "12_distilbert_roc_curve.png"
        plt.savefig(fig_12_path, dpi=300)
        plt.close()
        output_paths.append(fig_12_path)

        # 3. Figure 13: Precision-Recall Curve
        fig, ax = plt.subplots(figsize=(7, 6))
        precisions, recalls, _ = precision_recall_curve(y_true, y_prob)
        pr_auc = average_precision_score(y_true, y_prob)
        ax.plot(
            recalls,
            precisions,
            color="#2b5c8f",
            lw=2,
            label=f"DistilBERT (PR-AUC = {pr_auc:.4f})",
        )
        ax.set_title("DistilBERT Precision-Recall Curve", fontweight="bold")
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.legend(loc="lower left")
        plt.tight_layout()
        fig_13_path = self.figures_dir / "13_distilbert_pr_curve.png"
        plt.savefig(fig_13_path, dpi=300)
        plt.close()
        output_paths.append(fig_13_path)

        # 4. Figure 14: Learning Curves
        if history and "train_loss" in history and "val_loss" in history:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            epochs = range(1, len(history["train_loss"]) + 1)

            ax1.plot(
                epochs,
                history["train_loss"],
                "o-",
                label="Train Loss",
                color="#2b5c8f",
            )
            ax1.plot(
                epochs,
                history["val_loss"],
                "s-",
                label="Val Loss",
                color="#d9381e",
            )
            ax1.set_title("Training vs Validation Loss", fontweight="bold")
            ax1.set_xlabel("Epoch")
            ax1.set_ylabel("Loss")
            ax1.legend()

            if "val_f1" in history:
                ax2.plot(
                    epochs,
                    history["val_f1"],
                    "^-",
                    label="Val F1-Score",
                    color="#2e7d32",
                )
                ax2.set_title(
                    "Validation F1-Score over Epochs", fontweight="bold"
                )
                ax2.set_xlabel("Epoch")
                ax2.set_ylabel("F1-Score")
                ax2.legend()

            plt.tight_layout()
            fig_14_path = (
                self.figures_dir / "14_distilbert_learning_curves.png"
            )
            plt.savefig(fig_14_path, dpi=300)
            plt.close()
            output_paths.append(fig_14_path)

        return output_paths

    def generate_classical_vs_distilbert_comparison(
        self,
        distilbert_metrics: Dict[str, Any],
        best_classical_metadata_path: Path,
        output_metadata_path: Path,
    ) -> Dict[str, Any]:
        """Compare DistilBERT against the top classical model."""
        classical_meta = {}
        if best_classical_metadata_path.exists():
            with open(
                best_classical_metadata_path, "r", encoding="utf-8"
            ) as f:
                classical_meta = json.load(f)

        c_name = classical_meta.get("selected_best_model", "linear_svm_count")
        classical_metrics = classical_meta.get("metrics", {})

        comparison_data = {
            "classical_model": {
                "name": c_name,
                "metrics": classical_metrics,
            },
            "distilbert_model": {
                "name": "distilbert-base-uncased",
                "metrics": distilbert_metrics,
            },
            "delta": {
                "accuracy_gain": round(
                    distilbert_metrics["accuracy"]
                    - classical_metrics.get("accuracy", 0.0),
                    4,
                ),
                "f1_score_gain": round(
                    distilbert_metrics["f1_score"]
                    - classical_metrics.get("f1_score", 0.0),
                    4,
                ),
                "roc_auc_gain": round(
                    distilbert_metrics["roc_auc"]
                    - classical_metrics.get("roc_auc", 0.0),
                    4,
                ),
            },
            "winner": (
                "distilbert-base-uncased"
                if distilbert_metrics["f1_score"]
                >= classical_metrics.get("f1_score", 0.0)
                else c_name
            ),
        }

        output_metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_metadata_path, "w", encoding="utf-8") as f:
            json.dump(comparison_data, f, indent=2)

        # Generate Figure 15: Classical vs DistilBERT Comparison Bar Chart
        fig, ax = plt.subplots(figsize=(9, 6))
        metrics_keys = [
            "accuracy", "precision", "recall", "f1_score", "roc_auc"
        ]

        c_vals = [classical_metrics.get(k, 0.0) for k in metrics_keys]
        d_vals = [distilbert_metrics.get(k, 0.0) for k in metrics_keys]

        x = np.arange(len(metrics_keys))
        width = 0.35

        ax.bar(
            x - width / 2,
            c_vals,
            width,
            label=f"Best Classical ({c_name})",
            color="#2b5c8f",
        )
        ax.bar(
            x + width / 2,
            d_vals,
            width,
            label="DistilBERT Fine-Tuned",
            color="#d9381e",
        )

        ax.set_title(
            "Best Classical Model vs DistilBERT Performance Benchmark",
            fontweight="bold",
        )
        ax.set_ylabel("Metric Score")
        ax.set_xticks(x)
        ax.set_xticklabels(
            [k.upper().replace("_", " ") for k in metrics_keys],
            fontweight="bold",
        )
        ax.set_ylim(0.80, 1.02)
        ax.legend(loc="lower right")

        plt.tight_layout()
        fig_15_path = (
            self.figures_dir / "15_classical_vs_distilbert_comparison.png"
        )
        plt.savefig(fig_15_path, dpi=300)
        plt.close()

        return comparison_data
