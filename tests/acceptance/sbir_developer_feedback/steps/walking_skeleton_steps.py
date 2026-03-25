"""Walking skeleton step implementations for sbir-developer-feedback.

Drives through the full pipeline:
  sbir_feedback_cli.py save -> FeedbackSnapshotService -> FilesystemFeedbackAdapter
"""

from pytest_bdd import scenarios

from tests.acceptance.sbir_developer_feedback.steps.common_steps import *  # noqa: F403

scenarios("../walking-skeleton.feature")
