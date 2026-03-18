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
    pes_config_path,
    tmp_path,
    id1: str,
    id2: str,
):
    """Set up two separate proposals with isolated audit directories and engines."""
    from pes.adapters.file_audit_adapter import FileAuditAdapter
    from pes.adapters.json_rule_adapter import JsonRuleAdapter
    from pes.domain.engine import EnforcementEngine

    proposals = {}
    engines = {}
    audit_dirs = {}
    for pid in (id1, id2):
        state = {**base_proposal_state, "topic": {**base_proposal_state["topic"], "id": pid}}
        audit_dir = tmp_path / pid / ".sbir" / "audit"
        audit_dir.mkdir(parents=True)
        adapter = FileAuditAdapter(str(audit_dir))
        rule_loader = JsonRuleAdapter(str(pes_config_path))
        engine = EnforcementEngine(rule_loader, adapter)
        proposals[pid] = state
        engines[pid] = engine
        audit_dirs[pid] = audit_dir

    enforcement_context["proposals"] = proposals
    enforcement_context["engines"] = engines
    enforcement_context["audit_dirs"] = audit_dirs


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
def any_sequence(
    enforcement_engine,
    base_proposal_state: dict[str, Any],
    enforcement_context: dict[str, Any],
    proposal_dir,
):
    """Property: record initial decisions and snapshot them for later comparison."""
    import copy

    state = base_proposal_state.copy()
    enforcement_context["state"] = state
    enforcement_context["proposal_dir"] = str(proposal_dir)
    # Record initial decisions
    enforcement_engine.evaluate(state, tool_name="tool_a")
    enforcement_engine.evaluate(state, tool_name="tool_b")
    enforcement_context["prior_count"] = 2


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
    enforcement_context: dict[str, Any],
):
    """Start sessions for both proposals using their isolated engines."""
    proposals = enforcement_context["proposals"]
    engines = enforcement_context["engines"]
    results = {}
    for pid, state in proposals.items():
        results[pid] = engines[pid].check_session_start(state)
    enforcement_context["multi_results"] = results
    return enforcement_context


@when("new decisions are recorded")
def new_decisions_recorded(
    enforcement_engine,
    in_memory_audit_log,
    enforcement_context: dict[str, Any],
):
    """Record additional decisions and snapshot prior entries for comparison."""
    import copy

    # Snapshot the entries written so far (before new decisions)
    enforcement_context["snapshot"] = copy.deepcopy(in_memory_audit_log.entries)

    # Record new decisions
    state = enforcement_context["state"]
    enforcement_engine.evaluate(state, tool_name="tool_c")
    enforcement_engine.evaluate(state, tool_name="tool_d")


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
def separate_audit_entries(enforcement_context: dict[str, Any]):
    """Verify each proposal has its own audit file with its own entry."""
    import json

    audit_dirs = enforcement_context["audit_dirs"]
    for pid, audit_dir in audit_dirs.items():
        log_files = list(audit_dir.glob("*.log"))
        assert len(log_files) >= 1, (
            f"Expected audit log file for proposal {pid} in {audit_dir}"
        )
        content = log_files[0].read_text().strip()
        assert content, f"Audit file for {pid} is empty"
        entry = json.loads(content.split("\n")[0])
        assert entry.get("proposal_id") is not None, (
            f"Audit entry for {pid} missing proposal_id"
        )


@then("no entries are lost or mixed between proposals")
def no_mixed_entries(enforcement_context: dict[str, Any]):
    """Verify no audit entries were lost or mixed between proposal files."""
    import json

    audit_dirs = enforcement_context["audit_dirs"]
    proposals = enforcement_context["proposals"]
    for pid, audit_dir in audit_dirs.items():
        log_file = list(audit_dir.glob("*.log"))[0]
        lines = log_file.read_text().strip().split("\n")
        for line in lines:
            entry = json.loads(line)
            # Entry proposal_id should match state's proposal_id for this proposal
            expected_pid = proposals[pid].get("proposal_id")
            assert entry["proposal_id"] == expected_pid, (
                f"Cross-contamination: entry in {pid}'s audit has "
                f"proposal_id={entry['proposal_id']}, expected {expected_pid}"
            )


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
def prior_entries_unchanged(
    in_memory_audit_log,
    enforcement_context: dict[str, Any],
):
    """Property: prior audit entries are never modified after new writes."""
    snapshot = enforcement_context["snapshot"]
    current = in_memory_audit_log.entries

    # There should be more entries now than in the snapshot
    assert len(current) > len(snapshot), (
        f"Expected new entries after snapshot. Snapshot: {len(snapshot)}, "
        f"Current: {len(current)}"
    )

    # Every entry from the snapshot must be identical in the current list
    for i, prior_entry in enumerate(snapshot):
        assert current[i] == prior_entry, (
            f"Entry at index {i} was modified. "
            f"Before: {prior_entry}, After: {current[i]}"
        )
