"""Filesystem corpus scanner adapter.

Implements CorpusScanner port by scanning directories for supported files,
computing content hashes, and returning CorpusEntry objects.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from pes.domain.corpus import SUPPORTED_EXTENSIONS, CorpusEntry
from pes.ports.corpus_port import CorpusScanner


class FilesystemCorpusAdapter(CorpusScanner):
    """Scans local filesystem directories for supported document files."""

    def scan(self, directory: Path) -> list[CorpusEntry]:
        """Scan directory for supported files and return corpus entries.

        Computes SHA-256 hash of file contents for deduplication.
        Only returns entries for files with supported extensions.
        """
        if not directory.exists():
            msg = f"Directory does not exist: {directory}"
            raise FileNotFoundError(msg)

        entries: list[CorpusEntry] = []
        for file_path in sorted(directory.iterdir()):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            content = file_path.read_bytes()
            content_hash = hashlib.sha256(content).hexdigest()

            entries.append(CorpusEntry(
                path=str(file_path),
                content_hash=content_hash,
                file_type=file_path.suffix.lower(),
                size_bytes=len(content),
                source_directory=str(directory),
            ))

        return entries
