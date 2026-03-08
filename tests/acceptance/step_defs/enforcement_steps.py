"""Step definitions for PES enforcement system (US-006).

Invokes through: EnforcementEngine, ClaudeCodeHookAdapter.
Does NOT import internal Rule classes or SessionChecker directly.
"""

from __future__ import annotations

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Link to feature file
scenarios("../features/pes_enforcement.feature")


# --- Given steps ---


@given("Phil's last session ended unexpectedly")
def last_session_crashed():
    """Simulate unexpected session termination -- state may be inconsistent."""
    pass


@given("a draft file exists for section 3.2 without a compliance matrix entry")
def orphaned_draft(proposal_dir):
    """Create an orphaned draft file with no compliance matrix entry."""
    drafts_dir = proposal_dir / "drafts"
    drafts_dir.mkdir(exist_ok=True)
    (drafts_dir / "section-3.2.md").write_text("# Section 3.2 Draft\n\nIncomplete draft.")


@given("the proposal state is consistent with no orphaned files")
def clean_state(state_with_go, write_state):
    """Write a clean, consistent state."""
    write_state(state_with_go)


@given(
    parsers.parse("Phil has an active proposal with {days:d} days remaining"),
)
def proposal_near_deadline(sample_state, write_state, days):
    """Set up proposal with near deadline."""
    from datetime import date, timedelta

    state = sample_state.copy()
    state["go_no_go"] = "go"
    state["current_wave"] = 1
    state["topic"]["deadline"] = (date.today() + timedelta(days=days)).isoformat()
    write_state(state)


@given("Phil has an active proposal in Wave 1")
def proposal_in_wave_1(state_with_go, write_state):
    """Set up proposal in Wave 1."""
    write_state(state_with_go)


@given("the strategy brief has not been approved")
def strategy_not_approved(state_with_go):
    """Ensure strategy brief status is not approved."""
    state_with_go["strategy_brief"]["status"] = "not_started"


@given("Phil has an active proposal with a compliance matrix")
def proposal_with_matrix(state_with_go, write_state, compliance_matrix_path):
    """Set up proposal with compliance matrix but missing section."""
    state_with_go["compliance_matrix"]["item_count"] = 47
    write_state(state_with_go)
    compliance_matrix_path.write_text(
        "# Compliance Matrix\n\n| # | Requirement | Section | Status |\n"
    )


@given("no matrix entry covers section 3.2")
def no_section_32_entry():
    """Compliance matrix does not contain an entry for section 3.2."""
    pass


@given("the enforcement configuration file does not exist")
def missing_pes_config(proposal_dir):
    """Ensure pes-config.json does not exist."""
    config_path = proposal_dir / ".sbir" / "pes-config.json"
    if config_path.exists():
        config_path.unlink()


@given("the proposal state file is corrupted")
def corrupted_state(state_file):
    """Write corrupted state file."""
    state_file.write_text("{corrupted json content")


@given("any new enforcement rule defined in the configuration")
def new_enforcement_rule():
    """Precondition for extensibility property test."""
    pass


# --- When steps ---


@when("Phil starts a new session")
def start_session():
    """Invoke session startup through PES hook adapter."""
    # TODO: Invoke through ClaudeCodeHookAdapter session_start
    pytest.skip("Awaiting ClaudeCodeHookAdapter implementation")


@when("Phil attempts to start Wave 1 strategy work")
def attempt_wave_1():
    """Invoke wave strategy command through PES enforcement."""
    # TODO: Invoke through EnforcementEngine with PreToolUse event
    pytest.skip("Awaiting EnforcementEngine implementation")


@when("Phil starts Wave 1 strategy work")
def start_wave_1():
    """Invoke wave strategy after Go decision."""
    # TODO: Invoke through EnforcementEngine
    pytest.skip("Awaiting EnforcementEngine implementation")


@when("Phil attempts to start Wave 2 work")
def attempt_wave_2():
    """Invoke Wave 2 command through PES enforcement."""
    # TODO: Invoke through EnforcementEngine with PreToolUse event
    pytest.skip("Awaiting EnforcementEngine implementation")


@when("Phil attempts to draft section 3.2")
def attempt_draft_section():
    """Invoke draft command through PES compliance gate."""
    # TODO: Invoke through EnforcementEngine
    pytest.skip("Awaiting EnforcementEngine implementation")


@when("the enforcement engine loads rules")
def load_rules():
    """Invoke rule registry loading."""
    # TODO: Invoke through RuleRegistry
    pytest.skip("Awaiting RuleRegistry implementation")


@when("the enforcement system attempts to load rules")
def attempt_load_rules():
    """Invoke rule loading with missing config."""
    # TODO: Invoke through RuleRegistry
    pytest.skip("Awaiting RuleRegistry implementation")


@when("the enforcement system runs its integrity check")
def run_integrity_check():
    """Invoke session checker."""
    # TODO: Invoke through SessionChecker via hook adapter
    pytest.skip("Awaiting SessionChecker implementation")


# --- Then steps ---


@then("the enforcement system detects the orphaned draft")
def verify_orphan_detected():
    """Verify PES detects draft without matrix entry."""
    # TODO: Assert through enforcement result
    pass


@then(parsers.parse('Phil sees "{message}"'))
def verify_message(message):
    """Verify user-facing message content."""
    # TODO: Assert message from enforcement/service result
    pass


@then("Phil sees guidance to run the compliance check")
def verify_compliance_guidance():
    """Verify guidance suggests compliance check."""
    pass


@then("the enforcement system runs silently")
def verify_silent_run():
    """Verify no output from enforcement on clean state."""
    pass


@then("no warnings are displayed")
def verify_no_warnings():
    """Verify zero warning messages."""
    pass


@then("Phil sees a critical deadline warning")
def verify_deadline_warning():
    """Verify deadline warning at critical threshold."""
    pass


@then("Phil sees suggestions for prioritizing remaining work")
def verify_priority_suggestions():
    """Verify actionable suggestions for deadline pressure."""
    pass


@then("the enforcement system blocks the action")
def verify_action_blocked():
    """Verify enforcement returns block decision (exit code 1)."""
    # TODO: Assert Decision.block from EnforcementEngine
    pass


@then("Phil sees guidance to complete the Go/No-Go step first")
def verify_go_guidance():
    """Verify guidance points to Go/No-Go step."""
    pass


@then("the action proceeds normally")
def verify_action_allowed():
    """Verify enforcement returns allow decision (exit code 0)."""
    # TODO: Assert Decision.allow from EnforcementEngine
    pass


@then("Phil sees guidance to add a compliance item")
def verify_add_compliance_guidance():
    """Verify guidance suggests adding compliance item."""
    pass


@then("the block decision is recorded in the audit log with a timestamp")
def verify_audit_log():
    """Verify audit log entry for enforcement decision."""
    # TODO: Read audit log file and verify entry
    pass


@then("the new rule is evaluated alongside existing rules")
def verify_rule_evaluation():
    """Verify new rules loaded and evaluated."""
    pass


@then("the engine architecture remains unchanged")
def verify_engine_unchanged():
    """Verify extensibility without engine modification."""
    pass


@then("the system uses default enforcement rules")
def verify_default_rules():
    """Verify fallback to defaults on missing config."""
    pass


@then("Phil sees a warning that the configuration was not found")
def verify_config_warning():
    """Verify warning about missing configuration."""
    pass


@then("Phil sees guidance for recovery")
def verify_recovery_guidance():
    """Verify recovery guidance provided."""
    pass
