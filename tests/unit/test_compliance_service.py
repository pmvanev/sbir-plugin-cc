"""Unit tests for compliance matrix through ComplianceService (driving port).

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (ComplianceService).
ComplianceExtractor driven port replaced with fake.
Domain objects (ComplianceItem, ComplianceMatrix) are real collaborators.
"""

from __future__ import annotations

import pytest

from pes.domain.compliance import (
    ComplianceItem,
    ComplianceMatrix,
    CoverageStatus,
    RequirementType,
)
from pes.domain.compliance_service import ComplianceService
from pes.ports.compliance_port import ComplianceExtractor

# ---------------------------------------------------------------------------
# Fake driven port
# ---------------------------------------------------------------------------


class FakeComplianceExtractor(ComplianceExtractor):
    """Returns pre-configured compliance items."""

    def __init__(self, items: list[ComplianceItem] | None = None) -> None:
        self._items = items or []

    def extract(self, text: str) -> list[ComplianceItem]:
        return list(self._items)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_SOLICITATION = """
Topic ID: AF243-001
The contractor shall provide a prototype within 6 months.
The proposal shall not exceed 25 pages.
Format: All submissions must use 12-point Times New Roman font.
Evaluation criteria include technical merit and cost realism.
Section 3 shall include a risk mitigation plan.
"""

SAMPLE_ITEMS = [
    ComplianceItem(
        item_id=1,
        text="The contractor shall provide a prototype within 6 months",
        requirement_type=RequirementType.SHALL,
        proposal_section="Technical Volume",
    ),
    ComplianceItem(
        item_id=2,
        text="The proposal shall not exceed 25 pages",
        requirement_type=RequirementType.FORMAT,
        proposal_section="All Sections",
    ),
    ComplianceItem(
        item_id=3,
        text="All submissions must use 12-point Times New Roman font",
        requirement_type=RequirementType.FORMAT,
        proposal_section="All Sections",
    ),
    ComplianceItem(
        item_id=4,
        text="Technical merit evaluation criteria",
        requirement_type=RequirementType.IMPLICIT,
        proposal_section="Technical Volume",
        ambiguity="Implicit from evaluation criteria -- verify weighting",
    ),
    ComplianceItem(
        item_id=5,
        text="Cost realism evaluation criteria",
        requirement_type=RequirementType.IMPLICIT,
        proposal_section="Cost Volume",
        ambiguity="Implicit from evaluation criteria -- verify scope",
    ),
    ComplianceItem(
        item_id=6,
        text="Section 3 shall include a risk mitigation plan",
        requirement_type=RequirementType.SHALL,
        proposal_section="Section 3",
    ),
]


def _make_service(
    items: list[ComplianceItem] | None = None,
) -> ComplianceService:
    """Wire ComplianceService with fake extractor."""
    extractor = FakeComplianceExtractor(items if items is not None else SAMPLE_ITEMS)
    return ComplianceService(extractor)


# ---------------------------------------------------------------------------
# Behavior 1: Extracts shall-statements, format, and implicit requirements
# ---------------------------------------------------------------------------


class TestExtractRequirements:
    def test_extracts_all_requirement_types(self):
        service = _make_service()

        matrix = service.generate_matrix(SAMPLE_SOLICITATION)

        types = {item.requirement_type for item in matrix.items}
        assert RequirementType.SHALL in types
        assert RequirementType.FORMAT in types
        assert RequirementType.IMPLICIT in types

    def test_preserves_item_count_from_extraction(self):
        service = _make_service()

        matrix = service.generate_matrix(SAMPLE_SOLICITATION)

        assert matrix.item_count == 6


# ---------------------------------------------------------------------------
# Behavior 2: Maps items to sections and flags ambiguities
# ---------------------------------------------------------------------------


class TestSectionMappingAndAmbiguities:
    def test_maps_items_to_proposal_sections(self):
        service = _make_service()

        matrix = service.generate_matrix(SAMPLE_SOLICITATION)

        mapped = [i for i in matrix.items if i.proposal_section is not None]
        assert len(mapped) == 6

    def test_flags_ambiguous_items_with_explanations(self):
        service = _make_service()

        matrix = service.generate_matrix(SAMPLE_SOLICITATION)

        ambiguous = [i for i in matrix.items if i.ambiguity is not None]
        assert len(ambiguous) >= 2
        assert all(len(a.ambiguity) > 0 for a in ambiguous)


# ---------------------------------------------------------------------------
# Behavior 3: Low extraction count produces warning
# ---------------------------------------------------------------------------


class TestLowExtractionWarning:
    @pytest.mark.parametrize("count,expect_warning", [
        (2, True),
        (4, True),
        (5, False),
        (10, False),
    ])
    def test_warns_on_low_extraction_count(self, count, expect_warning):
        items = [
            ComplianceItem(
                item_id=i,
                text=f"Requirement {i}",
                requirement_type=RequirementType.SHALL,
                proposal_section="Technical Volume",
            )
            for i in range(1, count + 1)
        ]
        service = _make_service(items=items)

        matrix = service.generate_matrix(SAMPLE_SOLICITATION)

        has_warning = any("low" in w.lower() or "few" in w.lower() for w in matrix.warnings)
        assert has_warning == expect_warning


# ---------------------------------------------------------------------------
# Behavior 4: Manual add via /proposal compliance add
# ---------------------------------------------------------------------------


class TestManualAdd:
    def test_adds_item_marked_as_manual(self):
        service = _make_service()
        matrix = service.generate_matrix(SAMPLE_SOLICITATION)
        original_count = matrix.item_count

        updated = service.add_item(
            matrix, "Section 3 shall include risk mitigation table"
        )

        assert updated.item_count == original_count + 1
        new_item = updated.items[-1]
        assert new_item.requirement_type == RequirementType.MANUAL
        assert "risk mitigation table" in new_item.text

    def test_maps_manual_item_to_section_from_text(self):
        service = _make_service()
        matrix = service.generate_matrix(SAMPLE_SOLICITATION)

        updated = service.add_item(
            matrix, "Section 3 shall include risk mitigation table"
        )

        new_item = updated.items[-1]
        assert new_item.proposal_section is not None
        assert "3" in new_item.proposal_section


# ---------------------------------------------------------------------------
# Behavior 5: Coverage summary formatting
# ---------------------------------------------------------------------------


class TestCoverageSummary:
    def test_shows_coverage_breakdown(self):
        items = [
            ComplianceItem(
                item_id=i,
                text=f"Req {i}",
                requirement_type=RequirementType.SHALL,
                status=CoverageStatus.COVERED if i <= 12 else CoverageStatus.NOT_STARTED,
            )
            for i in range(1, 48)
        ]
        matrix = ComplianceMatrix(items=items)

        summary = matrix.coverage_summary()

        assert "12/47 covered" in summary
        assert "0 partial" in summary
        assert "35 not started" in summary
