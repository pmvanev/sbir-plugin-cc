"""Tests for outline gate enforcement -- domain logic.

Test Budget: 5 behaviors x 2 = 10 max unit tests (current: 7)

Behaviors:
1. Write/Edit to wave-4-drafting/ blocked when proposal-outline.md absent (parametrized Write/Edit)
2. Write/Edit to wave-4-drafting/ allowed when proposal-outline.md present (parametrized Write/Edit)
3. Writes outside wave-4-drafting/ not affected (parametrized various paths)
4. Non-write tools not affected
5. Block message includes guidance to complete Wave 3 outline first

Tests invoke OutlineGateEvaluator directly -- engine wiring is a separate step.
Evaluator is a pure domain object with stable public interface (triggers + build_block_message).
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.outline_gate import OutlineGateEvaluator
from pes.domain.rules import EnforcementRule


# --- Helpers ---


def _outline_gate_rule() -> EnforcementRule:
    """Rule: wave-4-drafting/ requires proposal-outline.md to exist."""
    return EnforcementRule(
        rule_id="outline-gate",
        description="Drafting requires proposal-outline.md prerequisite",
        rule_type="outline_gate",
        condition={},
        message="Complete Wave 3 outline before drafting",
    )


def _evaluator() -> OutlineGateEvaluator:
    return OutlineGateEvaluator()


# --- Tests ---


class TestOutlineGateBlocking:
    """Write/Edit to wave-4-drafting/ blocked when proposal-outline.md absent."""

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_blocks_drafting_write_when_outline_absent(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-4-drafting/section-1.md",
            "outline_artifacts_present": [],
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is True

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_blocks_drafting_write_when_outline_key_missing(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-4-drafting/section-2.md",
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is True


class TestOutlineGateAllowing:
    """Write/Edit to wave-4-drafting/ allowed when proposal-outline.md present."""

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_allows_drafting_write_when_outline_present(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-4-drafting/section-1.md",
            "outline_artifacts_present": ["proposal-outline.md"],
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is False


class TestOutlineGateScope:
    """Non-drafting paths and non-write tools not affected."""

    @pytest.mark.parametrize(
        "file_path",
        [
            "artifacts/sf25d-t1201/wave-3-outline/proposal-outline.md",
            "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
            "scripts/pes/domain/engine.py",
        ],
        ids=["wave-3-path", "wave-5-path", "non-artifact-path"],
    )
    def test_ignores_paths_outside_wave_4_drafting(self, file_path: str) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {"file_path": file_path, "outline_artifacts_present": []}

        result = evaluator.triggers(rule, state, "Write", tool_context)

        assert result is False

    @pytest.mark.parametrize("tool_name", ["Read", "Bash", "Glob", "Grep"])
    def test_ignores_non_write_tools(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-4-drafting/section-1.md",
            "outline_artifacts_present": [],
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is False


class TestOutlineGateBlockMessage:
    """Block message includes guidance to complete Wave 3 outline first."""

    def test_block_message_includes_wave_3_guidance(self) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}

        message = evaluator.build_block_message(rule, state)

        assert "proposal-outline.md" in message
        assert "wave 3" in message.lower() or "outline" in message.lower()

    def test_block_message_includes_rule_message(self) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}

        message = evaluator.build_block_message(rule, state)

        assert rule.message in message

    def test_block_message_mentions_completing_outline(self) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}

        message = evaluator.build_block_message(rule, state)

        assert "Complete" in message
        assert "drafting" in message.lower()


class TestOutlineGateBackslashPaths:
    """Ensure backslash paths are handled correctly."""

    def test_blocks_with_backslash_path(self) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        ctx = {
            "file_path": "artifacts\\sf25d-t1201\\wave-4-drafting\\sections\\tech.md",
            "outline_artifacts_present": [],
        }

        assert evaluator.triggers(rule, state, "Write", ctx) is True

    def test_allows_with_backslash_path_when_outline_present(self) -> None:
        evaluator = _evaluator()
        rule = _outline_gate_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        ctx = {
            "file_path": "artifacts\\sf25d-t1201\\wave-4-drafting\\sections\\tech.md",
            "outline_artifacts_present": ["proposal-outline.md"],
        }

        assert evaluator.triggers(rule, state, "Write", ctx) is False
