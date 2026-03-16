"""Unit tests for ImageFitnessService (driving port).

Test Budget: 7 behaviors x 2 = 14 unit tests max.
Tests enter through driving port (ImageFitnessService).
Driven port (ImageRegistryPort) replaced with in-memory fake.
Domain objects used as real collaborators.

Behaviors:
1. Quality assessment: PASS/WARN/FAIL from DPI thresholds
2. Freshness assessment: OK/WARNING/STALE from extraction age
3. Agency match: YES/NO based on current proposal agency
4. Caption analysis: detect proposal-specific terms
5. Compliance flagging: set flag with reason
6. Compliance unflagging: clear flag
7. Full assessment report: combined fitness result
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from pes.domain.corpus_image import ImageEntry, QualityLevel
from pes.domain.image_fitness_service import (
    CaptionAnalysisResult,
    FitnessAssessment,
    ImageFitnessService,
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
    dpi: int = 300,
    extraction_date: str | None = None,
    agency: str = "USAF",
    origin_type: str = "company-created",
    caption: str = "Figure 1: Test Image",
) -> ImageEntry:
    if extraction_date is None:
        extraction_date = datetime.now().strftime("%Y-%m-%d")
    return ImageEntry(
        id=image_id,
        source_proposal="TEST-001",
        page_number=7,
        caption=caption,
        figure_type="system-diagram",
        dpi=dpi,
        content_hash=f"hash-{image_id}",
        quality_level=QualityLevel.from_dpi(dpi),
        extraction_date=extraction_date,
        agency=agency,
        origin_type=origin_type,
    )


def _make_service(
    registry: FakeImageRegistry | None = None,
) -> tuple[ImageFitnessService, FakeImageRegistry]:
    reg = registry or FakeImageRegistry()
    return ImageFitnessService(registry=reg), reg


def _date_months_ago(months: int) -> str:
    return (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Behavior 1: Quality assessment (PASS/WARN/FAIL from DPI)
# ---------------------------------------------------------------------------


class TestQualityAssessment:
    @pytest.mark.parametrize(
        "dpi,expected_status",
        [
            (300, "PASS"),
            (600, "PASS"),
            (299, "WARN"),
            (150, "WARN"),
            (149, "FAIL"),
            (72, "FAIL"),
        ],
    )
    def test_quality_status_from_dpi(self, dpi: int, expected_status: str):
        service, registry = _make_service()
        entry = _make_entry(dpi=dpi)
        registry.add(entry)

        assessment = service.assess(entry.id)

        assert assessment.quality_status == expected_status
        assert f"{dpi} DPI" in assessment.quality_detail


# ---------------------------------------------------------------------------
# Behavior 2: Freshness assessment (OK/WARNING/STALE from age)
# ---------------------------------------------------------------------------


class TestFreshnessAssessment:
    @pytest.mark.parametrize(
        "months,expected_status",
        [
            (0, "OK"),
            (8, "OK"),
            (12, "OK"),
            (13, "WARNING"),
            (24, "WARNING"),
            (25, "STALE"),
            (36, "STALE"),
        ],
    )
    def test_freshness_status_from_age(self, months: int, expected_status: str):
        service, registry = _make_service()
        entry = _make_entry(extraction_date=_date_months_ago(months))
        registry.add(entry)

        assessment = service.assess(entry.id)

        assert assessment.freshness_status == expected_status


# ---------------------------------------------------------------------------
# Behavior 3: Agency match (YES/NO)
# ---------------------------------------------------------------------------


class TestAgencyMatch:
    @pytest.mark.parametrize(
        "image_agency,current_agency,expected",
        [
            ("USAF", "USAF", "YES"),
            ("USAF", "DARPA", "NO"),
            ("DARPA", "", "NO"),
        ],
    )
    def test_agency_match(
        self, image_agency: str, current_agency: str, expected: str
    ):
        service, registry = _make_service()
        entry = _make_entry(agency=image_agency)
        registry.add(entry)

        assessment = service.assess(entry.id, current_agency=current_agency)

        assert assessment.agency_match == expected


# ---------------------------------------------------------------------------
# Behavior 4: Caption analysis (detect proposal-specific terms)
# ---------------------------------------------------------------------------


class TestCaptionAnalysis:
    def test_flags_proposal_specific_terms_in_caption(self):
        result = ImageFitnessService.analyze_caption(
            "Figure 3: CDES System Architecture for Maritime Defense",
            known_terms=["CDES"],
        )

        assert "CDES" in result.flagged_terms
        assert len(result.warnings) > 0

    def test_no_warnings_when_no_terms_match(self):
        result = ImageFitnessService.analyze_caption(
            "Figure 1: Organization Chart",
            known_terms=["CDES", "AF243-001"],
        )

        assert result.flagged_terms == []
        assert result.warnings == []


# ---------------------------------------------------------------------------
# Behavior 5: Compliance flagging
# ---------------------------------------------------------------------------


class TestComplianceFlagging:
    def test_flag_image_sets_compliance_flag(self):
        service, registry = _make_service()
        entry = _make_entry()
        registry.add(entry)

        result = service.flag_image(entry.id, "possible government-furnished")

        assert result is True
        updated = registry.get_by_id(entry.id)
        assert updated is not None
        assert updated.compliance_flag == "possible government-furnished"


# ---------------------------------------------------------------------------
# Behavior 6: Compliance unflagging
# ---------------------------------------------------------------------------


class TestComplianceUnflagging:
    def test_unflag_image_clears_compliance_flag(self):
        service, registry = _make_service()
        entry = _make_entry()
        registry.add(entry)
        service.flag_image(entry.id, "test-reason")

        result = service.unflag_image(entry.id)

        assert result is True
        updated = registry.get_by_id(entry.id)
        assert updated is not None
        assert updated.compliance_flag is None


# ---------------------------------------------------------------------------
# Behavior 7: Full assessment includes all dimensions
# ---------------------------------------------------------------------------


class TestFullAssessment:
    def test_assessment_includes_all_fitness_dimensions(self):
        service, registry = _make_service()
        entry = _make_entry(
            dpi=300,
            extraction_date=_date_months_ago(6),
            agency="USAF",
        )
        registry.add(entry)

        assessment = service.assess(entry.id, current_agency="USAF")

        assert assessment.quality_status == "PASS"
        assert assessment.freshness_status == "OK"
        assert assessment.agency_match == "YES"
        assert assessment.quality_detail is not None
        assert assessment.freshness_detail is not None
