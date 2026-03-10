"""Unit tests for FinalReviewService (driving port) -- simulated government evaluator.

Test Budget: 6 behaviors x 2 = 12 unit tests max.
Tests enter through driving port (FinalReviewService).
Driven ports (ReviewSimulator, DebriefCorpus) mocked at port boundary.
Domain objects (ReviewerScorecard, RedTeamFinding, etc.) are real collaborators.

Behaviors:
1. Reviewer simulation returns scorecard with criteria scores and rationale
2. Red team review returns findings tagged by severity with section/page
3. Debrief cross-check flags known weaknesses from corpus
4. No debriefs available returns graceful message
5. Re-review tracks resolved vs remaining issues with iteration count
6. Third review cycle forces sign-off with unresolved issues documented
"""

from __future__ import annotations

from pes.domain.final_review import (
    CriterionScore,
    DebriefCrossCheckEntry,
    DebriefCrossCheckResult,
    ForcedSignOffResult,
    RedTeamFinding,
    RedTeamResult,
    ReReviewResult,
    ReviewerScorecard,
)
from pes.domain.final_review_service import (
    FinalReviewService,
)

# ---------------------------------------------------------------------------
# Fake driven ports at port boundary
# ---------------------------------------------------------------------------


class FakeReviewSimulator:
    """Fake driven port: deterministic reviewer simulation."""

    def __init__(
        self,
        *,
        scorecard: ReviewerScorecard | None = None,
        red_team_result: RedTeamResult | None = None,
        re_review_findings: list[RedTeamFinding] | None = None,
    ) -> None:
        self._scorecard = scorecard or ReviewerScorecard(
            scores=[
                CriterionScore("Technical Merit", 8, "Strong approach"),
                CriterionScore("Innovation", 7, "Novel but incremental"),
                CriterionScore("Feasibility", 9, "Well-scoped plan"),
                CriterionScore("Team Qualifications", 6, "Limited past performance"),
                CriterionScore("Commercialization", 7, "Clear dual-use pathway"),
            ],
            artifact_written=True,
        )
        self._red_team = red_team_result or RedTeamResult(
            findings=[
                RedTeamFinding("Weak TRL justification", "HIGH", "3.2", 7),
                RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
                RedTeamFinding("Minor formatting issue", "LOW", "2.1", 3),
            ],
            artifact_written=True,
        )
        # On re-review, return fewer findings (simulate resolution)
        self._re_review_findings = re_review_findings or [
            RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
        ]
        self._call_count = 0

    def simulate_reviewer(self, proposal_id: str) -> ReviewerScorecard:
        return self._scorecard

    def run_red_team(self, proposal_id: str) -> RedTeamResult:
        self._call_count += 1
        if self._call_count > 1:
            return RedTeamResult(
                findings=self._re_review_findings,
                artifact_written=True,
            )
        return self._red_team


class FakeDebriefCorpus:
    """Fake driven port: deterministic debrief data."""

    def __init__(self, entries: list[DebriefCrossCheckEntry] | None = None) -> None:
        self._entries = entries

    def get_debrief_weaknesses(
        self,
        proposal_id: str,
    ) -> list[DebriefCrossCheckEntry]:
        if self._entries is None:
            return []
        return list(self._entries)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_service(
    *,
    simulator: FakeReviewSimulator | None = None,
    corpus: FakeDebriefCorpus | None = None,
) -> FinalReviewService:
    sim = simulator or FakeReviewSimulator()
    return FinalReviewService(
        review_simulator=sim,
        debrief_corpus=corpus,
    )


def _prior_high_findings() -> list[RedTeamFinding]:
    return [
        RedTeamFinding("Weak TRL justification", "HIGH", "3.2", 7),
        RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
    ]


# ---------------------------------------------------------------------------
# Behavior 1: Reviewer simulation returns scorecard with criteria and rationale
# ---------------------------------------------------------------------------


class TestReviewerSimulation:
    def test_returns_scorecard_with_five_criteria(self):
        service = _make_service()

        result = service.run_reviewer_simulation("AF243-001")

        assert isinstance(result, ReviewerScorecard)
        assert result.criteria_count == 5

    def test_each_score_includes_rationale(self):
        service = _make_service()

        result = service.run_reviewer_simulation("AF243-001")

        for score in result.scores:
            assert score.rationale, f"Missing rationale for {score.criterion}"
            assert score.criterion
            assert score.score > 0


# ---------------------------------------------------------------------------
# Behavior 2: Red team returns findings tagged by severity with section/page
# ---------------------------------------------------------------------------


