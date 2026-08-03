# ==============================================================================
# MindShield Backend — Baseline ML Models Test Suite
# Phase 3.3: Unit & Integration Tests for Baselines, 5-Fold CV & Best Model Export
# ==============================================================================

from pathlib import Path

import pandas as pd
import pytest
from app.baselines.config import BaselineConfig
from app.baselines.evaluator import BaselineEvaluator
from app.baselines.trainer import BaselineTrainer


@pytest.fixture
def sample_dataframes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fixture providing synthetic train, val, and test DataFrames."""
    train_data = []
    for i in range(30):
        train_data.append(
            {"text": f"Safe legitimate message number {i}", "label": 0}
        )
        train_data.append(
            {
                "text": f"URGENT! Claim £{1000+i} prize at http://scam{i}.link",
                "label": 1,
            }
        )

    val_data = []
    for i in range(10):
        val_data.append(
            {"text": f"Val safe message number {i}", "label": 0}
        )
        val_data.append(
            {
                "text": f"URGENT! Call 0800{100+i} for prize claim",
                "label": 1,
            }
        )

    test_data = []
    for i in range(10):
        test_data.append(
            {"text": f"Test safe message number {i}", "label": 0}
        )
        test_data.append(
            {
                "text": f"URGENT! Win prize claim now http://test{i}.com",
                "label": 1,
            }
        )

    return (
        pd.DataFrame(train_data),
        pd.DataFrame(val_data),
        pd.DataFrame(test_data),
    )


def test_baseline_config_defaults():
    """Verify BaselineConfig defaults and serialization."""
    cfg = BaselineConfig()
    assert "tfidf" in cfg.vectorizer_types
    assert "count" in cfg.vectorizer_types
    assert cfg.max_features == 5000
    assert cfg.n_splits == 5

    d = cfg.to_dict()
    assert d["primary_metric"] == "f1_score"


def test_evaluator_computes_11_metrics():
    """Verify BaselineEvaluator calculates all 11 performance metrics."""
    evaluator = BaselineEvaluator()

    y_true = [0, 0, 1, 1, 0, 1, 0, 1]
    y_pred = [0, 0, 1, 1, 0, 1, 0, 0]
    y_prob = [0.1, 0.2, 0.9, 0.85, 0.15, 0.95, 0.2, 0.4]

    metrics = evaluator.compute_all_metrics(
        y_true=y_true,
        y_pred=y_pred,
        y_prob=y_prob,
        train_time_sec=0.05,
        pred_time_sec=0.01,
        model_size_mb=0.15,
    )

    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "f1_macro" in metrics
    assert "f1_weighted" in metrics
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics
    assert "mcc" in metrics
    assert "cohen_kappa" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["training_time_seconds"] == 0.05


def test_trainer_5fold_cv_and_training(
    tmp_path: Path, sample_dataframes
):
    """Verify BaselineTrainer 5-fold CV, training, and model export."""
    train_df, val_df, test_df = sample_dataframes

    cfg = BaselineConfig(
        models_output_dir=tmp_path / "models",
        best_model_dir=tmp_path / "best_model",
        figures_output_dir=tmp_path / "figures",
        metadata_output_dir=tmp_path / "metadata",
        max_features=500,
        n_splits=3,
    )

    trainer = BaselineTrainer(config=cfg)
    exp_results, best_meta = trainer.train_and_evaluate_all(
        train_df, val_df, test_df
    )

    assert len(exp_results) == 8
    assert "selected_best_model" in best_meta

    best_dir = tmp_path / "best_model"
    assert (best_dir / "model.joblib").exists()
    assert (best_dir / "vectorizer.joblib").exists()
    assert (best_dir / "metadata.json").exists()


def test_pakscam_baseline_dataset_compatibility(
    tmp_path: Path
):
    """Verify dataset-agnostic compatibility with PakScam payloads."""
    pakscam_train = pd.DataFrame({
        "text": [
            "BISP 25000 prize claimed call 03001234567",
            "Kese ho bhai Shaam ko milte hain",
            "BISP reward 25000 click link http://scam.pk",
            "Aapka parcel dispatch ho gaya hai",
        ] * 5,
        "label": [1, 0, 1, 0] * 5,
    })
    pakscam_val = pakscam_train.copy()
    pakscam_test = pakscam_train.copy()

    cfg = BaselineConfig(
        models_output_dir=tmp_path / "pak_models",
        best_model_dir=tmp_path / "pak_best",
        figures_output_dir=tmp_path / "pak_fig",
        metadata_output_dir=tmp_path / "pak_meta",
        max_features=100,
        n_splits=2,
    )

    trainer = BaselineTrainer(config=cfg)
    results, best = trainer.train_and_evaluate_all(
        pakscam_train, pakscam_val, pakscam_test
    )

    assert len(results) == 8
    assert (tmp_path / "pak_best" / "model.joblib").exists()
