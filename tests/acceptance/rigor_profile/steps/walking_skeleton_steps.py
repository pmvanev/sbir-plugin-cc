"""Step definitions for walking skeleton scenarios.

Invokes through: RigorService (driving port -- application service).
The rigor service orchestrates profile validation, persistence, and
resolution through port interfaces.

Note: The RigorService and supporting domain objects do not exist yet.
Step definitions reference the expected public interface. The
software-crafter will implement these to satisfy the tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.rigor_profile.steps.rigor_common_steps import *  # noqa: F403

# Link feature files
scenarios("../walking-skeleton.feature")


# --- When steps ---


@when(
    parsers.parse('Elena sets the rigor to "{profile}"'),
    target_fixture="service_result",
)
def elena_sets_rigor(
    workspace_root: Path, proposal_dir: Path, profile: str
) -> dict[str, Any]:
    """Invoke RigorService to set profile for the active proposal.

    Invokes through the RigorService driving port.
    """
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


@when("Phil reads the active rigor profile", target_fixture="service_result")
def phil_reads_rigor(
    workspace_root: Path, proposal_dir: Path
) -> dict[str, Any]:
    """Invoke RigorService to read the active rigor profile."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        profile = service.get_active_profile(proposal_dir=proposal_dir)
        result["profile"] = profile
        result["error"] = None
    except Exception as exc:
        result["profile"] = None
        result["error"] = str(exc)
    return result


@when(
    parsers.parse('the model tier is resolved for the "{role}" role'),
    target_fixture="resolution_result",
)
def resolve_model_tier_for_role(
    workspace_root: Path, proposal_dir: Path, role: str
) -> dict[str, Any]:
    """Invoke RigorService to resolve model tier for a specific agent role."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        tier = service.resolve_model_tier(
            proposal_dir=proposal_dir,
            agent_role=role,
        )
        result["tier"] = tier
        result["error"] = None
    except Exception as exc:
        result["tier"] = None
        result["error"] = str(exc)
    return result


# --- Then steps ---


@then(parsers.parse('the active rigor profile is "{profile}"'))
def rigor_profile_is(proposal_dir: Path, profile: str):
    """Verify the persisted rigor profile matches expected value."""
    rigor_path = proposal_dir / "rigor-profile.json"
    assert rigor_path.exists(), f"rigor-profile.json not found at {rigor_path}"
    data = json.loads(rigor_path.read_text())
    assert data["profile"] == profile, (
        f"Expected profile '{profile}', got '{data['profile']}'"
    )


@then(
    parsers.parse(
        'the change from "{old_profile}" to "{new_profile}" is recorded in history'
    )
)
def change_recorded_in_history(proposal_dir: Path, old_profile: str, new_profile: str):
    """Verify the rigor history contains the expected change entry."""
    rigor_path = proposal_dir / "rigor-profile.json"
    data = json.loads(rigor_path.read_text())
    history = data.get("history", [])
    assert len(history) > 0, "History is empty -- no change recorded"
    latest = history[-1]
    assert latest["from"] == old_profile, (
        f"Expected from '{old_profile}', got '{latest['from']}'"
    )
    assert latest["to"] == new_profile, (
        f"Expected to '{new_profile}', got '{latest['to']}'"
    )


@then(parsers.parse('the rigor profile resolves to "{profile}"'))
def rigor_resolves_to(service_result: dict[str, Any], profile: str):
    """Verify the resolved profile matches expected value."""
    assert service_result["error"] is None, (
        f"Unexpected error: {service_result['error']}"
    )
    resolved = service_result["profile"]
    assert resolved == profile, f"Expected '{profile}', got '{resolved}'"


@then("no error is reported")
def no_error_reported(service_result: dict[str, Any]):
    """Verify no error occurred during the operation."""
    assert service_result["error"] is None, (
        f"Unexpected error: {service_result['error']}"
    )


@then(parsers.parse('the resolved model tier is "{tier}"'))
def resolved_tier_is(resolution_result: dict[str, Any], tier: str):
    """Verify the resolved model tier matches expected value."""
    assert resolution_result["error"] is None, (
        f"Unexpected error: {resolution_result['error']}"
    )
    assert resolution_result["tier"] == tier, (
        f"Expected tier '{tier}', got '{resolution_result['tier']}'"
    )
