"""Unit tests for ImageExtractionService (driving port).

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (ImageExtractionService).
Driven ports (ImageExtractorPort, ImageRegistryPort) replaced with in-memory fakes.
Domain objects (ImageEntry, QualityLevel, RawImage) used as real collaborators.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from pes.domain.corpus_image import ImageEntry, QualityLevel
from pes.domain.image_extraction_service import (
    ExtractionReport,
    ImageExtractionService,
)
from pes.ports.image_extractor_port import (
    ExtractionFailure,
    ExtractionResult,
    ImageExtractorPort,
    RawImage,
)
from pes.ports.image_registry_port import ImageRegistryPort

# ---------------------------------------------------------------------------
# Fake driven ports
# ---------------------------------------------------------------------------

SYNTHETIC_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


class FakeImageExtractor(ImageExtractorPort):
    """In-memory fake returning pre-configured extraction results."""

    def __init__(self) -> None:
        self._results: dict[str, ExtractionResult] = {}

    def configure(self, path: str, result: ExtractionResult) -> None:
        self._results[path] = result

    def extract(self, file_path: Path) -> ExtractionResult:
        key = str(file_path)
        return self._results.get(key, ExtractionResult(images=[], failures=[]))


class FakeImageRegistry(ImageRegistryPort):
    """In-memory fake for image registry port."""

    def __init__(self) -> None:
        self._entries: dict[str, ImageEntry] = {}
        self._hashes: dict[str, str] = {}  # hash -> id

    def add(self, entry: ImageEntry) -> bool:
        if entry.content_hash in self._hashes:
            existing_id = self._hashes[entry.content_hash]
            existing = self._entries[existing_id]
            self._entries[existing_id] = existing.with_merged_source(
                entry.source_proposal
            )
            return False
        self._hashes[entry.content_hash] = entry.id
        self._entries[entry.id] = entry
        return True

    def get_by_id(self, image_id: str) -> ImageEntry | None:
        return self._entries.get(image_id)

    def get_all(self) -> list[ImageEntry]:
        return list(self._entries.values())

    def update_flag(self, image_id: str, flag: str | None) -> bool:
        entry = self._entries.get(image_id)
        if entry is None:
            return False
        self._entries[image_id] = entry.with_flag(flag)
        return True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_raw_image(
    page: int = 1,
    index: int = 1,
    caption: str = "Figure 1: Test Image",
    surrounding_text: str = "",
    dpi: int = 300,
    content: bytes | None = None,
) -> RawImage:
    return RawImage(
        image_bytes=content or SYNTHETIC_PNG,
        format="png",
        page_number=page,
        position_index=index,
        width=2048,
        height=1536,
        dpi=dpi,
        caption=caption,
        surrounding_text=surrounding_text,
    )


def _make_service(
    extractor: FakeImageExtractor | None = None,
    registry: FakeImageRegistry | None = None,
) -> ImageExtractionService:
    return ImageExtractionService(
        extractor=extractor or FakeImageExtractor(),
        registry=registry or FakeImageRegistry(),
    )


# ---------------------------------------------------------------------------
# Behavior 1: Classify figure type from caption/context heuristics
# ---------------------------------------------------------------------------


class TestClassifyFigureType:
    @pytest.mark.parametrize(
        "caption,expected_type",
        [
            ("Figure 3: CDES System Architecture", "system-diagram"),
            ("Figure 1: Block Diagram of RF Subsystem", "system-diagram"),
            ("Figure 7: TRL Maturation Plan", "trl-roadmap"),
            ("Figure 2: Technology Readiness Level Assessment", "trl-roadmap"),
            ("Figure 4: Organization Chart", "org-chart"),
            ("Figure 5: Project Schedule and Milestones", "schedule"),
            ("Figure 6: Gantt Chart", "schedule"),
            ("Figure 8: Concept of Operations", "concept-illustration"),
            ("Figure 9: Performance Data Results", "data-chart"),
            ("Figure 10: Process Flow Diagram", "process-flow"),
            ("Figure 11: Workflow Overview", "process-flow"),
            ("Figure 2: Prototype Assembly", "unclassified"),
            ("", "unclassified"),
        ],
    )
    def test_classifies_by_caption_keywords(
        self, caption: str, expected_type: str
    ):
        result = ImageExtractionService.classify_figure_type(caption, "")
        assert result == expected_type

    def test_surrounding_text_used_when_caption_has_no_match(self):
        result = ImageExtractionService.classify_figure_type(
            "Figure 1: Overview",
            "The system architecture shows the high-level design.",
        )
        assert result == "system-diagram"


# ---------------------------------------------------------------------------
# Behavior 2: Extract images from documents with classification and registry
# ---------------------------------------------------------------------------


class TestExtractFromDocuments:
    def test_extracts_classifies_and_registers_images(self):
        extractor = FakeImageExtractor()
        registry = FakeImageRegistry()
        img1 = _make_raw_image(
            page=7,
            caption="Figure 3: CDES System Architecture",
            content=b"img-content-1",
        )
        img2 = _make_raw_image(
            page=12,
            caption="Figure 7: TRL Maturation Plan",
            content=b"img-content-2",
        )
        extractor.configure(
            "proposal.pdf",
            ExtractionResult(images=[img1, img2], failures=[]),
        )

        service = _make_service(extractor, registry)
        report = service.extract_from_document(
            file_path=Path("proposal.pdf"),
            source_proposal="AF243-001",
        )

        assert report.total_extracted == 2
        entries = registry.get_all()
        assert len(entries) == 2
        types = {e.figure_type for e in entries}
        assert "system-diagram" in types
        assert "trl-roadmap" in types

    def test_registered_entries_have_correct_source_and_hash(self):
        extractor = FakeImageExtractor()
        registry = FakeImageRegistry()
        content = b"unique-image-bytes"
        img = _make_raw_image(page=1, content=content)
        extractor.configure(
            "doc.pdf",
            ExtractionResult(images=[img], failures=[]),
        )

        service = _make_service(extractor, registry)
        service.extract_from_document(Path("doc.pdf"), "TEST-001")

        entries = registry.get_all()
        assert len(entries) == 1
        entry = entries[0]
        assert entry.source_proposal == "TEST-001"
        assert entry.content_hash == hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# Behavior 3: Extraction report with counts by type and quality
# ---------------------------------------------------------------------------


class TestExtractionReport:
    def test_report_includes_type_and_quality_counts(self):
        extractor = FakeImageExtractor()
        registry = FakeImageRegistry()
        images = [
            _make_raw_image(page=1, caption="System Architecture", dpi=300, content=b"a"),
            _make_raw_image(page=2, caption="TRL Plan", dpi=200, content=b"b"),
            _make_raw_image(page=3, caption="Process Flow", dpi=72, content=b"c"),
        ]
        extractor.configure(
            "doc.pdf",
            ExtractionResult(images=images, failures=[]),
        )

        service = _make_service(extractor, registry)
        report = service.extract_from_document(Path("doc.pdf"), "RPT-001")

        assert report.total_extracted == 3
        assert report.counts_by_type["system-diagram"] == 1
        assert report.counts_by_type["trl-roadmap"] == 1
        assert report.counts_by_type["process-flow"] == 1
        assert report.counts_by_quality["high"] == 1
        assert report.counts_by_quality["medium"] == 1
        assert report.counts_by_quality["low"] == 1

    def test_report_includes_failures(self):
        extractor = FakeImageExtractor()
        registry = FakeImageRegistry()
        extractor.configure(
            "doc.pdf",
            ExtractionResult(
                images=[_make_raw_image(content=b"ok")],
                failures=[ExtractionFailure(page_number=14, reason="unsupported encoding")],
            ),
        )

        service = _make_service(extractor, registry)
        report = service.extract_from_document(Path("doc.pdf"), "FAIL-001")

        assert report.total_extracted == 1
        assert report.total_failed == 1


# ---------------------------------------------------------------------------
# Behavior 4: Dedup -- skip images already in registry
# ---------------------------------------------------------------------------


class TestExtractionDeduplication:
    def test_duplicate_hash_merges_source_not_duplicate_entry(self):
        extractor = FakeImageExtractor()
        registry = FakeImageRegistry()
        shared_content = b"shared-bytes"
        img = _make_raw_image(page=1, content=shared_content)

        # First extraction
        extractor.configure("a.pdf", ExtractionResult(images=[img], failures=[]))
        service = _make_service(extractor, registry)
        report1 = service.extract_from_document(Path("a.pdf"), "PROP-A")

        # Second extraction with same content
        extractor.configure("b.pdf", ExtractionResult(images=[img], failures=[]))
        report2 = service.extract_from_document(Path("b.pdf"), "PROP-B")

        entries = registry.get_all()
        assert len(entries) == 1
        assert report1.new_count == 1
        assert report2.new_count == 0
        assert report2.skipped_duplicates == 1


# ---------------------------------------------------------------------------
# Behavior 5: Text-only documents report zero images
# ---------------------------------------------------------------------------


class TestTextOnlyDocuments:
    def test_zero_images_produces_report_without_error(self):
        extractor = FakeImageExtractor()
        registry = FakeImageRegistry()
        extractor.configure(
            "text-only.pdf",
            ExtractionResult(images=[], failures=[]),
        )

        service = _make_service(extractor, registry)
        report = service.extract_from_document(Path("text-only.pdf"), "TEXT-001")

        assert report.total_extracted == 0
        assert report.new_count == 0
        assert report.total_failed == 0
        assert len(registry.get_all()) == 0
