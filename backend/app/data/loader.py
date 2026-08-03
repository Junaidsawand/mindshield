# ==============================================================================
# MindShield Backend — Dataset Loader Engine
# Phase 3.1: Dataset-Agnostic File Ingestion
# ==============================================================================

import logging
from pathlib import Path

import pandas as pd
from app.data.config import DatasetConfig

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Config-driven raw dataset loader.

    Reads raw data files (TSV, CSV, JSON) according to specifications in DatasetConfig
    and standardizes raw column names into internal representation.
    """

    def __init__(self, config: DatasetConfig):
        """Initialize the dataset loader with configuration.

        Args:
            config: DatasetConfig instance.
        """
        self.config = config

    def load_raw_dataset(self, file_path: Path) -> pd.DataFrame:
        """Load raw dataset from file into pandas DataFrame.

        Args:
            file_path: Path to raw dataset file.

        Returns:
            pd.DataFrame: Loaded DataFrame with mapped column names.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Raw dataset file not found at: {file_path}")

        logger.info(
            f"Loading raw dataset '{self.config.dataset_name}' from: {file_path}"
        )

        try:
            if self.config.file_format.lower() == "json":
                df = pd.read_json(file_path, encoding=self.config.encoding)
            else:
                df = pd.read_csv(
                    file_path,
                    sep=self.config.delimiter,
                    header=self.config.header,
                    names=self.config.column_names,
                    on_bad_lines="skip",
                    encoding=self.config.encoding,
                    engine="python",
                )
        except Exception as err:
            logger.error(
                f"Failed to load dataset with pandas default parser: {err}. "
                "Attempting fallback line-by-line parser."
            )
            df = self._load_fallback_line_by_line(file_path)

        # Standardize column naming
        text_col = self.config.text_column
        lbl_col = self.config.label_column
        if text_col in df.columns and lbl_col in df.columns:
            df = df[[lbl_col, text_col]].copy()
            df.columns = ["raw_label", "text"]
        elif len(df.columns) >= 2:
            df = df.iloc[:, :2].copy()
            df.columns = ["raw_label", "text"]
        else:
            raise ValueError(
                f"Dataset at {file_path} must contain at least 2 columns. "
                f"Found columns: {list(df.columns)}"
            )

        logger.info(
            f"Successfully loaded {len(df)} raw records from {file_path.name}"
        )
        return df

    def _load_fallback_line_by_line(self, file_path: Path) -> pd.DataFrame:
        """Fallback parser for malformed TSV files with extra tab characters."""
        records = []
        with open(
            file_path, "r", encoding=self.config.encoding, errors="replace"
        ) as f:
            for _line_idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(self.config.delimiter, 1)
                if len(parts) == 2:
                    records.append(
                        {"raw_label": parts[0].strip(), "text": parts[1].strip()}
                    )
                elif len(parts) == 1:
                    records.append(
                        {"raw_label": "ham", "text": parts[0].strip()}
                    )

        if not records:
            raise ValueError(f"No valid records parsed from {file_path}")

        return pd.DataFrame(records)
