# ==============================================================================
# MindShield Backend — Exploratory Data Analysis (EDA) Engine
# Phase 3.1: Dataset-Agnostic Statistical & Frequency Analysis
# ==============================================================================

import collections
import logging
import re
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from app.data.config import DatasetConfig

logger = logging.getLogger(__name__)

# Basic English stopwords list used strictly for EDA frequency visualization
DEFAULT_EDA_STOPWORDS = set(
    [
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
        "your", "yours", "yourself", "yourselves", "he", "him", "his",
        "himself", "she", "her", "hers", "herself", "it", "its", "itself",
        "they", "them", "their", "theirs", "themselves", "what", "which",
        "who", "whom", "this", "that", "these", "those", "am", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "having",
        "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if",
        "or", "because", "as", "until", "while", "of", "at", "by", "for",
        "with", "about", "against", "between", "into", "through", "during",
        "before", "after", "above", "below", "to", "from", "up", "down", "in",
        "out", "on", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "any",
        "both", "each", "few", "more", "most", "other", "some", "such", "no",
        "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s",
        "t", "can", "will", "just", "don", "should", "now", "u", "ur", "2", "4",
    ]
)


class SMSDatasetEDA:
    """Exploratory Data Analysis engine for text classification corpora.

    Computes statistical properties, length distributions, class balance ratios,
    vocabulary metrics, missing values, duplicates, and n-gram frequencies.
    """

    def __init__(self, config: DatasetConfig):
        """Initialize EDA engine with configuration.

        Args:
            config: DatasetConfig instance.
        """
        self.config = config

    def perform_full_eda(
        self, df: pd.DataFrame, dataset_stage: str = "cleaned"
    ) -> Dict[str, Any]:
        """Perform comprehensive exploratory data analysis on a text dataset.

        Args:
            df: DataFrame containing 'text' and 'label' columns.
            dataset_stage: Identifier for stage (e.g. 'raw', 'cleaned').

        Returns:
            Dict[str, Any]: Nested metadata dictionary.
        """
        logger.info(
            f"Running full EDA for stage '{dataset_stage}' on {len(df)} records."
        )

        label_col = (
            "label"
            if "label" in df.columns
            else ("raw_label" if "raw_label" in df.columns else df.columns[0])
        )

        missing_values_count = int(
            df["text"].isna().sum() + df[label_col].isna().sum()
        )
        exact_duplicates_count = int(df.duplicated(subset=["text"]).sum())

        # Precompute length metrics
        df_analyzed = df.copy()
        df_analyzed["char_length"] = df_analyzed["text"].apply(
            lambda x: len(str(x))
        )
        df_analyzed["word_count"] = df_analyzed["text"].apply(
            lambda x: len(str(x).split())
        )
        df_analyzed["avg_word_length"] = df_analyzed.apply(
            lambda r: r["char_length"] / r["word_count"]
            if r["word_count"] > 0
            else 0.0,
            axis=1,
        )
        df_analyzed["sentence_count"] = df_analyzed["text"].apply(
            lambda x: len(re.split(r"[.!?]+", str(x)))
        )

        # Class distribution
        class_counts = df_analyzed[label_col].value_counts().to_dict()
        total_records = len(df_analyzed)

        ham_count = int(class_counts.get(0, 0) + class_counts.get("ham", 0))
        spam_count = int(class_counts.get(1, 0) + class_counts.get("spam", 0))
        ham_pct = (
            round((ham_count / total_records) * 100, 2)
            if total_records > 0
            else 0.0
        )
        spam_pct = (
            round((spam_count / total_records) * 100, 2)
            if total_records > 0
            else 0.0
        )
        imbalance_ratio = (
            round(ham_count / spam_count, 2) if spam_count > 0 else 0.0
        )

        overall_length_stats = self._compute_summary_stats(df_analyzed)
        ham_mask = df_analyzed[label_col].isin([0, "ham"])
        spam_mask = df_analyzed[label_col].isin([1, "spam"])
        ham_df = df_analyzed[ham_mask]
        spam_df = df_analyzed[spam_mask]

        ham_length_stats = self._compute_summary_stats(ham_df)
        spam_length_stats = self._compute_summary_stats(spam_df)

        top_unigrams_ham = self._extract_top_ngrams(
            ham_df["text"], n=1, top_k=20
        )
        top_unigrams_spam = self._extract_top_ngrams(
            spam_df["text"], n=1, top_k=20
        )
        top_bigrams_spam = self._extract_top_ngrams(
            spam_df["text"], n=2, top_k=15
        )

        eda_results = {
            "dataset_name": self.config.dataset_name,
            "dataset_stage": dataset_stage,
            "total_records": total_records,
            "missing_values": missing_values_count,
            "exact_duplicates": exact_duplicates_count,
            "class_distribution": {
                "ham_count": ham_count,
                "spam_count": spam_count,
                "ham_percentage": ham_pct,
                "spam_percentage": spam_pct,
                "imbalance_ratio": imbalance_ratio,
            },
            "overall_metrics": overall_length_stats,
            "ham_metrics": ham_length_stats,
            "spam_metrics": spam_length_stats,
            "vocabulary_analysis": {
                "top_unigrams_ham": top_unigrams_ham,
                "top_unigrams_spam": top_unigrams_spam,
                "top_bigrams_spam": top_bigrams_spam,
            },
        }

        logger.info(
            f"EDA complete: {total_records} records (Ham: {ham_count} "
            f"[{ham_pct}%], Spam: {spam_count} [{spam_pct}%], Ratio: "
            f"{imbalance_ratio}:1)"
        )

        return eda_results

    def _compute_summary_stats(
        self, df: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """Compute parametric and non-parametric summary statistics."""
        if len(df) == 0:
            return {}

        stats = {}
        target_cols = [
            "char_length",
            "word_count",
            "sentence_count",
            "avg_word_length",
        ]
        for col in target_cols:
            series = df[col]
            q25, q75 = np.percentile(series, [25, 75])
            stats[col] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": round(float(series.mean()), 2),
                "std": round(float(series.std()), 2),
                "median": round(float(series.median()), 2),
                "q25": round(float(q25), 2),
                "q75": round(float(q75), 2),
                "iqr": round(float(q75 - q25), 2),
            }

        return stats

    def _extract_top_ngrams(
        self, text_series: pd.Series, n: int = 1, top_k: int = 20
    ) -> List[Tuple[str, int]]:
        """Extract top n-gram frequencies for EDA visualization."""
        counter = collections.Counter()
        for text in text_series:
            tokens = re.findall(r"\b[a-zA-Z0-9']+\b", str(text).lower())
            tokens = [
                t for t in tokens if t not in DEFAULT_EDA_STOPWORDS and len(t) > 1
            ]

            if n == 1:
                counter.update(tokens)
            else:
                ngrams = [
                    " ".join(tokens[i : i + n])
                    for i in range(len(tokens) - n + 1)
                ]
                counter.update(ngrams)

        return counter.most_common(top_k)
