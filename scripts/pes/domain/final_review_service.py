"""Final review service -- driving port for simulated government evaluator review.

Orchestrates: reviewer persona simulation, red team review, debrief cross-check,
issue resolution with iteration loop (max 2), and forced sign-off.
Delegates LLM review to ReviewSimulator driven port.
"""

from __future__ import annotations

from typing import Protocol

from pes.domain.final_review import (
    DebriefCrossCheckEntry,
    DebriefCrossCheckResult,
    ForcedSignOffResult,
    RedTeamFinding,
    RedTeamResult,
    ReReviewResult,
    ReviewerScorecard,
    SignOffRecord,
)

MAX_REVIEW_ITERATIONS = 2


class ReviewSimulator(Protocol):
    """Driven port: simulates government evaluator review."""

    def simulate_reviewer(self, proposal_id: str) -> ReviewerScorecard: ...

    def run_red_team(self, proposal_id: str) -> RedTeamResult: ...


class DebriefCorpus(Protocol):
    """Driven port: accesses past debrief feedback from corpus."""

    def get_debrief_weaknesses(self, proposal_id: str) -> list[DebriefCrossCheckEntry]: ...


class FinalReviewService:
    """Driving port: orchestrates final review with simulated evaluator.

    Delegates simulation to ReviewSimulator and debrief lookup to DebriefCorpus.
    Tracks review rounds and enforces max iteration limit.
    """

    def __init__(
        self,
        review_simulator: ReviewSimulator,
        debrief_corpus: DebriefCorpus | None = None,
    ) -> None:
        self._simulator = review_simulator
        self._corpus = debrief_corpus

    def run_reviewer_simulation(self, proposal_id: str) -> ReviewerScorecard:
        """Run reviewer persona simulation scoring against evaluation criteria."""
        return self._simulator.simulate_reviewer(proposal_id)

    def run_red_team(self, proposal_id: str) -> RedTeamResult:
        """Run red team review identifying objections by severity."""
        return self._simulator.run_red_team(proposal_id)

    def run_debrief_cross_check(self, proposal_id: str) -> DebriefCrossCheckResult:
        """Check proposal against known weaknesses from past debriefs.

        When no corpus is configured or no debriefs exist, returns a graceful
        message indicating the check improves as debriefs are ingested.
        """
        if self._corpus is None:
            return DebriefCrossCheckResult(
                entries=[],
                message="No past debrief data available",
                improvement_note="This check improves as debriefs are ingested",
            )

        entries = self._corpus.get_debrief_weaknesses(proposal_id)

        if not entries:
            return DebriefCrossCheckResult(
                entries=[],
                message="No past debrief data available",
                improvement_note="This check improves as debriefs are ingested",
            )

        return DebriefCrossCheckResult(
            entries=entries,
            message=f"Found {len(entries)} known weakness(es) from past debriefs",
        )

    def re_review(
        self,
        proposal_id: str,
        prior_findings: list[RedTeamFinding],
        review_round: int,
    ) -> ReReviewResult | ForcedSignOffResult:
        """Re-review after fixes. Returns ForcedSignOffResult if max iterations reached."""
        if review_round > MAX_REVIEW_ITERATIONS:
            return ForcedSignOffResult(
                sign_off_required=True,
                review_round=review_round,
                unresolved_issues=list(prior_findings),
                message=f"Sign-off required after {MAX_REVIEW_ITERATIONS} review iterations",
            )

        # Run new red team to see what remains
        current_result = self._simulator.run_red_team(proposal_id)
        current_objections = {f.objection for f in current_result.findings}

        resolved: list[RedTeamFinding] = []
        remaining: list[RedTeamFinding] = []

        for finding in prior_findings:
            if finding.objection not in current_objections:
                resolved.append(finding)
            else:
                remaining.append(finding)

        return ReReviewResult(
            resolved_issues=resolved,
            remaining_issues=remaining,
            review_round=review_round,
        )

    def sign_off(
        self,
        proposal_id: str,
        *,
        unresolved_issues: list[RedTeamFinding] | None = None,
        timestamp: str = "",
    ) -> SignOffRecord:
        """Record human sign-off on the final review."""
        return SignOffRecord(
            signed_off=True,
            timestamp=timestamp,
            unresolved_issues=unresolved_issues or [],
            artifact_written=True,
        )
