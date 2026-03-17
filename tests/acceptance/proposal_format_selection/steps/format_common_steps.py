"""Common steps shared across all Proposal Format Selection acceptance features.

These steps handle shared preconditions: proposal state setup, wave
positioning, and format field setup.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then


@given(
    parsers.parse('Phil Santos has an active proposal for topic "{topic_id}"'),
)
def active_proposal(
    topic_id: str,
    base_proposal_state: dict[str, Any],
    proposal_context: dict[str, Any],
) -> None:
    """Set up an active proposal state in context."""
    state = dict(base_proposal_state)
    state["topic"]["id"] = topic_id
    state["go_no_go"] = "go"
    state["current_wave"] = 1
    proposal_context["state"] = state


@given(
    parsers.parse('Phil Santos creates a new proposal for topic "{topic_id}"'),
)
def create_new_proposal(
    topic_id: str,
    base_proposal_state: dict[str, Any],
    proposal_context: dict[str, Any],
) -> None:
    """Set up a new proposal state in context (Wave 0, pending)."""
    state = dict(base_proposal_state)
    state["topic"]["id"] = topic_id
    proposal_context["state"] = state


@given(
    parsers.parse("the proposal is in Wave {wave:d}"),
)
def set_current_wave(wave: int, proposal_context: dict[str, Any]) -> None:
    """Set the current wave number on the proposal state."""
    proposal_context["state"]["current_wave"] = wave


@given(
    parsers.parse('the current output format is "{fmt}"'),
)
def set_current_format(fmt: str, proposal_context: dict[str, Any]) -> None:
    """Set the current output_format field on the proposal state."""
    proposal_context["state"]["output_format"] = fmt


@given(
    parsers.parse('Phil Santos selects "{fmt}" as the output format'),
)
def select_format(fmt: str, proposal_context: dict[str, Any]) -> None:
    """Record the user's format selection for the proposal."""
    proposal_context["selected_format"] = fmt


# --- Shared Then steps ---


@then(
    parsers.parse('the proposal state contains output format "{fmt}"'),
)
def state_has_format(fmt: str, read_state) -> None:
    """Assert the persisted state contains the expected output_format."""
    state = read_state()
    assert state["output_format"] == fmt, (
        f"Expected output_format '{fmt}', got '{state.get('output_format')}'"
    )
