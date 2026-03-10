"""Deadline blocking rule evaluation -- domain logic for deadline proximity."""

from __future__ import annotations

from datetime import date
from typing import Any

from pes.domain.rules import EnforcementRule


class DeadlineBlockingEvaluator:
    """Evaluate deadline blocking rules against proposal state.

    Blocks non-essential waves when deadline is within critical threshold.
    Warns with suggestion to submit available work or skip non-essential waves.
    """

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str) -> bool:
        """Check if deadline blocking rule triggers.

        Returns True if the rule triggers (blocks the action).
        """
        condition = rule.condition
        critical_days = condition.get("critical_days")
        non_essential_waves = condition.get("non_essential_waves", [])

        if critical_days is None:
            return False

        # Check if current tool targets a non-essential wave
        current_wave = state.get("current_wave")
        if current_wave not in non_essential_waves:
            return False

        # Check if tool name matches the current wave
        if f"wave_{current_wave}" not in tool_name:
            return False

        # Check deadline proximity
        topic = state.get("topic", {})
        deadline_str = topic.get("deadline")
        if not deadline_str:
            return False

        try:
            deadline = date.fromisoformat(deadline_str)
        except ValueError:
            return False

        days_remaining = (deadline - date.today()).days
        return days_remaining <= critical_days

    def build_block_message(self, rule: EnforcementRule, state: dict[str, Any]) -> str:
        """Build a block message with submit/skip suggestion."""
        topic = state.get("topic", {})
        deadline_str = topic.get("deadline", "unknown")
        try:
            deadline = date.fromisoformat(deadline_str)
            days_remaining = (deadline - date.today()).days
        except (ValueError, TypeError):
            days_remaining = 0

        return (
            f"{rule.message}. {days_remaining} days remaining until deadline. "
            f"Consider: submit with available work or skip non-essential waves."
        )
