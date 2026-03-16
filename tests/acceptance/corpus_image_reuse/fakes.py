"""In-memory fake adapters for corpus image reuse acceptance tests.

These fakes implement driven port interfaces with in-memory state,
enabling fast isolated testing without real PDF/DOCX files or filesystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawExtractedImage:
    """Raw image data returned by extraction adapters."""

    image_bytes: bytes
    format: str  # "png", "jpeg"
    page_number: int
    position_index: int
    width: int
    height: int
    dpi: int
    caption: str
    surrounding_text: str


class InMemoryImageExtractorAdapter:
    """In-memory fake for ImageExtractor port.

    Returns pre-configured image data without reading real PDF/DOCX files.
    Supports configuring extraction failures per page.
    """

    def __init__(self) -> None:
        self._images_by_source: dict[str, list[RawExtractedImage]] = {}
        self._failures_by_source: dict[str, list[dict[str, Any]]] = {}

    def configure_images(
        self, source_path: str, images: list[RawExtractedImage]
    ) -> None:
        """Pre-configure images that will be 'extracted' from a source."""
        self._images_by_source[source_path] = images

    def configure_failure(
        self, source_path: str, page: int, reason: str
    ) -> None:
        """Configure an extraction failure for a specific page."""
        if source_path not in self._failures_by_source:
            self._failures_by_source[source_path] = []
        self._failures_by_source[source_path].append(
            {"page": page, "reason": reason}
        )

    def extract(self, source_path: str) -> dict[str, Any]:
        """Extract images from the configured source.

        Returns dict with 'images' list and 'failures' list.
        """
        images = self._images_by_source.get(source_path, [])
        failures = self._failures_by_source.get(source_path, [])
        return {"images": images, "failures": failures}


@dataclass
class ImageRegistryEntry:
    """In-memory representation of an image registry entry."""

    id: str
    source_proposal: str
    agency: str
    outcome: str
    page_number: int
    caption: str
    surrounding_text: str
    figure_type: str
    file_path: str
    content_hash: str
    resolution_width: int
    resolution_height: int
    dpi: int
    quality_level: str
    size_bytes: int
    extraction_date: str
    origin_type: str = "company-created"
    compliance_flag: str | None = None
    duplicate_sources: list[str] = field(default_factory=list)


class InMemoryImageRegistryAdapter:
    """In-memory fake for ImageRegistryPort.

    Stores image registry entries in memory for fast isolated testing.
    """

    def __init__(self) -> None:
        self._entries: list[ImageRegistryEntry] = []
        self._hashes: set[str] = set()

    def add(self, entry: ImageRegistryEntry) -> bool:
        """Add an entry. Returns True if new, False if duplicate hash."""
        if entry.content_hash in self._hashes:
            # Merge source into existing entry
            for existing in self._entries:
                if existing.content_hash == entry.content_hash:
                    if entry.source_proposal not in existing.duplicate_sources:
                        existing.duplicate_sources.append(
                            entry.source_proposal
                        )
                    return False
            return False
        self._hashes.add(entry.content_hash)
        self._entries.append(entry)
        return True

    def get_by_id(self, image_id: str) -> ImageRegistryEntry | None:
        """Retrieve a single entry by ID."""
        for entry in self._entries:
            if entry.id == image_id:
                return entry
        return None

    def get_all(self) -> list[ImageRegistryEntry]:
        """Retrieve all entries."""
        return list(self._entries)

    def update_flag(
        self, image_id: str, flag: str | None
    ) -> bool:
        """Set or clear compliance flag. Returns True if entry found."""
        entry = self.get_by_id(image_id)
        if entry is None:
            return False
        entry.compliance_flag = flag
        return True

    def exists(self) -> bool:
        """Check if registry has any entries."""
        return len(self._entries) > 0

    @property
    def entry_count(self) -> int:
        return len(self._entries)
