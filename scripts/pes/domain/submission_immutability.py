"""Submission immutability rule evaluation -- domain logic for submitted artifact protection."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class SubmissionImmutabilityEvaluator:
    """Evaluate submission immutability rules against proposal state.

    Blocks all write operations when a proposal has been submitted
    and its artifacts are marked immutable.
    """

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str, tool_context: dict[str, Any] | None = None) -> bool:
        """Check if submission immutability rule triggers.

        Returns True if the rule triggers (blocks the action).
        """
        condition = rule.condition
        if not condition.get("requires_immutable"):
            return False

        submission = state.get("submission", {})
        if not isinstance(submission, dict):
            return False

        return (
            submission.get("status") == "submitted"
            and submission.get("immutable") is True
        )

    def build_block_message(
        self, rule: EnforcementRule, state: dict[str, Any]
    ) -> str:
        """Build a block message that includes the proposal topic ID if available."""
        topic = state.get("topic", {})
        topic_id = topic.get("id") if isinstance(topic, dict) else None

        if topic_id:
            return (
                f"Proposal {topic_id} is submitted. Artifacts are read-only."
            )
        return rule.message
