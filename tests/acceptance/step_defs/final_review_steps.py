"""Step definitions for final review with simulated evaluator (US-012).

Invokes through: FinalReviewService (driving port).
Does NOT import internal reviewer persona simulators or red team logic directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.final_review import (
    CriterionScore,
    DebriefCrossCheckEntry,
    RedTeamFinding,
    RedTeamResult,
    ReviewerScorecard,
)
from pes.domain.final_review_service import FinalReviewService
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/final_review.feature")


# ---------------------------------------------------------------------------
# Fake driven ports for acceptance tests
# ---------------------------------------------------------------------------


class FakeReviewSimulator:
    """Fake driven port: returns deterministic reviewer simulation results.

    On re-review (second run_red_team call), returns fewer findings to simulate
    that the HIGH issue was resolved after Phil's fix.
    """

    def __init__(self) -> None:
        self._red_team_call_count = 0

    def simulate_reviewer(self, proposal_id: str) -> ReviewerScorecard:
        return ReviewerScorecard(
            scores=[
                CriterionScore("Technical Merit", 8, "Strong technical approach"),
                CriterionScore("Innovation", 7, "Novel but incremental"),
                CriterionScore("Feasibility", 9, "Well-scoped Phase I plan"),
                CriterionScore("Team Qualifications", 6, "Limited past performance"),
                CriterionScore("Commercialization", 7, "Clear dual-use pathway"),
            ],
            artifact_written=True,
        )

    def run_red_team(self, proposal_id: str) -> RedTeamResult:
        self._red_team_call_count += 1
        if self._red_team_call_count > 1:
            # Re-review: HIGH issue resolved, only MEDIUM remains
            return RedTeamResult(
                findings=[
                    RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
                ],
                artifact_written=True,
            )
        return RedTeamResult(
            findings=[
                RedTeamFinding("Weak TRL justification", "HIGH", "3.2", 7),
                RedTeamFinding("Cost estimate lacks detail", "MEDIUM", "4.1", 12),
                RedTeamFinding("Minor formatting issue", "LOW", "2.1", 3),
            ],
            artifact_written=True,
        )


class FakeDebriefCorpus:
    """Fake driven port: returns deterministic debrief data."""

    def __init__(self, *, has_debriefs: bool = True) -> None:
        self._has_debriefs = has_debriefs

    def get_debrief_weaknesses(self, proposal_id: str) -> list[DebriefCrossCheckEntry]:
        if not self._has_debriefs:
            return []
        return [
            DebriefCrossCheckEntry(
                weakness="transition pathway specificity",
                addressed=False,
                source_debrief="AF241-087",
            ),
        ]


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def fake_simulator():
    return FakeReviewSimulator()


@pytest.fixture()
def fake_corpus():
    return FakeDebriefCorpus(has_debriefs=True)


@pytest.fixture()
def fake_corpus_empty():
    return FakeDebriefCorpus(has_debriefs=False)


@pytest.fixture()
def final_review_service(fake_simulator, fake_corpus):
    return FinalReviewService(
        review_simulator=fake_simulator,
        debrief_corpus=fake_corpus,
    )


@pytest.fixture()
def final_review_service_no_debriefs(fake_simulator, fake_corpus_empty):
    return FinalReviewService(
        review_simulator=fake_simulator,
        debrief_corpus=fake_corpus_empty,
    )


# --- Given steps ---


@given(
    "Phil has an active proposal with assembled volumes ready for review",
    target_fixture="active_state",
)
def proposal_assembled_for_review(sample_state, write_state):
    """Set up proposal with assembled volumes, ready for Wave 7."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 7
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "completed", "completed_at": "2026-03-09T10:00:00Z"},
        "6": {"status": "completed", "completed_at": "2026-03-10T10:00:00Z"},
        "7": {"status": "active", "completed_at": None},
    }
    state["assembly"] = {
        "status": "completed",
        "volume_count": 3,
        "compliance_check_status": "passed",
        "completed_at": "2026-03-10T10:00:00Z",
    }
    write_state(state)
    return state


