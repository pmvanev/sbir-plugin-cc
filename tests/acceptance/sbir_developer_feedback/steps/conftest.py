"""Step definition conftest -- shared step implementations for sbir-developer-feedback.

Step definitions invoke through driving ports only:
- FeedbackSnapshotService (domain service)
- FilesystemFeedbackAdapter (via FeedbackWriterPort)
- sbir_feedback_cli.py via subprocess (for CLI milestone tests)

All filesystem access uses pytest tmp_path fixture for isolation.
"""

from tests.acceptance.sbir_developer_feedback.steps.common_steps import *  # noqa: F403
