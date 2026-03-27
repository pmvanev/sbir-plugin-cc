"""Figure pipeline gate evaluation -- domain logic for figure-specs.md prerequisite."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class FigurePipelineGateEvaluator:
    """Evaluate figure pipeline gate rules.

    Blocks writes to wave-5-visuals/ when figure-specs.md is absent.
    Allows writing figure-specs.md itself. Ignores paths outside wave-5-visuals/.
    """

    _VISUAL_DIR = "wave-5-visuals/"
    _SPECS_FILENAME = "figure-specs.md"

    def triggers(self, rule: EnforcementRule, state: dict[str, Any], tool_name: str, tool_context: dict[str, Any] | None = None) -> bool:
        """Check if the figure pipeline gate blocks the given tool invocation.

        Returns True (BLOCK) when writing to wave-5-visuals/ without figure-specs.md.
        """
        if tool_name not in ("Write", "Edit"):
            return False

        tool_context = tool_context or {}
        file_path = tool_context.get("file_path", "")

        # Normalize backslashes for cross-platform paths
        normalized = file_path.replace("\\", "/")

        if self._VISUAL_DIR not in normalized:
            return False

        # Allow writing figure-specs.md itself
        filename = normalized.split("/")[-1]
        if filename == self._SPECS_FILENAME:
            return False

        # Block if figure-specs.md not in artifacts_present
        artifacts_present = tool_context.get("artifacts_present", [])
        if self._SPECS_FILENAME not in artifacts_present:
            return True

        return False

    def build_block_message(self, rule: EnforcementRule, state: dict[str, Any]) -> str:
        """Build block message guiding user to create figure-specs.md first."""
        return (
            f"{rule.message}. "
            f"Create {self._SPECS_FILENAME} in wave-5-visuals/ first "
            f"before writing other visual assets."
        )
