"""Application configuration and settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DOCAPI_",
        case_sensitive=False,
        extra="ignore",
    )

    # Document processing settings
    ocr_y_threshold: float = Field(
        default=0.01,
        description=(
            "Maximum vertical distance between word centres to group them into the same line"
        ),
        ge=0.0,
        le=1.0,
    )

    # Patient name extraction settings
    enable_feminine_titles: bool = Field(
        default=False,
        description="Enable support for feminine versions of medical titles",
    )


class PatientNameExtractionConfig:
    """Configuration for patient name extraction logic.

    This class encapsulates all the constants and rules used for extracting
    patient names from documents. It provides a centralized place to manage
    these rules and makes them easier to test and modify.
    """

    # Medical titles that should not be considered as patient names
    # Note: All comparisons are case-insensitive
    FORBIDDEN_TITLES: frozenset[str] = frozenset(
        {
            # General titles
            "dr",
            "docteur",
            "pr",
            "professeur",
            "m",
            # Medical roles
            "interne",
            "externe",
            "chef",
            "service",
            "clinique",
            # Specialties - Mental health
            "pédopsychiatre",
            "psychiatre",
            # Specialties - General
            "pédiatre",
            "généraliste",
            "spécialiste",
            # Specialties - Surgery & Anesthesia
            "chirurgien",
            "anesthésiste",
            "réanimateur",
            # Specialties - Women's health
            "gynécologue",
            "obstétricien",
            # Specialties - Internal organs
            "cardiologue",
            "pneumologue",
            "dermatologue",
            "vénérologue",
            "ophtalmologue",
            "stomatologue",
            "urologue",
            "néphrologue",
            # Specialties - Nervous system
            "neurologue",
            "neurochirurgien",
            # Specialties - Cancer
            "cancérologue",
            "oncologue",
            # Specialties - Imaging
            "radiologue",
            "radiothérapeute",
            # Specialties - Digestive
            "gastro-entérologue",
            "hépatologue",
            # Specialties - Bones & Metabolism
            "rhumatologue",
            "endocrinologue",
            "diabétologue",
            "nutritionniste",
            # Specialties - Other
            "gériatre",
            "urgentiste",
            "légiste",
            "biologiste",
        }
    )

    # Feminine versions of medical titles
    # TODO: Add more feminine versions as needed
    FORBIDDEN_TITLES_FEMININE: frozenset[str] = frozenset(
        {
            "doctoresse",
            "docteure",
            "professeure",
            "interne",  # Gender-neutral
            "externe",  # Gender-neutral
            "cheffe",
            "pédopsychiatre",  # Gender-neutral
            "psychiatre",  # Gender-neutral
            "pédiatre",  # Gender-neutral
            "généraliste",  # Gender-neutral
            "spécialiste",  # Gender-neutral
            "chirurgienne",
            "anesthésiste",  # Gender-neutral
            "réanimatrice",
            "gynécologue",  # Gender-neutral
            "obstétricienne",
            "cardiologue",  # Gender-neutral
            "pneumologue",  # Gender-neutral
            "dermatologue",  # Gender-neutral
            "vénérologue",  # Gender-neutral
            "ophtalmologue",  # Gender-neutral
            "stomatologue",  # Gender-neutral
            "urologue",  # Gender-neutral
            "néphrologue",  # Gender-neutral
            "neurologue",  # Gender-neutral
            "neurochirurgienne",
            "cancérologue",  # Gender-neutral
            "oncologue",  # Gender-neutral
            "radiologue",  # Gender-neutral
            "radiothérapeute",  # Gender-neutral
            "gastro-entérologue",  # Gender-neutral
            "hépatologue",  # Gender-neutral
            "rhumatologue",  # Gender-neutral
            "endocrinologue",  # Gender-neutral
            "diabétologue",  # Gender-neutral
            "nutritionniste",  # Gender-neutral
            "gériatre",  # Gender-neutral
            "urgentiste",  # Gender-neutral
            "légiste",  # Gender-neutral
            "biologiste",  # Gender-neutral
        }
    )

    # Capitalized words that are not names (honorifics)
    ALLOWED_CAPITALIZED_WORDS: frozenset[str] = frozenset(
        {
            "monsieur",
            "madame",
            "mademoiselle",
            "mr",
            "mme",
            "mlle",
            "m",
            "mde",
        }
    )

    # Punctuation marks that indicate the end of a sentence
    SENTENCE_END_PUNCTUATION: frozenset[str] = frozenset({".", "!", "?"})

    @classmethod
    def get_forbidden_titles(cls, include_feminine: bool = False) -> frozenset[str]:
        """Get the set of forbidden titles.

        Args:
            include_feminine: If True, include feminine versions of titles.

        Returns:
            A frozen set of forbidden title strings (lowercase).
        """
        if include_feminine:
            return cls.FORBIDDEN_TITLES | cls.FORBIDDEN_TITLES_FEMININE
        return cls.FORBIDDEN_TITLES

    @classmethod
    def is_forbidden_title(cls, word: str, include_feminine: bool = False) -> bool:
        """Check if a word is a forbidden title.

        Args:
            word: The word to check (case-insensitive).
            include_feminine: If True, check against feminine titles as well.

        Returns:
            True if the word is a forbidden title, False otherwise.
        """
        return word.lower() in cls.get_forbidden_titles(include_feminine)

    @classmethod
    def is_allowed_capitalized_word(cls, word: str) -> bool:
        """Check if a word is an allowed capitalized word (honorific).

        Args:
            word: The word to check (case-insensitive).

        Returns:
            True if the word is an allowed capitalized word, False otherwise.
        """
        return word.lower() in cls.ALLOWED_CAPITALIZED_WORDS

    @classmethod
    def is_sentence_end(cls, word: str) -> bool:
        """Check if a word ends with sentence-ending punctuation.

        Args:
            word: The word to check.

        Returns:
            True if the word ends with sentence-ending punctuation, False otherwise.
        """
        return bool(word) and word[-1] in cls.SENTENCE_END_PUNCTUATION


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    This function uses LRU cache to ensure settings are only loaded once.
    To reload settings (e.g., in tests), clear the cache using:
        get_settings.cache_clear()

    Returns:
        Application settings instance.
    """
    return Settings()


# Singleton instance for easy access
settings = get_settings()

# Patient name extraction configuration
patient_config = PatientNameExtractionConfig()
