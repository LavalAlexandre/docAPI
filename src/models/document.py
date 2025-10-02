"""Pydantic models related to documents."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Absolute coordinates for a word on the page."""

    x_min: float = Field(..., ge=0.0, le=1.0)
    x_max: float = Field(..., ge=0.0, le=1.0)
    y_min: float = Field(..., ge=0.0, le=1.0)
    y_max: float = Field(..., ge=0.0, le=1.0)


class Word(BaseModel):
    """A word identified on a page with its bounding box."""

    text: str
    bbox: BoundingBox


class Page(BaseModel):
    """A single page of a document containing words."""

    words: list[Word] = Field(default_factory=list)


class Document(BaseModel):
    """Represents a document exposed via the API."""

    id: str
    title: str
    pages: list[Page] = Field(default_factory=list)
    original_page_count: int = Field(default=0, ge=0)
    needs_ocr_case: Literal["no_ocr", "needs_ocr"] = "no_ocr"


class PatientNameResponse(BaseModel):
    """Response model for patient name extraction."""

    document_id: str
    extracted_name: str
