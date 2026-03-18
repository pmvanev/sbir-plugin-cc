"""Step definitions for Session Start Housekeeping acceptance scenarios.

Invokes through driving port: EnforcementEngine.check_session_start() only.
"""

from __future__ import annotations

from pytest_bdd import scenarios

from tests.acceptance.pes_enforcement_parity.steps.pep_common_steps import *  # noqa: F403

scenarios("../session_housekeeping.feature")
