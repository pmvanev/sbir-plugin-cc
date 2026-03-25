"""CLI for submitting developer feedback on the SBIR proposal plugin.

This is the entry point that agents call via Bash. It wires all adapters
and services internally -- callers just pass flags and read JSON output.

Commands:
  save    -- Capture and persist a feedback entry with context snapshot

Examples:
  python scripts/sbir_feedback_cli.py save --type quality --ratings '{"past_performance": 2}' --free-text "Wrong project selected"
  python scripts/sbir_feedback_cli.py save --type bug --free-text "CLI crashed on empty profile"
  python scripts/sbir_feedback_cli.py save --type suggestion
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pes.adapters.filesystem_feedback_adapter import FilesystemFeedbackAdapter
from pes.adapters.filesystem_rigor_adapter import FilesystemRigorAdapter
from pes.adapters.json_finder_results_adapter import JsonFinderResultsAdapter
from pes.adapters.json_profile_adapter import JsonProfileAdapter
from pes.adapters.json_state_adapter import JsonStateAdapter
from pes.domain.feedback import FeedbackEntry, FeedbackType, QualityRatings
from pes.domain.feedback_service import FeedbackSnapshotService

VALID_FEEDBACK_TYPES = {ft.value for ft in FeedbackType}


def _read_json_file(path: Path) -> dict[str, Any] | None:
    """Read and parse a JSON file, returning None on any error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _get_file_mtime(path: Path) -> float | None:
    """Return file mtime as float seconds, or None if file absent/unreadable."""
    try:
        return path.stat().st_mtime
    except Exception:  # noqa: BLE001
        return None


def _resolve_active_proposal_dir(state_dir: Path) -> Path | None:
    """Find the active proposal directory via active-proposal.json pointer."""
    active_file = state_dir / "active-proposal.json"
    data = _read_json_file(active_file)
    if data is None:
        return None
    proposal_name = data.get("active_proposal")
    if not proposal_name:
        return None
    proposal_dir = state_dir / "proposals" / proposal_name
    if proposal_dir.is_dir():
        return proposal_dir
    return None


def _load_state(state_dir: Path) -> dict[str, Any] | None:
    """Load proposal-state.json for the active proposal, degrading to None on any error."""
    proposal_dir = _resolve_active_proposal_dir(state_dir)
    if proposal_dir is None:
        return None
    try:
        adapter = JsonStateAdapter(str(proposal_dir))
        return adapter.load()
    except Exception:  # noqa: BLE001
        return None


def _load_rigor(state_dir: Path) -> dict[str, Any] | None:
    """Load rigor-profile.json for the active proposal, degrading to None on any error."""
    proposal_dir = _resolve_active_proposal_dir(state_dir)
    if proposal_dir is None:
        return None
    try:
        adapter = FilesystemRigorAdapter()
        return adapter.read_active_profile(proposal_dir)
    except Exception:  # noqa: BLE001
        return None


def _load_profile(profile_path: Path) -> dict[str, Any] | None:
    """Load company-profile.json, degrading to None on any error."""
    try:
        adapter = JsonProfileAdapter(str(profile_path.parent))
        return adapter.read()
    except Exception:  # noqa: BLE001
        return None


def _load_finder(state_dir: Path) -> dict[str, Any] | None:
    """Load finder-results.json, degrading to None on any error."""
    try:
        adapter = JsonFinderResultsAdapter(str(state_dir))
        return adapter.read()
    except Exception:  # noqa: BLE001
        return None


def _build_mtimes(state_dir: Path, profile_path: Path) -> dict[str, float | None]:
    """Collect mtimes for state, profile, and finder files."""
    proposal_dir = _resolve_active_proposal_dir(state_dir)
    state_file = (proposal_dir / "proposal-state.json") if proposal_dir else None
    finder_file = state_dir / "finder-results.json"

    return {
        "state": _get_file_mtime(state_file) if state_file else None,
        "profile": _get_file_mtime(profile_path),
        "finder": _get_file_mtime(finder_file),
    }


def _parse_ratings(ratings_json: str | None) -> QualityRatings:
    """Parse ratings JSON string into QualityRatings, defaulting all to None."""
    if not ratings_json:
        return QualityRatings()
    try:
        data = json.loads(ratings_json)
    except (json.JSONDecodeError, ValueError):
        return QualityRatings()
    return QualityRatings(
        past_performance=data.get("past_performance"),
        image_quality=data.get("image_quality"),
        writing_quality=data.get("writing_quality"),
        topic_scoring=data.get("topic_scoring"),
    )


def cmd_save(args: argparse.Namespace) -> None:
    """Assemble and persist a feedback entry with full context snapshot."""
    # Validate feedback type
    if args.type not in VALID_FEEDBACK_TYPES:
        print(
            f"Error: unrecognized feedback type '{args.type}'. "
            f"Valid types: {', '.join(sorted(VALID_FEEDBACK_TYPES))}",
            file=sys.stderr,
        )
        sys.exit(1)

    feedback_type = FeedbackType(args.type)
    state_dir = Path(args.state_dir)
    profile_path = Path(args.profile_path)
    feedback_dir = Path(args.feedback_dir)

    # Load all context data — all degrade to None gracefully
    state_dict = _load_state(state_dir)
    rigor_dict = _load_rigor(state_dir)
    profile_dict = _load_profile(profile_path)
    finder_dict = _load_finder(state_dir)
    mtimes_dict = _build_mtimes(state_dir, profile_path)

    # Build context snapshot
    snapshot_service = FeedbackSnapshotService()
    snapshot = snapshot_service.build_snapshot(
        state=state_dict,
        rigor=rigor_dict,
        profile=profile_dict,
        finder=finder_dict,
        mtimes=mtimes_dict,
        cwd=str(Path.cwd()),
    )

    # Build feedback entry
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    feedback_id = f"feedback-{timestamp.replace(':', '-')}"
    ratings = _parse_ratings(getattr(args, "ratings", None))
    free_text = getattr(args, "free_text", None) or None

    entry = FeedbackEntry(
        feedback_id=feedback_id,
        timestamp=timestamp,
        type=feedback_type,
        ratings=ratings,
        free_text=free_text,
        context_snapshot=snapshot,
    )

    # Persist
    writer = FilesystemFeedbackAdapter()
    file_path = writer.write(entry, feedback_dir)

    # Output JSON result
    output = {
        "feedback_id": file_path.stem,
        "file_path": str(file_path),
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")


# --- Argument parsing ---


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SBIR developer feedback capture CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_save = sub.add_parser("save", help="Capture and persist a feedback entry")
    p_save.add_argument("--type", required=True,
                        help=f"Feedback type: {', '.join(sorted(VALID_FEEDBACK_TYPES))}")
    p_save.add_argument("--ratings", type=str, default=None,
                        help="Quality ratings as JSON string, e.g. '{\"past_performance\": 3}'")
    p_save.add_argument("--free-text", type=str, default=None,
                        help="Optional free-text feedback comment")
    p_save.add_argument("--state-dir", type=str, default=str(Path(".sbir")),
                        help="Path to .sbir state directory")
    p_save.add_argument("--profile-path", type=str,
                        default=str(Path.home() / ".sbir" / "company-profile.json"),
                        help="Path to company-profile.json")
    p_save.add_argument("--feedback-dir", type=str,
                        default=str(Path(".sbir") / "feedback"),
                        help="Directory to write feedback files")

    args = parser.parse_args()

    commands = {
        "save": cmd_save,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
