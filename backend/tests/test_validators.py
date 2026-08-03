"""
MindShield Backend — Validator Utility Unit Tests (Phase 2.2).

Tests all pure validation functions in ``app/utils/validators.py``.
No HTTP stack, no fixtures required — pure unit tests.

Phase 2.2 additions:
  - TestContainsFinancialKeywords
  - TestContainsCredentialRequest
  - TestContainsPrizeLanguage
  - Extended TestComputeMessageFeatures (covers all 9 feature keys)
"""

from __future__ import annotations

from app.utils.validators import (
    compute_message_features,
    contains_credential_request,
    contains_financial_keywords,
    contains_prize_language,
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
        assert sanitise_message("  hello world  ") == "hello world"

    def test_collapses_internal_spaces(self) -> None:
        assert sanitise_message("hello   world") == "hello world"

    def test_normalises_unicode(self) -> None:
        assert sanitise_message("Ａ Ｂ Ｃ") == "A B C"

    def test_preserves_punctuation(self) -> None:
        assert sanitise_message("Hello, world!") == "Hello, world!"


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


class TestContainsFinancialKeywords:
    def test_detects_bank(self) -> None:
        assert contains_financial_keywords("Your bank account is at risk") is True

    def test_detects_payment(self) -> None:
        assert contains_financial_keywords("Payment of £100 failed") is True

    def test_detects_barclays(self) -> None:
        assert contains_financial_keywords("Barclays security alert") is True

    def test_detects_paypal(self) -> None:
        msg = "Your PayPal account needs verification"
        assert contains_financial_keywords(msg) is True

    def test_no_financial_in_casual_message(self) -> None:
        assert contains_financial_keywords("Hi! Are you free tomorrow?") is False

    def test_case_insensitive(self) -> None:
        assert contains_financial_keywords("BANK account suspended") is True


class TestContainsCredentialRequest:
    def test_detects_password(self) -> None:
        assert contains_credential_request("Enter your password to continue") is True

    def test_detects_otp(self) -> None:
        assert contains_credential_request("Enter your OTP code now") is True

    def test_detects_pin(self) -> None:
        assert contains_credential_request("Do not share your PIN") is True

    def test_detects_verification_code(self) -> None:
        assert contains_credential_request("Enter verification code") is True

    def test_no_credential_request_in_safe_message(self) -> None:
        assert contains_credential_request("Hi! See you at lunch.") is False

    def test_case_insensitive(self) -> None:
        assert contains_credential_request("YOUR PASSWORD IS REQUIRED") is True


class TestContainsPrizeLanguage:
    def test_detects_won(self) -> None:
        assert contains_prize_language("You have won a £500 prize") is True

    def test_detects_lottery(self) -> None:
        assert contains_prize_language("Lottery winner selected") is True

    def test_detects_congratulations(self) -> None:
        assert contains_prize_language("Congratulations! You have been chosen") is True

    def test_detects_claim_your(self) -> None:
        assert contains_prize_language("Claim your free gift now") is True

    def test_no_prize_in_normal_message(self) -> None:
        assert contains_prize_language("Meeting at 3pm today") is False


class TestComputeMessageFeatures:
    def test_returns_dict(self) -> None:
        features = compute_message_features("Hello world")
        assert isinstance(features, dict)

    def test_has_all_phase_22_keys(self) -> None:
        features = compute_message_features("Test message 123")
        expected_keys = {
            "has_url",
            "has_urgency",
            "has_financial",
            "has_credentials",
            "has_prize",
            "has_uppercase_ratio",
            "char_count",
            "word_count",
            "has_digits",
        }
        assert expected_keys == set(features.keys())

    def test_char_count_correct(self) -> None:
        text = "Hello world"
        assert compute_message_features(text)["char_count"] == len(text)

    def test_word_count_correct(self) -> None:
        assert compute_message_features("Hello world foo")["word_count"] == 3

    def test_has_url_true_for_url(self) -> None:
        features = compute_message_features("Visit http://example.com")
        assert features["has_url"] is True

    def test_has_url_false_for_plain(self) -> None:
        assert compute_message_features("No URL here at all")["has_url"] is False

    def test_has_financial_true_for_bank(self) -> None:
        features = compute_message_features("Your bank account is suspended")
        assert features["has_financial"] is True

    def test_has_credentials_true_for_otp(self) -> None:
        features = compute_message_features("Enter your OTP to verify")
        assert features["has_credentials"] is True

    def test_has_prize_true_for_lottery(self) -> None:
        features = compute_message_features("You have won the lottery jackpot")
        assert features["has_prize"] is True

    def test_has_digits_true(self) -> None:
        assert compute_message_features("Your code is 12345")["has_digits"] is True

    def test_has_digits_false(self) -> None:
        assert compute_message_features("Hello world")["has_digits"] is False
