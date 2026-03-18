"""Tests for EnforcementEngine -- driving port for PES rule evaluation.

Tests invoke through the EnforcementEngine public API with fake adapters
at port boundaries (RuleLoader, AuditLogger). No mocks inside the hexagon.

Test Budget: 7 behaviors x 2 = 14 max unit tests
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


# --- Fixtures ---


@pytest.fixture()
def audit_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture()
def clean_state() -> dict[str, Any]:
    """Consistent proposal state with Go decision, no orphaned files."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-001",
        "go_no_go": "go",
        "current_wave": 1,
        "waves": {
            "0": {"status": "completed", "completed_at": "2026-03-02T10:00:00Z"},
            "1": {"status": "active", "completed_at": None},
        },
        "topic": {"deadline": "2026-04-15"},
        "strategy_brief": {"status": "not_started"},
        "compliance_matrix": {"item_count": 0},
    }


@pytest.fixture()
def pending_state() -> dict[str, Any]:
    """Proposal state with Go/No-Go pending -- Wave 0."""
    return {
        "schema_version": "1.0.0",
        "proposal_id": "test-uuid-002",
        "go_no_go": "pending",
        "current_wave": 0,
        "waves": {
            "0": {"status": "active", "completed_at": None},
        },
        "topic": {"deadline": "2026-04-15"},
        "strategy_brief": {"status": "not_started"},
        "compliance_matrix": {"item_count": 0},
    }


def _wave_ordering_rule() -> EnforcementRule:
    """Rule: Wave 1 requires Go decision in Wave 0."""
    return EnforcementRule(
        rule_id="wave-1-requires-go",
        description="Wave 1 strategy work requires Go decision",
        rule_type="wave_ordering",
        condition={"requires_go_no_go": "go", "target_wave": 1},
        message="Wave 1 requires Go decision in Wave 0",
    )


# --- Test Classes ---


class TestEnforcementEngineSessionStart:
    """Session startup integrity check through driving port."""

    def test_clean_state_returns_allow_with_no_messages(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        result = engine.check_session_start(clean_state)
        assert result.decision == Decision.ALLOW
        assert result.messages == []

    def test_session_start_logs_audit_entry(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        engine.check_session_start(clean_state)
        assert len(audit_logger.entries) == 1
        assert "timestamp" in audit_logger.entries[0]
        assert audit_logger.entries[0]["event"] == "session_start"


class TestEnforcementEngineEvaluate:
    """Rule evaluation for tool invocations through driving port."""

    def test_blocks_wave_1_when_go_decision_pending(
        self, audit_logger: FakeAuditLogger, pending_state: dict[str, Any]
    ) -> None:
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        result = engine.evaluate(pending_state, tool_name="wave_1_strategy")
        assert result.decision == Decision.BLOCK
        assert "Wave 1 requires Go decision in Wave 0" in result.messages

    def test_allows_wave_1_when_go_decision_made(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        result = engine.evaluate(clean_state, tool_name="wave_1_strategy")
        assert result.decision == Decision.ALLOW

    def test_allows_action_when_no_rules_configured(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader([]), audit_logger)
        result = engine.evaluate(clean_state, tool_name="any_tool")
        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestEnforcementEngineAuditLogging:
    """Audit logging of enforcement decisions."""

    @pytest.mark.parametrize(
        "state_fixture,tool,expected_decision",
        [
            ("pending_state", "wave_1_strategy", "block"),
            ("clean_state", "wave_1_strategy", "allow"),
        ],
    )
    def test_audit_entry_records_lowercase_decision_with_required_fields(
        self,
        audit_logger: FakeAuditLogger,
        state_fixture: str,
        tool: str,
        expected_decision: str,
        request,
    ) -> None:
        state = request.getfixturevalue(state_fixture)
        rules = [_wave_ordering_rule()]
        engine = EnforcementEngine(FakeRuleLoader(rules), audit_logger)
        engine.evaluate(state, tool_name=tool)
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["decision"] == expected_decision
        assert "timestamp" in entry
        assert "proposal_id" in entry
        assert entry["tool_name"] == tool

    def test_session_start_audit_entry_has_lowercase_decision(
        self, audit_logger: FakeAuditLogger, clean_state: dict[str, Any]
    ) -> None:
        engine = EnforcementEngine(FakeRuleLoader(), audit_logger)
        engine.check_session_start(clean_state)
        assert len(audit_logger.entries) == 1
        entry = audit_logger.entries[0]
        assert entry["decision"] == "allow"
        assert entry["event"] == "session_start"
        assert "proposal_id" in entry
