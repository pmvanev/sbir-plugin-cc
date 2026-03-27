"""Outline gate evaluation -- domain logic for proposal-outline.md prerequisite."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class OutlineGateEvaluator:
    """Evaluate outline gate rules.

    Blocks writes to wave-4-drafting/ when proposal-outline.md is absent
    from outline_artifacts_present. No skip marker. No self-creation exception.
    """

    _DRAFTING_DIR = "wave-4-drafting/"
    _OUTLINE_FILENAME = "proposal-outline.md"

    def triggers(
        self,
        rule: EnforcementRule,
        state: dict[str, Any],
        tool_name: str,
        tool_context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if the outline gate blocks the given tool invocation.

        Returns True (BLOCK) when writing to wave-4-drafting/ without
        proposal-outline.md in outline_artifacts_present.
        """
        if tool_name not in ("Write", "Edit"):
            return False

        tool_context = tool_context or {}
        file_path = tool_context.get("file_path", "")

        # Normalize backslashes for cross-platform paths
        normalized = file_path.replace("\\", "/")

        if self._DRAFTING_DIR not in normalized:
            return False

        # Block if proposal-outline.md not in outline_artifacts_present
        outline_artifacts = tool_context.get("outline_artifacts_present", [])
        return self._OUTLINE_FILENAME not in outline_artifacts

    def build_block_message(self, rule: EnforcementRule, state: dict[str, Any]) -> str:
        """Build block message guiding user to complete Wave 3 outline first."""
        return (
            f"{rule.message}. "
            f"Complete the proposal outline ({self._OUTLINE_FILENAME}) in Wave 3 "
            f"before writing drafting artifacts."
        )
