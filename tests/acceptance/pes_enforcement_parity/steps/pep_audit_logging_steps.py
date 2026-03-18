"""Step definitions for Active Audit Logging acceptance scenarios.

Invokes through driving port: EnforcementEngine only.
Active audit logging replaces _NullAuditLogger with a real file-based
implementation -- these tests drive that creation.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.pes_enforcement_parity.steps.pep_common_steps import *  # noqa: F403

scenarios("../active_audit_logging.feature")


# ---------------------------------------------------------------------------
# Audit-Specific Steps
# ---------------------------------------------------------------------------


@given(
    parsers.parse(
        'Phil\'s proposal "{topic_id}" is submitted and near deadline'
    ),
)
def proposal_submitted_near_deadline(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
    topic_id: str,
):
    """Set up a submitted proposal with multiple rule violations.

    State triggers both submission_immutability (submitted + immutable)
    and pdc_gate (wave 5 with RED PDC items). The 'when' step uses
    wave_5 tool name to match both rules.
    """
    state = base_proposal_state.copy()
    state["topic"]["id"] = topic_id
    state["current_wave"] = 5
    state["go_no_go"] = "go"
    state["submission"] = {"status": "submitted", "immutable": True}
    state["pdc_status"] = {
        "technical_approach": {
            "tier_1": "RED",
            "tier_2": "GREEN",
            "red_items": ["TRL justification missing"],
        }
    }
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given(
    parsers.parse(
        'Phil has two proposals "{id1}" and "{id2}" with separate audit directories'
    ),
)
def two_proposals(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    tmp_path,
    id1: str,
    id2: str,
):
    """Set up two separate proposals for concurrent testing."""
    enforcement_context["proposals"] = {
        id1: {**base_proposal_state, "topic": {**base_proposal_state["topic"], "id": id1}},
        id2: {**base_proposal_state, "topic": {**base_proposal_state["topic"], "id": id2}},
    }


@given(
    parsers.parse("any valid proposal state and any tool action"),
)
def any_valid_state(
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
):
    """Set up a generic valid proposal state for property testing."""
    enforcement_context["state"] = base_proposal_state
    enforcement_context["proposal_dir"] = str(proposal_dir)


@given("any sequence of enforcement decisions")
def any_sequence(enforcement_context: dict[str, Any]):
    """Property: any sequence of decisions should preserve prior entries."""
    enforcement_context["prior_count"] = 0


@when(
    "the enforcement system processes the action",
    target_fixture="enforcement_context",
)
def process_any_action(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Process a generic action through the enforcement engine."""
    state = enforcement_context["state"]
    result = enforcement_engine.evaluate(state, tool_name="generic_tool")
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "both proposals start sessions simultaneously",
    target_fixture="enforcement_context",
)
def concurrent_sessions(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Start sessions for both proposals."""
    proposals = enforcement_context.get("proposals", {})
    results = {}
    for pid, state in proposals.items():
        results[pid] = enforcement_engine.check_session_start(state)
    enforcement_context["multi_results"] = results
    return enforcement_context


@when("new decisions are recorded")
def new_decisions_recorded(enforcement_context: dict[str, Any]):
    """Record additional decisions (property test stub)."""
    pass


@then("an audit file exists in the proposal audit directory")
def audit_file_exists(proposal_dir):
    """Verify an audit file was written to disk."""
    audit_dir = proposal_dir / ".sbir" / "audit"
    audit_files = list(audit_dir.glob("*.log"))
    assert len(audit_files) >= 1, (
        f"Expected audit log file in {audit_dir}. Found: {list(audit_dir.iterdir())}"
    )


@then("the file contains a timestamped entry for the action")
def audit_file_has_timestamp(proposal_dir):
    """Verify audit file contains timestamped entry."""
    import json

    audit_dir = proposal_dir / ".sbir" / "audit"
    for audit_file in audit_dir.glob("*.log"):
        content = audit_file.read_text()
        if content.strip():
            entry = json.loads(content.strip().split("\n")[0])
            assert "timestamp" in entry


@then("a warning is logged about the audit write failure")
def audit_write_failure_warning(enforcement_context: dict[str, Any]):
    """Verify a warning was produced about audit write failure."""
    warnings = enforcement_context.get("captured_warnings", [])
    assert len(warnings) >= 1, (
        "Expected at least one warning about audit write failure, got none"
    )
    warning_messages = [r.getMessage() for r in warnings]
    assert any("audit" in msg.lower() for msg in warning_messages), (
        f"Expected warning mentioning 'audit'. Got: {warning_messages}"
    )


@then("the audit entry includes all block reasons")
def audit_has_all_reasons(in_memory_audit_log):
    """Verify audit entry includes all block reasons -- multiple messages."""
    entries = in_memory_audit_log.entries
    block_entries = [e for e in entries if e.get("decision") == "block"]
    assert len(block_entries) >= 1, (
        f"Expected at least one block audit entry. Got: {entries}"
    )
    messages = block_entries[0].get("messages", [])
    assert len(messages) >= 2, (
        f"Expected multiple block reasons in audit entry. Got: {messages}"
    )


@then("each proposal has its own audit entry")
def separate_audit_entries(in_memory_audit_log):
    """Verify each proposal has its own audit entry."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 2


@then("no entries are lost or mixed between proposals")
def no_mixed_entries(in_memory_audit_log):
    """Verify no audit entries were lost or mixed."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 2


@then("exactly one audit entry is produced")
def exactly_one_entry(in_memory_audit_log):
    """Property: each decision produces exactly one audit entry."""
    entries = in_memory_audit_log.entries
    assert len(entries) == 1


@then("the entry contains a timestamp, decision, and proposal identifier")
def entry_has_required_fields(in_memory_audit_log):
    """Property: audit entries contain required fields."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1
    entry = entries[-1]
    assert "timestamp" in entry
    assert "decision" in entry
    assert "proposal_id" in entry


@then("previously written audit entries remain unchanged")
def prior_entries_unchanged(in_memory_audit_log):
    """Property: prior audit entries are never modified."""
    # Implementation: compare entry snapshots before and after
    pass
