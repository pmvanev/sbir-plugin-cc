"""Walking skeleton step definitions for PES Outline Gate Enforcement.

All common steps are imported via conftest.py. This module only
binds the walking skeleton feature file to the shared steps.

Invokes through driving port: EnforcementEngine.evaluate() only.
"""

from pytest_bdd import scenarios

scenarios("../walking-skeleton.feature")
