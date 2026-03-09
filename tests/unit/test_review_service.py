"""Unit tests for ReviewService (driving port) -- section review with iteration loop.

Test Budget: 5 behaviors x 2 = 10 unit tests max.
Tests enter through driving port (ReviewService).
Driven port (DraftReviewer) mocked at port boundary.
Domain objects (ReviewFinding, ReviewScorecard, SectionDraft) are real collaborators.

Behaviors:
1. Review section produces scorecard with findings by location and severity
2. Re-review tracks which prior findings were addressed vs open
3. Third review cycle escalates unresolved findings
4. Full draft review verifies compliance coverage across all sections
5. Review without existing draft raises descriptive error
"""

from __future__ import annotations

import pytest

from pes.domain.draft import SectionDraft
from pes.domain.outline import OutlineSection, ProposalOutline
from pes.domain.review import ReviewFinding, ReviewScorecard
from pes.domain.review_service import (
    EscalationResult,
    FullReviewResult,
    NoDraftExistsError,
    ReviewResult,
    ReviewService,
)

# ---------------------------------------------------------------------------
# Fake driven port (DraftReviewer) at port boundary
# ---------------------------------------------------------------------------


class FakeDraftReviewer:
    """Fake driven port that produces deterministic review scorecards."""

    def __init__(
        self,
        *,
        findings: list[ReviewFinding] | None = None,
        strengths: list[str] | None = None,
        weaknesses: list[str] | None = None,
    ) -> None:
        self._findings = findings or [
            ReviewFinding(
                location="section-1.para-2",
                severity="major",
                suggestion="Strengthen TRL advancement methodology",
            ),
            ReviewFinding(
                location="section-1.para-5",
                severity="minor",
                suggestion="Add quantitative metrics",
            ),
        ]
        self._strengths = strengths or ["Clear technical narrative"]
        self._weaknesses = weaknesses or ["Weak risk mitigation"]
        self.review_called_with: dict | None = None

    def review(
        self,
        draft: SectionDraft,
        *,
        prior_findings: list[ReviewFinding] | None = None,
    ) -> ReviewScorecard:
        self.review_called_with = {
            "draft": draft,
            "prior_findings": prior_findings,
        }
        if prior_findings:
            # On re-review, resolve the first prior finding, keep second
            return ReviewScorecard(
                findings=self._findings[1:],
                strengths=[*self._strengths, "Addressed prior findings"],
                weaknesses=[],
            )
        return ReviewScorecard(
            findings=list(self._findings),
            strengths=list(self._strengths),
            weaknesses=list(self._weaknesses),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_draft(
    *,
    section_id: str = "technical-approach",
    word_count: int = 500,
    compliance_item_ids: list[str] | None = None,
    iteration: int = 1,
) -> SectionDraft:
    words = ["word"] * word_count
    content = " ".join(words)
    return SectionDraft(
        section_id=section_id,
        content=content,
        compliance_item_ids=compliance_item_ids or ["CI-001", "CI-002", "CI-003"],
        iteration=iteration,
    )


def _make_outline(
    *,
    sections: list[OutlineSection] | None = None,
) -> ProposalOutline:
    if sections is None:
        sections = [
            OutlineSection(
                section_id="technical-approach",
                title="Technical Approach",
                compliance_item_ids=["CI-001", "CI-002", "CI-003"],
                page_budget=8.0,
                figure_placeholders=["fig-1"],
                thesis_statement="Novel approach",
            ),
            OutlineSection(
                section_id="statement-of-work",
                title="Statement of Work",
                compliance_item_ids=["CI-004", "CI-005"],
                page_budget=4.0,
                figure_placeholders=[],
                thesis_statement="Milestone deliverables",
            ),
        ]
    return ProposalOutline(sections=sections)


def _make_service(
    reviewer: FakeDraftReviewer | None = None,
) -> tuple[ReviewService, FakeDraftReviewer]:
    r = reviewer or FakeDraftReviewer()
    return ReviewService(draft_reviewer=r), r


def _prior_findings() -> list[ReviewFinding]:
    return [
        ReviewFinding(
            location="section-1.para-2",
            severity="major",
            suggestion="Strengthen TRL advancement methodology",
        ),
        ReviewFinding(
            location="section-1.para-5",
            severity="minor",
            suggestion="Add quantitative metrics",
        ),
    ]


# ---------------------------------------------------------------------------
# Behavior 1: Review section produces scorecard with findings
# ---------------------------------------------------------------------------


class TestReviewSectionHappyPath:
    def test_returns_scorecard_with_findings(self):
        service, _reviewer = _make_service()
        draft = _make_draft()

        result = service.review_section(draft=draft, review_round=1)

        assert isinstance(result, ReviewResult)
        assert len(result.scorecard.findings) == 2
        assert result.scorecard.findings[0].location == "section-1.para-2"
        assert result.scorecard.findings[0].severity == "major"

    def test_scorecard_includes_strengths_and_weaknesses(self):
        service, _ = _make_service()
        draft = _make_draft()

        result = service.review_section(draft=draft, review_round=1)

        assert len(result.scorecard.strengths) > 0
        assert len(result.scorecard.weaknesses) > 0


# ---------------------------------------------------------------------------
# Behavior 2: Re-review tracks addressed vs open findings
# ---------------------------------------------------------------------------


class TestReReviewTracking:
    def test_tracks_addressed_and_open_findings(self):
        service, _ = _make_service()
        draft = _make_draft()
        prior = _prior_findings()

        result = service.review_section(
            draft=draft, review_round=2, prior_findings=prior,
        )

        assert isinstance(result, ReviewResult)
        assert len(result.addressed_findings) > 0
        assert isinstance(result.open_findings, list)

    def test_addressed_findings_are_not_in_current_scorecard(self):
        service, _ = _make_service()
        draft = _make_draft()
        prior = _prior_findings()

        result = service.review_section(
            draft=draft, review_round=2, prior_findings=prior,
        )

        # Addressed findings should not appear in current scorecard
        current_locations = {f.location for f in result.scorecard.findings}
        for addressed in result.addressed_findings:
            assert addressed.location not in current_locations


# ---------------------------------------------------------------------------
# Behavior 3: Third review cycle escalates unresolved findings
# ---------------------------------------------------------------------------


class TestEscalationOnThirdCycle:
    def test_returns_escalation_result_on_round_3(self):
        service, _ = _make_service()
        draft = _make_draft()
        prior = _prior_findings()

        result = service.review_section(
            draft=draft, review_round=3, prior_findings=prior,
        )

        assert isinstance(result, EscalationResult)
        assert len(result.unresolved_findings) > 0

    def test_escalation_provides_accept_and_revise_options(self):
        service, _ = _make_service()
        draft = _make_draft()
        prior = _prior_findings()

        result = service.review_section(
            draft=draft, review_round=3, prior_findings=prior,
        )

        assert "accept" in result.options
        assert "revise" in result.options


# ---------------------------------------------------------------------------
# Behavior 4: Full draft review verifies compliance coverage
# ---------------------------------------------------------------------------


class TestFullDraftReview:
    def test_reports_all_compliance_addressed_when_covered(self):
        reviewer = FakeDraftReviewer(findings=[], strengths=["Good"], weaknesses=[])
        service, _ = _make_service(reviewer)
        outline = _make_outline()
        drafts = [
            _make_draft(
                section_id="technical-approach",
                compliance_item_ids=["CI-001", "CI-002", "CI-003"],
            ),
            _make_draft(
                section_id="statement-of-work",
                compliance_item_ids=["CI-004", "CI-005"],
            ),
        ]

        result = service.full_draft_review(drafts=drafts, outline=outline)

        assert isinstance(result, FullReviewResult)
        assert result.all_compliance_addressed is True
        assert result.can_approve is True

    def test_flags_unaddressed_compliance_items(self):
        reviewer = FakeDraftReviewer(findings=[], strengths=["Good"], weaknesses=[])
        service, _ = _make_service(reviewer)
        outline = _make_outline()
        # technical-approach draft missing CI-003
        drafts = [
            _make_draft(
                section_id="technical-approach",
                compliance_item_ids=["CI-001", "CI-002"],
            ),
            _make_draft(
                section_id="statement-of-work",
                compliance_item_ids=["CI-004", "CI-005"],
            ),
        ]

        result = service.full_draft_review(drafts=drafts, outline=outline)

        assert result.all_compliance_addressed is False
        assert "CI-003" in result.unaddressed_item_ids
        assert result.can_approve is False


# ---------------------------------------------------------------------------
# Behavior 5: Review without existing draft raises error
# ---------------------------------------------------------------------------


class TestReviewWithoutDraft:
    def test_raises_no_draft_exists_error(self):
        service, _ = _make_service()

        with pytest.raises(NoDraftExistsError) as exc_info:
            service.review_section(draft=None, review_round=1)

        assert "no draft" in str(exc_info.value).lower()

    def test_error_includes_draft_guidance(self):
        service, _ = _make_service()

        with pytest.raises(NoDraftExistsError) as exc_info:
            service.review_section(draft=None, review_round=1)

        assert "draft" in str(exc_info.value).lower()
