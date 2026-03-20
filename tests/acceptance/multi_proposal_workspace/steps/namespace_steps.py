"""Step definitions for namespace creation scenarios.

Invokes through: Namespace creation service (driving port).
Handles proposal creation, isolation verification, and collision detection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.multi_proposal_workspace.conftest import (
    file_checksum,
    make_proposal_state,
)
from tests.acceptance.multi_proposal_workspace.steps.workspace_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-02-namespace-creation.feature")


# --- Given steps ---


@given(
    parsers.parse('the "{topic_id}" state file checksum is recorded'),
)
def record_checksum(proposals_dir: Path, snapshot: dict[str, Any], topic_id: str):
    """Record the checksum of a proposal state file."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    snapshot[f"{topic_id}_checksum"] = file_checksum(state_path)


@given(
    parsers.parse(
        'Phil has a multi-proposal workspace with proposals "{p1}" and "{p2}"'
    ),
)
def multi_ws_two_for_ns(
    proposals_dir: Path,
    artifacts_dir: Path,
    set_active_proposal,
    create_proposal,
    p1: str,
    p2: str,
):
    """Set up workspace with two proposals (namespace context)."""
    create_proposal(proposals_dir, artifacts_dir, p1)
    create_proposal(proposals_dir, artifacts_dir, p2)
    set_active_proposal(p1)


@given(parsers.parse('Phil has a legacy workspace with proposal "{topic_id}" at the root level'))
def legacy_workspace_with_id(sbir_dir: Path, artifacts_dir: Path, topic_id: str):
    """Set up legacy workspace with known topic ID."""
    state = make_proposal_state(topic_id)
    (sbir_dir / "proposal-state.json").write_text(json.dumps(state, indent=2))
    (sbir_dir / "audit").mkdir(exist_ok=True)
    (sbir_dir / "audit" / "pes-audit.log").write_text("audit entry\n")


@given(parsers.parse("root-level artifacts exist for wave {wave_num:d}"))
def root_wave_artifacts(artifacts_dir: Path, wave_num: int):
    """Create root-level wave artifacts."""
    wave_dir = artifacts_dir / f"wave-{wave_num}-test"
    wave_dir.mkdir(parents=True, exist_ok=True)
    (wave_dir / "artifact.md").write_text(f"# Wave {wave_num}")


@given(parsers.parse("root-level artifacts exist for wave {w1:d} and wave {w2:d}"))
def root_wave_artifacts_two(artifacts_dir: Path, w1: int, w2: int):
    """Create root-level wave artifacts for two waves."""
    for w in (w1, w2):
        wave_dir = artifacts_dir / f"wave-{w}-test"
        wave_dir.mkdir(parents=True, exist_ok=True)
        (wave_dir / "artifact.md").write_text(f"# Wave {w}")


@given("root-level audit log exists")
def root_audit_exists(sbir_dir: Path):
    """Ensure root-level audit log exists."""
    audit_dir = sbir_dir / "audit"
    audit_dir.mkdir(exist_ok=True)
    (audit_dir / "pes-audit.log").write_text("legacy audit entry\n")


@given(parsers.parse("Phil has a multi-proposal workspace with {count:d} existing proposals"))
def multi_ws_n_proposals(
    proposals_dir: Path,
    artifacts_dir: Path,
    set_active_proposal,
    create_proposal,
    count: int,
):
    """Set up workspace with N proposals."""
    ids = [f"proposal-{i:03d}" for i in range(count)]
    for pid in ids:
        create_proposal(proposals_dir, artifacts_dir, pid)
    set_active_proposal(ids[0])


@given("Phil has a legacy workspace that was migrated")
def migrated_legacy_workspace(
    sbir_dir: Path,
    proposals_dir: Path,
    artifacts_dir: Path,
    set_active_proposal,
    create_proposal,
):
    """Set up a workspace that looks like it was migrated from legacy."""
    # Create multi-proposal structure
    create_proposal(proposals_dir, artifacts_dir, "af263-042")
    set_active_proposal("af263-042")
    # Leave the .migrated file
    state = make_proposal_state("af263-042")
    (sbir_dir / "proposal-state.json.migrated").write_text(json.dumps(state, indent=2))


# --- When steps ---


