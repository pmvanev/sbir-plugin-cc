"""Step definitions for Deadline Blocking enforcement scenarios (US-PEW-002).

Invokes through driving port: EnforcementEngine.evaluate() only.
Does NOT import DeadlineBlockingEvaluator directly.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from pytest_bdd import given, parsers, scenarios, when

from tests.acceptance.pes_enforcement_wiring.steps.pew_common_steps import *  # noqa: F403

scenarios("../deadline_blocking.feature")


# ---------------------------------------------------------------------------
# Given Steps (Deadline-specific)
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has a deadline {days:d} days from now'
    ),
)
def proposal_with_deadline_days(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
    days: int,
):
    """Set up proposal with deadline N days from today.

    Also sets prerequisite approvals so wave_ordering rules don't fire
    for wave 2/3 tools used in deadline blocking scenarios.
    """
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["go_no_go"] = "go"
    deadline = date.today() + timedelta(days=days)
    state["topic"]["deadline"] = deadline.isoformat()
    # Satisfy wave_ordering prerequisites for Waves 2 and 3
    state["strategy_brief"] = {
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["research_summary"] = {
        "status": "approved",
        "approved_at": "2026-03-06T10:00:00Z",
    }
    enforcement_context["state"] = state


@given(
    parsers.parse("Phil is working in Wave {wave:d}"),
)
def working_in_wave(
    enforcement_context: dict[str, Any],
    wave: int,
):
    """Set current_wave on the proposal state."""
    enforcement_context["state"]["current_wave"] = wave


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has no deadline set'),
)
def proposal_no_deadline(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with no deadline field."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["topic"]["deadline"] = None
    state["go_no_go"] = "go"
    # Satisfy wave_ordering prerequisites
    state["strategy_brief"] = {
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["research_summary"] = {
        "status": "approved",
        "approved_at": "2026-03-06T10:00:00Z",
    }
    enforcement_context["state"] = state


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has an unparseable deadline value'),
)
def proposal_invalid_deadline(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with an invalid deadline string."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["topic"]["deadline"] = "not-a-date"
    state["go_no_go"] = "go"
    # Satisfy wave_ordering prerequisites
    state["strategy_brief"] = {
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["research_summary"] = {
        "status": "approved",
        "approved_at": "2026-03-06T10:00:00Z",
    }
    enforcement_context["state"] = state


# ---------------------------------------------------------------------------
# When Steps (Deadline-specific)
# ---------------------------------------------------------------------------


@when(
    "Phil attempts Wave 2 research work",
    target_fixture="enforcement_context",
)
def attempt_wave_2(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with wave_2_research tool."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="wave_2_research")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil attempts Wave 5 drafting work",
    target_fixture="enforcement_context",
)
def attempt_wave_5_deadline(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with wave_5_draft tool."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="wave_5_draft")
    enforcement_context["result"] = result
    return enforcement_context
