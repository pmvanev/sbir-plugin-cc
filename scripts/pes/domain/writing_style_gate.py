"""Writing style gate evaluation -- domain logic for quality-preferences.json prerequisite."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class WritingStyleGateEvaluator:
    """Evaluate writing style gate rules against proposal state.

    Blocks writes to wave-4-drafting/ when quality-preferences.json is absent
    from global_artifacts_present and no writing_style_selection_skipped marker
    is set in state.
    """

    _WRITE_TOOLS = ("Write", "Edit")
    _DRAFTING_DIR = "wave-4-drafting/"
    _PREFERENCES_FILENAME = "quality-preferences.json"

    def triggers(
        self,
        rule: EnforcementRule,
        state: dict[str, Any],
        tool_name: str,
        tool_context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if the writing style gate blocks the given tool invocation.

        Returns True (BLOCK) when writing to wave-4-drafting/ without
        quality-preferences.json in global artifacts and no skip marker.
        """
        if tool_name not in self._WRITE_TOOLS:
            return False

        if tool_context is None:
            return False

        file_path = tool_context.get("file_path", "")

        # Normalize backslashes for cross-platform paths
        normalized = file_path.replace("\\", "/")

        if self._DRAFTING_DIR not in normalized:
            return False

        # Check if quality-preferences.json exists in global artifacts
        global_artifacts = tool_context.get("global_artifacts_present", [])
        if self._PREFERENCES_FILENAME in global_artifacts:
            return False

        # Check if writing style selection was explicitly skipped
        return state.get("writing_style_selection_skipped") is not True

    def build_block_message(
        self, rule: EnforcementRule, state: dict[str, Any]
    ) -> str:
        """Build block message with both resolution paths."""
        return (
            f"{rule.message}. "
            "Resolve by either: "
            "(1) Run /proposal quality discover to create quality-preferences.json, or "
            "(2) Skip style selection at the writer's style checkpoint."
        )
