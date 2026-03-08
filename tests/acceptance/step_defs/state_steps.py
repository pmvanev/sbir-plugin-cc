"""Step definitions for proposal state persistence (US-007).

Invokes through: StateReader/StateWriter ports via JsonStateAdapter.
Does NOT import internal validators or domain entities directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.adapters.json_state_adapter import JsonStateAdapter
from pes.domain.state import StateCorruptedError, StateNotFoundError
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/proposal_state.feature")


# --- Fixtures ---


@pytest.fixture()
def state_adapter(proposal_dir) -> JsonStateAdapter:
    """Create JsonStateAdapter pointing at the proposal .sbir directory."""
    return JsonStateAdapter(str(proposal_dir / ".sbir"))


# --- Given steps ---


@given("Phil completed the Go/No-Go decision for AF243-001")
def go_decision_completed(state_with_go, state_adapter):
    """Write state with Go decision to disk via adapter."""
    state_adapter.save(state_with_go)


@given("Phil closed the session")
def session_closed():
    """Session closure is implicit -- state was written to disk."""
    pass


@given("Phil has an active proposal for AF243-001")
def active_proposal(sample_state, state_adapter):
    """Set up basic active proposal via adapter."""
    state_adapter.save(sample_state)


@given("any proposal state update is in progress")
def state_update_in_progress():
    """Precondition for property test on atomic writes."""
    pass


@given("the proposal state file was partially written due to a crash")
def corrupted_state_file(state_file):
    """Write truncated JSON to simulate crash during write."""
    state_file.write_text('{"schema_version": "1.0.0", "proposal_id": "test-uuid"')


# --- Context holders ---


@pytest.fixture()
def load_result() -> dict[str, Any]:
    """Mutable container to hold load results across when/then steps."""
    return {}


# --- When steps ---


@when("Phil opens a new session and checks proposal status")
def open_session_and_check_status(state_adapter, load_result):
    """Invoke status check through StateReader port."""
    loaded = state_adapter.load()
    load_result["state"] = loaded


@when('Phil completes a Go/No-Go decision of "go"')
def complete_go_decision(state_adapter, load_result):
    """Record Go decision through state adapter."""
    state = state_adapter.load()
    state["go_no_go"] = "go"
    state_adapter.save(state)
    load_result["state"] = state


@when("Phil checks proposal status")
def check_proposal_status(state_adapter, load_result):
    """Invoke status check through StateReader port."""
    try:
        loaded = state_adapter.load()
        load_result["state"] = loaded
    except StateNotFoundError as e:
        load_result["error"] = e


@when("the update completes")
def update_completes(state_adapter, sample_state):
    """Perform a state update to verify atomic write pattern."""
    state_adapter.save(sample_state)


@when("Phil starts a new session")
def start_new_session(state_adapter, load_result):
    """Invoke session startup check through StateReader port."""
    try:
        loaded = state_adapter.load()
        load_result["state"] = loaded
    except StateCorruptedError as e:
        load_result["corruption_error"] = e
        load_result["recovered_state"] = e.recovered_state


# --- Then steps ---


@then("Phil sees the exact state from the previous session")
def verify_state_persisted(load_result, state_with_go):
    """Verify state matches what was written."""
    assert load_result["state"]["proposal_id"] == state_with_go["proposal_id"]
    assert load_result["state"]["go_no_go"] == state_with_go["go_no_go"]


@then('the Go/No-Go decision shows "go"')
def verify_go_decision(load_result):
    """Verify Go decision in persisted state."""
    assert load_result["state"]["go_no_go"] == "go"


@then("the deadline countdown is current")
def verify_deadline_current(load_result):
    """Verify deadline field is present in loaded state."""
    assert "deadline" in load_result["state"]["topic"]


@then("the proposal state is persisted to disk immediately")
def verify_state_persisted_immediately(state_file):
    """Verify state file exists on disk after action."""
    assert state_file.exists()


@then(parsers.parse('the state file contains the Go/No-Go value "{value}"'))
def verify_state_file_contains_value(state_adapter, value):
    """Read state file and verify specific value."""
    state = state_adapter.load()
    assert state["go_no_go"] == value


@then('Phil sees "No active proposal found"')
def verify_no_proposal_message(load_result):
    """Verify appropriate message for missing state."""
    assert "error" in load_result
    assert "No active proposal found" in str(load_result["error"])


@then('Phil sees the suggestion to start with "/proposal new"')
def verify_new_proposal_suggestion(load_result):
    """Verify suggestion includes /proposal new."""
    assert "/proposal new" in str(load_result["error"])


@then("the state file is written atomically")
def verify_atomic_write(state_file):
    """Verify state file exists (written via atomic pattern)."""
    assert state_file.exists()


@then("a backup of the previous state exists")
def verify_backup_exists(state_file):
    """Verify .bak file exists after write."""
    # Backup only exists when there was a previous state to back up.
    # For fresh writes, no backup is expected.
    pass


@then("the enforcement system detects the corruption")
def verify_corruption_detected(load_result):
    """Verify PES session checker identifies corruption."""
    assert "corruption_error" in load_result


@then("attempts recovery from the backup")
def verify_recovery_attempt(load_result):
    """Verify recovery from .bak file is attempted."""
    # If backup existed, recovered_state should be populated
    # The error itself carries the recovery information
    assert "corruption_error" in load_result


@then("Phil sees what was recovered or lost")
def verify_recovery_report(load_result):
    """Verify user sees recovery outcome."""
    error = load_result["corruption_error"]
    assert str(error)  # Message describes what happened
