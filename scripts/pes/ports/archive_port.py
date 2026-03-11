"""Port interface for archive creation.

Driven port: ArchiveCreator
Adapters implement this to create immutable archives from source directories.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ArchiveCreator(ABC):
    """Create an immutable archive by copying files -- driven port."""

    @abstractmethod
    def create_archive(self, source_dir: str, dest_dir: str) -> None:
        """Copy all files from source_dir into dest_dir.

        Both directories must exist. Only copies regular files (not subdirectories).
        """
