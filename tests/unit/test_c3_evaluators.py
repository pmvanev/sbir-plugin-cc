"""Tests for C3 enforcement evaluators through EnforcementEngine.

Test Budget: 8 behaviors x 2 = 16 max unit tests (target: ~10)

Behaviors:
1. PDC gate blocks Wave 5 when sections have RED Tier 1/2 PDC items
2. PDC gate allows Wave 5 when all sections GREEN
3. Deadline blocking warns at critical threshold with submit/skip suggestion
4. Deadline blocking does not trigger above threshold
5. Engine dispatches C3 rule types (pdc_gate, deadline_blocking,
   submission_immutability, corpus_integrity)
6. Submission immutability blocks writes to submitted artifacts
7. Corpus integrity blocks modification of existing win/loss tags
8. Corpus integrity allows appending new tags

Tests enter through driving port (EnforcementEngine.evaluate /
EnforcementEngine.check_session_start).
Driven ports (RuleLoader, AuditLogger) use fakes at port boundaries.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule
from pes.ports.audit_port import AuditLogger
from pes.ports.rule_port import RuleLoader

# --- Fake adapters at port boundaries ---


class FakeRuleLoader(RuleLoader):
    def __init__(self, rules: list[EnforcementRule] | None = None) -> None:
        self._rules = rules or []

    def load_rules(self) -> list[EnforcementRule]:
        return self._rules


class FakeAuditLogger(AuditLogger):
    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []

    def log(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)


# --- Helpers ---


def _make_engine(
    rules: list[EnforcementRule] | None = None,
) -> tuple[EnforcementEngine, FakeAuditLogger]:
    audit = FakeAuditLogger()
    engine = EnforcementEngine(FakeRuleLoader(rules or []), audit)
    return engine, audit


def _pdc_gate_rule() -> EnforcementRule:
    return EnforcementRule(
        rule_id="wave-5-requires-pdc-green",
        description="Wave 5 visuals require all sections Tier 1+2 PDCs GREEN",
        rule_type="pdc_gate",
        condition={"requires_pdc_green": True, "target_wave": 5},
        message="Wave 5 requires all sections to have Tier 1+2 PDCs GREEN",
    )


def _deadline_blocking_rule() -> EnforcementRule:
    return EnforcementRule(
        rule_id="deadline-blocking",
        description="Block non-essential waves at critical deadline threshold",
        rule_type="deadline_blocking",
        condition={"critical_days": 3, "non_essential_waves": [5]},
        message="Critical deadline threshold -- non-essential work blocked",
    )


def _submission_immutability_rule() -> EnforcementRule:
    return EnforcementRule(
        rule_id="submission-immutability",
        description="Block all writes to submitted proposal artifacts",
        rule_type="submission_immutability",
        condition={"requires_immutable": True},
        message="Proposal is submitted. Artifacts are read-only.",
    )


def _corpus_integrity_rule() -> EnforcementRule:
    return EnforcementRule(
        rule_id="corpus-integrity",
        description="Win/loss tags are append-only",
        rule_type="corpus_integrity",
        condition={"append_only_tags": True},
        message="Win/loss tags are append-only and cannot be modified",
    )


# --- PDC Gate Tests ---


class TestPdcGateBlocking:
    """PDC gate blocks Wave 5 when sections have RED PDC items."""

    @pytest.mark.parametrize(
        "pdc_status",
        [
            {
                "3.2": {
                    "tier_1": "GREEN",
                    "tier_2": "RED",
                    "red_items": ["Phase II pathway uses generic language"],
                }
            },
            {
                "3.1": {"tier_1": "RED", "tier_2": "GREEN", "red_items": ["Missing data"]},
                "3.2": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
            },
        ],
        ids=["single_section_red_t2", "section_red_t1"],
    )
    def test_blocks_wave_5_with_red_pdc_items(
        self, pdc_status: dict[str, Any]
    ) -> None:
        engine, _ = _make_engine([_pdc_gate_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "pdc_status": pdc_status,
        }

        result = engine.evaluate(state, tool_name="wave_5_visuals")

        assert result.decision == Decision.BLOCK
        assert any("pdc" in m.lower() or "red" in m.lower() or "section" in m.lower()
                    for m in result.messages)


class TestPdcGateAllowing:
    """PDC gate allows Wave 5 when all sections GREEN."""

    def test_allows_wave_5_when_all_pdcs_green(self) -> None:
        engine, _ = _make_engine([_pdc_gate_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "pdc_status": {
                "3.1": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
                "3.2": {"tier_1": "GREEN", "tier_2": "GREEN", "red_items": []},
            },
        }

        result = engine.evaluate(state, tool_name="wave_5_visuals")

        assert result.decision == Decision.ALLOW
        assert result.messages == []

    def test_allows_non_wave_5_tool_regardless_of_pdc(self) -> None:
        engine, _ = _make_engine([_pdc_gate_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "pdc_status": {
                "3.2": {"tier_1": "GREEN", "tier_2": "RED", "red_items": ["Issue"]},
            },
        }

        result = engine.evaluate(state, tool_name="wave_4_drafting")

        assert result.decision == Decision.ALLOW


# --- Deadline Blocking Tests ---


class TestDeadlineBlocking:
    """Deadline blocking warns at critical threshold."""

    def test_blocks_non_essential_wave_at_critical_deadline(self) -> None:
        deadline = (date.today() + timedelta(days=3)).isoformat()
        engine, _ = _make_engine([_deadline_blocking_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "topic": {"deadline": deadline},
            "current_wave": 5,
        }

        result = engine.evaluate(state, tool_name="wave_5_visuals")

        assert result.decision == Decision.BLOCK
        all_messages = " ".join(result.messages).lower()
        assert "submit" in all_messages or "skip" in all_messages

    def test_does_not_block_above_critical_threshold(self) -> None:
        deadline = (date.today() + timedelta(days=14)).isoformat()
        engine, _ = _make_engine([_deadline_blocking_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "topic": {"deadline": deadline},
            "current_wave": 5,
        }

        result = engine.evaluate(state, tool_name="wave_5_visuals")

        assert result.decision == Decision.ALLOW

    def test_does_not_block_essential_wave_at_critical_deadline(self) -> None:
        deadline = (date.today() + timedelta(days=2)).isoformat()
        engine, _ = _make_engine([_deadline_blocking_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "topic": {"deadline": deadline},
            "current_wave": 6,
        }

        result = engine.evaluate(state, tool_name="wave_6_format")

        assert result.decision == Decision.ALLOW


# --- Submission Immutability Tests ---


class TestSubmissionImmutability:
    """Submission immutability blocks writes to submitted artifacts."""

    def test_blocks_write_to_submitted_proposal(self) -> None:
        engine, _ = _make_engine([_submission_immutability_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "submission": {"status": "submitted", "immutable": True},
        }

        result = engine.evaluate(state, tool_name="wave_5_visuals")

        assert result.decision == Decision.BLOCK
        assert any("read-only" in m.lower() or "submitted" in m.lower()
                    for m in result.messages)

    def test_allows_action_when_not_submitted(self) -> None:
        engine, _ = _make_engine([_submission_immutability_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "submission": {"status": "draft", "immutable": False},
        }

        result = engine.evaluate(state, tool_name="wave_5_visuals")

        assert result.decision == Decision.ALLOW

    def test_block_message_includes_proposal_id(self) -> None:
        engine, _ = _make_engine([_submission_immutability_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "topic": {"id": "AF243-001"},
            "submission": {"status": "submitted", "immutable": True},
        }

        result = engine.evaluate(state, tool_name="write_file")

        assert result.decision == Decision.BLOCK
        all_messages = " ".join(result.messages)
        assert "AF243-001" in all_messages


# --- Corpus Integrity Tests ---


class TestCorpusIntegrity:
    """Corpus integrity blocks modification of existing win/loss tags."""

    def test_blocks_modification_of_existing_outcome_tag(self) -> None:
        engine, _ = _make_engine([_corpus_integrity_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "learning": {
                "outcome": "not_selected",
                "outcome_recorded_at": "2026-07-01T10:00:00Z",
            },
            "requested_outcome_change": "awarded",
        }

        result = engine.evaluate(state, tool_name="record_outcome")

        assert result.decision == Decision.BLOCK
        assert any("append-only" in m.lower() or "cannot be modified" in m.lower()
                    for m in result.messages)

    def test_allows_appending_new_outcome_tag(self) -> None:
        engine, _ = _make_engine([_corpus_integrity_rule()])
        state: dict[str, Any] = {
            "proposal_id": "p-001",
            "learning": {
                "outcome": None,
                "outcome_recorded_at": None,
            },
            "requested_outcome_change": "not_selected",
        }

        result = engine.evaluate(state, tool_name="record_outcome")

        assert result.decision == Decision.ALLOW
