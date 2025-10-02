"""Custom exception classes for the DocAPI application."""

from __future__ import annotations


class DocumentNotFoundError(Exception):
    """Raised when a document is not found in the data store."""

    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__(f"Document with id '{document_id}' not found.")
