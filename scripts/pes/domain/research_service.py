"""Research service -- driving port for research findings generation and checkpoint.

Orchestrates: research generation from strategy brief context,
research checkpoint (approve/revise/skip), and Wave 3 unlock.
Delegates to ResearchGenerator driven port for actual findings production.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from pes.domain.research import ResearchSummary
from pes.domain.strategy import StrategyBrief


class ResearchGenerator(Protocol):
    """Driven port: generates research findings from strategy brief context."""

    def generate(
        self,
        strategy_brief: StrategyBrief,
        *,
        tpoc_available: bool,
        feedback: str | None = None,
    ) -> ResearchSummary: ...


class StrategyBriefRequiredError(Exception):
    """Raised when research generation is attempted without a strategy brief."""


class ResearchFindingsNotFoundError(Exception):
    """Raised when checkpoint action is attempted without generated findings."""


class ResearchService:
    """Driving port: generates research findings and manages checkpoint.

    Delegates to ResearchGenerator driven port for actual findings production.
    Validates preconditions (strategy brief required, findings required for checkpoint)
    and passes TPOC availability context to the generator.
    """

    def __init__(self, research_generator: ResearchGenerator) -> None:
        self._generator = research_generator

    def generate_findings(
        self,
        strategy_brief: StrategyBrief,
        *,
        tpoc_available: bool = True,
    ) -> ResearchSummary:
        """Generate research findings from strategy brief context.

        Raises StrategyBriefRequiredError if strategy_brief is None.
        When tpoc_available is False, proceeds but generator notes caveat.
        """
        if strategy_brief is None:
            raise StrategyBriefRequiredError(
                "Strategy brief required before research generation. "
                "Generate and approve a strategy brief first."
            )

        return self._generator.generate(
            strategy_brief,
            tpoc_available=tpoc_available,
        )

    def approve_research(
        self,
        summary: ResearchSummary | None,
    ) -> dict[str, object]:
        """Approve research findings, recording approval and unlocking Wave 3.

        Raises ResearchFindingsNotFoundError if summary is None.
        Returns state update dict with approval timestamp and wave unlock.
        """
        if summary is None:
            raise ResearchFindingsNotFoundError(
                "No research findings to approve. Generate research first."
            )

        return {
            "research_status": "approved",
            "approved_at": datetime.now(tz=UTC).isoformat(),
            "wave_3_unlocked": True,
        }

    def revise_research(
        self,
        summary: ResearchSummary | None,
        strategy_brief: StrategyBrief,
        feedback: str,
    ) -> ResearchSummary:
        """Revise research findings incorporating user feedback.

        Raises ResearchFindingsNotFoundError if summary is None.
        Regenerates findings via ResearchGenerator with feedback context.
        """
        if summary is None:
            raise ResearchFindingsNotFoundError(
                "No research findings to revise. Generate research first."
            )

        return self._generator.generate(
            strategy_brief,
            tpoc_available=True,
            feedback=feedback,
        )

    def skip_research(self) -> dict[str, object]:
        """Skip research, marking as deferred and unlocking Wave 3.

        Does not require existing findings. Returns state update dict.
        """
        return {
            "research_status": "deferred",
            "wave_3_unlocked": True,
        }
