"""Step definitions for Agent Lifecycle Tracking acceptance scenarios.

Invokes through driving port: EnforcementEngine only.
Agent dispatch verification will be a new engine capability driven by
these tests.
"""

from __future__ import annotations

from pytest_bdd import scenarios

from tests.acceptance.pes_enforcement_parity.steps.pep_common_steps import *  # noqa: F403

scenarios("../agent_lifecycle.feature")
