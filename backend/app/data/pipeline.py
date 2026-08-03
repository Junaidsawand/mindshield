# ==============================================================================
# MindShield Backend — Generic Data Pipeline Orchestrator Engine
# Phase 3.1: Reproducible Dataset Engineering Pipeline
# ==============================================================================

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from app.data.cleaner import SMSDatasetCleaner
from app.data.config import UCI_SMS_CONFIG, DatasetConfig
from app.data.downloader import DatasetDownloader
from app.data.eda import SMSDatasetEDA
from app.data.loader import DatasetLoader
from app.data.visualizer import SMSDatasetVisualizer

logger = logging.getLogger(__name__)


class GenericDataPipeline:
    """Dataset-agnostic data engineering pipeline orchestrator.

    Executes download, loading, non-destructive cleaning, exploratory data
    analysis (EDA), reproducible stratified splitting, figure generation,
    and metadata export.
    """

    def __init__(
        self, config: DatasetConfig, base_data_dir: Optional[Path] = None
    ):
        """Initialize the pipeline with configuration and storage paths.

        Args:
            config: DatasetConfig instance.
            base_data_dir: Base storage directory (defaults to 'backend/data/').
        """
        self.config = config
        self.config.validate()

        if base_data_dir is None:
            base_data_dir = Path(__file__).resolve().parents[2] / "data"

        self.base_dir = Path(base_data_dir)
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.metadata_dir = self.base_dir / "metadata"
        self.figures_dir = self.base_dir / "figures"

        for d in [
            self.raw_dir,
            self.processed_dir,
            self.metadata_dir,
            self.figures_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

        self.downloader = DatasetDownloader(self.config, self.raw_dir)
        self.loader = DatasetLoader(self.config)
        self.cleaner = SMSDatasetCleaner(self.config)
        self.eda_engine = SMSDatasetEDA(self.config)
        self.visualizer = SMSDatasetVisualizer(self.config, self.figures_dir)

    def run_pipeline(self, force_redownload: bool = False) -> Dict[str, Any]:
        """Execute the end-to-end dataset engineering pipeline.

        Args:
            force_redownload: If True, forces redownloading raw archive.

        Returns:
            Dict[str, Any]: Execution results and complete metadata summary.
        """
        logger.info(
            f"=== Starting Data Engineering Pipeline: {self.config.dataset_name} ==="
        )
        start_time = datetime.now(timezone.utc)

        # 1. Download & Extract Raw Dataset
        raw_file_path = self.downloader.download_and_extract(
            force=force_redownload
        )

        # 2. Ingest Raw Dataset into DataFrame
        df_raw = self.loader.load_raw_dataset(raw_file_path)

        # 3. Exploratory Data Analysis (Raw State)
        raw_eda_meta = self.eda_engine.perform_full_eda(
            df_raw, dataset_stage="raw"
        )

        # 4. Non-Destructive Preprocessing & Deduplication
        df_cleaned, dedup_audit = self.cleaner.clean_dataset(df_raw)

        # 5. Exploratory Data Analysis (Cleaned State)
        cleaned_eda_meta = self.eda_engine.perform_full_eda(
            df_cleaned, dataset_stage="cleaned"
        )

        # 6. Stratified Train / Validation / Test Splitting
        splits = self.cleaner.create_stratified_splits(df_cleaned)

        # 7. Export Processed Datasets (CSV)
        processed_files = self._export_processed_datasets(splits)

        # 8. Publication-Quality Figure Generation (300 DPI PNGs)
        generated_figures = self.visualizer.generate_all_figures(
            df_cleaned, cleaned_eda_meta, splits
        )

        # 9. Aggregate Metadata & Export JSON
        end_time = datetime.now(timezone.utc)
        pipeline_duration_sec = round(
            (end_time - start_time).total_seconds(), 3
        )

        split_summaries = {}
        for split_key, split_df in splits.items():
            counts = split_df["label"].value_counts().to_dict()
            total = len(split_df)
            split_summaries[split_key] = {
                "total_records": total,
                "ham_count": int(counts.get(0, 0)),
                "spam_count": int(counts.get(1, 0)),
                "ham_percentage": round((counts.get(0, 0) / total) * 100, 2)
                if total > 0
                else 0.0,
                "spam_percentage": round((counts.get(1, 0) / total) * 100, 2)
                if total > 0
                else 0.0,
            }

        metadata = {
            "dataset_name": self.config.dataset_name,
            "pipeline_version": "3.1.0",
            "executed_at": end_time.isoformat(),
            "execution_duration_seconds": pipeline_duration_sec,
            "config": {
                "download_url": self.config.download_url,
                "raw_filename": self.config.raw_filename,
                "random_seed": self.config.random_seed,
                "train_ratio": self.config.train_ratio,
                "val_ratio": self.config.val_ratio,
                "test_ratio": self.config.test_ratio,
                "label_mapping": self.config.label_mapping,
            },
            "deduplication_audit": dedup_audit,
            "raw_eda_summary": raw_eda_meta,
            "cleaned_eda_summary": cleaned_eda_meta,
            "split_summaries": split_summaries,
            "processed_file_paths": {
                k: str(v) for k, v in processed_files.items()
            },
            "generated_figure_paths": [str(f) for f in generated_figures],
        }

        metadata_filepath = (
            self.metadata_dir / f"{self.config.dataset_name}_metadata.json"
        )
        with open(metadata_filepath, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(
            f"=== Pipeline completed successfully in {pipeline_duration_sec}s. "
            f"Metadata exported to {metadata_filepath} ==="
        )

        return metadata

    def _export_processed_datasets(
        self, splits: Dict[str, pd.DataFrame]
    ) -> Dict[str, Path]:
        """Save cleaned splits as standardized CSV files ('text', 'label')."""
        saved_paths = {}
        for split_name, df_split in splits.items():
            filename = f"{split_name}.csv"
            target_path = self.processed_dir / filename
            df_split[["text", "label"]].to_csv(
                target_path, index=False, encoding="utf-8"
            )
            saved_paths[split_name] = target_path
            logger.info(
                f"Saved split '{split_name}' ({len(df_split)} records) "
                f"to: {target_path}"
            )

        return saved_paths


def run_uci_pipeline(
    base_data_dir: Optional[Path] = None, force_redownload: bool = False
) -> Dict[str, Any]:
    """Run default UCI SMS Spam dataset engineering pipeline."""
    pipeline = GenericDataPipeline(UCI_SMS_CONFIG, base_data_dir=base_data_dir)
    return pipeline.run_pipeline(force_redownload=force_redownload)
