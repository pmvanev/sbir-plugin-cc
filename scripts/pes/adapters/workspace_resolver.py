"""Workspace path resolution for PES hooks.

Detects workspace layout (multi/legacy/fresh), reads active-proposal pointer,
and derives state_dir and artifact_base paths. Pure function: CWD input, paths output.

Consumer: hook_adapter.main() only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkspaceContext:
    """Resolved workspace paths and layout metadata."""

    layout: str  # "multi" | "legacy" | "fresh"
    state_dir: Path | None
    artifact_base: Path | None
    audit_dir: Path | None
    active_proposal: str | None
    is_legacy: bool


class WorkspaceResolutionError(Exception):
    """Raised when workspace path resolution fails."""


def resolve_workspace(workspace_root: Path) -> WorkspaceContext:
    """Resolve workspace layout and derive paths.

    Args:
        workspace_root: Path to the project workspace root directory.

    Returns:
        WorkspaceContext with resolved paths.

    Raises:
        WorkspaceResolutionError: If multi-proposal workspace has no valid
            active-proposal pointer.
    """
    sbir_dir = workspace_root / ".sbir"
    proposals_dir = sbir_dir / "proposals"

    # Multi-proposal layout: .sbir/proposals/ exists
    if proposals_dir.is_dir():
        return _resolve_multi(workspace_root, sbir_dir, proposals_dir)

    # Legacy layout: .sbir/proposal-state.json at root without proposals/
    if (sbir_dir / "proposal-state.json").is_file():
        return _resolve_legacy(workspace_root, sbir_dir)

    # Fresh workspace: neither exists
    return WorkspaceContext(
        layout="fresh",
        state_dir=None,
        artifact_base=None,
        audit_dir=None,
        active_proposal=None,
        is_legacy=False,
    )


def _resolve_multi(
    workspace_root: Path, sbir_dir: Path, proposals_dir: Path
) -> WorkspaceContext:
    """Resolve paths for multi-proposal layout."""
    active_file = sbir_dir / "active-proposal"
    available = sorted(
        d.name for d in proposals_dir.iterdir() if d.is_dir()
    )

    if not active_file.is_file():
        raise WorkspaceResolutionError(
            f"No active proposal selected. Available proposals: {', '.join(available)}"
        )

    topic_id = active_file.read_text().strip()

    if not topic_id:
        raise WorkspaceResolutionError(
            f"No active proposal selected. Available proposals: {', '.join(available)}"
        )

    proposal_dir = proposals_dir / topic_id
    if not proposal_dir.is_dir():
        raise WorkspaceResolutionError(
            f"Active proposal '{topic_id}' does not exist. "
            f"Available proposals: {', '.join(available)}"
        )

    return WorkspaceContext(
        layout="multi",
        state_dir=proposals_dir / topic_id,
        artifact_base=workspace_root / "artifacts" / topic_id,
        audit_dir=proposals_dir / topic_id / "audit",
        active_proposal=topic_id,
        is_legacy=False,
    )


def _resolve_legacy(workspace_root: Path, sbir_dir: Path) -> WorkspaceContext:
    """Resolve paths for legacy single-proposal layout."""
    return WorkspaceContext(
        layout="legacy",
        state_dir=sbir_dir,
        artifact_base=workspace_root / "artifacts",
        audit_dir=sbir_dir / "audit",
        active_proposal=None,
        is_legacy=True,
    )
