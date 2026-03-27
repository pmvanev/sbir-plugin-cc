"""Integration checkpoint step definitions for PES Figure Pipeline Enforcement.

All common steps are imported via conftest.py. This module only
binds the integration checkpoints feature file to the shared steps.

Invokes through driving port: EnforcementEngine.evaluate() only.
"""

from pytest_bdd import scenarios

scenarios("../integration_checkpoints.feature")
