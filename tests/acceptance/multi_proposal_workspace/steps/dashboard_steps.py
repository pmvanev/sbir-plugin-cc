"""Step definitions for dashboard enumeration scenarios.

Invokes through: Workspace enumeration service (driving port).
Handles proposal discovery, corruption handling, and status classification.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.multi_proposal_workspace.steps.workspace_common_steps import *  # noqa: F403

# Link feature files -- integration checkpoints that test enumeration
scenarios("../integration-checkpoints.feature")


# --- Given steps ---


@given(parsers.parse('the proposal "{topic_id}" has corrupted state'))
def corrupted_state(proposals_dir: Path, topic_id: str):
    """Write invalid JSON to a proposal's state file."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    state_path.write_text("{invalid json content!!!")


@given("both proposals have corrupted state")
def both_corrupted(proposals_dir: Path):
    """Corrupt all proposal state files."""
    for state_path in proposals_dir.glob("*/proposal-state.json"):
        state_path.write_text("{broken!!!")


@given(parsers.parse('the proposal "{topic_id}" has state and artifacts'))
def proposal_has_state_and_artifacts(
    proposals_dir: Path, artifacts_dir: Path, topic_id: str
):
    """Ensure proposal has both state file and artifact directory with content."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    assert state_path.exists()
    wave_dir = artifacts_dir / topic_id / "wave-1-test"
    wave_dir.mkdir(parents=True, exist_ok=True)
    (wave_dir / "artifact.md").write_text("# Test Artifact")


@given(parsers.parse('a filesystem snapshot of "{topic_id}" directories is recorded'))
def record_fs_snapshot(
    proposals_dir: Path, artifacts_dir: Path, snapshot: dict[str, Any], topic_id: str
):
    """Record the filesystem state of a proposal's directories."""
    state_dir = proposals_dir / topic_id
    artifact_dir = artifacts_dir / topic_id
    snapshot[f"{topic_id}_state_files"] = {
        str(f.relative_to(state_dir)): f.read_bytes()
        for f in state_dir.rglob("*")
        if f.is_file()
    }
    snapshot[f"{topic_id}_artifact_files"] = {
        str(f.relative_to(artifact_dir)): f.read_bytes()
        for f in artifact_dir.rglob("*")
        if f.is_file()
    }


# --- When steps ---


@when("all proposals are enumerated from the workspace")
def enumerate_proposals(workspace_root: Path, operation_result: dict[str, Any]):
    """Invoke enumeration service to discover all proposals.

    Invokes through the enumeration driving port.
    """
    try:
        from pes.adapters.workspace_enumerator import enumerate_proposals as enum_fn

        entries = enum_fn(workspace_root)
        operation_result["entries"] = entries
        operation_result["error"] = None
    except Exception as exc:
        operation_result["entries"] = []
        operation_result["error"] = str(exc)


# --- Then steps: Enumeration ---


@then(parsers.parse("{count:d} proposals are found"))
def n_proposals_found(operation_result: dict[str, Any], count: int):
    """Assert expected number of proposals discovered."""
    assert len(operation_result["entries"]) == count


@then(parsers.parse("{count:d} entries are returned"))
def n_entries_returned(operation_result: dict[str, Any], count: int):
    """Assert expected number of entries (including errors)."""
    assert len(operation_result["entries"]) == count


@then(
    parsers.parse(
        'the enumeration includes "{p1}", "{p2}", and "{p3}"'
    ),
)
def enumeration_includes_three(operation_result: dict[str, Any], p1: str, p2: str, p3: str):
    """Assert all three proposals appear in enumeration."""
    ids = {e.topic_id for e in operation_result["entries"]}
    for pid in (p1, p2, p3):
        assert pid in ids, f"Expected '{pid}' in enumeration, got {ids}"


@then(parsers.parse('the entry for "{topic_id}" is marked as corrupted'))
def entry_is_corrupted(operation_result: dict[str, Any], topic_id: str):
    """Assert a specific entry has corrupted status."""
    entry = next(
        (e for e in operation_result["entries"] if e.topic_id == topic_id),
        None,
    )
    assert entry is not None, f"Entry for '{topic_id}' not found"
    assert entry.status == "corrupted"


@then(parsers.parse('the entry for "{topic_id}" has valid state data'))
def entry_has_valid_state(operation_result: dict[str, Any], topic_id: str):
    """Assert a specific entry has valid state."""
    entry = next(
        (e for e in operation_result["entries"] if e.topic_id == topic_id),
        None,
    )
    assert entry is not None
    assert entry.status != "corrupted"


@then("all entries are marked as corrupted")
def all_entries_corrupted(operation_result: dict[str, Any]):
    """Assert all entries have corrupted status."""
    for entry in operation_result["entries"]:
        assert entry.status == "corrupted"


# --- Then steps: Isolation Snapshot ---


@then(
    parsers.parse(
        'the "{topic_id}" state directory contents are identical to the snapshot'
    ),
)
def state_dir_matches_snapshot(
    proposals_dir: Path, snapshot: dict[str, Any], topic_id: str
):
    """Assert state directory unchanged from snapshot."""
    state_dir = proposals_dir / topic_id
    current = {
        str(f.relative_to(state_dir)): f.read_bytes()
        for f in state_dir.rglob("*")
        if f.is_file()
    }
    assert current == snapshot[f"{topic_id}_state_files"]


@then(
    parsers.parse(
        'the "{topic_id}" artifact directory contents are identical to the snapshot'
    ),
)
def artifact_dir_matches_snapshot(
    artifacts_dir: Path, snapshot: dict[str, Any], topic_id: str
):
    """Assert artifact directory unchanged from snapshot."""
    artifact_dir = artifacts_dir / topic_id
    current = {
        str(f.relative_to(artifact_dir)): f.read_bytes()
        for f in artifact_dir.rglob("*")
        if f.is_file()
    }
    assert current == snapshot[f"{topic_id}_artifact_files"]
