"""Common steps shared across all PES Outline Gate acceptance features.

These steps handle shared preconditions (config loading, state setup,
tool_context construction) and shared assertions (BLOCK/ALLOW decisions,
message content, audit trail).

Invokes through driving port: EnforcementEngine.evaluate() only.

Key difference from figure pipeline and writing style gates:
- tool_context includes outline_artifacts_present for cross-directory check
- No global_artifacts_present (not a global artifact)
- No skip marker steps (outline is mandatory)
- No prerequisite creation exception steps (writer never writes to wave-3-outline)
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then, when


# ---------------------------------------------------------------------------
# Shared Given Steps -- Proposal Setup
# ---------------------------------------------------------------------------


@given(
    parsers.parse('an active proposal for topic "{topic_id}" at Wave 4'),
)
def active_proposal_wave4(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 4 for the given topic."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 4
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-4-drafting"


@given(
    parsers.parse(
        'an active proposal for topic "{topic_id}" at Wave 4 with multi-proposal workspace'
    ),
)
def active_proposal_multi_workspace(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 4 with multi-proposal path layout."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 4
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-4-drafting"


@given("an active proposal at Wave 4 with legacy single-proposal workspace")
def active_proposal_legacy_workspace(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
):
    """Set up proposal state at Wave 4 with legacy single-proposal path layout."""
    state = base_proposal_state.copy()
    state["current_wave"] = 4
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = "artifacts/wave-4-drafting"


@given(
    parsers.parse('an active proposal for topic "{topic_id}" at Wave 3'),
)
def active_proposal_wave3(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 3 (not in drafting phase)."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 3
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-3-outline"


@given(
    parsers.parse('an active proposal for topic "{topic_id}" at Wave 5'),
)
def active_proposal_wave5(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 5 (visual assets, not drafting)."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 5
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-5-visuals"


@given(
    parsers.parse(
        'Dr. Moreno\'s proposal "{topic_id}" is at Wave 4 (drafting)'
    ),
)
def moreno_proposal_wave4(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Dr. Moreno's proposal at Wave 4 for walking skeleton."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 4
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-4-drafting"


# ---------------------------------------------------------------------------
# Shared Given Steps -- Outline Artifact Presence
# ---------------------------------------------------------------------------


@given("the outline directory contains a proposal outline")
def outline_dir_has_outline(enforcement_context: dict[str, Any]):
    """Mark proposal-outline.md as present in the sibling outline directory."""
    artifacts = enforcement_context.setdefault("outline_artifacts_present", [])
    if "proposal-outline.md" not in artifacts:
        artifacts.append("proposal-outline.md")


@given("the outline directory does not contain a proposal outline")
def outline_dir_missing_outline(enforcement_context: dict[str, Any]):
    """Ensure proposal-outline.md is NOT present in the sibling outline directory."""
    artifacts = enforcement_context.setdefault("outline_artifacts_present", [])
    if "proposal-outline.md" in artifacts:
        artifacts.remove("proposal-outline.md")


@given("no approved outline has been created in the outline directory")
def no_outline_created(enforcement_context: dict[str, Any]):
    """Walking skeleton: no proposal-outline.md exists in wave-3-outline."""
    enforcement_context.setdefault("outline_artifacts_present", [])
    if "proposal-outline.md" in enforcement_context["outline_artifacts_present"]:
        enforcement_context["outline_artifacts_present"].remove("proposal-outline.md")


@given(
    parsers.parse(
        '"{file_path}" exists from a previous session'
    ),
)
def file_exists_previous_session(
    enforcement_context: dict[str, Any],
    file_path: str,
):
    """Mark that a file exists from a prior session (relevant for Edit operations)."""
    # No state change needed -- the tool_context file_path is what matters.
    # This step documents intent: the file already exists on disk.
    pass


# ---------------------------------------------------------------------------
# Shared Given Steps -- Config Loading
# ---------------------------------------------------------------------------


@given("the enforcement rules are loaded from the standard configuration")
def enforcement_rules_loaded(enforcement_engine):
    """Precondition satisfied by conftest fixtures wiring real config."""
    # The enforcement_engine fixture already loads real pes-config.json
    # through JsonRuleAdapter. This step documents intent.
    pass


# ---------------------------------------------------------------------------
# Shared When Steps
# ---------------------------------------------------------------------------


def _build_tool_context(enforcement_context: dict[str, Any], file_path: str) -> dict[str, Any]:
    """Build tool_context dict from enforcement_context state.

    Includes outline_artifacts_present for cross-directory prerequisite check.
    No global_artifacts_present needed (outline is a local cross-directory artifact).
    """
    return {
        "file_path": file_path,
        "outline_artifacts_present": list(
            enforcement_context.get("outline_artifacts_present", [])
        ),
    }


@when(
    "the writer agent attempts to write a draft section to the drafting directory",
    target_fixture="enforcement_context",
)
def attempt_write_section_walking_skeleton(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Walking skeleton: attempt to write a section draft file."""
    artifact_dir = enforcement_context["artifact_dir"]
    file_path = f"{artifact_dir}/section-1-technical-approach.md"
    tool_context = _build_tool_context(enforcement_context, file_path)
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="Write", tool_context=tool_context)
    enforcement_context["result"] = result
    enforcement_context["tool_context"] = tool_context
    return enforcement_context


@when(
    parsers.parse('the writer agent attempts to Write "{file_path}"'),
    target_fixture="enforcement_context",
)
def attempt_write(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    file_path: str,
):
    """Invoke engine.evaluate() with Write tool and the target file path."""
    tool_context = _build_tool_context(enforcement_context, file_path)
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="Write", tool_context=tool_context)
    enforcement_context["result"] = result
    enforcement_context["tool_context"] = tool_context
    return enforcement_context


