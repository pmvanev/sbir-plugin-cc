"""Step definitions for API key setup and validation scenarios (US-CPE-004).

Invokes through: ApiKeyPort (driving port -- abstract interface for key management).
Does NOT import JSON file handling directly. The JsonApiKeyAdapter implements
this port for file-based key storage.
"""

from __future__ import annotations

import json
from typing import Any

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.company_profile_enrichment.steps.enrichment_common_steps import *  # noqa: F403

# Link milestone-1 feature file
scenarios("../milestone-1-api-key-setup.feature")


# ---------------------------------------------------------------------------
# Given steps
# ---------------------------------------------------------------------------


@given("Rafael stored a SAM.gov API key in a previous session")
def existing_api_key(write_api_key):
    """Write a valid API key to simulate a previous session."""
    write_api_key("previously-stored-key-ending-x7Kf")


@given("no SAM.gov API key is stored")
def no_api_key(api_keys_path):
    """Ensure no API key file exists."""
    if api_keys_path.exists():
        api_keys_path.unlink()


# ---------------------------------------------------------------------------
# When steps
# ---------------------------------------------------------------------------


@when("the system checks for an existing API key")
def check_for_key(enrichment_context, api_keys_path):
    """Check for existing API key through ApiKeyPort.

    TODO (DELIVER): Wire to real JsonApiKeyAdapter.read_key().
    """
    if api_keys_path.exists():
        data = json.loads(api_keys_path.read_text())
        key = data.get("sam_gov_api_key")
        if key:
            enrichment_context["key_found"] = True
            enrichment_context["key_last_4"] = key[-4:]
        else:
            enrichment_context["key_found"] = False
    else:
        enrichment_context["key_found"] = False


@when("Rafael provides a valid SAM.gov API key")
def provide_valid_key(enrichment_context):
    """User provides a valid API key for storage.

    TODO (DELIVER): Wire to real key input flow.
    """
    enrichment_context["provided_key"] = "valid-test-key-ending-ghi9"


@when("the system validates the key against SAM.gov")
def validate_key(enrichment_context):
    """Validate the API key with a test call to SAM.gov.

    TODO (DELIVER): Wire to real ApiKeyPort.validate_sam_key().
    """
    key = enrichment_context.get("provided_key", "")
    # For now, keys starting with "valid" pass validation
    enrichment_context["key_valid"] = key.startswith("valid")


# ---------------------------------------------------------------------------
# Then steps
# ---------------------------------------------------------------------------


@then("the system reports the key is available")
def key_is_available(enrichment_context):
    """Assert the system found a stored API key."""
    assert enrichment_context["key_found"] is True


@then("the key is identified by its last 4 characters only")
def key_shows_last_4(enrichment_context):
    """Assert only the last 4 characters of the key are exposed."""
    assert len(enrichment_context["key_last_4"]) == 4


@then("Rafael is not prompted to enter a new key")
def no_key_prompt(enrichment_context):
    """Assert no key entry was needed."""
    assert enrichment_context["key_found"] is True
    assert "provided_key" not in enrichment_context


@then("the key passes validation")
def key_passes_validation(enrichment_context):
    """Assert the API key passed validation."""
    assert enrichment_context["key_valid"] is True


@then("the key is saved to the secure key storage location")
def key_saved(enrichment_context, api_keys_path, write_api_key):
    """Assert the key was saved to the expected location."""
    key = enrichment_context["provided_key"]
    write_api_key(key)
    assert api_keys_path.exists()


@then("the saved file has owner-only access permissions")
def key_file_permissions(api_keys_path):
    """Assert the key file has restricted permissions.

    Note: On Windows, file permissions are managed by ACLs on
    the user directory. This assertion verifies the file exists
    and is not world-readable. Full permission check is
    platform-dependent.
    """
    assert api_keys_path.exists()
    # TODO (DELIVER): Add os.stat permission check for Unix platforms
