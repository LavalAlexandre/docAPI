"""Tests for configuration module."""

import pytest
from pydantic import ValidationError

from src.config import PatientNameExtractionConfig, Settings, get_settings


def test_settings_defaults():
    """Test that settings have correct default values."""
    settings = Settings()
    assert settings.ocr_y_threshold == 0.01
    assert settings.enable_feminine_titles is False


def test_settings_from_env(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    monkeypatch.setenv("DOCAPI_OCR_Y_THRESHOLD", "0.02")
    monkeypatch.setenv("DOCAPI_ENABLE_FEMININE_TITLES", "true")

    # Clear cache to reload settings
    get_settings.cache_clear()
    settings = get_settings()

    assert settings.ocr_y_threshold == 0.02
    assert settings.enable_feminine_titles is True

    # Clean up
    get_settings.cache_clear()


def test_patient_config_forbidden_titles():
    """Test forbidden titles configuration."""
    config = PatientNameExtractionConfig()

    # Test some common titles
    assert config.is_forbidden_title("docteur")
    assert config.is_forbidden_title("DOCTEUR")  # Case-insensitive
    assert config.is_forbidden_title("Docteur")
    assert config.is_forbidden_title("pr")
    assert config.is_forbidden_title("professeur")
    assert not config.is_forbidden_title("Jean")
    assert not config.is_forbidden_title("DUPONT")


def test_patient_config_feminine_titles():
    """Test feminine titles configuration."""
    config = PatientNameExtractionConfig()

    # Without feminine titles enabled
    assert not config.is_forbidden_title("doctoresse", include_feminine=False)
    assert not config.is_forbidden_title("réanimatrice", include_feminine=False)

    # With feminine titles enabled
    assert config.is_forbidden_title("doctoresse", include_feminine=True)
    assert config.is_forbidden_title("réanimatrice", include_feminine=True)
    assert config.is_forbidden_title("chirurgienne", include_feminine=True)
    assert config.is_forbidden_title("Neurochirurgienne", include_feminine=True)


def test_patient_config_allowed_capitalized_words():
    """Test allowed capitalized words configuration."""
    config = PatientNameExtractionConfig()

    assert config.is_allowed_capitalized_word("Monsieur")
    assert config.is_allowed_capitalized_word("madame")
    assert config.is_allowed_capitalized_word("MADEMOISELLE")
    assert config.is_allowed_capitalized_word("mr")
    assert config.is_allowed_capitalized_word("mme")
    assert config.is_allowed_capitalized_word("mlle")
    assert not config.is_allowed_capitalized_word("Jean")
    assert not config.is_allowed_capitalized_word("Doctor")


def test_patient_config_sentence_end():
    """Test sentence end punctuation detection."""
    config = PatientNameExtractionConfig()

    assert config.is_sentence_end("hier.")
    assert config.is_sentence_end("Bonjour!")
    assert config.is_sentence_end("Vraiment?")
    assert not config.is_sentence_end("hier")
    assert not config.is_sentence_end("Bonjour")
    assert not config.is_sentence_end("")


def test_patient_config_get_forbidden_titles():
    """Test getting forbidden titles with/without feminine versions."""
    config = PatientNameExtractionConfig()

    titles_base = config.get_forbidden_titles(include_feminine=False)
    titles_with_feminine = config.get_forbidden_titles(include_feminine=True)

    # Base titles should be a subset
    assert titles_base.issubset(titles_with_feminine)

    # With feminine should have more titles
    assert len(titles_with_feminine) >= len(titles_base)

    # Specific checks
    assert "docteur" in titles_base
    assert "docteur" in titles_with_feminine
    assert "doctoresse" not in titles_base
    assert "doctoresse" in titles_with_feminine


def test_patient_config_immutability():
    """Test that configuration constants are immutable (frozenset)."""
    config = PatientNameExtractionConfig()

    # Should raise error if trying to modify
    with pytest.raises(AttributeError):
        config.FORBIDDEN_TITLES.add("new_title")

    with pytest.raises(AttributeError):
        config.ALLOWED_CAPITALIZED_WORDS.add("new_word")

    with pytest.raises(AttributeError):
        config.SENTENCE_END_PUNCTUATION.add("~")


def test_settings_singleton():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


def test_settings_y_threshold_validation():
    """Test that y_threshold is validated within range."""
    # Valid values
    settings = Settings(ocr_y_threshold=0.0)
    assert settings.ocr_y_threshold == 0.0

    settings = Settings(ocr_y_threshold=0.5)
    assert settings.ocr_y_threshold == 0.5

    settings = Settings(ocr_y_threshold=1.0)
    assert settings.ocr_y_threshold == 1.0

    # Invalid values should raise validation error
    with pytest.raises(ValidationError):
        Settings(ocr_y_threshold=-0.1)

    with pytest.raises(ValidationError):
        Settings(ocr_y_threshold=1.1)
