"""Port interface for artifact writing.

Driven port: ArtifactWriter
Adapters implement this to write artifacts to storage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ArtifactWriter(ABC):
    """Write artifacts (text and JSON) to a storage location -- driven port."""

    @abstractmethod
    def write_artifact(self, path: str, content: str) -> None:
        """Write text content to the given path, creating directories as needed."""

    @abstractmethod
    def write_json(self, path: str, data: dict[str, object]) -> None:
        """Write data as formatted JSON to the given path, creating directories as needed."""
