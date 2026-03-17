"""Common steps shared across all PES Enforcement Wiring acceptance features.

These steps handle shared preconditions (config loading, state setup)
and shared assertions (BLOCK/ALLOW decisions, message content).

Invokes through driving port: EnforcementEngine.evaluate() only.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then, when


# ---------------------------------------------------------------------------
# Shared Given Steps
# ---------------------------------------------------------------------------


@given("the enforcement rules are loaded from the standard configuration")
def enforcement_rules_loaded(enforcement_engine):
    """Precondition satisfied by conftest fixtures wiring real config."""
    # The enforcement_engine fixture already loads real pes-config.json
    # through JsonRuleAdapter. This step documents intent.
    pass


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has a pre-draft checklist with section'
        ' "{section}" showing Tier 1 RED for "{red_item}"'
    ),
)
def proposal_with_red_tier1_pdc(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
    section: str,
    red_item: str,
):
    """Set up proposal state with a RED Tier 1 PDC item in the given section."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 5
    state["pdc_status"] = {
        section: {
            "tier_1": "RED",
            "tier_2": "GREEN",
            "red_items": [red_item],
        }
    }
    enforcement_context["state"] = state


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has been submitted and marked as finalized'
    ),
)
def proposal_submitted_immutable(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal in submitted+immutable state."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 8
    state["submission"] = {
        "status": "submitted",
        "immutable": True,
    }
    enforcement_context["state"] = state


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has a recorded outcome of "{outcome}"'
    ),
)
def proposal_with_outcome(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
    outcome: str,
):
    """Set up proposal with an existing outcome tag."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 9
    state["learning"] = {"outcome": outcome}
    enforcement_context["state"] = state


@given(
    parsers.parse('Phil requests to change the outcome to "{new_outcome}"'),
)
def request_outcome_change(
    enforcement_context: dict[str, Any],
    new_outcome: str,
):
    """Set requested_outcome_change on state."""
    enforcement_context["state"]["requested_outcome_change"] = new_outcome


# ---------------------------------------------------------------------------
# Shared When Steps
# ---------------------------------------------------------------------------


@when(
    "Phil attempts to begin Wave 5 drafting work",
    target_fixture="enforcement_context",
)
def attempt_wave_5(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with wave_5_draft tool."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="wave_5_draft")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil attempts any action on the proposal",
    target_fixture="enforcement_context",
)
def attempt_any_action(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with a generic tool name."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="wave_6_format")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil attempts to record a different outcome",
    target_fixture="enforcement_context",
)
def attempt_record_outcome(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with record_outcome tool."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="record_outcome")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil uses a non-drafting tool",
    target_fixture="enforcement_context",
)
def use_non_drafting_tool(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with a tool that does not target Wave 5.

    Uses 'check_status' which does not match any wave_N pattern,
    so no wave_ordering or pdc_gate rules trigger.
    """
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="check_status")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil uses a non-outcome-related tool",
    target_fixture="enforcement_context",
)
def use_non_outcome_tool(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with a tool that is not outcome-related.

    Uses 'check_status' which does not contain 'outcome' or 'record_outcome',
    so corpus_integrity rules do not trigger.
    """
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="check_status")
    enforcement_context["result"] = result
    return enforcement_context


# ---------------------------------------------------------------------------
# Shared Then Steps
# ---------------------------------------------------------------------------


@then("the action is blocked")
def action_is_blocked(enforcement_context: dict[str, Any]):
    """Verify enforcement returned a BLOCK decision."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.BLOCK, (
        f"Expected BLOCK but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


@then("the action is allowed")
def action_is_allowed(enforcement_context: dict[str, Any]):
    """Verify enforcement returned an ALLOW decision."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.ALLOW, (
        f"Expected ALLOW but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


@then(
    parsers.parse('Phil sees "{expected_text}" in the block reason'),
)
def block_reason_contains_text(
    enforcement_context: dict[str, Any],
    expected_text: str,
):
    """Verify the block message contains the expected text."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages)
    assert expected_text in all_messages, (
        f"Expected '{expected_text}' in block messages. Got: {result.messages}"
    )


@then(
    parsers.parse('Phil sees "{expected_text}"'),
)
def sees_exact_text(
    enforcement_context: dict[str, Any],
    expected_text: str,
):
    """Verify the block message contains the expected text."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages)
    assert expected_text in all_messages, (
        f"Expected '{expected_text}' in messages. Got: {result.messages}"
    )


@then(
    parsers.parse('the block reason mentions "{expected_text}"'),
)
def block_reason_mentions(
    enforcement_context: dict[str, Any],
    expected_text: str,
):
    """Verify block message contains the expected text."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages)
    assert expected_text in all_messages, (
        f"Expected '{expected_text}' in block messages. Got: {result.messages}"
    )
