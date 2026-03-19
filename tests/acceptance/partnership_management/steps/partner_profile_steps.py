"""Step definitions for partner profile creation, validation, and persistence.

Invokes through:
- PartnerProfileValidationService (schema validation -- to be created)
- Partner profile read/write via filesystem adapter

Does NOT import internal validators or schema internals directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.partnership_management.conftest import make_partner_profile

# Link to feature files
scenarios("../milestone-01-partner-profile.feature")


# --- Fixtures ---


@pytest.fixture()
def partner_draft() -> dict[str, Any]:
    """Mutable container for partner profile being built during interview steps."""
    return {}


# --- Given steps ---


@given("the partner profile validation service is available")
def validation_service_available():
    """Confirm validation service can be instantiated."""
    # Service will be imported here once implemented
    # from pes.domain.partner_profile_validation import PartnerProfileValidationService
    pass


@given("Phil has no partner profiles on file")
def no_partner_profiles(partners_dir: Path):
    """Ensure partners directory is empty."""
    for f in partners_dir.glob("*.json"):
        f.unlink()
    assert len(list(partners_dir.glob("*.json"))) == 0


@given(
    parsers.parse(
        'Phil has prepared a complete partner profile for "{name}" as a {institution_type}'
    ),
)
def prepared_complete_profile(
    name: str,
    institution_type: str,
    partner_draft: dict[str, Any],
):
    """Build a partner profile draft with the given name and type."""
    type_map = {
        "university": "university",
        "federally funded R&D center": "federally_funded_rdc",
        "nonprofit research": "nonprofit_research",
    }
    partner_draft.update(
        make_partner_profile(
            partner_name=name,
            partner_type=type_map.get(institution_type, institution_type),
        )
    )


@given(
    parsers.parse(
        'the profile includes capabilities "{capabilities}"'
    ),
)
def profile_capabilities(capabilities: str, partner_draft: dict[str, Any]):
    """Set capabilities on the profile draft."""
    partner_draft["capabilities"] = [c.strip() for c in capabilities.split(",")]


@given(parsers.parse("the profile includes {count:d} capabilities"))
def profile_n_capabilities(count: int, partner_draft: dict[str, Any]):
    """Set N capabilities on the profile draft."""
    partner_draft["capabilities"] = [f"capability-{i}" for i in range(1, count + 1)]


@given(
    parsers.parse(
        'the profile includes key personnel "{name}" as {role} '
        'with expertise "{expertise}"'
    ),
)
def profile_key_personnel(
    name: str, role: str, expertise: str, partner_draft: dict[str, Any]
):
    """Add key personnel to the profile draft."""
    entry = {
        "name": name,
        "role": role,
        "expertise": [e.strip() for e in expertise.split(",")],
    }
    partner_draft.setdefault("key_personnel", []).append(entry)


@given(parsers.parse("the profile includes {count:d} key personnel entries"))
def profile_n_personnel(count: int, partner_draft: dict[str, Any]):
    """Set N key personnel entries."""
    partner_draft["key_personnel"] = [
        {"name": f"Dr. Person {i}", "role": "Researcher", "expertise": [f"field-{i}"]}
        for i in range(1, count + 1)
    ]


@given(parsers.parse('the profile includes facility "{name}"'))
def profile_facility(name: str, partner_draft: dict[str, Any]):
    """Add a facility to the profile draft."""
    partner_draft.setdefault("facilities", []).append(
        {"name": name, "description": ""}
    )


@given(parsers.parse("the profile includes {count:d} facility"))
def profile_n_facilities(count: int, partner_draft: dict[str, Any]):
    """Set N facilities."""
    partner_draft["facilities"] = [
        {"name": f"facility-{i}", "description": ""} for i in range(1, count + 1)
    ]


@given(
    parsers.parse(
        'the profile includes a past collaboration with "{agency}" '
        'on "{area}" with outcome "{outcome}"'
    ),
)
def profile_past_collab(
    agency: str, area: str, outcome: str, partner_draft: dict[str, Any]
):
    """Add past collaboration."""
    partner_draft.setdefault("past_collaborations", []).append(
        {"agency": agency, "topic_area": area, "outcome": outcome}
    )


@given(parsers.parse("the profile includes {count:d} past collaboration"))
def profile_n_collabs(count: int, partner_draft: dict[str, Any]):
    """Set N past collaborations."""
    partner_draft["past_collaborations"] = [
        {"agency": f"agency-{i}", "topic_area": f"area-{i}", "outcome": "WIN"}
        for i in range(1, count + 1)
    ]


@given(
    parsers.parse(
        "the profile includes STTR eligibility as qualifying with minimum effort capable"
    ),
)
def profile_sttr_eligible(partner_draft: dict[str, Any]):
    """Set STTR eligibility to qualifying."""
    partner_draft["sttr_eligibility"] = {
        "qualifies": True,
        "minimum_effort_capable": True,
        "notes": "",
    }


@given(parsers.parse("the profile includes STTR eligibility as qualifying"))
def profile_sttr_eligible_basic(partner_draft: dict[str, Any]):
    """Set STTR eligibility to qualifying (basic)."""
    partner_draft["sttr_eligibility"] = {
        "qualifies": True,
        "minimum_effort_capable": True,
        "notes": "",
    }


# --- When steps ---


@when("Phil submits the partner profile for validation and saving")
def submit_for_validation_and_save(
    partner_draft: dict[str, Any],
    partners_dir: Path,
    partnership_context: dict[str, Any],
):
    """Validate and save the partner profile through the driving port.

    TODO: Replace with PartnerProfileValidationService call once implemented.
    For now, performs basic schema validation inline.
    """
    errors = _validate_partner_profile(partner_draft)
    partnership_context["validation_errors"] = errors

    if not errors:
        slug = partner_draft.get("partner_slug", "unknown")
        path = partners_dir / f"{slug}.json"
        path.write_text(json.dumps(partner_draft, indent=2))
        partnership_context["saved_path"] = path
        partnership_context["saved"] = True
    else:
        partnership_context["saved"] = False


@when("Phil submits the partner profile for validation")
def submit_for_validation_only(
    partner_draft: dict[str, Any],
    partnership_context: dict[str, Any],
):
    """Validate without saving.

    TODO: Replace with PartnerProfileValidationService call once implemented.
    """
    errors = _validate_partner_profile(partner_draft)
    partnership_context["validation_errors"] = errors
    partnership_context["saved"] = False


@when("the partner profile is validated and saved")
def validate_and_save(
    partner_draft: dict[str, Any],
    partners_dir: Path,
    partnership_context: dict[str, Any],
):
    """Validate and persist partner profile."""
    errors = _validate_partner_profile(partner_draft)
    partnership_context["validation_errors"] = errors

    if not errors:
        slug = partner_draft.get("partner_slug", "unknown")
        path = partners_dir / f"{slug}.json"
        path.write_text(json.dumps(partner_draft, indent=2))
        partnership_context["saved_path"] = path
        partnership_context["saved"] = True


@when("the partner profile is reloaded from disk")
def reload_profile(partnership_context: dict[str, Any]):
    """Reload profile from saved path."""
    path = partnership_context["saved_path"]
    partnership_context["reloaded"] = json.loads(path.read_text())


# --- Then steps ---


@then("the partner profile passes validation with no errors")
def validation_passes(partnership_context: dict[str, Any]):
    """Assert zero validation errors."""
    errors = partnership_context.get("validation_errors", [])
    assert len(errors) == 0, f"Expected no validation errors, got: {errors}"


@then(
    parsers.parse(
        'the partner profile is saved to the partners directory as "{filename}"'
    ),
)
def profile_saved_to_dir(filename: str, partners_dir: Path):
    """Assert profile file exists in partners directory."""
    path = partners_dir / filename
    assert path.exists(), f"Expected {path} to exist"


@then(
    parsers.parse(
        'when Phil retrieves the partner profile the partner name is "{name}"'
    ),
)
def retrieved_partner_name(name: str, partnership_context: dict[str, Any]):
    """Assert partner name on retrieved profile."""
    path = partnership_context["saved_path"]
    profile = json.loads(path.read_text())
    assert profile["partner_name"] == name


@then(parsers.parse("the retrieved profile contains {count:d} capabilities"))
def retrieved_capabilities_count(count: int, partnership_context: dict[str, Any]):
    """Assert capability count on retrieved profile."""
    path = partnership_context["saved_path"]
    profile = json.loads(path.read_text())
    assert len(profile["capabilities"]) == count


@then(parsers.parse("the reloaded profile has {count:d} capabilities"))
def reloaded_capabilities(count: int, partnership_context: dict[str, Any]):
    """Assert capability count on reloaded profile."""
    assert len(partnership_context["reloaded"]["capabilities"]) == count


@then(parsers.parse("the reloaded profile has {count:d} key personnel entries"))
def reloaded_personnel(count: int, partnership_context: dict[str, Any]):
    """Assert key personnel count on reloaded profile."""
    assert len(partnership_context["reloaded"]["key_personnel"]) == count


@then(parsers.parse("the reloaded profile has {count:d} facility"))
def reloaded_facilities(count: int, partnership_context: dict[str, Any]):
    """Assert facility count on reloaded profile."""
    assert len(partnership_context["reloaded"]["facilities"]) == count


@then(parsers.parse("the reloaded profile has {count:d} past collaboration"))
def reloaded_collabs(count: int, partnership_context: dict[str, Any]):
    """Assert past collaboration count on reloaded profile."""
    assert len(partnership_context["reloaded"]["past_collaborations"]) == count


@then("the partner profile is not saved")
def profile_not_saved(partnership_context: dict[str, Any]):
    """Assert profile was not written to disk."""
    assert partnership_context.get("saved") is False


# ---------------------------------------------------------------------------
# Inline validation (placeholder until PartnerProfileValidationService exists)
# ---------------------------------------------------------------------------


def _validate_partner_profile(profile: dict[str, Any]) -> list[str]:
    """Basic partner profile validation.

    This is a placeholder that will be replaced by the production
    PartnerProfileValidationService once implemented in DELIVER wave.
    """
    errors: list[str] = []

    if not profile.get("partner_name"):
        errors.append("partner_name: required")

    partner_type = profile.get("partner_type", "")
    valid_types = {"university", "federally_funded_rdc", "nonprofit_research"}
    if partner_type not in valid_types:
        errors.append(
            f"partner_type: must be one of {sorted(valid_types)}, got '{partner_type}'"
        )

    capabilities = profile.get("capabilities", [])
    if not capabilities:
        errors.append("capabilities: must have at least 1 keyword")

    return errors
