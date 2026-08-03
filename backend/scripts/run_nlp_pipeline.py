# ==============================================================================
# MindShield Backend — NLP Preprocessing CLI Pipeline Runner
# Phase 3.2: CLI Execution, Feature Extraction & Comparison Export
# ==============================================================================

from pathlib import Path

import pandas as pd
from app.services.preprocessing_service import get_preprocessing_service


def run_pipeline():
    """Execute complete Phase 3.2 NLP Preprocessing Pipeline."""
    print("=" * 80)
    print("  MINDSHIELD AI CYBERSECURITY — PHASE 3.2 NLP PREPROCESSING  ")
    print("=" * 80)

    backend_dir = Path(__file__).resolve().parents[1]
    data_dir = backend_dir / "data"
    cleaned_csv = data_dir / "processed" / "cleaned_full.csv"
    raw_tsv = data_dir / "raw" / "SMSSpamCollection"

    if cleaned_csv.exists():
        print(f"[1/5] Ingesting cleaned corpus from {cleaned_csv}...")
        df = pd.read_csv(cleaned_csv)
    elif raw_tsv.exists():
        print(f"[1/5] Ingesting raw corpus from {raw_tsv}...")
        df = pd.read_csv(
            raw_tsv, sep="\t", header=None, names=["raw_label", "text"]
        )
    else:
        print("[1/5] Creating synthetic sample corpus for verification...")
        df = pd.DataFrame({
            "text": [
                "URGENT! Claim £1000 cash prize at http://scam.link 🎁",
                "Hi mom, I will be home by 7pm tonight.",
                "Call 0800111222 for free credit update. Reply OTP 123456.",
            ],
            "label": [1, 0, 1],
        })

    raw_texts = df["text"].dropna().tolist()
    print(f"      Total Input Documents: {len(raw_texts):,}")

    svc = get_preprocessing_service()

    # Step 2: Generate Comparison Metrics
    metrics_path = data_dir / "metadata" / "preprocessing_comparison.json"
    print(f"[2/5] Generating metrics -> {metrics_path}...")
    metrics = svc.generate_and_export_comparison_metrics(
        raw_texts, export_path=metrics_path
    )

    # Step 3: Fit Vectorizers
    print("[3/5] Fitting CountVectorizer and TF-IDF Vectorizers...")
    count_matrix, count_vec = svc.vectorize_corpus(
        raw_texts, method="count", max_features=5000
    )
    tfidf_matrix, tfidf_vec = svc.vectorize_corpus(
        raw_texts, method="tfidf", max_features=5000
    )

    print(
        f"      CountVectorizer shape: {count_matrix.shape} "
        f"(Vocabulary: {count_vec.get_vocabulary_size():,} terms)"
    )
    print(
        f"      TfidfVectorizer shape: {tfidf_matrix.shape} "
        f"(Vocabulary: {tfidf_vec.get_vocabulary_size():,} terms)"
    )

    # Step 4: Save Pipeline Serialization Config
    config_export_path = data_dir / "metadata" / "nlp_pipeline_config.json"
    print(f"[4/5] Exporting config artifact -> {config_export_path}...")
    svc.classical_pipeline.save_pipeline(config_export_path)

    # Step 5: Summary Report
    r_red = metrics["vocabulary_reduction_metrics"][
        "stemming_vocabulary_reduction_percent"
    ]
    l_red = metrics["vocabulary_reduction_metrics"][
        "lemmatization_vocabulary_reduction_percent"
    ]
    t_sec = metrics["processing_performance"][
        "total_processing_time_seconds"
    ]
    t_put = metrics["processing_performance"][
        "throughput_documents_per_second"
    ]

    print("[5/5] PREPROCESSING PIPELINE AUDIT SUMMARY:")
    print(
        f"    - Raw Vocabulary Size      : "
        f"{metrics['vocabulary_size_before']:,} unique terms"
    )
    print(
        f"    - Stemmed Vocabulary Size  : "
        f"{metrics['vocabulary_size_after']:,} unique terms"
    )
    print(f"    - Stemming Reduction       : {r_red}%")
    print(f"    - Lemmatization Reduction  : {l_red}%")
    print(f"    - Total Processing Time    : {t_sec} sec")
    print(f"    - Processing Throughput    : {t_put} docs/sec")
    print("=" * 80)
    print("[OK] Phase 3.2 NLP Preprocessing Pipeline execution finished successfully.")


if __name__ == "__main__":
    run_pipeline()