@when(
    parsers.parse('the writer agent attempts to Edit "{file_path}"'),
    target_fixture="enforcement_context",
)
def attempt_edit(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    file_path: str,
):
    """Invoke engine.evaluate() with Edit tool and the target file path."""
    tool_context = _build_tool_context(enforcement_context, file_path)
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="Edit", tool_context=tool_context)
    enforcement_context["result"] = result
    enforcement_context["tool_context"] = tool_context
    return enforcement_context


@when(
    parsers.parse('the writer agent uses Read on "{file_path}"'),
    target_fixture="enforcement_context",
)
def attempt_read(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    file_path: str,
):
    """Invoke engine.evaluate() with Read tool (should never be blocked by outline gate)."""
    tool_context = _build_tool_context(enforcement_context, file_path)
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="Read", tool_context=tool_context)
    enforcement_context["result"] = result
    enforcement_context["tool_context"] = tool_context
    return enforcement_context


# ---------------------------------------------------------------------------
# Shared Then Steps -- Decision Assertions
# ---------------------------------------------------------------------------


@then("PES returns decision BLOCK")
def decision_is_block(enforcement_context: dict[str, Any]):
    """Verify enforcement returned a BLOCK decision."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.BLOCK, (
        f"Expected BLOCK but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


@then("PES returns decision ALLOW")
def decision_is_allow(enforcement_context: dict[str, Any]):
    """Verify enforcement returned an ALLOW decision."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.ALLOW, (
        f"Expected ALLOW but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


@then("the action is blocked")
def action_is_blocked(enforcement_context: dict[str, Any]):
    """Verify enforcement returned a BLOCK decision (walking skeleton wording)."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.BLOCK, (
        f"Expected BLOCK but got {result.decision.value}. "
        f"Messages: {result.messages}"
    )


# ---------------------------------------------------------------------------
# Shared Then Steps -- Message Content
# ---------------------------------------------------------------------------


@then(
    parsers.parse('the block message includes "{expected_text}"'),
)
def block_message_includes(
    enforcement_context: dict[str, Any],
    expected_text: str,
):
    """Verify the block message contains the expected text."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages)
    assert expected_text in all_messages, (
        f"Expected '{expected_text}' in block messages. Got: {result.messages}"
    )


@then("the block reason explains that the proposal outline must be completed first")
def block_reason_explains_outline(enforcement_context: dict[str, Any]):
    """Walking skeleton: verify block message mentions proposal outline."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages).lower()
    assert "outline" in all_messages, (
        f"Expected block message to mention proposal outline. Got: {result.messages}"
    )


# ---------------------------------------------------------------------------
# Shared Then Steps -- Evaluator Non-interference
# ---------------------------------------------------------------------------


@then("the outline gate is not evaluated")
def outline_gate_not_evaluated(
    enforcement_context: dict[str, Any],
    in_memory_audit_log,
):
    """Verify the outline gate did not trigger for this operation.

    When the file_path does not target wave-4-drafting/, the outline gate
    evaluator should not trigger. We verify by checking the result has no
    outline-gate-related block messages.
    """
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages).lower()
    assert "outline" not in all_messages, (
        f"Outline gate should not have been evaluated. Messages: {result.messages}"
    )


# ---------------------------------------------------------------------------
# Shared Then Steps -- Audit Trail
# ---------------------------------------------------------------------------


@then("the block is recorded in the audit trail")
def block_recorded_in_audit(in_memory_audit_log):
    """Walking skeleton: verify audit log captured the block event."""
    evaluate_entries = [
        e for e in in_memory_audit_log.entries
        if e.get("event") == "evaluate"
    ]
    assert len(evaluate_entries) > 0, "No evaluate entries in audit log"
    last_entry = evaluate_entries[-1]
    assert last_entry["decision"] == "block", (
        f"Expected audit decision 'block', got '{last_entry['decision']}'"
    )


@then(
    parsers.parse(
        'an audit entry is recorded with event "{event}" and decision "{decision}"'
    ),
)
def audit_entry_with_event_and_decision(
    in_memory_audit_log,
    event: str,
    decision: str,
):
    """Verify audit log contains an entry with the specified event and decision."""
    matching = [
        e for e in in_memory_audit_log.entries
        if e.get("event") == event and e.get("decision") == decision
    ]
    assert len(matching) > 0, (
        f"No audit entry with event='{event}' and decision='{decision}'. "
        f"Entries: {in_memory_audit_log.entries}"
    )


@then(
    parsers.parse('the audit entry includes the rule_id "{rule_id}"'),
)
def audit_entry_includes_rule_id(
    in_memory_audit_log,
    rule_id: str,
):
    """Verify audit log contains an entry whose messages identify the given rule.

    Map rule_id to expected message fragments to verify rule participation.
    """
    rule_message_markers: dict[str, str] = {
        "drafting-requires-outline": "proposal-outline.md",
    }
    expected_marker = rule_message_markers.get(rule_id, rule_id)
    block_entries = [
        e for e in in_memory_audit_log.entries
        if e.get("decision") == "block"
    ]
    assert len(block_entries) > 0, (
        f"No block entries in audit log to check for rule_id '{rule_id}'. "
        f"Entries: {in_memory_audit_log.entries}"
    )
    all_messages = " ".join(
        msg for entry in block_entries for msg in entry.get("messages", [])
    )
    assert expected_marker in all_messages, (
        f"Expected marker '{expected_marker}' (for rule_id '{rule_id}') in block messages. "
        f"Got: {all_messages}"
    )
