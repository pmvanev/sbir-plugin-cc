"""Common steps shared across all Solicitation Finder acceptance features.

These steps handle shared preconditions like system availability
and profile setup.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given, parsers, then


@given("the solicitation finder system is available")
def finder_system_available():
    """System availability -- satisfied by test fixtures.

    In acceptance tests, the system is 'available' when the finder service,
    topic fetch port, and results port are instantiated with test fixtures.
    """
    pass


@given(parsers.parse('Phil has a company profile for "{company}"'))
def phil_has_profile_for_company(
    company: str,
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Write a company profile with the given company name."""
    profile = radiant_profile.copy()
    profile["company_name"] = company
    write_profile(profile)
    finder_context["profile"] = profile


@given("Phil has a company profile")
def phil_has_default_profile(
    radiant_profile: dict[str, Any],
    write_profile,
    finder_context: dict[str, Any],
):
    """Write the default Radiant Defense profile."""
    write_profile(radiant_profile)
    finder_context["profile"] = radiant_profile


@given("no company profile exists")
def no_company_profile(profile_path, finder_context: dict[str, Any]):
    """Ensure no profile file exists."""
    if profile_path.exists():
        profile_path.unlink()
    finder_context["profile"] = None


# --- Shared Then steps used across multiple feature files ---


@then(parsers.parse('the tool displays "{message}"'))
def displays_message(message: str, finder_context: dict[str, Any]):
    """Verify a specific message is displayed."""
    # TODO: Assert against service output messages
    pass


@then(parsers.parse('the tool warns "{message}"'))
def tool_warns_message(message: str, finder_context: dict[str, Any]):
    """Verify a specific warning message."""
    # TODO: Assert against warning output
    pass
