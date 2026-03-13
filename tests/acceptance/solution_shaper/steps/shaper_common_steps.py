"""Common steps shared across all Solution Shaper acceptance features.

These steps handle shared preconditions like system availability
and scoring system readiness.
"""

from __future__ import annotations

from typing import Any

from pytest_bdd import given


@given("the approach scoring system is available")
def scoring_system_available():
    """System availability -- satisfied by test fixtures.

    In acceptance tests, the scoring system is 'available' when the
    scoring fixtures and validation helpers are instantiated.
    """
    pass
