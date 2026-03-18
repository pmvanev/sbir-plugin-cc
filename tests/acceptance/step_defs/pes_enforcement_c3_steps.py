"""Step definitions for PES C3 enforcement (US-014).

Invokes through: EnforcementEngine (driving port).
Does NOT import PDCGateEvaluator, DeadlineBlockingEvaluator,
SubmissionImmutabilityEvaluator, or CorpusIntegrityEvaluator directly.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from pes.domain.rules import Decision
from tests.acceptance.step_defs.common_steps import *  # noqa: F403

# Link to feature file
scenarios("../features/pes_enforcement_c3.feature")


# --- Given steps ---


@given(
    "Phil has an active proposal with all sections drafted",
    target_fixture="active_state",
)
def proposal_all_sections_drafted(sample_state, write_state):
    """Set up proposal at Wave 4 completed, ready for Wave 5."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 5
    state["waves"] = {
        "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
        "1": {"status": "completed", "completed_at": "2026-03-05T10:00:00Z"},
        "2": {"status": "completed", "completed_at": "2026-03-06T10:00:00Z"},
        "3": {"status": "completed", "completed_at": "2026-03-07T10:00:00Z"},
        "4": {"status": "completed", "completed_at": "2026-03-08T10:00:00Z"},
        "5": {"status": "active", "completed_at": None},
    }
    state["strategy_brief"] = {
        "path": "./artifacts/wave-1-strategy/strategy-brief.md",
        "status": "approved",
        "approved_at": "2026-03-05T10:00:00Z",
    }
    state["outline"] = {
        "status": "approved",
        "approved_at": "2026-03-07T10:00:00Z",
    }
    write_state(state)
    return state


@given(
    parsers.parse("section {section_id} has {count:d} RED Tier 2 PDC item"),
)
def section_has_red_pdc(active_state, write_state, proposal_dir, section_id, count):
    """Create PDC state indicating RED items for a section."""
    pdcs_dir = proposal_dir / "pdcs"
    pdcs_dir.mkdir(exist_ok=True)
    pdc_data = {
        "section_id": section_id,
        "tier_1": {"status": "GREEN", "items": []},
        "tier_2": {
            "status": "RED",
            "items": [
                {
                    "item_id": f"pdc-{section_id}-t2-001",
                    "description": "Phase II pathway uses generic language",
                    "status": "RED",
                }
            ],
        },
    }
    (pdcs_dir / f"section-{section_id}.pdc").write_text(json.dumps(pdc_data, indent=2))
    # Update state with PDC status for engine evaluation
    if "pdc_status" not in active_state:
        active_state["pdc_status"] = {}
    active_state["pdc_status"][section_id] = {
        "tier_1": "GREEN",
        "tier_2": "RED",
        "red_items": ["Phase II pathway uses generic language"],
    }
    write_state(active_state)


@given("all sections have Tier 1 and Tier 2 PDCs GREEN")
def all_sections_green_pdcs(active_state, write_state, proposal_dir):
    """Create PDC state indicating all sections GREEN."""
    pdcs_dir = proposal_dir / "pdcs"
    pdcs_dir.mkdir(exist_ok=True)
    pdc_status: dict[str, Any] = {}
    for section_id in ["3.1", "3.2", "3.3", "3.4", "4.1"]:
        pdc_data = {
            "section_id": section_id,
            "tier_1": {"status": "GREEN", "items": []},
            "tier_2": {"status": "GREEN", "items": []},
        }
        (pdcs_dir / f"section-{section_id}.pdc").write_text(
            json.dumps(pdc_data, indent=2)
        )
        pdc_status[section_id] = {
            "tier_1": "GREEN",
            "tier_2": "GREEN",
            "red_items": [],
        }
    active_state["pdc_status"] = pdc_status
    write_state(active_state)


@given(
    parsers.parse("Phil has an active proposal in Wave {wave:d}"),
    target_fixture="active_state",
)
def proposal_in_wave_c3(sample_state, write_state, wave):
    """Set up an active proposal at a specific wave."""
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


