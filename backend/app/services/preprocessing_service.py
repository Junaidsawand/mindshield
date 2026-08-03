# ==============================================================================
# MindShield Backend — NLP Preprocessing Service Layer
# Phase 3.2: High-Level Reusable Service Layer for API & Training Pipelines
# ==============================================================================

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from app.nlp.config import NLPPreprocessingConfig
from app.nlp.pipeline import NLPPreprocessingPipeline
from app.nlp.vectorizer import NLPVectorizer


class PreprocessingService:
    """Production service wrapping classical and transformer preprocessing pipelines."""

    def __init__(self):
        self.classical_pipeline = NLPPreprocessingPipeline(
            NLPPreprocessingConfig.create_classical_config()
        )
        self.transformer_pipeline = NLPPreprocessingPipeline(
            NLPPreprocessingConfig.create_transformer_config()
        )

    def preprocess_single_message(
        self, text: str, mode: str = "classical"
    ) -> Dict[str, Any]:
        """Preprocess single text payload under classical or transformer mode."""
        if mode == "transformer":
            return self.transformer_pipeline.preprocess_text(text)
        return self.classical_pipeline.preprocess_text(text)

    def preprocess_batch_messages(
        self, texts: List[str], mode: str = "classical"
    ) -> List[Dict[str, Any]]:
        """Preprocess batch of text payloads under classical or transformer mode."""
        if mode == "transformer":
            return self.transformer_pipeline.preprocess_corpus(texts)
        return self.classical_pipeline.preprocess_corpus(texts)

    def vectorize_corpus(
        self,
        texts: List[str],
        method: str = "tfidf",
        max_features: int = 5000,
        ngram_range: tuple[int, int] = (1, 2),
    ) -> Tuple[Any, NLPVectorizer]:
        """Vectorize cleaned text corpus into numerical matrix."""
        # 1. Clean corpus using classical pipeline
        processed = [
            p["final_processed_text"]
            for p in self.classical_pipeline.preprocess_corpus(texts)
        ]

        # 2. Fit and transform using vectorizer
        vectorizer = NLPVectorizer(
            method=method, max_features=max_features, ngram_range=ngram_range
        )
        feature_matrix = vectorizer.fit_transform(processed)
        return feature_matrix, vectorizer

    def generate_and_export_comparison_metrics(
        self, raw_texts: List[str], export_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """Generate and export preprocessing comparison metrics."""
        return self.classical_pipeline.generate_comparison_metrics(
            raw_texts, export_path=export_path
        )


# Global singleton instance
_preprocessing_service_instance: Optional[PreprocessingService] = None


def get_preprocessing_service() -> PreprocessingService:
    """Return singleton instance of PreprocessingService."""
    global _preprocessing_service_instance
    if _preprocessing_service_instance is None:
        _preprocessing_service_instance = PreprocessingService()
    return _preprocessing_service_instance
