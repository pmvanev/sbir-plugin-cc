"""Step definitions for strategy brief and Wave 1 checkpoint (US-009).

Invokes through: StrategyService (driving port).
Does NOT import brief generators or strategy synthesizers directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.compliance import ComplianceItem, ComplianceMatrix, RequirementType
from pes.domain.strategy import REQUIRED_SECTION_KEYS
from pes.domain.strategy_service import (
    ComplianceMatrixRequiredError,
    StrategyBriefNotFoundError,
    StrategyService,
)
from pes.domain.tpoc_ingestion import AnswerStatus, TpocAnswer, TpocIngestionResult

# Link to feature file
scenarios("../features/strategy_brief.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def strategy_service() -> StrategyService:
    """Wire StrategyService driving port."""
    return StrategyService()


@pytest.fixture()
def strategy_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


@pytest.fixture()
def sample_matrix() -> ComplianceMatrix:
    """Compliance matrix with realistic items."""
    return ComplianceMatrix(
        items=[
            ComplianceItem(
                item_id=i,
                text=f"Requirement {i}: system shall fulfill obligation {i}",
                requirement_type=RequirementType.SHALL,
                proposal_section="Technical Volume",
            )
            for i in range(1, 48)
        ]
    )


@pytest.fixture()
def sample_tpoc_result() -> TpocIngestionResult:
    """TPOC ingestion result with answered questions."""
    return TpocIngestionResult(
        answers=[
            TpocAnswer(
                question_id=1,
                question_text="What does compact mean?",
                answer_text="Less than 50 lbs.",
                status=AnswerStatus.ANSWERED,
            ),
            TpocAnswer(
                question_id=2,
                question_text="What is Phase III target?",
                answer_text="PMS 501 integration.",
                status=AnswerStatus.ANSWERED,
            ),
        ],
    )


# --- Given steps ---


@given(
    parsers.parse(
        'Phil has an active proposal for {topic_id} with Go/No-Go "{decision}"'
    ),
    target_fixture="active_state",
)
def proposal_for_topic_with_decision(
    sample_state, write_state, topic_id, decision
):
    """Set up proposal with a specific topic and Go/No-Go state."""
    state = sample_state.copy()
    state["topic"]["id"] = topic_id
    state["go_no_go"] = decision
    if decision == "go":
        state["current_wave"] = 1
        state["waves"] = {
            "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
            "1": {"status": "active", "completed_at": None},
        }
    write_state(state)
    return state


@given("a compliance matrix exists for AF243-001")
def matrix_for_strategy(
    compliance_matrix_path, state_with_go, write_state, strategy_context, sample_matrix
):
    """Set up compliance matrix for strategy generation."""
    state_with_go["compliance_matrix"]["item_count"] = 47
    state_with_go["compliance_matrix"]["generated_at"] = "2026-03-05T10:00:00Z"
    write_state(state_with_go)
    compliance_matrix_path.write_text("# Compliance Matrix\n\n47 items\n")
    strategy_context["matrix"] = sample_matrix


@given("TPOC answers have been ingested")
def tpoc_answers_ingested(
    state_with_go, write_state, strategy_context, sample_tpoc_result
):
    """Set TPOC status to answers ingested."""
    state_with_go["tpoc"]["status"] = "answers_ingested"
    state_with_go["tpoc"]["answers_ingested_at"] = "2026-03-10T10:00:00Z"
    write_state(state_with_go)
    strategy_context["tpoc_result"] = sample_tpoc_result


@given("the corpus has relevant past proposals")
def corpus_with_relevant():
    """Corpus has proposals relevant to the topic."""
    pass


@given("a strategy brief exists for AF243-001")
def strategy_brief_exists(
    proposal_dir, state_with_go, write_state, strategy_context,
    strategy_service, sample_matrix,
):
    """Create a strategy brief via driving port."""
    state_with_go["strategy_brief"]["status"] = "generated"
    state_with_go["strategy_brief"]["path"] = (
        "./artifacts/wave-1-strategy/strategy-brief.md"
    )
    write_state(state_with_go)
    strategy_context["matrix"] = sample_matrix
    brief = strategy_service.generate_brief(sample_matrix)
    strategy_context["brief"] = brief


@given('TPOC questions are in "pending" state')
def tpoc_pending_for_strategy(state_with_go, write_state):
    """Set TPOC to pending."""
    state_with_go["tpoc"]["status"] = "questions_generated"
    write_state(state_with_go)


@given("no compliance matrix exists")
def no_matrix_for_strategy(compliance_matrix_path, strategy_context):
    """Ensure no compliance matrix."""
    if compliance_matrix_path.exists():
        compliance_matrix_path.unlink()
    strategy_context["matrix"] = None


@given("no strategy brief has been generated")
def no_strategy_brief(state_with_go, write_state, strategy_context):
    """Ensure no strategy brief."""
    state_with_go["strategy_brief"]["status"] = "not_started"
    state_with_go["strategy_brief"]["path"] = None
    write_state(state_with_go)
    strategy_context["brief"] = None


@given("a compliance matrix exists for N244-012")
def matrix_for_n244(compliance_matrix_path, state_with_go, write_state, strategy_context):
    """Set up compliance matrix for different topic."""
    state_with_go["topic"]["id"] = "N244-012"
    state_with_go["compliance_matrix"]["item_count"] = 32
    write_state(state_with_go)
    compliance_matrix_path.write_text("# Compliance Matrix\n\n32 items\n")
    matrix = ComplianceMatrix(
        items=[
            ComplianceItem(
                item_id=i,
                text=f"Requirement {i}",
                requirement_type=RequirementType.SHALL,
            )
            for i in range(1, 33)
        ]
    )
    strategy_context["matrix"] = matrix


# --- When steps ---


@when("the strategy brief is generated")
def generate_strategy(strategy_service, strategy_context):
    """Invoke strategy generation through driving port."""
    matrix = strategy_context.get("matrix")
    tpoc_result = strategy_context.get("tpoc_result")
    brief = strategy_service.generate_brief(matrix, tpoc_result=tpoc_result)
    strategy_context["brief"] = brief


@when("Phil approves the strategy brief")
def approve_strategy(strategy_service, strategy_context):
    """Record strategy approval through driving port."""
    brief = strategy_context.get("brief")
    result = strategy_service.approve_brief(brief)
    strategy_context["approval_result"] = result


@when(
    parsers.parse('Phil provides revision feedback "{feedback}"')
)
def revise_strategy(strategy_service, strategy_context, feedback):
    """Submit revision feedback through driving port."""
    brief = strategy_context.get("brief")
    matrix = strategy_context.get("matrix")
    tpoc_result = strategy_context.get("tpoc_result")
    revised = strategy_service.revise_brief(brief, matrix, feedback, tpoc_result)
    strategy_context["brief"] = revised


@when("Phil attempts to generate the strategy brief")
def attempt_generate_strategy(strategy_service, strategy_context):
    """Attempt strategy generation without prerequisites."""
    try:
        strategy_service.generate_brief(None)  # type: ignore[arg-type]
    except ComplianceMatrixRequiredError as exc:
        strategy_context["error"] = str(exc)
        strategy_context["error_type"] = "compliance_required"


@when("Phil attempts to approve the strategy brief")
def attempt_approve_strategy(strategy_service, strategy_context):
    """Attempt approval of nonexistent brief."""
    try:
        strategy_service.approve_brief(None)
    except StrategyBriefNotFoundError as exc:
        strategy_context["error"] = str(exc)
        strategy_context["error_type"] = "brief_not_found"


# --- Then steps ---


@then(
    "Phil sees the brief covering technical approach, TRL, teaming, "
    "Phase III, budget, and risks"
)
def verify_brief_content(strategy_context):
    """Verify strategy brief covers required topics."""
    brief = strategy_context["brief"]
    assert brief.covers_required_sections
    for key in REQUIRED_SECTION_KEYS:
        section = brief.get_section(key)
        assert section is not None, f"Missing section: {key}"


@then("the brief references TPOC insights where applicable")
def verify_tpoc_references(strategy_context):
    """Verify TPOC insights in brief."""
    brief = strategy_context["brief"]
    assert brief.tpoc_available is True
    all_content = " ".join(s.content for s in brief.sections)
    assert "tpoc" in all_content.lower()


@then("the brief is written to the Wave 1 strategy artifacts")
def verify_brief_location(strategy_context):
    """Verify brief was generated (artifact writing is adapter concern)."""
    brief = strategy_context["brief"]
    assert brief is not None
    assert brief.covers_required_sections


@then("the approval is recorded in the proposal state")
def verify_approval_recorded(strategy_context):
    """Verify strategy approval in state."""
    result = strategy_context["approval_result"]
    assert result["strategy_brief_status"] == "approved"
    assert result["approved_at"] is not None


@then("Wave 2 is unlocked")
def verify_wave_2_unlocked(strategy_context):
    """Verify Wave 2 status changed."""
    result = strategy_context["approval_result"]
    assert result["wave_2_unlocked"] is True


@then("the brief is generated from solicitation and corpus data alone")
def verify_brief_without_tpoc(strategy_context):
    """Verify brief generated without TPOC data."""
    brief = strategy_context["brief"]
    assert brief.covers_required_sections
    assert brief.tpoc_available is False


@then('the brief notes "TPOC insights: not available"')
def verify_tpoc_absent_note(strategy_context):
    """Verify TPOC absence noted in brief."""
    brief = strategy_context["brief"]
    all_content = " ".join(s.content for s in brief.sections)
    assert "tpoc insights: not available" in all_content.lower()


@then("the strategy brief is regenerated incorporating the feedback")
def verify_regeneration(strategy_context):
    """Verify brief regenerated with feedback."""
    brief = strategy_context["brief"]
    assert brief.revision_feedback is not None
    assert len(brief.revision_feedback) > 0


@then("Phil reviews the revised brief")
def verify_revised_review(strategy_context):
    """Verify revised brief presented for review."""
    brief = strategy_context["brief"]
    assert brief.covers_required_sections


@then(parsers.parse('Phil sees "{message}"'))
def verify_strategy_message(strategy_context, message):
    """Verify user-facing strategy message."""
    error = strategy_context.get("error", "")
    assert message.lower() in error.lower(), (
        f"Expected '{message}' in error message, got: '{error}'"
    )


@then("Phil sees guidance to run the strategy wave command first")
def verify_strategy_wave_guidance(strategy_context):
    """Verify guidance to run strategy wave."""
    error = strategy_context.get("error", "")
    assert "compliance matrix" in error.lower() or "strategy" in error.lower()


@then("Phil sees guidance to generate one first")
def verify_generate_brief_guidance(strategy_context):
    """Verify guidance to generate brief."""
    error = strategy_context.get("error", "")
    assert "generate" in error.lower()
