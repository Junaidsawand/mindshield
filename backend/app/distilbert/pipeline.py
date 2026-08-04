# ==============================================================================
# MindShield Backend — DistilBERT Pipeline Orchestrator
# Phase 3.4: Master Facade, Fine-Tuning Execution & Classical Comparison Export
# ==============================================================================

import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
from app.distilbert.config import DistilBERTConfig
from app.distilbert.trainer import DistilBERTTrainer


class DistilBERTPipeline:
    """Master orchestrator facade for DistilBERT fine-tuning and comparison."""

    def __init__(self, config: Optional[DistilBERTConfig] = None):
        self.config = config or DistilBERTConfig()
        self.trainer = DistilBERTTrainer(self.config)

    def run_pipeline(self) -> Dict[str, Any]:
        """Execute complete Phase 3.4 fine-tuning and evaluation workflow."""
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

        print(
            f"[DistilBERT Pipeline] Ingesting datasets from {processed_dir}..."
        )
        train_df = pd.read_csv(train_csv)
        val_df = pd.read_csv(val_csv)
        test_df = pd.read_csv(test_csv)

        # Fine-tune DistilBERT model
        metrics, history = self.trainer.train_and_evaluate(
            train_df, val_df, test_df
        )

        meta_dir = backend_dir / self.config.metadata_output_dir
        meta_dir.mkdir(parents=True, exist_ok=True)
        distilbert_meta_file = meta_dir / "distilbert_metrics.json"

        distilbert_export = {
            "pipeline_name": "MindShield DistilBERT Fine-Tuning Engine",
            "pipeline_version": "3.4.0",
            "model_name": self.config.model_name,
            "metrics": metrics,
            "training_history": history,
        }

        with open(distilbert_meta_file, "w", encoding="utf-8") as f:
            json.dump(distilbert_export, f, indent=2)

        # Compare against Best Classical Model from Phase 3.3
        best_classical_path = (
            backend_dir / "data/models/best_classical_model/metadata.json"
        )
        comparison_out_path = (
            meta_dir / "classical_vs_distilbert_comparison.json"
        )

        comparison_res = (
            self.trainer.evaluator.generate_classical_vs_distilbert_comparison(
                distilbert_metrics=metrics,
                best_classical_metadata_path=best_classical_path,
                output_metadata_path=comparison_out_path,
            )
        )

        print(
            f"[DistilBERT Pipeline] Metadata exported to {distilbert_meta_file}"
        )
        print(
            f"[DistilBERT Pipeline] Comparison exported to {comparison_out_path}"
        )

        return {
            "distilbert_metrics": distilbert_export,
            "comparison": comparison_res,
        }
