"""Step definitions for debrief ingestion and request letter (US-015, US-016).

Invokes through: DebriefService, OutcomeService (driving ports).
Does NOT import internal debrief parsers or pattern analyzers directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to both feature files
scenarios("../features/debrief_ingestion.feature")
scenarios("../features/debrief_request.feature")


# --- Given steps ---


@given(
    "Phil has a submitted proposal for AF243-001",
    target_fixture="active_state",
)
def submitted_proposal_af243(sample_state, write_state):
    """Set up a submitted proposal ready for Wave 9."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 9
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "completed", "completed_at": "2026-03-09T10:00:00Z"},
        "6": {"status": "completed", "completed_at": "2026-03-10T10:00:00Z"},
        "7": {"status": "completed", "completed_at": "2026-03-11T10:00:00Z"},
        "8": {"status": "completed", "completed_at": "2026-04-07T14:23:17Z"},
        "9": {"status": "active", "completed_at": None},
    }
    state["submission"] = {
        "status": "submitted",
        "portal": "DSIP",
        "confirmation_number": "DSIP-2026-AF243-001-7842",
        "submitted_at": "2026-04-07T14:23:17Z",
        "archive_path": "./artifacts/wave-8-submission/archive/",
        "immutable": True,
    }
    state["learning"] = {
        "outcome": None,
        "outcome_recorded_at": None,
        "debrief_requested": None,
        "debrief_ingested": False,
    }
    write_state(state)
    return state


@given("AF243-001 was not selected and Phil has a debrief letter")
def proposal_not_selected_with_debrief(active_state, write_state):
    """Record not-selected outcome with debrief available."""
    active_state["learning"]["outcome"] = "not_selected"
    active_state["learning"]["outcome_recorded_at"] = "2026-07-01T10:00:00Z"
    write_state(active_state)


@given(
    parsers.parse(
        "the corpus contains {total:d} proposals with {wins:d} awarded and {losses:d} not selected"
    ),
)
def corpus_with_outcomes(total, wins, losses):
    """Corpus with specified outcome distribution."""
    pass


@given("AF243-001 was awarded")
def proposal_awarded(active_state, write_state):
    """Record awarded outcome."""
    active_state["learning"]["outcome"] = "awarded"
    active_state["learning"]["outcome_recorded_at"] = "2026-07-01T10:00:00Z"
    write_state(active_state)


@given("AF243-001 was not selected")
def proposal_not_selected(active_state, write_state):
    """Record not-selected outcome."""
    active_state["learning"]["outcome"] = "not_selected"
    active_state["learning"]["outcome_recorded_at"] = "2026-07-01T10:00:00Z"
    write_state(active_state)


@given("no debrief letter is available")
def no_debrief_available():
    """No debrief letter from agency."""
    pass


@given("the debrief letter is a single paragraph with no scores")
def unstructured_debrief():
    """Debrief is unstructured freeform text."""
    pass


@given("debrief ingestion and pattern analysis are complete")
def debrief_and_patterns_complete():
    """Debrief ingested and patterns updated."""
    pass


@given(
    parsers.parse('the submission confirmation is "{confirmation}"'),
)
def submission_confirmation(confirmation):
    """Submission confirmation number."""
    pass


@given("N244-012 was submitted to NSPIRES and not selected")
def nasa_not_selected():
    """NASA submission not selected."""
    pass


@given("any proposal with an existing outcome tag")
def proposal_with_existing_tag():
    """Precondition for append-only property test."""
    pass


# --- When steps ---


@when("Phil ingests the debrief from a PDF file")
def ingest_debrief():
    """Ingest debrief through DebriefService."""
    pytest.skip("Awaiting DebriefService implementation")


@when("the tool updates pattern analysis")
def update_patterns():
    """Update pattern analysis through OutcomeService."""
    pytest.skip("Awaiting OutcomeService implementation")


@when(
    parsers.parse('Phil records the outcome as "{outcome}"'),
)
def record_outcome(outcome):
    """Record outcome through OutcomeService."""
    pytest.skip("Awaiting OutcomeService implementation")


@when("Phil records the outcome")
def record_outcome_no_debrief():
    """Record outcome without debrief."""
    pytest.skip("Awaiting OutcomeService implementation")


@when("the tool presents lessons learned")
def present_lessons():
    """Present lessons learned through OutcomeService."""
    pytest.skip("Awaiting OutcomeService implementation")


