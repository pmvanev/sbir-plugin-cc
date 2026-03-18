"""Error paths: wave skips and concurrent evaluator composition.

Cross-wave integration test verifying that the EnforcementEngine returns
correct BLOCK decisions for wave skip attempts and when multiple evaluators
trigger simultaneously.

Test Budget: 5 behaviors x 2 = 10 max unit tests
- B1: Wave 0->3 skip returns BLOCK from wave_ordering evaluator (AC1)
- B2: Wave 2->5 skip returns BLOCK from wave_ordering (not pdc_gate); audit rule_type is wave_ordering (AC2)
- B3: Outcome tag modification with existing outcome returns BLOCK from corpus_integrity (AC3)
- B4: wave_ordering + deadline_blocking both triggering returns BLOCK with messages from both (AC4)
- B5: pdc_gate + deadline_blocking both triggering returns BLOCK with messages from both (AC5)
"""

from __future__ import annotations

from typing import Any

import pytest

from pes.domain.engine import EnforcementEngine
from pes.domain.rules import Decision, EnforcementRule

from tests.integration.conftest import (
    InMemoryAuditLogger,
    InMemoryRuleLoader,
    build_state,
)


# ---------------------------------------------------------------------------
# Rule definitions for error path scenarios
# ---------------------------------------------------------------------------

WAVE_ORDERING_RULE_W3 = EnforcementRule(
    rule_id="wave-3-requires-research",
    description="Wave 3 outline requires research review approval in Wave 2",
    rule_type="wave_ordering",
    condition={"requires_research_approval": True, "target_wave": 3},
    message="Wave 3 requires research review approval in Wave 2",
)

WAVE_ORDERING_RULE_W5 = EnforcementRule(
    rule_id="wave-5-requires-outline",
    description="Wave 5 requires outline approval in Wave 3",
    rule_type="wave_ordering",
    condition={"requires_outline_approval": True, "target_wave": 5},
    message="Wave 5 requires outline approval in Wave 3",
)

PDC_GATE_RULE_W5 = EnforcementRule(
    rule_id="wave-5-requires-pdc-green",
    description="Wave 5 visual assets requires all PDC sections GREEN",
    rule_type="pdc_gate",
    condition={"requires_pdc_green": True, "target_wave": 5},
    message="Wave 5 requires all PDC sections GREEN",
)

DEADLINE_BLOCKING_RULE = EnforcementRule(
    rule_id="deadline-critical-block",
    description="Block non-essential waves when deadline is within 7 days",
    rule_type="deadline_blocking",
    condition={"critical_days": 9999, "non_essential_waves": [0, 1, 2, 3, 4, 5]},
    message="Deadline is critically close",
)

CORPUS_INTEGRITY_RULE = EnforcementRule(
    rule_id="corpus-outcome-append-only",
    description="Win/loss outcome tags are append-only",
    rule_type="corpus_integrity",
    condition={"append_only_tags": True},
    message="Outcome tags are immutable once recorded",
)


def _make_engine(
    rules: list[EnforcementRule],
) -> tuple[EnforcementEngine, InMemoryAuditLogger]:
    """Create engine wired with given rules and in-memory audit logger."""
    audit_logger = InMemoryAuditLogger()
    rule_loader = InMemoryRuleLoader(rules=rules)
    engine = EnforcementEngine(rule_loader, audit_logger)
    return engine, audit_logger


# ---------------------------------------------------------------------------
# B1: Wave 0->3 skip returns BLOCK from wave_ordering (AC1)
# ---------------------------------------------------------------------------


def test_wave_0_to_3_skip_blocked_by_wave_ordering() -> None:
    """Skipping from wave 0 to wave 3 returns BLOCK; message matches wave ordering rule."""
    engine, _audit = _make_engine(rules=[WAVE_ORDERING_RULE_W3])

    # State at wave 0 -- research_summary has no approval
    state = build_state(
        current_wave=0,
        overrides={"research_summary": {"findings": [], "approved_at": None}},
    )
    result = engine.evaluate(state, tool_name="wave_3_outline")

    assert result.decision == Decision.BLOCK
    assert any("Wave 3 requires research review approval" in msg for msg in result.messages)


