"""Smoke tests for cross-wave integration test fixtures.

Verify that the state builder, in-memory port stubs, and engine wiring
work together correctly before subsequent integration test steps use them.

Test Budget: 3 behaviors x 2 = 6 max unit tests
- B1: State builder produces valid proposal state for any wave (parametrized)
- B2: Engine with in-memory ports returns ALLOW for valid Wave 0 invocation
- B3: Audit logger stub captures entries with required fields
"""

from __future__ import annotations

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision

from tests.integration.conftest import InMemoryAuditLogger, InMemoryRuleLoader, build_state


# ---------------------------------------------------------------------------
# B1: State builder produces valid state for any wave 0-9
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("wave", list(range(10)))
def test_state_builder_produces_valid_state_for_each_wave(wave: int) -> None:
    """State builder returns well-formed proposal state with correct wave."""
    state = build_state(current_wave=wave)

    assert state["schema_version"] == "2.0.0"
    assert state["proposal_id"] is not None
    assert state["current_wave"] == wave
    assert str(wave) in state["waves"]
    assert state["waves"][str(wave)]["status"] == "active"
    assert state["topic"]["deadline"] is not None
    assert state["go_no_go"] in ("pending", "go")
    # All waves 0 through 9 should be present
    for w in range(10):
        assert str(w) in state["waves"]


# ---------------------------------------------------------------------------
# B2: Engine with in-memory ports returns ALLOW for valid Wave 0
# ---------------------------------------------------------------------------


def test_engine_allows_valid_wave_0_tool_invocation() -> None:
    """Engine constructed with in-memory ports returns ALLOW for Wave 0 tool."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader()
    engine = EnforcementEngine(rule_loader, audit_logger)

    state = build_state(current_wave=0)
    result = engine.evaluate(state, tool_name="wave_0_intelligence")

    assert result.decision == Decision.ALLOW
    assert result.messages == []


# ---------------------------------------------------------------------------
# B3: Audit logger stub captures entries with required fields
# ---------------------------------------------------------------------------


def test_audit_logger_captures_entries_with_required_fields() -> None:
    """Audit logger stub records entries with timestamp, event, decision, proposal_id."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader()
    engine = EnforcementEngine(rule_loader, audit_logger)

    state = build_state(current_wave=0)
    engine.evaluate(state, tool_name="wave_0_intelligence")

    assert len(audit_logger.entries) == 1
    entry = audit_logger.entries[0]
    assert "timestamp" in entry
    assert "event" in entry
    assert "decision" in entry
    assert "proposal_id" in entry
    assert entry["proposal_id"] == state["proposal_id"]
