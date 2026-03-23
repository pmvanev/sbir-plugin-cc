"""Step definitions for diff computation scenarios.

Invokes through: RigorService diff computation (driving port).
Tests per-role diff, behavioral parameter diff, and edge cases.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pytest_bdd import parsers, scenarios, then, when

from tests.acceptance.rigor_profile.steps.rigor_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-05-diff-computation.feature")


# --- When steps ---


@when(
    parsers.parse('a diff is computed from "{from_p}" to "{to_p}"'),
    target_fixture="diff_result",
)
def compute_diff(from_p: str, to_p: str) -> dict[str, Any]:
    """Invoke DiffComputer to compute changes between two profiles."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor import DiffComputer
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=Path("/tmp"),
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        diff = service.compute_diff(from_profile=from_p, to_profile=to_p)
        result["diff"] = diff
        result["error"] = None
    except Exception as exc:
        result["diff"] = None
        result["error"] = str(exc)
        result["error_type"] = type(exc).__name__
    return result


# --- Then steps ---


@then(
    parsers.parse(
        'the diff includes the {role} role changing from "{from_t}" to "{to_t}"'
    )
)
def diff_includes_role_change(
    diff_result: dict[str, Any], role: str, from_t: str, to_t: str
):
    """Verify the diff includes a specific role tier change."""
    diff = diff_result["diff"]
    assert diff is not None, f"No diff -- error: {diff_result.get('error')}"
    role_diff = diff.get("agent_roles", {}).get(role, {})
    assert role_diff.get("from") == from_t, (
        f"Role '{role}' from: expected '{from_t}', got '{role_diff.get('from')}'"
    )
    assert role_diff.get("to") == to_t, (
        f"Role '{role}' to: expected '{to_t}', got '{role_diff.get('to')}'"
    )


@then(
    parsers.parse(
        "the diff includes review passes changing from {from_v:d} to {to_v:d}"
    )
)
def diff_includes_review_change(
    diff_result: dict[str, Any], from_v: int, to_v: int
):
    """Verify the diff includes review pass count change."""
    diff = diff_result["diff"]
    review_diff = diff.get("review_passes", {})
    assert review_diff.get("from") == from_v
    assert review_diff.get("to") == to_v


@then(
    parsers.parse(
        "the diff includes critique iterations changing from {from_v:d} to {to_v:d}"
    )
)
def diff_includes_critique_change(
    diff_result: dict[str, Any], from_v: int, to_v: int
):
    """Verify the diff includes critique iteration change."""
    diff = diff_result["diff"]
    critique_diff = diff.get("critique_max_iterations", {})
    assert critique_diff.get("from") == from_v
    assert critique_diff.get("to") == to_v


@then("the diff contains zero changes")
def diff_has_no_changes(diff_result: dict[str, Any]):
    """Verify the diff is empty when comparing same profile."""
    diff = diff_result["diff"]
    assert diff is not None
    # All sub-diffs should be empty or not present
    agent_roles = diff.get("agent_roles", {})
    assert len(agent_roles) == 0, f"Expected no role changes, got {agent_roles}"


@then(parsers.parse("the diff does not include the {role} role"))
def diff_excludes_role(diff_result: dict[str, Any], role: str):
    """Verify the diff does not contain changes for the specified role."""
    diff = diff_result["diff"]
    agent_roles = diff.get("agent_roles", {})
    assert role not in agent_roles, (
        f"Role '{role}' should not be in diff but found: {agent_roles[role]}"
    )


@then("the diff operation fails with an invalid profile error")
def diff_fails_invalid(diff_result: dict[str, Any]):
    """Verify the diff operation failed with invalid profile."""
    assert diff_result["error"] is not None, "Expected error but none occurred"
