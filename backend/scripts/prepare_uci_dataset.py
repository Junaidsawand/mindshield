#!/usr/bin/env python3
# ==============================================================================
# MindShield Backend — UCI SMS Dataset Preparation CLI Runner
# Phase 3.1: UCI Dataset Preparation & Exploratory Data Analysis
# ==============================================================================

import argparse
import logging
import sys
from pathlib import Path

# Add backend root directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.config import UCI_SMS_CONFIG, DatasetConfig  # noqa: E402
from app.data.pipeline import GenericDataPipeline  # noqa: E402


def setup_logging(verbose: bool = False) -> None:
    """Configure terminal logging output."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """CLI entrypoint for UCI dataset preparation pipeline."""
    parser = argparse.ArgumentParser(
        description=(
            "MindShield Phase 3.1 — UCI SMS Dataset Preparation & EDA Pipeline"
        )
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Path to backend data storage directory (default: backend/data)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for 100% reproducible splitting (default: 42)",
    )
    parser.add_argument(
        "--val-size",
        type=float,
        default=0.10,
        help="Validation split ratio (default: 0.10)",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.10,
        help="Test split ratio (default: 0.10)",
    )
    parser.add_argument(
        "--force-redownload",
        action="store_true",
        help="Force redownloading raw dataset from UCI archive URL",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug logging"
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    train_size = 1.0 - (args.val_size + args.test_size)
    if train_size <= 0:
        print(f"Error: Invalid split ratios. Train size would be {train_size}")
        sys.exit(1)

    config = DatasetConfig(
        dataset_name=UCI_SMS_CONFIG.dataset_name,
        download_url=UCI_SMS_CONFIG.download_url,
        archive_filename=UCI_SMS_CONFIG.archive_filename,
        raw_filename=UCI_SMS_CONFIG.raw_filename,
        file_format=UCI_SMS_CONFIG.file_format,
        delimiter=UCI_SMS_CONFIG.delimiter,
        header=UCI_SMS_CONFIG.header,
        column_names=UCI_SMS_CONFIG.column_names,
        text_column=UCI_SMS_CONFIG.text_column,
        label_column=UCI_SMS_CONFIG.label_column,
        label_mapping=UCI_SMS_CONFIG.label_mapping,
        standard_label_names=UCI_SMS_CONFIG.standard_label_names,
        random_seed=args.seed,
        train_ratio=round(train_size, 4),
        val_ratio=args.val_size,
        test_ratio=args.test_size,
    )

    base_dir = Path(args.data_dir) if args.data_dir else None

    print("\n" + "=" * 80)
    print("  MINDSHIELD AI CYBERSECURITY — DATA ENGINEERING PIPELINE (PHASE 3.1)")
    print("=" * 80)
    print(f"  Target Dataset: {config.dataset_name}")
    print(f"  Random Seed:    {config.random_seed}")
    print(
        f"  Split Ratios:   Train={config.train_ratio*100:.1f}%, "
        f"Val={config.val_ratio*100:.1f}%, Test={config.test_ratio*100:.1f}%"
    )
    print("=" * 80 + "\n")

    pipeline = GenericDataPipeline(config, base_data_dir=base_dir)
    results = pipeline.run_pipeline(force_redownload=args.force_redownload)

    audit = results["deduplication_audit"]
    print("\n" + "=" * 80)
    print("  EXECUTION SUMMARY & VERIFICATION")
    print("=" * 80)
    print(f"  Raw Records Ingested:      {audit['initial_raw_records']:,}")
    print(f"  Exact Duplicates Removed: {audit['exact_duplicates_removed']:,}")
    print(f"  Final Cleaned Corpus:      {audit['final_cleaned_records']:,}")
    print("-" * 80)
    print("  SPLIT BREAKDOWN:")
    for split_name, summary in results["split_summaries"].items():
        print(
            f"    - {split_name.capitalize():<12}: "
            f"Total={summary['total_records']:,} | "
            f"Ham={summary['ham_count']:,} ({summary['ham_percentage']}%) | "
            f"Spam={summary['spam_count']:,} ({summary['spam_percentage']}%)"
        )
    print("-" * 80)
    print(
        f"  Publication Figures: {len(results['generated_figure_paths'])} "
        "saved to backend/data/figures/"
    )
    print(
        "  Metadata JSON:       Saved to "
        "backend/data/metadata/uci_sms_spam_metadata.json"
    )
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
