"""Unit tests for ResearchService (driving port) -- research findings generation.

Test Budget: 3 behaviors x 2 = 6 unit tests max.
Tests enter through driving port (ResearchService).
Driven port (ResearchGenerator) mocked at port boundary.
Domain objects (ResearchSummary, ResearchFinding, StrategyBrief) are real collaborators.

Behaviors:
1. Generate research findings covering all six categories
2. Generation without strategy brief raises descriptive error
3. Generation without TPOC data proceeds with caveat noted
"""

from __future__ import annotations

from typing import Protocol

import pytest

from pes.domain.research import (
    ResearchCategory,
    ResearchFinding,
    ResearchSummary,
)
from pes.domain.research_service import (
    ResearchService,
    StrategyBriefRequiredError,
)
from pes.domain.strategy import StrategyBrief, StrategySection


# ---------------------------------------------------------------------------
# Fake driven port (ResearchGenerator) at port boundary
# ---------------------------------------------------------------------------


class FakeResearchGenerator:
    """Fake driven port that produces deterministic findings for all six categories."""

    def __init__(self, *, include_tpoc_caveat: bool = False) -> None:
        self._include_tpoc_caveat = include_tpoc_caveat
        self.generate_called_with: dict | None = None

    def generate(
        self,
        strategy_brief: StrategyBrief,
        *,
        tpoc_available: bool,
    ) -> ResearchSummary:
        self.generate_called_with = {
            "strategy_brief": strategy_brief,
            "tpoc_available": tpoc_available,
        }
        findings = [
            ResearchFinding(
                category=cat,
                content=f"Finding for {cat.value}",
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

SAMPLE_BRIEF = StrategyBrief(
    sections=[
        StrategySection(key="technical_approach", title="Technical Approach", content="approach"),
        StrategySection(key="trl", title="TRL", content="trl assessment"),
        StrategySection(key="teaming", title="Teaming", content="teaming plan"),
        StrategySection(key="phase_iii", title="Phase III", content="commercialization"),
        StrategySection(key="budget", title="Budget", content="budget plan"),
        StrategySection(key="risks", title="Risks", content="risk assessment"),
    ],
    tpoc_available=True,
)


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
