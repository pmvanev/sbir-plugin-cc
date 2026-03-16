"""Port interface for image registry persistence.

Driven port: ImageRegistryPort
Adapters implement this to store and retrieve image catalog entries.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pes.domain.corpus_image import ImageEntry


class ImageRegistryPort(ABC):
    """Read/write image registry entries -- driven port."""

    @abstractmethod
    def add(self, entry: ImageEntry) -> bool:
        """Add an image entry.

        Returns True if new entry added.
        Returns False if duplicate hash exists (merges source proposal).
        """

    @abstractmethod
    def get_by_id(self, image_id: str) -> ImageEntry | None:
        """Retrieve a single entry by ID, or None if not found."""

    @abstractmethod
    def get_all(self) -> list[ImageEntry]:
        """Retrieve all registry entries."""

    @abstractmethod
    def update_flag(self, image_id: str, flag: str | None) -> bool:
        """Set or clear compliance flag on an entry.

        Returns True if entry found and updated, False if not found.
        """
