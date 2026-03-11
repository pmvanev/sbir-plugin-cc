"""Unit tests for corpus ingestion through CorpusIngestionService (driving port).

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (CorpusIngestionService).
CorpusScanner driven port replaced with in-memory fake.
Domain objects (CorpusRegistry, CorpusEntry) used as real collaborators.
"""

from __future__ import annotations

from pathlib import Path

from pes.domain.corpus import (
    SUPPORTED_EXTENSIONS,
    CorpusEntry,
    CorpusIngestionService,
    CorpusRegistry,
)
from pes.ports.corpus_port import CorpusScanner

# ---------------------------------------------------------------------------
# Fake driven port -- returns pre-configured entries
# ---------------------------------------------------------------------------


class FakeCorpusScanner(CorpusScanner):
    """In-memory fake that returns pre-configured corpus entries."""

    def __init__(self, entries: list[CorpusEntry] | None = None) -> None:
        self._entries = entries or []

    def scan(self, directory: Path) -> list[CorpusEntry]:
        return list(self._entries)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_entry(name: str, ext: str, content: str = "content") -> CorpusEntry:
    """Create a CorpusEntry with deterministic hash from content."""
    import hashlib

    content_hash = hashlib.sha256(content.encode()).hexdigest()
    return CorpusEntry(
        path=f"/fake/{name}{ext}",
        content_hash=content_hash,
        file_type=ext,
        size_bytes=len(content),
    )


def _make_service(
    entries: list[CorpusEntry] | None = None,
    registry: CorpusRegistry | None = None,
) -> CorpusIngestionService:
    """Wire CorpusIngestionService with fake scanner and optional registry."""
    scanner = FakeCorpusScanner(entries)
    reg = registry or CorpusRegistry()
    return CorpusIngestionService(scanner, reg)


# ---------------------------------------------------------------------------
# Behavior 1: Ingests supported files and reports count/type
# ---------------------------------------------------------------------------


class TestCorpusIngestionHappyPath:
    def test_ingests_supported_files_and_reports_count_by_type(self, tmp_path: Path):
        entries = [
            _make_entry("proposal-1", ".pdf", "pdf1"),
            _make_entry("proposal-2", ".pdf", "pdf2"),
            _make_entry("debrief-1", ".docx", "docx1"),
        ]
        # Create actual directory with matching files (for iterdir count)
        corpus_dir = tmp_path / "docs"
        corpus_dir.mkdir()
        for e in entries:
            (corpus_dir / Path(e.path).name).write_text("x")

        service = _make_service(entries)
        result = service.ingest_directory(corpus_dir)

        assert len(result.new_entries) == 3
        assert "Ingested 3 documents" in result.message

    def test_ingested_documents_registered_in_corpus(self, tmp_path: Path):
        entries = [_make_entry("doc", ".pdf", "content")]
        corpus_dir = tmp_path / "docs"
        corpus_dir.mkdir()
        (corpus_dir / "doc.pdf").write_text("x")

        registry = CorpusRegistry()
        service = _make_service(entries, registry)
        service.ingest_directory(corpus_dir)

        assert registry.document_count == 1


# ---------------------------------------------------------------------------
# Behavior 2: Re-ingestion deduplicates by content hash
# ---------------------------------------------------------------------------


class TestCorpusDeduplication:
    def test_re_ingestion_adds_only_new_files(self, tmp_path: Path):
        existing = _make_entry("old", ".pdf", "old-content")
        new = _make_entry("new", ".pdf", "new-content")

        corpus_dir = tmp_path / "docs"
        corpus_dir.mkdir()
        (corpus_dir / "old.pdf").write_text("x")
        (corpus_dir / "new.pdf").write_text("x")

        registry = CorpusRegistry()
        # Simulate prior ingestion
        registry.register(existing)

        service = _make_service([existing, new], registry)
        result = service.ingest_directory(corpus_dir)

        assert len(result.new_entries) == 1
        assert result.skipped_existing == 1
        assert "1 new document" in result.message
        assert "1 already in corpus" in result.message

    def test_all_duplicates_reports_no_new(self, tmp_path: Path):
        entry = _make_entry("doc", ".pdf", "same")

        corpus_dir = tmp_path / "docs"
        corpus_dir.mkdir()
        (corpus_dir / "doc.pdf").write_text("x")

        registry = CorpusRegistry()
        registry.register(entry)

        service = _make_service([entry], registry)
        result = service.ingest_directory(corpus_dir)

        assert len(result.new_entries) == 0
        assert result.skipped_existing == 1


# ---------------------------------------------------------------------------
# Behavior 3: Skips unsupported file types with count
# ---------------------------------------------------------------------------


class TestCorpusUnsupportedFiles:
    def test_reports_skipped_unsupported_files(self, tmp_path: Path):
        supported = [_make_entry("doc", ".pdf", "pdf")]

        corpus_dir = tmp_path / "mixed"
        corpus_dir.mkdir()
        (corpus_dir / "doc.pdf").write_text("x")
        # Create unsupported files
        for i in range(3):
            (corpus_dir / f"script-{i}.py").write_text("x")

        service = _make_service(supported)
        result = service.ingest_directory(corpus_dir)

        assert len(result.new_entries) == 1
        assert result.skipped_unsupported == 3
        assert "Skipped 3 unsupported" in result.message


# ---------------------------------------------------------------------------
# Behavior 4: Empty directory produces helpful message
# ---------------------------------------------------------------------------


class TestCorpusEmptyDirectory:
    def test_empty_directory_shows_supported_formats(self, tmp_path: Path):
        corpus_dir = tmp_path / "empty"
        corpus_dir.mkdir()

        service = _make_service([])
        result = service.ingest_directory(corpus_dir)

        assert "No supported documents found" in result.message
        for ext in SUPPORTED_EXTENSIONS:
            assert ext in result.message


# ---------------------------------------------------------------------------
# Behavior 5: Non-existent directory rejected
# ---------------------------------------------------------------------------


class TestCorpusNonExistentDirectory:
    def test_nonexistent_directory_produces_error(self, tmp_path: Path):
        missing = tmp_path / "does-not-exist"

        service = _make_service([])
        result = service.ingest_directory(missing)

        assert "Directory not found" in result.message
        assert len(result.new_entries) == 0

    def test_nonexistent_directory_includes_path_guidance(self, tmp_path: Path):
        missing = tmp_path / "nope"

        service = _make_service([])
        result = service.ingest_directory(missing)

        assert "verify" in result.message.lower() or "path" in result.message.lower()
