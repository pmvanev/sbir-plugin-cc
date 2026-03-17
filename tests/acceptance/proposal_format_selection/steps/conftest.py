"""Step definition conftest -- shared step imports for format selection features.

Step definitions are organized by domain concept, not by feature file.
This conftest imports common steps so pytest-bdd can discover them.
"""

from tests.acceptance.proposal_format_selection.steps.format_common_steps import *  # noqa: F403