@given("Wave 5 is not complete")
def wave_5_not_complete(active_state):
    """Wave 5 is still in progress."""
    # Already in active state from proposal_in_wave_c3
    pass


@given(
    "AF243-001 has been submitted with confirmation recorded",
    target_fixture="active_state",
)
def submitted_proposal(sample_state, write_state):
    """Set up proposal in submitted state with immutability flag."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 8
    state["submission"] = {
        "status": "submitted",
        "portal": "DSIP",
        "confirmation_number": "DSIP-2026-AF243-001-7842",
        "submitted_at": "2026-04-07T14:23:17Z",
        "archive_path": "./artifacts/wave-8-submission/archive/",
        "immutable": True,
    }
    write_state(state)
    return state


@given(
    parsers.parse('AF243-001 has a win/loss tag of "{tag}"'),
    target_fixture="active_state",
)
def proposal_with_outcome(sample_state, write_state, tag):
    """Set up proposal with existing outcome tag."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 9
    state["learning"] = {
        "outcome": tag,
        "outcome_recorded_at": "2026-07-01T10:00:00Z",
        "debrief_requested": None,
        "debrief_ingested": False,
    }
    write_state(state)
    return state


@given("AF243-001 has no outcome tag recorded", target_fixture="active_state")
def proposal_no_outcome(sample_state, write_state):
    """Set up proposal with no outcome tag."""
    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 9
    state["learning"] = {
        "outcome": None,
        "outcome_recorded_at": None,
    }
    write_state(state)
    return state


@given("PES has blocked 3 actions during Waves 5-8")
def pes_blocked_actions(in_memory_audit_log):
    """Pre-populate audit log with 3 blocked actions."""
    for i in range(3):
        in_memory_audit_log.log(
            {
                "timestamp": f"2026-03-{10 + i}T10:00:00Z",
                "decision": "BLOCK",
                "rule_name": f"c3-rule-{i}",
                "details": f"Blocked action {i}",
            }
        )


@given("any C3 enforcement rule defined in pes-config.json")
def c3_enforcement_rule():
    """Precondition for configuration property test."""
    pass


# --- When steps ---


@when(
    "Phil attempts to start Wave 5 visual asset work",
    target_fixture="enforcement_result",
)
def attempt_wave_5(enforcement_engine, state_file):
    """Invoke Wave 5 command through PES enforcement."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_5_visuals")


@when(
    "Phil starts Wave 5 visual asset work",
    target_fixture="enforcement_result",
)
def start_wave_5(enforcement_engine, state_file):
    """Invoke Wave 5 work after prerequisites met."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.evaluate(state, tool_name="wave_5_visuals")


@when("Phil checks proposal status", target_fixture="enforcement_result")
def check_status_c3(enforcement_engine, state_file, proposal_dir):
    """Check proposal status through enforcement engine session check."""
    from pes.adapters.json_state_adapter import JsonStateAdapter

    state_reader = JsonStateAdapter(str(state_file.parent))
    state = state_reader.load()
    return enforcement_engine.check_session_start(
        state, proposal_dir=str(proposal_dir)
    )


@when("Phil attempts to write to any file under the proposal artifact directories")
def attempt_write_submitted():
    """Attempt to modify a submitted artifact."""
    pytest.skip("Awaiting SubmissionImmutabilityEvaluator implementation")


@when("Phil reads a submitted artifact")
def read_submitted():
    """Read a submitted artifact (should be allowed)."""
    pytest.skip("Awaiting SubmissionImmutabilityEvaluator implementation")


