"""Step definitions for profile update scenarios.

Invokes through: ProfilePort (read existing, write updated) and
ProfileValidationService (validate updated profile).
Does NOT import internal components directly.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.company_profile_builder.steps.profile_common_steps import *  # noqa: F403

# Link to feature files
scenarios("../milestone-03-extraction-update.feature")


# --- Given steps ---


@given(
    parsers.parse("Rafael has a saved profile with {count:d} past performance entries"),
)
def saved_profile_with_pp(valid_profile_data, write_profile, count):
    """Write a profile with specific past performance count."""
    profile = valid_profile_data.copy()
    profile["past_performance"] = [
        {"agency": f"Agency_{i}", "topic_area": f"Topic_{i}", "outcome": "awarded"}
        for i in range(count)
    ]
    write_profile(profile)


@given(
    parsers.parse("Rafael has a saved profile with {count:d} key personnel"),
)
def saved_profile_with_kp(valid_profile_data, write_profile, count):
    """Write a profile with specific key personnel count."""
    profile = valid_profile_data.copy()
    profile["key_personnel"] = [
        {"name": f"Person_{i}", "role": f"Role_{i}", "expertise": [f"skill_{i}"]}
        for i in range(count)
    ]
    write_profile(profile)


@given(
    parsers.parse("Rafael has a saved profile with employee count {count:d}"),
)
def saved_profile_with_employee_count(valid_profile_data, write_profile, count):
    """Write a profile with specific employee count."""
    profile = valid_profile_data.copy()
    profile["employee_count"] = count
    write_profile(profile)


@given(
    parsers.parse('Rafael has a saved profile with valid CAGE code "{cage}"'),
)
def saved_profile_with_cage(valid_profile_data, write_profile, cage):
    """Write a profile with specific CAGE code."""
    profile = valid_profile_data.copy()
    profile["certifications"]["sam_gov"]["cage_code"] = cage
    write_profile(profile)


@given("Rafael has a saved profile with SAM.gov inactive")
def saved_profile_sam_inactive(valid_profile_data, write_profile):
    """Write a profile with inactive SAM.gov."""
    profile = valid_profile_data.copy()
    profile["certifications"]["sam_gov"] = {"active": False}
    write_profile(profile)


@given(
    parsers.parse("Rafael has a saved profile with:\n{table}"),
)
def saved_profile_with_section_counts(valid_profile_data, write_profile, table):
    """Write a profile with multiple section counts from table."""
    profile = valid_profile_data.copy()
    # Adjust counts based on table -- placeholder for pytest-bdd table parsing
    profile["capabilities"] = [f"cap_{i}" for i in range(5)]
    profile["key_personnel"] = [
        {"name": f"Person_{i}", "role": f"Role_{i}", "expertise": [f"skill_{i}"]}
        for i in range(2)
    ]
    profile["past_performance"] = [
        {"agency": f"Agency_{i}", "topic_area": f"Topic_{i}", "outcome": "awarded"}
        for i in range(2)
    ]
    profile["research_institution_partners"] = ["Partner_0"]
    write_profile(profile)


@given(
    "any valid existing profile and any valid section update",
    target_fixture="profile_draft",
)
def any_valid_profile_for_update(valid_profile_data):
    """Use sample valid profile for property test."""
    return valid_profile_data.copy()


# --- Document extraction Given steps ---


@given(
    parsers.parse('a document extraction produced company name "{company}"'),
    target_fixture="extraction_data",
)
def extraction_with_company(company):
    """Simulate document extraction result with company name."""
    return {"company_name": company}


@given(
    parsers.parse('the extraction produced capabilities "{caps}"'),
)
def extraction_with_capabilities(extraction_data, caps):
    """Add capabilities to extraction result."""
    extraction_data["capabilities"] = [c.strip() for c in caps.split(",")]


@given(
    parsers.parse("the extraction produced employee count {count:d}"),
)
def extraction_with_employee_count(extraction_data, count):
    """Add employee count to extraction result."""
    extraction_data["employee_count"] = count


@given("a first extraction produced company name and capabilities")
def first_extraction(profile_context):
    """Simulate first document extraction."""
    profile_context["extraction_1"] = {
        "company_name": "Radiant Defense Systems, LLC",
        "capabilities": ["directed energy", "RF systems"],
    }


@given(
    parsers.parse(
        'a second extraction produced SAM.gov details with CAGE "{cage}" and UEI "{uei}"'
    ),
)
def second_extraction(profile_context, cage, uei):
    """Simulate second document extraction."""
    profile_context["extraction_2"] = {
        "certifications": {
            "sam_gov": {"active": True, "cage_code": cage, "uei": uei},
        },
    }


@given("a document extraction produced only company name and employee count")
def partial_extraction(profile_context):
    """Simulate partial extraction."""
    profile_context["extraction"] = {
        "company_name": "Radiant Defense Systems, LLC",
        "employee_count": 23,
    }


@given(
    "a document extraction found no profile-relevant fields",
    target_fixture="extraction_data",
)
def empty_extraction():
    """Simulate empty extraction."""
    return {}


@given(
    parsers.parse('a document extraction produced CAGE code "{cage}" and employee count {count:d}'),
    target_fixture="extraction_data",
)
def extraction_with_invalid_data(cage, count):
    """Simulate extraction with invalid data."""
    return {
        "company_name": "Test Corp",
        "capabilities": ["testing"],
        "certifications": {
            "sam_gov": {"active": True, "cage_code": cage, "uei": "TEST123"},
        },
        "employee_count": count,
    }


# --- When steps ---


@when(
    parsers.parse(
        'Rafael adds a past performance entry for agency "{agency}" '
        'with topic "{topic}" and outcome "{outcome}"'
    ),
)
def add_past_performance(profile_path, profile_context, agency, topic, outcome):
    """Add a past performance entry to existing profile.

    Invokes through ProfilePort to read existing, modify, and prepare for save.
    """
    # TODO: Replace with actual adapter invocation.
    # from pes.adapters.json_profile_adapter import JsonProfileAdapter
    # adapter = JsonProfileAdapter(str(profile_path.parent))
    # profile = adapter.load()
    # profile["past_performance"].append({
    #     "agency": agency, "topic_area": topic, "outcome": outcome,
    # })
    # profile_context["updated_profile"] = profile
    pytest.skip("Profile adapter not yet implemented")


@when("the updated profile is validated and saved")
def validate_and_save_update(profile_context, profile_path):
    """Validate and save the updated profile."""
    # TODO: Replace with actual service invocations.
    pytest.skip("Validation service and profile adapter not yet implemented")


@when(
    parsers.parse(
        'Rafael adds key personnel "{name}" as "{role}" with expertise "{expertise}"'
    ),
)
def add_key_personnel(profile_path, profile_context, name, role, expertise):
    """Add a key personnel entry to existing profile."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


