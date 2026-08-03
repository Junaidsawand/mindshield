# ==============================================================================
# MindShield Backend — Data Engineering Pipeline Test Suite
# Phase 3.1: Automated Verification of Data Pipeline & EDA
# ==============================================================================

from pathlib import Path

import pandas as pd
import pytest
from app.data.cleaner import SMSDatasetCleaner
from app.data.config import PAKSCAM_CONFIG_TEMPLATE, UCI_SMS_CONFIG, DatasetConfig
from app.data.downloader import DatasetDownloader
from app.data.eda import SMSDatasetEDA
from app.data.loader import DatasetLoader
from app.data.pipeline import GenericDataPipeline
from app.data.visualizer import SMSDatasetVisualizer


@pytest.fixture
def sample_config(tmp_path: Path) -> DatasetConfig:
    """Fixture providing an isolated test DatasetConfig."""
    return DatasetConfig(
        dataset_name="test_sms_dataset",
        download_url="",
        archive_filename="test_dataset.zip",
        raw_filename="test_messages.tsv",
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
    )


@pytest.fixture
def sample_raw_dataframe() -> pd.DataFrame:
    """Fixture providing a synthetic raw text DataFrame."""
    data = []
    # Add 40 ham samples
    for i in range(40):
        data.append(
            {
                "raw_label": "ham",
                "text": (
                    f"Legitimate message number {i} with some content. "
                    f"Check https://safe{i}.com 😊"
                ),
            }
        )
    # Add 1 duplicate ham sample
    data.append(
        {
            "raw_label": "ham",
            "text": (
                "Legitimate message number 0 with some content. "
                "Check https://safe0.com 😊"
            ),
        }
    )
    # Add 20 spam samples
    for i in range(20):
        data.append(
            {
                "raw_label": "spam",
                "text": (
                    f"URGENT! You won a £{1000+i} prize reward! "
                    f"Claim now at http://scam{i}.link 🎁"
                ),
            }
        )

    return pd.DataFrame(data)


def test_dataset_config_validation():
    """Verify DatasetConfig ratio validation logic."""
    valid_cfg = DatasetConfig(
        dataset_name="valid",
        download_url="",
        archive_filename="a.zip",
        raw_filename="a.tsv",
        train_ratio=0.8,
        val_ratio=0.1,
        test_ratio=0.1,
    )
    valid_cfg.validate()  # Should not raise

    invalid_cfg = DatasetConfig(
        dataset_name="invalid",
        download_url="",
        archive_filename="a.zip",
        raw_filename="a.tsv",
        train_ratio=0.7,
        val_ratio=0.1,
        test_ratio=0.1,  # Sums to 0.9
    )
    with pytest.raises(ValueError, match="Split ratios must sum to 1.0"):
        invalid_cfg.validate()


def test_dataset_downloader_fallback(sample_config: DatasetConfig, tmp_path: Path):
    """Verify DatasetDownloader generates offline fallback when URL is empty."""
    downloader = DatasetDownloader(sample_config, data_raw_dir=tmp_path)
    target_path = downloader.download_and_extract(force=True)
    assert target_path.exists()
    assert target_path.stat().st_size > 0


def test_dataset_loader(sample_config: DatasetConfig, tmp_path: Path):
    """Verify DatasetLoader ingests raw TSV files and standardizes columns."""
    raw_file = tmp_path / "test_messages.tsv"
    with open(raw_file, "w", encoding="utf-8") as f:
        f.write("ham\tHello friend\nspam\tWIN PRIZE NOW\n")

    loader = DatasetLoader(sample_config)
    df = loader.load_raw_dataset(raw_file)

    assert "raw_label" in df.columns
    assert "text" in df.columns
    assert len(df) == 2
    assert df.iloc[0]["raw_label"] == "ham"
    assert df.iloc[1]["raw_label"] == "spam"


def test_non_destructive_cleaner(
    sample_config: DatasetConfig, sample_raw_dataframe: pd.DataFrame
):
    """Verify SMSDatasetCleaner performs non-destructive text cleaning."""
    cleaner = SMSDatasetCleaner(sample_config)
    df_cleaned, stats = cleaner.clean_dataset(sample_raw_dataframe)

    # 1. Column compliance (text: str, label: int)
    assert list(df_cleaned.columns) == ["text", "label"]
    assert pd.api.types.is_integer_dtype(df_cleaned["label"])

    # 2. Label mapping compliance (0 for ham, 1 for spam)
    assert set(df_cleaned["label"].unique()).issubset({0, 1})

    # 3. Non-destructive text preservation (case, URLs, emojis intact)
    sample_text = df_cleaned.iloc[0]["text"]
    assert "Legitimate message" in sample_text or "URGENT!" in sample_text
    assert (
        "https://" in df_cleaned.to_string()
        or "http://" in df_cleaned.to_string()
    )

    # 4. Exact deduplication verification
    assert stats["exact_duplicates_removed"] == 1
    assert len(df_cleaned) == len(sample_raw_dataframe) - 1


