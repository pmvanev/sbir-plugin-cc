"""Writing style gate step definitions for PES Writing Style Gate Enforcement.

All common steps are imported via conftest.py. This module only
binds the writing style gate feature file to the shared steps.

Invokes through driving port: EnforcementEngine.evaluate() only.
"""

from pytest_bdd import scenarios

scenarios("../writing_style_gate.feature")
