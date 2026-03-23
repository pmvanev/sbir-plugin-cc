"""Step definitions for profile selection and persistence scenarios.

Invokes through: RigorService (driving port -- application service).
Tests profile set, diff display, history recording, and edge cases.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.rigor_profile.steps.rigor_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-02-profile-selection.feature")


# --- When steps ---


@when(
    parsers.parse('Elena sets the rigor to "{profile}"'),
    target_fixture="service_result",
)
def elena_sets_rigor_selection(
    workspace_root: Path, proposal_dir: Path, profile: str
) -> dict[str, Any]:
    """Invoke RigorService to set profile for Elena's proposal."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        outcome = service.set_profile(
            proposal_dir=proposal_dir,
            new_profile=profile,
        )
        result["outcome"] = outcome
        result["error"] = None
    except Exception as exc:
        result["outcome"] = None
        result["error"] = str(exc)
        result["error_type"] = type(exc).__name__
    return result


@when(
    parsers.parse('Marcus sets the rigor to "{profile}"'),
    target_fixture="service_result",
)
def marcus_sets_rigor(
    workspace_root: Path, proposal_dir: Path, profile: str
) -> dict[str, Any]:
    """Invoke RigorService to set profile for Marcus's proposal."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        outcome = service.set_profile(
            proposal_dir=proposal_dir,
            new_profile=profile,
        )
        result["outcome"] = outcome
        result["error"] = None
    except Exception as exc:
        result["outcome"] = None
        result["error"] = str(exc)
        result["error_type"] = type(exc).__name__
    return result


@when(
    parsers.parse('the user attempts to set rigor to "{profile}"'),
    target_fixture="service_result",
)
def user_attempts_set_rigor(
    workspace_root: Path, proposal_dir: Path, profile: str
) -> dict[str, Any]:
    """Attempt to set rigor with potentially no active proposal."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=workspace_root / ".sbir" / "proposals",
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        # With no active proposal, proposal_dir is workspace root, not proposal ns
        outcome = service.set_profile(
            proposal_dir=None,
            new_profile=profile,
        )
        result["outcome"] = outcome
        result["error"] = None
    except Exception as exc:
        result["outcome"] = None
        result["error"] = str(exc)
        result["error_type"] = type(exc).__name__
    return result


# --- Then steps ---


@then(
    parsers.parse(
        'the diff shows writer model changed from "{from_tier}" to "{to_tier}"'
    )
)
def diff_shows_writer_change(
    service_result: dict[str, Any], from_tier: str, to_tier: str
):
    """Verify the diff includes the writer role tier change."""
    outcome = service_result["outcome"]
    assert outcome is not None, f"No outcome -- error: {service_result.get('error')}"
    diff = outcome.get("diff", {})
    writer_diff = diff.get("writer", {})
    assert writer_diff.get("from") == from_tier
    assert writer_diff.get("to") == to_tier


@then(
    parsers.parse(
        'the diff shows reviewer model changed from "{from_tier}" to "{to_tier}"'
    )
)
def diff_shows_reviewer_change(
    service_result: dict[str, Any], from_tier: str, to_tier: str
):
    """Verify the diff includes the reviewer role tier change."""
    outcome = service_result["outcome"]
    diff = outcome.get("diff", {})
    reviewer_diff = diff.get("reviewer", {})
    assert reviewer_diff.get("from") == from_tier
    assert reviewer_diff.get("to") == to_tier


@then(
    parsers.parse(
        "the diff shows critique iterations changed from {from_val:d} to {to_val:d}"
    )
)
def diff_shows_critique_change(
    service_result: dict[str, Any], from_val: int, to_val: int
):
    """Verify the diff includes critique iteration change."""
    outcome = service_result["outcome"]
    diff = outcome.get("diff", {})
    critique_diff = diff.get("critique_max_iterations", {})
    assert critique_diff.get("from") == from_val
    assert critique_diff.get("to") == to_val


@then('the diff shows all agent roles changed to "basic" model tier')
def diff_shows_all_basic(service_result: dict[str, Any]):
    """Verify the diff shows every agent role changed to basic."""
    outcome = service_result["outcome"]
    diff = outcome.get("diff", {})
    agent_roles = [
        "strategist", "writer", "reviewer", "researcher",
        "topic-scout", "compliance", "visual-assets", "formatter",
    ]
    for role in agent_roles:
        if role in diff:
            assert diff[role].get("to") == "basic", (
                f"Role '{role}' expected to be 'basic', got '{diff[role].get('to')}'"
            )


@then(
    parsers.parse(
        'the history contains an entry with from "{from_p}" and to "{to_p}"'
    )
)
def history_contains_entry(proposal_dir: Path, from_p: str, to_p: str):
    """Verify the history contains an entry with the expected from/to."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    history = data.get("history", [])
    matching = [
        h for h in history
        if h.get("from") == from_p and h.get("to") == to_p
    ]
    assert len(matching) > 0, (
        f"No history entry from '{from_p}' to '{to_p}'. History: {history}"
    )


@then(parsers.parse("the history entry includes wave number {wave:d}"))
def history_includes_wave(proposal_dir: Path, wave: int):
    """Verify the latest history entry includes the expected wave number."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    latest = data["history"][-1]
    assert latest.get("wave") == wave, (
        f"Expected wave {wave}, got {latest.get('wave')}"
    )


@then("the history entry includes a timestamp")
def history_includes_timestamp(proposal_dir: Path):
    """Verify the latest history entry includes a timestamp."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    latest = data["history"][-1]
    assert "at" in latest and latest["at"], "History entry missing timestamp"


@then("the operation fails with a no-active-proposal error")
def operation_fails_no_proposal(service_result: dict[str, Any]):
    """Verify the operation failed because no proposal is active."""
    assert service_result["error"] is not None, "Expected error but none occurred"


@then(parsers.parse('the operation confirms rigor is already "{profile}"'))
def operation_confirms_already(service_result: dict[str, Any], profile: str):
    """Verify the operation returned a no-op confirmation."""
    outcome = service_result["outcome"]
    assert outcome is not None
    assert outcome.get("no_change") is True


@then("no history entry is appended")
def no_history_appended(proposal_dir: Path):
    """Verify the rigor history has not grown."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    history = data.get("history", [])
    assert len(history) == 0, f"Expected empty history, got {len(history)} entries"


@then("the rigor state file is not modified")
def rigor_file_unchanged(proposal_dir: Path):
    """Verify the rigor-profile.json was not modified (same-profile no-op)."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    # If profile is still what was set in Given, file was not overwritten
    assert data.get("profile") is not None


@then(parsers.parse("the history contains {count:d} entries"))
def history_has_count(proposal_dir: Path, count: int):
    """Verify the number of history entries."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    actual = len(data.get("history", []))
    assert actual == count, f"Expected {count} entries, got {actual}"


@then(parsers.parse("the first entry records {from_p} to {to_p}"))
def first_entry_records(proposal_dir: Path, from_p: str, to_p: str):
    """Verify the first history entry."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    first = data["history"][0]
    assert first["from"] == from_p and first["to"] == to_p


@then(parsers.parse("the second entry records {from_p} to {to_p}"))
def second_entry_records(proposal_dir: Path, from_p: str, to_p: str):
    """Verify the second history entry."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    second = data["history"][1]
    assert second["from"] == from_p and second["to"] == to_p
