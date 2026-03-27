"""Common steps shared across all PES Figure Pipeline acceptance features.

These steps handle shared preconditions (config loading, state setup,
tool_context construction) and shared assertions (BLOCK/ALLOW decisions,
message content, audit trail).

Invokes through driving port: EnforcementEngine.evaluate() only.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then, when


# ---------------------------------------------------------------------------
# Shared Given Steps -- Proposal Setup
# ---------------------------------------------------------------------------


@given(
    parsers.parse('an active proposal for topic "{topic_id}" at Wave 5'),
)
def active_proposal_wave5(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 5 for the given topic."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 5
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-5-visuals"


@given(
    parsers.parse(
        'an active proposal for topic "{topic_id}" at Wave 5 with multi-proposal workspace'
    ),
)
def active_proposal_multi_workspace(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 5 with multi-proposal path layout."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 5
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-5-visuals"


@given("an active proposal at Wave 5 with legacy single-proposal workspace")
def active_proposal_legacy_workspace(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
):
    """Set up proposal state at Wave 5 with legacy single-proposal path layout."""
    state = base_proposal_state.copy()
    state["current_wave"] = 5
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = "artifacts/wave-5-visuals"


@given(
    parsers.parse('an active proposal for topic "{topic_id}" at Wave 4'),
)
def active_proposal_wave4(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Set up proposal state at Wave 4 (not in visual assets phase)."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 4
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-4-drafting"


@given(
    parsers.parse(
        'Dr. Moreno\'s proposal "{topic_id}" is at Wave 5 (visual assets)'
    ),
)
def moreno_proposal_wave5(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    topic_id: str,
):
    """Dr. Moreno's proposal at Wave 5 for walking skeleton."""
    state = base_proposal_state.copy()
    state["topic"] = {**state["topic"], "id": topic_id}
    state["proposal_id"] = f"test-uuid-{topic_id.lower()}"
    state["current_wave"] = 5
    enforcement_context["state"] = state
    enforcement_context["artifact_dir"] = f"artifacts/{topic_id.lower()}/wave-5-visuals"


# ---------------------------------------------------------------------------
# Shared Given Steps -- Artifact Presence
# ---------------------------------------------------------------------------


@given("the visual assets directory contains a figure specification plan")
def visual_dir_has_specs(enforcement_context: dict[str, Any]):
    """Mark figure-specs.md as present in the artifact directory."""
    artifacts = enforcement_context.setdefault("artifacts_present", [])
    if "figure-specs.md" not in artifacts:
        artifacts.append("figure-specs.md")


@given("the visual assets directory does not contain a figure specification plan")
def visual_dir_missing_specs(enforcement_context: dict[str, Any]):
    """Ensure figure-specs.md is NOT present in the artifact directory."""
    artifacts = enforcement_context.setdefault("artifacts_present", [])
    if "figure-specs.md" in artifacts:
        artifacts.remove("figure-specs.md")


@given("no figure specification plan has been created in the visual assets directory")
def no_specs_created(enforcement_context: dict[str, Any]):
    """Walking skeleton: no figure-specs.md exists."""
    enforcement_context.setdefault("artifacts_present", [])
    if "figure-specs.md" in enforcement_context["artifacts_present"]:
        enforcement_context["artifacts_present"].remove("figure-specs.md")


@given("the visual assets directory contains a style profile")
def visual_dir_has_style(enforcement_context: dict[str, Any]):
    """Mark style-profile.yaml as present in the artifact directory."""
    artifacts = enforcement_context.setdefault("artifacts_present", [])
    if "style-profile.yaml" not in artifacts:
        artifacts.append("style-profile.yaml")


@given("the visual assets directory does not contain a style profile")
def visual_dir_missing_style(enforcement_context: dict[str, Any]):
    """Ensure style-profile.yaml is NOT present in the artifact directory."""
    artifacts = enforcement_context.setdefault("artifacts_present", [])
    if "style-profile.yaml" in artifacts:
        artifacts.remove("style-profile.yaml")


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
# Shared Given Steps -- State Markers
# ---------------------------------------------------------------------------


@given("the proposal state does not contain a style analysis skip marker")
def no_style_skip_marker(enforcement_context: dict[str, Any]):
    """Ensure style_analysis_skipped is not set in proposal state."""
    state = enforcement_context.get("state", {})
    state.pop("style_analysis_skipped", None)


@given("the proposal state contains a style analysis skip marker")
def has_style_skip_marker(enforcement_context: dict[str, Any]):
    """Set style_analysis_skipped: true in proposal state."""
    enforcement_context["state"]["style_analysis_skipped"] = True


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
    """Build tool_context dict from enforcement_context state."""
    return {
        "file_path": file_path,
        "artifacts_present": list(enforcement_context.get("artifacts_present", [])),
    }


@when(
    "the formatter agent attempts to write a figure file to the visual assets directory",
    target_fixture="enforcement_context",
)
def attempt_write_figure_walking_skeleton(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Walking skeleton: attempt to write an SVG figure file."""
    artifact_dir = enforcement_context["artifact_dir"]
    file_path = f"{artifact_dir}/figure-1-system-arch.svg"
    tool_context = _build_tool_context(enforcement_context, file_path)
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="Write", tool_context=tool_context)
    enforcement_context["result"] = result
    enforcement_context["tool_context"] = tool_context
    return enforcement_context


@when(
    parsers.parse('the formatter agent attempts to Write "{file_path}"'),
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
    parsers.parse('the formatter agent attempts to Edit "{file_path}"'),
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
    parsers.parse('the formatter agent uses Read on "{file_path}"'),
    target_fixture="enforcement_context",
)
def attempt_read(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    file_path: str,
):
    """Invoke engine.evaluate() with Read tool (should never be blocked by figure gates)."""
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


@then("the block reason explains that figure specifications must be created first")
def block_reason_explains_specs(enforcement_context: dict[str, Any]):
    """Walking skeleton: verify block message mentions figure specifications."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages).lower()
    assert "figure" in all_messages and "spec" in all_messages, (
        f"Expected block message to mention figure specifications. Got: {result.messages}"
    )


# ---------------------------------------------------------------------------
# Shared Then Steps -- Evaluator Non-interference
# ---------------------------------------------------------------------------


@then("the figure pipeline gate is not evaluated")
def figure_gate_not_evaluated(
    enforcement_context: dict[str, Any],
    in_memory_audit_log,
):
    """Verify the figure pipeline gate did not trigger for this operation.

    When the file_path does not target wave-5-visuals/, the figure pipeline
    evaluator should not trigger. We verify by checking the result has no
    figure-pipeline-related block messages.
    """
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages).lower()
    assert "figure" not in all_messages, (
        f"Figure pipeline gate should not have been evaluated. Messages: {result.messages}"
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
    """Verify audit log contains an entry referencing the specified rule_id."""
    all_entries_text = str(in_memory_audit_log.entries)
    assert rule_id in all_entries_text, (
        f"Expected rule_id '{rule_id}' in audit entries. "
        f"Entries: {in_memory_audit_log.entries}"
    )
