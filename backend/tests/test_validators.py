"""
MindShield Backend — Validator Utility Unit Tests.

Tests pure validation functions in ``app/utils/validators.py``.
No HTTP stack, no fixtures required — pure unit tests.
"""

from __future__ import annotations

from app.utils.validators import (
    compute_message_features,
    contains_urgency_language,
    contains_url,
    is_valid_message,
    is_valid_sender,
    sanitise_message,
)


class TestIsValidMessage:
    def test_valid_message(self) -> None:
        assert is_valid_message("Hello, this is a test message.") is True

    def test_empty_string_invalid(self) -> None:
        assert is_valid_message("") is False

    def test_whitespace_only_invalid(self) -> None:
        assert is_valid_message("   ") is False

    def test_too_short_invalid(self) -> None:
        assert is_valid_message("ab") is False

    def test_exactly_min_length_valid(self) -> None:
        assert is_valid_message("abc") is True

    def test_exactly_max_length_valid(self) -> None:
        assert is_valid_message("a" * 2000) is True

    def test_over_max_length_invalid(self) -> None:
        assert is_valid_message("a" * 2001) is False

    def test_purely_numeric_invalid(self) -> None:
        assert is_valid_message("123456") is False

    def test_numeric_with_text_valid(self) -> None:
        assert is_valid_message("OTP 123456 for your account") is True


class TestIsValidSender:
    def test_none_is_valid(self) -> None:
        assert is_valid_sender(None) is True

    def test_empty_string_is_valid(self) -> None:
        assert is_valid_sender("") is True

    def test_e164_number_valid(self) -> None:
        assert is_valid_sender("+447911123456") is True

    def test_short_name_valid(self) -> None:
        assert is_valid_sender("MyBank") is True

    def test_too_long_sender_invalid(self) -> None:
        assert is_valid_sender("x" * 51) is False


class TestSanitiseMessage:
    def test_strips_whitespace(self) -> None:
        result = sanitise_message("  hello world  ")
        assert result == "hello world"

    def test_collapses_internal_spaces(self) -> None:
        result = sanitise_message("hello   world")
        assert result == "hello world"

    def test_normalises_unicode(self) -> None:
        # Full-width characters should normalise to ASCII
        result = sanitise_message("Ａ Ｂ Ｃ")
        assert result == "A B C"

    def test_preserves_punctuation(self) -> None:
        result = sanitise_message("Hello, world!")
        assert result == "Hello, world!"


class TestContainsUrl:
    def test_detects_http_url(self) -> None:
        assert contains_url("Visit http://example.com now") is True

    def test_detects_https_url(self) -> None:
        assert contains_url("Go to https://example.com") is True

    def test_detects_www_url(self) -> None:
        assert contains_url("Visit www.example.com") is True

    def test_detects_bitly(self) -> None:
        assert contains_url("Click bit.ly/abc123") is True

    def test_no_url_in_plain_text(self) -> None:
        assert contains_url("This is a normal message") is False


class TestContainsUrgencyLanguage:
    def test_detects_urgent(self) -> None:
        assert contains_urgency_language("URGENT action required") is True

    def test_detects_suspended(self) -> None:
        assert contains_urgency_language("Your account has been suspended") is True

    def test_detects_click_here(self) -> None:
        assert contains_urgency_language("Click here to verify") is True

    def test_case_insensitive(self) -> None:
        assert contains_urgency_language("CLICK HERE NOW") is True

    def test_no_urgency_in_normal_message(self) -> None:
        assert contains_urgency_language("Hi, hope you are doing well") is False


class TestComputeMessageFeatures:
    def test_returns_dict(self) -> None:
        features = compute_message_features("Hello world")
        assert isinstance(features, dict)

    def test_has_all_expected_keys(self) -> None:
        features = compute_message_features("Test message 123")
        expected_keys = {
            "has_url",
            "has_urgency",
            "char_count",
            "word_count",
            "has_digits",
            "has_uppercase_ratio",
        }
        assert expected_keys.issubset(features.keys())

    def test_char_count_correct(self) -> None:
        text = "Hello world"
        features = compute_message_features(text)
        assert features["char_count"] == len(text)

    def test_word_count_correct(self) -> None:
        features = compute_message_features("Hello world foo")
        assert features["word_count"] == 3

    def test_has_url_true_for_url(self) -> None:
        features = compute_message_features("Visit http://example.com")
        assert features["has_url"] is True

    def test_has_url_false_for_plain(self) -> None:
        features = compute_message_features("No URL here at all")
        assert features["has_url"] is False
