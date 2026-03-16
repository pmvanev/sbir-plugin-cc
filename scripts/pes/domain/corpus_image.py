"""Corpus image domain model -- value objects for image registry entries.

Pure domain objects with no infrastructure imports.
ImageEntry captures metadata for a single extracted image.
QualityLevel classifies image quality by DPI threshold.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class QualityLevel(Enum):
    """Image quality classification based on DPI thresholds."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @staticmethod
    def from_dpi(dpi: int) -> QualityLevel:
        """Classify quality from DPI value.

        >= 300 DPI -> HIGH, >= 150 DPI -> MEDIUM, else LOW.
        """
        if dpi >= 300:
            return QualityLevel.HIGH
        if dpi >= 150:
            return QualityLevel.MEDIUM
        return QualityLevel.LOW


@dataclass(frozen=True)
class ImageEntry:
    """A single image cataloged in the corpus registry.

    Frozen value object -- immutable after creation.
    Captures: source, page, caption, type, DPI, hash, compliance flag.
    """

    id: str
    source_proposal: str
    page_number: int
    caption: str
    figure_type: str
    dpi: int
    content_hash: str
    quality_level: QualityLevel
    extraction_date: str = ""
    agency: str = ""
    origin_type: str = "company-created"
    compliance_flag: str | None = None
    duplicate_sources: tuple[str, ...] = ()

    def with_flag(self, flag: str | None) -> ImageEntry:
        """Return a new entry with the compliance flag updated."""
        return ImageEntry(
            id=self.id,
            source_proposal=self.source_proposal,
            page_number=self.page_number,
            caption=self.caption,
            figure_type=self.figure_type,
            dpi=self.dpi,
            content_hash=self.content_hash,
            quality_level=self.quality_level,
            extraction_date=self.extraction_date,
            agency=self.agency,
            origin_type=self.origin_type,
            compliance_flag=flag,
            duplicate_sources=self.duplicate_sources,
        )

    def with_merged_source(self, source: str) -> ImageEntry:
        """Return a new entry with an additional source proposal."""
        if source == self.source_proposal or source in self.duplicate_sources:
            return self
        return ImageEntry(
            id=self.id,
            source_proposal=self.source_proposal,
            page_number=self.page_number,
            caption=self.caption,
            figure_type=self.figure_type,
            dpi=self.dpi,
            content_hash=self.content_hash,
            quality_level=self.quality_level,
            extraction_date=self.extraction_date,
            agency=self.agency,
            origin_type=self.origin_type,
            compliance_flag=self.compliance_flag,
            duplicate_sources=(*self.duplicate_sources, source),
        )
