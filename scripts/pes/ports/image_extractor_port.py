"""Port interface for image extraction from documents.

Driven port: ImageExtractorPort
Adapters implement this to extract images from PDF, DOCX, or other formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RawImage:
    """A single image extracted from a document.

    Frozen value object -- immutable after creation.
    Captures: raw bytes, format, page location, quality metrics, and context.
    """

    image_bytes: bytes
    format: str  # "png", "jpeg", etc. -- as-extracted, no conversion
    page_number: int
    position_index: int
    width: int
    height: int
    dpi: int
    caption: str
    surrounding_text: str


@dataclass(frozen=True)
class ExtractionFailure:
    """Records a per-image extraction failure."""

    page_number: int
    reason: str


@dataclass(frozen=True)
class ExtractionResult:
    """Result of extracting images from a document.

    Contains successfully extracted images and per-image failures.
    Failures do not block successful extractions.
    """

    images: list[RawImage]
    failures: list[ExtractionFailure]


class ImageExtractorPort(ABC):
    """Extract images from a document file -- driven port."""

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractionResult:
        """Extract all images from the given document.

        Returns an ExtractionResult with extracted images and any failures.
        Unsupported encodings are logged as failures without blocking
        extraction of other images in the document.
        """