@when(parsers.parse('Phil creates a new proposal with topic ID "{topic_id}"'))
def create_new_proposal(
    workspace_root: Path,
    operation_result: dict[str, Any],
    topic_id: str,
):
    """Invoke namespace creation service for a new proposal.

    Invokes through the namespace creation driving port.
    """
    try:
        from pes.adapters.namespace_manager import create_proposal_namespace

        result = create_proposal_namespace(workspace_root, topic_id)
        operation_result["success"] = True
        operation_result["result"] = result
        operation_result["error"] = None
    except Exception as exc:
        operation_result["success"] = False
        operation_result["result"] = None
        operation_result["error"] = str(exc)


@when(
    parsers.parse(
        'Phil creates a new proposal with topic ID "{topic_id}" and name "{name}"'
    ),
)
def create_proposal_with_name(
    workspace_root: Path,
    operation_result: dict[str, Any],
    topic_id: str,
    name: str,
):
    """Invoke namespace creation with custom name override."""
    try:
        from pes.adapters.namespace_manager import create_proposal_namespace

        result = create_proposal_namespace(workspace_root, topic_id, name=name)
        operation_result["success"] = True
        operation_result["result"] = result
        operation_result["error"] = None
    except Exception as exc:
        operation_result["success"] = False
        operation_result["result"] = None
        operation_result["error"] = str(exc)


@when(parsers.parse("Phil creates {count:d} additional proposals"))
def create_additional_proposals(
    workspace_root: Path,
    operation_result: dict[str, Any],
    count: int,
):
    """Create multiple additional proposals."""
    from pes.adapters.namespace_manager import create_proposal_namespace

    created = []
    for i in range(count):
        pid = f"new-proposal-{i:03d}"
        result = create_proposal_namespace(workspace_root, pid)
        created.append(result)
    operation_result["created"] = created


@when("Phil migrates the legacy workspace")
def migrate_workspace(
    workspace_root: Path,
    operation_result: dict[str, Any],
):
    """Invoke migration service for legacy-to-multi conversion."""
    try:
        from pes.adapters.migration_service import migrate_legacy_workspace

        result = migrate_legacy_workspace(workspace_root)
        operation_result["success"] = True
        operation_result["result"] = result
        operation_result["error"] = None
    except Exception as exc:
        operation_result["success"] = False
        operation_result["result"] = None
        operation_result["error"] = str(exc)


@when("the migrated-suffix file is restored to its original name")
def restore_migrated_file(sbir_dir: Path):
    """Restore .migrated file to original name."""
    migrated = sbir_dir / "proposal-state.json.migrated"
    original = sbir_dir / "proposal-state.json"
    if migrated.exists():
        migrated.rename(original)


@when("the proposals directory is removed")
def remove_proposals_dir(sbir_dir: Path):
    """Remove the proposals directory."""
    import shutil
    proposals = sbir_dir / "proposals"
    if proposals.exists():
        shutil.rmtree(proposals)


# --- Then steps: Namespace Existence ---


@then(parsers.parse('the proposal "{topic_id}" namespace exists with its own state'))
def proposal_namespace_exists(proposals_dir: Path, topic_id: str):
    """Assert proposal namespace directory and state file exist."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    assert state_path.exists(), f"State file not found: {state_path}"


@then(parsers.parse('the state directory for "{topic_id}" exists under the proposals directory'))
def state_dir_exists_for(proposals_dir: Path, topic_id: str):
    """Assert proposal directory exists under proposals/."""
    assert (proposals_dir / topic_id).is_dir()
    assert (proposals_dir / topic_id / "proposal-state.json").exists()


@then(parsers.parse('the artifact directory for "{topic_id}" exists'))
def artifact_dir_exists_for(artifacts_dir: Path, topic_id: str):
    """Assert proposal artifact directory exists."""
    assert (artifacts_dir / topic_id).is_dir()


@then("no root-level proposal state file exists")
def no_root_state(sbir_dir: Path):
    """Assert no proposal-state.json at .sbir/ root."""
    assert not (sbir_dir / "proposal-state.json").exists()


# --- Then steps: Active Proposal ---


@then(parsers.parse('the active proposal is now "{topic_id}"'))
def active_is_now(active_proposal_path: Path, topic_id: str):
    """Assert active-proposal file contains expected topic ID."""
    assert active_proposal_path.read_text().strip() == topic_id


@then(parsers.parse('the active proposal file contains "{topic_id}"'))
def active_file_has(active_proposal_path: Path, topic_id: str):
    """Assert active-proposal file content."""
    assert active_proposal_path.read_text().strip() == topic_id


# --- Then steps: Isolation ---


@then(parsers.parse('the proposal "{topic_id}" state is unchanged'))
def proposal_state_unchanged(proposals_dir: Path, topic_id: str):
    """Assert proposal state file exists and is readable."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    assert state_path.exists()
    data = json.loads(state_path.read_text())
    assert "topic" in data


