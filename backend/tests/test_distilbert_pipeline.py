# ==============================================================================
# MindShield Backend — DistilBERT Test Suite
# Phase 3.4: Unit & Integration Tests for DistilBERT Fine-Tuning & Comparison
# ==============================================================================

import json
from pathlib import Path

import numpy as np
from app.distilbert.config import DistilBERTConfig
from app.distilbert.dataset import SMSDataset
from app.distilbert.evaluator import DistilBERTEvaluator


class MockTokenizer:
    """Mock tokenizer for fast unit testing of SMSDataset."""

    def __call__(
        self,
        text: str,
        truncation: bool = True,
        padding: bool = True,
        max_length: int = 64,
        return_tensors: str = "pt",
    ):
        """Encode mock input tensors."""
        import torch

        return {
            "input_ids": torch.ones((1, max_length), dtype=torch.long),
            "attention_mask": torch.ones((1, max_length), dtype=torch.long),
        }


def test_distilbert_config_defaults():
    """Verify DistilBERTConfig defaults and serialization."""
    cfg = DistilBERTConfig()
    assert cfg.model_name == "distilbert-base-uncased"
    assert cfg.batch_size == 32
    assert cfg.learning_rate == 2e-5
    assert cfg.max_length == 64

    d = cfg.to_dict()
    assert d["model_name"] == "distilbert-base-uncased"
    assert "models_output_dir" in d


def test_sms_dataset_structure():
    """Verify PyTorch SMSDataset length and tensor structure."""
    texts = ["Legitimate message 1", "URGENT! Claim prize now"]
    labels = [0, 1]
    tokenizer = MockTokenizer()

    ds = SMSDataset(
        texts=texts, labels=labels, tokenizer=tokenizer, max_length=64
    )
    assert len(ds) == 2

    item = ds[0]
    assert "input_ids" in item
    assert "attention_mask" in item
    assert "labels" in item
    assert item["input_ids"].shape[0] == 64
    assert item["labels"].item() == 0


def test_distilbert_evaluator_metrics():
    """Verify DistilBERTEvaluator calculates 11 performance metrics."""
    evaluator = DistilBERTEvaluator()

    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    y_pred = np.array([0, 0, 1, 1, 0, 1, 0, 0])
    y_prob = np.array([0.1, 0.2, 0.9, 0.85, 0.15, 0.95, 0.2, 0.4])

    metrics = evaluator.compute_all_metrics(
        y_true=y_true,
        y_pred=y_pred,
        y_prob=y_prob,
        train_time_sec=12.5,
        pred_time_sec=0.8,
        model_size_mb=256.0,
    )

    assert metrics["accuracy"] == 0.875
    assert "f1_score" in metrics
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics
    assert "mcc" in metrics
    assert "cohen_kappa" in metrics
    assert "confusion_matrix" in metrics
    assert "classification_report" in metrics


def test_classical_vs_distilbert_comparison_generation(tmp_path: Path):
    """Verify classical vs DistilBERT comparison report and figure generation."""
    fig_dir = tmp_path / "figures"
    evaluator = DistilBERTEvaluator(figures_dir=fig_dir)

    distil_metrics = {
        "accuracy": 0.985,
        "precision": 0.980,
        "recall": 0.910,
        "f1_score": 0.9438,
        "roc_auc": 0.9950,
    }

    best_classical_meta = tmp_path / "classical_meta.json"
    classical_data = {
        "selected_best_model": "linear_svm_count",
        "metrics": {
            "accuracy": 0.9825,
            "precision": 0.9825,
            "recall": 0.8750,
            "f1_score": 0.9256,
            "roc_auc": 0.9908,
        },
    }
    with open(best_classical_meta, "w", encoding="utf-8") as f:
        json.dump(classical_data, f)

    out_comp_json = tmp_path / "comparison.json"
    comp_result = evaluator.generate_classical_vs_distilbert_comparison(
        distilbert_metrics=distil_metrics,
        best_classical_metadata_path=best_classical_meta,
        output_metadata_path=out_comp_json,
    )

    assert comp_result["winner"] == "distilbert-base-uncased"
    assert comp_result["delta"]["f1_score_gain"] > 0
    assert out_comp_json.exists()
    assert (fig_dir / "15_classical_vs_distilbert_comparison.png").exists()
