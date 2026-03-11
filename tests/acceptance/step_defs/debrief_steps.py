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
    target_fixture="confirmation_number",
)
def submission_confirmation(confirmation):
    """Submission confirmation number."""
    return confirmation


@given(
    "N244-012 was submitted to NSPIRES and not selected",
    target_fixture="active_state",
)
def nasa_not_selected(active_state, write_state):
    """NASA submission not selected -- update state to NASA agency and topic."""
    active_state["topic"]["id"] = "N244-012"
    active_state["topic"]["agency"] = "NASA"
    active_state["learning"]["outcome"] = "not_selected"
    active_state["learning"]["outcome_recorded_at"] = "2026-07-01T10:00:00Z"
    active_state["submission"]["confirmation_number"] = "NSPIRES-2026-N244-012"
    write_state(active_state)
    return active_state


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
    target_fixture="outcome_result",
)
def record_outcome(outcome, active_state, proposal_dir):
    """Record outcome through OutcomeService."""
    from pes.domain.outcome_service import OutcomeService

    topic_id = active_state["topic"]["id"]
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")

    service = OutcomeService()
    return service.record_outcome(
        topic_id=topic_id,
        outcome=outcome,
        artifacts_dir=artifacts_dir,
    )


@when(
    "Phil records the outcome",
    target_fixture="outcome_result",
)
def record_outcome_no_debrief(active_state, proposal_dir):
    """Record outcome without debrief through OutcomeService."""
    from pes.domain.outcome_service import OutcomeService

    topic_id = active_state["topic"]["id"]
    outcome = active_state["learning"]["outcome"]
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")

    service = OutcomeService()
    return service.record_outcome(
        topic_id=topic_id,
        outcome=outcome,
        artifacts_dir=artifacts_dir,
    )


@when("the tool presents lessons learned")
def present_lessons():
    """Present lessons learned through OutcomeService."""
    pytest.skip("Awaiting OutcomeService implementation")


@when(
    "Phil requests a debrief letter draft",
    target_fixture="debrief_letter_result",
)
def request_debrief_letter(active_state, proposal_dir):
    """Generate debrief request letter through OutcomeService."""
    from pes.domain.outcome_service import OutcomeService

    topic_id = active_state["topic"]["id"]
    agency = active_state["topic"]["agency"]
    confirmation = active_state["submission"]["confirmation_number"]
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")

    service = OutcomeService()
    return service.generate_debrief_letter(
        topic_id=topic_id,
        agency=agency,
        confirmation_number=confirmation,
        artifacts_dir=artifacts_dir,
    )


@when(
    "Phil decides not to request a debrief",
    target_fixture="skip_debrief_result",
)
def skip_debrief_request(active_state):
    """Skip debrief request through OutcomeService."""
    from pes.domain.outcome_service import OutcomeService

    topic_id = active_state["topic"]["id"]
    service = OutcomeService()
    return service.skip_debrief_request(topic_id=topic_id)


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
def verify_winner_archived(outcome_result):
    """Verify winning proposal is archived with outcome tag."""
    assert outcome_result.outcome_tag == "awarded"
    assert outcome_result.archived is True


@then("winning discriminators are extracted for pattern analysis")
def verify_discriminators_extracted(outcome_result):
    """Verify winning discriminators extracted."""
    assert outcome_result.discriminators is not None
    assert len(outcome_result.discriminators) >= 0  # may be empty list but must exist


@then("the tool suggests Phase II pre-planning")
def verify_phase_ii_suggestion(outcome_result):
    """Verify Phase II suggestion for awarded proposals."""
    assert "Phase II" in outcome_result.message


@then("the outcome tag is appended to the proposal state")
def verify_outcome_appended(outcome_result):
    """Verify outcome tag appended to state."""
    assert outcome_result.outcome_tag is not None
    assert outcome_result.outcome_tag in ("awarded", "not_selected")


@then("no debrief artifacts are created")
def verify_no_debrief_artifacts(outcome_result):
    """Verify no debrief artifacts when no debrief."""
    assert outcome_result.debrief_artifacts_created is False


@then(
    parsers.parse('the tool notes "{note}"'),
)
def verify_tool_note(note, outcome_result):
    """Verify tool note message."""
    assert note in outcome_result.message


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
def verify_letter_references(topic, debrief_letter_result):
    """Verify letter references topic and confirmation."""
    assert topic in debrief_letter_result.content
    assert debrief_letter_result.confirmation_number in debrief_letter_result.content


@then(
    parsers.parse("the letter cites {regulation}"),
)
def verify_regulation_cited(regulation, debrief_letter_result):
    """Verify regulation is cited in letter."""
    assert regulation in debrief_letter_result.content


@then("the draft is written to the learning artifacts directory")
def verify_draft_written(debrief_letter_result, proposal_dir):
    """Verify debrief request draft artifact."""
    from pathlib import Path

    written_path = Path(debrief_letter_result.file_path)
    assert written_path.exists()
    artifacts_dir = proposal_dir / "artifacts" / "wave-9-learning"
    assert str(written_path).startswith(str(artifacts_dir))


@then("the tool generates a letter using NASA-specific debrief procedures")
def verify_nasa_letter(debrief_letter_result):
    """Verify NASA-specific letter generated."""
    assert "NASA" in debrief_letter_result.content
    assert "FAR 15.505" not in debrief_letter_result.content


@then(
    parsers.parse('the tool records "{status}"'),
)
def verify_status_recorded(status, skip_debrief_result):
    """Verify status recorded."""
    assert skip_debrief_result.status == status


@then("proceeds to outcome recording without creating a request letter")
def verify_no_letter_created(skip_debrief_result):
    """Verify no letter when debrief skipped."""
    assert skip_debrief_result.letter_created is False


@then("the modification is blocked")
def verify_tag_modification_blocked():
    """Verify outcome tag modification is blocked."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")


@then("the original tag is preserved")
def verify_original_tag():
    """Verify original tag is unchanged."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")