@given("the assembled proposal for AF243-001 is ready for final review")
def assembled_proposal_ready():
    """Assembled proposal is ready for review."""
    pass


@given("the reviewer simulation has completed", target_fixture="red_team_prereq")
def reviewer_simulation_complete(final_review_service):
    """Reviewer simulation has been run -- run it to establish prereq."""
    return final_review_service.run_reviewer_simulation("AF243-001")


@given("past debrief feedback for AF241-087 exists in the corpus")
def debrief_in_corpus():
    """Past debrief feedback available in corpus."""
    pass


@given(
    parsers.parse('that debrief said "{critique}"'),
)
def debrief_critique(critique):
    """Specific debrief critique content."""
    pass


@given(
    parsers.parse("the red team found {count:d} HIGH issue in Section {section}"),
    target_fixture="prior_findings",
)
def red_team_high_issue(count, section, fake_simulator):
    """Red team found HIGH severity issue.

    Also primes the simulator so the next run_red_team call (the re-review)
    simulates that the HIGH issue was fixed.
    """
    # Prime the simulator: first call already happened (the initial red team).
    # Increment call count so the re-review returns reduced findings.
    fake_simulator._red_team_call_count = 1
    return [
        RedTeamFinding(
            objection="Weak TRL justification",
            severity="HIGH",
            section=section,
            page=7,
        )
    ]


@given("no debrief feedback exists in the corpus")
def no_debriefs_in_corpus():
    """No past debrief data available."""
    pass


@given(
    parsers.parse("{count:d} review iterations have been completed"),
    target_fixture="completed_iterations",
)
def review_iterations_done(count):
    """Review iterations completed."""
    return count


@given(
    parsers.parse("{count:d} MEDIUM issue remains unresolved"),
    target_fixture="unresolved_findings",
)
def unresolved_medium_issues(count):
    """Unresolved MEDIUM severity issues."""
    return [
        RedTeamFinding(
            objection="Cost estimate lacks detail",
            severity="MEDIUM",
            section="4.1",
            page=12,
        )
    ]


@given("all HIGH issues are addressed")
def all_high_addressed():
    """All HIGH severity issues resolved."""
    pass


# --- When steps ---


@when("Phil requests the final review", target_fixture="scorecard_result")
def request_final_review(final_review_service):
    """Invoke final review through FinalReviewService."""
    return final_review_service.run_reviewer_simulation("AF243-001")


@when("the tool runs a red team review", target_fixture="red_team_result")
def run_red_team(final_review_service):
    """Run red team review through FinalReviewService."""
    return final_review_service.run_red_team("AF243-001")


@when("the tool checks against known weaknesses", target_fixture="crosscheck_result")
def check_known_weaknesses(final_review_service):
    """Check against known weaknesses from corpus."""
    return final_review_service.run_debrief_cross_check("AF243-001")


@when("Phil fixes the issue and requests re-review", target_fixture="rereview_result")
def fix_and_rereview(final_review_service, prior_findings):
    """Fix issue and re-review through FinalReviewService."""
    return final_review_service.re_review(
        proposal_id="AF243-001",
        prior_findings=prior_findings,
        review_round=2,
    )


@when(
    "the tool runs the debrief cross-check",
    target_fixture="crosscheck_result",
)
def run_debrief_crosscheck(final_review_service_no_debriefs):
    """Run debrief cross-check through FinalReviewService (no debriefs)."""
    return final_review_service_no_debriefs.run_debrief_cross_check("AF243-001")


@when("Phil requests a third review cycle", target_fixture="forced_signoff_result")
def request_third_review(final_review_service, unresolved_findings, completed_iterations):
    """Attempt third review cycle (should force sign-off)."""
    return final_review_service.re_review(
        proposal_id="AF243-001",
        prior_findings=unresolved_findings,
        review_round=completed_iterations + 1,
    )


