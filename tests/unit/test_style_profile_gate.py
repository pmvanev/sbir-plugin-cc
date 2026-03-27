"""Tests for style profile gate evaluator -- domain logic.

Test Budget: 8 behaviors x 2 = 16 max unit tests (current: 8)

Behaviors:
1. Non-Write/Edit tools never trigger (parametrized)
2. Paths outside wave-5-visuals/ never trigger
3. Writing style-profile.yaml itself never triggers
4. Writing figure-specs.md never triggers
5. Figure write allowed when style-profile.yaml in artifacts_present
6. Figure write allowed when style_analysis_skipped is true in state
7. Figure write blocked when no style-profile.yaml and no skip marker
8. Block message includes both resolution paths (create profile + record skip)

Tests call the evaluator directly since engine wiring for tool_context
comes in a later step. The evaluator is a pure domain strategy object.
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.rules import EnforcementRule
from pes.domain.style_profile_gate import StyleProfileGateEvaluator


def _style_profile_gate_rule() -> EnforcementRule:
    """Rule: Wave 5 figure writes require style profile or explicit skip."""
    return EnforcementRule(
        rule_id="style-profile-gate",
        description="Figure writes require style analysis profile or skip marker",
        rule_type="style_profile_gate",
        condition={},
        message="Style profile required before writing figures",
    )


def _evaluator() -> StyleProfileGateEvaluator:
    return StyleProfileGateEvaluator()


def _wave5_tool_context(
    file_path: str = "artifacts/wave-5-visuals/figure-1.svg",
    artifacts_present: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "file_path": file_path,
        "artifacts_present": artifacts_present or [],
    }


class TestStyleProfileGateNotTriggered:
    """Cases where the gate should NOT trigger (return False)."""

    @pytest.mark.parametrize("tool_name", ["Read", "Bash", "Glob", "Grep"])
    def test_non_write_tools_never_trigger(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave5_tool_context()

        assert evaluator.triggers(rule, state, tool_name, ctx) is False

    def test_paths_outside_wave5_visuals_never_trigger(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave5_tool_context(file_path="artifacts/wave-4-draft/section-1.md")

        assert evaluator.triggers(rule, state, "Write", ctx) is False

    def test_writing_style_profile_itself_always_allowed(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave5_tool_context(
            file_path="artifacts/wave-5-visuals/style-profile.yaml"
        )

        assert evaluator.triggers(rule, state, "Write", ctx) is False

    def test_writing_figure_specs_not_gated(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave5_tool_context(
            file_path="artifacts/wave-5-visuals/figure-specs.md"
        )

        assert evaluator.triggers(rule, state, "Write", ctx) is False

    def test_allowed_when_style_profile_in_artifacts_present(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave5_tool_context(
            artifacts_present=["figure-specs.md", "style-profile.yaml"]
        )

        assert evaluator.triggers(rule, state, "Write", ctx) is False

    def test_allowed_when_style_analysis_skipped(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {"style_analysis_skipped": True}
        ctx = _wave5_tool_context()

        assert evaluator.triggers(rule, state, "Write", ctx) is False


class TestStyleProfileGateBlocking:
    """Cases where the gate SHOULD trigger (return True)."""

    def test_blocks_figure_write_without_profile_or_skip(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave5_tool_context()

        assert evaluator.triggers(rule, state, "Write", ctx) is True


class TestStyleProfileGateBlockMessage:
    """Block message includes both resolution paths."""

    def test_block_message_includes_both_resolution_paths(self) -> None:
        evaluator = _evaluator()
        rule = _style_profile_gate_rule()
        state: dict[str, Any] = {}

        message = evaluator.build_block_message(rule, state)

        assert "style-profile.yaml" in message
        assert "style_analysis_skipped" in message or "skip" in message.lower()
