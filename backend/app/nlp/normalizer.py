# ==============================================================================
# MindShield Backend — Text Normalizer Module
# Phase 3.2: Reusable Text Cleaning, Regex Matching & Entity Handling
# ==============================================================================

import re
from typing import Optional

try:
    import emoji
    EMOJI_AVAILABLE = True
except ImportError:
    EMOJI_AVAILABLE = False

from app.nlp.config import NLPPreprocessingConfig


class TextNormalizer:
    """Production-grade text normalizer.

    Supports entity replacement, lowercasing, emoji demojization,
    punctuation handling, and whitespace cleanup.
    """

    # --- Compiled Regex Patterns ---
    URL_PATTERN = re.compile(
        r"https?://\S+|www\.\S+|bit\.ly/\S+|t\.co/\S+", re.IGNORECASE
    )
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE
    )
    PHONE_PATTERN = re.compile(
        r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)?\d{3,4}[\s-]?\d{3,4}|"
        r"(?:0800|0845|0906|0870|0871|07\d{9}|03\d{9}|\+92\d{10})",
        re.IGNORECASE,
    )
    NUMBER_PATTERN = re.compile(r"\b\d+\b")
    EMOJI_PATTERN = re.compile(r"[\U00010000-\U0010ffff]", re.UNICODE)
    PUNCT_REMOVE_PATTERN = re.compile(r"[^\w\s]")
    REPEATED_PUNCT_PATTERN = re.compile(r"([!?.])\1+")

    def __init__(self, config: Optional[NLPPreprocessingConfig] = None):
        self.config = config or NLPPreprocessingConfig()

    def clean_urls(self, text: str) -> str:
        """Process URLs based on configured url_policy."""
        if self.config.url_policy == "replace":
            return self.URL_PATTERN.sub(self.config.url_placeholder, text)
        elif self.config.url_policy == "remove":
            return self.URL_PATTERN.sub("", text)
        return text

    def clean_emails(self, text: str) -> str:
        """Process emails based on configured email_policy."""
        if self.config.email_policy == "replace":
            return self.EMAIL_PATTERN.sub(self.config.email_placeholder, text)
        elif self.config.email_policy == "remove":
            return self.EMAIL_PATTERN.sub("", text)
        return text

    def clean_phones_and_numbers(self, text: str) -> str:
        """Process phone numbers and digits based on config policies."""
        if self.config.phone_policy == "replace":
            text = self.PHONE_PATTERN.sub(self.config.phone_placeholder, text)
        elif self.config.phone_policy == "remove":
            text = self.PHONE_PATTERN.sub("", text)

        if self.config.number_policy == "replace":
            text = self.NUMBER_PATTERN.sub(self.config.number_placeholder, text)
        elif self.config.number_policy == "remove":
            text = self.NUMBER_PATTERN.sub("", text)

        return text

    def clean_emojis(self, text: str) -> str:
        """Process Unicode emojis based on configured emoji_policy."""
        if self.config.emoji_policy == "demojize":
            if EMOJI_AVAILABLE:
                return emoji.demojize(text, delimiters=(" :", ": "))
            # Fallback Unicode emoji regex if emoji package unavailable
            return text
        elif self.config.emoji_policy == "remove":
            if EMOJI_AVAILABLE:
                text = emoji.replace_emoji(text, replace="")
            return self.EMOJI_PATTERN.sub("", text)
        return text

    def normalize_punctuation(self, text: str) -> str:
        """Process punctuation based on configured punctuation_policy."""
        if self.config.punctuation_policy == "remove":
            return self.PUNCT_REMOVE_PATTERN.sub(" ", text)
        elif self.config.punctuation_policy == "normalize":
            return self.REPEATED_PUNCT_PATTERN.sub(r"\1", text)
        return text

    def clean_whitespace(self, text: str) -> str:
        """Normalize line endings and collapse multiple internal spaces."""
        text = text.replace("\x00", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        return "\n".join([line for line in lines if line]).strip()

    def normalize(self, text: str) -> str:
        """Execute master text normalization pipeline."""
        if not isinstance(text, str):
            text = str(text) if text is not None else ""

        # Step 1: Whitespace pre-cleanup & line ending normalization
        text = self.clean_whitespace(text)

        # Step 2: URL & Email handling
        text = self.clean_urls(text)
        text = self.clean_emails(text)

        # Step 3: Phone & Number normalization
        text = self.clean_phones_and_numbers(text)

        # Step 4: Emoji handling
        text = self.clean_emojis(text)

        # Step 5: Lowercasing (if configured)
        if self.config.lowercase:
            text = text.lower()

        # Step 6: Punctuation normalization or removal
        text = self.normalize_punctuation(text)

        # Step 7: Final whitespace cleanup
        if self.config.whitespace_cleanup:
            text = self.clean_whitespace(text)

        return text
