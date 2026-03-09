"""Tests for wave ordering enforcement rules through EnforcementEngine.

Test Budget: 4 behaviors x 2 = 8 max unit tests

Behaviors:
1. Wave 1 blocked when go_no_go is not 'go' (parametrized variations)
2. Wave 1 allowed when go_no_go equals 'go'
3. Block message explains prerequisite requirement
4. Non-wave tools unaffected by wave ordering rules

Tests enter through driving port (EnforcementEngine.evaluate).
Driven ports (RuleLoader, AuditLogger) use fakes at port boundaries.
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader

# --- Fake adapters at port boundaries ---


class FakeRuleLoader(RuleLoader):
    """Fake rule loader returning preconfigured rules."""

    def __init__(self, rules: list[EnforcementRule] | None = None) -> None:
        self._rules = rules or []

    def load_rules(self) -> list[EnforcementRule]:
        return self._rules


class FakeAuditLogger(AuditLogger):
    """Fake audit logger capturing entries for assertion."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


# --- Helpers ---


def _wave_1_go_rule() -> EnforcementRule:
    """Rule: Wave 1 requires Go decision in Wave 0."""
    return EnforcementRule(
        rule_id="wave-1-requires-go",
        description="Wave 1 strategy work requires Go decision",
        rule_type="wave_ordering",
        condition={"requires_go_no_go": "go", "target_wave": 1},
        message="Wave 1 requires Go decision in Wave 0",
    )


def _make_engine(
    rules: list[EnforcementRule] | None = None,
) -> tuple[EnforcementEngine, FakeAuditLogger]:
    audit = FakeAuditLogger()
    engine = EnforcementEngine(FakeRuleLoader(rules or []), audit)
    return engine, audit


# --- Tests ---


class TestWaveOrderingBlocking:
    """Wave 1 commands blocked when go_no_go is not 'go'."""

    @pytest.mark.parametrize(
        "go_no_go_value",
        ["pending", "no_go", "deferred", ""],
    )
    def test_blocks_wave_1_for_non_go_states(self, go_no_go_value: str) -> None:
        engine, _ = _make_engine([_wave_1_go_rule()])
        state = {"proposal_id": "p-001", "go_no_go": go_no_go_value}

        result = engine.evaluate(state, tool_name="wave_1_strategy")

        assert result.decision == Decision.BLOCK

    def test_blocks_wave_1_when_go_no_go_missing_from_state(self) -> None:
        engine, _ = _make_engine([_wave_1_go_rule()])
        state: dict[str, Any] = {"proposal_id": "p-001"}

        result = engine.evaluate(state, tool_name="wave_1_strategy")

        assert result.decision == Decision.BLOCK


class TestWaveOrderingAllowing:
    """Wave 1 commands allowed when go_no_go equals 'go'."""

    def test_allows_wave_1_when_go_decision_made(self) -> None:
        engine, _ = _make_engine([_wave_1_go_rule()])
        state = {"proposal_id": "p-001", "go_no_go": "go"}

        result = engine.evaluate(state, tool_name="wave_1_strategy")

        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestWaveOrderingBlockMessage:
    """Block message explains what prerequisite is required."""

    def test_block_message_identifies_prerequisite(self) -> None:
        engine, _ = _make_engine([_wave_1_go_rule()])
        state = {"proposal_id": "p-001", "go_no_go": "pending"}

        result = engine.evaluate(state, tool_name="wave_1_strategy")

        assert len(result.messages) == 1
        assert "Wave 1 requires Go decision in Wave 0" in result.messages[0]


class TestWaveOrderingScope:
    """Non-wave tools unaffected by wave ordering rules."""

    def test_non_wave_tool_not_blocked_by_wave_rule(self) -> None:
        engine, _ = _make_engine([_wave_1_go_rule()])
        state = {"proposal_id": "p-001", "go_no_go": "pending"}

        result = engine.evaluate(state, tool_name="compliance_check")

        assert result.decision == Decision.ALLOW
