"""Step definitions for proposal state persistence (US-007).

Invokes through: StateReader port, state write utilities.
Does NOT import internal validators or domain entities directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature file
scenarios("../features/proposal_state.feature")


# --- Given steps ---


@given("Phil completed the Go/No-Go decision for AF243-001")
def go_decision_completed(state_with_go, write_state):
    """Write state with Go decision to disk."""
    write_state(state_with_go)


@given("Phil closed the session")
def session_closed():
    """Session closure is implicit -- state was written to disk."""
    pass


@given("Phil has an active proposal for AF243-001")
def active_proposal(sample_state, write_state):
    """Set up basic active proposal."""
    write_state(sample_state)


@given("any proposal state update is in progress")
def state_update_in_progress():
    """Precondition for property test on atomic writes."""
    pass


@given("the proposal state file was partially written due to a crash")
def corrupted_state_file(state_file):
    """Write truncated JSON to simulate crash during write."""
    state_file.write_text('{"schema_version": "1.0.0", "proposal_id": "test-uuid"')


# --- When steps ---


@when("Phil opens a new session and checks proposal status")
def open_session_and_check_status():
    """Invoke status check through driving port."""
    # TODO: Invoke through StateReader port when implemented
    pytest.skip("Awaiting StateReader port implementation")


@when('Phil completes a Go/No-Go decision of "go"')
def complete_go_decision():
    """Record Go decision through driving port."""
    # TODO: Invoke through state write service when implemented
    pytest.skip("Awaiting state write service implementation")


@when("Phil checks proposal status")
def check_proposal_status():
    """Invoke status check through driving port."""
    # TODO: Invoke through StatusService when implemented
    pytest.skip("Awaiting StatusService implementation")


@when("the update completes")
def update_completes():
    """State update completion -- property test."""
    # TODO: Invoke through atomic write utility when implemented
    pytest.skip("Awaiting atomic write implementation")


@when("Phil starts a new session")
def start_new_session():
    """Invoke session startup check through PES hook adapter."""
    # TODO: Invoke through ClaudeCodeHookAdapter when implemented
    pytest.skip("Awaiting ClaudeCodeHookAdapter implementation")


# --- Then steps ---


@then("Phil sees the exact state from the previous session")
def verify_state_persisted():
    """Verify state matches what was written."""
    # TODO: Assert through StateReader port
    pass


@then('the Go/No-Go decision shows "go"')
def verify_go_decision():
    """Verify Go decision in persisted state."""
    # TODO: Assert go_no_go value from StateReader
    pass


@then("the deadline countdown is current")
def verify_deadline_current():
    """Verify days-to-deadline is computed from stored deadline."""
    # TODO: Assert computed deadline
    pass


@then("the proposal state is persisted to disk immediately")
def verify_state_persisted_immediately():
    """Verify state file exists on disk after action."""
    # TODO: Assert state file write timestamp
    pass


@then(parsers.parse('the state file contains the Go/No-Go value "{value}"'))
def verify_state_file_contains_value(value):
    """Read state file and verify specific value."""
    # TODO: Read file and parse JSON
    pass


@then('Phil sees "No active proposal found"')
def verify_no_proposal_message():
    """Verify appropriate message for missing state."""
    # TODO: Assert message from status service
    pass


@then('Phil sees the suggestion to start with "/proposal new"')
def verify_new_proposal_suggestion():
    """Verify suggestion includes /proposal new."""
    # TODO: Assert suggestion text
    pass


@then("the state file is written atomically")
def verify_atomic_write():
    """Verify atomic write pattern (tmp -> rename)."""
    # TODO: Assert no partial writes possible
    pass


@then("a backup of the previous state exists")
def verify_backup_exists():
    """Verify .bak file exists after write."""
    # TODO: Assert .bak file
    pass


@then("the enforcement system detects the corruption")
def verify_corruption_detected():
    """Verify PES session checker identifies corruption."""
    # TODO: Assert corruption detection through PES
    pass


@then("attempts recovery from the backup")
def verify_recovery_attempt():
    """Verify recovery from .bak file is attempted."""
    # TODO: Assert recovery behavior
    pass


@then("Phil sees what was recovered or lost")
def verify_recovery_report():
    """Verify user sees recovery outcome."""
    # TODO: Assert recovery message
    pass
