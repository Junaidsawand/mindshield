# ==============================================================================
# MindShield Backend — Data Engineering Pipeline Configuration
# Phase 3.1: Dataset-Agnostic & Model-Compatible Configuration Engine
# ==============================================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DatasetConfig:
    """Dataset-agnostic configuration container for data pipeline execution.

    Decouples preprocessing, cleaning, EDA, visualization, and splitting logic
    from specific dataset formats, enabling seamless reusability across datasets
    (e.g., UCI SMS Spam Collection, PakScam).
    """

    dataset_name: str
    download_url: str
    archive_filename: str
    raw_filename: str
    file_format: str = "tsv"  # "tsv", "csv", "json", "txt"
    delimiter: str = "\t"
    header: Optional[int] = None  # None for headerless TSV
    column_names: List[str] = field(default_factory=lambda: ["raw_label", "text"])
    text_column: str = "text"
    label_column: str = "raw_label"
    label_mapping: Dict[str, int] = field(
        default_factory=lambda: {"ham": 0, "spam": 1}
    )
    standard_label_names: Dict[int, str] = field(
        default_factory=lambda: {0: "ham", 1: "spam"}
    )
    random_seed: int = 42
    train_ratio: float = 0.80
    val_ratio: float = 0.10
    test_ratio: float = 0.10
    encoding: str = "utf-8"

    def validate(self) -> None:
        """Validate configuration parameters for consistency."""
        if not (0.0 < self.train_ratio < 1.0):
            raise ValueError(f"Invalid train_ratio: {self.train_ratio}")
        if not (0.0 <= self.val_ratio < 1.0):
            raise ValueError(f"Invalid val_ratio: {self.val_ratio}")
        if not (0.0 <= self.test_ratio < 1.0):
            raise ValueError(f"Invalid test_ratio: {self.test_ratio}")
        total = round(self.train_ratio + self.val_ratio + self.test_ratio, 4)
        if total != 1.0:
            raise ValueError(
                f"Split ratios must sum to 1.0 (got {total}: "
                f"train={self.train_ratio}, val={self.val_ratio}, "
                f"test={self.test_ratio})"
            )


# ==============================================================================
# Pre-Configured Dataset Definitions
# ==============================================================================

# UCI SMS Spam Collection Dataset Configuration
UCI_SMS_CONFIG = DatasetConfig(
    dataset_name="uci_sms_spam",
    download_url=(
        "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
    ),
    archive_filename="sms_spam_collection.zip",
    raw_filename="SMSSpamCollection",
    file_format="tsv",
    delimiter="\t",
    header=None,
    column_names=["raw_label", "text"],
    text_column="text",
    label_column="raw_label",
    label_mapping={"ham": 0, "spam": 1},
    standard_label_names={0: "ham", 1: "spam"},
    random_seed=42,
    train_ratio=0.80,
    val_ratio=0.10,
    test_ratio=0.10,
    encoding="utf-8",
)

# PakScam Dataset Template Configuration (For Future Integration)
PAKSCAM_CONFIG_TEMPLATE = DatasetConfig(
    dataset_name="pakscam_v1",
    download_url="",  # Local or threat intelligence feed repository URL
    archive_filename="pakscam_dataset.zip",
    raw_filename="pakscam_messages.csv",
    file_format="csv",
    delimiter=",",
    header=0,
    column_names=["message_id", "text", "category", "timestamp"],
    text_column="text",
    label_column="category",
    label_mapping={"safe": 0, "ham": 0, "phishing": 1, "smishing": 1, "spam": 1},
    standard_label_names={0: "ham", 1: "spam"},
    random_seed=42,
    train_ratio=0.80,
    val_ratio=0.10,
    test_ratio=0.10,
    encoding="utf-8",
)
