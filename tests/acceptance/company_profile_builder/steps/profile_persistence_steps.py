"""Step definitions for profile persistence scenarios.

Invokes through: ProfilePort (driving port -- abstract interface).
The JsonProfileAdapter implements this port for file-based persistence.
Does NOT import internal file handling directly.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.company_profile_builder.steps.profile_common_steps import *  # noqa: F403

# Link to feature files -- persistence scenarios in milestone-01
# (scenarios already linked from profile_validation_steps.py)


# --- Given steps ---


@given(
    parsers.parse('a valid profile for "{company}"'),
    target_fixture="profile_draft",
)
def valid_profile_for_company(valid_profile_data, company):
    """Build a valid profile with a specific company name."""
    profile = valid_profile_data.copy()
    profile["company_name"] = company
    return profile


@given(
    parsers.parse('Rafael has an existing profile for "{company}"'),
)
def existing_profile(valid_profile_data, write_profile, company):
    """Write an existing profile to disk."""
    profile = valid_profile_data.copy()
    profile["company_name"] = company
    write_profile(profile)


@given(
    parsers.parse('Rafael has a saved profile for "{company}"'),
)
def saved_profile(valid_profile_data, write_profile, company):
    """Write a profile to disk for later retrieval."""
    profile = valid_profile_data.copy()
    profile["company_name"] = company
    write_profile(profile)


@given("the profile directory does not exist")
def no_profile_directory(profile_dir):
    """Remove the profile directory to test creation."""
    import shutil
    if profile_dir.exists():
        shutil.rmtree(profile_dir)


@given("no company profile exists")
def no_profile(profile_path):
    """Ensure no profile file exists."""
    if profile_path.exists():
        profile_path.unlink()


@given(
    parsers.parse(
        "Rafael has a saved company profile with {cap_count:d} capabilities "
        "and {pp_count:d} past performance entries"
    ),
)
def saved_profile_with_counts(valid_profile_data, write_profile, cap_count, pp_count):
    """Write profile with specific entry counts."""
    profile = valid_profile_data.copy()
    profile["capabilities"] = [f"capability_{i}" for i in range(cap_count)]
    profile["past_performance"] = [
        {"agency": f"Agency_{i}", "topic_area": f"Topic_{i}", "outcome": "awarded"}
        for i in range(pp_count)
    ]
    write_profile(profile)


# --- When steps ---


@when("the profile is saved")
def save_profile(profile_draft, profile_path, profile_dir):
    """Save profile through the profile adapter.

    Invokes through ProfilePort driving port.
    """
    from pes.adapters.json_profile_adapter import JsonProfileAdapter

    adapter = JsonProfileAdapter(str(profile_dir))
    adapter.write(profile_draft)


@when(parsers.parse('a new profile for "{company}" is saved'))
def save_new_profile(valid_profile_data, profile_path, profile_dir, company):
    """Save a new profile, potentially overwriting existing."""
    from pes.adapters.json_profile_adapter import JsonProfileAdapter

    profile = valid_profile_data.copy()
    profile["company_name"] = company
    adapter = JsonProfileAdapter(str(profile_dir))
    adapter.write(profile)


@when("a valid profile is saved")
def save_valid_profile(minimal_valid_profile, profile_dir):
    """Save a minimal valid profile."""
    from pes.adapters.json_profile_adapter import JsonProfileAdapter

    adapter = JsonProfileAdapter(str(profile_dir))
    adapter.write(minimal_valid_profile)


@when("the system checks for an existing profile")
def check_existing(profile_dir, profile_context):
    """Check for existing profile metadata through adapter."""
    from pes.adapters.json_profile_adapter import JsonProfileAdapter

    adapter = JsonProfileAdapter(str(profile_dir))
    profile_context["metadata"] = adapter.metadata()


@when("the system attempts to load the profile")
def attempt_load(profile_dir, profile_context):
    """Attempt to load profile through adapter."""
    from pes.adapters.json_profile_adapter import JsonProfileAdapter

    adapter = JsonProfileAdapter(str(profile_dir))
    result = adapter.read()
    if result is None:
        profile_context["not_found"] = True
    else:
        profile_context["loaded"] = result


# --- Then steps ---


@then("the profile file exists at the expected location")
def profile_file_exists(profile_path):
    """Assert profile file is on disk."""
    assert profile_path.exists()


@then("the file contains valid data matching the saved profile")
def file_matches_saved(profile_path, profile_draft):
    """Assert file content matches what was saved."""
    data = json.loads(profile_path.read_text())
    assert data["company_name"] == profile_draft["company_name"]


@then("a backup file exists with the previous profile data")
def backup_exists(profile_path):
    """Assert .bak file exists after overwrite."""
    bak_path = profile_path.with_suffix(".json.bak")
    assert bak_path.exists()


@then(parsers.parse('the current profile contains "{company}"'))
def current_profile_company(profile_path, company):
    """Assert current profile has expected company name."""
    data = json.loads(profile_path.read_text())
    assert data["company_name"] == company


@then("the profile directory is created")
def directory_created(profile_dir):
    """Assert profile directory exists."""
    assert profile_dir.exists()


@then("the profile file is written successfully")
def profile_written(profile_path):
    """Assert profile file was written."""
    assert profile_path.exists()


@then("the check reports the profile exists")
def profile_exists_check(profile_context):
    """Assert metadata reports existence."""
    assert profile_context["metadata"].exists is True


@then(parsers.parse('the company name "{name}" is returned'))
def metadata_company_name(profile_context, name):
    """Assert metadata contains company name."""
    assert profile_context["metadata"].company_name == name


@then("the system reports that no profile was found")
def no_profile_found(profile_context):
    """Assert load operation reports absence."""
    assert "not_found" in profile_context or "error" in profile_context
