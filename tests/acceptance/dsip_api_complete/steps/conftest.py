"""Step definition conftest -- shared step implementations across dsip-api-complete features.

Step definitions are organized by domain concept, not by feature file.
This conftest imports common steps so pytest-bdd can discover them
across all feature-specific step modules.

Note: Do NOT import step modules that call scenarios() here --
that causes circular import issues. Those modules are discovered
directly by pytest as test modules.
"""

from tests.acceptance.dsip_api_complete.steps.common_steps import *  # noqa: F403
