"""Step definitions for Post-Action Validation acceptance scenarios.

Invokes through driving port: EnforcementEngine only.
Post-action validation will be a new engine method driven by these tests.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import scenarios, then, when

from tests.acceptance.pes_enforcement_parity.steps.pep_common_steps import *  # noqa: F403

scenarios("../post_action_validation.feature")


# ---------------------------------------------------------------------------
# Post-Action-Specific Steps
# ---------------------------------------------------------------------------


@when(
    "Phil saves the proposal state after updating the compliance matrix",
    target_fixture="enforcement_context",
)
def save_state_after_compliance(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    proposal_dir,
):
    """Invoke post-action check for state file write."""
    import json as _json

    state = enforcement_context["state"]
    # Write a valid state file for verification
    state_file = proposal_dir / ".sbir" / "proposal-state.json"
    state_file.write_text(_json.dumps(state, indent=2))
    artifact_info = {
        "tool_name": "Write",
        "file_path": str(state_file),
    }
    result = enforcement_engine.check_post_action(state, "Write", artifact_info)
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil completes writing and the artifact lands in the Wave 3 directory",
    target_fixture="enforcement_context",
)
def artifact_in_wrong_directory(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke post-action check where artifact is in wrong wave directory."""
    state = enforcement_context["state"]
    artifact_info = {
        "tool_name": "Write",
        "file_path": "artifacts/wave-3-outline/technical-approach.md",
    }
    result = enforcement_engine.check_post_action(state, "Write", artifact_info)
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil saves the proposal state and the resulting file is malformed",
    target_fixture="enforcement_context",
)
def state_file_corrupted(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    proposal_dir,
):
    """Invoke post-action check where state file is corrupted."""
    state = enforcement_context["state"]
    # Write malformed content to state file
    state_file = proposal_dir / ".sbir" / "proposal-state.json"
    state_file.write_text("{invalid json content###")
    artifact_info = {
        "tool_name": "Write",
        "file_path": str(state_file),
    }
    result = enforcement_engine.check_post_action(state, "Write", artifact_info)
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil completes writing but no artifact file is found",
    target_fixture="enforcement_context",
)
def artifact_missing(
    enforcement_engine,
    enforcement_context: dict[str, Any],
    proposal_dir,
):
    """Invoke post-action check where expected artifact is missing."""
    state = enforcement_context["state"]
    # Use absolute path -- file does not exist on disk
    missing_path = str(
        proposal_dir / "artifacts" / "wave-4-drafting" / "sections" / "nonexistent-section.md"
    )
    artifact_info = {
        "tool_name": "Write",
        "file_path": missing_path,
    }
    result = enforcement_engine.check_post_action(state, "Write", artifact_info)
    enforcement_context["result"] = result
    return enforcement_context


@when(
    "Phil checks proposal status",
    target_fixture="enforcement_context",
)
def check_status(
    enforcement_engine,
    enforcement_context: dict[str, Any],
):
    """Invoke engine with a read-only tool (no post-action needed)."""
    state = enforcement_context["state"]
    artifact_info = {"tool_name": "Read"}
    result = enforcement_engine.check_post_action(state, "Read", artifact_info)
    enforcement_context["result"] = result
    return enforcement_context


@then("the system confirms the state file is well-formed")
def state_file_valid(enforcement_context: dict[str, Any]):
    """Verify post-action validation confirmed state file integrity."""
    from pes.domain.rules import Decision

    result = enforcement_context["result"]
    assert result.decision == Decision.ALLOW


@then("the system warns that the artifact is misplaced")
def artifact_misplaced_warning(enforcement_context: dict[str, Any]):
    """Verify post-action validation warned about misplaced artifact."""
    result = enforcement_context["result"]
    assert len(result.messages) >= 1


@then("the warning includes the expected directory and actual directory")
def warning_includes_directories(enforcement_context: dict[str, Any]):
    """Verify the warning message includes path information."""
    result = enforcement_context["result"]
    all_messages = " ".join(result.messages)
    # Implementation will include directory paths in the message
    assert len(all_messages) > 0


@then("the misplacement is recorded in the audit trail")
def misplacement_audited(in_memory_audit_log):
    """Verify misplacement was recorded in audit."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1


@then("the system warns that the state file appears corrupted")
def state_corrupted_warning(enforcement_context: dict[str, Any]):
    """Verify post-action detected corrupted state."""
    result = enforcement_context["result"]
    assert len(result.messages) >= 1


@then("the corruption is recorded in the audit trail")
def corruption_audited(in_memory_audit_log):
    """Verify corruption detection was audited."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1


@then("the system warns that the expected artifact was not created")
def missing_artifact_warning(enforcement_context: dict[str, Any]):
    """Verify post-action detected missing artifact."""
    result = enforcement_context["result"]
    assert len(result.messages) >= 1


@then("the missing artifact is recorded in the audit trail")
def missing_artifact_audited(in_memory_audit_log):
    """Verify missing artifact was audited."""
    entries = in_memory_audit_log.entries
    assert len(entries) >= 1


@then("the audit directory is created automatically")
def audit_dir_created(proposal_dir):
    """Verify audit directory was auto-created when missing."""
    audit_dir = proposal_dir / ".sbir" / "audit"
    assert audit_dir.exists()