class TestRedTeamReview:
    def test_returns_findings_with_severity_tags(self):
        service = _make_service()

        result = service.run_red_team("AF243-001")

        assert isinstance(result, RedTeamResult)
        severities = {f.severity for f in result.findings}
        assert "HIGH" in severities
        assert "MEDIUM" in severities
        assert "LOW" in severities

    def test_each_finding_references_section_and_page(self):
        service = _make_service()

        result = service.run_red_team("AF243-001")

        for finding in result.findings:
            assert finding.section, "Missing section reference"
            assert finding.page > 0, "Missing page reference"


# ---------------------------------------------------------------------------
# Behavior 3: Debrief cross-check flags known weaknesses
# ---------------------------------------------------------------------------


class TestDebriefCrossCheck:
    def test_flags_known_weakness_from_corpus(self):
        corpus = FakeDebriefCorpus(
            entries=[
                DebriefCrossCheckEntry(
                    weakness="transition pathway specificity",
                    addressed=False,
                    source_debrief="AF241-087",
                ),
            ]
        )
        service = _make_service(corpus=corpus)

        result = service.run_debrief_cross_check("AF243-001")

        assert isinstance(result, DebriefCrossCheckResult)
        assert len(result.entries) == 1
        assert result.entries[0].weakness == "transition pathway specificity"

    def test_reports_whether_weakness_is_addressed(self):
        corpus = FakeDebriefCorpus(
            entries=[
                DebriefCrossCheckEntry(
                    weakness="transition pathway specificity",
                    addressed=False,
                    source_debrief="AF241-087",
                ),
            ]
        )
        service = _make_service(corpus=corpus)

        result = service.run_debrief_cross_check("AF243-001")

        assert isinstance(result.entries[0].addressed, bool)


# ---------------------------------------------------------------------------
# Behavior 4: No debriefs available returns graceful message
# ---------------------------------------------------------------------------


class TestNoDebriefs:
    def test_returns_no_data_message(self):
        corpus = FakeDebriefCorpus(entries=None)
        service = _make_service(corpus=corpus)

        result = service.run_debrief_cross_check("AF243-001")

        assert "No past debrief data available" in result.message

    def test_includes_improvement_note(self):
        corpus = FakeDebriefCorpus(entries=None)
        service = _make_service(corpus=corpus)

        result = service.run_debrief_cross_check("AF243-001")

        assert result.improvement_note


# ---------------------------------------------------------------------------
# Behavior 5: Re-review tracks resolved vs remaining with iteration count
# ---------------------------------------------------------------------------


class TestReReview:
    def test_tracks_resolved_and_remaining_issues(self):
        # Simulator returns only MEDIUM finding on re-review (HIGH resolved)
        simulator = FakeReviewSimulator(
            red_team_result=RedTeamResult(
                findings=[
                    RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
                ],
                artifact_written=True,
            ),
        )
        service = _make_service(simulator=simulator)
        prior = _prior_high_findings()

        result = service.re_review("AF243-001", prior_findings=prior, review_round=2)

        assert isinstance(result, ReReviewResult)
        assert len(result.resolved_issues) > 0
        assert result.review_round == 2

    def test_resolved_issues_not_in_remaining(self):
        simulator = FakeReviewSimulator(
            red_team_result=RedTeamResult(
                findings=[
                    RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
                ],
                artifact_written=True,
            ),
        )
        service = _make_service(simulator=simulator)
        prior = _prior_high_findings()

        result = service.re_review("AF243-001", prior_findings=prior, review_round=2)

        resolved_objs = {f.objection for f in result.resolved_issues}
        remaining_objs = {f.objection for f in result.remaining_issues}
        assert not resolved_objs.intersection(remaining_objs)


# ---------------------------------------------------------------------------
# Behavior 6: Third review forces sign-off with unresolved issues documented
# ---------------------------------------------------------------------------


class TestForcedSignOff:
    def test_forces_signoff_after_max_iterations(self):
        service = _make_service()
        unresolved = [
            RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
        ]

        result = service.re_review("AF243-001", prior_findings=unresolved, review_round=3)

        assert isinstance(result, ForcedSignOffResult)
        assert result.sign_off_required is True

    def test_documents_unresolved_issues_in_signoff(self):
        service = _make_service()
        unresolved = [
            RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
        ]

        result = service.re_review("AF243-001", prior_findings=unresolved, review_round=3)

        assert len(result.unresolved_issues) > 0
        assert result.unresolved_issues[0].severity == "MEDIUM"
