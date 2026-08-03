# ==============================================================================
# MindShield Backend — Stemmer & Lemmatizer Comparer Module
# Phase 3.2: Vocabulary Reduction & Morphological Feature Evaluation
# ==============================================================================

import time
from typing import Any, Dict, List

try:
    import nltk
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    NLTK_AVAILABLE = True
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        try:
            nltk.download("wordnet", quiet=True)
            nltk.download("omw-1.4", quiet=True)
        except Exception:
            pass
except ImportError:
    NLTK_AVAILABLE = False


class LightweightPorterStemmer:
    """Rule-based suffix stripping fallback when NLTK is absent."""

    SUFFIXES = ["ing", "ed", "es", "s", "ment", "ness", "able", "ible", "ly"]

    def stem(self, word: str) -> str:
        """Strip common suffixes from word."""
        word = word.lower()
        if len(word) <= 3:
            return word
        for suf in self.SUFFIXES:
            if word.endswith(suf) and len(word) - len(suf) >= 3:
                return word[: -len(suf)]
        return word


class LightweightLemmatizer:
    """Rule-based lemmatizer fallback when NLTK wordnet is absent."""

    LEMMA_RULES = {
        "running": "run", "runs": "run", "ran": "run",
        "winning": "win", "wins": "win", "won": "win",
        "claiming": "claim", "claims": "claim", "claimed": "claim",
        "prizes": "prize", "messages": "message", "calling": "call",
        "called": "call", "urgent": "urgent", "freemsg": "freemsg",
    }

    def lemmatize(self, word: str, pos: str = "v") -> str:
        """Map word to base lemma."""
        word = word.lower()
        return self.LEMMA_RULES.get(word, word)


class StemmerLemmatizerComparer:
    """Analyzer evaluating Stemming vs Lemmatization vs Raw tokenization."""

    def __init__(self):
        if NLTK_AVAILABLE:
            try:
                self.stemmer = PorterStemmer()
                self.lemmatizer = WordNetLemmatizer()
            except Exception:
                self.stemmer = LightweightPorterStemmer()
                self.lemmatizer = LightweightLemmatizer()
        else:
            self.stemmer = LightweightPorterStemmer()
            self.lemmatizer = LightweightLemmatizer()

    def stem_token(self, token: str) -> str:
        """Stem single word token."""
        return self.stemmer.stem(token.lower())

    def lemmatize_token(self, token: str) -> str:
        """Lemmatize single word token."""
        if hasattr(self.lemmatizer, "lemmatize"):
            try:
                return self.lemmatizer.lemmatize(token.lower(), pos="v")
            except Exception:
                return token.lower()
        return token.lower()

    def analyze_corpus(self, tokenized_docs: List[List[str]]) -> Dict[str, Any]:
        """Compute metrics across Raw, Stemmed, and Lemmatized tokens."""
        start_time = time.perf_counter()

        raw_all_tokens: List[str] = []
        stemmed_all_tokens: List[str] = []
        lemmatized_all_tokens: List[str] = []

        for doc in tokenized_docs:
            for token in doc:
                t_lower = token.lower()
                raw_all_tokens.append(t_lower)
                stemmed_all_tokens.append(self.stem_token(t_lower))
                lemmatized_all_tokens.append(self.lemmatize_token(t_lower))

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        raw_vocab = set(raw_all_tokens)
        stemmed_vocab = set(stemmed_all_tokens)
        lemmatized_vocab = set(lemmatized_all_tokens)

        raw_size = len(raw_vocab)
        stemmed_size = len(stemmed_vocab)
        lemmatized_size = len(lemmatized_vocab)

        stemmed_reduction = (
            round((raw_size - stemmed_size) / raw_size * 100, 2)
            if raw_size > 0 else 0.0
        )
        lemmatized_reduction = (
            round((raw_size - lemmatized_size) / raw_size * 100, 2)
            if raw_size > 0 else 0.0
        )

        avg_len_raw = (
            round(sum(len(t) for t in raw_all_tokens) / len(raw_all_tokens), 2)
            if raw_all_tokens else 0.0
        )
        avg_len_stem = (
            round(
                sum(len(t) for t in stemmed_all_tokens)
                / len(stemmed_all_tokens),
                2,
            )
            if stemmed_all_tokens else 0.0
        )
        avg_len_lemma = (
            round(
                sum(len(t) for t in lemmatized_all_tokens)
                / len(lemmatized_all_tokens),
                2,
            )
            if lemmatized_all_tokens else 0.0
        )

        return {
            "total_documents": len(tokenized_docs),
            "total_token_count": len(raw_all_tokens),
            "raw_vocabulary_size": raw_size,
            "stemmed_vocabulary_size": stemmed_size,
            "lemmatized_vocabulary_size": lemmatized_size,
            "stemming_vocabulary_reduction_percent": stemmed_reduction,
            "lemmatization_vocabulary_reduction_percent": lemmatized_reduction,
            "average_token_length": {
                "raw": avg_len_raw,
                "stemmed": avg_len_stem,
                "lemmatized": avg_len_lemma,
            },
            "processing_time_ms": elapsed_ms,
            "oov_statistics": {
                "stemming_collapsed_terms": raw_size - stemmed_size,
                "lemmatization_collapsed_terms": raw_size - lemmatized_size,
            },
        }
