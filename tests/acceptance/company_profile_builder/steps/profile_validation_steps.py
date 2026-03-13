"""Step definitions for profile validation scenarios.

Invokes through: ProfileValidationService (driving port -- domain service).
Does NOT import internal validators or schema internals directly.

The validation service is the entry point for all schema enforcement.
Tests exercise it with profile dicts and assert on ProfileValidationResult.
"""

from __future__ import annotations

from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.company_profile_builder.conftest import build_profile_from_table
from tests.acceptance.company_profile_builder.steps.profile_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../walking-skeleton.feature")
scenarios("../milestone-01-foundation.feature")


# --- Fixtures ---


@pytest.fixture()
def profile_draft() -> dict[str, Any]:
    """Mutable container for the profile being built during a scenario."""
    return {}


# --- Given steps ---


@given(
    parsers.parse(
        'Rafael has prepared a complete valid profile for "{company}"'
    ),
    target_fixture="profile_draft",
)
def profile_prepared_for_company(company, valid_profile_data):
    """Build a complete valid profile for a named company."""
    profile = valid_profile_data.copy()
    profile["company_name"] = company
    # Use 2 capabilities to match walking skeleton assertion
    profile["capabilities"] = ["directed energy", "RF systems"]
    return profile


@given(
    parsers.parse(
        'Rafael has prepared a profile with CAGE code "{cage}" and employee count {count:d}'
    ),
    target_fixture="profile_draft",
)
def profile_with_cage_and_count(cage, count):
    """Build profile with specific CAGE code and employee count."""
    return build_profile_from_table(cage_code=cage, employee_count=count)


@given(
    parsers.parse(
        'a complete valid profile for "{company}" with {cap_count:d} capabilities'
    ),
    target_fixture="profile_draft",
)
def complete_profile_with_capabilities(company, cap_count, valid_profile_data):
    """Build a complete profile with specific capability count."""
    profile = valid_profile_data.copy()
    profile["company_name"] = company
    profile["capabilities"] = profile["capabilities"][:cap_count]
    return profile


@given(
    parsers.parse('a profile with CAGE code "{cage}" and SAM.gov active'),
    target_fixture="profile_draft",
)
def profile_with_cage_active(cage):
    """Build profile with specific CAGE code and active SAM."""
    return build_profile_from_table(cage_code=cage, sam_gov_active=True)


@given(
    parsers.parse('a profile with security clearance "{clearance}"'),
    target_fixture="profile_draft",
)
def profile_with_clearance(clearance):
    """Build profile with specific clearance level."""
    return build_profile_from_table(clearance=clearance)


@given(
    parsers.parse("a profile with employee count {count:d}"),
    target_fixture="profile_draft",
)
def profile_with_employee_count(count):
    """Build profile with specific employee count."""
    return build_profile_from_table(employee_count=count)


@given(
    "a profile with an empty capabilities list",
    target_fixture="profile_draft",
)
def profile_with_empty_capabilities():
    """Build profile with no capabilities."""
    return build_profile_from_table(capabilities=[])


@given(
    "a profile with no company name",
    target_fixture="profile_draft",
)
def profile_without_company_name():
    """Build profile missing the company name."""
    profile = build_profile_from_table()
    profile["company_name"] = ""
    return profile


@given(
    parsers.parse(
        'a profile with SAM.gov active and CAGE code "{cage}" but no UEI'
    ),
    target_fixture="profile_draft",
)
def profile_active_sam_no_uei(cage):
    """Build profile with active SAM.gov but missing UEI."""
    return build_profile_from_table(cage_code=cage, sam_gov_active=True, uei="")


@given(
    parsers.parse('a profile with socioeconomic certification "{cert}"'),
    target_fixture="profile_draft",
)
def profile_with_invalid_socioeconomic(cert):
    """Build profile with specific socioeconomic certification."""
    return build_profile_from_table(socioeconomic=[cert])


@given(
    "a profile with SAM.gov inactive and no CAGE code or UEI",
    target_fixture="profile_draft",
)
def profile_inactive_sam():
    """Build profile with inactive SAM.gov (no CAGE/UEI required)."""
    profile = build_profile_from_table(sam_gov_active=False)
    profile["certifications"]["sam_gov"].pop("cage_code", None)
    profile["certifications"]["sam_gov"].pop("uei", None)
    return profile


@given(
    parsers.parse(
        'a profile with CAGE code "{cage}" and employee count {count:d} and clearance "{clearance}"'
    ),
    target_fixture="profile_draft",
)
def profile_multiple_errors(cage, count, clearance):
    """Build profile with multiple validation issues."""
    return build_profile_from_table(
        cage_code=cage, employee_count=count, clearance=clearance,
    )


@given(
    "any valid company profile",
    target_fixture="profile_draft",
)
def any_valid_profile(valid_profile_data):
    """Use sample valid profile for property tests."""
    return valid_profile_data.copy()


# --- When steps ---


@when("the profile is validated")
def validate_profile(profile_draft, validation_result):
    """Invoke profile validation through the validation service.

    This step delegates to the ProfileValidationService driving port.
    The actual service will be implemented in scripts/pes/domain/profile_validation.py.
    """
    # TODO: Replace with actual validation service invocation when implemented.
    # from pes.domain.profile_validation import ProfileValidationService
    # service = ProfileValidationService()
    # result = service.validate(profile_draft)
    # validation_result["result"] = result
    pytest.skip("Validation service not yet implemented")


