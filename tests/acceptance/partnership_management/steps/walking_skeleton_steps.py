"""Walking skeleton step definitions -- links walking-skeleton.feature
to steps defined in partner_profile_steps and partnership_scoring_steps.

This file imports all step definitions needed by the walking skeleton
scenarios and registers the feature file linkage.
"""

from pytest_bdd import scenarios

# Import all step definitions used by walking skeleton scenarios
from tests.acceptance.partnership_management.steps.partner_profile_steps import *  # noqa: F401, F403
from tests.acceptance.partnership_management.steps.partnership_scoring_steps import *  # noqa: F401, F403

# Link to feature file
scenarios("../walking-skeleton.feature")
