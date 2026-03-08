"""Step definition conftest -- shared step implementations across features.

Step definitions are organized by domain concept, not by feature file.
This conftest imports all step modules so pytest-bdd can discover them.
"""

from tests.acceptance.step_defs.common_steps import *  # noqa: F403