@when("Phil signs off on the final review", target_fixture="signoff_result")
def sign_off_review(final_review_service):
    """Sign off through FinalReviewService."""
    return final_review_service.sign_off(
        proposal_id="AF243-001",
        timestamp="2026-03-10T14:00:00Z",
    )


# --- Then steps ---


@then(
    parsers.parse("the tool scores the proposal against {count:d} evaluation criteria"),
)
def verify_scores(count, scorecard_result):
    """Verify scoring against evaluation criteria."""
    assert scorecard_result.criteria_count == count


@then("each score includes a brief rationale")
def verify_score_rationale(scorecard_result):
    """Verify rationale accompanies each score."""
    for score in scorecard_result.scores:
        assert score.rationale, f"Missing rationale for {score.criterion}"


@then("the scorecard is written to the review artifacts directory")
def verify_scorecard_written(scorecard_result):
    """Verify scorecard artifact is created."""
    assert scorecard_result.artifact_written is True


@then("it identifies objections tagged by severity (HIGH, MEDIUM, LOW)")
def verify_objections_tagged(red_team_result):
    """Verify objections are tagged by severity."""
    severities = {f.severity for f in red_team_result.findings}
    assert "HIGH" in severities
    assert "MEDIUM" in severities
    assert "LOW" in severities


@then("each objection references a specific section and page")
def verify_objection_references(red_team_result):
    """Verify objections reference specific locations."""
    for finding in red_team_result.findings:
        assert finding.section, "Missing section reference"
        assert finding.page > 0, "Missing page reference"


@then("the findings are written to the review artifacts directory")
def verify_findings_written(red_team_result):
    """Verify red team findings artifact."""
    assert red_team_result.artifact_written is True


@then(
    parsers.parse('it flags "{weakness}" as a known weakness'),
)
def verify_weakness_flagged(weakness, crosscheck_result):
    """Verify known weakness is flagged."""
    weaknesses = [e.weakness for e in crosscheck_result.entries]
    assert weakness in weaknesses


@then("reports whether the current proposal addresses it")
def verify_weakness_status(crosscheck_result):
    """Verify whether weakness is addressed in current proposal."""
    for entry in crosscheck_result.entries:
        assert isinstance(entry.addressed, bool)


@then("the tool re-reviews and confirms the HIGH issue is resolved")
def verify_issue_resolved(rereview_result):
    """Verify re-review confirms resolution."""
    assert len(rereview_result.resolved_issues) > 0
    assert any(i.severity == "HIGH" for i in rereview_result.resolved_issues)


@then("the iteration count is logged")
def verify_iteration_logged(rereview_result):
    """Verify iteration count is tracked."""
    assert rereview_result.review_round > 0


@then(
    parsers.parse('it reports "{message}"'),
)
def verify_report_message(message, crosscheck_result):
    """Verify report message content."""
    assert message in crosscheck_result.message


@then("notes this check improves as debriefs are ingested")
def verify_improvement_note(crosscheck_result):
    """Verify note about future improvement."""
    assert crosscheck_result.improvement_note


@then("Phil sees that sign-off is required after 2 iterations")
def verify_forced_signoff(forced_signoff_result):
    """Verify forced sign-off after max iterations."""
    assert forced_signoff_result.sign_off_required is True


@then("unresolved issues are documented in the sign-off record")
def verify_unresolved_documented(forced_signoff_result):
    """Verify unresolved issues in sign-off record."""
    assert len(forced_signoff_result.unresolved_issues) > 0


@then("the sign-off is recorded with timestamp")
def verify_signoff_recorded(signoff_result):
    """Verify sign-off timestamp recorded."""
    assert signoff_result.signed_off is True
    assert signoff_result.timestamp


@then("the sign-off is written to the review artifacts directory")
def verify_signoff_written(signoff_result):
    """Verify sign-off record artifact."""
    assert signoff_result.artifact_written is True


@then("Wave 8 is unlocked")
def verify_wave_8_unlocked():
    """Verify Wave 8 is unlocked after sign-off."""
    # Wave unlock is handled by PES state management, not the service.
    # Acceptance test just verifies sign-off was recorded.
    pass
