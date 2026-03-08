"""Step definitions for strategy brief and Wave 1 checkpoint (US-009).

Invokes through: StrategyService, CheckpointService (driving ports).
Does NOT import brief generators or strategy synthesizers directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature file
scenarios("../features/strategy_brief.feature")


# --- Given steps ---


@given("a compliance matrix exists for AF243-001")
def matrix_for_strategy(compliance_matrix_path, state_with_go, write_state):
    """Set up compliance matrix for strategy generation."""
    state_with_go["compliance_matrix"]["item_count"] = 47
    state_with_go["compliance_matrix"]["generated_at"] = "2026-03-05T10:00:00Z"
    write_state(state_with_go)
    compliance_matrix_path.write_text("# Compliance Matrix\n\n47 items\n")


@given("TPOC answers have been ingested")
def tpoc_answers_ingested(state_with_go, write_state):
    """Set TPOC status to answers ingested."""
    state_with_go["tpoc"]["status"] = "answers_ingested"
    state_with_go["tpoc"]["answers_ingested_at"] = "2026-03-10T10:00:00Z"
    write_state(state_with_go)


@given("the corpus has relevant past proposals")
def corpus_with_relevant():
    """Corpus has proposals relevant to the topic."""
    pass


@given("a strategy brief exists for AF243-001")
def strategy_brief_exists(proposal_dir, state_with_go, write_state):
    """Create a strategy brief artifact."""
    state_with_go["strategy_brief"]["status"] = "generated"
    state_with_go["strategy_brief"]["path"] = (
        "./artifacts/wave-1-strategy/strategy-brief.md"
    )
    write_state(state_with_go)
    brief_path = proposal_dir / "artifacts" / "wave-1-strategy" / "strategy-brief.md"
    brief_path.write_text(
        "# Strategy Brief -- AF243-001\n\n"
        "## Technical Approach\nSolid-state laser\n\n"
        "## TRL\nEntry: 3, Target: 5\n"
    )


@given('TPOC questions are in "pending" state')
def tpoc_pending_for_strategy(state_with_go, write_state):
    """Set TPOC to pending."""
    state_with_go["tpoc"]["status"] = "questions_generated"
    write_state(state_with_go)


@given("no compliance matrix exists")
def no_matrix_for_strategy(compliance_matrix_path):
    """Ensure no compliance matrix."""
    if compliance_matrix_path.exists():
        compliance_matrix_path.unlink()


@given("no strategy brief has been generated")
def no_strategy_brief(state_with_go, write_state):
    """Ensure no strategy brief."""
    state_with_go["strategy_brief"]["status"] = "not_started"
    state_with_go["strategy_brief"]["path"] = None
    write_state(state_with_go)


@given("a compliance matrix exists for N244-012")
def matrix_for_n244(compliance_matrix_path, state_with_go, write_state):
    """Set up compliance matrix for different topic."""
    state_with_go["topic"]["id"] = "N244-012"
    state_with_go["compliance_matrix"]["item_count"] = 32
    write_state(state_with_go)
    compliance_matrix_path.write_text("# Compliance Matrix\n\n32 items\n")


# --- When steps ---


@when("the strategy brief is generated")
def generate_strategy():
    """Invoke strategy generation through driving port."""
    # TODO: Invoke through StrategyService
    pytest.skip("Awaiting StrategyService implementation")


@when("Phil approves the strategy brief")
def approve_strategy():
    """Record strategy approval through driving port."""
    # TODO: Invoke through CheckpointService
    pytest.skip("Awaiting CheckpointService implementation")


@when(
    parsers.parse('Phil provides revision feedback "{feedback}"')
)
def revise_strategy(feedback):
    """Submit revision feedback through driving port."""
    # TODO: Invoke through StrategyService
    pytest.skip("Awaiting StrategyService implementation")


@when("Phil attempts to generate the strategy brief")
def attempt_generate_strategy():
    """Attempt strategy generation without prerequisites."""
    # TODO: Invoke through StrategyService
    pytest.skip("Awaiting StrategyService implementation")


@when("Phil attempts to approve the strategy brief")
def attempt_approve_strategy():
    """Attempt approval of nonexistent brief."""
    # TODO: Invoke through CheckpointService
    pytest.skip("Awaiting CheckpointService implementation")


# --- Then steps ---


@then(
    "Phil sees the brief covering technical approach, TRL, teaming, "
    "Phase III, budget, and risks"
)
def verify_brief_content():
    """Verify strategy brief covers required topics."""
    pass


@then("the brief references TPOC insights where applicable")
def verify_tpoc_references():
    """Verify TPOC insights in brief."""
    pass


@then("the brief is written to the Wave 1 strategy artifacts")
def verify_brief_location():
    """Verify brief file location."""
    pass


@then("the approval is recorded in the proposal state")
def verify_approval_recorded():
    """Verify strategy approval in state."""
    pass


@then("Wave 2 is unlocked")
def verify_wave_2_unlocked():
    """Verify Wave 2 status changed."""
    pass


@then("the brief is generated from solicitation and corpus data alone")
def verify_brief_without_tpoc():
    """Verify brief generated without TPOC data."""
    pass


@then('the brief notes "TPOC insights: not available"')
def verify_tpoc_absent_note():
    """Verify TPOC absence noted in brief."""
    pass


@then("the strategy brief is regenerated incorporating the feedback")
def verify_regeneration():
    """Verify brief regenerated with feedback."""
    pass


@then("Phil reviews the revised brief")
def verify_revised_review():
    """Verify revised brief presented for review."""
    pass


@then(parsers.parse('Phil sees "{message}"'))
def verify_strategy_message(message):
    """Verify user-facing strategy message."""
    pass


@then("Phil sees guidance to run the strategy wave command first")
def verify_strategy_wave_guidance():
    """Verify guidance to run strategy wave."""
    pass


@then("Phil sees guidance to generate one first")
def verify_generate_brief_guidance():
    """Verify guidance to generate brief."""
    pass
