"""Discrimination service -- driving port for discrimination table generation and iteration.

Orchestrates: discrimination table generation from strategy brief, compliance matrix,
and research findings context. Supports TPOC insight integration and feedback iteration.
Delegates to DiscriminationGenerator driven port for actual table production.
"""

from __future__ import annotations

from typing import Any, Protocol

from pes.domain.discrimination import DiscriminationTable
from pes.domain.research import ResearchSummary
from pes.domain.strategy import StrategyBrief


class DiscriminationGenerator(Protocol):
    """Driven port: generates discrimination table from proposal context."""

    def generate(
        self,
        strategy_brief: StrategyBrief,
        compliance_matrix: dict[str, Any],
        research_summary: ResearchSummary,
        *,
        tpoc_insights: str | None = None,
        feedback: str | None = None,
    ) -> DiscriminationTable: ...


class ResearchApprovalRequiredError(Exception):
    """Raised when discrimination generation is attempted without approved research."""


class DiscriminationService:
    """Driving port: generates discrimination table and manages iteration.

    Delegates to DiscriminationGenerator driven port for actual table production.
    Validates preconditions (research approval required) and passes context to generator.
    """

    def __init__(self, discrimination_generator: DiscriminationGenerator) -> None:
        self._generator = discrimination_generator

    def generate_table(
        self,
        strategy_brief: StrategyBrief,
        compliance_matrix: dict[str, Any],
        research_summary: ResearchSummary | None,
        research_approved: bool,
        *,
        tpoc_insights: str | None = None,
    ) -> DiscriminationTable:
        """Generate discrimination table from proposal context.

        Raises ResearchApprovalRequiredError if research is not approved.
        Passes TPOC insights to generator when available.
        """
        if not research_approved:
            raise ResearchApprovalRequiredError(
                "Research review required before discrimination table. "
                "Complete and approve Wave 2 research review first."
            )

        return self._generator.generate(
            strategy_brief,
            compliance_matrix,
            research_summary,
            tpoc_insights=tpoc_insights,
        )

    def revise_table(
        self,
        existing_table: DiscriminationTable | None,
        strategy_brief: StrategyBrief,
        compliance_matrix: dict[str, Any],
        research_summary: ResearchSummary,
        research_approved: bool,
        feedback: str,
    ) -> DiscriminationTable:
        """Revise discrimination table incorporating user feedback.

        Regenerates table via DiscriminationGenerator with feedback context.
        """
        return self._generator.generate(
            strategy_brief,
            compliance_matrix,
            research_summary,
            feedback=feedback,
        )
