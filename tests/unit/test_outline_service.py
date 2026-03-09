"""Unit tests for OutlineService (driving port) -- proposal outline generation.

Test Budget: 4 behaviors x 2 = 8 unit tests max.
Tests enter through driving port (OutlineService).
Driven port (OutlineGenerator) mocked at port boundary.
Domain objects (ProposalOutline, OutlineSection) are real collaborators.

Behaviors:
1. Generate outline mapping all compliance items to sections
2. Section page budgets total to solicitation page limit or fewer
3. Unmapped compliance items flagged with item IDs listed
4. Generation without approved discrimination table raises error
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.outline import OutlineSection, ProposalOutline
from pes.domain.outline_service import (
    DiscriminationApprovalRequiredError,
    OutlineService,
)


# ---------------------------------------------------------------------------
# Fake driven port (OutlineGenerator) at port boundary
# ---------------------------------------------------------------------------


class FakeOutlineGenerator:
    """Fake driven port that produces deterministic proposal outlines."""

    def __init__(
        self,
        *,
        unmapped_ids: list[str] | None = None,
        total_pages: float = 25.0,
    ) -> None:
        self.generate_called_with: dict[str, Any] | None = None
        self._unmapped_ids = unmapped_ids or []
        self._total_pages = total_pages

    def generate(
        self,
        discrimination_table: dict[str, Any],
        compliance_matrix: dict[str, Any],
        *,
        page_limit: float,
    ) -> ProposalOutline:
        self.generate_called_with = {
            "discrimination_table": discrimination_table,
            "compliance_matrix": compliance_matrix,
            "page_limit": page_limit,
        }

        # Derive compliance item IDs from matrix
        all_item_ids: list[str] = [
            item["id"] for item in compliance_matrix.get("items", [])
        ]
        mapped_ids = [
            cid for cid in all_item_ids if cid not in self._unmapped_ids
        ]

        # Split mapped items across 3 sections
        per_section = max(1, len(mapped_ids) // 3)
        section_groups = [
            mapped_ids[:per_section],
            mapped_ids[per_section : 2 * per_section],
            mapped_ids[2 * per_section :],
        ]

        page_per_section = self._total_pages / 3.0

        sections = [
            OutlineSection(
                section_id=f"sec-{i + 1}",
                title=f"Section {i + 1}",
                compliance_item_ids=group,
                page_budget=round(page_per_section, 1),
                figure_placeholders=[f"fig-{i + 1}-1"],
                thesis_statement=f"Thesis for section {i + 1}",
            )
            for i, group in enumerate(section_groups)
            if group  # only create sections that have items
        ]

        return ProposalOutline(sections=sections)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_compliance_matrix(item_count: int = 47) -> dict[str, Any]:
    """Build a compliance matrix with the given number of items."""
    return {
        "item_count": item_count,
        "items": [{"id": f"CI-{i + 1:03d}"} for i in range(item_count)],
    }


SAMPLE_DISCRIMINATION_TABLE: dict[str, Any] = {
    "items": [
        {"category": "company_strengths", "claim": "Superior facility"},
        {"category": "technical_approach", "claim": "Novel beam-steering"},
    ],
    "approved_at": "2026-03-01T00:00:00Z",
}

UNAPPROVED_DISCRIMINATION_TABLE: dict[str, Any] = {
    "items": [
        {"category": "company_strengths", "claim": "Superior facility"},
    ],
    "approved_at": None,
}


def _make_service(
    generator: FakeOutlineGenerator | None = None,
) -> tuple[OutlineService, FakeOutlineGenerator]:
    gen = generator or FakeOutlineGenerator()
    return OutlineService(outline_generator=gen), gen


# ---------------------------------------------------------------------------
# Behavior 1: Generate outline mapping all compliance items to sections
# ---------------------------------------------------------------------------


class TestGenerateOutlineMapping:
    def test_every_compliance_item_mapped_to_at_least_one_section(self):
        matrix = _make_compliance_matrix(47)
        service, _gen = _make_service()

        result = service.generate_outline(
            discrimination_table=SAMPLE_DISCRIMINATION_TABLE,
            compliance_matrix=matrix,
            page_limit=25.0,
        )

        all_mapped_ids: set[str] = set()
        for section in result.outline.sections:
            all_mapped_ids.update(section.compliance_item_ids)

        expected_ids = {f"CI-{i + 1:03d}" for i in range(47)}
        assert expected_ids == all_mapped_ids

    def test_delegates_discrimination_table_and_matrix_to_generator(self):
        matrix = _make_compliance_matrix(6)
        service, gen = _make_service()

        service.generate_outline(
            discrimination_table=SAMPLE_DISCRIMINATION_TABLE,
            compliance_matrix=matrix,
            page_limit=25.0,
        )

        assert gen.generate_called_with is not None
        assert gen.generate_called_with["discrimination_table"] is SAMPLE_DISCRIMINATION_TABLE
        assert gen.generate_called_with["compliance_matrix"] is matrix
        assert gen.generate_called_with["page_limit"] == 25.0


# ---------------------------------------------------------------------------
# Behavior 2: Section page budgets total to solicitation page limit or fewer
# ---------------------------------------------------------------------------


class TestPageBudgetCompliance:
    @pytest.mark.parametrize(
        "total_pages,page_limit",
        [
            (25.0, 25.0),
            (20.0, 25.0),
            (10.0, 25.0),
        ],
    )
    def test_total_page_budget_within_limit(self, total_pages, page_limit):
        gen = FakeOutlineGenerator(total_pages=total_pages)
        service, _ = _make_service(gen)

        result = service.generate_outline(
            discrimination_table=SAMPLE_DISCRIMINATION_TABLE,
            compliance_matrix=_make_compliance_matrix(6),
            page_limit=page_limit,
        )

        assert result.outline.total_page_budget <= page_limit


# ---------------------------------------------------------------------------
# Behavior 3: Unmapped compliance items flagged with item IDs listed
# ---------------------------------------------------------------------------


class TestUnmappedComplianceItems:
    def test_flags_unmapped_items_with_ids(self):
        unmapped = ["CI-045", "CI-046", "CI-047"]
        gen = FakeOutlineGenerator(unmapped_ids=unmapped)
        service, _ = _make_service(gen)

        result = service.generate_outline(
            discrimination_table=SAMPLE_DISCRIMINATION_TABLE,
            compliance_matrix=_make_compliance_matrix(47),
            page_limit=25.0,
        )

        assert result.unmapped_item_ids == unmapped

    def test_no_unmapped_items_returns_empty_list(self):
        service, _ = _make_service()

        result = service.generate_outline(
            discrimination_table=SAMPLE_DISCRIMINATION_TABLE,
            compliance_matrix=_make_compliance_matrix(6),
            page_limit=25.0,
        )

        assert result.unmapped_item_ids == []


# ---------------------------------------------------------------------------
# Behavior 4: Generation without approved discrimination table raises error
# ---------------------------------------------------------------------------


class TestGenerateWithoutDiscriminationApproval:
    def test_raises_discrimination_approval_required_error(self):
        service, _gen = _make_service()

        with pytest.raises(DiscriminationApprovalRequiredError) as exc_info:
            service.generate_outline(
                discrimination_table=UNAPPROVED_DISCRIMINATION_TABLE,
                compliance_matrix=_make_compliance_matrix(6),
                page_limit=25.0,
            )

        assert "approved discrimination table required" in str(exc_info.value).lower()

    def test_raises_error_when_discrimination_table_is_none(self):
        service, _gen = _make_service()

        with pytest.raises(DiscriminationApprovalRequiredError):
            service.generate_outline(
                discrimination_table=None,
                compliance_matrix=_make_compliance_matrix(6),
                page_limit=25.0,
            )
