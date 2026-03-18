"""Step definitions for Wave 2-4 ordering enforcement (C2).

Invokes through: EnforcementEngine (driving port).
Does NOT import WaveOrderingEvaluator or internal rule classes directly.
"""

from __future__ import annotations

from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.rules import Decision
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/wave_ordering_c2.feature")


# --- Given steps ---


@given(
    parsers.parse("Phil has an active proposal in Wave {wave:d}"),
    target_fixture="active_state",
)
def proposal_in_wave(sample_state, write_state, wave):
    """Set up an active proposal at a specific wave with Go decision."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = wave
    for w in range(wave):
        state["waves"][str(w)] = {
            "status": "completed",
            "completed_at": "2026-03-01T10:00:00Z",
        }
    state["waves"][str(wave)] = {"status": "active", "completed_at": None}
    write_state(state)
    return state


@given(
    "Phil has an active proposal with an approved strategy brief",
    target_fixture="active_state",
)
def proposal_with_strategy_approved(sample_state, write_state):
    """Set up proposal with strategy brief approved, ready for Wave 2."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 2
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "active", "completed_at": None},
    }
    state["strategy_brief"] = {
        "path": "./artifacts/wave-1-strategy/strategy-brief.md",
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    write_state(state)
    return state


@given(
    "Phil has an active proposal with approved research review",
    target_fixture="active_state",
)
def proposal_with_research_approved(sample_state, write_state):
    """Set up proposal with research approved, ready for Wave 3."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 3
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "3": {"status": "active", "completed_at": None},
    }
    state["strategy_brief"] = {
        "path": "./artifacts/wave-1-strategy/strategy-brief.md",
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["research_summary"] = {
        "status": "approved",
        "approved_at": "2026-03-08T10:00:00Z",
    }
    write_state(state)
    return state


@given(
    "Phil has an active proposal with an approved proposal outline",
    target_fixture="active_state",
)
def proposal_with_outline_approved(sample_state, write_state):
    """Set up proposal with outline approved, ready for Wave 4."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 4
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-10T10:00:00Z"},
        "4": {"status": "active", "completed_at": None},
    }
    state["strategy_brief"] = {
        "path": "./artifacts/wave-1-strategy/strategy-brief.md",
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["research_summary"] = {
        "status": "approved",
        "approved_at": "2026-03-08T10:00:00Z",
    }
    state["discrimination_table"] = {
        "status": "approved",
        "approved_at": "2026-03-09T10:00:00Z",
    }
    state["outline"] = {
        "status": "approved",
        "approved_at": "2026-03-10T10:00:00Z",
    }
    write_state(state)
    return state


@given("the strategy brief has not been approved")
def strategy_not_approved(active_state, write_state):
    """Ensure strategy brief status is not approved."""
    active_state.setdefault("strategy_brief", {})["status"] = "not_started"
    if "approved_at" in active_state.get("strategy_brief", {}):
        active_state["strategy_brief"]["approved_at"] = None
    write_state(active_state)


@given("the research review has not been approved")
def research_not_approved(active_state, write_state):
    """Ensure research review status is not approved."""
    active_state.setdefault("research_summary", {})["status"] = "not_started"
    write_state(active_state)


@given("the proposal outline has not been approved")
def outline_not_approved(active_state, write_state):
    """Ensure outline status is not approved."""
    active_state.setdefault("outline", {})["status"] = "not_started"
    write_state(active_state)


# --- When steps ---


@when("Phil starts Wave 2 research work", target_fixture="enforcement_result")
def start_wave_2(enforcement_engine, state_file):
    """Invoke Wave 2 work through PES enforcement."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_2_research")


@when(
    "Phil attempts to start Wave 2 research work",
    target_fixture="enforcement_result",
)
def attempt_wave_2_research(enforcement_engine, state_file):
    """Attempt Wave 2 work before prerequisites met."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_2_research")


@when(
    "Phil starts Wave 3 discrimination and outline work",
    target_fixture="enforcement_result",
)
def start_wave_3(enforcement_engine, state_file):
    """Invoke Wave 3 work through PES enforcement."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_3_outline")


@when("Phil attempts to start Wave 3 work", target_fixture="enforcement_result")
def attempt_wave_3(enforcement_engine, state_file):
    """Attempt Wave 3 work before prerequisites met."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_3_outline")


@when("Phil starts Wave 4 drafting work", target_fixture="enforcement_result")
def start_wave_4(enforcement_engine, state_file):
    """Invoke Wave 4 work through PES enforcement."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_4_drafting")


@when(
    "Phil attempts to start Wave 4 drafting work",
    target_fixture="enforcement_result",
)
def attempt_wave_4(enforcement_engine, state_file):
    """Attempt Wave 4 work before prerequisites met."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_4_drafting")


# --- Then steps ---


@then("the action proceeds normally")
def verify_action_allowed(enforcement_result):
    """Verify enforcement returns allow decision."""
    assert enforcement_result.decision == Decision.ALLOW


@then("the enforcement system blocks the action")
def verify_action_blocked(enforcement_result):
    """Verify enforcement returns block decision."""
    assert enforcement_result.decision == Decision.BLOCK


@then(parsers.parse('Phil sees "{message}"'))
def verify_message(enforcement_result, message):
    """Verify user-facing message content."""
    all_messages = " ".join(enforcement_result.messages)
    assert message in all_messages, (
        f"Expected '{message}' in {enforcement_result.messages}"
    )


@then("Phil sees guidance about completing prerequisite waves")
def verify_prerequisite_guidance(enforcement_result):
    """Verify guidance mentions prerequisites."""
    all_messages = " ".join(enforcement_result.messages).lower()
    assert "require" in all_messages or "prerequisite" in all_messages, (
        f"Expected prerequisite guidance in {enforcement_result.messages}"
    )


@then("the block decision is recorded in the audit log with a timestamp")
def verify_audit_logged(in_memory_audit_log):
    """Verify audit log entry for enforcement decision."""
    assert len(in_memory_audit_log.entries) > 0
    entry = in_memory_audit_log.entries[-1]
    assert "timestamp" in entry
    assert entry["decision"] == "block"


@then(parsers.parse('the audit entry includes the rule "{rule_id}"'))
def verify_audit_rule_id(in_memory_audit_log, rule_id):
    """Verify specific rule ID in audit entry."""
    entry = in_memory_audit_log.entries[-1]
    all_text = str(entry)
    assert rule_id in all_text or "wave" in all_text.lower(), (
        f"Expected rule '{rule_id}' referenced in audit entry: {entry}"
    )
