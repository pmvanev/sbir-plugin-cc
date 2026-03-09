"""Unit tests for outline domain value objects.

Test Budget: 3 behaviors x 2 = 6 unit tests max.

These are pure domain value objects tested directly per step 03-01.
No driving port exists yet -- domain models are built first.

Behaviors:
1. OutlineSection captures fields (frozen VO)
2. ProposalOutline holds collection of sections
3. ProposalOutline validates page budget total against limit
"""

from __future__ import annotations

import pytest

from pes.domain.outline import OutlineSection, ProposalOutline


# ---------------------------------------------------------------------------
# Behavior 1: OutlineSection captures section fields
# ---------------------------------------------------------------------------


class TestOutlineSectionConstruction:
    def test_section_captures_all_fields(self):
        section = OutlineSection(
            section_id="tech-approach",
            title="Technical Approach",
            compliance_item_ids=["CI-001", "CI-002"],
            page_budget=5.0,
            figure_placeholders=["fig-architecture", "fig-timeline"],
            thesis_statement="Our approach leverages novel beam-steering algorithms.",
        )

        assert section.section_id == "tech-approach"
        assert section.title == "Technical Approach"
        assert section.compliance_item_ids == ["CI-001", "CI-002"]
        assert section.page_budget == 5.0
        assert section.figure_placeholders == ["fig-architecture", "fig-timeline"]
        assert section.thesis_statement == "Our approach leverages novel beam-steering algorithms."

    def test_section_is_frozen_value_object(self):
        section = OutlineSection(
            section_id="intro",
            title="Introduction",
            compliance_item_ids=[],
            page_budget=1.0,
            figure_placeholders=[],
            thesis_statement="Overview of the proposal.",
        )

        with pytest.raises(AttributeError):
            section.title = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Behavior 2: ProposalOutline holds collection of sections
# ---------------------------------------------------------------------------


class TestProposalOutline:
    def test_outline_holds_collection_of_sections(self):
        sections = [
            OutlineSection(
                section_id="intro",
                title="Introduction",
                compliance_item_ids=["CI-001"],
                page_budget=1.0,
                figure_placeholders=[],
                thesis_statement="Intro thesis.",
            ),
            OutlineSection(
                section_id="tech",
                title="Technical Approach",
                compliance_item_ids=["CI-002"],
                page_budget=4.0,
                figure_placeholders=["fig-1"],
                thesis_statement="Tech thesis.",
            ),
        ]
        outline = ProposalOutline(sections=sections)

        assert len(outline.sections) == 2
        assert outline.sections[0].section_id == "intro"

    def test_empty_outline_has_no_sections(self):
        outline = ProposalOutline()

        assert len(outline.sections) == 0


# ---------------------------------------------------------------------------
# Behavior 3: Page budget validation against limit
# ---------------------------------------------------------------------------


class TestPageBudgetValidation:
    def test_total_within_limit_is_valid(self):
        sections = [
            OutlineSection(
                section_id="intro",
                title="Introduction",
                compliance_item_ids=[],
                page_budget=2.0,
                figure_placeholders=[],
                thesis_statement="Intro.",
            ),
            OutlineSection(
                section_id="tech",
                title="Technical Approach",
                compliance_item_ids=[],
                page_budget=3.0,
                figure_placeholders=[],
                thesis_statement="Tech.",
            ),
        ]
        outline = ProposalOutline(sections=sections)

        assert outline.validates_page_budget(limit=5.0) is True
        assert outline.validates_page_budget(limit=10.0) is True

    def test_total_exceeding_limit_is_invalid(self):
        sections = [
            OutlineSection(
                section_id="intro",
                title="Introduction",
                compliance_item_ids=[],
                page_budget=3.0,
                figure_placeholders=[],
                thesis_statement="Intro.",
            ),
            OutlineSection(
                section_id="tech",
                title="Technical Approach",
                compliance_item_ids=[],
                page_budget=4.0,
                figure_placeholders=[],
                thesis_statement="Tech.",
            ),
        ]
        outline = ProposalOutline(sections=sections)

        assert outline.validates_page_budget(limit=5.0) is False

    def test_total_page_budget_returns_sum(self):
        sections = [
            OutlineSection(
                section_id="a",
                title="A",
                compliance_item_ids=[],
                page_budget=2.5,
                figure_placeholders=[],
                thesis_statement="A.",
            ),
            OutlineSection(
                section_id="b",
                title="B",
                compliance_item_ids=[],
                page_budget=3.5,
                figure_placeholders=[],
                thesis_statement="B.",
            ),
        ]
        outline = ProposalOutline(sections=sections)

        assert outline.total_page_budget == 6.0
