"""Corpus integrity rule evaluation -- domain logic for win/loss tag protection."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class CorpusIntegrityEvaluator:
    """Evaluate corpus integrity rules against proposal state.

    Blocks modification of existing win/loss outcome tags.
    Allows appending new tags when no existing tag is recorded.
    """

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str) -> bool:
        """Check if corpus integrity rule triggers.

        Returns True if the rule triggers (blocks the action).
        """
        condition = rule.condition
        if not condition.get("append_only_tags"):
            return False

        # Only triggers on outcome-related actions
        if "outcome" not in tool_name and "record_outcome" not in tool_name:
            return False

        learning = state.get("learning", {})
        if not isinstance(learning, dict):
            return False

        existing_outcome = learning.get("outcome")

        # Block if there's already an outcome and a change is requested
        if existing_outcome is not None:
            requested_change = state.get("requested_outcome_change")
            if requested_change is not None and requested_change != existing_outcome:
                return True

        return False
