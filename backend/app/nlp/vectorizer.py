# ==============================================================================
# MindShield Backend — Vectorizer Module
# Phase 3.2: Extensible Feature Vectorization (CountVectorizer & TF-IDF)
# ==============================================================================

from abc import ABC, abstractmethod
import pickle
from pathlib import Path
from typing import Any, List, Optional, Union

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


class BaseVectorizer(ABC):
    """Abstract Base Class for NLP Text Vectorizers.

    Enables integration of n-gram vectorizers (Count, TF-IDF) and future
    dense neural word embeddings (Word2Vec, FastText, Transformer Embeddings).
    """

    @abstractmethod
    def fit(self, raw_documents: List[str]) -> "BaseVectorizer":
        """Fit vectorizer vocabulary on document corpus."""
        pass

    @abstractmethod
    def transform(self, raw_documents: List[str]) -> Any:
        """Transform documents into numerical feature matrix."""
        pass

    @abstractmethod
    def fit_transform(self, raw_documents: List[str]) -> Any:
        """Fit vocabulary and transform documents in one step."""
        pass

    @abstractmethod
    def get_feature_names_out(self) -> List[str]:
        """Return list of vocabulary feature names."""
        pass


class CountVectorizerWrapper(BaseVectorizer):
    """CountVectorizer wrapper for term frequency feature matrix generation."""

    def __init__(
        self,
        max_features: Optional[int] = 5000,
        ngram_range: tuple[int, int] = (1, 2),
        min_df: Union[int, float] = 2,
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.vectorizer = CountVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
        )

    def fit(self, raw_documents: List[str]) -> "CountVectorizerWrapper":
        """Fit vocabulary on raw documents."""
        self.vectorizer.fit(raw_documents)
        return self

    def transform(self, raw_documents: List[str]) -> Any:
        """Transform documents into count feature matrix."""
        return self.vectorizer.transform(raw_documents)

    def fit_transform(self, raw_documents: List[str]) -> Any:
        """Fit and transform documents in one step."""
        return self.vectorizer.fit_transform(raw_documents)

    def get_feature_names_out(self) -> List[str]:
        """Return feature names list."""
        return list(self.vectorizer.get_feature_names_out())


class TfidfVectorizerWrapper(BaseVectorizer):
    """TF-IDF Vectorizer wrapper for term frequency-IDF weighting."""

    def __init__(
        self,
        max_features: Optional[int] = 5000,
        ngram_range: tuple[int, int] = (1, 2),
        min_df: Union[int, float] = 2,
        sublinear_tf: bool = True,
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.sublinear_tf = sublinear_tf
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            sublinear_tf=self.sublinear_tf,
        )

    def fit(self, raw_documents: List[str]) -> "TfidfVectorizerWrapper":
        """Fit vocabulary on raw documents."""
        self.vectorizer.fit(raw_documents)
        return self

    def transform(self, raw_documents: List[str]) -> Any:
        """Transform documents into TF-IDF feature matrix."""
        return self.vectorizer.transform(raw_documents)

    def fit_transform(self, raw_documents: List[str]) -> Any:
        """Fit and transform documents in one step."""
        return self.vectorizer.fit_transform(raw_documents)

    def get_feature_names_out(self) -> List[str]:
        """Return feature names list."""
        return list(self.vectorizer.get_feature_names_out())


class NLPVectorizer:
    """Master Vectorizer manager.

    Provides unified creation, fitting, matrix export, and serialization
    across CountVectorizer and TfidfVectorizer backends.
    """

    def __init__(
        self,
        method: str = "tfidf",
        max_features: Optional[int] = 5000,
        ngram_range: tuple[int, int] = (1, 2),
        min_df: Union[int, float] = 2,
    ):
        self.method = method.lower()
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df

        if self.method == "count":
            self.vectorizer: BaseVectorizer = CountVectorizerWrapper(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
            )
        elif self.method == "tfidf":
            self.vectorizer: BaseVectorizer = TfidfVectorizerWrapper(
                max_features=self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
            )
        else:
            raise ValueError(
                f"Unsupported method '{method}'. Choose 'count' or 'tfidf'."
            )

        self.is_fitted = False

    def fit(self, raw_documents: List[str]) -> "NLPVectorizer":
        """Fit vectorizer on text documents."""
        self.vectorizer.fit(raw_documents)
        self.is_fitted = True
        return self

    def transform(self, raw_documents: List[str]) -> Any:
        """Transform text documents into sparse matrix."""
        if not self.is_fitted:
            raise RuntimeError(
                "Vectorizer must be fitted before transforming text."
            )
        return self.vectorizer.transform(raw_documents)

    def fit_transform(self, raw_documents: List[str]) -> Any:
        """Fit and transform text documents in a single call."""
        matrix = self.vectorizer.fit_transform(raw_documents)
        self.is_fitted = True
        return matrix

    def get_feature_names(self) -> List[str]:
        """Return vocabulary feature names."""
        if not self.is_fitted:
            return []
        return self.vectorizer.get_feature_names_out()

    def get_vocabulary_size(self) -> int:
        """Return count of vocabulary terms."""
        return len(self.get_feature_names())

    def save(self, filepath: Union[str, Path]) -> None:
        """Serialize fitted vectorizer instance to disk."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "NLPVectorizer":
        """Deserialize vectorizer instance from disk."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Vectorizer file not found: {filepath}")
        with open(filepath, "rb") as f:
            instance = pickle.load(f)
        return instance
