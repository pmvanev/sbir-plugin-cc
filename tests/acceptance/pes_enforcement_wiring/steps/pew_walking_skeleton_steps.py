"""Step definitions for PES Enforcement Wiring walking skeletons.

Invokes through driving port: EnforcementEngine.evaluate() only.
Does NOT import evaluators directly -- they are exercised indirectly
through engine dispatch.
"""

from __future__ import annotations

from pytest_bdd import scenarios

from tests.acceptance.pes_enforcement_wiring.steps.pew_common_steps import *  # noqa: F403

scenarios("../walking-skeleton.feature")
