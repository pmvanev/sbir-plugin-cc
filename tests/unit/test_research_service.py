"""Unit tests for ResearchService (driving port) -- research findings generation and checkpoint.

Test Budget: 7 behaviors x 2 = 14 unit tests max.
Tests enter through driving port (ResearchService).
Driven port (ResearchGenerator) mocked at port boundary.
Domain objects (ResearchSummary, ResearchFinding, StrategyBrief) are real collaborators.

Behaviors:
1. Generate research findings covering all six categories
2. Generation without strategy brief raises descriptive error
3. Generation without TPOC data proceeds with caveat noted
4. Approve research records approval and unlocks Wave 3
5. Revise research regenerates findings incorporating feedback
6. Approve or revise without findings raises error
7. Skip research marks as deferred and unlocks Wave 3
"""

from __future__ import annotations

import pytest

from pes.domain.research import (
    ResearchCategory,
    ResearchFinding,
    ResearchSummary,
)
from pes.domain.research_service import (
    ResearchFindingsNotFoundError,
    ResearchService,
    StrategyBriefRequiredError,
)
from pes.domain.strategy import StrategyBrief
from tests.fixtures.research_fixtures import make_research_summary
from tests.fixtures.strategy_fixtures import SAMPLE_BRIEF

# ---------------------------------------------------------------------------
# Fake driven port (ResearchGenerator) at port boundary
# ---------------------------------------------------------------------------


class FakeResearchGenerator:
    """Fake driven port that produces deterministic findings for all six categories."""

    def __init__(self) -> None:
        self.generate_called_with: dict | None = None
        self.last_feedback: str | None = None

    def generate(
        self,
        strategy_brief: StrategyBrief,
        *,
        tpoc_available: bool,
        feedback: str | None = None,
    ) -> ResearchSummary:
        self.generate_called_with = {
            "strategy_brief": strategy_brief,
            "tpoc_available": tpoc_available,
        }
        self.last_feedback = feedback
        content_suffix = f" (revised: {feedback})" if feedback else ""
        findings = [
            ResearchFinding(
                category=cat,
                content=f"Finding for {cat.value}{content_suffix}",
                evidence_source=f"Source for {cat.value}",
            )
            for cat in ResearchCategory
        ]
        caveats: list[str] = []
        if not tpoc_available:
            caveats.append("TPOC data not available; findings based on solicitation only.")
        return ResearchSummary(findings=findings, caveats=caveats)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_service(generator: FakeResearchGenerator | None = None) -> ResearchService:
    gen = generator or FakeResearchGenerator()
    return ResearchService(research_generator=gen)


# ---------------------------------------------------------------------------
# Behavior 1: Generate research findings covering all six categories
# ---------------------------------------------------------------------------


class TestGenerateResearchFindings:
    def test_findings_cover_all_six_research_categories(self):
        generator = FakeResearchGenerator()
        service = _make_service(generator)

        result = service.generate_findings(strategy_brief=SAMPLE_BRIEF, tpoc_available=True)

        assert result.is_complete
        assert result.covered_categories == set(ResearchCategory)

    def test_findings_delegated_to_generator_with_brief_context(self):
        generator = FakeResearchGenerator()
        service = _make_service(generator)

        service.generate_findings(strategy_brief=SAMPLE_BRIEF, tpoc_available=True)

        assert generator.generate_called_with is not None
        assert generator.generate_called_with["strategy_brief"] is SAMPLE_BRIEF
        assert generator.generate_called_with["tpoc_available"] is True


# ---------------------------------------------------------------------------
# Behavior 2: Generation without strategy brief raises descriptive error
# ---------------------------------------------------------------------------


class TestGenerateWithoutStrategyBrief:
    def test_none_brief_raises_strategy_brief_required_error(self):
        service = _make_service()

        with pytest.raises(StrategyBriefRequiredError) as exc_info:
            service.generate_findings(strategy_brief=None, tpoc_available=True)  # type: ignore[arg-type]

        assert "strategy brief" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Behavior 3: Generation without TPOC data proceeds with caveat noted
# ---------------------------------------------------------------------------


class TestGenerateWithoutTpocData:
    def test_generates_findings_when_tpoc_unavailable(self):
        generator = FakeResearchGenerator()
        service = _make_service(generator)

        result = service.generate_findings(strategy_brief=SAMPLE_BRIEF, tpoc_available=False)

        assert result.is_complete
        assert generator.generate_called_with is not None
        assert generator.generate_called_with["tpoc_available"] is False

    def test_caveat_noted_when_tpoc_unavailable(self):
        generator = FakeResearchGenerator()
        service = _make_service(generator)

        result = service.generate_findings(strategy_brief=SAMPLE_BRIEF, tpoc_available=False)

        assert len(result.caveats) > 0
        caveat_text = " ".join(result.caveats).lower()
        assert "tpoc" in caveat_text


# ---------------------------------------------------------------------------
# Helpers for checkpoint tests
# ---------------------------------------------------------------------------


_make_summary = make_research_summary


# ---------------------------------------------------------------------------
# Behavior 4: Approve research records approval and unlocks Wave 3
# ---------------------------------------------------------------------------


class TestApproveResearch:
    def test_approval_returns_state_with_approved_status_and_timestamp(self):
        service = _make_service()
        summary = _make_summary()

        result = service.approve_research(summary)

        assert result["research_status"] == "approved"
        assert result["approved_at"] is not None

    def test_approval_unlocks_wave_3(self):
        service = _make_service()
        summary = _make_summary()

        result = service.approve_research(summary)

        assert result["wave_3_unlocked"] is True


# ---------------------------------------------------------------------------
# Behavior 5: Revise research regenerates findings incorporating feedback
# ---------------------------------------------------------------------------


class TestReviseResearch:
    def test_revision_regenerates_with_feedback(self):
        generator = FakeResearchGenerator()
        service = _make_service(generator)
        summary = _make_summary()

        revised = service.revise_research(summary, SAMPLE_BRIEF, "Deepen prior award analysis")

        assert revised.is_complete
        assert generator.last_feedback == "Deepen prior award analysis"

    def test_revised_findings_still_complete(self):
        generator = FakeResearchGenerator()
        service = _make_service(generator)
        summary = _make_summary()

        revised = service.revise_research(summary, SAMPLE_BRIEF, "Add Navy DEW programs")

        assert revised.covered_categories == set(ResearchCategory)


# ---------------------------------------------------------------------------
# Behavior 6: Approve or revise without findings raises error
# ---------------------------------------------------------------------------


class TestCheckpointWithoutFindings:
    def test_approve_none_raises_findings_not_found(self):
        service = _make_service()

        with pytest.raises(ResearchFindingsNotFoundError) as exc_info:
            service.approve_research(None)

        assert "no research findings" in str(exc_info.value).lower()

    def test_revise_none_raises_findings_not_found(self):
        service = _make_service()

        with pytest.raises(ResearchFindingsNotFoundError) as exc_info:
            service.revise_research(None, SAMPLE_BRIEF, "feedback")

        assert "no research findings" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Behavior 7: Skip research marks as deferred and unlocks Wave 3
# ---------------------------------------------------------------------------


class TestSkipResearch:
    def test_skip_returns_deferred_status_and_unlocks_wave_3(self):
        service = _make_service()

        result = service.skip_research()

        assert result["research_status"] == "deferred"
        assert result["wave_3_unlocked"] is True
