from src.data import fake_documents_db
from src.operations.documents import (
    extract_patient_name,
    extract_patient_name_from_words,
    get_document_by_id,
    rebuild_text_from_bounding_boxes,
)


def test_rebuild_text_from_bounding_boxes():
    doc = fake_documents_db["foo"]
    words = rebuild_text_from_bounding_boxes(doc)

    assert words == [
        "J'ai",
        "bien",
        "revu",
        "en",
        "consultation",
        "Monsieur",
        "Jean",
        "DUPONT",
        "pour",
        "une",
        "douleur",
        "à",
        "la",
        "hanche",
        "droite.",
        "Docteur",
        "Nicolas",
        "JACQUES",
    ]


def test_get_document_by_id():
    doc = get_document_by_id("foo")
    assert doc.id == "foo"


def test_extract_patient_name():
    name = extract_patient_name("foo")
    assert name == "Jean DUPONT"


def test_extract_patient_name_from_words_from_document():
    doc = fake_documents_db["foo"]
    words = rebuild_text_from_bounding_boxes(doc)

    assert extract_patient_name_from_words(words) == "Jean DUPONT"


def test_extract_patient_name_skips_titles_and_punctuation():
    words = [
        "Docteur",
        "Nicolas",
        "JACQUES",
        "a",
        "rencontré",
        "Madame",
        "Clara",
        "Martin",
        "hier.",
    ]

    assert extract_patient_name_from_words(words) == "Clara Martin"


def test_extract_patient_name_returns_empty_when_absent():
    words = ["Consultation", "terminée."]

    assert extract_patient_name_from_words(words) == ""
