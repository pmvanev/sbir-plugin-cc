"""Common steps shared across all Company Profile Builder acceptance features.

These steps handle shared preconditions like system availability and
profile state setup.
"""

from __future__ import annotations

from pytest_bdd import given


@given("the profile builder system is available")
def profile_builder_available():
    """System availability -- satisfied by test fixtures.

    In acceptance tests, the system is 'available' when the validation
    service and profile adapter are instantiated with test fixtures.
    """
    pass


@given("Rafael has no company profile")
def no_existing_profile(profile_path):
    """Ensure no profile file exists."""
    if profile_path.exists():
        profile_path.unlink()