@when("any process attempts to change the tag to \"awarded\"")
def attempt_modify_outcome():
    """Attempt to overwrite an existing outcome tag."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")


@when(
    parsers.parse('the outcome is recorded as "{outcome}"'),
)
def record_new_outcome(outcome):
    """Record a new outcome tag on a proposal with no existing tag."""
    pytest.skip("Awaiting OutcomeService implementation")


@when("Phil reviews the audit log")
def review_audit_log():
    """Review PES audit log."""
    # Audit log is checked in Then step
    pass


@when("the rule is enabled or disabled via configuration")
def toggle_rule_config():
    """Toggle a C3 enforcement rule configuration."""
    pytest.skip("Awaiting C3 PES config extension implementation")


# --- Then steps ---


@then("the enforcement system blocks the action")
def verify_action_blocked_c3(enforcement_result):
    """Verify enforcement returns block decision."""
    assert enforcement_result.decision == Decision.BLOCK


@then("Phil sees the specific section and PDC items that remain RED")
def verify_red_pdc_details(enforcement_result):
    """Verify message contains PDC-specific details."""
    all_messages = " ".join(enforcement_result.messages).lower()
    assert "pdc" in all_messages or "red" in all_messages or "section" in all_messages, (
        f"Expected PDC details in {enforcement_result.messages}"
    )


@then("the action proceeds normally")
def verify_action_allowed_c3(enforcement_result):
    """Verify enforcement returns allow decision."""
    assert enforcement_result.decision == Decision.ALLOW


@then("Phil sees a critical deadline warning")
def verify_critical_deadline_warning(enforcement_result):
    """Verify critical deadline warning is present."""
    all_messages = " ".join(enforcement_result.messages).lower()
    assert "critical" in all_messages or "deadline" in all_messages, (
        f"Expected critical deadline warning in {enforcement_result.messages}"
    )


@then("Phil sees a suggestion to submit with available work or skip non-essential waves")
def verify_deadline_suggestion(enforcement_result):
    """Verify deadline guidance suggests submitting or skipping."""
    all_messages = " ".join(enforcement_result.messages).lower()
    assert "submit" in all_messages or "skip" in all_messages, (
        f"Expected submission/skip suggestion in {enforcement_result.messages}"
    )


@then("no deadline blocking warning is displayed")
def verify_no_deadline_warning(enforcement_result):
    """Verify no deadline blocking warning."""
    all_messages = " ".join(enforcement_result.messages).lower()
    assert "critical" not in all_messages or "deadline" not in all_messages


@then("the enforcement system blocks the write operation")
def verify_write_blocked():
    """Verify write to submitted artifact is blocked."""
    pytest.skip("Awaiting SubmissionImmutabilityEvaluator implementation")


@then("the blocked attempt is recorded in the audit log")
def verify_blocked_in_audit(in_memory_audit_log):
    """Verify blocked attempt is logged."""
    assert len(in_memory_audit_log.entries) > 0
    assert in_memory_audit_log.entries[-1]["decision"] == "block"


@then("the read proceeds normally")
def verify_read_allowed():
    """Verify read of submitted artifact is allowed."""
    pytest.skip("Awaiting SubmissionImmutabilityEvaluator implementation")


@then("the enforcement system blocks the modification")
def verify_modification_blocked():
    """Verify modification of outcome tag is blocked."""
    pytest.skip("Awaiting CorpusIntegrityEvaluator implementation")


@then("the outcome tag is appended successfully")
def verify_outcome_appended():
    """Verify new outcome tag is appended."""
    pytest.skip("Awaiting OutcomeService implementation")


@then(
    "all 3 blocked actions are recorded with timestamps, rule names, and details"
)
def verify_audit_log_entries(in_memory_audit_log):
    """Verify all 3 blocked actions in audit log."""
    assert len(in_memory_audit_log.entries) >= 3
    for entry in in_memory_audit_log.entries:
        assert "timestamp" in entry
        assert "rule_name" in entry
        assert "decision" in entry


@then("the enforcement engine respects the configuration setting")
def verify_config_respected():
    """Verify rule configuration is respected."""
    pytest.skip("Awaiting C3 PES config extension implementation")


@then("existing C1 invariants continue to function")
def verify_c1_invariants():
    """Verify C1 enforcement rules still work."""
    pytest.skip("Awaiting C3 PES config extension implementation")
