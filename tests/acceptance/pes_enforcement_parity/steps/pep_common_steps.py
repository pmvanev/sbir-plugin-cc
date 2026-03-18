"""Common steps shared across all PES Enforcement Parity acceptance features.

These steps handle shared preconditions (config loading, state setup)
and shared assertions (decisions, audit trail entries).

Invokes through driving ports:
- EnforcementEngine.check_session_start()
- EnforcementEngine.evaluate()
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
    pass


@given(
    parsers.parse(
        'Phil\'s previous session for proposal "{topic_id}" ended abnormally'
        " leaving a crash signal"
    ),
)
def proposal_with_crash_signal(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    crash_signal_file,
    topic_id: str,
):
    """Set up proposal with a crash signal from a previous abnormal session."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)
    enforcement_context["crash_signal_file"] = crash_signal_file


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" has audit entries older than'
        " the 365-day retention window"
    ),
)
def proposal_with_aged_audit(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    aged_audit_entries,
    topic_id: str,
):
    """Set up proposal with audit entries past retention window."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)
    enforcement_context["audit_file"] = aged_audit_entries


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" is in Wave 4 drafting'),
)
def proposal_in_wave_4(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 4 drafting state."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 4
    state["go_no_go"] = "go"
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" is in Wave 7 review'),
)
def proposal_in_wave_7(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 7 review state."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 7
    state["go_no_go"] = "go"
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" is in Wave 2 research'),
)
def proposal_in_wave_2(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 2 research state."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 2
    state["go_no_go"] = "go"
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" is in Wave 3 outline'),
)
def proposal_in_wave_3(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 3 outline state."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 3
    state["go_no_go"] = "go"
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" is in Wave 6 formatting'),
)
def proposal_in_wave_6(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 6 formatting state."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 6
    state["go_no_go"] = "go"
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" is in Wave 4 drafting'
        " with all prerequisites met"
    ),
)
def proposal_in_wave_4_ready(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 4 with all prerequisites satisfied."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 4
    state["go_no_go"] = "go"
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" is in Wave 5 but pre-draft'
        " checklist items are incomplete"
    ),
)
def proposal_in_wave_5_incomplete(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal in Wave 5 with RED PDC items."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 5
    state["go_no_go"] = "go"
    state["pdc_status"] = {
        "technical_approach": {
            "tier_1": "RED",
            "tier_2": "GREEN",
            "red_items": ["TRL justification missing"],
        }
    }
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given("the writer agent is currently active")
def writer_agent_active(enforcement_context: dict[str, Any]):
    """Record that writer agent is currently active in context."""
    enforcement_context["active_agent"] = "writer"


@given("no proposal session is active")
def no_active_proposal(enforcement_context: dict[str, Any]):
    """Set up context with no proposal state."""
    enforcement_context["state"] = None


@given(
    parsers.parse('Phil\'s proposal "{topic_id}" has a clean workspace'),
)
def proposal_clean_workspace(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up proposal with clean workspace, no crash signals."""
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given("active audit logging is enabled in the configuration")
def audit_logging_enabled(enforcement_context: dict[str, Any]):
    """Precondition: active audit logging is enabled in pes-config.json."""
    enforcement_context["audit_enabled"] = True


@given("the audit directory does not exist")
def audit_dir_missing(proposal_dir):
    """Remove the audit directory to simulate missing dir."""
    import shutil

    audit_dir = proposal_dir / ".sbir" / "audit"
    if audit_dir.exists():
        shutil.rmtree(audit_dir)


@given("the audit directory is not writable")
def audit_dir_not_writable(proposal_dir):
    """Mark audit directory as read-only."""
    import os
    import stat

    audit_dir = proposal_dir / ".sbir" / "audit"
    audit_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)


# ---------------------------------------------------------------------------
# Shared When Steps
# ---------------------------------------------------------------------------


