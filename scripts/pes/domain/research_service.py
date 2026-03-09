"""Research service -- driving port for research findings generation.

Orchestrates: research generation from strategy brief context,
delegating to ResearchGenerator driven port for actual findings production.
"""

from __future__ import annotations

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
    ) -> ResearchSummary: ...


class StrategyBriefRequiredError(Exception):
    """Raised when research generation is attempted without a strategy brief."""


class ResearchService:
    """Driving port: generates research findings from strategy brief context.

    Delegates to ResearchGenerator driven port for actual findings production.
    Validates preconditions (strategy brief required) and passes TPOC availability
    context to the generator so it can note caveats when TPOC data is missing.
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
