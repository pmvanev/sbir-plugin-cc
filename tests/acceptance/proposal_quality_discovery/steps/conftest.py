"""Step definition conftest -- shared step imports for quality discovery features.

Step definitions are organized by domain concept, not by feature file.
This conftest imports common steps so pytest-bdd can discover them.

Note: Do NOT import step modules that call scenarios() here --
that causes circular import issues. Those modules are discovered
directly by pytest as test modules.
"""

from tests.acceptance.proposal_quality_discovery.steps.quality_common_steps import *  # noqa: F403