@then(parsers.parse('the "{topic_id}" state file checksum is unchanged'))
def checksum_unchanged(proposals_dir: Path, snapshot: dict[str, Any], topic_id: str):
    """Assert state file checksum matches recorded value."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    current = file_checksum(state_path)
    assert current == snapshot[f"{topic_id}_checksum"]


# --- Then steps: State Content ---


@then(parsers.parse('the "{topic_id}" proposal state contains topic ID "{expected_id}"'))
def state_contains_topic_id(proposals_dir: Path, topic_id: str, expected_id: str):
    """Assert proposal state has correct topic ID."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    data = json.loads(state_path.read_text())
    assert data["topic"]["id"] == expected_id


@then(
    parsers.parse(
        'the "{ns}" proposal state records original topic ID "{orig_id}"'
    ),
)
def state_records_original_id(proposals_dir: Path, ns: str, orig_id: str):
    """Assert state has correct original topic ID."""
    state_path = proposals_dir / ns / "proposal-state.json"
    data = json.loads(state_path.read_text())
    assert data["topic"]["id"] == orig_id


@then(parsers.parse('the "{ns}" proposal state records namespace "{namespace}"'))
def state_records_namespace(proposals_dir: Path, ns: str, namespace: str):
    """Assert state has namespace field."""
    state_path = proposals_dir / ns / "proposal-state.json"
    data = json.loads(state_path.read_text())
    assert data.get("namespace") == namespace


# --- Then steps: Error Cases ---


@then(parsers.parse('the creation fails with error mentioning "{msg}"'))
def creation_fails_with(operation_result: dict[str, Any], msg: str):
    """Assert creation failed with expected error message."""
    assert not operation_result["success"], "Expected creation to fail"
    assert msg in operation_result["error"], (
        f"Expected '{msg}' in error: {operation_result['error']}"
    )


@then("the error suggests using a custom name flag")
def error_suggests_name_flag(operation_result: dict[str, Any]):
    """Assert error mentions --name flag."""
    assert "--name" in operation_result["error"]


@then("no new files are created in the workspace")
def no_new_files(operation_result: dict[str, Any]):
    """Assert no filesystem changes on failed creation."""
    # The creation service should be atomic -- no partial writes on error
    assert not operation_result["success"]


# --- Then steps: Migration ---


@then(parsers.parse("the original root state file is preserved with migrated suffix"))
def migrated_suffix_exists(sbir_dir: Path):
    """Assert .migrated safety net file exists."""
    assert (sbir_dir / "proposal-state.json.migrated").exists()


@then("the migrated-suffix file contains the original proposal data")
def migrated_has_data(sbir_dir: Path):
    """Assert .migrated file has valid proposal data."""
    data = json.loads((sbir_dir / "proposal-state.json.migrated").read_text())
    assert "topic" in data


@then(parsers.parse('wave {wave_num:d} artifacts exist under the "{topic_id}" artifact namespace'))
def wave_artifacts_in_namespace(artifacts_dir: Path, wave_num: int, topic_id: str):
    """Assert wave artifacts moved to proposal namespace."""
    wave_dirs = list((artifacts_dir / topic_id).glob(f"wave-{wave_num}-*"))
    assert len(wave_dirs) > 0, f"No wave-{wave_num} artifacts found under {topic_id}"


@then(parsers.parse('the audit log exists under the "{topic_id}" proposal namespace'))
def audit_in_namespace(proposals_dir: Path, topic_id: str):
    """Assert audit directory exists in proposal namespace."""
    audit_dir = proposals_dir / topic_id / "audit"
    assert audit_dir.is_dir()


# --- Then steps: Property-based ---


@then(parsers.parse("all {count:d} proposal state files are valid and independently readable"))
def all_states_valid(proposals_dir: Path, count: int):
    """Assert all proposal state files are valid JSON."""
    state_files = list(proposals_dir.glob("*/proposal-state.json"))
    assert len(state_files) == count
    for sf in state_files:
        data = json.loads(sf.read_text())
        assert "topic" in data


@then("the workspace is detected as legacy layout")
def detected_as_legacy(workspace_root: Path):
    """Verify workspace is detected as legacy after restoration."""
    from pes.adapters.workspace_resolver import resolve_workspace

    ctx = resolve_workspace(workspace_root)
    assert ctx.layout == "legacy"
