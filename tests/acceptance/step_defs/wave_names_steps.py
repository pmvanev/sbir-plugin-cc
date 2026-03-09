"""Step definitions for wave names and cross-cutting state expansion (C2 Foundation).

Invokes through: StatusService (driving port) for wave name display.
Does NOT import internal wave name constants or state builders directly.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/wave_names.feature")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def wave_names_context() -> dict[str, Any]:
    """Mutable context to pass data between steps."""
    return {}


# --- Given steps ---


@given(
    parsers.parse(
        "Phil has an active proposal for {topic_id} with waves 0 through 9 initialized"
    ),
    target_fixture="active_state",
)
def proposal_with_all_waves(sample_state, write_state, topic_id):
    """Set up proposal state with all 10 waves initialized."""
    state = sample_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 2
    state["go_no_go"] = "go"
    waves = {}
    for w in range(10):
        if w < 2:
            waves[str(w)] = {
                "status": "completed",
                "completed_at": "2026-03-01T10:00:00Z",
            }
        elif w == 2:
            waves[str(w)] = {"status": "active", "completed_at": None}
        else:
            waves[str(w)] = {"status": "not_started", "completed_at": None}
    state["waves"] = waves
    write_state(state)
    return state


# --- When steps ---


@when("Phil checks proposal status", target_fixture="status_report")
def check_status(state_file):
    """Invoke StatusService through driving port."""
    from pes.adapters.json_state_adapter import JsonStateAdapter
    from pes.domain.status_service import StatusService

    state_reader = JsonStateAdapter(str(state_file.parent))
    service = StatusService(state_reader)
    return service.get_status()


# --- Then steps ---


@then(parsers.parse('Phil sees "{wave_name}"'))
def verify_wave_name_in_status(status_report, wave_name):
    """Verify that the wave name appears in the status report."""
    all_wave_names = [w.name for w in status_report.waves]
    current = status_report.current_wave
    all_text = " ".join(all_wave_names) + " " + current
    assert wave_name in all_text, (
        f"Expected '{wave_name}' in wave names. "
        f"Found waves: {all_wave_names}, current: {current}"
    )
