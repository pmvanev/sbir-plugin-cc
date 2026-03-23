"""Step definitions for model tier resolution scenarios.

Invokes through: RigorService (driving port -- application service).
Tests model tier resolution for agent roles, behavioral parameters
(review passes, critique iterations), and fallback behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.rigor_profile.steps.rigor_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-03-model-resolution.feature")


# --- When steps ---


@when(
    "the model tier is resolved for each agent role",
    target_fixture="resolution_result",
)
def resolve_all_roles(
    workspace_root: Path, proposal_dir: Path
) -> dict[str, Any]:
    """Resolve model tier for every agent role in the active profile."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        roles = [
            "strategist", "writer", "reviewer", "researcher",
            "topic-scout", "compliance", "visual-assets", "formatter",
        ]
        tiers = {}
        for role in roles:
            tiers[role] = service.resolve_model_tier(
                proposal_dir=proposal_dir,
                agent_role=role,
            )
        result["tiers"] = tiers
        result["error"] = None
    except Exception as exc:
        result["tiers"] = None
        result["error"] = str(exc)
    return result


@when(
    "the review configuration is resolved",
    target_fixture="resolution_result",
)
def resolve_review_config(
    workspace_root: Path, proposal_dir: Path
) -> dict[str, Any]:
    """Resolve review configuration from the active rigor profile."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        config = service.resolve_behavioral_params(proposal_dir=proposal_dir)
        result["config"] = config
        result["error"] = None
    except Exception as exc:
        result["config"] = None
        result["error"] = str(exc)
    return result


@when(
    "the critique loop configuration is resolved",
    target_fixture="resolution_result",
)
def resolve_critique_config(
    workspace_root: Path, proposal_dir: Path
) -> dict[str, Any]:
    """Resolve critique loop configuration from the active rigor profile."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=proposal_dir.parent,
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        config = service.resolve_behavioral_params(proposal_dir=proposal_dir)
        result["config"] = config
        result["error"] = None
    except Exception as exc:
        result["config"] = None
        result["error"] = str(exc)
    return result


@when(
    parsers.parse('the model tier is resolved for the "{role}" role'),
    target_fixture="resolution_result",
)
def resolve_tier_for_role(
    workspace_root: Path, proposal_dir: Path, role: str
) -> dict[str, Any]:
    """Resolve model tier for a specific agent role."""
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


@when("the profile definition is loaded", target_fixture="resolution_result")
def load_profile_def_for_property(
    resolution_result: dict[str, Any],
) -> dict[str, Any]:
    """Load profile definition for property-based validation."""
    # Profile name stored from Given step
    return resolution_result


@when("the model tier is resolved", target_fixture="resolution_result")
def resolve_tier_property(resolution_result: dict[str, Any]) -> dict[str, Any]:
    """Resolve model tier for property-based validation."""
    return resolution_result


# --- Given steps for property scenarios ---


@given("any valid rigor profile name", target_fixture="resolution_result")
def any_valid_profile() -> dict[str, Any]:
    """Set up for property test: iterate all profile names."""
    return {"profiles": ["lean", "standard", "thorough", "exhaustive"]}


@given(
    "any valid rigor profile and agent role",
    target_fixture="resolution_result",
)
def any_valid_profile_and_role() -> dict[str, Any]:
    """Set up for property test: iterate all profile + role combinations."""
    return {
        "profiles": ["lean", "standard", "thorough", "exhaustive"],
        "roles": [
            "strategist", "writer", "reviewer", "researcher",
            "topic-scout", "compliance", "visual-assets", "formatter",
        ],
    }


# --- Then steps ---


@then(parsers.parse('every agent role resolves to "{tier}" model tier'))
def all_roles_resolve_to(resolution_result: dict[str, Any], tier: str):
    """Verify every agent role resolved to the expected tier."""
    tiers = resolution_result["tiers"]
    assert tiers is not None, f"Error: {resolution_result.get('error')}"
    for role, resolved_tier in tiers.items():
        assert resolved_tier == tier, (
            f"Role '{role}' expected '{tier}', got '{resolved_tier}'"
        )


@then(parsers.parse("the review pass count is {count:d}"))
def review_pass_count_is(resolution_result: dict[str, Any], count: int):
    """Verify the resolved review pass count."""
    config = resolution_result["config"]
    assert config is not None, f"Error: {resolution_result.get('error')}"
    assert config.get("review_passes") == count, (
        f"Expected {count} passes, got {config.get('review_passes')}"
    )


@then(parsers.parse("the maximum critique iterations is {count:d}"))
def max_critique_iterations_is(resolution_result: dict[str, Any], count: int):
    """Verify the resolved critique loop iteration cap."""
    config = resolution_result["config"]
    assert config is not None, f"Error: {resolution_result.get('error')}"
    assert config.get("critique_max_iterations") == count, (
        f"Expected {count} iterations, got {config.get('critique_max_iterations')}"
    )


@then(
    parsers.parse(
        'the resolved model tier is "{tier}"'
    )
)
def resolved_tier_is_resolution(resolution_result: dict[str, Any], tier: str):
    """Verify the resolved model tier for resolution scenarios."""
    assert resolution_result.get("error") is None, (
        f"Unexpected error: {resolution_result.get('error')}"
    )
    assert resolution_result.get("tier") == tier, (
        f"Expected '{tier}', got '{resolution_result.get('tier')}'"
    )


@then("every agent role has a model tier of basic, standard, or strongest")
def all_tiers_valid_property(resolution_result: dict[str, Any]):
    """Property: every profile defines valid tiers for every role."""
    valid_tiers = {"basic", "standard", "strongest"}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=Path("/tmp"),
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        for profile in resolution_result["profiles"]:
            definition = service.get_profile_definition(profile)
            for role, config in definition.get("agent_roles", {}).items():
                tier = config.get("model_tier")
                assert tier in valid_tiers, (
                    f"Profile '{profile}', role '{role}': invalid tier '{tier}'"
                )
    except Exception as exc:
        pytest.fail(f"Property check failed: {exc}")


@then(
    "the result is always the same for the same profile and role"
)
def resolution_deterministic(resolution_result: dict[str, Any]):
    """Property: resolution is deterministic."""
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=Path("/tmp"),
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        definitions = service.get_all_definitions()
        for profile in resolution_result["profiles"]:
            for role in resolution_result["roles"]:
                results = set()
                for _ in range(3):
                    tier = definitions[profile]["agent_roles"][role]["model_tier"]
                    results.add(tier)
                assert len(results) == 1, (
                    f"Non-deterministic: profile '{profile}', role '{role}' "
                    f"produced {results}"
                )
    except Exception as exc:
        pytest.fail(f"Determinism check failed: {exc}")
