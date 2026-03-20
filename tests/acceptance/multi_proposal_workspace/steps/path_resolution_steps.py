"""Step definitions for path resolution scenarios.

Invokes through: Path resolution module (driving port -- new adapter module).
The path resolver detects workspace layout, reads active proposal pointer,
and derives state_dir and artifact_base paths.

Note: The actual path resolution module does not exist yet. Step definitions
reference the expected public interface. The software-crafter will implement
the module to satisfy these tests.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.multi_proposal_workspace.steps.workspace_common_steps import *  # noqa: F403

# Link feature files
scenarios("../walking-skeleton.feature")
scenarios("../milestone-01-path-resolution.feature")


# --- When steps ---


@when("Phil requests the workspace paths")
def resolve_workspace_paths(workspace_root: Path, path_result: dict[str, Any]):
    """Invoke path resolution module to resolve workspace paths.

    Invokes through the path resolution driving port.
    """
    # NOTE: Import will be updated when module is implemented by crafter.
    # Expected interface: resolve_workspace(workspace_root: Path) -> WorkspaceContext
    # For now, step is a placeholder that will fail with ImportError,
    # which is the expected outer-loop TDD behavior.
    try:
        from pes.adapters.workspace_resolver import resolve_workspace

        result = resolve_workspace(workspace_root)
        path_result["context"] = result
        path_result["error"] = None
    except Exception as exc:
        path_result["context"] = None
        path_result["error"] = str(exc)


@when("the workspace layout is detected")
def detect_layout(workspace_root: Path, path_result: dict[str, Any]):
    """Invoke workspace layout detection."""
    try:
        from pes.adapters.workspace_resolver import resolve_workspace

        result = resolve_workspace(workspace_root)
        path_result["context"] = result
        path_result["error"] = None
    except Exception as exc:
        path_result["context"] = None
        path_result["error"] = str(exc)


@when("Phil requests the workspace paths multiple times")
def resolve_paths_multiple(workspace_root: Path, path_result: dict[str, Any]):
    """Invoke path resolution multiple times for consistency check."""
    from pes.adapters.workspace_resolver import resolve_workspace

    results = []
    for _ in range(5):
        results.append(resolve_workspace(workspace_root))
    path_result["multiple_results"] = results


# --- Then steps: Layout ---


@then(parsers.parse('the layout is "{layout}"'))
def layout_is(path_result: dict[str, Any], layout: str):
    """Assert the detected workspace layout."""
    ctx = path_result["context"]
    assert ctx.layout == layout, f"Expected layout '{layout}', got '{ctx.layout}'"


@then("the workspace is identified as multi-proposal layout")
def layout_is_multi(path_result: dict[str, Any]):
    """Assert multi-proposal layout detected."""
    ctx = path_result["context"]
    assert ctx.layout == "multi"


@then("the workspace is identified as legacy layout")
def layout_is_legacy(path_result: dict[str, Any]):
    """Assert legacy layout detected."""
    ctx = path_result["context"]
    assert ctx.layout == "legacy"


# --- Then steps: State Directory ---


@then(parsers.parse('the state directory points to the "{topic_id}" proposal namespace'))
def state_dir_points_to_proposal(path_result: dict[str, Any], topic_id: str):
    """Assert state_dir references the expected proposal namespace."""
    ctx = path_result["context"]
    assert topic_id in str(ctx.state_dir), (
        f"Expected '{topic_id}' in state_dir '{ctx.state_dir}'"
    )


@then(parsers.parse('the state directory ends with "{suffix}"'))
def state_dir_ends_with(path_result: dict[str, Any], suffix: str):
    """Assert state_dir path ends with expected suffix."""
    ctx = path_result["context"]
    state_str = str(ctx.state_dir).replace("\\", "/")
    assert state_str.endswith(suffix), (
        f"Expected state_dir to end with '{suffix}', got '{state_str}'"
    )


@then("the state directory points to the root workspace directory")
def state_dir_is_root(path_result: dict[str, Any], sbir_dir: Path):
    """Assert state_dir is the root .sbir/ directory."""
    ctx = path_result["context"]
    assert Path(ctx.state_dir) == sbir_dir


@then("the state directory is the root workspace directory")
def state_dir_is_root_alt(path_result: dict[str, Any], sbir_dir: Path):
    """Assert state_dir is the root .sbir/ directory (alternate wording)."""
    ctx = path_result["context"]
    assert Path(ctx.state_dir) == sbir_dir


# --- Then steps: Artifact Directory ---


@then(
    parsers.parse('the artifact directory points to the "{topic_id}" artifact namespace')
)
def artifact_dir_points_to_proposal(path_result: dict[str, Any], topic_id: str):
    """Assert artifact_base references the expected proposal namespace."""
    ctx = path_result["context"]
    assert topic_id in str(ctx.artifact_base), (
        f"Expected '{topic_id}' in artifact_base '{ctx.artifact_base}'"
    )


@then(parsers.parse('the artifact base directory ends with "{suffix}"'))
def artifact_dir_ends_with(path_result: dict[str, Any], suffix: str):
    """Assert artifact_base path ends with expected suffix."""
    ctx = path_result["context"]
    artifact_str = str(ctx.artifact_base).replace("\\", "/")
    assert artifact_str.endswith(suffix), (
        f"Expected artifact_base to end with '{suffix}', got '{artifact_str}'"
    )


@then("the artifact directory points to the root artifact directory")
def artifact_dir_is_root(path_result: dict[str, Any], artifacts_dir: Path):
    """Assert artifact_base is the root artifacts/ directory."""
    ctx = path_result["context"]
    assert Path(ctx.artifact_base) == artifacts_dir


@then("the artifact base directory is the root artifact directory")
def artifact_dir_is_root_alt(path_result: dict[str, Any], artifacts_dir: Path):
    """Assert artifact_base is root (alternate wording)."""
    ctx = path_result["context"]
    assert Path(ctx.artifact_base) == artifacts_dir


# --- Then steps: Audit Directory ---


@then(parsers.parse('the audit directory ends with "{suffix}"'))
def audit_dir_ends_with(path_result: dict[str, Any], suffix: str):
    """Assert audit_dir path ends with expected suffix."""
    ctx = path_result["context"]
    audit_str = str(ctx.audit_dir).replace("\\", "/")
    assert audit_str.endswith(suffix), (
        f"Expected audit_dir to end with '{suffix}', got '{audit_str}'"
    )


# --- Then steps: Active Proposal ---


@then(parsers.parse('the active proposal ID is "{topic_id}"'))
def active_proposal_is(path_result: dict[str, Any], topic_id: str):
    """Assert the active proposal ID in the resolved context."""
    ctx = path_result["context"]
    assert ctx.active_proposal == topic_id


@then("the active proposal ID is absent")
def active_proposal_absent(path_result: dict[str, Any]):
    """Assert no active proposal in legacy context."""
    ctx = path_result["context"]
    assert ctx.active_proposal is None


# --- Then steps: Error Cases ---


@then("an error is returned indicating no active proposal is selected")
def error_no_active(path_result: dict[str, Any]):
    """Assert path resolution returned an error about missing active proposal."""
    assert path_result["error"] is not None or (
        path_result["context"] is not None
        and hasattr(path_result["context"], "error")
        and path_result["context"].error is not None
    )


@then(
    parsers.parse('the error lists available proposals "{p1}" and "{p2}"')
)
def error_lists_proposals(path_result: dict[str, Any], p1: str, p2: str):
    """Assert error message includes available proposal IDs."""
    error_text = path_result.get("error", "")
    if path_result.get("context") and hasattr(path_result["context"], "error"):
        error_text = str(path_result["context"].error)
    assert p1 in error_text, f"Expected '{p1}' in error: {error_text}"
    assert p2 in error_text, f"Expected '{p2}' in error: {error_text}"


@then("an error is returned indicating the active proposal does not exist")
def error_active_not_found(path_result: dict[str, Any]):
    """Assert error about active proposal referencing nonexistent directory."""
    error_text = path_result.get("error", "")
    if path_result.get("context") and hasattr(path_result["context"], "error"):
        error_text = str(path_result["context"].error)
    assert error_text, "Expected an error but none was returned"


@then(parsers.parse('the error lists available proposals including "{topic_id}"'))
def error_lists_proposal(path_result: dict[str, Any], topic_id: str):
    """Assert error includes at least one available proposal."""
    error_text = path_result.get("error", "")
    if path_result.get("context") and hasattr(path_result["context"], "error"):
        error_text = str(path_result["context"].error)
    assert topic_id in error_text


# --- Then steps: Consistency ---


@then("every result returns identical state and artifact directories")
def all_results_identical(path_result: dict[str, Any]):
    """Assert all repeated resolution calls return same paths."""
    results = path_result["multiple_results"]
    first = results[0]
    for r in results[1:]:
        assert str(r.state_dir) == str(first.state_dir)
        assert str(r.artifact_base) == str(first.artifact_base)


# --- Then steps: Cross-reference ---


@then(parsers.parse('the state directory and artifact directory both reference "{topic_id}"'))
def both_reference_proposal(path_result: dict[str, Any], topic_id: str):
    """Assert state_dir and artifact_base both contain the topic ID."""
    ctx = path_result["context"]
    assert topic_id in str(ctx.state_dir)
    assert topic_id in str(ctx.artifact_base)


@then("the proposals directory does not exist")
def no_proposals_directory(sbir_dir: Path):
    """Assert .sbir/proposals/ does not exist."""
    assert not (sbir_dir / "proposals").exists()
