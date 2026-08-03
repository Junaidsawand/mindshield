# ==============================================================================
# MindShield Backend — NLP Preprocessing Configuration Module
# Phase 3.2: Declarative, Model-Agnostic & Future-Proof Configuration
# ==============================================================================

from dataclasses import asdict, dataclass, field
from typing import Any, Dict


@dataclass
class NLPPreprocessingConfig:
    """Declarative configuration model for NLP text preprocessing pipelines.

    Supports dual operating presets:
    - Classical ML Preset: Aggressive normalization, lowercasing, stopword
      removal, stemming/lemmatization, placeholder substitution.
    - Transformer Preset (DistilBERT): Light non-destructive normalization,
      preserving case, URLs, emojis, punctuation, and phone numbers.
    """

    # --- Core Normalization Toggles ---
    lowercase: bool = True
    url_policy: str = "replace"        # "replace" | "remove" | "preserve"
    email_policy: str = "replace"      # "replace" | "remove" | "preserve"
    number_policy: str = "replace"     # "replace" | "remove" | "preserve"
    phone_policy: str = "replace"      # "replace" | "remove" | "preserve"
    emoji_policy: str = "demojize"     # "demojize" | "remove" | "preserve"
    punctuation_policy: str = "remove"  # "normalize" | "remove" | "preserve"
    whitespace_cleanup: bool = True

    # --- Placeholders ---
    url_placeholder: str = "[URL]"
    email_placeholder: str = "[EMAIL]"
    number_placeholder: str = "[NUMBER]"
    phone_placeholder: str = "[PHONE]"

    # --- Tokenization & Vocabulary Reduction ---
    remove_stopwords: bool = True
    custom_stopwords: list[str] = field(default_factory=list)
    stemmer: str = "none"              # "none" | "porter" | "snowball"
    lemmatizer: str = "none"           # "none" | "wordnet" | "rule"

    def validate(self) -> None:
        """Validate policy string parameters."""
        valid_policies = {"replace", "remove", "preserve"}
        valid_emojis = {"demojize", "remove", "preserve"}
        valid_puncts = {"normalize", "remove", "preserve"}
        valid_stemmers = {"none", "porter", "snowball"}
        valid_lemmatizers = {"none", "wordnet", "rule"}

        if self.url_policy not in valid_policies:
            raise ValueError(f"Invalid url_policy: {self.url_policy}")
        if self.email_policy not in valid_policies:
            raise ValueError(f"Invalid email_policy: {self.email_policy}")
        if self.number_policy not in valid_policies:
            raise ValueError(f"Invalid number_policy: {self.number_policy}")
        if self.phone_policy not in valid_policies:
            raise ValueError(f"Invalid phone_policy: {self.phone_policy}")
        if self.emoji_policy not in valid_emojis:
            raise ValueError(f"Invalid emoji_policy: {self.emoji_policy}")
        if self.punctuation_policy not in valid_puncts:
            raise ValueError(
                f"Invalid punctuation_policy: {self.punctuation_policy}"
            )
        if self.stemmer not in valid_stemmers:
            raise ValueError(f"Invalid stemmer: {self.stemmer}")
        if self.lemmatizer not in valid_lemmatizers:
            raise ValueError(f"Invalid lemmatizer: {self.lemmatizer}")

    @classmethod
    def create_classical_config(cls, **kwargs: Any) -> "NLPPreprocessingConfig":
        """Preset configuration optimized for Classical ML models.

        Applies lowercasing, placeholder substitution, punctuation removal,
        stopword filtering, and optional stemming.
        """
        config = cls(
            lowercase=True,
            url_policy="replace",
            email_policy="replace",
            number_policy="replace",
            phone_policy="replace",
            emoji_policy="demojize",
            punctuation_policy="remove",
            whitespace_cleanup=True,
            remove_stopwords=True,
            stemmer="porter",
            lemmatizer="none",
        )
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.validate()
        return config

    @classmethod
    def create_transformer_config(
        cls, **kwargs: Any
    ) -> "NLPPreprocessingConfig":
        """Preset configuration optimized for DistilBERT fine-tuning.

        Applies light normalization (whitespace trimming, line ending fix)
        while preserving case, URLs, emails, phone numbers, emojis, and punctuation.
        """
        config = cls(
            lowercase=False,
            url_policy="preserve",
            email_policy="preserve",
            number_policy="preserve",
            phone_policy="preserve",
            emoji_policy="preserve",
            punctuation_policy="preserve",
            whitespace_cleanup=True,
            remove_stopwords=False,
            stemmer="none",
            lemmatizer="none",
        )
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.validate()
        return config

    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NLPPreprocessingConfig":
        """Instantiate configuration from dictionary."""
        config = cls(**data)
        config.validate()
        return config
