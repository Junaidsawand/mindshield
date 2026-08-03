# ==============================================================================
# MindShield Backend — NLP Tokenizer Module
# Phase 3.2: Word Tokenization & Stopword Removal Engine
# ==============================================================================

import re
from typing import List, Optional, Set

from app.nlp.config import NLPPreprocessingConfig

DEFAULT_ENGLISH_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
    "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its",
    "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
    "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves", "ur", "u", "2", "4"
}


class NLPTokenizer:
    """Word tokenizer with regex boundary splitting and stopword filtering."""

    TOKEN_PATTERN = re.compile(r"\b[a-zA-Z0-9'\[\]_:]+\b")

    def __init__(
        self,
        config: Optional[NLPPreprocessingConfig] = None,
        custom_stopwords: Optional[Set[str]] = None,
    ):
        self.config = config or NLPPreprocessingConfig()
        self.stopwords = set(DEFAULT_ENGLISH_STOPWORDS)
        if custom_stopwords:
            self.stopwords.update(custom_stopwords)
        if self.config.custom_stopwords:
            self.stopwords.update(self.config.custom_stopwords)

    def tokenize(self, text: str) -> List[str]:
        """Extract word tokens matching boundary pattern."""
        if not text:
            return []
        return self.TOKEN_PATTERN.findall(text)

    def filter_stopwords(self, tokens: List[str]) -> List[str]:
        """Filter out stopwords from token sequence."""
        if not self.config.remove_stopwords:
            return tokens
        return [
            t for t in tokens if t.lower() not in self.stopwords and len(t) > 1
        ]

    def tokenize_and_filter(self, text: str) -> List[str]:
        """Master tokenization and stopword removal method."""
        tokens = self.tokenize(text)
        return self.filter_stopwords(tokens)
