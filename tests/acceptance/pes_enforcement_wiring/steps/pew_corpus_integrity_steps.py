"""Step definitions for Corpus Integrity enforcement scenarios (US-PEW-004).

Invokes through driving port: EnforcementEngine.evaluate() only.
Does NOT import CorpusIntegrityEvaluator directly.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, scenarios, when

from tests.acceptance.pes_enforcement_wiring.steps.pew_common_steps import *  # noqa: F403

scenarios("../corpus_integrity.feature")


# ---------------------------------------------------------------------------
# Given Steps (Corpus-specific)
# ---------------------------------------------------------------------------


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has no recorded outcome'),
)
def proposal_no_outcome(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with no existing outcome tag."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 9
    state["learning"] = {"outcome": None}
    enforcement_context["state"] = state


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has no learning data'),
)
def proposal_no_learning(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal with no learning field at all."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 9
    # Deliberately no learning key
    enforcement_context["state"] = state


# ---------------------------------------------------------------------------
# When Steps (Corpus-specific)
# ---------------------------------------------------------------------------


@when(
    parsers.parse('Phil records outcome as "{outcome}"'),
    target_fixture="enforcement_context",
)
def record_outcome(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    outcome: str,
):
    """Invoke engine.evaluate() with record_outcome tool."""
    state = enforcement_context["state"]
    state["requested_outcome_change"] = outcome
    result = enforcement_engine.evaluate(state, tool_name="record_outcome")
    enforcement_context["result"] = result
    return enforcement_context
