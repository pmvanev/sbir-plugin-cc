"""Corpus domain model -- entry tracking and deduplication."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pes.ports.corpus_port import CorpusScanner


SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".txt", ".md"})


@dataclass(frozen=True)
class CorpusEntry:
    """A single document cataloged in the corpus."""

    path: str
    content_hash: str
    file_type: str
    size_bytes: int


@dataclass
class IngestionResult:
    """Outcome of a corpus ingestion operation."""

    new_entries: list[CorpusEntry] = field(default_factory=list)
    skipped_existing: int = 0
    skipped_unsupported: int = 0
    message: str = ""


class CorpusRegistry:
    """Tracks ingested corpus entries and deduplicates by content hash."""

    def __init__(self) -> None:
        self._entries: list[CorpusEntry] = []
        self._known_hashes: set[str] = set()

    @property
    def entries(self) -> list[CorpusEntry]:
        return list(self._entries)

    @property
    def document_count(self) -> int:
        return len(self._entries)

    @property
    def known_hashes(self) -> set[str]:
        return set(self._known_hashes)

    def register(self, entry: CorpusEntry) -> bool:
        """Register an entry. Returns True if new, False if duplicate."""
        if entry.content_hash in self._known_hashes:
            return False
        self._known_hashes.add(entry.content_hash)
        self._entries.append(entry)
        return True

    def load_hashes(self, hashes: set[str]) -> None:
        """Load previously known hashes for deduplication."""
        self._known_hashes.update(hashes)


class CorpusIngestionService:
    """Driving port: ingests documents from a directory into the corpus.

    Collaborators injected via constructor:
    - scanner: CorpusScanner (driven port) for file discovery and hashing
    - registry: CorpusRegistry (domain) for dedup tracking
    """

    def __init__(self, scanner: CorpusScanner, registry: CorpusRegistry) -> None:
        self._scanner = scanner
        self._registry = registry

    def ingest_directory(self, directory: Path) -> IngestionResult:
        """Scan directory and ingest supported documents.

        Returns an IngestionResult with counts and user-facing message.
        """
        if not directory.exists():
            return IngestionResult(
                message=(
                    f"Directory not found: {directory}\n"
                    f"Please verify the path and try again."
                )
            )

        if not directory.is_dir():
            return IngestionResult(message=f"Not a directory: {directory}")

        scanned = self._scanner.scan(directory)

        all_files = [f for f in directory.iterdir() if f.is_file()]
        unsupported_count = len(all_files) - len(scanned)

        if not scanned and unsupported_count == 0:
            supported_list = ", ".join(sorted(SUPPORTED_EXTENSIONS))
            return IngestionResult(
                message=f"No supported documents found. Supported types: {supported_list}"
            )

        new_entries: list[CorpusEntry] = []
        skipped_existing = 0

        for entry in scanned:
            if self._registry.register(entry):
                new_entries.append(entry)
            else:
                skipped_existing += 1

        result = IngestionResult(
            new_entries=new_entries,
            skipped_existing=skipped_existing,
            skipped_unsupported=unsupported_count,
        )
        result.message = self._build_message(result)
        return result

    def _build_message(self, result: IngestionResult) -> str:
        new_count = len(result.new_entries)

        if result.skipped_existing > 0 and new_count > 0:
            return (
                f"{new_count} new document ingested. "
                f"{result.skipped_existing} already in corpus."
            )

        if result.skipped_existing > 0 and new_count == 0:
            return f"No new documents. {result.skipped_existing} already in corpus."

        if result.skipped_unsupported > 0:
            return (
                f"Ingested {new_count} documents. "
                f"Skipped {result.skipped_unsupported} unsupported files."
            )

        type_counts: dict[str, int] = {}
        for entry in result.new_entries:
            ext = entry.file_type
            type_counts[ext] = type_counts.get(ext, 0) + 1

        type_summary = ", ".join(
            f"{count} {ext.lstrip('.')}s" if count > 1 else f"{count} {ext.lstrip('.')}"
            for ext, count in sorted(type_counts.items())
        )

        return f"Ingested {new_count} documents ({type_summary})"
