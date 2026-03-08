"""Common steps shared across all acceptance features.

These steps handle shared preconditions like plugin activation
and proposal state setup.
"""

from __future__ import annotations

import pytest
from pytest_bdd import given, parsers


@given("the proposal plugin is active")
def plugin_is_active():
    """Plugin activation context -- satisfied by test fixtures."""
    # In acceptance tests, the plugin is "active" when PES components
    # are instantiated with test fixtures. No actual Claude Code runtime needed.
    pass


@given("no proposal exists in the current directory")
def no_proposal_exists(proposal_dir):
    """Ensure no proposal-state.json exists."""
    state_file = proposal_dir / ".sbir" / "proposal-state.json"
    if state_file.exists():
        state_file.unlink()


@given(
    parsers.parse(
        'Phil has an active proposal for topic {topic_id} in Wave {wave:d}'
    ),
    target_fixture="active_state",
)
def active_proposal_in_wave(sample_state, write_state, topic_id, wave):
    """Set up an active proposal at a specific wave."""
    state = sample_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = wave
    for w in range(wave):
        state["waves"][str(w)] = {
            "status": "completed",
            "completed_at": "2026-03-01T10:00:00Z",
        }
    state["waves"][str(wave)] = {"status": "active", "completed_at": None}
    if wave >= 1:
        state["go_no_go"] = "go"
    write_state(state)
    return state


@given(
    parsers.parse(
        'Phil has an active proposal with Go/No-Go "{decision}"'
    ),
    target_fixture="active_state",
)
def proposal_with_decision(sample_state, write_state, decision):
    """Set up proposal with a specific Go/No-Go state."""
    state = sample_state.copy()
    state["go_no_go"] = decision
    write_state(state)
    return state


@given(
    parsers.parse("{days:d} days remain until the deadline"),
)
def days_until_deadline(active_state, write_state, days):
    """Adjust deadline to be N days from today."""
    from datetime import date, timedelta

    deadline = date.today() + timedelta(days=days)
    active_state["topic"]["deadline"] = deadline.isoformat()
    write_state(active_state)
