"""Wave ordering rule evaluation -- domain logic for wave prerequisites."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class WaveOrderingEvaluator:
    """Evaluate wave ordering rules against proposal state.

    Determines whether a tool invocation targeting a specific wave
    is allowed based on prerequisite conditions in the proposal state.
    """

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str) -> bool:
        """Check if a wave ordering rule blocks the given tool invocation.

        Returns True if the rule triggers (blocks the action).
        """
        condition = rule.condition
        target_wave = condition.get("target_wave")
        requires_go = condition.get("requires_go_no_go")

        if target_wave is None:
            return False

        if f"wave_{target_wave}" not in tool_name:
            return False

        return bool(requires_go and state.get("go_no_go") != requires_go)
