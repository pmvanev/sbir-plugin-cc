"""Step definition conftest -- shared step implementations across PFP features.

Step definitions are organized by domain concept, not by feature file.
This conftest imports common steps so pytest-bdd can discover them
across all feature-specific step modules.

Note: Do NOT import step modules that call scenarios() here --
that causes circular import issues. Those modules are discovered
directly by pytest as test modules.
"""

from tests.acceptance.pes_figure_pipeline.steps.pfp_common_steps import *  # noqa: F403
