# ==============================================================================
# MindShield Backend — Baseline ML Configuration Module
# Phase 3.3: Declarative Configuration for Classical Machine Learning Baselines
# ==============================================================================

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class BaselineConfig:
    """Declarative configuration model for Classical Machine Learning baselines."""

    # --- Feature Extraction Settings ---
    vectorizer_types: List[str] = field(
        default_factory=lambda: ["tfidf", "count"]
    )
    max_features: int = 5000
    ngram_range: tuple[int, int] = (1, 2)
    min_df: int = 2

    # --- Cross-Validation Settings ---
    n_splits: int = 5
    random_state: int = 42

    # --- Directory Paths (Relative to Backend Root) ---
    processed_data_dir: Path = Path("data/processed")
    models_output_dir: Path = Path("data/models/baselines")
    best_model_dir: Path = Path("data/models/best_classical_model")
    metadata_output_dir: Path = Path("data/metadata")
    figures_output_dir: Path = Path("data/figures")

    # --- Primary Metric for Best Model Selection ---
    primary_metric: str = "f1_score"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to dictionary."""
        data = asdict(self)
        data["processed_data_dir"] = str(self.processed_data_dir)
        data["models_output_dir"] = str(self.models_output_dir)
        data["best_model_dir"] = str(self.best_model_dir)
        data["metadata_output_dir"] = str(self.metadata_output_dir)
        data["figures_output_dir"] = str(self.figures_output_dir)
        return data