@when("Rafael submits the profile for validation and saving")
def validate_and_save(profile_draft, validation_result, profile_path):
    """Validate profile and save if valid.

    Invokes through both driving ports: validation service then profile adapter.
    """
    # TODO: Replace with actual service invocations.
    # from pes.domain.profile_validation import ProfileValidationService
    # from pes.adapters.json_profile_adapter import JsonProfileAdapter
    # service = ProfileValidationService()
    # result = service.validate(profile_draft)
    # validation_result["result"] = result
    # if result.valid:
    #     adapter = JsonProfileAdapter(str(profile_path.parent))
    #     adapter.save(profile_draft)
    #     validation_result["saved"] = True
    pytest.skip("Validation service and profile adapter not yet implemented")


@when("Rafael submits the profile for validation")
def validate_only(profile_draft, validation_result):
    """Validate profile without saving.

    Invokes through validation service driving port only.
    """
    # TODO: Replace with actual validation service invocation.
    pytest.skip("Validation service not yet implemented")


@when("the profile is saved and then loaded")
def roundtrip_save_load(profile_draft, profile_context, profile_path):
    """Save profile then load it back -- property test for roundtrip."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


# --- Then steps ---


@then("the profile passes validation with no errors")
def validation_passed(validation_result):
    """Assert validation result is valid with empty error list."""
    result = validation_result["result"]
    assert result.valid is True
    assert len(result.errors) == 0


@then("validation passes with no errors")
def validation_passes(validation_result):
    """Assert validation result is valid."""
    result = validation_result["result"]
    assert result.valid is True
    assert len(result.errors) == 0


@then(parsers.parse("validation reports {count:d} issues"))
def validation_reports_count(validation_result, count):
    """Assert specific number of validation errors."""
    result = validation_result["result"]
    assert result.valid is False
    assert len(result.errors) == count


@then(parsers.parse("validation reports {count:d} or more issues"))
def validation_reports_at_least_count(validation_result, count):
    """Assert minimum number of validation errors."""
    result = validation_result["result"]
    assert result.valid is False
    assert len(result.errors) >= count


@then(parsers.parse('validation fails with an error on field "{field}"'))
def validation_error_on_field(validation_result, field):
    """Assert at least one error references the specified field."""
    result = validation_result["result"]
    assert result.valid is False
    error_fields = [e.field for e in result.errors]
    assert field in error_fields, f"Expected error on '{field}', got errors on: {error_fields}"


@then("one issue identifies the CAGE code as having wrong length")
def cage_code_length_error(validation_result):
    """Assert CAGE code length error is present."""
    result = validation_result["result"]
    cage_errors = [e for e in result.errors if "cage_code" in e.field]
    assert len(cage_errors) > 0


@then("one issue identifies the employee count as invalid")
def employee_count_error(validation_result):
    """Assert employee count error is present."""
    result = validation_result["result"]
    count_errors = [e for e in result.errors if "employee_count" in e.field]
    assert len(count_errors) > 0


@then(parsers.parse('the error message mentions "{text}"'))
def error_message_contains(validation_result, text):
    """Assert at least one error message contains the given text."""
    result = validation_result["result"]
    messages = [e.message for e in result.errors]
    assert any(text.lower() in m.lower() for m in messages), (
        f"Expected '{text}' in error messages, got: {messages}"
    )


@then("the error message mentions the allowed values")
def error_mentions_allowed_values(validation_result):
    """Assert error message lists valid options."""
    result = validation_result["result"]
    messages = " ".join(e.message for e in result.errors)
    assert "none" in messages.lower() or "secret" in messages.lower()


@then("the error message indicates the count must be positive")
def error_positive_count(validation_result):
    """Assert error indicates positive count requirement."""
    result = validation_result["result"]
    messages = " ".join(e.message for e in result.errors)
    assert "positive" in messages.lower() or "> 0" in messages or "greater than" in messages.lower()


@then("the error message indicates at least one capability is required")
def error_capability_required(validation_result):
    """Assert error indicates capabilities must not be empty."""
    result = validation_result["result"]
    messages = " ".join(e.message for e in result.errors)
    assert "at least" in messages.lower() or "empty" in messages.lower()


@then("each issue identifies the specific field and expected format")
def each_issue_has_field_and_format(validation_result):
    """Assert every error has both field and expected format."""
    result = validation_result["result"]
    for error in result.errors:
        assert error.field, "Error missing field identifier"
        assert error.expected or error.message, "Error missing expected format"


@then("the profile is saved to the company profile location")
def profile_saved(profile_path):
    """Assert profile file exists on disk."""
    assert profile_path.exists()


@then("the profile is not saved")
def profile_not_saved(profile_path):
    """Assert no profile file was written."""
    assert not profile_path.exists()


@then(
    parsers.parse(
        'when Rafael retrieves the profile the company name is "{name}"'
    )
)
def retrieved_company_name(profile_path, name):
    """Load profile from disk and verify company name."""
    import json
    data = json.loads(profile_path.read_text())
    assert data["company_name"] == name


@then(parsers.parse("the retrieved profile contains {count:d} capabilities"))
def retrieved_capabilities_count(profile_path, count):
    """Load profile and verify capability count."""
    import json
    data = json.loads(profile_path.read_text())
    assert len(data["capabilities"]) == count


@then("the loaded profile matches the original exactly")
def roundtrip_matches(profile_context):
    """Assert roundtrip preserves all data (property test)."""
    assert profile_context["loaded"] == profile_context["original"]
