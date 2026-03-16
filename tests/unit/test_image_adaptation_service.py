"""Unit tests for ImageAdaptationService (driving port).

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (ImageAdaptationService).
Driven port (ImageRegistryPort) replaced with in-memory fake.
Domain objects used as real collaborators.

Behaviors:
1. Caption adaptation: remove proposal-specific terms, update figure number
2. Generic caption: no terms to remove, update figure number only
3. Manual review items: generated for diagram types with embedded text risk
4. Compliance-flagged image: blocked with error message
5. Image not found: returns SelectionError
"""

from __future__ import annotations

import pytest

from pes.domain.corpus_image import ImageEntry, QualityLevel
from pes.domain.image_adaptation_service import (
    AdaptationResult,
    ImageAdaptationService,
    SelectionError,
)
from pes.ports.image_registry_port import ImageRegistryPort


# ---------------------------------------------------------------------------
# Fake driven port
# ---------------------------------------------------------------------------


class FakeImageRegistry(ImageRegistryPort):
    """In-memory fake for image registry port."""

    def __init__(self) -> None:
        self._entries: dict[str, ImageEntry] = {}
        self._hashes: dict[str, str] = {}

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


def _make_entry(
    image_id: str = "test-img-01",
    caption: str = "Figure 3: CDES System Architecture",
    source_proposal: str = "AF243-001",
    figure_type: str = "system-diagram",
    compliance_flag: str | None = None,
) -> ImageEntry:
    return ImageEntry(
        id=image_id,
        source_proposal=source_proposal,
        page_number=7,
        caption=caption,
        figure_type=figure_type,
        dpi=300,
        content_hash=f"hash-{image_id}",
        quality_level=QualityLevel.HIGH,
        extraction_date="2025-07-16",
        agency="USAF",
        compliance_flag=compliance_flag,
    )


def _make_service(
    registry: FakeImageRegistry | None = None,
) -> tuple[ImageAdaptationService, FakeImageRegistry]:
    reg = registry or FakeImageRegistry()
    return ImageAdaptationService(registry=reg), reg


# ---------------------------------------------------------------------------
# Behavior 1: Caption adaptation (remove terms + update figure number)
# ---------------------------------------------------------------------------


class TestCaptionAdaptation:
    def test_removes_proposal_specific_terms_and_updates_figure_number(self):
        service, registry = _make_service()
        entry = _make_entry(caption="Figure 3: CDES System Architecture")
        registry.add(entry)

        result = service.select_for_reuse(
            image_id=entry.id,
            figure_number=5,
            section_id="technical-approach",
            proposal_specific_terms=["CDES"],
        )

        assert isinstance(result, AdaptationResult)
        assert result.adapted_caption == "Figure 5: System Architecture"
        assert result.original_caption == "Figure 3: CDES System Architecture"
        assert result.figure_number == 5
        assert result.section_id == "technical-approach"
        assert result.file_copied is True

    def test_returns_figure_inventory_entry_with_corpus_reuse_method(self):
        service, registry = _make_service()
        entry = _make_entry()
        registry.add(entry)

        result = service.select_for_reuse(
            image_id=entry.id,
            figure_number=3,
            section_id="technical-approach",
        )

        assert isinstance(result, AdaptationResult)
        assert result.figure_inventory_entry["generation_method"] == "corpus-reuse"
        assert result.figure_inventory_entry["figure_number"] == 3

    def test_returns_attribution_from_source_proposal(self):
        service, registry = _make_service()
        entry = _make_entry(source_proposal="AF243-001")
        registry.add(entry)

        result = service.select_for_reuse(
            image_id=entry.id,
            figure_number=3,
            section_id="technical-approach",
        )

        assert isinstance(result, AdaptationResult)
        assert result.attribution["source_proposal"] == "AF243-001"


# ---------------------------------------------------------------------------
# Behavior 2: Generic caption (no terms to remove)
# ---------------------------------------------------------------------------


class TestGenericCaptionReuse:
    def test_updates_figure_number_without_term_removal(self):
        service, registry = _make_service()
        entry = _make_entry(caption="Figure 4: Organization Chart")
        registry.add(entry)

        result = service.select_for_reuse(
            image_id=entry.id,
            figure_number=2,
            proposal_specific_terms=[],
        )

        assert isinstance(result, AdaptationResult)
        assert result.adapted_caption == "Figure 2: Organization Chart"
        assert result.warnings == []


# ---------------------------------------------------------------------------
# Behavior 3: Manual review items for diagram types
# ---------------------------------------------------------------------------


class TestManualReviewItems:
    @pytest.mark.parametrize(
        "figure_type,expect_items",
        [
            ("system-diagram", True),
            ("process-flow", True),
            ("org-chart", False),
        ],
    )
    def test_generates_review_items_for_diagram_types(
        self, figure_type: str, expect_items: bool
    ):
        service, registry = _make_service()
        entry = _make_entry(figure_type=figure_type)
        registry.add(entry)

        items = service.generate_review_items(
            image_id=entry.id,
            figure_type=figure_type,
        )

        if expect_items:
            assert len(items) > 0
        else:
            assert len(items) == 0


# ---------------------------------------------------------------------------
# Behavior 4: Compliance-flagged image blocked
# ---------------------------------------------------------------------------


class TestComplianceFlaggedBlocked:
    def test_blocks_flagged_image_with_error_message(self):
        service, registry = _make_service()
        entry = _make_entry(compliance_flag="possible government-furnished")
        registry.add(entry)

        result = service.select_for_reuse(
            image_id=entry.id,
            figure_number=1,
        )

        assert isinstance(result, SelectionError)
        assert result.blocked is True
        assert "flagged" in result.message.lower()


# ---------------------------------------------------------------------------
# Behavior 5: Image not found
# ---------------------------------------------------------------------------


class TestImageNotFound:
    def test_returns_error_for_nonexistent_image(self):
        service, registry = _make_service()

        result = service.select_for_reuse(
            image_id="nonexistent-id",
            figure_number=1,
        )

        assert isinstance(result, SelectionError)
        assert result.blocked is True
        assert "not found" in result.message.lower()
