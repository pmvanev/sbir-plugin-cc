"""Common steps shared across all Quality Discovery acceptance features.

These steps handle shared preconditions like schema availability,
artifact directory setup, and artifact loading.
"""

from __future__ import annotations

from pathlib import Path

from pytest_bdd import given


@given("the quality artifact schemas are available")
def schemas_available(
    quality_preferences_schema,
    winning_patterns_schema,
    writing_quality_profile_schema,
):
    """Schemas are loaded by session fixtures in conftest."""
    assert quality_preferences_schema is not None
    assert winning_patterns_schema is not None
    assert writing_quality_profile_schema is not None


@given("the quality artifact directory exists at the company profile location")
def quality_dir_exists(quality_dir: Path):
    """Quality artifact directory exists (provided by conftest fixture)."""
    assert quality_dir.exists()
