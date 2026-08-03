# ==============================================================================
# MindShield Backend — Baseline ML Pipeline Orchestrator
# Phase 3.3: Master Facade, Experiment Execution & Metadata Export
# ==============================================================================

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from app.baselines.config import BaselineConfig
from app.baselines.trainer import BaselineTrainer


class BaselineMLPipeline:
    """Master orchestrator facade for Classical Machine Learning Baselines."""

    def __init__(self, config: Optional[BaselineConfig] = None):
        self.config = config or BaselineConfig()
        self.trainer = BaselineTrainer(self.config)

    def run_pipeline(self) -> Dict[str, Any]:
        """Execute complete Phase 3.3 baseline training workflow."""
        backend_dir = Path(__file__).resolve().parents[2]
        processed_dir = backend_dir / self.config.processed_data_dir

        train_csv = processed_dir / "train.csv"
        val_csv = processed_dir / "val.csv"
        test_csv = processed_dir / "test.csv"

        if not (train_csv.exists() and test_csv.exists()):
            raise FileNotFoundError(
                f"Processed dataset CSV files not found in {processed_dir}. "
                "Ensure Phase 3.1 dataset preparation pipeline has been run."
            )

        print(f"[Pipeline] Ingesting datasets from {processed_dir}...")
        train_df = pd.read_csv(train_csv)
        val_df = pd.read_csv(val_csv)
        test_df = pd.read_csv(test_csv)

        # Execute training and evaluation across all model combinations
        exp_results, best_meta = self.trainer.train_and_evaluate_all(
            train_df, val_df, test_df
        )

        # Prepare summary records for JSON export
        exportable_records = []
        for r in exp_results:
            rec = {k: v for k, v in r.items() if k != "y_prob"}
            exportable_records.append(rec)

        metadata_export = {
            "pipeline_name": "MindShield Classical ML Baseline Engine",
            "pipeline_version": "3.3.0",
            "total_experiments_evaluated": len(exportable_records),
            "best_classical_model": best_meta,
            "experiments": exportable_records,
        }

        # Export comparison JSON
        meta_dir = backend_dir / self.config.metadata_output_dir
        meta_file = meta_dir / "baseline_models_comparison.json"
        meta_file.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(metadata_export, f, indent=2)

        print(f"[Pipeline] Metadata comparison exported to {meta_file}")
        return metadata_export
