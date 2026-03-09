"""Strategy service -- driving port for strategy brief generation and Wave 1 checkpoint.

Orchestrates: brief generation from compliance matrix and TPOC data,
strategy checkpoint (approve/revise/skip), and Wave 2 unlock.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pes.domain.compliance import ComplianceMatrix
from pes.domain.strategy import (
    StrategyBrief,
    StrategySection,
)
from pes.domain.tpoc_ingestion import TpocIngestionResult


class ComplianceMatrixRequiredError(Exception):
    """Raised when strategy brief generation is attempted without a compliance matrix."""


class StrategyBriefNotFoundError(Exception):
    """Raised when checkpoint action is attempted without a generated brief."""


class StrategyService:
    """Driving port: generates strategy brief and manages checkpoint."""

    def generate_brief(
        self,
        matrix: ComplianceMatrix,
        tpoc_result: TpocIngestionResult | None = None,
        revision_feedback: str | None = None,
    ) -> StrategyBrief:
        """Generate strategy brief from compliance matrix and optional TPOC data.

        Raises ComplianceMatrixRequiredError if matrix is None.
        """
        if matrix is None:
            raise ComplianceMatrixRequiredError(
                "Compliance matrix required before strategy brief generation."
            )

        has_tpoc = tpoc_result is not None and tpoc_result.answered_count > 0
        tpoc_note = self._build_tpoc_note(tpoc_result)
        tpoc_insights = self._build_tpoc_insights(tpoc_result) if has_tpoc else ""

        sections = [
            StrategySection(
                key="technical_approach",
                title="Technical Approach",
                content=self._build_technical_approach(matrix, revision_feedback),
            ),
            StrategySection(
                key="trl",
                title="Technology Readiness Level",
                content=self._build_trl_section(matrix, tpoc_insights),
            ),
            StrategySection(
                key="teaming",
                title="Teaming Strategy",
                content=self._build_teaming_section(matrix),
            ),
            StrategySection(
                key="phase_iii",
                title="Phase III Commercialization Pathway",
                content=self._build_phase_iii_section(matrix, tpoc_insights),
            ),
            StrategySection(
                key="budget",
                title="Budget Strategy",
                content=self._build_budget_section(matrix, revision_feedback),
            ),
            StrategySection(
                key="risks",
                title="Risk Assessment",
                content=f"Key risks identified from {matrix.item_count} compliance items. "
                f"{tpoc_note}",
            ),
        ]

        return StrategyBrief(
            sections=sections,
            tpoc_available=has_tpoc,
            revision_feedback=revision_feedback,
        )

    def approve_brief(
        self,
        brief: StrategyBrief | None,
    ) -> dict[str, object]:
        """Approve strategy brief, recording approval and unlocking Wave 2.

        Raises StrategyBriefNotFoundError if brief is None.
        Returns state update dict with approval timestamp and wave unlock.
        """
        if brief is None:
            raise StrategyBriefNotFoundError(
                "No strategy brief to approve. Generate one first."
            )

        return {
            "strategy_brief_status": "approved",
            "approved_at": datetime.now(tz=UTC).isoformat(),
            "wave_2_unlocked": True,
        }

    def revise_brief(
        self,
        brief: StrategyBrief | None,
        matrix: ComplianceMatrix,
        feedback: str,
        tpoc_result: TpocIngestionResult | None = None,
    ) -> StrategyBrief:
        """Revise strategy brief incorporating user feedback.

        Raises StrategyBriefNotFoundError if brief is None.
        """
        if brief is None:
            raise StrategyBriefNotFoundError(
                "No strategy brief to revise. Generate one first."
            )

        return self.generate_brief(
            matrix,
            tpoc_result=tpoc_result,
            revision_feedback=feedback,
        )

    def _build_tpoc_note(self, tpoc_result: TpocIngestionResult | None) -> str:
        """Build TPOC availability note."""
        if tpoc_result is None or tpoc_result.answered_count == 0:
            return "TPOC insights: not available."
        return (
            f"TPOC insights: {tpoc_result.answered_count} answers integrated, "
            f"{tpoc_result.unanswered_count} pending."
        )

    def _build_tpoc_insights(self, tpoc_result: TpocIngestionResult | None) -> str:
        """Build TPOC insights summary from answered questions."""
        if tpoc_result is None:
            return ""
        insights = []
        for answer in tpoc_result.answers:
            if answer.is_answered and answer.answer_text:
                insights.append(
                    f"TPOC clarification (Q{answer.question_id}): {answer.answer_text}"
                )
        return " ".join(insights)

    def _build_technical_approach(
        self, matrix: ComplianceMatrix, revision_feedback: str | None
    ) -> str:
        """Build technical approach section from compliance requirements."""
        base = (
            f"Technical approach addressing {matrix.item_count} solicitation requirements."
        )
        if revision_feedback:
            base += f" Revised per feedback: {revision_feedback}"
        return base

    def _build_trl_section(self, matrix: ComplianceMatrix, tpoc_insights: str) -> str:
        """Build TRL assessment section."""
        base = "TRL assessment based on solicitation requirements and technical baseline."
        if tpoc_insights:
            base += f" {tpoc_insights}"
        return base

    def _build_teaming_section(self, matrix: ComplianceMatrix) -> str:
        """Build teaming strategy section."""
        return (
            "Teaming strategy to address capability gaps identified "
            f"across {matrix.item_count} requirements."
        )

    def _build_phase_iii_section(
        self, matrix: ComplianceMatrix, tpoc_insights: str
    ) -> str:
        """Build Phase III pathway section."""
        base = "Phase III commercialization pathway and transition plan."
        if tpoc_insights:
            base += f" {tpoc_insights}"
        return base

    def _build_budget_section(
        self, matrix: ComplianceMatrix, revision_feedback: str | None
    ) -> str:
        """Build budget strategy section."""
        base = f"Budget allocation across {matrix.item_count} requirements."
        if revision_feedback:
            base += f" Adjusted per feedback: {revision_feedback}"
        return base