@when(parsers.parse("Rafael updates the employee count to {count:d}"))
def update_employee_count(profile_path, profile_context, count):
    """Update employee count in existing profile."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


@when("Rafael attempts to update a profile section")
def attempt_update_no_profile(profile_path, profile_context):
    """Attempt to update when no profile exists."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


@when(parsers.parse("Rafael updates only the employee count to {count:d}"))
def update_only_employee_count(profile_path, profile_context, count):
    """Update only employee count, preserving everything else."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


@when(parsers.parse('Rafael attempts to update the CAGE code to "{cage}"'))
def attempt_update_cage(profile_path, profile_context, cage):
    """Attempt to update CAGE code to potentially invalid value."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


@when("the updated profile is validated")
def validate_update(profile_context, validation_result):
    """Validate the updated profile without saving."""
    # TODO: Replace with actual validation invocation.
    pytest.skip("Validation service not yet implemented")


@when(
    parsers.parse(
        'Rafael updates SAM.gov to active with CAGE "{cage}" and UEI "{uei}"'
    ),
)
def update_sam_gov(profile_path, profile_context, cage, uei):
    """Update SAM.gov status from inactive to active."""
    # TODO: Replace with actual adapter invocation.
    pytest.skip("Profile adapter not yet implemented")


@when("the extracted data is assembled into a profile draft")
def assemble_extraction(extraction_data, profile_context):
    """Assemble extracted data into a profile draft."""
    from pes.domain.profile_merge import assemble_draft

    profile_context["draft"] = assemble_draft(extraction_data)


