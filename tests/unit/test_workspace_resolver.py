"""Unit tests for workspace path resolution module.

Driving port: resolve_workspace() pure function.
Tests workspace layout detection, path derivation, and error cases.

Test Budget: 7 behaviors x 2 = 14 max unit tests.
Behaviors:
1. Multi-proposal layout detection
2. Multi-proposal path derivation (state_dir, artifact_base, audit_dir)
3. Legacy layout detection + root paths
4. Fresh workspace detection
5. Missing active-proposal file error with available list
6. Active proposal references nonexistent proposal error
7. Empty/whitespace active-proposal file error (parametrized)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests.acceptance.multi_proposal_workspace.conftest import make_proposal_state


def _setup_multi_workspace(
    tmp_path: Path,
    topic_ids: list[str],
    active: str | None = None,
    active_content: str | None = None,
) -> Path:
    """Helper to set up a multi-proposal workspace."""
    sbir = tmp_path / ".sbir"
    sbir.mkdir()
    proposals = sbir / "proposals"
    proposals.mkdir()
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()

    for tid in topic_ids:
        p = proposals / tid
        p.mkdir()
        (p / "audit").mkdir()
        (p / "proposal-state.json").write_text(
            json.dumps(make_proposal_state(tid), indent=2)
        )
        (artifacts / tid).mkdir()

    if active is not None:
        (sbir / "active-proposal").write_text(active)
    elif active_content is not None:
        (sbir / "active-proposal").write_text(active_content)

    return tmp_path


def _setup_legacy_workspace(tmp_path: Path) -> Path:
    """Helper to set up a legacy workspace."""
    sbir = tmp_path / ".sbir"
    sbir.mkdir()
    (sbir / "proposal-state.json").write_text(
        json.dumps(make_proposal_state("af263-042", title="Legacy"), indent=2)
    )
    (sbir / "audit").mkdir()
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    return tmp_path


# --- Behavior 1: Multi-proposal layout detection ---


def test_multi_proposal_layout_detected(tmp_path: Path):
    """Multi-proposal layout detected when .sbir/proposals/ exists with active pointer."""
    ws = _setup_multi_workspace(tmp_path, ["af263-042"], active="af263-042")
    from pes.adapters.workspace_resolver import resolve_workspace

    ctx = resolve_workspace(ws)
    assert ctx.layout == "multi"
    assert ctx.active_proposal == "af263-042"
    assert ctx.is_legacy is False


# --- Behavior 1b: WorkspaceContext is immutable ---


def test_workspace_context_is_immutable(tmp_path: Path):
    """WorkspaceContext is frozen — attributes cannot be reassigned."""
    ws = _setup_multi_workspace(tmp_path, ["af263-042"], active="af263-042")
    from pes.adapters.workspace_resolver import resolve_workspace

    ctx = resolve_workspace(ws)
    with pytest.raises(AttributeError):
        ctx.layout = "tampered"


# --- Behavior 2: Multi-proposal path derivation ---


def test_multi_proposal_paths_derived_correctly(tmp_path: Path):
    """State dir, artifact base, and audit dir derived from active proposal."""
    ws = _setup_multi_workspace(tmp_path, ["af263-042", "n244-012"], active="af263-042")
    from pes.adapters.workspace_resolver import resolve_workspace

    ctx = resolve_workspace(ws)
    state_str = str(ctx.state_dir).replace("\\", "/")
    artifact_str = str(ctx.artifact_base).replace("\\", "/")
    audit_str = str(ctx.audit_dir).replace("\\", "/")

    assert state_str.endswith("proposals/af263-042")
    assert artifact_str.endswith("artifacts/af263-042")
    assert "artifacts" in artifact_str  # kills mutant #33: "artifacts" → "XXartifactsXX"
    assert audit_str.endswith("proposals/af263-042/audit")


# --- Behavior 3: Legacy layout detection + root paths ---


def test_legacy_layout_detected(tmp_path: Path):
    """Legacy layout detected when root state exists without proposals/."""
    ws = _setup_legacy_workspace(tmp_path)
    from pes.adapters.workspace_resolver import resolve_workspace

    ctx = resolve_workspace(ws)
    assert ctx.layout == "legacy"
    assert ctx.is_legacy is True
    assert ctx.active_proposal is None
    assert Path(ctx.state_dir) == ws / ".sbir"
    assert Path(ctx.artifact_base) == ws / "artifacts"
    assert Path(ctx.audit_dir) == ws / ".sbir" / "audit"


# --- Behavior 4: Fresh workspace detection ---


def test_fresh_workspace_detected(tmp_path: Path):
    """Fresh workspace when neither .sbir/proposals/ nor root state exists."""
    from pes.adapters.workspace_resolver import resolve_workspace

    ctx = resolve_workspace(tmp_path)
    assert ctx.layout == "fresh"
    assert ctx.state_dir is None
    assert ctx.artifact_base is None
    assert ctx.is_legacy is False  # kills mutant #12: is_legacy=False → True


# --- Behavior 5: Missing active-proposal file ---


def test_missing_active_proposal_raises_with_available_list(tmp_path: Path):
    """Missing active-proposal in multi workspace produces error listing proposals."""
    ws = _setup_multi_workspace(tmp_path, ["af263-042", "n244-012"])
    from pes.adapters.workspace_resolver import WorkspaceResolutionError, resolve_workspace

    with pytest.raises(WorkspaceResolutionError, match="No active proposal selected"):
        resolve_workspace(ws)


# --- Behavior 6: Active proposal references nonexistent proposal ---


def test_nonexistent_active_proposal_raises_with_available_list(tmp_path: Path):
    """Active proposal pointing to nonexistent dir produces error."""
    ws = _setup_multi_workspace(tmp_path, ["af263-042"], active="xyz-999")
    from pes.adapters.workspace_resolver import WorkspaceResolutionError, resolve_workspace

    with pytest.raises(WorkspaceResolutionError, match="does not exist") as exc_info:
        resolve_workspace(ws)
    assert "Available proposals" in str(exc_info.value)
    assert "af263-042" in str(exc_info.value)


# --- Behavior 7: Empty/whitespace active-proposal file ---


@pytest.mark.parametrize(
    "content",
    [
        "",
        "   \n  ",
    ],
    ids=["empty", "whitespace-only"],
)
def test_empty_or_whitespace_active_proposal_raises(tmp_path: Path, content: str):
    """Empty or whitespace-only active-proposal file produces error."""
    ws = _setup_multi_workspace(tmp_path, ["af263-042"], active_content=content)
    from pes.adapters.workspace_resolver import WorkspaceResolutionError, resolve_workspace

    with pytest.raises(WorkspaceResolutionError, match="No active proposal selected"):
        resolve_workspace(ws)
