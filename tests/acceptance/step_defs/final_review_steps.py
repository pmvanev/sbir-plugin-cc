"""Step definitions for final review with simulated evaluator (US-012).

Invokes through: FinalReviewService (driving port).
Does NOT import internal reviewer persona simulators or red team logic directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/final_review.feature")


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


@given("the reviewer simulation has completed")
def reviewer_simulation_complete():
    """Reviewer simulation has been run."""
    pass


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
)
def red_team_high_issue(count, section):
    """Red team found HIGH severity issue."""
    pass


@given("no debrief feedback exists in the corpus")
def no_debriefs_in_corpus():
    """No past debrief data available."""
    pass


@given(
    parsers.parse("{count:d} review iterations have been completed"),
)
def review_iterations_done(count):
    """Review iterations completed."""
    pass


@given(
    parsers.parse("{count:d} MEDIUM issue remains unresolved"),
)
def unresolved_medium_issues(count):
    """Unresolved MEDIUM severity issues."""
    pass


@given("all HIGH issues are addressed")
def all_high_addressed():
    """All HIGH severity issues resolved."""
    pass


# --- When steps ---


@when("Phil requests the final review")
def request_final_review():
    """Invoke final review through FinalReviewService."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("the tool runs a red team review")
def run_red_team():
    """Run red team review through FinalReviewService."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("the tool checks against known weaknesses")
def check_known_weaknesses():
    """Check against known weaknesses from corpus."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("Phil fixes the issue and requests re-review")
def fix_and_rereview():
    """Fix issue and re-review through FinalReviewService."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("the tool runs the debrief cross-check")
def run_debrief_crosscheck():
    """Run debrief cross-check through FinalReviewService."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("Phil requests a third review cycle")
def request_third_review():
    """Attempt third review cycle (should force sign-off)."""
    pytest.skip("Awaiting FinalReviewService implementation")


@when("Phil signs off on the final review")
def sign_off_review():
    """Sign off through FinalReviewService."""
    pytest.skip("Awaiting FinalReviewService implementation")


# --- Then steps ---


@then(
    parsers.parse("the tool scores the proposal against {count:d} evaluation criteria"),
)
def verify_scores(count):
    """Verify scoring against evaluation criteria."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("each score includes a brief rationale")
def verify_score_rationale():
    """Verify rationale accompanies each score."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("the scorecard is written to the review artifacts directory")
def verify_scorecard_written():
    """Verify scorecard artifact is created."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("it identifies objections tagged by severity (HIGH, MEDIUM, LOW)")
def verify_objections_tagged():
    """Verify objections are tagged by severity."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("each objection references a specific section and page")
def verify_objection_references():
    """Verify objections reference specific locations."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("the findings are written to the review artifacts directory")
def verify_findings_written():
    """Verify red team findings artifact."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then(
    parsers.parse('it flags "{weakness}" as a known weakness'),
)
def verify_weakness_flagged(weakness):
    """Verify known weakness is flagged."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("reports whether the current proposal addresses it")
def verify_weakness_status():
    """Verify whether weakness is addressed in current proposal."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("the tool re-reviews and confirms the HIGH issue is resolved")
def verify_issue_resolved():
    """Verify re-review confirms resolution."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("the iteration count is logged")
def verify_iteration_logged():
    """Verify iteration count is tracked."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then(
    parsers.parse('it reports "{message}"'),
)
def verify_report_message(message):
    """Verify report message content."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("notes this check improves as debriefs are ingested")
def verify_improvement_note():
    """Verify note about future improvement."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("Phil sees that sign-off is required after 2 iterations")
def verify_forced_signoff():
    """Verify forced sign-off after max iterations."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("unresolved issues are documented in the sign-off record")
def verify_unresolved_documented():
    """Verify unresolved issues in sign-off record."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("the sign-off is recorded with timestamp")
def verify_signoff_recorded():
    """Verify sign-off timestamp recorded."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("the sign-off is written to the review artifacts directory")
def verify_signoff_written():
    """Verify sign-off record artifact."""
    pytest.skip("Awaiting FinalReviewService implementation")


@then("Wave 8 is unlocked")
def verify_wave_8_unlocked():
    """Verify Wave 8 is unlocked after sign-off."""
    pytest.skip("Awaiting FinalReviewService implementation")