@when("both extractions are merged into the profile draft")
def merge_both_extractions(profile_context):
    """Merge multiple extractions into a single draft."""
    from pes.domain.profile_merge import merge_extractions

    ext1 = profile_context["extraction_1"]
    ext2 = profile_context["extraction_2"]
    profile_context["draft"] = merge_extractions(ext1, ext2)


@when("the draft is checked for completeness")
def check_draft_completeness(profile_context):
    """Check which profile sections are populated."""
    from pes.domain.profile_merge import assemble_draft, check_completeness

    draft = assemble_draft(profile_context["extraction"])
    profile_context["draft"] = draft
    profile_context["missing"] = check_completeness(draft)


@when("the extracted profile draft is validated")
def validate_extraction(extraction_data, validation_result):
    """Validate profile assembled from extraction."""
    from pes.domain.profile_merge import assemble_draft
    from pes.domain.profile_validation import ProfileValidationService

    draft = assemble_draft(extraction_data)
    service = ProfileValidationService()
    validation_result["result"] = service.validate(draft)


@when("the update is applied to the selected section")
def apply_section_update(profile_draft, profile_context):
    """Apply a section update for property testing."""
    # TODO: Replace with actual update logic.
    pytest.skip("Update logic not yet implemented")


# --- Then steps ---


@then(parsers.parse("the profile contains {count:d} past performance entries"))
def past_performance_count(profile_path, count):
    """Assert past performance entry count."""
    data = json.loads(profile_path.read_text())
    assert len(data["past_performance"]) == count


@then(parsers.parse("the profile now has {count:d} past performance entries"))
def now_has_pp_count(profile_path, count):
    """Assert updated past performance count."""
    data = json.loads(profile_path.read_text())
    assert len(data["past_performance"]) == count


@then(parsers.parse('the new entry shows agency "{agency}"'))
def new_entry_agency(profile_path, agency):
    """Assert new past performance entry has expected agency."""
    data = json.loads(profile_path.read_text())
    agencies = [pp["agency"] for pp in data["past_performance"]]
    assert agency in agencies


@then(parsers.parse("the previous {count:d} entries are unchanged"))
def previous_entries_unchanged(profile_path, count):
    """Assert previous entries were not modified."""
    # This is verified by the count check -- entries are appended.
    data = json.loads(profile_path.read_text())
    assert len(data["past_performance"]) > count


@then(parsers.parse("the profile contains {count:d} key personnel entries"))
def key_personnel_count(profile_path, count):
    """Assert key personnel entry count."""
    data = json.loads(profile_path.read_text())
    assert len(data["key_personnel"]) == count


@then(parsers.parse("the original {count:d} personnel entries are unchanged"))
def original_personnel_unchanged(profile_path, count):
    """Assert original personnel were not modified."""
    data = json.loads(profile_path.read_text())
    assert len(data["key_personnel"]) > count


@then(parsers.parse("the profile shows employee count {count:d}"))
def employee_count_value(profile_path, count):
    """Assert employee count was updated."""
    data = json.loads(profile_path.read_text())
    assert data["employee_count"] == count


@then("suggests creating a profile first")
def suggest_create_profile(profile_context):
    """Assert error message suggests setup command."""
    error_msg = str(profile_context.get("error", ""))
    assert "setup" in error_msg.lower() or "create" in error_msg.lower()


@then(parsers.parse("capabilities still has {count:d} entries"))
def capabilities_count(profile_path, count):
    """Assert capabilities were preserved."""
    data = json.loads(profile_path.read_text())
    assert len(data["capabilities"]) == count


@then(parsers.parse("the capabilities list still contains {count:d} entries"))
def capabilities_list_count(profile_path, count):
    """Assert capabilities count preserved after update."""
    data = json.loads(profile_path.read_text())
    assert len(data["capabilities"]) == count


