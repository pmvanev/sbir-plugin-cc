"""Step definitions for profile validation and registry scenarios.

Invokes through: RigorService and domain validators (driving ports).
Tests profile name validation, definition completeness, and model tier validity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.rigor_profile.steps.rigor_common_steps import *  # noqa: F403

# Link feature files
scenarios("../milestone-01-profile-validation.feature")


# --- When steps ---


@when(
    parsers.parse(
        'each profile name is validated: "{p1}", "{p2}", "{p3}", "{p4}"'
    ),
    target_fixture="service_result",
)
def validate_all_profile_names(
    p1: str, p2: str, p3: str, p4: str
) -> dict[str, Any]:
    """Validate each profile name through the domain validator."""
    result: dict[str, Any] = {"valid": [], "invalid": []}
    try:
        from pes.domain.rigor import validate_profile_name

        for name in [p1, p2, p3, p4]:
            if validate_profile_name(name):
                result["valid"].append(name)
            else:
                result["invalid"].append(name)
        result["error"] = None
    except Exception as exc:
        result["error"] = str(exc)
    return result


@when(
    parsers.parse('Elena sets the rigor to "{profile}"'),
    target_fixture="service_result",
)
def elena_sets_rigor_validation(
    workspace_root: Path, proposal_dir: Path, profile: str
) -> dict[str, Any]:
    """Invoke RigorService to set profile -- validation focused."""
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
    parsers.parse('the "{profile}" profile definition is loaded'),
    target_fixture="service_result",
)
def load_profile_definition(profile: str) -> dict[str, Any]:
    """Load a specific profile definition from plugin config."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=Path("/tmp"),  # not needed for definition read
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        definition = service.get_profile_definition(profile)
        result["definition"] = definition
        result["error"] = None
    except Exception as exc:
        result["definition"] = None
        result["error"] = str(exc)
    return result


@when("all profile definitions are loaded", target_fixture="service_result")
def load_all_definitions() -> dict[str, Any]:
    """Load all profile definitions."""
    result: dict[str, Any] = {}
    try:
        from pes.domain.rigor_service import RigorService
        from pes.adapters.filesystem_rigor_adapter import FileSystemRigorAdapter

        adapter = FileSystemRigorAdapter(
            proposals_dir=Path("/tmp"),
            plugin_config_dir=Path(__file__).parents[4] / "config",
        )
        service = RigorService(adapter)
        definitions = service.get_all_definitions()
        result["definitions"] = definitions
        result["error"] = None
    except Exception as exc:
        result["definitions"] = None
        result["error"] = str(exc)
    return result


# --- Then steps ---


@then("all four are accepted as valid")
def all_four_valid(service_result: dict[str, Any]):
    """Verify all four profile names were accepted."""
    assert service_result["error"] is None
    assert len(service_result["valid"]) == 4
    assert len(service_result["invalid"]) == 0


@then("the operation fails with an invalid profile error")
def operation_fails_invalid_profile(service_result: dict[str, Any]):
    """Verify the operation produced an invalid profile error."""
    assert service_result["error"] is not None, "Expected error but none occurred"


@then(parsers.parse('the error message includes "{text}"'))
def error_includes_text(service_result: dict[str, Any], text: str):
    """Verify the error message contains the expected text."""
    assert text in service_result["error"], (
        f"Expected '{text}' in error: {service_result['error']}"
    )


@then(
    parsers.parse(
        "the error lists available profiles: {p1}, {p2}, {p3}, {p4}"
    )
)
def error_lists_profiles(
    service_result: dict[str, Any], p1: str, p2: str, p3: str, p4: str
):
    """Verify the error message lists all available profiles."""
    error = service_result["error"]
    for name in [p1, p2, p3, p4]:
        assert name in error, f"Expected '{name}' in error: {error}"


@then(parsers.parse("the profile includes model tier for {role}"))
def profile_includes_role(service_result: dict[str, Any], role: str):
    """Verify the profile definition includes the specified agent role."""
    definition = service_result["definition"]
    assert definition is not None, "Profile definition not loaded"
    agent_roles = definition.get("agent_roles", {})
    assert role in agent_roles, (
        f"Role '{role}' not found in profile. Roles: {list(agent_roles.keys())}"
    )


@then("every model tier value is one of: basic, standard, strongest")
def all_tiers_valid(service_result: dict[str, Any]):
    """Verify every model tier in every profile is a valid value."""
    valid_tiers = {"basic", "standard", "strongest"}
    definitions = service_result["definitions"]
    assert definitions is not None
    for profile_name, profile_def in definitions.items():
        for role, config in profile_def.get("agent_roles", {}).items():
            tier = config.get("model_tier")
            assert tier in valid_tiers, (
                f"Profile '{profile_name}', role '{role}': "
                f"invalid tier '{tier}'. Must be one of {valid_tiers}"
            )
