"""Port interface for corpus scanning.

Driven port: CorpusScanner
Adapters implement this to scan directories for document files.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from pes.domain.corpus import CorpusEntry


class CorpusScanner(ABC):
    """Scan a directory for supported document files -- driven port."""

    @abstractmethod
    def scan(self, directory: Path) -> list[CorpusEntry]:
        """Scan directory and return entries for all supported files.

        Returns CorpusEntry for each supported file found.
        Does not filter by hash -- that is the registry's job.

        Raises:
            FileNotFoundError: if directory does not exist.
        """
