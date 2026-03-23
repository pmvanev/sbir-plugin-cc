"""Acceptance test conftest -- fixtures for Rigor Profile BDD scenarios.

All acceptance tests invoke through driving ports only:
- RigorService (application service for profile set/validate/diff/history)
- RigorDefinitionsReader (plugin config for profile definitions)
- ModelTierReader (tier-to-model resolution)

Per-proposal rigor state uses real filesystem via tmp_path.
Profile definitions and tier mappings use in-memory fakes of port interfaces.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Workspace and Proposal Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def workspace_root(tmp_path: Path) -> Path:
    """Fresh temporary directory simulating a user's proposal workspace."""
    return tmp_path


@pytest.fixture()
def sbir_dir(workspace_root: Path) -> Path:
    """The .sbir directory within the workspace."""
    d = workspace_root / ".sbir"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture()
def proposals_dir(sbir_dir: Path) -> Path:
    """The .sbir/proposals/ directory."""
    d = sbir_dir / "proposals"
    d.mkdir(exist_ok=True)
    return d


@pytest.fixture()
def active_proposal_path(sbir_dir: Path) -> Path:
    """Path to the .sbir/active-proposal file."""
    return sbir_dir / "active-proposal"


@pytest.fixture()
def set_active_proposal(active_proposal_path: Path):
    """Helper to write the active-proposal pointer file."""

    def _set(topic_id: str) -> None:
        active_proposal_path.write_text(topic_id)

    return _set


# ---------------------------------------------------------------------------
# Per-Proposal Rigor State Fixtures
# ---------------------------------------------------------------------------


def make_rigor_profile_state(
    profile: str = "standard",
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a minimal rigor-profile.json dict for testing."""
    return {
        "schema_version": "1.0.0",
        "profile": profile,
        "set_at": "2026-04-01T14:30:00Z",
        "history": history or [],
    }


@pytest.fixture()
def create_proposal_with_rigor(proposals_dir: Path, set_active_proposal):
    """Factory fixture to create a proposal namespace with rigor config."""

    def _create(
        topic_id: str,
        rigor_profile: str = "standard",
        current_wave: int = 0,
        include_rigor: bool = True,
        fit_score: int | None = None,
        phase: str = "I",
    ) -> Path:
        """Create proposal namespace and return the proposal directory."""
        proposal_dir = proposals_dir / topic_id.lower()
        proposal_dir.mkdir(parents=True, exist_ok=True)

        # Write proposal-state.json
        state: dict[str, Any] = {
            "topic": {
                "id": topic_id.upper(),
                "title": f"Test Proposal {topic_id.upper()}",
                "deadline": "2026-06-01",
                "phase": phase,
            },
            "current_wave": current_wave,
            "go_no_go": "go",
        }
        if fit_score is not None:
            state["fit_scoring"] = {
                "composite_score": fit_score,
            }
        state_path = proposal_dir / "proposal-state.json"
        state_path.write_text(json.dumps(state, indent=2))

        # Write rigor-profile.json if requested
        if include_rigor:
            rigor_state = make_rigor_profile_state(profile=rigor_profile)
            rigor_path = proposal_dir / "rigor-profile.json"
            rigor_path.write_text(json.dumps(rigor_state, indent=2))

        # Set as active proposal
        set_active_proposal(topic_id.lower())

        return proposal_dir

    return _create


# ---------------------------------------------------------------------------
# Result Containers
# ---------------------------------------------------------------------------


@pytest.fixture()
def service_result() -> dict[str, Any]:
    """Mutable container to hold service operation results across steps."""
    return {}


@pytest.fixture()
def resolution_result() -> dict[str, Any]:
    """Mutable container to hold model tier resolution results across steps."""
    return {}


@pytest.fixture()
def suggestion_result() -> dict[str, Any]:
    """Mutable container to hold suggestion computation results across steps."""
    return {}


@pytest.fixture()
def diff_result() -> dict[str, Any]:
    """Mutable container to hold diff computation results across steps."""
    return {}