@when("Phil requests a debrief letter draft")
def request_debrief_letter():
    """Generate debrief request letter through OutcomeService."""
    pytest.skip("Awaiting OutcomeService implementation")


@when("Phil decides not to request a debrief")
def skip_debrief_request():
    """Skip debrief request through OutcomeService."""
    pytest.skip("Awaiting OutcomeService implementation")


@when("any process attempts to overwrite the tag")
def attempt_overwrite_tag():
    """Attempt to overwrite existing outcome tag."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")


# --- Then steps ---


@then("the tool parses reviewer scores and critique comments")
def verify_scores_parsed():
    """Verify debrief scores are parsed."""
    pytest.skip("Awaiting DebriefService implementation")


@then("maps each critique to a specific proposal section and page")
def verify_critique_mapped():
    """Verify critiques mapped to sections."""
    pytest.skip("Awaiting DebriefService implementation")


@then("flags critiques matching known weaknesses from past debriefs")
def verify_weaknesses_flagged():
    """Verify known weaknesses are flagged."""
    pytest.skip("Awaiting DebriefService implementation")


@then("writes the structured debrief to the learning artifacts directory")
def verify_debrief_written():
    """Verify structured debrief artifact."""
    pytest.skip("Awaiting DebriefService implementation")


@then("it identifies recurring weaknesses across losses")
def verify_recurring_weaknesses():
    """Verify recurring weakness patterns identified."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("identifies recurring strengths across wins")
def verify_recurring_strengths():
    """Verify recurring strength patterns identified."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("writes pattern analysis to the learning artifacts directory")
def verify_patterns_written():
    """Verify pattern analysis artifact."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the winning proposal is archived with outcome tag")
def verify_winner_archived():
    """Verify winning proposal is archived."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("winning discriminators are extracted for pattern analysis")
def verify_discriminators_extracted():
    """Verify winning discriminators extracted."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the tool suggests Phase II pre-planning")
def verify_phase_ii_suggestion():
    """Verify Phase II suggestion."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the outcome tag is appended to the proposal state")
def verify_outcome_appended():
    """Verify outcome tag appended to state."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("no debrief artifacts are created")
def verify_no_debrief_artifacts():
    """Verify no debrief artifacts when no debrief."""
    pytest.skip("Awaiting OutcomeService implementation")


@then(
    parsers.parse('the tool notes "{note}"'),
)
def verify_tool_note(note):
    """Verify tool note message."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the tool preserves the full text as freeform feedback")
def verify_freeform_preserved():
    """Verify freeform text is preserved."""
    pytest.skip("Awaiting DebriefService implementation")


@then(
    parsers.parse('notes "{note}"'),
)
def verify_parsing_note(note):
    """Verify parsing limitation note."""
    pytest.skip("Awaiting DebriefService implementation")


@then("the freeform text is available for keyword-based pattern matching")
def verify_freeform_searchable():
    """Verify freeform text is searchable."""
    pytest.skip("Awaiting DebriefService implementation")


@then("Phil can review, edit, and acknowledge before corpus update completes")
def verify_lessons_checkpoint():
    """Verify lessons learned human checkpoint."""
    pytest.skip("Awaiting OutcomeService implementation")


@then(
    parsers.parse("the tool generates a letter referencing {topic} and the confirmation number"),
)
def verify_letter_references(topic):
    """Verify letter references topic and confirmation."""
    pytest.skip("Awaiting OutcomeService implementation")


@then(
    parsers.parse("the letter cites {regulation}"),
)
def verify_regulation_cited(regulation):
    """Verify regulation is cited in letter."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the draft is written to the learning artifacts directory")
def verify_draft_written():
    """Verify debrief request draft artifact."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the tool generates a letter using NASA-specific debrief procedures")
def verify_nasa_letter():
    """Verify NASA-specific letter generated."""
    pytest.skip("Awaiting OutcomeService implementation")


@then(
    parsers.parse('the tool records "{status}"'),
)
def verify_status_recorded(status):
    """Verify status recorded."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("proceeds to outcome recording without creating a request letter")
def verify_no_letter_created():
    """Verify no letter when debrief skipped."""
    pytest.skip("Awaiting OutcomeService implementation")


@then("the modification is blocked")
def verify_tag_modification_blocked():
    """Verify outcome tag modification is blocked."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")


@then("the original tag is preserved")
def verify_original_tag():
    """Verify original tag is unchanged."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")
