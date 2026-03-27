"""Figure pipeline gate step definitions for PES Figure Pipeline Enforcement.

All common steps are imported via conftest.py. This module only
binds the figure pipeline gate feature file to the shared steps.

Invokes through driving port: EnforcementEngine.evaluate() only.
"""

from pytest_bdd import scenarios

scenarios("../figure_pipeline_gate.feature")
