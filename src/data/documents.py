"""Temporary in-memory document fixtures for development/testing."""

from __future__ import annotations

from src.models.document import BoundingBox, Document, Page, Word

fake_documents_db: dict[str, Document] = {
    "foo": Document(
        id="foo",
        title="Consultation report",
        pages=[
            Page(
                words=[
                    Word(
                        text="hanche",
                        bbox=BoundingBox(x_min=0.75, x_max=0.81, y_min=0.09, y_max=0.1),
                    ),
                    Word(
                        text="JACQUES",
                        bbox=BoundingBox(x_min=0.74, x_max=0.83, y_min=0.16, y_max=0.17),
                    ),
                    Word(
                        text="pour", bbox=BoundingBox(x_min=0.57, x_max=0.61, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="la", bbox=BoundingBox(x_min=0.73, x_max=0.75, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="en", bbox=BoundingBox(x_min=0.23, x_max=0.26, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="bien", bbox=BoundingBox(x_min=0.15, x_max=0.19, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="consultation",
                        bbox=BoundingBox(x_min=0.26, x_max=0.36, y_min=0.09, y_max=0.1),
                    ),
                    Word(
                        text="Monsieur",
                        bbox=BoundingBox(x_min=0.36, x_max=0.44, y_min=0.09, y_max=0.1),
                    ),
                    Word(
                        text="Jean", bbox=BoundingBox(x_min=0.44, x_max=0.48, y_min=0.09, y_max=0.1)
                    ),
                    Word(text="à", bbox=BoundingBox(x_min=0.72, x_max=0.73, y_min=0.09, y_max=0.1)),
                    Word(
                        text="droite.",
                        bbox=BoundingBox(x_min=0.82, x_max=0.87, y_min=0.09, y_max=0.1),
                    ),
                    Word(
                        text="revu", bbox=BoundingBox(x_min=0.19, x_max=0.23, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="DUPONT",
                        bbox=BoundingBox(x_min=0.49, x_max=0.57, y_min=0.09, y_max=0.1),
                    ),
                    Word(
                        text="douleur",
                        bbox=BoundingBox(x_min=0.65, x_max=0.71, y_min=0.09, y_max=0.1),
                    ),
                    Word(
                        text="J'ai", bbox=BoundingBox(x_min=0.12, x_max=0.15, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="une", bbox=BoundingBox(x_min=0.61, x_max=0.65, y_min=0.09, y_max=0.1)
                    ),
                    Word(
                        text="Nicolas",
                        bbox=BoundingBox(x_min=0.67, x_max=0.73, y_min=0.16, y_max=0.17),
                    ),
                    Word(
                        text="Docteur",
                        bbox=BoundingBox(x_min=0.6, x_max=0.67, y_min=0.16, y_max=0.17),
                    ),
                ]
            )
        ],
        original_page_count=1,
        needs_ocr_case="no_ocr",
    ),
    "bar": Document(id="bar", title="Bar"),
    "baz": Document(id="baz", title="Baz"),
}