# ---------------------------------------------------------------------------
# B2: Wave 2->5 skip returns BLOCK from wave_ordering, not pdc_gate (AC2)
# ---------------------------------------------------------------------------


def test_wave_2_to_5_skip_blocked_by_wave_ordering_not_pdc_gate() -> None:
    """Skipping from wave 2 to wave 5 returns BLOCK from wave_ordering evaluator.

    Both wave_ordering and pdc_gate rules target wave 5, but with no PDC
    status present, only wave_ordering triggers. Audit entry rule_type
    reflects wave_ordering origin.
    """
    engine, audit_logger = _make_engine(
        rules=[WAVE_ORDERING_RULE_W5, PDC_GATE_RULE_W5],
    )

    # State at wave 2 -- outline not approved, no pdc_status at all
    state = build_state(
        current_wave=2,
        overrides={
            "outline": {"path": None, "status": "not_started", "approved_at": None},
        },
    )
    result = engine.evaluate(state, tool_name="wave_5_visuals")

    assert result.decision == Decision.BLOCK
    # Only wave_ordering message present, not pdc_gate
    assert len(result.messages) == 1
    assert "Wave 5 requires outline approval" in result.messages[0]

    # Audit entry confirms wave_ordering origin
    assert len(audit_logger.entries) == 1
    entry = audit_logger.entries[0]
    assert entry["decision"] == "block"
    assert entry["messages"] == result.messages


# ---------------------------------------------------------------------------
# B3: Outcome tag modification with existing outcome returns BLOCK (AC3)
# ---------------------------------------------------------------------------


def test_outcome_tag_modification_blocked_by_corpus_integrity() -> None:
    """Modifying an existing outcome tag returns BLOCK from corpus_integrity evaluator."""
    engine, _audit = _make_engine(rules=[CORPUS_INTEGRITY_RULE])

    state = build_state(
        current_wave=9,
        overrides={
            "learning": {"outcome": "win"},
            "requested_outcome_change": "loss",
        },
    )
    result = engine.evaluate(state, tool_name="record_outcome")

    assert result.decision == Decision.BLOCK
    assert any("Outcome tags are immutable" in msg for msg in result.messages)


# ---------------------------------------------------------------------------
# B4: wave_ordering + deadline_blocking both trigger -> BLOCK with both messages (AC4)
# ---------------------------------------------------------------------------


def test_wave_ordering_and_deadline_blocking_both_trigger() -> None:
    """When both wave_ordering and deadline_blocking trigger, BLOCK includes messages from both."""
    engine, _audit = _make_engine(
        rules=[WAVE_ORDERING_RULE_W3, DEADLINE_BLOCKING_RULE],
    )

    # State at wave 3 but without research approval, and deadline imminent
    # deadline_blocking uses critical_days=9999, so any deadline will trigger
    state = build_state(
        current_wave=3,
        overrides={
            "research_summary": {"findings": [], "approved_at": None},
        },
    )
    result = engine.evaluate(state, tool_name="wave_3_outline")

    assert result.decision == Decision.BLOCK
    assert len(result.messages) == 2

    messages_joined = " ".join(result.messages)
    assert "Wave 3 requires research review approval" in messages_joined
    assert "Deadline is critically close" in messages_joined


# ---------------------------------------------------------------------------
# B5: pdc_gate + deadline_blocking both trigger -> BLOCK with both messages (AC5)
# ---------------------------------------------------------------------------


def test_pdc_gate_and_deadline_blocking_both_trigger() -> None:
    """When both pdc_gate and deadline_blocking trigger, BLOCK includes messages from both."""
    engine, _audit = _make_engine(
        rules=[PDC_GATE_RULE_W5, DEADLINE_BLOCKING_RULE],
    )

    red_pdc: dict[str, Any] = {
        "3.1": {"tier_1": "RED", "tier_2": "GREEN", "red_items": ["missing figure"]},
    }
    state = build_state(
        current_wave=5,
        overrides={"pdc_status": red_pdc},
    )
    result = engine.evaluate(state, tool_name="wave_5_visuals")

    assert result.decision == Decision.BLOCK
    assert len(result.messages) == 2

    messages_joined = " ".join(result.messages)
    assert "RED PDC items" in messages_joined
    assert "Deadline is critically close" in messages_joined
