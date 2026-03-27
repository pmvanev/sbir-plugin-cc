"""Tests for writing style gate evaluator -- domain logic.

Test Budget: 6 behaviors x 2 = 12 max unit tests (current: 9)

Behaviors:
1. Non-Write/Edit tools never trigger (parametrized)
2. Paths outside wave-4-drafting/ never trigger
3. Write allowed when quality-preferences.json in global_artifacts_present
4. Write allowed when writing_style_selection_skipped is true in state
5. Write/Edit blocked when no quality-preferences.json and no skip marker
6. Block message includes both resolution paths

Tests call the evaluator directly since engine wiring for tool_context
comes in a later step. The evaluator is a pure domain strategy object.
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.rules import EnforcementRule
from pes.domain.writing_style_gate import WritingStyleGateEvaluator


def _writing_style_gate_rule() -> EnforcementRule:
    """Rule: Wave 4 drafting writes require quality preferences or explicit skip."""
    return EnforcementRule(
        rule_id="writing-style-gate",
        description="Drafting writes require quality preferences or skip marker",
        rule_type="writing_style_gate",
        condition={},
        message="Writing style gate: quality-preferences.json required before drafting",
    )


def _evaluator() -> WritingStyleGateEvaluator:
    return WritingStyleGateEvaluator()


def _wave4_tool_context(
    file_path: str = "artifacts/wave-4-drafting/section-1.md",
    global_artifacts_present: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "file_path": file_path,
        "global_artifacts_present": global_artifacts_present or [],
    }


class TestWritingStyleGateNotTriggered:
    """Cases where the gate should NOT trigger (return False)."""

    @pytest.mark.parametrize("tool_name", ["Read", "Bash", "Glob", "Grep"])
    def test_non_write_tools_never_trigger(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave4_tool_context()

        assert evaluator.triggers(rule, state, tool_name, ctx) is False

    def test_paths_outside_wave4_drafting_never_trigger(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave4_tool_context(file_path="artifacts/wave-3-design/outline.md")

        assert evaluator.triggers(rule, state, "Write", ctx) is False

    def test_allowed_when_quality_preferences_in_global_artifacts(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave4_tool_context(
            global_artifacts_present=["quality-preferences.json"]
        )

        assert evaluator.triggers(rule, state, "Write", ctx) is False

    def test_allowed_when_writing_style_selection_skipped(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {"writing_style_selection_skipped": True}
        ctx = _wave4_tool_context()

        assert evaluator.triggers(rule, state, "Write", ctx) is False


class TestWritingStyleGateBlocking:
    """Cases where the gate SHOULD trigger (return True)."""

    def test_blocks_write_without_preferences_or_skip(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave4_tool_context()

        assert evaluator.triggers(rule, state, "Write", ctx) is True

    def test_blocks_edit_without_preferences_or_skip(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}
        ctx = _wave4_tool_context()

        assert evaluator.triggers(rule, state, "Edit", ctx) is True

    def test_does_not_block_when_tool_context_is_none(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}

        assert evaluator.triggers(rule, state, "Write", None) is False

    def test_does_not_block_when_tool_context_absent(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}

        assert evaluator.triggers(rule, state, "Write") is False


class TestWritingStyleGateBlockMessage:
    """Block message includes both resolution paths."""

    def test_block_message_includes_both_resolution_paths(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}

        message = evaluator.build_block_message(rule, state)

        assert "quality-preferences.json" in message
        assert "/proposal quality discover" in message or "quality discover" in message
        assert "skip" in message.lower() or "style checkpoint" in message.lower()

    def test_block_message_includes_rule_message(self) -> None:
        evaluator = _evaluator()
        rule = _writing_style_gate_rule()
        state: dict[str, Any] = {}

        message = evaluator.build_block_message(rule, state)

        assert rule.message in message
