# ==============================================================================
# MindShield Backend — Baseline Evaluator & Metrics Module
# Phase 3.3: 11 Performance Metrics, Feature Importance & Figure Generation
# ==============================================================================

from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

COLOR_HAM = "#2b5c8f"
COLOR_SPAM = "#d9381e"
MODEL_COLORS = [
    "#2b5c8f", "#d9381e", "#2e7d32", "#f57c00",
    "#7b1fa2", "#00838f", "#c2185b", "#455a64"
]


class BaselineEvaluator:
    """Evaluation engine for baseline classifiers.

    Computes 11 performance metrics, extracts feature importances,
    and generates publication-grade 300 DPI figures.
    """

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
        """Compute complete 11 evaluation metrics."""
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
        }

    def extract_feature_importance(
        self,
        classifier: Any,
        feature_names: List[str],
        top_k: int = 15,
    ) -> Dict[str, Any]:
        """Extract model feature importance or log-likelihood coefficients."""
        result: Dict[str, Any] = {}

        # 1. Random Forest Feature Importance
        if hasattr(classifier, "feature_importances_"):
            importances = classifier.feature_importances_
            indices = np.argsort(importances)[::-1][:top_k]
            result["random_forest"] = [
                {
                    "feature": feature_names[i],
                    "importance": round(float(importances[i]), 5),
                }
                for i in indices
            ]

        # 2. Logistic Regression Coefficients
        if hasattr(classifier, "coef_"):
            coefs = classifier.coef_[0]
            top_pos_idx = np.argsort(coefs)[::-1][:top_k]
            top_neg_idx = np.argsort(coefs)[:top_k]
            result["logistic_regression"] = {
                "top_spam_indicators": [
                    {
                        "feature": feature_names[i],
                        "coefficient": round(float(coefs[i]), 4),
                    }
                    for i in top_pos_idx
                ],
                "top_ham_indicators": [
                    {
                        "feature": feature_names[i],
                        "coefficient": round(float(coefs[i]), 4),
                    }
                    for i in top_neg_idx
                ],
            }

        # 3. Multinomial Naive Bayes Log-Likelihood Ratio
        if hasattr(classifier, "feature_log_prob_"):
            log_ratios = (
                classifier.feature_log_prob_[1]
                - classifier.feature_log_prob_[0]
            )
            top_spam_idx = np.argsort(log_ratios)[::-1][:top_k]
            top_ham_idx = np.argsort(log_ratios)[:top_k]
            result["naive_bayes"] = {
                "top_spam_features": [
                    {
                        "feature": feature_names[i],
                        "log_ratio": round(float(log_ratios[i]), 4),
                    }
                    for i in top_spam_idx
                ],
                "top_ham_features": [
                    {
                        "feature": feature_names[i],
                        "log_ratio": round(float(log_ratios[i]), 4),
                    }
                    for i in top_ham_idx
                ],
            }

        return result

    def generate_all_figures(
        self,
        experiment_results: List[Dict[str, Any]],
        test_y: np.ndarray,
    ) -> List[Path]:
        """Generate publication-grade 300 DPI figures."""
        output_paths = []

        # 1. Figure 07: Model Metrics Comparison Bar Chart
        fig, ax = plt.subplots(figsize=(12, 6))
        df_comp = pd.DataFrame(experiment_results)
        df_comp["name_vec"] = (
            df_comp["model_name"] + " (" + df_comp["vectorizer"] + ")"
        )

        x = np.arange(len(df_comp))
        width = 0.20

        ax.bar(
            x - 1.5 * width,
            df_comp["accuracy"],
            width,
            label="Accuracy",
            color="#2b5c8f",
        )
        ax.bar(
            x - 0.5 * width,
            df_comp["precision"],
            width,
            label="Precision",
            color="#00838f",
        )
        ax.bar(
            x + 0.5 * width,
            df_comp["recall"],
            width,
            label="Recall",
            color="#f57c00",
        )
        ax.bar(
            x + 1.5 * width,
            df_comp["f1_score"],
            width,
            label="F1-Score",
            color="#d9381e",
        )

        ax.set_title(
            "Baseline Machine Learning Performance Comparison",
            fontweight="bold",
        )
        ax.set_ylabel("Metric Score")
        ax.set_xticks(x)
        ax.set_xticklabels(
            df_comp["name_vec"], rotation=30, ha="right", fontweight="bold"
        )
        ax.set_ylim(0.80, 1.02)
        ax.legend(loc="lower right")

        plt.tight_layout()
        fig_07_path = self.figures_dir / "07_baseline_model_comparison.png"
        plt.savefig(fig_07_path, dpi=300)
        plt.close()
        output_paths.append(fig_07_path)

        # 2. Figure 08: Subplot Confusion Matrices (2x4 Grid)
        fig, axes = plt.subplots(2, 4, figsize=(16, 8))
        axes = axes.flatten()

        for idx, res in enumerate(experiment_results):
            if idx >= 8:
                break
            ax = axes[idx]
            cm = np.array(res["metrics"]["confusion_matrix"])
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
                f"{res['model_name']}\n({res['vectorizer'].upper()})",
                fontweight="bold",
                fontsize=10,
            )
            ax.set_ylabel("True Label")
            ax.set_xlabel("Predicted Label")

        plt.tight_layout()
        fig_08_path = self.figures_dir / "08_baseline_confusion_matrices.png"
        plt.savefig(fig_08_path, dpi=300)
        plt.close()
        output_paths.append(fig_08_path)

        # 3. Figure 09: Overlay ROC Curves with AUC Scores
        fig, ax = plt.subplots(figsize=(9, 7))
        for idx, res in enumerate(experiment_results):
            if "y_prob" in res:
                fpr, tpr, _ = roc_curve(test_y, res["y_prob"])
                auc_val = res["metrics"]["roc_auc"]
                c = MODEL_COLORS[idx % len(MODEL_COLORS)]
                ax.plot(
                    fpr,
                    tpr,
                    label=f"{res['model_name']} ({res['vectorizer']}) "
                    f"AUC={auc_val:.4f}",
                    color=c,
                    lw=2,
                )

        ax.plot(
            [0, 1],
            [0, 1],
            "k--",
            lw=1.5,
            label="Random Classifier (AUC=0.50)",
        )
        ax.set_title(
            "Receiver Operating Characteristic (ROC) Curves",
            fontweight="bold",
        )
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.legend(loc="lower right", fontsize=9)
        plt.tight_layout()
        fig_09_path = self.figures_dir / "09_baseline_roc_curves.png"
        plt.savefig(fig_09_path, dpi=300)
        plt.close()
        output_paths.append(fig_09_path)

        return output_paths
