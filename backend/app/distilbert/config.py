# ==============================================================================
# MindShield Backend — DistilBERT Fine-Tuning Configuration Module
# Phase 3.4: Declarative Configuration for Transformer Fine-Tuning & Evaluation
# ==============================================================================

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict

import torch


@dataclass
class DistilBERTConfig:
    """Declarative configuration model for DistilBERT fine-tuning and evaluation."""

    # --- Transformer Model Settings ---
    model_name: str = "distilbert-base-uncased"
    num_labels: int = 2
    max_length: int = 64

    # --- Training Hyper-parameters ---
    batch_size: int = 32
    learning_rate: float = 2e-5
    epochs: int = 1
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    seed: int = 42
    patience: int = 2  # Early stopping patience

    # --- Hardware & Acceleration ---
    use_gpu: bool = field(default_factory=lambda: torch.cuda.is_available())
    use_fp16: bool = field(default_factory=lambda: torch.cuda.is_available())
    device: str = field(
        default_factory=lambda: "cuda" if torch.cuda.is_available() else "cpu"
    )

    # --- Directories ---
    processed_data_dir: Path = Path("data/processed")
    models_output_dir: Path = Path("data/models/distilbert")
    metadata_output_dir: Path = Path("data/metadata")
    figures_output_dir: Path = Path("data/figures")

    # --- Label Mappings ---
    id2label: Dict[int, str] = field(
        default_factory=lambda: {0: "ham", 1: "spam"}
    )
    label2id: Dict[str, int] = field(
        default_factory=lambda: {"ham": 0, "spam": 1}
    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to dictionary."""
        data = asdict(self)
        data["processed_data_dir"] = str(self.processed_data_dir)
        data["models_output_dir"] = str(self.models_output_dir)
        data["metadata_output_dir"] = str(self.metadata_output_dir)
        data["figures_output_dir"] = str(self.figures_output_dir)
        return data
