# ==============================================================================
# MindShield Backend — NLP Preprocessing Pipeline Orchestrator
# Phase 3.2: Reusable Pipeline, Metric Export & Serialization
# ==============================================================================

import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union

from app.nlp.comparer import StemmerLemmatizerComparer
from app.nlp.config import NLPPreprocessingConfig
from app.nlp.normalizer import TextNormalizer
from app.nlp.tokenizer import NLPTokenizer
from app.nlp.vectorizer import NLPVectorizer


class NLPPreprocessingPipeline:
    """Master orchestrator for NLP preprocessing.

    Unifies text normalization, tokenization, stemming/lemmatization,
    vectorization, metric comparison export, and pipeline serialization.
    """

    def __init__(
        self,
        config: Optional[NLPPreprocessingConfig] = None,
        vectorizer: Optional[NLPVectorizer] = None,
    ):
        self.config = config or NLPPreprocessingConfig.create_classical_config()
        self.normalizer = TextNormalizer(self.config)
        self.tokenizer = NLPTokenizer(self.config)
        self.comparer = StemmerLemmatizerComparer()
        self.vectorizer = vectorizer

    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """Preprocess single text message payload."""
        # 1. Normalization
        normalized = self.normalizer.normalize(text)

        # 2. Tokenization & Stopword Removal
        tokens = self.tokenizer.tokenize(normalized)
        filtered_tokens = self.tokenizer.filter_stopwords(tokens)

        # 3. Optional Stemming / Lemmatization
        stemmed_tokens = [self.comparer.stem_token(t) for t in filtered_tokens]
        lemmatized_tokens = [
            self.comparer.lemmatize_token(t) for t in filtered_tokens
        ]

        # Select final output token stream based on config
        if self.config.stemmer == "porter":
            final_tokens = stemmed_tokens
        elif self.config.lemmatizer == "wordnet":
            final_tokens = lemmatized_tokens
        else:
            final_tokens = filtered_tokens

        final_processed_text = " ".join(final_tokens)

        return {
            "raw_text": text,
            "normalized_text": normalized,
            "tokens": tokens,
            "filtered_tokens": filtered_tokens,
            "stemmed_tokens": stemmed_tokens,
            "lemmatized_tokens": lemmatized_tokens,
            "final_processed_text": final_processed_text,
            "char_length": len(normalized),
            "word_count": len(final_tokens),
        }

    def preprocess_corpus(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Preprocess list of text messages."""
        return [self.preprocess_text(t) for t in texts]

    def generate_comparison_metrics(
        self,
        raw_texts: List[str],
        export_path: Optional[Union[str, Path]] = None,
    ) -> Dict[str, Any]:
        """Generate comprehensive metrics and export JSON file."""
        start_time = time.perf_counter()

        raw_tokens_list: List[List[str]] = []
        normalized_texts: List[str] = []

        for text in raw_texts:
            norm = self.normalizer.normalize(text)
            normalized_texts.append(norm)
            toks = self.tokenizer.tokenize(norm)
            raw_tokens_list.append(toks)

        # Statistical comparisons
        eda_stats = self.comparer.analyze_corpus(raw_tokens_list)
        elapsed_sec = round(time.perf_counter() - start_time, 4)

        raw_char_lens = [len(str(t)) for t in raw_texts]
        norm_char_lens = [len(str(t)) for t in normalized_texts]

        metrics = {
            "pipeline_name": "MindShield NLP Preprocessing Pipeline",
            "pipeline_version": "3.2.0",
            "mode": "classical" if self.config.lowercase else "transformer",
            "total_documents_processed": len(raw_texts),
            "vocabulary_size_before": eda_stats["raw_vocabulary_size"],
            "vocabulary_size_after": eda_stats["stemmed_vocabulary_size"],
            "token_count_statistics": {
                "total_raw_tokens": eda_stats["total_token_count"],
                "unique_raw_tokens": eda_stats["raw_vocabulary_size"],
                "unique_stemmed_tokens": eda_stats[
                    "stemmed_vocabulary_size"
                ],
                "unique_lemmatized_tokens": eda_stats[
                    "lemmatized_vocabulary_size"
                ],
            },
            "average_message_length": {
                "raw_character_length_mean": round(
                    sum(raw_char_lens) / max(len(raw_char_lens), 1), 2
                ),
                "normalized_character_length_mean": round(
                    sum(norm_char_lens) / max(len(norm_char_lens), 1), 2
                ),
            },
            "vocabulary_reduction_metrics": {
                "stemming_vocabulary_reduction_percent": eda_stats[
                    "stemming_vocabulary_reduction_percent"
                ],
                "lemmatization_vocabulary_reduction_percent": eda_stats[
                    "lemmatization_vocabulary_reduction_percent"
                ],
            },
            "processing_performance": {
                "total_processing_time_seconds": elapsed_sec,
                "throughput_documents_per_second": round(
                    len(raw_texts) / max(elapsed_sec, 0.0001), 2
                ),
            },
            "oov_statistics": eda_stats["oov_statistics"],
            "configuration": self.config.to_dict(),
        }

        if export_path:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(metrics, f, indent=2)

        return metrics

    def save_pipeline(self, filepath: Union[str, Path]) -> None:
        """Export pipeline configuration JSON artifact."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        artifact = {
            "config": self.config.to_dict(),
            "pipeline_version": "3.2.0",
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(artifact, f, indent=2)

    @classmethod
    def load_pipeline(
        cls, filepath: Union[str, Path]
    ) -> "NLPPreprocessingPipeline":
        """Load pipeline instance from configuration JSON artifact."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Pipeline config file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            artifact = json.load(f)
        config = NLPPreprocessingConfig.from_dict(artifact["config"])
        return cls(config=config)
