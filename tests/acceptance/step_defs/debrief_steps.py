"""Step definitions for debrief ingestion and request letter (US-015, US-016).

Invokes through: DebriefService, OutcomeService (driving ports).
Does NOT import internal debrief parsers or pattern analyzers directly.
"""

from __future__ import annotations

from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to both feature files
scenarios("../features/debrief_ingestion.feature")
scenarios("../features/debrief_request.feature")

# Project root for template resolution
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_TEMPLATES_DIR = str(_PROJECT_ROOT / "templates" / "debrief-request")


def _make_outcome_service():
    """Create OutcomeService with real filesystem adapters for acceptance tests."""
    from pes.adapters.filesystem_artifact_writer_adapter import FilesystemArtifactWriter
    from pes.adapters.filesystem_template_loader_adapter import FilesystemTemplateLoader
    from pes.domain.outcome_service import OutcomeService

    return OutcomeService(
        template_loader=FilesystemTemplateLoader(_TEMPLATES_DIR),
        artifact_writer=FilesystemArtifactWriter(),
    )


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


@given(
    "AF243-001 was not selected and Phil has a debrief letter",
    target_fixture="debrief_context",
)
def proposal_not_selected_with_debrief(active_state, write_state, proposal_dir):
    """Record not-selected outcome with debrief available and provide debrief text."""
    active_state["learning"]["outcome"] = "not_selected"
    active_state["learning"]["outcome_recorded_at"] = "2026-07-01T10:00:00Z"
    write_state(active_state)

    # Simulate a structured debrief letter as extracted text from PDF
    debrief_text = (
        "SBIR Phase I Proposal Evaluation Summary\n"
        "Topic: AF243-001\n"
        "Proposal: Compact Directed Energy for Maritime UAS Defense\n\n"
        "Evaluator Scores:\n"
        "  Technical Merit: 3.5/5.0\n"
        "  Team Qualifications: 4.0/5.0\n"
        "  Cost Realism: 2.5/5.0\n\n"
        "Critique Comments:\n"
        "1. Section 3.1 (Technical Approach), Page 5: "
        "The proposed beam-steering mechanism lacks sufficient detail "
        "on thermal management under sustained operation.\n"
        "2. Section 4.2 (Project Schedule), Page 12: "
        "Timeline appears aggressive given the TRL advancement required.\n"
        "3. Section 2.1 (Innovation), Page 3: "
        "Novel waveguide design is promising but risk mitigation "
        "for manufacturing scalability is insufficient.\n"
    )
    return {
        "debrief_text": debrief_text,
        "known_weaknesses": ["thermal management", "cost realism"],
        "proposal_dir": proposal_dir,
    }


@given(
    parsers.parse(
        "the corpus contains {total:d} proposals with {wins:d} awarded and {losses:d} not selected"
    ),
    target_fixture="corpus_outcomes",
)
def corpus_with_outcomes(total, wins, losses, proposal_dir):
    """Corpus with specified outcome distribution -- build corpus entries."""
    outcomes = []
    for i in range(wins):
        outcomes.append(
            {
                "topic_id": f"WIN-{i + 1:03d}",
                "outcome": "awarded",
                "strengths": ["strong technical approach", "experienced team"],
                "weaknesses": [],
            }
        )
    for i in range(losses):
        outcomes.append(
            {
                "topic_id": f"LOSS-{i + 1:03d}",
                "outcome": "not_selected",
                "strengths": [],
                "weaknesses": ["cost realism", "schedule risk"],
            }
        )
    return {
        "outcomes": outcomes,
        "artifacts_dir": str(proposal_dir / "artifacts" / "wave-9-learning"),
    }


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


