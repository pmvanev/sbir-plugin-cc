"""Step definitions for completed proposal lifecycle scenarios.

Invokes through: Lifecycle management service (driving port).
Handles completion detection, auto-switch logic, and status classification.
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
scenarios("../milestone-04-lifecycle.feature")


# --- Given steps ---


@given(parsers.parse('the proposal "{topic_id}" is marked as active'))
def proposal_is_active(proposals_dir: Path, topic_id: str):
    """Ensure proposal state indicates active status."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    data["waves"]["8"]["status"] = "not_started"
    data["go_no_go"] = "pending"
    data["archived"] = False
    state_path.write_text(json.dumps(data, indent=2))


@given("both proposals are marked as completed")
def both_completed(proposals_dir: Path):
    """Mark all proposals as completed."""
    for state_path in proposals_dir.glob("*/proposal-state.json"):
        data = json.loads(state_path.read_text())
        data["waves"]["8"]["status"] = "completed"
        state_path.write_text(json.dumps(data, indent=2))


@given(parsers.parse('proposals "{p1}" and "{p2}" are marked as active'))
def two_proposals_active(proposals_dir: Path, p1: str, p2: str):
    """Ensure two specific proposals are in active state."""
    for pid in (p1, p2):
        state_path = proposals_dir / pid / "proposal-state.json"
        data = json.loads(state_path.read_text())
        data["waves"]["8"]["status"] = "not_started"
        data["go_no_go"] = "pending"
        data["archived"] = False
        state_path.write_text(json.dumps(data, indent=2))


@given(
    parsers.parse('Phil has a multi-proposal workspace with only proposal "{topic_id}"'),
)
def single_proposal_workspace(
    proposals_dir: Path,
    artifacts_dir: Path,
    set_active_proposal,
    create_proposal,
    topic_id: str,
):
    """Set up workspace with exactly one proposal."""
    create_proposal(proposals_dir, artifacts_dir, topic_id)
    set_active_proposal(topic_id)


@given(parsers.parse('the proposal "{topic_id}" has go-no-go set to "{decision}"'))
def proposal_go_no_go(proposals_dir: Path, topic_id: str, decision: str):
    """Set go_no_go field on proposal state."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    data["go_no_go"] = decision
    state_path.write_text(json.dumps(data, indent=2))


@given(parsers.parse('the proposal "{topic_id}" has archived set to true'))
def proposal_archived(proposals_dir: Path, topic_id: str):
    """Set archived flag on proposal state."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    data["archived"] = True
    state_path.write_text(json.dumps(data, indent=2))


# --- When steps ---


@when(parsers.parse('proposal "{topic_id}" is marked as completed'))
def mark_completed(proposals_dir: Path, topic_id: str):
    """Mark a proposal as completed by setting wave 8 status."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    data["waves"]["8"]["status"] = "completed"
    state_path.write_text(json.dumps(data, indent=2))


@when("auto-switch logic is evaluated")
def evaluate_auto_switch(
    workspace_root: Path,
    operation_result: dict[str, Any],
):
    """Invoke auto-switch evaluation after proposal completion.

    Invokes through the lifecycle management driving port.
    """
    try:
        from pes.adapters.lifecycle_manager import evaluate_auto_switch

        result = evaluate_auto_switch(workspace_root)
        operation_result["auto_switch"] = result
        operation_result["error"] = None
    except Exception as exc:
        operation_result["auto_switch"] = None
        operation_result["error"] = str(exc)


@when("the active proposals are enumerated")
def enumerate_active(workspace_root: Path, operation_result: dict[str, Any]):
    """Count active vs completed proposals."""
    try:
        from pes.adapters.workspace_enumerator import enumerate_proposals

        entries = enumerate_proposals(workspace_root)
        active = [e for e in entries if e.status == "active"]
        completed = [e for e in entries if e.status == "completed"]
        operation_result["active_count"] = len(active)
        operation_result["completed_count"] = len(completed)
        operation_result["entries"] = entries
    except Exception as exc:
        operation_result["error"] = str(exc)


@when(parsers.parse('the completion status of "{topic_id}" is checked'))
def check_completion(
    workspace_root: Path,
    operation_result: dict[str, Any],
    topic_id: str,
):
    """Check whether a proposal is classified as completed."""
    try:
        from pes.adapters.lifecycle_manager import is_proposal_completed

        completed = is_proposal_completed(workspace_root, topic_id)
        operation_result[f"{topic_id}_completed"] = completed
    except Exception as exc:
        operation_result["error"] = str(exc)


# --- Then steps ---


@then("the active proposal count is 0")
def no_active_proposals(operation_result: dict[str, Any]):
    """Assert zero active proposals."""
    assert operation_result["active_count"] == 0


@then(parsers.parse("the completed proposal count is {count:d}"))
def completed_count(operation_result: dict[str, Any], count: int):
    """Assert expected completed count."""
    assert operation_result["completed_count"] == count


@then(parsers.parse('the "{topic_id}" proposal state is fully readable'))
def state_fully_readable(proposals_dir: Path, topic_id: str):
    """Assert proposal state can be loaded and has expected structure."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    assert "topic" in data
    assert "current_wave" in data


@then("the active proposal is not automatically changed")
def no_auto_switch(operation_result: dict[str, Any]):
    """Assert auto-switch did not occur."""
    result = operation_result["auto_switch"]
    assert result is not None
    assert not result.switched


@then(parsers.parse("{count:d} active proposals are available for selection"))
def active_proposals_for_selection(operation_result: dict[str, Any], count: int):
    """Assert number of active proposals available for user selection."""
    result = operation_result["auto_switch"]
    assert len(result.available_active) == count


@then(parsers.parse('the proposal "{topic_id}" is classified as completed'))
def proposal_classified_completed(operation_result: dict[str, Any], topic_id: str):
    """Assert proposal completion classification."""
    assert operation_result[f"{topic_id}_completed"] is True


@then("no auto-switch occurs")
def auto_switch_not_triggered(operation_result: dict[str, Any]):
    """Assert auto-switch did not execute."""
    result = operation_result["auto_switch"]
    assert result is not None
    assert not result.switched


@then("the result indicates all proposals are completed")
def all_completed_indication(operation_result: dict[str, Any]):
    """Assert result signals all proposals completed."""
    result = operation_result["auto_switch"]
    assert result.all_completed is True