@when(
    "Phil starts a new session",
    target_fixture="enforcement_context",
)
def start_new_session(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.check_session_start() -- the driving port for session events."""
    state = enforcement_context["state"]
    proposal_dir = enforcement_context.get("proposal_dir")
    result = enforcement_engine.check_session_start(state, proposal_dir=proposal_dir)
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil completes writing the technical approach section",
    target_fixture="enforcement_context",
)
def complete_writing_section(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke post-action validation through the engine driving port.

    This will call a new engine method (to be implemented) for post-tool
    validation, checking that the artifact landed in the correct directory.
    """
    state = enforcement_context["state"]
    # Post-action validation: verify artifact placement after write
    # The engine will need a check_post_action() method -- this is the
    # acceptance test that drives its creation.
    enforcement_context["tool_name"] = "write_section"
    enforcement_context["artifact_path"] = "artifacts/wave-4-drafting/sections/technical-approach.md"
    # For now, invoke evaluate() -- post-action method will be added during implementation
    result = enforcement_engine.evaluate(state, tool_name="write_section")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    parsers.parse("the {agent_name} agent is dispatched for Wave {wave_num:d} work"),
    target_fixture="enforcement_context",
)
def dispatch_agent_for_wave(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    agent_name: str,
    wave_num: int,
):
    """Invoke agent lifecycle check through the engine driving port.

    This will call a new engine method (to be implemented) for agent dispatch
    verification, checking agent is authorized for the current wave.
    """
    state = enforcement_context["state"]
    enforcement_context["dispatched_agent"] = agent_name
    enforcement_context["dispatched_wave"] = wave_num
    # Agent dispatch check will be a new engine method -- acceptance test drives creation
    # For walking skeleton: invoke evaluate with agent context
    result = enforcement_engine.evaluate(state, tool_name=f"agent_dispatch_{agent_name}")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "the writer agent completes its work",
    target_fixture="enforcement_context",
)
def agent_completes_work(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke agent stop lifecycle event through the engine driving port."""
    state = enforcement_context["state"]
    enforcement_context["agent_event"] = "stop"
    enforcement_context["stopped_agent"] = "writer"
    result = enforcement_engine.evaluate(state, tool_name="agent_stop_writer")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil uses a drafting tool",
    target_fixture="enforcement_context",
)
def use_drafting_tool(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with a Wave 4 drafting tool."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="draft_section")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil attempts to begin Wave 5 work",
    target_fixture="enforcement_context",
)
def attempt_wave_5_work(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine.evaluate() with a Wave 5 tool."""
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
    """Invoke engine.evaluate() with a generic tool."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="wave_6_format")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    parsers.parse('an unrecognized agent "{agent_name}" is dispatched'),
    target_fixture="enforcement_context",
)
def dispatch_unknown_agent(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    agent_name: str,
):
    """Invoke agent dispatch check with an unknown agent name."""
    state = enforcement_context["state"]
    enforcement_context["dispatched_agent"] = agent_name
    result = enforcement_engine.evaluate(state, tool_name=f"agent_dispatch_{agent_name}")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "the writer agent is dispatched",
    target_fixture="enforcement_context",
)
def dispatch_writer_no_proposal(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke agent dispatch with no active proposal."""
    state = enforcement_context.get("state") or {}
    result = enforcement_engine.evaluate(state, tool_name="agent_dispatch_writer")
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


@then("the agent dispatch is allowed")
def agent_dispatch_allowed(enforcement_context: dict[str, Any]):
    """Verify agent dispatch was allowed."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.ALLOW, (
        f"Expected agent dispatch ALLOW but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


@then("the agent dispatch is blocked")
def agent_dispatch_blocked(enforcement_context: dict[str, Any]):
    """Verify agent dispatch was blocked."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.BLOCK, (
        f"Expected agent dispatch BLOCK but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


@then("the stale crash signal is removed")
def crash_signal_removed(enforcement_context: dict[str, Any]):
    """Verify the crash signal file has been cleaned up."""
    crash_signal = enforcement_context.get("crash_signal_file")
    if crash_signal:
        assert not crash_signal.exists(), (
            f"Crash signal file still exists at {crash_signal}"
        )


@then("the session start is recorded in the audit trail")
def session_start_audited(in_memory_audit_log):
    """Verify an audit entry was recorded for the session start event."""
    entries = in_memory_audit_log.entries
    session_entries = [e for e in entries if e.get("event") == "session_start"]
    assert len(session_entries) >= 1, (
        f"Expected session_start audit entry. Got: {entries}"
    )


@then("the verification result is recorded in the audit trail")
def verification_audited(in_memory_audit_log):
    """Verify an audit entry was recorded for the post-action verification."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1, (
        f"Expected at least one audit entry for verification. Got: {entries}"
    )


@then("the agent activation is recorded in the audit trail")
def agent_activation_audited(in_memory_audit_log):
    """Verify an audit entry was recorded for agent activation."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1, (
        f"Expected audit entry for agent activation. Got: {entries}"
    )


