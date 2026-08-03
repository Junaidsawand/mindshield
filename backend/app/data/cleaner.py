# ==============================================================================
# MindShield Backend — Data Cleaner & Stratified Splitter Engine
# Phase 3.1: Non-Destructive Preprocessing & DistilBERT Compatibility
# ==============================================================================

import logging
import re
from typing import Dict, Tuple

import pandas as pd
from app.data.config import DatasetConfig
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class SMSDatasetCleaner:
    """Dataset-agnostic data cleaner and stratified train/val/test splitter.

    Applies non-destructive text normalization designed for maximum compatibility
    with Transformer models (DistilBERT), normalizes labels, removes exact duplicates,
    and creates stratified dataset splits.
    """

    def __init__(self, config: DatasetConfig):
        """Initialize cleaner with dataset configuration.

        Args:
            config: DatasetConfig instance.
        """
        self.config = config

    def normalize_text(self, text: str) -> str:
        """Perform non-destructive text normalization for transformer compatibility.

        Preserves punctuation, capitalization, URLs, phone numbers, domain names,
        currency symbols, and emojis intact.

        Args:
            text: Input raw text string.

        Returns:
            str: Safely normalized text string.
        """
        if not isinstance(text, str):
            text = str(text) if pd.notna(text) else ""

        # Remove null bytes
        text = text.replace("\x00", "")

        # Normalize line endings (\r\n -> \n, \r -> \n)
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Normalize multiple spaces / tabs into single spaces
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        cleaned = "\n".join(lines).strip()

        return cleaned

    def clean_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """Clean raw dataset, normalize labels, and remove exact duplicates.

        Args:
            df: Raw input DataFrame with 'raw_label' and 'text' columns.

        Returns:
            Tuple[pd.DataFrame, Dict[str, int]]: Cleaned DataFrame and audit metrics.
        """
        initial_record_count = len(df)
        logger.info(
            f"Starting dataset cleaning on {initial_record_count} raw records."
        )

        # 1. Drop records with missing text or missing raw_label
        cleaned_df = df.dropna(subset=["text", "raw_label"]).copy()
        missing_dropped_count = initial_record_count - len(cleaned_df)

        # 2. Non-destructive text normalization
        cleaned_df["text"] = cleaned_df["text"].apply(self.normalize_text)

        # Drop records that became empty after whitespace trimming
        cleaned_df = cleaned_df[cleaned_df["text"].str.len() > 0].copy()

        # 3. Label normalization (map raw_label str -> integer label)
        cleaned_df["raw_label_clean"] = (
            cleaned_df["raw_label"].astype(str).str.strip().str.lower()
        )
        cleaned_df["label"] = cleaned_df["raw_label_clean"].map(
            self.config.label_mapping
        )

        # Drop unmapped or invalid labels
        unmapped_mask = cleaned_df["label"].isna()
        if unmapped_mask.any():
            unmapped_count = unmapped_mask.sum()
            logger.warning(
                f"Dropping {unmapped_count} records with unmapped labels: "
                f"{cleaned_df[unmapped_mask]['raw_label'].unique()}"
            )
            cleaned_df = cleaned_df[~unmapped_mask].copy()

        cleaned_df["label"] = cleaned_df["label"].astype(int)

        # Select standard columns: text (str), label (int)
        cleaned_df = cleaned_df[["text", "label"]].copy()

        # 4. Remove exact duplicate messages
        pre_dedup_count = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates(
            subset=["text"], keep="first"
        ).copy()
        cleaned_df = cleaned_df.reset_index(drop=True)
        dedup_removed_count = pre_dedup_count - len(cleaned_df)

        stats = {
            "initial_raw_records": initial_record_count,
            "missing_or_empty_dropped": missing_dropped_count,
            "exact_duplicates_removed": dedup_removed_count,
            "final_cleaned_records": len(cleaned_df),
        }

        logger.info(
            f"Cleaning complete: {len(cleaned_df)} records remaining. "
            f"Removed {dedup_removed_count} exact duplicates."
        )

        return cleaned_df, stats

    def create_stratified_splits(
        self, df: pd.DataFrame
    ) -> Dict[str, pd.DataFrame]:
        """Create reproducible stratified train/validation/test splits.

        Args:
            df: Cleaned DataFrame with 'text' and 'label' columns.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing 'train', 'val', 'test',
            and 'cleaned_full' DataFrames.
        """
        self.config.validate()

        logger.info(
            f"Generating stratified splits (train={self.config.train_ratio}, "
            f"val={self.config.val_ratio}, test={self.config.test_ratio}, "
            f"seed={self.config.random_seed})..."
        )

        val_test_ratio = self.config.val_ratio + self.config.test_ratio
        test_size_rel = (
            self.config.test_ratio / val_test_ratio
            if val_test_ratio > 0
            else 0.5
        )

        # Check if stratified splitting is feasible
        label_counts = df["label"].value_counts().to_dict()
        min_class_count = min(label_counts.values()) if label_counts else 0

        # Require at least 20 samples per class for safe stratified splitting
        can_stratify = min_class_count >= 20

        stratify_step1 = df["label"] if can_stratify else None
        if not can_stratify:
            logger.warning(
                f"Small class count detected (min class samples: {min_class_count}). "
                "Falling back to unstratified random splitting."
            )

        # Step 1: Split into Train vs (Val + Test)
        train_df, temp_df = train_test_split(
            df,
            test_size=val_test_ratio,
            stratify=stratify_step1,
            random_state=self.config.random_seed,
        )

        if len(temp_df) <= 1:
            val_df = temp_df.copy()
            test_df = temp_df.copy()
        else:
            temp_counts = temp_df["label"].value_counts().to_dict().values()
            temp_min_class = min(temp_counts) if len(temp_df) > 0 else 0
            stratify_step2 = (
                temp_df["label"]
                if (can_stratify and temp_min_class >= 5)
                else None
            )

            # Step 2: Split (Val + Test) into Val and Test
            val_df, test_df = train_test_split(
                temp_df,
                test_size=test_size_rel,
                stratify=stratify_step2,
                random_state=self.config.random_seed,
            )

        splits = {
            "train": train_df.reset_index(drop=True),
            "val": val_df.reset_index(drop=True),
            "test": test_df.reset_index(drop=True),
            "cleaned_full": df.reset_index(drop=True),
        }

        logger.info(
            f"Stratified splits created successfully: "
            f"Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}"
        )

        return splits
