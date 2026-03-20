"""Step definitions for context switching scenarios.

Invokes through: Switch service (driving port).
Handles proposal context switching, validation, and idempotency.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.multi_proposal_workspace.conftest import make_proposal_state
from tests.acceptance.multi_proposal_workspace.steps.workspace_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-03-context-switching.feature")


# --- Given steps ---


@given(
    parsers.parse('the proposal "{topic_id}" is marked as completed'),
)
def proposal_completed(proposals_dir: Path, topic_id: str):
    """Mark a proposal as completed (wave 8 done)."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    data["waves"]["8"]["status"] = "completed"
    state_path.write_text(json.dumps(data, indent=2))


# --- When steps ---


@when(parsers.parse('Phil switches to proposal "{topic_id}"'))
def switch_proposal(
    workspace_root: Path,
    operation_result: dict[str, Any],
    topic_id: str,
):
    """Invoke switch service to change active proposal.

    Invokes through the switch driving port.
    """
    try:
        from pes.adapters.proposal_switch import switch_active_proposal

        result = switch_active_proposal(workspace_root, topic_id)
        operation_result["success"] = True
        operation_result["result"] = result
        operation_result["error"] = None
    except Exception as exc:
        operation_result["success"] = False
        operation_result["result"] = None
        operation_result["error"] = str(exc)


@when("Phil attempts to switch proposals")
def attempt_switch_legacy(
    workspace_root: Path,
    operation_result: dict[str, Any],
):
    """Attempt switch in a legacy workspace."""
    try:
        from pes.adapters.proposal_switch import switch_active_proposal

        result = switch_active_proposal(workspace_root, "any-id")
        operation_result["success"] = True
        operation_result["result"] = result
        operation_result["error"] = None
    except Exception as exc:
        operation_result["success"] = False
        operation_result["result"] = None
        operation_result["error"] = str(exc)


# --- Then steps ---


@then("the switch reports that the proposal is already active")
def switch_already_active(operation_result: dict[str, Any]):
    """Assert switch result indicates already-active status."""
    result = operation_result["result"]
    assert result is not None
    assert result.already_active is True


@then(parsers.parse('an error is returned indicating proposal "{topic_id}" was not found'))
def error_proposal_not_found(operation_result: dict[str, Any], topic_id: str):
    """Assert error mentions the missing proposal ID."""
    assert not operation_result["success"]
    assert topic_id in operation_result["error"]


@then(parsers.parse('the active proposal file still contains "{topic_id}"'))
def active_file_still_has(active_proposal_path: Path, topic_id: str):
    """Assert active-proposal file was not changed."""
    assert active_proposal_path.read_text().strip() == topic_id


@then("an error is returned indicating switching requires multi-proposal layout")
def error_requires_multi(operation_result: dict[str, Any]):
    """Assert error about legacy workspace not supporting switch."""
    assert not operation_result["success"]
    error_lower = operation_result["error"].lower()
    assert "legacy" in error_lower or "multi" in error_lower or "switch" in error_lower
