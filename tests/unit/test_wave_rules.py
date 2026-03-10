"""Tests for wave ordering enforcement rules through EnforcementEngine.

Test Budget: 10 behaviors x 2 = 20 max unit tests (current: 16)

Behaviors (C1):
1. Wave 1 blocked when go_no_go is not 'go' (parametrized variations)
2. Wave 1 allowed when go_no_go equals 'go'
3. Block message explains prerequisite requirement
4. Non-wave tools unaffected by wave ordering rules

Behaviors (C2 - Waves 2-4):
5. Wave 2 blocked when strategy brief not approved (parametrized)
6. Wave 2 allowed when strategy brief approved
7. Wave 3 blocked when research not approved; allowed when approved (parametrized)
8. Wave 4 blocked when outline not approved; allowed when approved (parametrized)
9. Skipping waves blocked with prerequisite guidance
10. Block decisions recorded in audit log with rule ID

Behaviors (C3 - Wave 8 sign-off gate):
11. Wave 8 blocked without final review sign-off (parametrized)
12. Wave 8 allowed when final review sign-off recorded

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


def _wave_2_strategy_rule() -> EnforcementRule:
    """Rule: Wave 2 requires strategy brief approval in Wave 1."""
    return EnforcementRule(
        rule_id="wave-2-requires-strategy",
        description="Wave 2 writing requires strategy brief approval",
        rule_type="wave_ordering",
        condition={"requires_strategy_approval": True, "target_wave": 2},
        message="Wave 2 requires strategy brief approval in Wave 1",
    )


def _wave_3_research_rule() -> EnforcementRule:
    """Rule: Wave 3 requires research review approval in Wave 2."""
    return EnforcementRule(
        rule_id="wave-3-requires-research",
        description="Wave 3 outline requires research review approval",
        rule_type="wave_ordering",
        condition={"requires_research_approval": True, "target_wave": 3},
        message="Wave 3 requires research review approval in Wave 2",
    )


def _wave_4_outline_rule() -> EnforcementRule:
    """Rule: Wave 4 requires outline approval in Wave 3."""
    return EnforcementRule(
        rule_id="wave-4-requires-outline",
        description="Wave 4 drafting requires outline approval",
        rule_type="wave_ordering",
        condition={"requires_outline_approval": True, "target_wave": 4},
        message="Wave 4 requires outline approval in Wave 3",
    )


def _all_wave_rules() -> list[EnforcementRule]:
    """All wave ordering rules for comprehensive testing."""
    return [
        _wave_1_go_rule(),
        _wave_2_strategy_rule(),
        _wave_3_research_rule(),
        _wave_4_outline_rule(),
    ]


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


# --- C2: Wave 2-4 ordering tests ---


class TestWave2StrategyApproval:
    """Wave 2 blocked when strategy brief not approved; allowed when approved."""

    @pytest.mark.parametrize(
        "strategy_brief",
        [
            {"status": "not_started", "approved_at": None},
            {"status": "draft", "approved_at": None},
            {},
        ],
        ids=["not_started", "draft", "missing_fields"],
    )
    def test_blocks_wave_2_without_strategy_approval(
        self, strategy_brief: dict[str, Any]
    ) -> None:
        engine, _ = _make_engine([_wave_2_strategy_rule()])
        state = {"proposal_id": "p-001", "strategy_brief": strategy_brief}

        result = engine.evaluate(state, tool_name="wave_2_research")

        assert result.decision == Decision.BLOCK

    def test_blocks_wave_2_when_strategy_brief_missing_from_state(self) -> None:
        engine, _ = _make_engine([_wave_2_strategy_rule()])
        state: dict[str, Any] = {"proposal_id": "p-001"}

        result = engine.evaluate(state, tool_name="wave_2_research")

        assert result.decision == Decision.BLOCK

    def test_allows_wave_2_when_strategy_brief_approved(self) -> None:
        engine, _ = _make_engine([_wave_2_strategy_rule()])
        state = {
            "proposal_id": "p-001",
            "strategy_brief": {
                "status": "approved",
                "approved_at": "2026-03-05T10:00:00Z",
            },
        }

        result = engine.evaluate(state, tool_name="wave_2_research")

        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestWave3ResearchApproval:
    """Wave 3 blocked when research not approved; allowed when approved."""

    @pytest.mark.parametrize(
        "research_summary",
        [
            {"status": "not_started", "approved_at": None},
            {},
        ],
        ids=["not_started", "missing_fields"],
    )
    def test_blocks_wave_3_without_research_approval(
        self, research_summary: dict[str, Any]
    ) -> None:
        engine, _ = _make_engine([_wave_3_research_rule()])
        state = {"proposal_id": "p-001", "research_summary": research_summary}

        result = engine.evaluate(state, tool_name="wave_3_outline")

        assert result.decision == Decision.BLOCK

    def test_allows_wave_3_when_research_approved(self) -> None:
        engine, _ = _make_engine([_wave_3_research_rule()])
        state = {
            "proposal_id": "p-001",
            "research_summary": {
                "status": "approved",
                "approved_at": "2026-03-08T10:00:00Z",
            },
        }

        result = engine.evaluate(state, tool_name="wave_3_outline")

        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestWave4OutlineApproval:
    """Wave 4 blocked when outline not approved; allowed when approved."""

    @pytest.mark.parametrize(
        "outline",
        [
            {"status": "not_started", "approved_at": None},
            {},
        ],
        ids=["not_started", "missing_fields"],
    )
    def test_blocks_wave_4_without_outline_approval(
        self, outline: dict[str, Any]
    ) -> None:
        engine, _ = _make_engine([_wave_4_outline_rule()])
        state = {"proposal_id": "p-001", "outline": outline}

        result = engine.evaluate(state, tool_name="wave_4_drafting")

        assert result.decision == Decision.BLOCK

    def test_allows_wave_4_when_outline_approved(self) -> None:
        engine, _ = _make_engine([_wave_4_outline_rule()])
        state = {
            "proposal_id": "p-001",
            "outline": {
                "status": "approved",
                "approved_at": "2026-03-10T10:00:00Z",
            },
        }

        result = engine.evaluate(state, tool_name="wave_4_drafting")

        assert result.decision == Decision.ALLOW
        assert result.messages == []


class TestWaveSkipping:
    """Skipping waves is blocked with prerequisite guidance message."""

    @pytest.mark.parametrize(
        "tool_name,expected_message_fragment",
        [
            ("wave_3_outline", "Wave 3 requires"),
            ("wave_4_drafting", "Wave 4 requires"),
        ],
        ids=["skip_1_to_3", "skip_2_to_4"],
    )
    def test_skipping_waves_blocked(
        self, tool_name: str, expected_message_fragment: str
    ) -> None:
        engine, _ = _make_engine(_all_wave_rules())
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "go_no_go": "go",
        }

        result = engine.evaluate(state, tool_name=tool_name)

        assert result.decision == Decision.BLOCK
        assert any(expected_message_fragment in m for m in result.messages)


class TestWaveBlockAuditLogging:
    """Block decisions recorded in audit log with rule ID and timestamp."""

    def test_block_audit_entry_includes_timestamp_and_decision(self) -> None:
        engine, audit = _make_engine([_wave_2_strategy_rule()])
        state: dict[str, Any] = {"proposal_id": "p-001"}

        engine.evaluate(state, tool_name="wave_2_research")

        assert len(audit.entries) == 1
        entry = audit.entries[0]
        assert "timestamp" in entry
        assert entry["decision"] == "BLOCK"


# --- C3: Wave 8 sign-off gate ---


def _wave_8_signoff_rule() -> EnforcementRule:
    """Rule: Wave 8 requires final review sign-off."""
    return EnforcementRule(
        rule_id="wave-8-requires-signoff",
        description="Wave 8 submission requires final review sign-off",
        rule_type="wave_ordering",
        condition={"requires_final_review_signoff": True, "target_wave": 8},
        message="Wave 8 requires final review sign-off",
    )


class TestWave8SignOffBlocking:
    """Wave 8 blocked when final review sign-off not recorded."""

    @pytest.mark.parametrize(
        "final_review",
        [
            {"signed_off": False},
            {},
        ],
        ids=["not_signed_off", "missing_signed_off"],
    )
    def test_blocks_wave_8_without_signoff(
        self, final_review: dict[str, Any]
    ) -> None:
        engine, _ = _make_engine([_wave_8_signoff_rule()])
        state = {"proposal_id": "p-001", "final_review": final_review}

        result = engine.evaluate(state, tool_name="wave_8_submission")

        assert result.decision == Decision.BLOCK

    def test_blocks_wave_8_when_final_review_missing_from_state(self) -> None:
        engine, _ = _make_engine([_wave_8_signoff_rule()])
        state: dict[str, Any] = {"proposal_id": "p-001"}

        result = engine.evaluate(state, tool_name="wave_8_submission")

        assert result.decision == Decision.BLOCK


class TestWave8SignOffAllowing:
    """Wave 8 allowed when final review sign-off is recorded."""

    def test_allows_wave_8_when_signed_off(self) -> None:
        engine, _ = _make_engine([_wave_8_signoff_rule()])
        state = {
            "proposal_id": "p-001",
            "final_review": {
                "signed_off": True,
                "signed_off_at": "2026-03-10T14:00:00Z",
            },
        }

        result = engine.evaluate(state, tool_name="wave_8_submission")

        assert result.decision == Decision.ALLOW
        assert result.messages == []
