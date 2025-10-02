from collections.abc import Iterable

from src.config import patient_config, settings
from src.data import fake_documents_db
from src.exceptions import DocumentNotFoundError
from src.models.document import Document, Word


def rebuild_text_from_bounding_boxes(
    document: Document, *, y_threshold: float | None = None
) -> list[str]:
    """Return the ordered words of a document based on their bounding boxes.

    Words are grouped into lines when the vertical distance between their centres is
    within ``y_threshold`` (expressed in the same normalised coordinates as the
    bounding boxes). The resulting list contains the document's words ordered
    top-to-bottom then left-to-right; no additional separators are inserted between
    lines or pages.

    Args:
        document: Document containing pages of OCR words.
        y_threshold: Maximum vertical distance between word centres to consider
            them part of the same line. If None, uses the default from settings.

    Returns:
        A list of word strings ordered as they should appear when reading.
    """
    if y_threshold is None:
        y_threshold = settings.ocr_y_threshold

    def _group_words_into_lines(words: Iterable[Word]) -> list[list[Word]]:
        sorted_words = sorted(
            words,
            key=lambda w: ((w.bbox.y_min + w.bbox.y_max) / 2, w.bbox.x_min),
        )

        lines: list[list[Word]] = []
        current_line: list[Word] = []
        current_y: float | None = None

        for word in sorted_words:
            word_y = (word.bbox.y_min + word.bbox.y_max) / 2
            if current_y is None or abs(word_y - current_y) <= y_threshold:
                current_line.append(word)
                current_y = word_y if current_y is None else (current_y + word_y) / 2
            else:
                lines.append(current_line)
                current_line = [word]
                current_y = word_y

        if current_line:
            lines.append(current_line)

        return lines

    reconstructed_words: list[str] = []

    for page in document.pages:
        page_lines = _group_words_into_lines(page.words)

        for line in page_lines:
            ordered_words = sorted(line, key=lambda w: w.bbox.x_min)
            reconstructed_words.extend(word.text for word in ordered_words)

    return reconstructed_words


def get_document_by_id(document_id: str) -> Document:
    """Retrieve a document by its ID.
    
    Args:
        document_id: The unique identifier of the document to retrieve.
        
    Returns:
        The requested document.
        
    Raises:
        DocumentNotFoundError: If the document with the given ID does not exist.
    """
    if document_id not in fake_documents_db:
        raise DocumentNotFoundError(document_id)
    return fake_documents_db[document_id]


def extract_patient_name(document_id: str) -> str:
    """Extract the patient's name from a document.
    
    This is a convenience function that retrieves the document, rebuilds the text
    from its bounding boxes, and extracts the patient name.
    
    Args:
        document_id: The unique identifier of the document.
        
    Returns:
        The extracted patient name, or an empty string if no name is found.
        
    Raises:
        DocumentNotFoundError: If the document with the given ID does not exist.
    """
    document = get_document_by_id(document_id)

    words = rebuild_text_from_bounding_boxes(document)

    return extract_patient_name_from_words(words)


def extract_patient_name_from_words(words: list[str]) -> str:
    """Extract the patient's name from a list of ordered words.

    Here the global heuristics is that capitalized words that are not preceded by
    a doctor title or a sentence-ending punctuation are considered as names.

    Args:
        words: A list of ordered words from the document.

    Rules:
        - A patient name is either a single word or two words (first name and last name).
        - Each word in the name starts with an uppercase letter.
        - Some words are not considered as names even if they start with an uppercase
          letter (forbidden titles and allowed capitalized words/honorifics)
        - The name can't start a sentence (i.e. it is not the first word of the document,
          and the preceding word does not end with a sentence-terminating punctuation
          mark like '.', '!', or '?').
        - If the preceding word is a forbidden title, the next word is not a name.
          (e.g., to avoid "Docteur Nicolas JACQUES" being identified as a patient name)

    Returns:
        The extracted patient name.
    """
    to_be_skipped = False
    include_feminine = settings.enable_feminine_titles

    for i, word in enumerate(words):
        if i == 0:
            continue
        if to_be_skipped:
            to_be_skipped = False
            continue

        preceding_word = words[i - 1]

        # Rule: Not preceded by a sentence-ending punctuation mark.
        if patient_config.is_sentence_end(preceding_word):
            continue

        # Rule: Not preceded by a forbidden title.
        # In this case we also skip the next word as it is likely part of the title.
        # (e.g., "Docteur Nicolas Dupont")
        if patient_config.is_forbidden_title(preceding_word, include_feminine):
            to_be_skipped = True
            continue

        # Rule: Word must start with an uppercase letter and not be a title
        if not word[0].isupper() or patient_config.is_forbidden_title(word, include_feminine):
            continue

        # Rule: Allow certain capitalized words that are not names
        if patient_config.is_allowed_capitalized_word(word):
            continue

        # Check for a two-word name.
        # If the next word also starts with an uppercase letter, it's part of the name.
        if i + 1 < len(words):
            next_word = words[i + 1]
            if next_word[0].isupper():
                return f"{word} {next_word}"

        # If a two-word name isn't found, return the single-word name.
        return word

    return ""
