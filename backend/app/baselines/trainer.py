# ==============================================================================
# MindShield Backend — Baseline Trainer & Model Serialization Module
# Phase 3.3: 5-Fold Stratified CV, Model Serialization & Best Model Selection
# ==============================================================================

import json
from pathlib import Path
import shutil
import time
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from app.baselines.config import BaselineConfig
from app.baselines.evaluator import BaselineEvaluator
from app.nlp.pipeline import NLPPreprocessingPipeline
from app.nlp.vectorizer import NLPVectorizer


class BaselineTrainer:
    """Trainer orchestrator for baseline classifiers.

    Executes 5-Fold Stratified Cross-Validation, model training, feature
    importance extraction, artifact serialization, and best model export.
    """

    def __init__(self, config: Optional[BaselineConfig] = None):
        self.config = config or BaselineConfig()
        self.pipeline = NLPPreprocessingPipeline()
        self.evaluator = BaselineEvaluator(self.config.figures_output_dir)

    def instantiate_classifiers(self) -> Dict[str, Any]:
        """Instantiate standard baseline classifiers."""
        return {
            "multinomial_nb": MultinomialNB(alpha=1.0),
            "logistic_regression": LogisticRegression(
                C=1.0, max_iter=1000, random_state=self.config.random_state
            ),
            "linear_svm": CalibratedClassifierCV(
                estimator=LinearSVC(
                    C=1.0, random_state=self.config.random_state, dual="auto"
                )
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                random_state=self.config.random_state,
                n_jobs=-1,
            ),
        }

    def run_5fold_cv(
        self,
        clf: Any,
        vectorizer_type: str,
        train_texts: List[str],
        train_labels: List[int],
    ) -> Dict[str, float]:
        """Perform 5-Fold Stratified Cross-Validation."""
        skf = StratifiedKFold(
            n_splits=self.config.n_splits,
            shuffle=True,
            random_state=self.config.random_state,
        )
        acc_scores = []
        f1_scores = []

        X_array = np.array(train_texts)
        y_array = np.array(train_labels)

        for train_idx, val_idx in skf.split(X_array, y_array):
            X_tr, X_val = X_array[train_idx], X_array[val_idx]
            y_tr, y_val = y_array[train_idx], y_array[val_idx]

            # Fit vectorizer on fold train
            vec = NLPVectorizer(
                method=vectorizer_type,
                max_features=self.config.max_features,
                ngram_range=self.config.ngram_range,
                min_df=self.config.min_df,
            )
            X_tr_mat = vec.fit_transform(X_tr)
            X_val_mat = vec.transform(X_val)

            # Fit classifier clone
            clf_clone = clone(clf)
            clf_clone.fit(X_tr_mat, y_tr)
            preds = clf_clone.predict(X_val_mat)

            acc_scores.append(accuracy_score(y_val, preds))
            f1_scores.append(f1_score(y_val, preds, zero_division=0))

        return {
            "cv_mean_accuracy": round(float(np.mean(acc_scores)), 4),
            "cv_std_accuracy": round(float(np.std(acc_scores)), 4),
            "cv_mean_f1": round(float(np.mean(f1_scores)), 4),
            "cv_std_f1": round(float(np.std(f1_scores)), 4),
        }

    def train_and_evaluate_all(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Train and evaluate all 8 model/vectorizer combinations."""
        print("[Trainer] Preprocessing train, val, test datasets...")
        train_clean = [
            p["final_processed_text"]
            for p in self.pipeline.preprocess_corpus(
                train_df["text"].tolist()
            )
        ]
        test_clean = [
            p["final_processed_text"]
            for p in self.pipeline.preprocess_corpus(test_df["text"].tolist())
        ]

        y_train = train_df["label"].values
        y_test = test_df["label"].values

        experiment_results: List[Dict[str, Any]] = []

        for vec_type in self.config.vectorizer_types:
            print(
                f"\n[Trainer] Fitting {vec_type.upper()} Vectorizer on Train..."
            )
            vectorizer = NLPVectorizer(
                method=vec_type,
                max_features=self.config.max_features,
                ngram_range=self.config.ngram_range,
                min_df=self.config.min_df,
            )
            X_train_mat = vectorizer.fit_transform(train_clean)
            X_test_mat = vectorizer.transform(test_clean)
            feature_names = vectorizer.get_feature_names()

            classifiers = self.instantiate_classifiers()

            for model_name, clf in classifiers.items():
                exp_key = f"{model_name}_{vec_type}"
                print(f"  -> Training Model: {exp_key}...")

                # 5-Fold Stratified Cross Validation
                cv_stats = self.run_5fold_cv(
                    clf, vec_type, train_clean, y_train
                )

                # Fit on full training set
                t_start = time.perf_counter()
                clf.fit(X_train_mat, y_train)
                train_time_sec = time.perf_counter() - t_start

                # Predict on test set
                t_pred_start = time.perf_counter()
                y_pred = clf.predict(X_test_mat)
                pred_time_sec = time.perf_counter() - t_pred_start

                # Probability scores for ROC-AUC
                if hasattr(clf, "predict_proba"):
                    y_prob = clf.predict_proba(X_test_mat)[:, 1]
                elif hasattr(clf, "decision_function"):
                    y_prob = clf.decision_function(X_test_mat)
                else:
                    y_prob = y_pred.astype(float)

                # Save individual model artifact folder
                artifact_dir = self.config.models_output_dir / exp_key
                artifact_dir.mkdir(parents=True, exist_ok=True)

                model_file = artifact_dir / "model.joblib"
                vec_file = artifact_dir / "vectorizer.joblib"
                pipeline_file = artifact_dir / "pipeline.json"

                joblib.dump(clf, model_file)
                vectorizer.save(vec_file)
                self.pipeline.save_pipeline(pipeline_file)

                # Compute model file size in MB
                model_size_mb = model_file.stat().st_size / (1024 * 1024)

                # Compute 11 evaluation metrics
                metrics = self.evaluator.compute_all_metrics(
                    y_test,
                    y_pred,
                    y_prob,
                    train_time_sec,
                    pred_time_sec,
                    model_size_mb,
                )

                # Extract feature importances
                extracted_feat_imp = (
                    self.evaluator.extract_feature_importance(
                        clf.estimator if hasattr(clf, "estimator") else clf,
                        feature_names,
                        top_k=15,
                    )
                )

                metrics_file = artifact_dir / "metrics.json"
                with open(metrics_file, "w", encoding="utf-8") as f:
                    json.dump(
                        {"metrics": metrics, "cv_stats": cv_stats},
                        f,
                        indent=2,
                    )

                exp_record = {
                    "experiment_key": exp_key,
                    "model_name": model_name,
                    "vectorizer": vec_type,
                    "metrics": metrics,
                    "cv_stats": cv_stats,
                    "feature_importance": extracted_feat_imp,
                    "artifact_dir": str(artifact_dir),
                    "accuracy": metrics["accuracy"],
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1_score": metrics["f1_score"],
                    "roc_auc": metrics["roc_auc"],
                    "pr_auc": metrics["pr_auc"],
                    "mcc": metrics["mcc"],
                    "cohen_kappa": metrics["cohen_kappa"],
                    "training_time_seconds": metrics["training_time_seconds"],
                    "prediction_time_seconds": metrics[
                        "prediction_time_seconds"
                    ],
                    "model_size_mb": metrics["model_size_mb"],
                    "y_prob": y_prob,
                }
                experiment_results.append(exp_record)

        # 3. Best Model Selection & Export
        sorted_results = sorted(
            experiment_results, key=lambda r: r["f1_score"], reverse=True
        )
        best_model_record = sorted_results[0]
        print(
            f"\n[Trainer] [BEST] BEST CLASSICAL MODEL SELECTED: "
            f"{best_model_record['experiment_key']} "
            f"(F1={best_model_record['f1_score']:.4f})"
        )

        best_dir = self.config.best_model_dir
        best_dir.mkdir(parents=True, exist_ok=True)

        src_dir = Path(best_model_record["artifact_dir"])
        for fname in ["model.joblib", "vectorizer.joblib", "pipeline.json"]:
            if (src_dir / fname).exists():
                shutil.copy(src_dir / fname, best_dir / fname)

        best_meta = {
            "selected_best_model": best_model_record["experiment_key"],
            "model_name": best_model_record["model_name"],
            "vectorizer": best_model_record["vectorizer"],
            "metrics": best_model_record["metrics"],
            "cv_stats": best_model_record["cv_stats"],
            "export_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with open(best_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(best_meta, f, indent=2)

        # 4. Generate Figures
        print("[Trainer] Generating publication figures (300 DPI)...")
        _ = self.evaluator.generate_all_figures(experiment_results, y_test)

        return experiment_results, best_meta
