"""Wave ordering rule evaluation -- domain logic for wave prerequisites."""

from __future__ import annotations

from typing import Any, ClassVar

from pes.domain.rules import EnforcementRule


class WaveOrderingEvaluator:
    """Evaluate wave ordering rules against proposal state.

    Determines whether a tool invocation targeting a specific wave
    is allowed based on prerequisite conditions in the proposal state.
    """

    # Maps condition keys to (state_key, approval_field) for approval-based checks.
    _APPROVAL_CONDITIONS: ClassVar[dict[str, tuple[str, str]]] = {
        "requires_strategy_approval": ("strategy_brief", "approved_at"),
        "requires_research_approval": ("research_summary", "approved_at"),
        "requires_outline_approval": ("outline", "approved_at"),
    }

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str, tool_context: dict[str, Any] | None = None) -> bool:
        """Check if a wave ordering rule blocks the given tool invocation.

        Returns True if the rule triggers (blocks the action).
        """
        condition = rule.condition
        target_wave = condition.get("target_wave")

        if target_wave is None:
            return False

        if f"wave_{target_wave}" not in tool_name:
            return False

        # Check go/no-go condition (Wave 1)
        requires_go = condition.get("requires_go_no_go")
        if requires_go and state.get("go_no_go") != requires_go:
            return True

        # Check approval-based conditions (Waves 2-4)
        for condition_key, (state_key, approval_field) in self._APPROVAL_CONDITIONS.items():
            if condition.get(condition_key):
                artifact = state.get(state_key, {})
                if not isinstance(artifact, dict) or not artifact.get(approval_field):
                    return True

        # Check final review sign-off condition (Wave 8)
        if condition.get("requires_final_review_signoff"):
            final_review = state.get("final_review", {})
            if not isinstance(final_review, dict) or not final_review.get("signed_off"):
                return True

        return False