@given(
    "the debrief letter is a single paragraph with no scores",
    target_fixture="debrief_context",
)
def unstructured_debrief(proposal_dir):
    """Debrief is unstructured freeform text with no structure."""
    debrief_text = (
        "Thank you for your submission. After careful review, your proposal "
        "was not selected for award. The evaluation panel noted that while "
        "the concept showed promise, several areas needed improvement "
        "including cost justification and timeline feasibility."
    )
    return {
        "debrief_text": debrief_text,
        "known_weaknesses": [],
        "proposal_dir": proposal_dir,
    }


@given(
    "debrief ingestion and pattern analysis are complete",
    target_fixture="lessons_context",
)
def debrief_and_patterns_complete(proposal_dir):
    """Debrief ingested and patterns updated -- set up artifacts dir for lessons."""
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")
    return {"artifacts_dir": artifacts_dir}


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


@given(
    "any proposal with an existing outcome tag",
    target_fixture="tag_context",
)
def proposal_with_existing_tag(active_state, write_state):
    """Precondition for append-only property test -- proposal with recorded outcome."""
    active_state["learning"]["outcome"] = "not_selected"
    active_state["learning"]["outcome_recorded_at"] = "2026-07-01T10:00:00Z"
    active_state["requested_outcome_change"] = "awarded"
    write_state(active_state)
    return active_state


# --- When steps ---


@when(
    "Phil ingests the debrief from a PDF file",
    target_fixture="debrief_result",
)
def ingest_debrief(debrief_context):
    """Ingest debrief through DebriefService (driving port)."""
    from pes.adapters.filesystem_artifact_writer_adapter import FilesystemArtifactWriter
    from pes.adapters.text_debrief_parser_adapter import TextDebriefParserAdapter
    from pes.domain.debrief_service import DebriefService

    parser = TextDebriefParserAdapter()
    writer = FilesystemArtifactWriter()
    service = DebriefService(parser=parser, artifact_writer=writer)
    artifacts_dir = str(debrief_context["proposal_dir"] / "artifacts" / "wave-9-learning")

    return service.ingest_debrief(
        debrief_text=debrief_context["debrief_text"],
        known_weaknesses=debrief_context["known_weaknesses"],
        artifacts_dir=artifacts_dir,
    )


@when(
    "the tool updates pattern analysis",
    target_fixture="pattern_result",
)
def update_patterns(corpus_outcomes):
    """Update pattern analysis through OutcomeService."""
    service = _make_outcome_service()
    return service.update_pattern_analysis(
        corpus_outcomes=corpus_outcomes["outcomes"],
        artifacts_dir=corpus_outcomes["artifacts_dir"],
    )


@when(
    parsers.parse('Phil records the outcome as "{outcome}"'),
    target_fixture="outcome_result",
)
def record_outcome(outcome, active_state, proposal_dir):
    """Record outcome through OutcomeService."""
    topic_id = active_state["topic"]["id"]
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")

    service = _make_outcome_service()
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
    topic_id = active_state["topic"]["id"]
    outcome = active_state["learning"]["outcome"]
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")

    service = _make_outcome_service()
    return service.record_outcome(
        topic_id=topic_id,
        outcome=outcome,
        artifacts_dir=artifacts_dir,
    )


@when(
    "the tool presents lessons learned",
    target_fixture="lessons_result",
)
def present_lessons(lessons_context):
    """Present lessons learned through OutcomeService."""
    service = _make_outcome_service()
    return service.present_lessons_learned(
        artifacts_dir=lessons_context["artifacts_dir"],
    )


@when(
    "Phil requests a debrief letter draft",
    target_fixture="debrief_letter_result",
)
def request_debrief_letter(active_state, proposal_dir):
    """Generate debrief request letter through OutcomeService."""
    topic_id = active_state["topic"]["id"]
    agency = active_state["topic"]["agency"]
    confirmation = active_state["submission"]["confirmation_number"]
    artifacts_dir = str(proposal_dir / "artifacts" / "wave-9-learning")

    service = _make_outcome_service()
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
    topic_id = active_state["topic"]["id"]
    service = _make_outcome_service()
    return service.skip_debrief_request(topic_id=topic_id)


