"""Common step definitions shared across Visual Asset Quality features.

Provides shared Given steps for service availability and basic fixtures
used across multiple feature files.
"""

from __future__ import annotations

from pytest_bdd import given


@given("the visual asset service is available")
def visual_asset_service_available():
    """Confirm the visual asset service module is importable."""
    from pes.domain.visual_asset_service import VisualAssetService  # noqa: F401
