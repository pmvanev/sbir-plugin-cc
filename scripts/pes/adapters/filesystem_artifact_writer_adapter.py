"""Filesystem artifact writer adapter.

Implements ArtifactWriter port by writing to the local filesystem.
"""

from __future__ import annotations

import json
from pathlib import Path

from pes.ports.artifact_writer_port import ArtifactWriter


class FilesystemArtifactWriter(ArtifactWriter):
    """Writes artifacts to the local filesystem."""

    def write_artifact(self, path: str, content: str) -> None:
        """Write text content to path, creating parent directories as needed."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def write_json(self, path: str, data: dict[str, object]) -> None:
        """Write data as formatted JSON to path, creating parent directories as needed."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")
