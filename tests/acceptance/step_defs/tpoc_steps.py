"""Step definitions for TPOC questions and answer ingestion (US-005).

Invokes through: TpocService (driving port).
Does NOT import question generators or answer matchers directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature file
scenarios("../features/tpoc_questions.feature")


# --- Given steps ---


@given(parsers.parse("a compliance matrix exists with {count:d} flagged ambiguities"))
def matrix_with_ambiguities(count, compliance_matrix_path, state_with_go, write_state):
    """Create compliance matrix with flagged ambiguities."""
    state_with_go["compliance_matrix"]["item_count"] = 47
    state_with_go["compliance_matrix"]["generated_at"] = "2026-03-05T10:00:00Z"
    write_state(state_with_go)
    lines = ["# Compliance Matrix\n"]
    for i in range(count):
        lines.append(f"| {i + 1} | AMBIGUOUS: Requirement {i + 1} | ? | -- |\n")
    compliance_matrix_path.write_text("".join(lines))


@given("TPOC questions were generated for AF243-001")
def tpoc_questions_exist(state_with_go, write_state, proposal_dir):
    """Set up state with generated TPOC questions."""
    state_with_go["tpoc"]["status"] = "questions_generated"
    state_with_go["tpoc"]["questions_generated_at"] = "2026-03-03T10:00:00Z"
    state_with_go["tpoc"]["questions_path"] = (
        "./artifacts/wave-1-strategy/tpoc-questions.md"
    )
    write_state(state_with_go)
    questions_file = proposal_dir / "artifacts" / "wave-1-strategy" / "tpoc-questions.md"
    questions_file.write_text("# TPOC Questions\n\n1. Question one?\n2. Question two?\n")


@given("Phil has a notes file from the TPOC call")
def tpoc_notes_file(tmp_path):
    """Create TPOC call notes file."""
    notes_path = tmp_path / "notes" / "tpoc-call-2026-03-15.txt"
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text(
        "TPOC Call Notes\n\n"
        "Q1 Answer: Compact means less than 50 lbs.\n"
        "Q2 Answer: Phase III target is PMS 501.\n"
    )
    return notes_path


@given(parsers.parse("TPOC questions were generated {days:d} days ago"))
def tpoc_questions_aged(state_with_go, write_state, days):
    """Set up TPOC questions generated N days ago."""
    from datetime import datetime, timedelta

    generated = datetime.now() - timedelta(days=days)
    state_with_go["tpoc"]["status"] = "questions_generated"
    state_with_go["tpoc"]["questions_generated_at"] = generated.isoformat()
    write_state(state_with_go)


@given("no answers have been ingested")
def no_answers():
    """Ensure no TPOC answers in state."""
    pass


@given(parsers.parse("{count:d} TPOC questions were generated"))
def tpoc_question_count(count, state_with_go, write_state, proposal_dir):
    """Generate specific number of TPOC questions."""
    state_with_go["tpoc"]["status"] = "questions_generated"
    write_state(state_with_go)
    lines = ["# TPOC Questions\n\n"]
    for i in range(count):
        lines.append(f"{i + 1}. Question {i + 1}?\n")
    questions_file = proposal_dir / "artifacts" / "wave-1-strategy" / "tpoc-questions.md"
    questions_file.write_text("".join(lines))


@given(parsers.parse("Phil's notes cover only {count:d} questions"))
def partial_notes(count, tmp_path):
    """Create notes covering only some questions."""
    notes_path = tmp_path / "notes" / "partial-notes.txt"
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["TPOC Call Notes (partial)\n\n"]
    for i in range(count):
        lines.append(f"Q{i + 1} Answer: Answer for question {i + 1}.\n")
    notes_path.write_text("".join(lines))
    return notes_path


@given("no compliance matrix exists")
def no_matrix_for_tpoc(compliance_matrix_path):
    """Ensure no compliance matrix."""
    if compliance_matrix_path.exists():
        compliance_matrix_path.unlink()


@given("TPOC questions were generated")
def questions_generated(state_with_go, write_state):
    """Set TPOC status to questions_generated."""
    state_with_go["tpoc"]["status"] = "questions_generated"
    write_state(state_with_go)


# --- When steps ---


@when("Phil generates TPOC questions")
def generate_tpoc_questions():
    """Invoke TPOC question generation through driving port."""
    # TODO: Invoke through TpocService
    pytest.skip("Awaiting TpocService implementation")


@when("Phil ingests the TPOC call notes")
def ingest_tpoc_notes():
    """Invoke TPOC answer ingestion through driving port."""
    # TODO: Invoke through TpocService
    pytest.skip("Awaiting TpocService implementation")


@when("Phil checks proposal status")
def check_tpoc_status():
    """Check status to verify TPOC pending state."""
    # TODO: Invoke through StatusService
    pytest.skip("Awaiting StatusService implementation")


@when("Phil ingests the partial notes")
def ingest_partial_notes():
    """Invoke partial TPOC ingestion."""
    # TODO: Invoke through TpocService
    pytest.skip("Awaiting TpocService implementation")


@when("Phil attempts to generate TPOC questions")
def attempt_generate_questions():
    """Attempt question generation without matrix."""
    # TODO: Invoke through TpocService
    pytest.skip("Awaiting TpocService implementation")


@when("Phil attempts to ingest notes from a non-existent file path")
def attempt_ingest_bad_path():
    """Attempt ingestion with invalid file path."""
    # TODO: Invoke through TpocService
    pytest.skip("Awaiting TpocService implementation")


# --- Then steps ---


@then("questions are generated tagged by category")
def verify_questions_categorized():
    """Verify questions have category tags."""
    pass


@then("questions are ordered by strategic priority")
def verify_priority_order():
    """Verify question priority ordering."""
    pass


@then("questions are written to the Wave 1 strategy artifacts")
def verify_questions_written():
    """Verify questions file location."""
    pass


@then('the TPOC status changes to "questions generated"')
def verify_tpoc_generated_status():
    """Verify TPOC status update."""
    pass


@then("answers are matched to original questions")
def verify_answers_matched():
    """Verify answer matching."""
    pass


@then("unanswered questions are marked")
def verify_unanswered_marked():
    """Verify unanswered marking."""
    pass


@then("a solicitation delta analysis is generated")
def verify_delta_analysis():
    """Verify delta analysis created."""
    pass


@then("the compliance matrix is updated with TPOC clarifications")
def verify_matrix_updated():
    """Verify matrix updates from TPOC."""
    pass


@then('the TPOC status changes to "answers ingested"')
def verify_tpoc_ingested_status():
    """Verify TPOC status update to ingested."""
    pass


@then(parsers.parse('Phil sees "{message}"'))
def verify_tpoc_message(message):
    """Verify user-facing TPOC message."""
    pass


@then("no wave is blocked by the pending TPOC state")
def verify_no_block():
    """Verify pending TPOC does not block waves."""
    pass


@then(parsers.parse("{count:d} answers are matched"))
def verify_match_count(count):
    """Verify matched answer count."""
    pass


@then(parsers.parse("{count:d} questions are marked as unanswered"))
def verify_unanswered_count(count):
    """Verify unanswered question count."""
    pass


@then(parsers.parse("delta analysis is generated from the {count:d} answered questions"))
def verify_partial_delta(count):
    """Verify delta from partial answers."""
    pass


@then("Phil sees guidance to run the strategy wave command first")
def verify_wave_guidance():
    """Verify strategy wave guidance."""
    pass


@then("Phil sees guidance to verify the file path")
def verify_path_guidance_tpoc():
    """Verify file path guidance."""
    pass
