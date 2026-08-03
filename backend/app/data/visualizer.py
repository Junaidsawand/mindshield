# ==============================================================================
# MindShield Backend — Publication Quality Visualizer Engine
# Phase 3.1: Publication-Grade 300-DPI Figure Generation
# ==============================================================================

import logging
from pathlib import Path
from typing import Any, Dict, List

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from app.data.config import DatasetConfig

matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt  # noqa: E402

logger = logging.getLogger(__name__)

# Configure global publication styling
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 11,
        "figure.titlesize": 14,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)

COLOR_HAM = "#2b5c8f"  # Deep Slate Blue
COLOR_SPAM = "#d9381e"  # Vivid Crimson Red
COLOR_PALETTE = [COLOR_HAM, COLOR_SPAM]


class SMSDatasetVisualizer:
    """Publication-grade visualizer generating 300-DPI figures for dataset EDA."""

    def __init__(self, config: DatasetConfig, output_figures_dir: Path):
        """Initialize visualizer with configuration and output path.

        Args:
            config: DatasetConfig instance.
            output_figures_dir: Path to output directory.
        """
        self.config = config
        self.figures_dir = Path(output_figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def generate_all_figures(
        self,
        df: pd.DataFrame,
        eda_meta: Dict[str, Any],
        splits: Dict[str, pd.DataFrame],
    ) -> List[Path]:
        """Generate all publication-quality EDA figures.

        Args:
            df: Cleaned full dataset DataFrame with 'text' and 'label'.
            eda_meta: Precomputed EDA analysis metadata.
            splits: Dictionary of split DataFrames ('train', 'val', 'test').

        Returns:
            List[Path]: Paths to generated PNG figure files.
        """
        logger.info(
            f"Generating 6 publication-grade figures in: {self.figures_dir}"
        )

        df_plot = df.copy()
        df_plot["char_length"] = df_plot["text"].apply(lambda x: len(str(x)))
        df_plot["word_count"] = df_plot["text"].apply(
            lambda x: len(str(x).split())
        )
        df_plot["class_name"] = df_plot["label"].map(
            self.config.standard_label_names
        )

        fig_paths = []
        fig_paths.append(self._plot_class_distribution(eda_meta))
        fig_paths.append(self._plot_message_length_distribution(df_plot))
        fig_paths.append(self._plot_length_boxplots(df_plot))
        fig_paths.append(self._plot_top_words_comparison(eda_meta))
        fig_paths.append(self._plot_ngram_frequency(eda_meta))
        fig_paths.append(self._plot_split_distribution(splits))

        logger.info(
            f"Successfully generated all {len(fig_paths)} publication figures."
        )

        return fig_paths

    def _plot_class_distribution(self, eda_meta: Dict[str, Any]) -> Path:
        """Figure 1: Bar chart and Pie chart of Class Distribution."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        dist = eda_meta["class_distribution"]
        counts = [dist["ham_count"], dist["spam_count"]]
        labels = ["Legitimate (Ham)", "Spam / Smishing"]

        # Bar chart
        bars = ax1.bar(
            labels,
            counts,
            color=COLOR_PALETTE,
            width=0.5,
            edgecolor="black",
            linewidth=1.2,
        )
        ax1.set_title("Class Frequency Count", pad=12, fontweight="bold")
        ax1.set_ylabel("Number of Messages")
        ax1.set_ylim(0, max(counts) * 1.15)
        ax1.grid(axis="y", linestyle="--", alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            ax1.annotate(
                f"{height:,}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        # Pie chart
        ax2.pie(
            counts,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=COLOR_PALETTE,
            explode=(0, 0.08),
            wedgeprops={"edgecolor": "black", "linewidth": 1.2},
            textprops={"fontsize": 11, "fontweight": "bold"},
        )
        ax2.set_title("Class Imbalance Percentage", pad=12, fontweight="bold")

        fig.suptitle(
            f"Dataset Class Distribution ({self.config.dataset_name.upper()}) "
            f"— Imbalance Ratio {dist['imbalance_ratio']}:1",
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )

        out_path = self.figures_dir / "01_class_distribution.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def _plot_message_length_distribution(self, df: pd.DataFrame) -> Path:
        """Figure 2: Kernel Density Estimation & Histograms of Lengths."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        use_kde = len(df) >= 20 and df["char_length"].nunique() > 3

        # Char length distribution
        sns.histplot(
            data=df,
            x="char_length",
            hue="class_name",
            palette={"ham": COLOR_HAM, "spam": COLOR_SPAM},
            kde=use_kde,
            ax=ax1,
            bins=40,
            alpha=0.4,
            element="step",
        )
        ax1.set_title("Character Length Distribution", fontweight="bold")
        ax1.set_xlabel("Character Count per Message")
        ax1.set_ylabel("Message Count")
        ax1.set_xlim(0, 350)
        ax1.grid(True, linestyle="--", alpha=0.6)

        # Word count distribution
        sns.histplot(
            data=df,
            x="word_count",
            hue="class_name",
            palette={"ham": COLOR_HAM, "spam": COLOR_SPAM},
            kde=use_kde,
            ax=ax2,
            bins=40,
            alpha=0.4,
            element="step",
        )
        ax2.set_title("Word Count Distribution", fontweight="bold")
        ax2.set_xlabel("Word Count per Message")
        ax2.set_ylabel("Message Count")
        ax2.set_xlim(0, 80)
        ax2.grid(True, linestyle="--", alpha=0.6)

        fig.suptitle(
            "SMS Text Length & Word Count Distributions by Class",
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )

        out_path = self.figures_dir / "02_message_length_distribution.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def _plot_length_boxplots(self, df: pd.DataFrame) -> Path:
        """Figure 3: Side-by-side Box Plots of Lengths."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        sns.boxplot(
            data=df,
            x="class_name",
            y="char_length",
            hue="class_name",
            legend=False,
            palette={"ham": COLOR_HAM, "spam": COLOR_SPAM},
            ax=ax1,
            width=0.4,
            boxprops=dict(alpha=0.85, edgecolor="black"),
            flierprops=dict(marker="o", markersize=4, alpha=0.5),
        )
        ax1.set_title("Character Length Box Plot", fontweight="bold")
        ax1.set_xlabel("Class")
        ax1.set_ylabel("Character Count")
        ax1.set_ylim(0, 300)
        ax1.grid(True, linestyle="--", alpha=0.6)

        sns.boxplot(
            data=df,
            x="class_name",
            y="word_count",
            hue="class_name",
            legend=False,
            palette={"ham": COLOR_HAM, "spam": COLOR_SPAM},
            ax=ax2,
            width=0.4,
            boxprops=dict(alpha=0.85, edgecolor="black"),
            flierprops=dict(marker="o", markersize=4, alpha=0.5),
        )
        ax2.set_title("Word Count Box Plot", fontweight="bold")
        ax2.set_xlabel("Class")
        ax2.set_ylabel("Word Count")
        ax2.set_ylim(0, 60)
        ax2.grid(True, linestyle="--", alpha=0.6)

        fig.suptitle(
            "Length & Word Count Quartile Distributions and Outliers",
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )

        out_path = self.figures_dir / "03_length_boxplots.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def _plot_top_words_comparison(self, eda_meta: Dict[str, Any]) -> Path:
        """Figure 4: Top 20 Unigrams Comparison in Ham vs Spam."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        vocab = eda_meta["vocabulary_analysis"]
        ham_top = vocab["top_unigrams_ham"][:15] if vocab["top_unigrams_ham"] else []
        spam_top = vocab["top_unigrams_spam"][:15] if vocab["top_unigrams_spam"] else []

        ham_words, ham_counts = zip(*ham_top) if ham_top else ([], [])
        spam_words, spam_counts = zip(*spam_top) if spam_top else ([], [])

        # Ham bar chart
        ax1.barh(
            range(len(ham_words)),
            ham_counts,
            color=COLOR_HAM,
            edgecolor="black",
            alpha=0.85,
        )
        ax1.set_yticks(range(len(ham_words)))
        ax1.set_yticklabels(ham_words, fontweight="bold")
        ax1.invert_yaxis()
        ax1.set_title(
            "Top 15 Vocabulary Terms in Legitimate (Ham)", fontweight="bold"
        )
        ax1.set_xlabel("Frequency Count")
        ax1.grid(axis="x", linestyle="--", alpha=0.7)

        # Spam bar chart
        ax2.barh(
            range(len(spam_words)),
            spam_counts,
            color=COLOR_SPAM,
            edgecolor="black",
            alpha=0.85,
        )
        ax2.set_yticks(range(len(spam_words)))
        ax2.set_yticklabels(spam_words, fontweight="bold")
        ax2.invert_yaxis()
        ax2.set_title(
            "Top 15 Vocabulary Terms in Spam / Smishing", fontweight="bold"
        )
        ax2.set_xlabel("Frequency Count")
        ax2.grid(axis="x", linestyle="--", alpha=0.7)

        fig.suptitle(
            "Comparative Vocabulary Frequency Analysis",
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )

        out_path = self.figures_dir / "04_top_words_comparison.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def _plot_ngram_frequency(self, eda_meta: Dict[str, Any]) -> Path:
        """Figure 5: Top 15 Bigrams in Spam Messages."""
        fig, ax = plt.subplots(figsize=(10, 6))

        vocab = eda_meta["vocabulary_analysis"]
        bigrams = vocab.get("top_bigrams_spam", [])[:15]

        if bigrams:
            words, counts = zip(*bigrams)
            bars = ax.barh(
                range(len(words)),
                counts,
                color=COLOR_SPAM,
                edgecolor="black",
                alpha=0.85,
            )
            ax.set_yticks(range(len(words)))
            ax.set_yticklabels(words, fontweight="bold")
            ax.invert_yaxis()

            for bar in bars:
                width = bar.get_width()
                ax.annotate(
                    f"{width:,}",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(4, 0),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontweight="bold",
                )

        ax.set_title(
            "Top 15 Recurring Bigrams (2-Word Phrases) in Spam Messages",
            fontweight="bold",
            pad=12,
        )
        ax.set_xlabel("Frequency Count")
        ax.grid(axis="x", linestyle="--", alpha=0.7)

        out_path = self.figures_dir / "05_ngram_frequency.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def _plot_split_distribution(self, splits: Dict[str, pd.DataFrame]) -> Path:
        """Figure 6: Stacked Bar Chart of Train/Val/Test Split Preservation."""
        fig, ax = plt.subplots(figsize=(10, 5))

        split_names = ["Train (80%)", "Validation (10%)", "Test (10%)"]
        split_keys = ["train", "val", "test"]

        ham_counts = []
        spam_counts = []

        for key in split_keys:
            s_df = splits[key]
            c = s_df["label"].value_counts().to_dict()
            ham_counts.append(c.get(0, 0))
            spam_counts.append(c.get(1, 0))

        ind = np.arange(len(split_names))
        width = 0.45

        ax.bar(
            ind,
            ham_counts,
            width,
            color=COLOR_HAM,
            edgecolor="black",
            label="Legitimate (Ham)",
        )
        ax.bar(
            ind,
            spam_counts,
            width,
            bottom=ham_counts,
            color=COLOR_SPAM,
            edgecolor="black",
            label="Spam / Smishing",
        )

        ax.set_ylabel("Message Count")
        ax.set_title(
            "Preservation of Class Balance across Stratified Dataset Splits",
            fontweight="bold",
            pad=12,
        )
        ax.set_xticks(ind)
        ax.set_xticklabels(split_names, fontweight="bold")
        ax.legend(loc="upper right")
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        # Annotate percentages inside bars
        for i in range(len(split_names)):
            total = ham_counts[i] + spam_counts[i]
            h_pct = (ham_counts[i] / total) * 100 if total > 0 else 0
            s_pct = (spam_counts[i] / total) * 100 if total > 0 else 0
            if ham_counts[i] > 0:
                ax.text(
                    i,
                    ham_counts[i] / 2,
                    f"{ham_counts[i]:,}\n({h_pct:.1f}%)",
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )
            if spam_counts[i] > 0:
                ax.text(
                    i,
                    ham_counts[i] + (spam_counts[i] / 2),
                    f"{spam_counts[i]:,}\n({s_pct:.1f}%)",
                    ha="center",
                    va="center",
                    color="white",
                    fontweight="bold",
                )

        out_path = self.figures_dir / "06_split_distribution.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path