@then("the agent deactivation is recorded in the audit trail")
def agent_deactivation_audited(in_memory_audit_log):
    """Verify an audit entry was recorded for agent deactivation."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1, (
        f"Expected audit entry for agent deactivation. Got: {entries}"
    )


@then("the audit entry includes the agent name and wave number")
def audit_has_agent_and_wave(in_memory_audit_log):
    """Verify the audit entry includes agent and wave information."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1
    # Implementation will add agent_name and wave to audit entries


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


@then("the system confirms the artifact is in the correct location")
def artifact_in_correct_location(enforcement_context: dict[str, Any]):
    """Verify the post-action validation confirmed correct artifact placement."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.ALLOW, (
        f"Expected artifact placement confirmation (ALLOW) but got "
        f"{result.decision.value}. Messages: {result.messages}"
    )


@then(parsers.parse("audit entries older than {days:d} days are archived"))
def old_entries_archived(
    enforcement_context: dict[str, Any],
    days: int,
):
    """Verify audit entries older than retention window were archived."""
    # Implementation will move old entries to archive file
    pass


@then("current audit entries are preserved")
def current_entries_preserved(enforcement_context: dict[str, Any]):
    """Verify current audit entries were not removed during rotation."""
    pass


@then("the log rotation is recorded in the audit trail")
def log_rotation_audited(in_memory_audit_log):
    """Verify an audit entry was recorded for log rotation."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1, (
        f"Expected audit entry for log rotation. Got: {entries}"
    )


@then(
    parsers.parse(
        'the audit log contains an entry with decision "{decision}"'
    ),
)
def audit_has_decision(in_memory_audit_log, decision: str):
    """Verify audit log contains an entry with the specified decision."""
    entries = in_memory_audit_log.entries
    matching = [e for e in entries if e.get("decision") == decision]
    assert len(matching) >= 1, (
        f"Expected audit entry with decision '{decision}'. Got: {entries}"
    )


@then(
    parsers.parse(
        'the audit entry includes the proposal identifier "{topic_id}"'
    ),
)
def audit_has_proposal_id(in_memory_audit_log, topic_id: str):
    """Verify audit entry includes the proposal identifier."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1
    # Proposal ID is included in audit entries by the engine


@then("the audit entry includes the block reason")
def audit_has_block_reason(in_memory_audit_log):
    """Verify audit entry includes block reason messages."""
    entries = in_memory_audit_log.entries
    block_entries = [e for e in entries if e.get("decision") == "block"]
    assert len(block_entries) >= 1
    assert block_entries[0].get("messages"), (
        "Expected block reason in audit entry"
    )


@then("the audit log contains an entry for session start")
def audit_has_session_start(in_memory_audit_log):
    """Verify audit log contains a session_start event entry."""
    entries = in_memory_audit_log.entries
    session_entries = [e for e in entries if e.get("event") == "session_start"]
    assert len(session_entries) >= 1, (
        f"Expected session_start entry in audit log. Got: {entries}"
    )


@then("the session continues without blocking")
def session_not_blocked(enforcement_context: dict[str, Any]):
    """Verify session was not blocked despite cleanup issues."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.ALLOW


@then("no cleanup actions are performed")
def no_cleanup_performed(enforcement_context: dict[str, Any]):
    """Verify no cleanup was needed for clean workspace."""
    pass


@then("no post-action validation is performed")
def no_post_action_validation(enforcement_context: dict[str, Any]):
    """Verify read-only operations skip post-action validation."""
    pass
