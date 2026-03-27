"""Style profile gate evaluation -- domain logic for figure write prerequisites."""

from __future__ import annotations

from typing import Any

from pes.domain.rules import EnforcementRule


class StyleProfileGateEvaluator:
    """Evaluate style profile gate rules against proposal state.

    Blocks figure writes in wave-5-visuals/ when no style-profile.yaml
    exists and no style_analysis_skipped marker is set in state.
    Always allows writing style-profile.yaml and figure-specs.md themselves.
    """

    _WRITE_TOOLS = ("Write", "Edit")
    _WAVE5_MARKER = "wave-5-visuals/"
    _ALLOWED_FILES = ("style-profile.yaml", "figure-specs.md")

    def triggers(
        self,
        rule: EnforcementRule,
        state: dict[str, Any],
        tool_name: str,
        tool_context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if the style profile gate blocks a tool invocation.

        Returns True if the rule triggers (blocks the action).
        """
        if tool_name not in self._WRITE_TOOLS:
            return False

        if tool_context is None:
            return False

        file_path = tool_context.get("file_path", "")

        if self._WAVE5_MARKER not in file_path:
            return False

        # Extract filename from path using string operations (pure domain)
        filename = file_path.rsplit("/", 1)[-1] if "/" in file_path else file_path

        if filename in self._ALLOWED_FILES:
            return False

        # Check if style-profile.yaml already exists in artifacts
        artifacts_present = tool_context.get("artifacts_present", [])
        if "style-profile.yaml" in artifacts_present:
            return False

        # Check if style analysis was explicitly skipped
        if state.get("style_analysis_skipped") is True:
            return False

        return True

    def build_block_message(
        self, rule: EnforcementRule, state: dict[str, Any]
    ) -> str:
        """Build block message with both resolution paths."""
        return (
            f"{rule.message}. "
            "Resolve by either: "
            "(1) creating style-profile.yaml via style analysis conversation, or "
            "(2) recording style_analysis_skipped in proposal state to bypass."
        )