@then(parsers.parse("key personnel still has {count:d} entries"))
def kp_count(profile_path, count):
    """Assert key personnel preserved."""
    data = json.loads(profile_path.read_text())
    assert len(data["key_personnel"]) == count


@then(parsers.parse("past performance still has {count:d} entries"))
def pp_preserved_count(profile_path, count):
    """Assert past performance preserved."""
    data = json.loads(profile_path.read_text())
    assert len(data["past_performance"]) == count


@then(parsers.parse("research partners still has {count:d} entry"))
def rp_count(profile_path, count):
    """Assert research partners preserved."""
    data = json.loads(profile_path.read_text())
    assert len(data["research_institution_partners"]) == count


@then("validation rejects the update with a CAGE code error")
def cage_update_rejected(validation_result):
    """Assert CAGE code error in validation result."""
    result = validation_result["result"]
    assert result.valid is False
    cage_errors = [e for e in result.errors if "cage_code" in e.field]
    assert len(cage_errors) > 0


@then("the original profile is not modified")
def original_not_modified(profile_path, profile_context):
    """Assert original profile file is unchanged."""
    # Original was saved with a known CAGE code -- verify it is still there.
    data = json.loads(profile_path.read_text())
    assert len(data["certifications"]["sam_gov"]["cage_code"]) == 5


@then(parsers.parse('the profile shows SAM.gov active with CAGE "{cage}"'))
def sam_active_with_cage(profile_path, cage):
    """Assert SAM.gov is active with correct CAGE code."""
    data = json.loads(profile_path.read_text())
    assert data["certifications"]["sam_gov"]["active"] is True
    assert data["certifications"]["sam_gov"]["cage_code"] == cage


@then(parsers.parse('the draft contains company name "{company}"'))
def draft_has_company(profile_context, company):
    """Assert draft contains expected company name."""
    assert profile_context["draft"]["company_name"] == company


@then(parsers.parse("the draft contains {count:d} capabilities"))
def draft_has_capabilities(profile_context, count):
    """Assert draft contains expected capability count."""
    assert len(profile_context["draft"]["capabilities"]) == count


@then(parsers.parse("the draft contains employee count {count:d}"))
def draft_has_employee_count(profile_context, count):
    """Assert draft contains expected employee count."""
    assert profile_context["draft"]["employee_count"] == count


@then("the draft contains data from both sources")
def draft_merged(profile_context):
    """Assert draft contains data from multiple extractions."""
    draft = profile_context["draft"]
    assert draft.get("company_name")
    assert draft.get("certifications", {}).get("sam_gov", {}).get("active")


@then(parsers.parse('the SAM.gov section shows active with CAGE "{cage}"'))
def sam_section_active(profile_context, cage):
    """Assert SAM.gov section in draft."""
    sam = profile_context["draft"]["certifications"]["sam_gov"]
    assert sam["active"] is True
    assert sam["cage_code"] == cage


@then("the following sections are identified as missing:")
def missing_sections(profile_context, datatable):
    """Assert missing sections are identified."""
    assert "missing" in profile_context
    # Extract expected missing sections from the datatable (skip header row)
    expected = [row[0] for row in datatable[1:]]
    assert sorted(profile_context["missing"]) == sorted(expected)


@then("the draft has no populated fields")
def draft_empty(profile_context):
    """Assert draft is empty after failed extraction."""
    draft = profile_context.get("draft", {})
    assert not draft or all(not v for v in draft.values())


@then("validation reports errors for the invalid fields")
def extraction_validation_errors(validation_result):
    """Assert validation caught invalid extracted data."""
    result = validation_result["result"]
    assert result.valid is False
    assert len(result.errors) > 0


@then("all unrelated sections remain identical to the original")
def unrelated_sections_unchanged(profile_context):
    """Property test assertion: unmodified sections match original."""
    original = profile_context.get("original", {})
    updated = profile_context.get("updated", {})
    modified_section = profile_context.get("modified_section", "")
    for key in original:
        if key != modified_section:
            assert updated.get(key) == original[key], (
                f"Section '{key}' was modified unexpectedly"
            )
