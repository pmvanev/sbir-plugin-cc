"""Unit tests for DraftService (driving port) -- section drafting with compliance tracking.

Test Budget: 6 behaviors x 2 = 12 unit tests max.
Tests enter through driving port (DraftService).
Driven port (SectionDrafter) mocked at port boundary.
Domain objects (SectionDraft, OutlineSection, ProposalOutline) are real collaborators.

Behaviors:
1. Section drafted addressing mapped compliance items
2. Draft word count reported against section page budget
3. Section exceeding page budget produces warning
4. Unaddressed compliance items in a section flagged by item ID
5. Drafting without approved outline raises descriptive error
6. Attempting to draft an undefined section returns guidance on available sections
"""

from __future__ import annotations

import pytest

from pes.domain.draft import SectionDraft
from pes.domain.draft_service import (
    ApprovedOutlineRequiredError,
    DraftService,
    SectionNotInOutlineError,
)
from pes.domain.outline import OutlineSection, ProposalOutline

# ---------------------------------------------------------------------------
# Fake driven port (SectionDrafter) at port boundary
# ---------------------------------------------------------------------------


class FakeSectionDrafter:
    """Fake driven port that produces deterministic section drafts."""

    def __init__(self, *, word_count: int = 500, addressed_ids: list[str] | None = None) -> None:
        self._word_count = word_count
        self._addressed_ids = addressed_ids
        self.draft_called_with: dict | None = None

    def draft(
        self,
        section: OutlineSection,
        *,
        iteration: int = 1,
    ) -> SectionDraft:
        self.draft_called_with = {
            "section": section,
            "iteration": iteration,
        }
        words = ["word"] * self._word_count
        content = " ".join(words)
        addressed = self._addressed_ids if self._addressed_ids is not None else section.compliance_item_ids
        return SectionDraft(
            section_id=section.section_id,
            content=content,
            compliance_item_ids=addressed,
            iteration=iteration,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_outline(
    *,
    sections: list[OutlineSection] | None = None,
) -> ProposalOutline:
    """Build a proposal outline with default sections."""
    if sections is None:
        sections = [
            OutlineSection(
                section_id="technical-approach",
                title="Technical Approach",
                compliance_item_ids=["CI-001", "CI-002", "CI-003"],
                page_budget=8.0,
                figure_placeholders=["fig-1"],
                thesis_statement="Novel approach",
            ),
            OutlineSection(
                section_id="statement-of-work",
                title="Statement of Work",
                compliance_item_ids=["CI-004", "CI-005"],
                page_budget=4.0,
                figure_placeholders=[],
                thesis_statement="Milestone deliverables",
            ),
        ]
    return ProposalOutline(sections=sections)


def _make_service(
    drafter: FakeSectionDrafter | None = None,
) -> tuple[DraftService, FakeSectionDrafter]:
    d = drafter or FakeSectionDrafter()
    return DraftService(section_drafter=d), d


# ---------------------------------------------------------------------------
# Behavior 1: Section drafted addressing mapped compliance items
# ---------------------------------------------------------------------------


class TestDraftSectionHappyPath:
    def test_returns_draft_with_content_for_requested_section(self):
        service, drafter = _make_service()
        outline = _make_outline()

        result = service.draft_section(outline=outline, section_id="technical-approach")

        assert result.draft.section_id == "technical-approach"
        assert result.draft.word_count > 0

    def test_delegates_section_to_drafter(self):
        service, drafter = _make_service()
        outline = _make_outline()

        service.draft_section(outline=outline, section_id="technical-approach")

        assert drafter.draft_called_with is not None
        assert drafter.draft_called_with["section"].section_id == "technical-approach"


# ---------------------------------------------------------------------------
# Behavior 2: Draft word count reported against section page budget
# ---------------------------------------------------------------------------


class TestWordCountReporting:
    def test_reports_word_count_and_page_budget(self):
        drafter = FakeSectionDrafter(word_count=1500)
        service, _ = _make_service(drafter)
        outline = _make_outline()

        result = service.draft_section(outline=outline, section_id="technical-approach")

        assert result.word_count == 1500
        assert result.page_budget == 8.0
        assert result.pages_used == pytest.approx(1500 / 250, rel=0.01)


# ---------------------------------------------------------------------------
# Behavior 3: Section exceeding page budget produces warning
# ---------------------------------------------------------------------------


class TestPageBudgetWarning:
    @pytest.mark.parametrize(
        "word_count,page_budget,expect_warning",
        [
            (2100, 8.0, True),   # 8.4 pages > 8.0
            (5200, 8.0, True),   # 20.8 pages > 8.0
            (1500, 8.0, False),  # 6.0 pages < 8.0
            (2000, 8.0, False),  # 8.0 pages == 8.0, no warning at exact
        ],
    )
    def test_warning_when_draft_exceeds_page_budget(
        self, word_count, page_budget, expect_warning
    ):
        drafter = FakeSectionDrafter(word_count=word_count)
        service, _ = _make_service(drafter)
        section = OutlineSection(
            section_id="technical-approach",
            title="Technical Approach",
            compliance_item_ids=["CI-001"],
            page_budget=page_budget,
            figure_placeholders=[],
            thesis_statement="Thesis",
        )
        outline = ProposalOutline(sections=[section])

        result = service.draft_section(outline=outline, section_id="technical-approach")

        if expect_warning:
            assert result.budget_warning is not None
            assert "exceeds" in result.budget_warning.lower()
        else:
            assert result.budget_warning is None


# ---------------------------------------------------------------------------
# Behavior 4: Unaddressed compliance items flagged by item ID
# ---------------------------------------------------------------------------


class TestUnaddressedComplianceItems:
    def test_flags_unaddressed_items_by_id(self):
        # Drafter only addresses CI-001, leaving CI-002 and CI-003 unaddressed
        drafter = FakeSectionDrafter(addressed_ids=["CI-001"])
        service, _ = _make_service(drafter)
        outline = _make_outline()

        result = service.draft_section(outline=outline, section_id="technical-approach")

        assert sorted(result.unaddressed_item_ids) == ["CI-002", "CI-003"]

    def test_no_unaddressed_items_when_all_covered(self):
        drafter = FakeSectionDrafter(addressed_ids=["CI-001", "CI-002", "CI-003"])
        service, _ = _make_service(drafter)
        outline = _make_outline()

        result = service.draft_section(outline=outline, section_id="technical-approach")

        assert result.unaddressed_item_ids == []


# ---------------------------------------------------------------------------
# Behavior 5: Drafting without approved outline raises descriptive error
# ---------------------------------------------------------------------------


class TestDraftWithoutApprovedOutline:
    def test_raises_approved_outline_required_error(self):
        service, _ = _make_service()

        with pytest.raises(ApprovedOutlineRequiredError) as exc_info:
            service.draft_section(outline=None, section_id="technical-approach")

        assert "approved outline required" in str(exc_info.value).lower()

    def test_error_includes_wave_3_guidance(self):
        service, _ = _make_service()

        with pytest.raises(ApprovedOutlineRequiredError) as exc_info:
            service.draft_section(outline=None, section_id="technical-approach")

        assert "outline approval" in str(exc_info.value).lower() or "wave 3" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Behavior 6: Undefined section returns guidance on available sections
# ---------------------------------------------------------------------------


class TestDraftUndefinedSection:
    def test_raises_section_not_in_outline_error(self):
        service, _ = _make_service()
        outline = _make_outline()

        with pytest.raises(SectionNotInOutlineError) as exc_info:
            service.draft_section(outline=outline, section_id="executive-summary")

        assert "executive-summary" in str(exc_info.value).lower()

    def test_error_lists_available_section_ids(self):
        service, _ = _make_service()
        outline = _make_outline()

        with pytest.raises(SectionNotInOutlineError) as exc_info:
            service.draft_section(outline=outline, section_id="executive-summary")

        msg = str(exc_info.value).lower()
        assert "technical-approach" in msg
        assert "statement-of-work" in msg
