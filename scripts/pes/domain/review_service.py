"""Review service -- driving port for section review with iteration loop and checkpoint.

Orchestrates: section review producing scorecards, re-review tracking addressed
findings, escalation after max review cycles, and full draft compliance checkpoint.
Validates preconditions (draft must exist), delegates to DraftReviewer driven port.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pes.domain.draft import SectionDraft
from pes.domain.outline import ProposalOutline
from pes.domain.review import ReviewFinding, ReviewScorecard

MAX_REVIEW_ROUNDS = 2


class DraftReviewer(Protocol):
    """Driven port: reviews a section draft and produces a scorecard."""

    def review(
        self,
        draft: SectionDraft,
        *,
        prior_findings: list[ReviewFinding] | None = None,
    ) -> ReviewScorecard: ...


class NoDraftExistsError(Exception):
    """Raised when review is attempted without an existing draft."""


@dataclass
class ReviewResult:
    """Result of a section review with finding tracking."""

    scorecard: ReviewScorecard
    review_round: int
    addressed_findings: list[ReviewFinding] = field(default_factory=list)
    open_findings: list[ReviewFinding] = field(default_factory=list)


@dataclass
class EscalationResult:
    """Result when max review cycles exceeded -- escalation for human decision."""

    unresolved_findings: list[ReviewFinding]
    review_round: int
    options: list[str] = field(default_factory=lambda: ["accept", "revise"])


@dataclass
class FullReviewResult:
    """Result of full draft review across all sections."""

    section_scorecards: dict[str, ReviewScorecard]
    all_compliance_addressed: bool
    unaddressed_item_ids: list[str]
    can_approve: bool


class ReviewService:
    """Driving port: reviews proposal sections with iteration tracking.

    Delegates to DraftReviewer driven port for scorecard generation.
    Tracks review rounds, compares prior findings on re-review,
    and escalates after MAX_REVIEW_ROUNDS.
    """

    def __init__(self, draft_reviewer: DraftReviewer) -> None:
        self._reviewer = draft_reviewer

    def review_section(
        self,
        draft: SectionDraft | None,
        review_round: int,
        *,
        prior_findings: list[ReviewFinding] | None = None,
        section_id: str | None = None,
    ) -> ReviewResult | EscalationResult:
        """Review a section draft.

        Raises NoDraftExistsError if draft is None.
        Returns EscalationResult if review_round > MAX_REVIEW_ROUNDS.
        Returns ReviewResult with finding tracking otherwise.
        """
        if draft is None:
            name = section_id or "this section"
            raise NoDraftExistsError(
                f"No draft exists for {name}. "
                "Draft the section first before requesting review."
            )

        # Escalate if past max rounds
        if review_round > MAX_REVIEW_ROUNDS and prior_findings:
            return EscalationResult(
                unresolved_findings=list(prior_findings),
                review_round=review_round,
            )

        # Delegate to driven port
        scorecard = self._reviewer.review(
            draft, prior_findings=prior_findings,
        )

        # Track addressed vs open findings on re-review
        addressed: list[ReviewFinding] = []
        open_findings: list[ReviewFinding] = []

        if prior_findings:
            current_locations = {f.location for f in scorecard.findings}
            for pf in prior_findings:
                if pf.location not in current_locations:
                    addressed.append(pf)
                else:
                    open_findings.append(pf)

        return ReviewResult(
            scorecard=scorecard,
            review_round=review_round,
            addressed_findings=addressed,
            open_findings=open_findings,
        )

    def full_draft_review(
        self,
        drafts: list[SectionDraft],
        outline: ProposalOutline,
    ) -> FullReviewResult:
        """Review all sections and verify compliance coverage.

        Checks that every compliance item from the outline is addressed
        by at least one draft section.
        """
        # Collect all required compliance item IDs from outline
        required_ids: set[str] = set()
        for section in outline.sections:
            required_ids.update(section.compliance_item_ids)

        # Collect all addressed compliance item IDs from drafts
        addressed_ids: set[str] = set()
        section_scorecards: dict[str, ReviewScorecard] = {}

        for draft in drafts:
            addressed_ids.update(draft.compliance_item_ids)
            scorecard = self._reviewer.review(draft)
            section_scorecards[draft.section_id] = scorecard

        unaddressed = sorted(required_ids - addressed_ids)
        all_addressed = len(unaddressed) == 0

        return FullReviewResult(
            section_scorecards=section_scorecards,
            all_compliance_addressed=all_addressed,
            unaddressed_item_ids=unaddressed,
            can_approve=all_addressed,
        )
