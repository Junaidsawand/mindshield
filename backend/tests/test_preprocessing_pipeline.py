# ==============================================================================
# MindShield Backend — NLP Preprocessing Pipeline Test Suite
# Phase 3.2: Comprehensive Unit & Integration Tests
# ==============================================================================

from pathlib import Path

from app.nlp.comparer import StemmerLemmatizerComparer
from app.nlp.config import NLPPreprocessingConfig
from app.nlp.normalizer import TextNormalizer
from app.nlp.pipeline import NLPPreprocessingPipeline
from app.nlp.tokenizer import NLPTokenizer
from app.nlp.vectorizer import NLPVectorizer
from app.services.preprocessing_service import PreprocessingService


def test_config_classical_vs_transformer_preset():
    """Verify preset configs for Classical ML vs Transformer pipelines."""
    classical = NLPPreprocessingConfig.create_classical_config()
    assert classical.lowercase is True
    assert classical.url_policy == "replace"
    assert classical.email_policy == "replace"
    assert classical.phone_policy == "replace"
    assert classical.remove_stopwords is True
    assert classical.stemmer == "porter"

    transformer = NLPPreprocessingConfig.create_transformer_config()
    assert transformer.lowercase is False
    assert transformer.url_policy == "preserve"
    assert transformer.email_policy == "preserve"
    assert transformer.phone_policy == "preserve"
    assert transformer.remove_stopwords is False
    assert transformer.stemmer == "none"


def test_url_email_phone_normalization_policies():
    """Verify entity replacement policies for URLs, emails, and phone numbers."""
    config_replace = NLPPreprocessingConfig(
        url_policy="replace",
        email_policy="replace",
        phone_policy="replace",
        number_policy="replace",
    )
    normalizer = TextNormalizer(config_replace)

    sample = (
        "Contact me at user@test.com or visit http://scam.link. "
        "Call 0800123456 or 100."
    )
    norm = normalizer.normalize(sample)

    assert "email" in norm or "[EMAIL]" in norm
    assert "url" in norm or "[URL]" in norm
    assert "phone" in norm or "number" in norm
    assert "http://" not in norm
    assert "user@test.com" not in norm


def test_emoji_handling():
    """Verify emoji demojization, removal, and preservation policies."""
    cfg_demojize = NLPPreprocessingConfig(emoji_policy="demojize")
    norm_demojize = TextNormalizer(cfg_demojize)
    res_dem = norm_demojize.normalize("WIN PRIZE 🎁😊")
    assert "gift" in res_dem or "win prize" in res_dem

    cfg_remove = NLPPreprocessingConfig(emoji_policy="remove")
    norm_remove = TextNormalizer(cfg_remove)
    res_rem = norm_remove.normalize("WIN PRIZE 🎁😊")
    assert "🎁" not in res_rem and "😊" not in res_rem


def test_punctuation_and_whitespace_cleanup():
    """Verify repeated punctuation collapse and whitespace trimming."""
    cfg_norm = NLPPreprocessingConfig(
        lowercase=False, punctuation_policy="normalize"
    )
    normalizer = TextNormalizer(cfg_norm)
    res = normalizer.normalize("  URGENT!!!   Claim now???   ")
    assert "URGENT!" in res
    assert "now?" in res
    assert "  " not in res


def test_tokenization_and_stopwords():
    """Verify token extraction and stopword removal logic."""
    cfg = NLPPreprocessingConfig(lowercase=True, remove_stopwords=True)
    tokenizer = NLPTokenizer(cfg)

    tokens = tokenizer.tokenize_and_filter(
        "This is an URGENT prize message for you"
    )
    assert "this" not in tokens
    assert "is" not in tokens
    assert "an" not in tokens
    assert "for" not in tokens
    assert "urgent" in tokens or "URGENT" in tokens
    assert "prize" in tokens


def test_stemmer_lemmatizer_comparison_metrics():
    """Verify stemmer/lemmatizer analysis metrics computation."""
    comparer = StemmerLemmatizerComparer()
    sample_docs = [
        ["running", "runs", "ran", "winner", "winning"],
        ["prizes", "claimed", "messages", "calling"],
    ]
    metrics = comparer.analyze_corpus(sample_docs)

    assert metrics["total_documents"] == 2
    assert metrics["total_token_count"] == 9
    assert metrics["raw_vocabulary_size"] > 0
    assert "stemming_vocabulary_reduction_percent" in metrics
    assert "lemmatization_vocabulary_reduction_percent" in metrics


def test_count_and_tfidf_vectorizer():
    """Verify CountVectorizer and TF-IDF matrix generation."""
    docs = [
        "urgent prize claim now",
        "hello friend see you tonight",
        "urgent prize call now",
    ]

    count_vec = NLPVectorizer(method="count", max_features=100)
    count_mat = count_vec.fit_transform(docs)
    assert count_mat.shape[0] == 3
    assert count_vec.get_vocabulary_size() > 0

    tfidf_vec = NLPVectorizer(method="tfidf", max_features=100)
    tfidf_mat = tfidf_vec.fit_transform(docs)
    assert tfidf_mat.shape[0] == 3
    assert tfidf_vec.get_vocabulary_size() > 0


def test_pipeline_serialization_save_load(tmp_path: Path):
    """Verify pipeline configuration serialization and deserialization."""
    cfg = NLPPreprocessingConfig.create_classical_config(
        url_placeholder="[SAFE_URL]"
    )
    pipeline = NLPPreprocessingPipeline(cfg)

    export_file = tmp_path / "pipeline_config.json"
    pipeline.save_pipeline(export_file)

    assert export_file.exists()
    loaded_pipeline = NLPPreprocessingPipeline.load_pipeline(export_file)
    assert loaded_pipeline.config.url_placeholder == "[SAFE_URL]"
    assert loaded_pipeline.config.lowercase is True


def test_metadata_json_export(tmp_path: Path):
    """Verify preprocessing comparison JSON export."""
    pipeline = NLPPreprocessingPipeline()
    docs = ["URGENT! Call 0800111222 now", "Hello friend, how are you?"]

    export_json = tmp_path / "preprocessing_comparison.json"
    metrics = pipeline.generate_comparison_metrics(
        docs, export_path=export_json
    )

    assert export_json.exists()
    assert metrics["vocabulary_size_before"] > 0
    assert "token_count_statistics" in metrics
    assert "processing_performance" in metrics


def test_preprocessing_service_batch_execution():
    """Verify batch processing execution via PreprocessingService."""
    svc = PreprocessingService()
    batch = [
        "URGENT prize notification http://scam.link",
        "Meeting at 5pm today",
    ]

    results_class = svc.preprocess_batch_messages(batch, mode="classical")
    assert len(results_class) == 2
    norm_text = results_class[0]["normalized_text"]
    assert "url" in norm_text or "[URL]" in norm_text

    results_trans = svc.preprocess_batch_messages(batch, mode="transformer")
    assert len(results_trans) == 2
    assert "http://scam.link" in results_trans[0]["normalized_text"]


def test_pakscam_dataset_config_compatibility():
    """Verify dataset-agnostic compatibility with PakScam payloads."""
    pakscam_payloads = [
        "BISP 25000 Qist mil gayi hai. Call 03001234567 par karein.",
        "Kese ho bhai? Shaam ko milte hain.",
    ]
    pipeline = NLPPreprocessingPipeline()
    res = pipeline.preprocess_corpus(pakscam_payloads)

    assert len(res) == 2
    assert (
        "phone" in res[0]["normalized_text"]
        or "number" in res[0]["normalized_text"]
        or "0300" in res[0]["normalized_text"]
    )
