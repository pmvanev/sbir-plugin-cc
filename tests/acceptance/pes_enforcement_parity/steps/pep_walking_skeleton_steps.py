"""Step definitions for PES Enforcement Parity walking skeletons.

Invokes through driving port: EnforcementEngine only.
Does NOT import internal components directly -- they are exercised
indirectly through engine dispatch.
"""

from __future__ import annotations

from pytest_bdd import scenarios

from tests.acceptance.pes_enforcement_parity.steps.pep_common_steps import *  # noqa: F403

scenarios("../walking-skeleton.feature")