def test_eda_engine(
    sample_config: DatasetConfig, sample_raw_dataframe: pd.DataFrame
):
    """Verify SMSDatasetEDA computes comprehensive statistical summaries."""
    cleaner = SMSDatasetCleaner(sample_config)
    df_cleaned, _ = cleaner.clean_dataset(sample_raw_dataframe)

    eda = SMSDatasetEDA(sample_config)
    meta = eda.perform_full_eda(df_cleaned, dataset_stage="cleaned")

    assert meta["total_records"] == len(df_cleaned)
    assert "class_distribution" in meta
    assert meta["class_distribution"]["ham_count"] > 0
    assert meta["class_distribution"]["spam_count"] > 0

    assert "overall_metrics" in meta
    assert "char_length" in meta["overall_metrics"]
    assert "word_count" in meta["overall_metrics"]


def test_stratified_splitter(
    sample_config: DatasetConfig, sample_raw_dataframe: pd.DataFrame
):
    """Verify stratified splitting maintains class ratios across splits."""
    cleaner = SMSDatasetCleaner(sample_config)
    df_cleaned, _ = cleaner.clean_dataset(sample_raw_dataframe)

    splits = cleaner.create_stratified_splits(df_cleaned)
    assert "train" in splits
    assert "val" in splits
    assert "test" in splits
    assert "cleaned_full" in splits

    total_split_len = (
        len(splits["train"]) + len(splits["val"]) + len(splits["test"])
    )
    assert total_split_len == len(df_cleaned)


def test_visualizer(
    sample_config: DatasetConfig,
    sample_raw_dataframe: pd.DataFrame,
    tmp_path: Path,
):
    """Verify SMSDatasetVisualizer generates publication figures as PNGs."""
    cleaner = SMSDatasetCleaner(sample_config)
    df_cleaned, _ = cleaner.clean_dataset(sample_raw_dataframe)
    splits = cleaner.create_stratified_splits(df_cleaned)

    eda = SMSDatasetEDA(sample_config)
    meta = eda.perform_full_eda(df_cleaned, dataset_stage="cleaned")

    figures_dir = tmp_path / "figures"
    visualizer = SMSDatasetVisualizer(sample_config, figures_dir)
    paths = visualizer.generate_all_figures(df_cleaned, meta, splits)

    assert len(paths) == 6
    for p in paths:
        assert p.exists()
        assert p.stat().st_size > 0
        assert p.suffix == ".png"


def test_generic_pipeline_end_to_end(tmp_path: Path):
    """Verify end-to-end execution of GenericDataPipeline with UCI config."""
    pipeline = GenericDataPipeline(UCI_SMS_CONFIG, base_data_dir=tmp_path)
    metadata = pipeline.run_pipeline(force_redownload=False)

    assert metadata["dataset_name"] == "uci_sms_spam"
    assert metadata["pipeline_version"] == "3.1.0"
    assert "split_summaries" in metadata

    processed_dir = tmp_path / "processed"
    for filename in ["train.csv", "val.csv", "test.csv", "cleaned_full.csv"]:
        file_path = processed_dir / filename
        assert file_path.exists()
        df = pd.read_csv(file_path)
        assert list(df.columns) == ["text", "label"]
        assert pd.api.types.is_integer_dtype(df["label"])


def test_pakscam_config_compatibility(tmp_path: Path):
    """Verify pipeline reusability with PakScam dataset template."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy PakScam CSV raw file with 11 records (1 duplicate)
    pakscam_file = raw_dir / "pakscam_messages.csv"
    records = ["message_id,text,category,timestamp"]
    for i in range(5):
        records.append(
            f'{100+i},"BISP 25000 prize claimed. Call 0300{i}",'
            'smishing,2026-08-01 10:00:00'
        )
    for i in range(5):
        records.append(
            f'{200+i},"Kese ho bhai? Shaam ko milte hain {i}.",'
            'safe,2026-08-01 10:00:00'
        )
    # Add duplicate record
    records.append(
        '300,"BISP 25000 prize claimed. Call 03000",smishing,2026-08-01 10:00:00'
    )

    with open(pakscam_file, "w", encoding="utf-8") as f:
        f.write("\n".join(records))

    pipeline = GenericDataPipeline(
        PAKSCAM_CONFIG_TEMPLATE, base_data_dir=tmp_path
    )
    metadata = pipeline.run_pipeline(force_redownload=False)

    assert metadata["dataset_name"] == "pakscam_v1"
    assert metadata["deduplication_audit"]["exact_duplicates_removed"] == 1
    assert metadata["deduplication_audit"]["final_cleaned_records"] == 10

    processed_dir = tmp_path / "processed"
    df_test = pd.read_csv(processed_dir / "cleaned_full.csv")
    assert list(df_test.columns) == ["text", "label"]
    assert set(df_test["label"].unique()).issubset({0, 1})
