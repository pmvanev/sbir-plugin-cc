"""Integration tests: end-to-end pipeline enforcement for figure writes.

Loads the REAL pes-config.json through JsonRuleAdapter -> EnforcementEngine
and verifies both figure_pipeline_gate and style_profile_gate block and allow
correctly through the full hook-to-evaluator path.

Test Budget: 5 behaviors x 2 = 10 max unit tests.
  1. Figure write blocked when specs absent (full pipeline: config -> engine -> evaluator -> BLOCK)
  2. Style gate blocks independently when specs present but style absent
  3. Both gates pass when all prerequisites met
  4. Both gates pass when style_analysis_skipped marker set
  5. Both gates pass for writes outside wave-5-visuals/
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from pes.adapters.json_rule_adapter import JsonRuleAdapter
from pes.domain.engine import EnforcementEngine
from pes.ports.audit_port import AuditLogger

# ---------------------------------------------------------------------------
# Path to real pes-config.json
# ---------------------------------------------------------------------------

REAL_CONFIG_PATH = str(
    Path(__file__).resolve().parents[2] / "templates" / "pes-config.json"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class FakeAuditLogger(AuditLogger):
    """Captures audit entries for assertion."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


@pytest.fixture()
def audit_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture()
def engine(audit_logger: FakeAuditLogger) -> EnforcementEngine:
    """EnforcementEngine wired with real pes-config.json via JsonRuleAdapter."""
    rule_loader = JsonRuleAdapter(REAL_CONFIG_PATH)
    return EnforcementEngine(rule_loader, audit_logger)


def _base_state() -> dict[str, Any]:
    """Minimal proposal state for figure pipeline tests."""
    return {
        "proposal_id": "test-fig-001",
        "current_wave": 5,
    }


# ---------------------------------------------------------------------------
# 1. Figure write BLOCKED when figure-specs.md absent
# ---------------------------------------------------------------------------


def test_figure_write_blocked_when_specs_absent(
    engine: EnforcementEngine,
    audit_logger: FakeAuditLogger,
) -> None:
    """Write to wave-5-visuals/ with NO figure-specs.md -> BLOCK."""
    state = _base_state()
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
        "artifacts_present": [],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "BLOCK"
    assert any("figure-specs.md" in msg for msg in result.messages)
    # Verify audit trail captured the block
    evaluate_entries = [e for e in audit_logger.entries if e["event"] == "evaluate"]
    assert len(evaluate_entries) == 1
    assert evaluate_entries[0]["decision"] == "block"


# ---------------------------------------------------------------------------
# 2. Style gate blocks independently when specs present but style absent
# ---------------------------------------------------------------------------


def test_style_gate_blocks_when_specs_present_but_style_absent(
    engine: EnforcementEngine,
) -> None:
    """Write to wave-5-visuals/ WITH figure-specs.md but NO style-profile.yaml -> BLOCK."""
    state = _base_state()
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
        "artifacts_present": ["figure-specs.md"],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "BLOCK"
    assert any("style-profile.yaml" in msg or "style" in msg.lower() for msg in result.messages)
    # Figure pipeline gate should NOT block (specs present), only style gate
    assert not any("figure-specs.md" in msg and "Create" in msg for msg in result.messages)


# ---------------------------------------------------------------------------
# 3. Both gates pass when all prerequisites met
# ---------------------------------------------------------------------------


def test_both_gates_allow_when_all_prerequisites_met(
    engine: EnforcementEngine,
) -> None:
    """Write to wave-5-visuals/ WITH figure-specs.md AND style-profile.yaml -> ALLOW."""
    state = _base_state()
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
        "artifacts_present": ["figure-specs.md", "style-profile.yaml"],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "ALLOW"
    assert result.messages == []


# ---------------------------------------------------------------------------
# 4. Both gates pass when style_analysis_skipped marker set
# ---------------------------------------------------------------------------


def test_both_gates_allow_when_style_analysis_skipped(
    engine: EnforcementEngine,
) -> None:
    """Write to wave-5-visuals/ WITH figure-specs.md AND style_analysis_skipped -> ALLOW."""
    state = _base_state()
    state["style_analysis_skipped"] = True
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
        "artifacts_present": ["figure-specs.md"],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "ALLOW"
    assert result.messages == []


# ---------------------------------------------------------------------------
# 5. Both gates pass for writes outside wave-5-visuals/
# ---------------------------------------------------------------------------


def test_gates_not_triggered_for_writes_outside_wave5_visuals(
    engine: EnforcementEngine,
) -> None:
    """Write outside wave-5-visuals/ -> ALLOW (figure gates not triggered).

    Includes global_artifacts_present and outline_artifacts_present to avoid
    triggering the writing_style_gate and outline_gate for wave-4-drafting paths.
    """
    state = _base_state()
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-4-drafting/section-a.md",
        "artifacts_present": [],
        "global_artifacts_present": ["quality-preferences.json"],
        "outline_artifacts_present": ["proposal-outline.md"],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "ALLOW"
