"""Acceptance test conftest -- fixtures for Multi-Proposal Workspace BDD scenarios.

All acceptance tests invoke through driving ports only:
- Path resolution module (workspace layout detection, path derivation)
- Namespace creation service (proposal directory operations)
- Migration service (legacy-to-multi conversion)

External dependencies (file system) use tmp_path-based real filesystem
operations since the feature is fundamentally about file layout.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Workspace Directory Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def workspace_root(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating a project workspace root."""
    return tmp_path


@pytest.fixture()
def sbir_dir(workspace_root: Path) -> Path:
    """The .sbir directory within the workspace. Created on demand."""
    d = workspace_root / ".sbir"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture()
def proposals_dir(sbir_dir: Path) -> Path:
    """The .sbir/proposals/ directory. Created on demand."""
    d = sbir_dir / "proposals"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture()
def artifacts_dir(workspace_root: Path) -> Path:
    """The artifacts/ directory at workspace root. Created on demand."""
    d = workspace_root / "artifacts"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture()
def active_proposal_path(sbir_dir: Path) -> Path:
    """Path to the .sbir/active-proposal file."""
    return sbir_dir / "active-proposal"


# ---------------------------------------------------------------------------
# Proposal State Helpers
# ---------------------------------------------------------------------------


def make_proposal_state(
    topic_id: str,
    title: str = "",
    current_wave: int = 0,
    deadline: str = "2026-06-01",
    go_no_go: str = "pending",
    archived: bool = False,
    wave_8_status: str = "not_started",
    namespace: str | None = None,
) -> dict[str, Any]:
    """Build a minimal proposal-state.json dict for testing."""
    title = title or f"Test Proposal {topic_id.upper()}"
    state: dict[str, Any] = {
        "topic": {
            "id": topic_id.upper(),
            "title": title,
            "deadline": deadline,
        },
        "current_wave": current_wave,
        "go_no_go": go_no_go,
        "archived": archived,
        "waves": {
            "8": {"status": wave_8_status},
        },
    }
    if namespace is not None:
        state["namespace"] = namespace
    return state


@pytest.fixture()
def create_proposal():
    """Factory fixture to create a proposal namespace with state file."""

    def _create(
        proposals_dir: Path,
        artifacts_dir: Path,
        topic_id: str,
        **state_kwargs: Any,
    ) -> Path:
        """Create proposal namespace and return the state file path."""
        proposal_dir = proposals_dir / topic_id
        proposal_dir.mkdir(parents=True, exist_ok=True)
        (proposal_dir / "audit").mkdir(exist_ok=True)

        artifact_proposal_dir = artifacts_dir / topic_id
        artifact_proposal_dir.mkdir(parents=True, exist_ok=True)

        state = make_proposal_state(topic_id, **state_kwargs)
        state_path = proposal_dir / "proposal-state.json"
        state_path.write_text(json.dumps(state, indent=2))
        return state_path

    return _create


@pytest.fixture()
def set_active_proposal(active_proposal_path: Path):
    """Helper to write the active-proposal pointer file."""

    def _set(topic_id: str) -> None:
        active_proposal_path.write_text(topic_id)

    return _set


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def path_result() -> dict[str, Any]:
    """Mutable container to hold path resolution results across steps."""
    return {}


@pytest.fixture()
def operation_result() -> dict[str, Any]:
    """Mutable container to hold operation results (create, switch, migrate)."""
    return {}


@pytest.fixture()
def snapshot() -> dict[str, Any]:
    """Mutable container to hold filesystem snapshots for isolation checks."""
    return {}


# ---------------------------------------------------------------------------
# Checksum Helpers
# ---------------------------------------------------------------------------


def file_checksum(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
