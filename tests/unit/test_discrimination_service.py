"""Unit tests for DiscriminationService (driving port) -- discrimination table generation and iteration.

Test Budget: 4 behaviors x 2 = 8 unit tests max.
Tests enter through driving port (DiscriminationService).
Driven port (DiscriminationGenerator) mocked at port boundary.
Domain objects (DiscriminationTable, DiscriminatorItem, StrategyBrief, ResearchSummary) are real collaborators.

Behaviors:
1. Generate discrimination table with items that have claims and evidence citations
2. TPOC insights passed to generator when available
3. Revision with feedback regenerates table incorporating feedback
4. Generation without approved research raises descriptive error
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.discrimination import DiscriminationTable, DiscriminatorItem
from pes.domain.discrimination_service import (
    DiscriminationService,
    ResearchApprovalRequiredError,
)
from pes.domain.research import ResearchSummary
from pes.domain.strategy import StrategyBrief
from tests.fixtures.research_fixtures import make_research_summary
from tests.fixtures.strategy_fixtures import SAMPLE_BRIEF

# ---------------------------------------------------------------------------
# Fake driven port (DiscriminationGenerator) at port boundary
# ---------------------------------------------------------------------------


class FakeDiscriminationGenerator:
    """Fake driven port that produces deterministic discrimination tables."""

    def __init__(self) -> None:
        self.generate_called_with: dict[str, Any] | None = None
        self.last_tpoc_insights: str | None = None
        self.last_feedback: str | None = None

    def generate(
        self,
        strategy_brief: StrategyBrief,
        compliance_matrix: dict[str, Any],
        research_summary: ResearchSummary,
        *,
        tpoc_insights: str | None = None,
        feedback: str | None = None,
    ) -> DiscriminationTable:
        self.generate_called_with = {
            "strategy_brief": strategy_brief,
            "compliance_matrix": compliance_matrix,
            "research_summary": research_summary,
            "tpoc_insights": tpoc_insights,
            "feedback": feedback,
        }
        self.last_tpoc_insights = tpoc_insights
        self.last_feedback = feedback

        items = [
            DiscriminatorItem(
                category="company_strengths",
                claim="Superior manufacturing capacity",
                evidence_citation="Company profile: 50k sq ft facility",
            ),
            DiscriminatorItem(
                category="technical_approach",
                claim="Novel beam-steering approach",
                evidence_citation="Research: patent landscape analysis",
            ),
            DiscriminatorItem(
                category="team_qualifications",
                claim="PI has 15 years directed energy experience",
                evidence_citation="Company profile: team roster",
            ),
        ]

        if feedback:
            items.append(
                DiscriminatorItem(
                    category="company_strengths",
                    claim=f"Revised per feedback: {feedback}",
                    evidence_citation="User feedback",
                )
            )

        return DiscriminationTable(items=items)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------




SAMPLE_COMPLIANCE_MATRIX: dict[str, Any] = {"item_count": 47, "items": []}


def _make_service(
    generator: FakeDiscriminationGenerator | None = None,
) -> tuple[DiscriminationService, FakeDiscriminationGenerator]:
    gen = generator or FakeDiscriminationGenerator()
    return DiscriminationService(discrimination_generator=gen), gen


# ---------------------------------------------------------------------------
# Behavior 1: Generate discrimination table with claims and evidence
# ---------------------------------------------------------------------------


class TestGenerateDiscriminationTable:
    def test_generates_table_with_discriminator_items(self):
        service, _gen = _make_service()

        result = service.generate_table(
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
        )

        assert isinstance(result, DiscriminationTable)
        assert len(result.items) > 0

    def test_each_discriminator_has_claim_and_evidence(self):
        service, _gen = _make_service()

        result = service.generate_table(
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
        )

        for item in result.items:
            assert item.claim, f"Discriminator in '{item.category}' missing claim"
            assert item.evidence_citation, f"Discriminator '{item.claim}' missing evidence"

    def test_delegates_to_generator_with_context(self):
        service, gen = _make_service()

        service.generate_table(
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
        )

        assert gen.generate_called_with is not None
        assert gen.generate_called_with["strategy_brief"] is SAMPLE_BRIEF
        assert gen.generate_called_with["compliance_matrix"] is SAMPLE_COMPLIANCE_MATRIX


# ---------------------------------------------------------------------------
# Behavior 2: TPOC insights passed to generator when available
# ---------------------------------------------------------------------------


class TestTpocInsightsIncorporated:
    def test_tpoc_insights_passed_to_generator(self):
        service, gen = _make_service()

        service.generate_table(
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
            tpoc_insights="Agency prior approach failed due to overheating",
        )

        assert gen.last_tpoc_insights == "Agency prior approach failed due to overheating"

    def test_generates_without_tpoc_when_not_available(self):
        service, gen = _make_service()

        result = service.generate_table(
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
        )

        assert gen.last_tpoc_insights is None
        assert len(result.items) > 0


# ---------------------------------------------------------------------------
# Behavior 3: Revision with feedback regenerates table
# ---------------------------------------------------------------------------


class TestReviseDiscriminationTable:
    def test_revision_passes_feedback_to_generator(self):
        service, gen = _make_service()
        existing = DiscriminationTable(items=[
            DiscriminatorItem(category="c", claim="original", evidence_citation="e"),
        ])

        service.revise_table(
            existing_table=existing,
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
            feedback="Add facility clearance as discriminator",
        )

        assert gen.last_feedback == "Add facility clearance as discriminator"

    def test_revision_returns_new_table(self):
        service, gen = _make_service()
        existing = DiscriminationTable(items=[
            DiscriminatorItem(category="c", claim="original", evidence_citation="e"),
        ])

        revised = service.revise_table(
            existing_table=existing,
            strategy_brief=SAMPLE_BRIEF,
            compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
            research_summary=make_research_summary(),
            research_approved=True,
            feedback="Add facility clearance",
        )

        assert isinstance(revised, DiscriminationTable)
        assert len(revised.items) > 0


# ---------------------------------------------------------------------------
# Behavior 4: Generation without approved research raises error
# ---------------------------------------------------------------------------


class TestGenerateWithoutResearchApproval:
    def test_raises_research_approval_required_error(self):
        service, _gen = _make_service()

        with pytest.raises(ResearchApprovalRequiredError) as exc_info:
            service.generate_table(
                strategy_brief=SAMPLE_BRIEF,
                compliance_matrix=SAMPLE_COMPLIANCE_MATRIX,
                research_summary=make_research_summary(),
                research_approved=False,
            )

        assert "research review required" in str(exc_info.value).lower()
