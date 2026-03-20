"""Common steps shared across all Multi-Proposal Workspace acceptance features.

These steps handle shared preconditions like workspace setup,
proposal creation, and active proposal configuration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pytest_bdd import given, parsers

from tests.acceptance.multi_proposal_workspace.conftest import make_proposal_state


@given("a workspace root directory exists")
def workspace_root_exists(workspace_root: Path):
    """Workspace root is provided by the workspace_root fixture."""
    assert workspace_root.exists()


@given(
    parsers.parse(
        'Phil has a multi-proposal workspace with proposals "{prop1}" and "{prop2}"'
    ),
)
def multi_proposal_workspace_two(
    proposals_dir: Path,
    artifacts_dir: Path,
    active_proposal_path: Path,
    create_proposal,
    prop1: str,
    prop2: str,
):
    """Set up a multi-proposal workspace with two proposals."""
    create_proposal(proposals_dir, artifacts_dir, prop1)
    create_proposal(proposals_dir, artifacts_dir, prop2)


@given(
    parsers.parse(
        'Phil has a multi-proposal workspace with proposals "{p1}", "{p2}", and "{p3}"'
    ),
)
def multi_proposal_workspace_three(
    proposals_dir: Path,
    artifacts_dir: Path,
    create_proposal,
    p1: str,
    p2: str,
    p3: str,
):
    """Set up a multi-proposal workspace with three proposals."""
    create_proposal(proposals_dir, artifacts_dir, p1)
    create_proposal(proposals_dir, artifacts_dir, p2)
    create_proposal(proposals_dir, artifacts_dir, p3)


@given(
    parsers.parse('Phil has a multi-proposal workspace with active proposal "{topic_id}"'),
)
def multi_proposal_workspace_active(
    proposals_dir: Path,
    artifacts_dir: Path,
    set_active_proposal,
    create_proposal,
    topic_id: str,
):
    """Set up a multi-proposal workspace with one proposal set as active."""
    create_proposal(proposals_dir, artifacts_dir, topic_id)
    set_active_proposal(topic_id)


@given(
    parsers.parse('the active proposal is "{topic_id}"'),
)
def set_active(set_active_proposal, topic_id: str):
    """Set the active proposal pointer."""
    set_active_proposal(topic_id)


@given(
    parsers.parse(
        'the proposal "{topic_id}" has state with topic title "{title}"'
    ),
)
def proposal_has_state_with_title(proposals_dir: Path, topic_id: str, title: str):
    """Update the proposal state with a specific title."""
    state_path = proposals_dir / topic_id / "proposal-state.json"
    state = json.loads(state_path.read_text())
    state["topic"]["title"] = title
    state_path.write_text(json.dumps(state, indent=2))


@given("Phil has a legacy workspace with proposal state at the root level")
def legacy_workspace(sbir_dir: Path, artifacts_dir: Path):
    """Set up a legacy workspace with root-level state."""
    state = make_proposal_state("af263-042", title="Legacy Proposal")
    (sbir_dir / "proposal-state.json").write_text(json.dumps(state, indent=2))
    (sbir_dir / "audit").mkdir(exist_ok=True)


@given("artifacts exist at the root artifact directory")
def root_artifacts_exist(artifacts_dir: Path):
    """Create root-level wave artifacts (legacy layout)."""
    wave_dir = artifacts_dir / "wave-3-outline"
    wave_dir.mkdir(parents=True, exist_ok=True)
    (wave_dir / "outline.md").write_text("# Outline")


@given("Phil has a fresh workspace with no proposals")
def fresh_workspace(workspace_root: Path):
    """Workspace root exists but no .sbir/ directory."""
    # workspace_root fixture already provides a clean directory
    pass


@given(
    parsers.parse("the workspace has no proposal state and no proposals directory"),
)
def no_state_no_proposals(workspace_root: Path):
    """Ensure workspace has neither legacy nor multi-proposal layout."""
    sbir = workspace_root / ".sbir"
    if sbir.exists():
        import shutil
        shutil.rmtree(sbir)


@given(
    parsers.parse('the workspace contains a proposals directory with "{topic_id}"'),
)
def workspace_with_proposals_dir_one(
    proposals_dir: Path,
    artifacts_dir: Path,
    create_proposal,
    topic_id: str,
):
    """Set up proposals directory with one proposal."""
    create_proposal(proposals_dir, artifacts_dir, topic_id)


@given(
    parsers.parse(
        'the workspace contains a proposals directory with "{p1}" and "{p2}"'
    ),
)
def workspace_with_proposals_dir_two(
    proposals_dir: Path,
    artifacts_dir: Path,
    create_proposal,
    p1: str,
    p2: str,
):
    """Set up proposals directory with two proposals."""
    create_proposal(proposals_dir, artifacts_dir, p1)
    create_proposal(proposals_dir, artifacts_dir, p2)


@given("the workspace contains proposal state at the root level")
def root_state_exists(sbir_dir: Path):
    """Create root-level proposal-state.json (legacy marker)."""
    state = make_proposal_state("af263-042")
    (sbir_dir / "proposal-state.json").write_text(json.dumps(state, indent=2))


@given("no proposals directory exists")
def no_proposals_dir(sbir_dir: Path):
    """Ensure no proposals/ subdirectory exists in .sbir/."""
    proposals = sbir_dir / "proposals"
    if proposals.exists():
        import shutil
        shutil.rmtree(proposals)


@given(parsers.parse('the active proposal file contains "{topic_id}"'))
def active_file_contains(set_active_proposal, topic_id: str):
    """Write active-proposal file with given topic ID."""
    set_active_proposal(topic_id)


@given("the active proposal file does not exist")
def no_active_file(active_proposal_path: Path):
    """Ensure active-proposal file does not exist."""
    if active_proposal_path.exists():
        active_proposal_path.unlink()


@given("the active proposal file is empty")
def empty_active_file(active_proposal_path: Path):
    """Create an empty active-proposal file."""
    active_proposal_path.write_text("")


@given("the active proposal file contains only whitespace")
def whitespace_active_file(active_proposal_path: Path):
    """Create active-proposal file with only whitespace."""
    active_proposal_path.write_text("   \n  ")
