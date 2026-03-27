"""Integration tests: end-to-end outline gate enforcement.

Loads the REAL pes-config.json through JsonRuleAdapter -> EnforcementEngine
and verifies the outline_gate blocks and allows correctly through the full
hook-to-evaluator path including outline_artifacts_present resolution.

Test Budget: 3 behaviors x 2 = 6 max unit tests.
  1. Draft write blocked when proposal-outline.md absent (config -> engine -> evaluator -> BLOCK)
  2. Draft write allowed when proposal-outline.md present in outline_artifacts_present
  3. Gate does not interfere with existing wave-5-visuals/ or writing style gates
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
    """Minimal proposal state for outline gate tests.

    Wave 4 is the drafting wave; wave ordering rules require approvals
    so we set all prerequisite flags to isolate the outline gate.
    """
    return {
        "proposal_id": "test-outline-001",
        "current_wave": 4,
        "go_no_go": "go",
        "strategy_approved": True,
        "research_approved": True,
        "outline_approved": True,
    }


# ---------------------------------------------------------------------------
# 1. Draft write BLOCKED when proposal-outline.md absent
# ---------------------------------------------------------------------------


def test_draft_write_blocked_when_outline_absent(
    engine: EnforcementEngine,
    audit_logger: FakeAuditLogger,
) -> None:
    """Write to wave-4-drafting/ with NO proposal-outline.md -> BLOCK."""
    state = _base_state()
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-4-drafting/sections/tech.md",
        "artifacts_present": [],
        "global_artifacts_present": ["quality-preferences.json"],
        "outline_artifacts_present": [],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "BLOCK"
    assert any("proposal-outline.md" in msg for msg in result.messages)
    # Verify audit trail captured the block
    evaluate_entries = [e for e in audit_logger.entries if e["event"] == "evaluate"]
    assert len(evaluate_entries) == 1
    assert evaluate_entries[0]["decision"] == "block"


# ---------------------------------------------------------------------------
# 2. Draft write ALLOWED when proposal-outline.md present
# ---------------------------------------------------------------------------


def test_draft_write_allowed_when_outline_present(
    engine: EnforcementEngine,
) -> None:
    """Write to wave-4-drafting/ WITH proposal-outline.md in outline_artifacts_present -> ALLOW."""
    state = _base_state()
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-4-drafting/sections/tech.md",
        "artifacts_present": [],
        "global_artifacts_present": ["quality-preferences.json"],
        "outline_artifacts_present": ["proposal-outline.md"],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "ALLOW"
    assert result.messages == []


# ---------------------------------------------------------------------------
# 3. Outline gate does not interfere with wave-5-visuals/ or writing style gates
# ---------------------------------------------------------------------------


def test_outline_gate_does_not_interfere_with_wave5_visuals(
    engine: EnforcementEngine,
) -> None:
    """Write to wave-5-visuals/ with all figure prerequisites -> ALLOW.

    Confirms outline_gate does not trigger for wave-5-visuals paths,
    even when outline_artifacts_present is empty.
    """
    state = _base_state()
    state["current_wave"] = 5
    tool_context = {
        "file_path": "artifacts/sf25d-t1201/wave-5-visuals/figure-1.svg",
        "artifacts_present": ["figure-specs.md", "style-profile.yaml"],
        "outline_artifacts_present": [],
    }

    result = engine.evaluate(state, "Write", tool_context=tool_context)

    assert result.decision.value == "ALLOW"
    assert result.messages == []
