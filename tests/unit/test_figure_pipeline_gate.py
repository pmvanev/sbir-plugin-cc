"""Tests for figure pipeline gate enforcement -- domain logic.

Test Budget: 5 behaviors x 2 = 10 max unit tests (current: 7)

Behaviors:
1. Write to wave-5-visuals/ blocked when figure-specs.md absent (parametrized Write/Edit)
2. Writing figure-specs.md itself always allowed (parametrized Write/Edit)
3. Writes outside wave-5-visuals/ not affected (parametrized various paths)
4. Non-write tools not affected
5. Block message includes guidance to create figure-specs.md first

Tests invoke FigurePipelineGateEvaluator directly -- engine wiring is a separate step.
Evaluator is a pure domain object with stable public interface (triggers + build_block_message).
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.figure_pipeline_gate import FigurePipelineGateEvaluator
from pes.domain.rules import EnforcementRule


# --- Helpers ---


def _figure_pipeline_rule() -> EnforcementRule:
    """Rule: wave-5-visuals/ requires figure-specs.md to exist."""
    return EnforcementRule(
        rule_id="figure-pipeline-gate",
        description="Figure visuals require figure-specs.md prerequisite",
        rule_type="figure_pipeline_gate",
        condition={},
        message="Create figure-specs.md before writing visual assets",
    )


def _evaluator() -> FigurePipelineGateEvaluator:
    return FigurePipelineGateEvaluator()


# --- Tests ---


class TestFigurePipelineBlocking:
    """Write/Edit to wave-5-visuals/ blocked when figure-specs.md absent."""

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_blocks_visual_write_when_specs_absent(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
            "artifacts_present": [],
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is True

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_blocks_visual_write_when_artifacts_present_missing(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-5-visuals/chart.png",
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is True


class TestFigurePipelineAllowing:
    """Writing figure-specs.md itself always allowed; writes allowed when specs present."""

    @pytest.mark.parametrize("tool_name", ["Write", "Edit"])
    def test_allows_writing_figure_specs_itself(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-specs.md",
            "artifacts_present": [],
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is False

    def test_allows_visual_write_when_specs_present(self) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
            "artifacts_present": ["figure-specs.md"],
        }

        result = evaluator.triggers(rule, state, "Write", tool_context)

        assert result is False


class TestFigurePipelineScope:
    """Non-visual paths and non-write tools not affected."""

    @pytest.mark.parametrize(
        "file_path",
        [
            "artifacts/sf25d-t1201/wave-4-drafting/section-1.md",
            "artifacts/sf25d-t1201/wave-6-review/checklist.md",
            "scripts/pes/domain/engine.py",
        ],
        ids=["wave-4-path", "wave-6-path", "non-artifact-path"],
    )
    def test_ignores_paths_outside_wave_5_visuals(self, file_path: str) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {"file_path": file_path, "artifacts_present": []}

        result = evaluator.triggers(rule, state, "Write", tool_context)

        assert result is False

    @pytest.mark.parametrize("tool_name", ["Read", "Bash", "Glob", "Grep"])
    def test_ignores_non_write_tools(self, tool_name: str) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}
        tool_context = {
            "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
            "artifacts_present": [],
        }

        result = evaluator.triggers(rule, state, tool_name, tool_context)

        assert result is False


class TestFigurePipelineBlockMessage:
    """Block message includes guidance to create figure-specs.md first."""

    def test_block_message_includes_figure_specs_guidance(self) -> None:
        evaluator = _evaluator()
        rule = _figure_pipeline_rule()
        state: dict[str, Any] = {"proposal_id": "p-001"}

        message = evaluator.build_block_message(rule, state)

        assert "figure-specs.md" in message
        assert "first" in message.lower() or "before" in message.lower()