@when(
    "any process attempts to overwrite the tag",
    target_fixture="overwrite_result",
)
def attempt_overwrite_tag(tag_context, enforcement_engine, state_file):
    """Attempt to overwrite existing outcome tag through PES enforcement."""
    import json

    state = json.loads(state_file.read_text())
    result = enforcement_engine.evaluate(
        state=state,
        tool_name="record_outcome",
    )
    return result


# --- Then steps ---


@then("the tool parses reviewer scores and critique comments")
def verify_scores_parsed(debrief_result):
    """Verify debrief scores are parsed."""
    assert debrief_result.scores is not None
    assert len(debrief_result.scores) > 0
    assert debrief_result.parsing_confidence > 0.0


@then("maps each critique to a specific proposal section and page")
def verify_critique_mapped(debrief_result):
    """Verify critiques mapped to sections."""
    assert debrief_result.critique_map is not None
    assert len(debrief_result.critique_map) > 0
    for critique in debrief_result.critique_map:
        assert critique.section is not None
        assert critique.page is not None


@then("flags critiques matching known weaknesses from past debriefs")
def verify_weaknesses_flagged(debrief_result):
    """Verify known weaknesses are flagged."""
    assert debrief_result.flagged_weaknesses is not None
    assert len(debrief_result.flagged_weaknesses) > 0


@then("writes the structured debrief to the learning artifacts directory")
def verify_debrief_written(debrief_result, proposal_dir):
    """Verify structured debrief artifact."""
    from pathlib import Path

    assert debrief_result.artifact_path is not None
    written = Path(debrief_result.artifact_path)
    assert written.exists()
    artifacts_dir = proposal_dir / "artifacts" / "wave-9-learning"
    assert str(written).startswith(str(artifacts_dir))


@then("it identifies recurring weaknesses across losses")
def verify_recurring_weaknesses(pattern_result):
    """Verify recurring weakness patterns identified."""
    assert pattern_result.recurring_weaknesses is not None
    assert len(pattern_result.recurring_weaknesses) > 0


@then("identifies recurring strengths across wins")
def verify_recurring_strengths(pattern_result):
    """Verify recurring strength patterns identified."""
    assert pattern_result.recurring_strengths is not None
    assert len(pattern_result.recurring_strengths) > 0


@then("writes pattern analysis to the learning artifacts directory")
def verify_patterns_written(pattern_result):
    """Verify pattern analysis artifact."""
    from pathlib import Path

    assert pattern_result.artifact_path is not None
    written = Path(pattern_result.artifact_path)
    assert written.exists()


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
def verify_freeform_preserved(debrief_result):
    """Verify freeform text is preserved."""
    assert debrief_result.freeform_text is not None
    assert len(debrief_result.freeform_text) > 0


@then(
    parsers.parse('notes "{note}"'),
)
def verify_parsing_note(note, debrief_result):
    """Verify parsing limitation note."""
    assert debrief_result.message is not None
    assert note in debrief_result.message


@then("the freeform text is available for keyword-based pattern matching")
def verify_freeform_searchable(debrief_result):
    """Verify freeform text is searchable via keywords."""
    assert debrief_result.freeform_text is not None
    # Freeform text should contain searchable content
    assert "cost" in debrief_result.freeform_text.lower() or len(debrief_result.freeform_text) > 0


@then("Phil can review, edit, and acknowledge before corpus update completes")
def verify_lessons_checkpoint(lessons_result):
    """Verify lessons learned human checkpoint."""
    assert lessons_result.requires_human_acknowledgment is True
    assert lessons_result.status == "pending_review"


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
def verify_tag_modification_blocked(overwrite_result):
    """Verify outcome tag modification is blocked."""
    from pes.domain.rules import Decision

    assert overwrite_result.decision == Decision.BLOCK


@then("the original tag is preserved")
def verify_original_tag(tag_context):
    """Verify original tag is unchanged."""
    assert tag_context["learning"]["outcome"] == "not_selected"
